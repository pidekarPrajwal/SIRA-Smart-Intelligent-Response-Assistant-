"""
SIRA AI Assistant - Voice Loop (V2 / Step 2)

Coordinates the full voice pipeline:

    microphone -> audio_recorder
               -> speech_to_text (Faster-Whisper)
               -> conversation history
               -> ollama_client (local Ollama LLM)
               -> text_to_speech (Piper)
               -> speaker

Text is also always printed to the terminal for debugging, per the
Step 1 behavior this step builds on.
"""

from typing import List

from config import APP_BANNER, EXIT_COMMANDS, MAX_CONSECUTIVE_SILENCES
from ollama_client import Message, build_initial_history, send_chat_request, warm_up_model
from audio_recorder import record_audio
from speech_to_text import transcribe_audio
from text_to_speech import speak


def user_requested_exit(text: str) -> bool:
    normalized = text.strip().lower()
    return normalized in EXIT_COMMANDS or any(
        normalized.endswith(cmd) for cmd in EXIT_COMMANDS
    )


def main() -> None:
    print(APP_BANNER)

    warm_up_model()  # Loads the Ollama model only - does NOT speak or print a reply

    conversation_history: List[Message] = build_initial_history()
    consecutive_silences = 0

    while True:
        audio = record_audio()

        if audio is None:
            break

        text = transcribe_audio(audio)

        if text is None:
            break

        if not text.strip():
            consecutive_silences += 1
            if consecutive_silences >= MAX_CONSECUTIVE_SILENCES:
                speak("I didn't hear anything. Until next time.")
                break
            continue

        consecutive_silences = 0  # reset once we hear something
        print(f"\nYou: {text}")

        if user_requested_exit(text):
            speak("Until next time.")
            break

        conversation_history.append({"role": "user", "content": text})

        response = send_chat_request(conversation_history)

        if response is None:
            conversation_history.pop()
            continue

        conversation_history.append({"role": "assistant", "content": response})
        speak(response)  # speak() also prints the text - only place this happens


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nSIRA: Until next time.")