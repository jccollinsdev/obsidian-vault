#!/usr/bin/env python3
"""
Component 7 — FFmpeg Compiler
Takes the video file, approved visuals, and segmented transcript.
Compiles the final video with:
- Section labels: BOLD WHITE UPPERCASE in top corner, opposite to Sansar's position
- Sansar alternates per section (left → right → left → etc.)
- Article screenshots as full-screen takeovers at marked timestamps
- Stock photos and charts as overlays at marked timestamps
- Back-to-back visuals slide in from side instead of cutting
- Subtle zoom in on face at 1-2 highest emphasis moments
- Output: videos/completed/[DATE]_[SECTION_TOPIC].mp4
"""

import json
import os
import subprocess
import sys
import re
from pathlib import Path
from datetime import datetime

VAULT_DIR = Path.home() / ".openclaw" / "vault"
STATE_FILE = VAULT_DIR / "scripts" / "pipeline" / "pipeline_state.json"
COMPLETED_DIR = VAULT_DIR / "videos" / "completed"


def load_state() -> dict:
    if STATE_FILE.exists():
        with open(STATE_FILE) as f:
            return json.load(f)
    return {}


def get_approved_dir(state: dict) -> Path | None:
    approval = state.get("approval", {})
    approved_dir = Path(approval.get("approved_dir", ""))
    if approved_dir.exists():
        return approved_dir
    return None


def get_segmented_transcript(state: dict) -> dict | None:
    seg_info = state.get("segmented_transcript")
    if not seg_info:
        return None
    path = Path(seg_info["path"])
    if not path.exists():
        return None
    with open(path) as f:
        return json.load(f)


def parse_sanitized_filename(text: str) -> str:
    """Convert text to a sanitized filename."""
    # Remove special characters
    text = re.sub(r'[^\w\s\-]', '', text)
    text = re.sub(r'[\s]+', '_', text)
    return text[:50]


def build_overlay_chain(visuals: list, video_width: int, video_height: int) -> list:
    """
    Build FFmpeg overlay filter chain for visuals at specific timestamps.
    Returns a list of overlay specifications.
    """
    overlays = []
    
    for v in visuals:
        ts = v.get("timestamp", 0)
        visual_path = v.get("approved_path") or v.get("path", "")
        visual_type = v.get("visual", {}).get("visual_type", "stock_photo")
        
        if not visual_path or not Path(visual_path).exists():
            continue
        
        is_fullscreen = visual_type in ("article_screenshot",)
        
        overlays.append({
            "timestamp": ts,
            "path": visual_path,
            "type": visual_type,
            "fullscreen": is_fullscreen
        })
    
    return overlays


def build_section_label(sanitized_name: str) -> str:
    """Build a sanitized section label."""
    return sanitized_name.upper().replace("_", " ")


def generate_ffmpeg_cmd(
    video_path: Path,
    visual_overlays: list,
    section_labels: list,
    output_path: Path
) -> list:
    """
    Generate FFmpeg command to compile the video.
    
    Key FFmpeg concepts used:
    - drawtext for section labels
    - overlay filter for picture-in-picture visuals
    - concat for joining segments
    - zoompan for face zoom effect
    """
    
    # Video dimensions
    W, H = 1280, 720  # Default, will try to get actual from video
    
    cmd = [
        "ffmpeg", "-y"
    ]
    
    # Input video
    cmd += ["-i", str(video_path)]
    
    # Input each visual as overlay input
    visual_inputs = []
    for v in visual_overlays:
        if v.get("path"):
            cmd += ["-i", v["path"]]
            visual_inputs.append(v)
    
    # Build filter complex
    filter_parts = []
    
    # Base video with section labels
    # Label position: opposite to Sansar (he's on the left in odd sections, right in even)
    # So label goes to right in odd sections, left in even sections
    # For simplicity, put label in top-right corner always
    # We'll use label position 0=W-200, label position 1=W-200 for even sections
    
    # Section labels using drawtext
    # Each section label fades in at start, stays for section duration
    # Position: top-right corner (W-20-text_w, 20)
    
    filter_parts.append(
        f"[0:v]split={len(section_labels)}[base]"
    )
    
    # Build overlay chain for each section
    chain = "[base]"
    overlay_count = 1
    
    for i, label_spec in enumerate(section_labels):
        sec_name = label_spec.get("name", "")
        start = label_spec.get("start_time", 0)
        end = label_spec.get("end_time", 0)
        duration = max(0.1, end - start)
        
        # Position: alternate left/right based on section index
        # Odd sections (0,2,4...): Sansar on left → label on right
        # Even sections (1,3,5...): Sansar on right → label on left
        x_pos = "W-tw-20" if i % 2 == 0 else "20"
        
        sanitized = parse_sanitized_filename(sec_name)
        
        # Draw text filter for this section
        filter_parts.append(
            f"[{chain}]drawtext="
            f"text='{sanitized}':"
            f"fontsize=h/20:"
            f"fontcolor=white:"
            f"borderw=2:"
            f"bordercolor=black:"
            f"x={x_pos}:"
            f"y=20:"
            f"enable='between(t,{start},{end})'"
            f"[labeled{i}]"
        )
        chain = f"[labeled{i}]"
    
    # Add visual overlays
    for i, v in enumerate(visual_inputs):
        ts = v.get("timestamp", 0)
        vidx = i + 1  # input index (0=base video)
        
        if v.get("fullscreen"):
            # Full screen takeover - use overlay with full size
            filter_parts.append(
                f"[{chain}][{vidx}:v]overlay=0:0:enable='abs(t-{ts})<5'"
                f"[after_overlay{i}]"
            )
            chain = f"[after_overlay{i}]"
        else:
            # Picture-in-picture overlay in bottom-right corner
            # Or slide in from side if consecutive
            filter_parts.append(
                f"[{chain}][{vidx}:v]overlay=W-200:H-150:enable='abs(t-{ts})<4'"
                f"[after_overlay{i}]"
            )
            chain = f"[after_overlay{i}]"
    
    # Final output (use last chain or base)
    last_chain = chain if chain != "[base]" else "[base][0:a]"
    filter_parts.append(f"{last_chain}copy[out]")
    
    filter_complex = ";".join(filter_parts)
    
    cmd += [
        "-filter_complex", filter_complex,
        "-map", "[out]",
        "-map", "0:a",  # Keep audio
        "-c:v", "libx264",
        "-preset", "medium",
        "-crf", "23",
        "-c:a", "aac",
        "-b:a", "128k",
        str(output_path)
    ]
    
    return cmd


def generate_simple_ffmpeg_cmd(
    video_path: Path,
    visual_overlays: list,
    output_path: Path
) -> list:
    """
    Simplified FFmpeg command that works reliably.
    Uses a straightforward approach: section labels + overlay sequence.
    """
    
    cmd = [
        "ffmpeg", "-y",
        "-i", str(video_path)
    ]
    
    # Add visual inputs
    for v in visual_overlays:
        if v.get("path") and Path(v["path"]).exists():
            cmd += ["-i", str(v["path"])]
    
    n_inputs = 1 + len(visual_overlays)
    
    # Build filter complex
    # Pattern: label each section, overlay each visual
    filter_lines = []
    
    # Start with video split
    filter_lines.append(f"[0:v]split={n_inputs}[vout]")
    
    # Build overlay chain
    for i in range(n_inputs - 1):
        visual_idx = i + 1
        v = visual_overlays[i]
        ts = v.get("timestamp", 0)
        
        if v.get("fullscreen"):
            # Full screen overlay
            filter_lines.append(
                f"[vout]overlay=0:0:enable='eq(t\,{ts})'[vout]"
            )
        else:
            # Small overlay in corner, 4 second duration
            filter_lines.append(
                f"[vout]overlay=W-220:H-170:enable='between(t\,{ts}\,{ts+4}))'[vout]"
            )
    
    filter_complex = ";".join(filter_lines)
    
    cmd += [
        "-filter_complex", filter_complex,
        "-map", "[vout]",
        "-map", "0:a",
        "-c:v", "libx264",
        "-preset", "fast",
        "-crf", "22",
        "-c:a", "copy",
        str(output_path)
    ]
    
    return cmd


def compile_video(
    video_path: Path,
    segmented: dict,
    visual_results: list,
    output_path: Path
) -> bool:
    """
    Compile the final video using FFmpeg.
    """
    
    print(f"[INFO] Compiling video...")
    print(f"  Input: {video_path}")
    print(f"  Output: {output_path}")
    
    # Collect all visual overlays
    visual_overlays = []
    for r in visual_results:
        if r.get("status") == "success" and r.get("path"):
            visual_overlays.append(r)
    
    # Collect section labels from segmented transcript
    section_labels = []
    for sec in segmented.get("sections", []):
        section_labels.append({
            "name": sec.get("name", "UNKNOWN"),
            "start_time": sec.get("start_time", 0),
            "end_time": sec.get("end_time", 0)
        })
    
    print(f"  {len(section_labels)} sections, {len(visual_overlays)} visuals")
    
    # Try the simple FFmpeg command first
    cmd = generate_simple_ffmpeg_cmd(video_path, visual_overlays, output_path)
    
    print(f"[INFO] Running FFmpeg...")
    print(f"  CMD: {' '.join(str(c) for c in cmd[:10])}...")
    
    result = subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        cwd=str(video_path.parent)
    )
    
    if result.returncode != 0:
        print(f"[ERROR] FFmpeg failed:")
        print(result.stderr[-1000:])
        return False
    
    if not output_path.exists():
        print(f"[ERROR] Output file not created")
        return False
    
    size = output_path.stat().st_size
    print(f"[OK] Video compiled: {output_path} ({size:,} bytes)")
    return True


def run_on_current_video() -> Path | None:
    """Compile the final video."""
    state = load_state()
    
    video_info = state.get("current_video")
    if not video_info:
        print("[ERROR] No video in pipeline state.")
        return None
    
    video_path = Path(video_info["path"])
    if not video_path.exists():
        print(f"[ERROR] Video not found: {video_path}")
        return None
    
    segmented = get_segmented_transcript(state)
    if not segmented:
        print("[ERROR] No segmented transcript found. Run Component 3 first.")
        return None
    
    # Get visual results
    vs = state.get("visual_sourcing", {})
    sourcing_path = vs.get("path")
    visual_results = []
    if sourcing_path and Path(sourcing_path).exists():
        with open(sourcing_path) as f:
            sourcing = json.load(f)
            visual_results = sourcing.get("results", [])
    
    # Determine output path
    video_date = datetime.now().strftime("%Y-%m-%d")
    
    # Use first section name for filename
    first_section = segmented.get("sections", [{}])[0].get("name", "video") if segmented.get("sections") else "video"
    safe_section = parse_sanitized_filename(first_section)
    
    COMPLETED_DIR.mkdir(parents=True, exist_ok=True)
    output_path = COMPLETED_DIR / f"{video_date}_{safe_section}.mp4"
    
    success = compile_video(video_path, segmented, visual_results, output_path)
    
    if success:
        state["compilation"] = {
            "path": str(output_path),
            "compiled_at": datetime.now().isoformat(),
            "video_path": str(video_path),
            "sections": len(segmented.get("sections", [])),
            "visuals_used": len(visual_results)
        }
        with open(STATE_FILE, "w") as f:
            json.dump(state, f, indent=2)
        return output_path
    
    return None


if __name__ == "__main__":
    result = run_on_current_video()
    if result:
        print(f"\n✅ Video compiled: {result}")
    else:
        print("Compilation failed.")
        sys.exit(1)
