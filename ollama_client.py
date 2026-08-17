# ==========================================================================
# ----------------- Voice  settings (Step 2)
# ==========================================================================
"""
ollama_client.py

Handles ONLY communication with the local Ollama server.
No terminal I/O, no audio - just sending conversation history and
returning SIRA's reply text (or None on failure).
"""

from typing import List, Dict, Optional

import requests

from config import (
    OLLAMA_CHAT_ENDPOINT,
    OLLAMA_MODEL,
    OLLAMA_BASE_URL,
    REQUEST_TIMEOUT_SECONDS,
    SIRA_SYSTEM_PROMPT,
)

Message = Dict[str, str]


def build_initial_history() -> List[Message]:
    """Create the starting conversation history with SIRA's system prompt."""
    return [{"role": "system", "content": SIRA_SYSTEM_PROMPT}]


def send_chat_request(messages: List[Message]) -> Optional[str]:
    """
    Send the full conversation history to Ollama's /api/chat endpoint
    and return SIRA's reply text, or None if something went wrong
    (the caller is responsible for printing/speaking a user-friendly error).
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
            "\nSIRA: I cannot connect to the local AI engine.\n"
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


def warm_up_model() -> None:
    """
    Send a trivial request before the main loop starts so the (potentially
    slow) first-time model load happens now, with a clear message, instead
    of silently eating into the user's first real prompt.
    """
    print(f"Loading model '{OLLAMA_MODEL}' into memory, please wait...\n")
    warm_up_messages: List[Message] = [
        {"role": "system", "content": SIRA_SYSTEM_PROMPT},
        {"role": "user", "content": "Hello"},
    ]
    send_chat_request(warm_up_messages)