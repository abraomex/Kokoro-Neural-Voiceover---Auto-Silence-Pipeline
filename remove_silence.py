import soundfile as sf
import numpy as np

INPUT_WAV = "kokoro_voiceover.wav"
OUTPUT_WAV = "kokoro_voiceover_tight.wav"

# --- TUNING SETTINGS ---
THRESHOLD_DB = -42.0   # Anything quieter than -42 dB is treated as silence
MAX_PAUSE_SEC = 0.25   # Any silence longer than 0.25s gets trimmed
KEEP_PAUSE_SEC = 0.18  # How much natural breathing room to leave behind (0.15s - 0.25s is ideal)

def trim_silences(audio, sr, threshold_db, max_pause_sec, keep_pause_sec):
    # Convert decibel threshold to linear amplitude
    threshold = 10 ** (threshold_db / 20.0)
    
    # Analyze in 20ms windows
    frame_len = int(sr * 0.02)
    num_frames = len(audio) // frame_len
    
    if num_frames == 0:
        return audio

    # Handle both mono and stereo audio
    trimmed = audio[:num_frames * frame_len]
    if audio.ndim > 1:
        frames = trimmed.reshape(num_frames, frame_len, audio.shape[1])
        rms = np.sqrt(np.mean(frames ** 2, axis=(1, 2)))
    else:
        frames = trimmed.reshape(num_frames, frame_len)
        rms = np.sqrt(np.mean(frames ** 2, axis=1))

    is_loud = rms > threshold

    # Add a tiny 1-frame buffer before/after speech so word endings ("s", "t") never get clipped
    is_speech = np.copy(is_loud)
    is_speech[1:] |= is_loud[:-1]
    is_speech[:-1] |= is_loud[1:]

    max_silent_frames = int(max_pause_sec / 0.02)
    keep_silent_frames = int(keep_pause_sec / 0.02)

    output_chunks = []
    silent_count = 0

    for i in range(num_frames):
        if is_speech[i]:
            if silent_count > 0:
                # Keep the full silence if it's already short; otherwise cap it at KEEP_PAUSE_SEC
                frames_to_keep = min(silent_count, keep_silent_frames) if silent_count > max_silent_frames else silent_count
                if frames_to_keep > 0:
                    start_idx = (i - silent_count) * frame_len
                    end_idx = start_idx + (frames_to_keep * frame_len)
                    output_chunks.append(audio[start_idx:end_idx])
                silent_count = 0
            output_chunks.append(frames[i])
        else:
            silent_count += 1

    return np.concatenate(output_chunks, axis=0) if output_chunks else audio

if __name__ == "__main__":
    print(f"Loading '{INPUT_WAV}'...")
    audio, sr = sf.read(INPUT_WAV, dtype="float32")
    orig_duration = len(audio) / sr

    print("Removing dead air and tightening pauses...")
    tight_audio = trim_silences(audio, sr, THRESHOLD_DB, MAX_PAUSE_SEC, KEEP_PAUSE_SEC)
    new_duration = len(tight_audio) / sr

    sf.write(OUTPUT_WAV, tight_audio, sr)
    saved_sec = orig_duration - new_duration
    print(f"Done! Saved '{OUTPUT_WAV}'")
    print(f"Original: {orig_duration:.1f}s -> New: {new_duration:.1f}s (Cut {saved_sec:.1f} seconds of silence!)")