# ==========================================================================
# ----------------- TEXt settings (Step 1)
# ==========================================================================


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