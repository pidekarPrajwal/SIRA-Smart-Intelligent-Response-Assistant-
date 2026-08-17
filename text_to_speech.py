# ==========================================================================
# -----------------Voice settings (Step 2)
# ==========================================================================
"""
text_to_speech.py

Handles ONLY speech synthesis (via the local Piper executable) and
playback of the resulting audio. Does not touch the microphone,
Whisper, or Ollama.
"""

import shutil
import subprocess
from pathlib import Path

from config import PIPER_EXECUTABLE, PIPER_MODEL, TTS_OUTPUT_FILE

try:
    import soundfile as sf
    import sounddevice as sd
    _PLAYBACK_AVAILABLE = True
except (ImportError, OSError):
    _PLAYBACK_AVAILABLE = False


def _piper_is_available() -> bool:
    """Check whether the configured Piper executable can actually be found."""
    return shutil.which(PIPER_EXECUTABLE) is not None or Path(PIPER_EXECUTABLE).exists()


def _voice_model_is_available() -> bool:
    return Path(PIPER_MODEL).exists()


def speak(text: str) -> None:
    """
    Convert `text` to speech with Piper and play it back through the
    default output device. Prints the text regardless, so the terminal
    transcript stays useful even if voice output is unavailable.
    """
    print(f"\nSIRA: {text}\n")

    if not text or not text.strip():
        return

    if not _piper_is_available() or not _voice_model_is_available():
        print("SIRA: I can generate a response, but the voice engine is unavailable.\n")
        return

    try:
        subprocess.run(
            [
                PIPER_EXECUTABLE,
                "--model", PIPER_MODEL,
                "--output_file", TTS_OUTPUT_FILE,
            ],
            input=text.encode("utf-8"),
            check=True,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.PIPE,
        )
    except (subprocess.CalledProcessError, FileNotFoundError, OSError) as exc:
        print(f"SIRA: I can generate a response, but the voice engine failed to run.\nDetails: {exc}\n")
        return

    _play_audio_file(TTS_OUTPUT_FILE)


def _play_audio_file(path: str) -> None:
    """Play a WAV file and block until playback finishes."""
    if not _PLAYBACK_AVAILABLE:
        print("SIRA: Voice generated, but no audio playback library is available.\n")
        return

    try:
        data, samplerate = sf.read(path, dtype="float32")
        sd.play(data, samplerate)
        sd.wait()  # Do not start listening again until playback is done
    except Exception as exc:  # noqa: BLE001 - keep playback errors from crashing SIRA
        print(f"SIRA: I generated a response but could not play the audio.\nDetails: {exc}\n")