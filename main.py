"""
SIRA AI Assistant - Always Listening + Wake Word (V3 / Step 3)
"""

from typing import List

from config import APP_BANNER, EXIT_COMMANDS, MAX_CONSECUTIVE_SILENCES
from ollama_client import Message, build_initial_history, ask_sira, warm_up_model
from audio_recorder import record_audio
from speech_to_text import transcribe_audio
from text_to_speech import speak
from wake_word import wait_for_wake_word


def user_requested_exit(text: str) -> bool:
    normalized = text.strip().lower()
    return normalized in EXIT_COMMANDS or any(
        normalized.endswith(cmd) for cmd in EXIT_COMMANDS
    )


def handle_command(conversation_history: List[Message]) -> bool:
    """
    Runs one full record -> transcribe -> ollama -> speak cycle after the
    wake word was heard. Returns False if SIRA should shut down entirely.
    """
    consecutive_silences = 0

    while True:
        audio = record_audio()
        if audio is None:
            return True  # mic hiccup - go back to wake-word listening

        text = transcribe_audio(audio)
        if text is None:
            return True

        if not text.strip():
            consecutive_silences += 1
            if consecutive_silences >= MAX_CONSECUTIVE_SILENCES:
                return True  # heard nothing - go back to waiting for wake word
            continue

        print(f"\nYou: {text}")

        if user_requested_exit(text):
            speak("Until next time.")
            return False

        conversation_history.append({"role": "user", "content": text})
        response = ask_sira(conversation_history)

        if response is None:
            conversation_history.pop()
            return True

        conversation_history.append({"role": "assistant", "content": response})
        speak(response)
        return True


def main() -> None:
    print(APP_BANNER)

    warm_up_model()

    conversation_history: List[Message] = build_initial_history()

    print("SIRA is ready.")
    print("Waiting for wake word...\n")

    while True:
        detected = wait_for_wake_word()

        if not detected:
            # Mic or wake-word model unavailable - can't recover, stop cleanly.
            break

        print("Wake word detected!")

        keep_running = handle_command(conversation_history)

        if not keep_running:
            break

        print("\nWaiting for wake word...\n")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nSIRA: Until next time.")