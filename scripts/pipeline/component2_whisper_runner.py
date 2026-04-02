#!/usr/bin/env python3
"""
Component 2 — Whisper Runner
Takes a downloaded video file and runs it through Whisper locally.
Outputs a transcript JSON with word-level timestamps.
Saves alongside the video in videos/in_progress/.
"""

import os
import json
import subprocess
import sys
from pathlib import Path

VAULT_DIR = Path.home() / ".openclaw" / "vault"
IN_PROGRESS_DIR = VAULT_DIR / "videos" / "in_progress"
STATE_FILE = VAULT_DIR / "scripts" / "pipeline" / "pipeline_state.json"


def load_state() -> dict:
    if STATE_FILE.exists():
        with open(STATE_FILE) as f:
            return json.load(f)
    return {}


def save_state(state: dict):
    STATE_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(STATE_FILE, "w") as f:
        json.dump(state, f, indent=2)


def get_video_path(state: dict) -> Path | None:
    """Get the current video path from state."""
    current = state.get("current_video")
    if current:
        p = Path(current["path"])
        if p.exists():
            return p
    return None


def run_whisper(video_path: Path) -> Path | None:
    """Run Whisper on the video file and return the path to the output JSON."""
    output_dir = video_path.parent
    filename = video_path.stem  # without extension
    
    print(f"[INFO] Running Whisper on {video_path.name}...")
    print(f"[INFO] Output directory: {output_dir}")
    
    # Whisper command
    cmd = [
        "whisper",
        str(video_path),
        "--model", "small",  # Fast to download, good accuracy for testing
        "--output_dir", str(output_dir),
        "--output_format", "json",  # Only json to get word timestamps
        "--word_timestamps", "True",
        "--verbose", "False",
    ]
    
    result = subprocess.run(cmd, capture_output=True, text=True)
    
    if result.returncode != 0:
        print(f"[ERROR] Whisper failed: {result.stderr}")
        return None
    
    # Whisper outputs to --output_dir with same filename stem
    output_json = output_dir / f"{filename}.json"
    
    if not output_json.exists():
        print(f"[ERROR] Whisper output not found at {output_json}")
        return None
    
    print(f"[OK] Whisper transcript saved: {output_json}")
    return output_json


def validate_transcript(json_path: Path) -> bool:
    """Check that the transcript has word-level timestamps."""
    try:
        with open(json_path) as f:
            data = json.load(f)
        
        # Check for word-level timestamps
        if "segments" not in data:
            print("[WARN] No segments found in transcript")
            return False
        
        has_words = False
        total_words = 0
        for seg in data.get("segments", []):
            words = seg.get("words", [])
            total_words += len(words)
            if words:
                has_words = True
        
        print(f"[INFO] Transcript has {len(data['segments'])} segments, {total_words} words with timestamps")
        
        if has_words and total_words > 0:
            # Show a sample
            first_seg = data["segments"][0]
            if "words" in first_seg and first_seg["words"]:
                first_word = first_seg["words"][0]
                print(f"[INFO] Sample word: '{first_word.get('word', '')}' at {first_word.get('start', 0):.2f}s")
            print(f"[OK] Transcript validated with word-level timestamps")
            return True
        else:
            print("[WARN] Transcript appears to lack word-level timestamps")
            return False
            
    except Exception as e:
        print(f"[ERROR] Could not validate transcript: {e}")
        return False


def run_on_current_video() -> Path | None:
    """Run Whisper on the video specified in pipeline state."""
    state = load_state()
    video_path = get_video_path(state)
    
    if not video_path:
        print("[ERROR] No video in pipeline state. Run Component 1 first.")
        return None
    
    # Check if transcript already exists
    transcript_path = video_path.parent / f"{video_path.stem}.json"
    if transcript_path.exists():
        print(f"[INFO] Transcript already exists at {transcript_path}")
        if validate_transcript(transcript_path):
            # Update state with transcript info
            state["transcript"] = {
                "path": str(transcript_path),
                "generated_at": subprocess.run(
                    ["date", "+%Y-%m-%dT%H:%M:%S"], capture_output=True, text=True
                ).stdout.strip()
            }
            save_state(state)
            return transcript_path
        # If validation fails, regenerate
        print("[INFO] Regenerating transcript...")
    
    result = run_whisper(video_path)
    
    if result and validate_transcript(result):
        # Update state
        state["transcript"] = {"path": str(result), "generated_at": subprocess.run(
            ["date", "+%Y-%m-%dT%H:%M:%S"], capture_output=True, text=True
        ).stdout.strip()}
        save_state(state)
        return result
    
    return None


if __name__ == "__main__":
    result = run_on_current_video()
    if result:
        print(f"Transcript generated: {result}")
    else:
        print("Whisper failed. Check errors above.")
        sys.exit(1)
