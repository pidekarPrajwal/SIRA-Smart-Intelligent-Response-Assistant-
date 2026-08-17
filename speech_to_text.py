# ==========================================================================
# -----------------Voice settings (Step 2)
# ==========================================================================
"""
speech_to_text.py

Handles ONLY transcription of recorded audio into text using Faster-Whisper.
Does not touch the microphone, Ollama, or Piper directly.
"""

from typing import Optional

import numpy as np

from config import WHISPER_MODEL, WHISPER_DEVICE, WHISPER_COMPUTE_TYPE

_model = None
_model_load_failed = False


def _get_model():
    """Lazily load the Faster-Whisper model once and reuse it."""
    global _model, _model_load_failed

    if _model is not None:
        return _model

    if _model_load_failed:
        return None

    try:
        from faster_whisper import WhisperModel

        print(f"Loading speech recognition model '{WHISPER_MODEL}', please wait...\n")
        _model = WhisperModel(
            WHISPER_MODEL,
            device=WHISPER_DEVICE,
            compute_type=WHISPER_COMPUTE_TYPE,
        )
        return _model
    except Exception as exc:  # noqa: BLE001 - any load failure should not crash SIRA
        print(f"\nSIRA: The speech recognition model could not be loaded.\nDetails: {exc}\n")
        _model_load_failed = True
        return None


def transcribe_audio(audio: np.ndarray) -> Optional[str]:
    """
    Transcribe a 1D float32 NumPy array of audio samples into text.
    Returns the transcribed text (possibly empty string if silence),
    or None if transcription could not be performed at all.
    """
    model = _get_model()
    if model is None:
        return None

    try:
        segments, _info = model.transcribe(audio, language="en")
        text = "".join(segment.text for segment in segments).strip()
        return text
    except Exception as exc:  # noqa: BLE001 - surface transcription errors cleanly
        print(f"\nSIRA: An error occurred during transcription: {exc}\n")
        return None