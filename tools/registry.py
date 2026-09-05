"""
tools/registry.py

Central registry of available tools + a safe executor. This is the ONLY
place tool names get mapped to real Python functions. Unknown tools are
always rejected. The LLM's output is never eval()'d or exec()'d.
"""

from typing import Dict, Any, Callable

from tools.weather import get_weather
from tools.applications import open_app
from tools.web_search import search_web

# Name -> callable. Add new tools here only.
TOOLS: Dict[str, Callable[..., Dict[str, Any]]] = {
    "get_weather": get_weather,
    "open_app": open_app,
    "search_web": search_web,
}

# Name -> expected argument names, for basic validation.
TOOL_ARG_SPEC: Dict[str, set] = {
    "get_weather": {"city"},
    "open_app": {"name"},
    "search_web": {"query"},
}

TOOL_DESCRIPTIONS = """
get_weather - Get the current weather for a city. Arguments: city (string)
open_app - Open a whitelisted application. Arguments: name (string)
search_web - Search the web for information. Arguments: query (string)
"""


def execute_tool(tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
    """
    Safely execute a registered tool by name.

    Returns a structured dict:
        {"success": True, "tool": name, "result": <tool's return dict>}
        {"success": False, "tool": name, "error": "..."}

    Never raises. Never executes anything not explicitly in TOOLS.
    """
    if not isinstance(tool_name, str) or tool_name not in TOOLS:
        return {"success": False, "tool": tool_name, "error": "Unknown or unregistered tool."}

    if not isinstance(arguments, dict):
        return {"success": False, "tool": tool_name, "error": "Invalid arguments format."}

    expected_args = TOOL_ARG_SPEC.get(tool_name, set())
    # Only pass through arguments we actually expect - never forward unknown kwargs.
    filtered_args = {k: v for k, v in arguments.items() if k in expected_args}

    missing = expected_args - filtered_args.keys()
    if missing:
        return {
            "success": False,
            "tool": tool_name,
            "error": f"Missing required argument(s): {', '.join(sorted(missing))}",
        }

    tool_function = TOOLS[tool_name]

    try:
        result = tool_function(**filtered_args)
    except Exception as exc:  # noqa: BLE001 - a tool must never crash SIRA
        return {"success": False, "tool": tool_name, "error": f"Tool raised an error: {exc}"}

    if isinstance(result, dict) and "error" in result:
        return {"success": False, "tool": tool_name, "error": result["error"]}

    return {"success": True, "tool": tool_name, "result": result}