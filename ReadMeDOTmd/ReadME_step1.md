# SIRA AI Assistant — V1 (Core)

SIRA is a personal AI assistant inspired by JARVIS. This is **Step 1**: a
minimal terminal-based conversational assistant that talks to a locally
running [Ollama](https://ollama.com) model and remembers the conversation
for as long as the session is running.

No voice, no GUI, no internet access, no automation — just a clean text
chat loop with memory for the current session. Later steps will build on
this foundation.

## 1. What SIRA is

SIRA sends your messages to a local LLM (via Ollama) using the
`/api/chat` endpoint, keeps track of the full conversation history in
memory, and prints SIRA's replies back to you in the terminal. SIRA has a
calm, professional, JARVIS-inspired personality defined in `config.py`.

## 2. Prerequisites

- Python 3.10+
- [Ollama](https://ollama.com) installed and running locally
- At least one Ollama model pulled (default: `llama3.2`)

## 3. Install Python dependencies

From the `sira/` directory:

```bash
pip install -r requirements.txt
```

## 4. Install and run Ollama

Install Ollama from https://ollama.com/download (macOS, Windows, Linux
installers available).

Start the Ollama server (it often starts automatically after install,
but you can start it manually):

```bash
ollama serve
```

By default it listens on `http://localhost:11434`, which matches
`OLLAMA_BASE_URL` in `config.py`.

## 5. Download the configured model

The default model is `llama3.2`. Pull it with:

```bash
ollama pull llama3.2
```

If you want to use a different model, pull that instead, e.g.:

```bash
ollama pull mistral
```

## 6. Start SIRA

With Ollama running in the background, start SIRA from the `sira/`
directory:

```bash
python main.py
```

Type your message and press Enter. Type `exit` or `quit` to close SIRA.

## 7. Changing the Ollama model

Open `config.py` and change:

```python
OLLAMA_MODEL = "llama3.2"
```

to the name of any model you have pulled locally, for example:

```python
OLLAMA_MODEL = "mistral"
```

No other code changes are needed.

## 8. Example conversation

```text
========================================
              SIRA AI
========================================
Local AI Assistant
Type 'exit' or 'quit' to close SIRA.

You: Hello SIRA

SIRA: Hello. How may I assist you?

You: My name is Alex.

SIRA: It's a pleasure to meet you, Alex.

You: What is my name?

SIRA: Your name is Alex.

You: exit

SIRA: Until next time.
```

## Project structure

```text
sira/
├── main.py           # Terminal interface + conversation loop
├── config.py          # Configuration: Ollama settings, system prompt, UI text
├── requirements.txt   # Python dependencies
└── README.md          # This file
```

## Notes

- Conversation history exists only for the current run of `main.py`. Closing
  SIRA clears it. Persistent memory will be added in a later step.
- If Ollama isn't running, or the configured model isn't pulled, SIRA will
  print a clear error message instead of crashing.