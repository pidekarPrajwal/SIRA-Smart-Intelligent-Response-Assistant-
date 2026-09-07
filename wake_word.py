"""
wake_word.py

Handles ONLY continuous microphone listening + wake-word detection.
Does not touch Whisper, Ollama, or Piper. Blocks until the wake word
is heard, then returns control to main.py.
"""

from typing import Optional

import numpy as np

from config import (
    SAMPLE_RATE,
    WAKE_WORD_MODEL,
    WAKE_WORD_THRESHOLD,
    WAKE_WORD_FRAME_SAMPLES,
)

try:
    import sounddevice as sd
    _SOUNDDEVICE_AVAILABLE = True
except (ImportError, OSError):
    _SOUNDDEVICE_AVAILABLE = False

_owwmodel = None
_model_load_failed = False


def _get_model():
    """Lazily load the openWakeWord model once and reuse it."""
    global _owwmodel, _model_load_failed

    if _owwmodel is not None:
        return _owwmodel
    if _model_load_failed:
        return None

    try:
        from openwakeword.model import Model

        _owwmodel = Model(wakeword_models=[WAKE_WORD_MODEL], inference_framework="onnx")
        return _owwmodel
    except Exception as exc:  # noqa: BLE001
        print(f"\nSIRA: The wake-word model could not be loaded.\nDetails: {exc}\n")
        _model_load_failed = True
        return None


def wait_for_wake_word() -> bool:
    """
    Block until the wake word is detected (or an error occurs).
    Returns True if the wake word was detected, False if listening
    could not proceed (mic or model unavailable) - caller should stop.
    """
    if not _SOUNDDEVICE_AVAILABLE:
        print(
            "\nSIRA: I cannot access the microphone.\n"
            "Please check your microphone settings.\n"
        )
        return False

    model = _get_model()
    if model is None:
        return False

    try:
        with sd.InputStream(
            samplerate=SAMPLE_RATE,
            channels=1,
            dtype="int16",
            blocksize=WAKE_WORD_FRAME_SAMPLES,
        ) as stream:
            while True:
                frame, _overflowed = stream.read(WAKE_WORD_FRAME_SAMPLES)
                audio_chunk: np.ndarray = frame.flatten()

                predictions = model.predict(audio_chunk)

                for _model_name, score in predictions.items():
                    if score >= WAKE_WORD_THRESHOLD:
                        return True
    except sd.PortAudioError:
        print(
            "\nSIRA: I cannot access the microphone.\n"
            "Please check your microphone settings and permissions.\n"
        )
        return False
    except Exception as exc:  # noqa: BLE001
        print(f"\nSIRA: An unexpected error occurred while listening for the wake word: {exc}\n")
        return False