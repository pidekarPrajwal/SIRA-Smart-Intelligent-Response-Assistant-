"""
Configuration for SIRA AI Assistant.

Keep all tunable settings here so other modules stay free of hardcoded values.
"""

# --- Ollama connection settings ---
OLLAMA_BASE_URL = "http://localhost:11434"
OLLAMA_CHAT_ENDPOINT = f"{OLLAMA_BASE_URL}/api/chat"

# Change this to any model you have pulled locally (e.g. "llama3.2", "mistral", "qwen2.5").
OLLAMA_MODEL = "llama3.2"

# Request timeout in seconds. The FIRST request after starting Ollama can be
# slow because the model has to load into memory - give it plenty of room.
REQUEST_TIMEOUT_SECONDS = 300

# --- SIRA personality ---
SIRA_SYSTEM_PROMPT = """You are SIRA, a highly intelligent personal AI assistant inspired by JARVIS.

Your personality:
- Calm
- Intelligent
- Professional
- Helpful
- Concise
- Confident
- Slightly witty when appropriate
- Respectful

You are SIRA, not JARVIS.
Always identify yourself as SIRA when appropriate.

Communicate naturally with the user.
Understand context from previous messages in the conversation.
Do not unnecessarily repeat information.
Keep answers concise unless the user asks for detailed explanations.

You are currently running as a local AI assistant through Ollama.
At this stage you are a conversational assistant only.
Do not claim to control the user's computer, access files, control devices,
browse the internet, or perform actions unless those capabilities are actually implemented.
"""

# --- Terminal UI text ---
APP_BANNER = """========================================
              SIRA AI
========================================
Voice mode: ON
"""

EXIT_COMMANDS = {"exit", "quit", "goodbye", "goodbye sira", "shutdown", "stop"}

# ==========================================================================
# Voice settings (Step 2)
# ==========================================================================

# --- Microphone / recording settings ---
SAMPLE_RATE = 16000          # Whisper expects 16kHz mono audio
CHANNELS = 1
RECORD_SECONDS = 7           # Simple fixed-duration recording (V1 of voice mode)

# If SIRA hears nothing (empty transcription) this many times in a row,
# say goodbye and exit instead of listening forever.
MAX_CONSECUTIVE_SILENCES = 1

# --- Speech-to-Text (Faster-Whisper) settings ---
WHISPER_MODEL = "small"      # tiny | base | small | medium | large-v3 ...
WHISPER_DEVICE = "cpu"       # "cpu" or "cuda" if you have a compatible GPU
WHISPER_COMPUTE_TYPE = "int8"  # int8 is a good balance of speed/accuracy on CPU

# --- Text-to-Speech (Piper) settings ---
# Path to the Piper executable. On Windows this is typically "piper.exe",
# on Linux/macOS it is usually just "piper" if it's on your PATH, or a
# full path to the binary you downloaded. See README for install steps.
PIPER_EXECUTABLE = "piper"

# Path to the Piper voice model (.onnx file). Download a voice from
# https://github.com/rhasspy/piper/blob/master/VOICES.md and point this
# at the .onnx file (a matching .onnx.json must sit next to it).
PIPER_MODEL = "voices/en_US-lessac-medium.onnx"

# Where Piper writes the generated speech before playback.
TTS_OUTPUT_FILE = "sira_response.wav"

# ==========================================================================
# Wake-word settings (Step 3)
# ==========================================================================

# openWakeWord ships pre-trained models like "hey_jarvis", "alexa", "hey_mycroft".
# A pre-trained "hey_sira" model does not exist yet, so we default to a
# working pre-trained model for testing. Swap WAKE_WORD_MODEL to a custom
# "hey_sira" .onnx/.tflite file once you train one (not part of this step).
WAKE_WORD_MODEL = "hey_jarvis"   # name of built-in model OR path to custom model file
WAKE_WORD = "hey_sira"           # display name only - used in prints, not detection

# Confidence threshold (0-1) above which a frame counts as "wake word detected".
WAKE_WORD_THRESHOLD = 0.5

# Frame size openWakeWord expects, in samples, at 16kHz (80ms chunks).
WAKE_WORD_FRAME_SAMPLES = 1280

# ==========================================================================
# Tools & Actions settings (Step 4)
# ==========================================================================

DEBUG = True  # Set False to hide raw JSON/tool-call debug prints

# Safety cap on how many tool calls Ollama can chain per single user request.
MAX_TOOL_CALLS = 3

# --- open_app whitelist ---
# Only these names may be opened. The LLM can never run arbitrary commands.
# Values are the actual command/executable launched on this OS.
ALLOWED_APPS = {
    "chrome": "chrome",
    "notepad": "notepad",
    "calculator": "calc",
}

# --- Weather tool ---
# Get a free API key from https://openweathermap.org/api and set it as an
# environment variable so it never lives in source code:
#   Windows (PowerShell):  $env:OPENWEATHER_API_KEY = "your_key_here"
#   Linux/macOS:            export OPENWEATHER_API_KEY="your_key_here"
import os  # noqa: E402
OPENWEATHER_API_KEY = os.environ.get("OPENWEATHER_API_KEY", "")

# --- Web search tool ---
# Uses DuckDuckGo's HTML endpoint (no API key required) for basic local use.
WEB_SEARCH_MAX_RESULTS = 3

# --- Tool-calling system prompt addendum ---
# Appended to SIRA_SYSTEM_PROMPT so the base personality is unchanged.
TOOLS_SYSTEM_PROMPT_ADDENDUM = """

You also have access to tools that let you take real actions. Use them only
when the user's request actually requires one of these actions.

When the user's request can be answered without a tool, respond normally
with plain natural language text (not JSON).

When a tool is required, respond with ONLY valid JSON, exactly in this
format, and nothing else (no Markdown, no explanation before or after):

{
    "type": "tool_call",
    "tool": "tool_name",
    "arguments": {
        "argument_name": "value"
    }
}

Available tools:

1. get_weather
   Description: Get the current weather for a city.
   Arguments: city (string)

2. open_app
   Description: Open an application on the user's computer. Only apps in
   the allowed list can be opened: chrome, notepad, calculator.
   Arguments: name (string)

3. search_web
   Description: Search the web for information.
   Arguments: query (string)

Do not invent tools that are not listed above.
Do not wrap the JSON in Markdown code fences.
Do not add any text before or after the JSON when calling a tool.

If no tool is required, you may also use this JSON form instead of plain
text if you prefer consistency, but plain natural language is preferred
for normal conversation:

{
    "type": "response",
    "content": "your normal response"
}
"""