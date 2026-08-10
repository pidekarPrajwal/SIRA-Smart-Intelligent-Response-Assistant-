"""
SIRA AI Assistant - Core (V1 / Step 1)

A minimal terminal-based conversational assistant backed by a locally
running Ollama server. This module is split into two concerns:

- Ollama communication (send_chat_request)
- Terminal interface / conversation loop (main)
"""

from __future__ import annotations

import sys
from typing import List, Dict, Optional

import requests

from config import (
    OLLAMA_CHAT_ENDPOINT,
    OLLAMA_MODEL,
    OLLAMA_BASE_URL,
    REQUEST_TIMEOUT_SECONDS,
    SIRA_SYSTEM_PROMPT,
    APP_BANNER,
    EXIT_COMMANDS,
)

Message = Dict[str, str]


def build_initial_history() -> List[Message]:
    """Create the starting conversation history with SIRA's system prompt."""
    return [{"role": "system", "content": SIRA_SYSTEM_PROMPT}]


def send_chat_request(messages: List[Message]) -> Optional[str]:
    """
    Send the full conversation history to Ollama's /api/chat endpoint
    and return SIRA's reply text, or None if something went wrong
    (the caller is responsible for printing a user-friendly error).
    """
    payload = {
        "model": OLLAMA_MODEL,
        "messages": messages,
        "stream": False,
    }

    try:
        response = requests.post(
            OLLAMA_CHAT_ENDPOINT,
            json=payload,
            timeout=REQUEST_TIMEOUT_SECONDS,
        )
    except requests.exceptions.ConnectionError:
        print(
            "\nSIRA: I cannot connect to the local Ollama server.\n"
            f"Please make sure Ollama is running at {OLLAMA_BASE_URL}.\n"
        )
        return None
    except requests.exceptions.Timeout:
        print(
            "\nSIRA: The request to Ollama timed out.\n"
            "The model may be taking too long to respond. Please try again.\n"
        )
        return None
    except requests.exceptions.RequestException as exc:
        print(f"\nSIRA: An unexpected network error occurred: {exc}\n")
        return None

    if response.status_code == 404:
        print(
            f"\nSIRA: The model '{OLLAMA_MODEL}' does not appear to be available.\n"
            f"Pull it first with: ollama pull {OLLAMA_MODEL}\n"
        )
        return None

    if response.status_code != 200:
        print(
            f"\nSIRA: Ollama returned an unexpected status code ({response.status_code}).\n"
            f"Details: {response.text}\n"
        )
        return None

    try:
        data = response.json()
        reply = data["message"]["content"]
    except (ValueError, KeyError, TypeError):
        print("\nSIRA: I received an invalid response from Ollama. Please try again.\n")
        return None

    if not reply or not reply.strip():
        print("\nSIRA: I received an empty response from Ollama. Please try again.\n")
        return None

    return reply.strip()


def get_user_input() -> str:
    """Prompt the user and return trimmed input. Handles Ctrl+C / Ctrl+D gracefully."""
    try:
        return input("You: ").strip()
    except (EOFError, KeyboardInterrupt):
        print("\n\nSIRA: Until next time.")
        sys.exit(0)


def main() -> None:
    print(APP_BANNER)

    conversation_history: List[Message] = build_initial_history()

    while True:
        user_input = get_user_input()

        if not user_input:
            print("\nSIRA: I did not receive any input. Please say something.\n")
            continue

        if user_input.lower() in EXIT_COMMANDS:
            print("\nSIRA: Until next time.")
            break

        conversation_history.append({"role": "user", "content": user_input})

        reply = send_chat_request(conversation_history)

        if reply is None:
            # Remove the last user message so a failed request doesn't
            # pollute history with an unanswered turn.
            conversation_history.pop()
            continue

        conversation_history.append({"role": "assistant", "content": reply})
        print(f"\nSIRA: {reply}\n")


if __name__ == "__main__":
    main()