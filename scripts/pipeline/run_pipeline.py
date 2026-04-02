#!/usr/bin/env python3
"""
Post-Recording Pipeline Orchestrator
Runs all 7 components in sequence to go from email recording → compiled video.

Components:
1. Email Monitor - watches for recording emails, downloads video
2. Whisper Runner - transcribes video with word-level timestamps
3. Topic Segmenter - matches transcript to script sections
4. Visual Proposer - proposes 3 visuals per section
5. Visual Sourcer - sources actual visuals (articles, photos, charts)
6. Telegram Approval Gate - gets approval on photos via Telegram
7. FFmpeg Compiler - compiles final video

Usage:
  python3 run_pipeline.py [--dry-run] [--component N]
  
  --dry-run: Use dummy video instead of waiting for email
  --component N: Start from component N (1-7)
"""

import os
import sys
import json
import subprocess
from pathlib import Path
from datetime import datetime

VAULT_DIR = Path.home() / ".openclaw" / "vault"
STATE_FILE = VAULT_DIR / "scripts" / "pipeline" / "pipeline_state.json"
COMPONENT_DIR = VAULT_DIR / "scripts" / "pipeline"

DRY_RUN_VIDEO = VAULT_DIR / "videos" / "in_progress" / "test_dummy_20260402.mp4"


def load_state() -> dict:
    if STATE_FILE.exists():
        with open(STATE_FILE) as f:
            return json.load(f)
    return {}


def save_state(state: dict):
    STATE_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(STATE_FILE, "w") as f:
        json.dump(state, f, indent=2)


def run_component(name: str, component_num: int, extra_args: list = None) -> bool:
    """Run a component script and return success status."""
    script_path = COMPONENT_DIR / f"component{component_num}_{name}.py"
    
    if not script_path.exists():
        print(f"[ERROR] Component script not found: {script_path}")
        return False
    
    cmd = ["python3", str(script_path)]
    if extra_args:
        cmd += extra_args
    
    print(f"\n{'='*60}")
    print(f"COMPONENT {component_num}: {name}")
    print(f"{'='*60}")
    
    result = subprocess.run(cmd, cwd=str(VAULT_DIR))
    
    if result.returncode != 0:
        print(f"\n[ERROR] Component {component_num} ({name}) failed with exit code {result.returncode}")
        return False
    
    print(f"\n[OK] Component {component_num} ({name}) completed successfully")
    return True


def setup_dry_run_state():
    """Set up state for a dry run with the test video."""
    if not DRY_RUN_VIDEO.exists():
        print(f"[ERROR] Dry run video not found: {DRY_RUN_VIDEO}")
        print("      Creating a test video first...")
        # Create a simple test video
        test_video = DRY_RUN_VIDEO.parent / "test_dummy_20260402.mp4"
        test_video.parent.mkdir(parents=True, exist_ok=True)
        subprocess.run([
            "ffmpeg", "-f", "lavfi", "-i", "color=c=blue:s=1280x720:d=5",
            "-f", "lavfi", "-i", "anullsrc=channel_layout=stereo:sample_rate=44100",
            "-c:v", "libx264", "-c:a", "aac", "-shortest",
            str(test_video), "-y"
        ], capture_output=True)
    
    state = {
        "processed_message_ids": [],
        "current_video": {
            "path": str(DRY_RUN_VIDEO),
            "message_id": "dry_run",
            "subject": "Dry Run Test Video",
            "downloaded_at": datetime.now().isoformat()
        }
    }
    save_state(state)
    print(f"[INFO] Dry run state set up with: {DRY_RUN_VIDEO}")


def run_full_pipeline(start_from: int = 1, dry_run: bool = False):
    """Run the full pipeline or a subset of components."""
    
    if dry_run:
        setup_dry_run_state()
    else:
        # Verify state has a video
        state = load_state()
        if not state.get("current_video"):
            print("[ERROR] No video in pipeline state.")
            print("       Run Component 1 (Email Monitor) first to download a recording.")
            return False
    
    components = [
        ("email_monitor", 1),
        ("whisper_runner", 2),
        ("topic_segmenter", 3),
        ("visual_proposer", 4),
        ("visual_sourcer", 5),
        ("telegram_approval", 6),
        ("ffmpeg_compiler", 7),
    ]
    
    for name, num in components:
        if num < start_from:
            print(f"[SKIP] Component {num} ({name}) - before start point")
            continue
        
        success = run_component(name, num)
        if not success:
            print(f"\n[ABORT] Pipeline stopped at Component {num} ({name})")
            return False
        
        # Brief pause between components
        if num < 7:
            print(f"[INFO] Component {num} done. Next: Component {num+1}")
    
    print(f"\n{'='*60}")
    print("🎉 PIPELINE COMPLETE!")
    print(f"{'='*60}")
    
    # Print final state summary
    state = load_state()
    print("\nFinal State Summary:")
    print(f"  Video: {state.get('current_video', {}).get('path', 'N/A')}")
    print(f"  Transcript: {state.get('transcript', {}).get('path', 'N/A')}")
    print(f"  Segmented: {state.get('segmented_transcript', {}).get('sections', 'N/A')} sections")
    print(f"  Visual plan: {state.get('visual_plan', {}).get('total_visuals', 'N/A')} visuals")
    print(f"  Sourcing: {state.get('visual_sourcing', {}).get('success', 'N/A')}/{state.get('visual_sourcing', {}).get('total', 'N/A')} successful")
    print(f"  Approval: {state.get('approval', {}).get('approved_count', 'N/A')} approved")
    print(f"  Compilation: {state.get('compilation', {}).get('path', 'N/A')}")
    
    return True


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Post-Recording Pipeline")
    parser.add_argument("--dry-run", action="store_true", help="Run with test video (no email needed)")
    parser.add_argument("--component", type=int, default=1, help="Start from component N (1-7)")
    args = parser.parse_args()
    
    if args.component < 1 or args.component > 7:
        print("[ERROR] --component must be between 1 and 7")
        sys.exit(1)
    
    success = run_full_pipeline(start_from=args.component, dry_run=args.dry_run)
    sys.exit(0 if success else 1)
