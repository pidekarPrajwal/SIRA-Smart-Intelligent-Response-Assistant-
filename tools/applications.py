"""
tools/applications.py

Handles ONLY opening whitelisted applications. Never runs LLM-generated
shell commands - only the explicit ALLOWED_APPS mapping decides what runs.
"""

import platform
import subprocess
from typing import Dict, Any

from config import ALLOWED_APPS


def open_app(name: str) -> Dict[str, Any]:
    """
    Open a whitelisted application by its friendly name.
    Returns a structured result dict - never raises.
    """
    if not name or not name.strip():
        return {"error": "No application name was provided."}

    key = name.strip().lower()

    if key not in ALLOWED_APPS:
        return {"error": "I don't have permission to open that application yet."}

    command = ALLOWED_APPS[key]

    try:
        system = platform.system()
        if system == "Windows":
            subprocess.Popen(["start", "", command], shell=True)
        elif system == "Darwin":
            subprocess.Popen(["open", "-a", command])
        else:  # Linux and others
            subprocess.Popen([command])
        return {"opened": key}
    except (OSError, FileNotFoundError) as exc:
        return {"error": f"Application was not found or could not be started: {exc}"}