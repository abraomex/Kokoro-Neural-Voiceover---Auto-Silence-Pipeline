import os
import warnings

# Hide the HuggingFace symlink and PyTorch warnings for a clean terminal
os.environ["HF_HUB_DISABLE_SYMLINKS_WARNING"] = "1"
warnings.filterwarnings("ignore")

from kokoro import KPipeline
import soundfile as sf
import numpy as np

INPUT_FILE = "script.txt"
OUTPUT_FILE = "kokoro_voiceover.wav"
SAMPLE_RATE = 24000

# 1. Read the script
with open(INPUT_FILE, "r", encoding="utf-8") as f:
    text = f.read().strip()

if not text:
    raise ValueError(f"'{INPUT_FILE}' is empty! Paste your narration text in it first.")

# 2. Initialize the Kokoro pipeline ('a' = American English)
print("Loading Kokoro model...")
pipeline = KPipeline(lang_code='a', repo_id='hexgrad/Kokoro-82M')

# 3. Blend two voices for a custom documentary narrator tone
# 65% conversational essayist (am_michael) + 35% deep narrator (am_adam)
print("Blending narrator voice...")
voice_michael = pipeline.load_voice('am_michael')
voice_adam = pipeline.load_voice('am_adam')
custom_voice = (voice_michael * 0.65) + (voice_adam * 0.35)

# 4. Generate audio chunk by chunk (0.95 speed for a calm documentary cadence)
print("Starting generation...\n")
generator = pipeline(text, voice=custom_voice, speed=0.95, split_pattern=r'\n+')

all_audio = []
pause = np.zeros(int(SAMPLE_RATE * 0.35), dtype=np.float32)  # 0.35s breath pause

for i, (gs, ps, audio) in enumerate(generator):
    preview = gs.replace("\n", " ")[:55]
    print(f"[Chunk {i+1:02d}] Rendering: {preview}...")
    all_audio.append(audio)
    all_audio.append(pause)

# 5. Combine and save the final WAV file
final_audio = np.concatenate(all_audio)
sf.write(OUTPUT_FILE, final_audio, SAMPLE_RATE)

duration_mins = (len(final_audio) / SAMPLE_RATE) / 60
print(f"\nDone! Saved '{OUTPUT_FILE}' ({duration_mins:.1f} minutes total).")