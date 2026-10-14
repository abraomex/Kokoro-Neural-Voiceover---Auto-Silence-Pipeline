# Kokoro Neural Voiceover & Auto-Silence Pipeline

A local, offline Python pipeline for generating natural documentary and explainer voiceovers using **Kokoro-82M**, paired with an automated RMS-based silence trimmer for punchy YouTube and animation pacing.

## Features
* **100% Free & Offline TTS:** Runs `hexgrad/Kokoro-82M` locally on CPU with no API keys or character limits.
* **Custom Voice Blending:** Mixes multiple voice tensors (`am_michael` + `am_adam`) to create a unique, warm documentary narrator tone.
* **Smart Silence Remover:** Scans audio in 20ms windows (`-42 dB` threshold) to strip dead air and tighten long pauses down to crisp `0.16s` beats without clipping soft consonants.

## Project Structure
* `kokoro_vo.py` — Reads `script.txt`, blends narrator voices, and renders the raw narration (`kokoro_voiceover.wav`).
* `remove_silence.py` — Standalone post-processor that strips dead air and tightens pauses (`kokoro_voiceover_tight.wav`).
* `script.txt` — Input narration script formatted for natural speech cadence.

## Setup & Installation

Because `kokoro` requires **Python 3.10–3.12**, use `uv` to create an isolated Python 3.12 virtual environment:

```powershell
# 1. Install uv (if not already installed)
pip install uv

# 2. Create a Python 3.12 virtual environment
python -m uv venv --python 3.12

# 3. Install Kokoro, SoundFile, and the spaCy English dictionary into .venv
python -m uv pip install --python .venv "kokoro>=0.9.2" soundfile pip [https://github.com/explosion/spacy-models/releases/download/en_core_web_sm-3.8.0/en_core_web_sm-3.8.0-py3-none-any.whl](https://github.com/explosion/spacy-models/releases/download/en_core_web_sm-3.8.0/en_core_web_sm-3.8.0-py3-none-any.whl)
```

## Usage

**1. Generate the Voiceover**
Paste your narration into `script.txt` and run:
```powershell
.\.venv\Scripts\python.exe kokoro_vo.py
```
*(Note: The first run automatically downloads and caches the ~327MB Kokoro model from Hugging Face).*

**2. Remove Dead Air & Tighten Pauses**
Run the standalone silence remover to tighten the pacing for video editing:
```powershell
.\.venv\Scripts\python.exe remove_silence.py
```

## Customization
* **Change Voices:** Inside `kokoro_vo.py`, adjust the tensor blend weights between `am_michael` (conversational essayist), `am_adam` (deep narrator), `bm_george` (British documentary), or `af_heart` (expressive female narrator).
* **Adjust Pacing:** Inside `remove_silence.py`, modify `KEEP_PAUSE_SEC` (`0.12` for fast-paced Shorts/animations, `0.22` for relaxed long-form essays).