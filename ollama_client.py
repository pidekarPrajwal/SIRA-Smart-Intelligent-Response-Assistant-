"""
ollama_client.py

Handles ONLY communication with the local Ollama server, plus the
tool-call loop that lets SIRA request JSON tool calls and get natural
language back. No terminal I/O beyond debug/error prints, no audio.
"""

import json
from typing import List, Dict, Optional, Any

import requests

from config import (
    OLLAMA_CHAT_ENDPOINT,
    OLLAMA_MODEL,
    OLLAMA_BASE_URL,
    REQUEST_TIMEOUT_SECONDS,
    SIRA_SYSTEM_PROMPT,
    TOOLS_SYSTEM_PROMPT_ADDENDUM,
    MAX_TOOL_CALLS,
    DEBUG,
)
from tools.registry import execute_tool

Message = Dict[str, str]


def build_initial_history() -> List[Message]:
    """Create the starting conversation history with SIRA's system prompt."""
    full_prompt = SIRA_SYSTEM_PROMPT + TOOLS_SYSTEM_PROMPT_ADDENDUM
    return [{"role": "system", "content": full_prompt}]


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


def _try_parse_tool_call(raw_text: str) -> Optional[Dict[str, Any]]:
    """
    Try to parse `raw_text` as a SIRA tool-call JSON object.
    Returns the parsed dict if it's a well-formed {"type": "tool_call", ...}
    object, otherwise None (treated as a normal natural-language reply).
    Never raises.
    """
    stripped = raw_text.strip()

    # Only attempt JSON parsing if it actually looks like a JSON object -
    # avoids wasting time/errors on normal sentences.
    if not (stripped.startswith("{") and stripped.endswith("}")):
        return None

    try:
        parsed = json.loads(stripped)
    except (ValueError, TypeError):
        return None

    if not isinstance(parsed, dict):
        return None

    if parsed.get("type") != "tool_call":
        return None

    if "tool" not in parsed or "arguments" not in parsed:
        return None

    return parsed


def ask_sira(messages: List[Message]) -> Optional[str]:
    """
    Send `messages` to Ollama and handle the full tool-call loop:

      response = ask_ollama(messages)
      while response is a tool_call:
          execute the tool
          append assistant + tool messages
          response = ask_ollama(messages)

    Returns SIRA's final natural-language reply, or None on failure.
    `messages` is mutated in place so the caller's conversation history
    stays in sync with what actually happened (including tool calls).
    """
    tool_calls_made = 0

    while True:
        raw_reply = send_chat_request(messages)

        if raw_reply is None:
            return None

        tool_call = _try_parse_tool_call(raw_reply)

        if tool_call is None:
            # Normal natural-language response - we're done.
            return raw_reply

        tool_name = tool_call.get("tool")
        arguments = tool_call.get("arguments", {})

        if DEBUG:
            print(f"SIRA: Tool requested -> {tool_name}")

        tool_calls_made += 1
        if tool_calls_made > MAX_TOOL_CALLS:
            print("SIRA: Too many tool calls were requested. Stopping to avoid a loop.")
            return "I'm having trouble completing that action. Could you try again?"

        result = execute_tool(tool_name, arguments)

        if DEBUG:
            status = "Success" if result.get("success") else f"Failed - {result.get('error')}"
            print(f"Tool result: {status}")

        # Record what happened so SIRA has context for its next reply.
        messages.append({"role": "assistant", "content": raw_reply})
        messages.append({"role": "tool", "content": json.dumps(result)})

        # Loop again: ask Ollama to turn the tool result into a spoken reply.