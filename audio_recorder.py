# ==========================================================================
# ----------------- Voice settings (Step 2)
# ==========================================================================

"""
audio_recorder.py

Handles ONLY microphone recording. Returns raw audio as a NumPy array
(or None on failure). Does not know about Whisper, Ollama, or Piper.
"""

from typing import Optional

import numpy as np

from config import SAMPLE_RATE, CHANNELS, RECORD_SECONDS

try:
    import sounddevice as sd
    _SOUNDDEVICE_AVAILABLE = True
except (ImportError, OSError):
    # OSError can happen if the underlying PortAudio library isn't installed.
    _SOUNDDEVICE_AVAILABLE = False


def record_audio() -> Optional[np.ndarray]:
    """
    Record RECORD_SECONDS of audio from the default microphone at SAMPLE_RATE.
    Returns a 1D float32 NumPy array of samples, or None if recording failed.
    """
    if not _SOUNDDEVICE_AVAILABLE:
        print(
            "\nSIRA: I cannot access the microphone.\n"
            "The 'sounddevice' library (or its PortAudio backend) is not available.\n"
        )
        return None

    try:
        print("Listening...")
        recording = sd.rec(
            int(RECORD_SECONDS * SAMPLE_RATE),
            samplerate=SAMPLE_RATE,
            channels=CHANNELS,
            dtype="float32",
        )
        sd.wait()  # Block until recording is finished
        return recording.flatten()
    except sd.PortAudioError:
        print(
            "\nSIRA: I cannot access the microphone.\n"
            "Please check your microphone settings and permissions.\n"
        )
        return None
    except Exception as exc:  # noqa: BLE001 - surface any other audio failure cleanly
        print(f"\nSIRA: An unexpected microphone error occurred: {exc}\n")
        return None