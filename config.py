"""
Configuration for SIRA AI Assistant.

Keep all tunable settings here so main.py stays free of hardcoded values.
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
# --Systematic Intelligent Response Assistant--
# --- Terminal UI text ---
APP_BANNER = """========================================
              SIRA AI
========================================
--Systematic Intelligent Response Assistant--
Type 'exit' or 'quit' to close SIRA.
"""

EXIT_COMMANDS = {"exit", "quit", "bye"}