# SIRA AI Assistant — V2 (Voice Input + Voice Output)

SIRA is a personal AI assistant inspired by JARVIS. **Step 2** adds a fully
local voice pipeline on top of the Step 1 text engine:

```text
MICROPHONE -> FASTER-WHISPER -> TEXT -> CONVERSATION HISTORY -> OLLAMA
   -> SIRA RESPONSE -> PIPER -> AUDIO -> SPEAKER
```

Everything runs on your machine. No cloud speech-to-text, no cloud
text-to-speech.

Not included yet: wake word, always-listening mode, GUI, web search,
computer control, or long-term memory. Those come in later steps.

## Project structure

```text
sira/
├── main.py            # Coordinates the full voice loop
├── config.py           # All configuration (Ollama, Whisper, recording, Piper)
├── ollama_client.py    # ONLY talks to Ollama
├── audio_recorder.py   # ONLY records from the microphone
├── speech_to_text.py   # ONLY transcribes audio with Faster-Whisper
├── text_to_speech.py   # ONLY synthesizes + plays speech with Piper
├── requirements.txt
└── README.md
```

## Step 1 — Python environment

```bash
python -m venv venv
```

Windows:
```bash
venv\Scripts\activate
```

Linux/macOS:
```bash
source venv/bin/activate
```

## Step 2 — Install Python dependencies

```bash
pip install -r requirements.txt
```

This installs `requests`, `faster-whisper`, `sounddevice`, `soundfile`,
and `numpy`. Piper is installed separately (Step 6 below).

> **Windows note:** `sounddevice` needs the PortAudio library, which
> normally ships with the pip package. If you get a PortAudio error,
> install the "Microsoft Visual C++ Redistributable" or reinstall
> `sounddevice`.

## Step 3 — Start Ollama

Make sure Ollama is installed and running:

```bash
ollama serve
```

It listens on `http://localhost:11434` by default, matching
`OLLAMA_BASE_URL` in `config.py`.

## Step 4 — Download the configured Ollama model

The default model is `llama3.2`:

```bash
ollama pull llama3.2
```

To use a different model, pull it and update `OLLAMA_MODEL` in
`config.py`.

## Step 5 — Install Faster-Whisper

Already included in `requirements.txt`. No separate install needed —
but note that **the first time SIRA runs**, Faster-Whisper will
download the chosen model (`WHISPER_MODEL` in `config.py`, default
`"small"`) from Hugging Face, so the first startup needs internet
access and may take a minute. After that it's cached locally and works
offline.

To change accuracy/speed, edit in `config.py`:

```python
WHISPER_MODEL = "small"   # try "tiny" or "base" for speed, "medium"/"large-v3" for accuracy
WHISPER_DEVICE = "cpu"    # set to "cuda" if you have a supported NVIDIA GPU
```

## Step 6 — Install Piper

Piper is a standalone executable, not a Python package, so install it
for your OS:

- **Windows / Linux / macOS binaries:** download from the official
  releases page: https://github.com/rhasspy/piper/releases
  Extract the archive and note the path to `piper.exe` (Windows) or
  `piper` (Linux/macOS).
- Alternatively on Linux you may be able to install via your package
  manager or `pip install piper-tts` (a Python wrapper), depending on
  your platform — check the Piper repo for the current recommended
  method for your OS.

Download a voice model (`.onnx` + matching `.onnx.json`) from:
https://github.com/rhasspy/piper/blob/master/VOICES.md

For example, `en_US-lessac-medium.onnx` and
`en_US-lessac-medium.onnx.json`. Put both files in a folder such as
`sira/voices/`.

## Step 7 — Configure Piper

In `config.py`, set the executable path and voice model path to match
where you installed/downloaded them:

```python
# If piper.exe / piper is on your system PATH, the name alone works:
PIPER_EXECUTABLE = "piper"
# Otherwise use a full path, e.g.:
# PIPER_EXECUTABLE = r"C:\tools\piper\piper.exe"

PIPER_MODEL = "voices/en_US-lessac-medium.onnx"
```

If Piper or the voice model can't be found, SIRA will still print and
process responses normally — it will just tell you that voice output
is unavailable instead of crashing.

## Step 8 — Start SIRA

```bash
python main.py
```

You'll see:

```text
========================================
              SIRA AI
========================================
Voice mode: ON

Loading model 'llama3.2' into memory, please wait...

Loading speech recognition model 'small', please wait...

Listening...
```

Speak into your microphone. SIRA records for a fixed duration
(`RECORD_SECONDS` in `config.py`, default 5 seconds), transcribes what
you said, sends it to Ollama with full conversation history, and
speaks the reply aloud while also printing it.

### Example

```text
Listening...

You: My name is Alex.

SIRA: It's a pleasure to meet you, Alex.

Listening...

You: What is my name?

SIRA: Your name is Alex.

Listening...

You: Goodbye SIRA

SIRA: Until next time.
```

### Exiting

Say any of: `exit`, `quit`, `goodbye`, `shutdown`, `stop` (or a phrase
ending in one of these, e.g. "Goodbye SIRA"). You can also press
`Ctrl+C` at any time.

## Adjusting recording length

`RECORD_SECONDS` in `config.py` controls how long SIRA listens per
turn. This is a simple fixed-duration approach for now — automatic
silence detection will be added in a later step.

## Troubleshooting

| Message | Meaning |
|---|---|
| `I cannot access the microphone.` | `sounddevice`/PortAudio isn't available, or no mic permission. Check OS mic settings. |
| `The speech recognition model could not be loaded.` | Faster-Whisper failed to load — check internet access on first run, or disk space. |
| `I cannot connect to the local AI engine.` | Ollama isn't running. Run `ollama serve`. |
| `I can generate a response, but the voice engine is unavailable.` | Piper executable or voice model path in `config.py` is wrong, or Piper isn't installed. Text output still works. |