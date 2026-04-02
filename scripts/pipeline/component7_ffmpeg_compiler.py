#!/usr/bin/env python3
"""
Component 7 — FFmpeg Compiler (Deterministic)
A clean, predictable FFmpeg pipeline that always works.
"""
import json, subprocess, sys, re
from pathlib import Path
from datetime import datetime

VAULT_DIR = Path.home() / ".openclaw" / "vault"
STATE_FILE = VAULT_DIR / "scripts" / "pipeline" / "pipeline_state.json"
COMPLETED_DIR = VAULT_DIR / "videos" / "completed"


def run_ffmpeg(cmd: list) -> tuple:
    result = subprocess.run(cmd, capture_output=True, text=True)
    return result.returncode == 0, result.stderr


def get_video_info(path: Path) -> dict:
    cmd = ["ffprobe", "-v", "quiet", "-print_format", "json", "-show_streams", str(path)]
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode != 0:
        return dict(width=1280, height=720, fps=25, duration=5.0)
    d = json.loads(r.stdout)
    for s in d.get("streams", []):
        if s.get("codec_type") == "video":
            fs = s.get("r_frame_rate", "25/1")
            if "/" in fs:
                num, den = fs.split("/")
                fps = int(num) / int(den)
            else:
                fps = float(fs)
            return dict(
                width=s.get("width", 1280),
                height=s.get("height", 720),
                fps=int(fps),
                duration=float(s.get("duration", 5.0))
            )
    return dict(width=1280, height=720, fps=25, duration=5.0)


def sanitize(text: str) -> str:
    return text.replace("\\", "\\\\").replace("'", "\\'").replace(":", "\\:")


def safe_name(text: str) -> str:
    return re.sub(r"[^\w\s\-]", "", re.sub(r"\s+", "_", text))[:50]


def compile_labels_and_export(
    video_path: Path,
    output_path: Path,
    sections: list,
) -> bool:
    """Compile video with only labels, no visuals."""
    info = get_video_info(video_path)
    W, H = info["width"], info["height"]
    
    filter_lines = ["[0:v]null[base]"]
    current = "[base]"
    
    for label_idx, (name, start, end) in enumerate(sections):
        if start >= end or start < 0:
            continue
        xpos = "W-tw-20" if label_idx % 2 == 0 else "20"
        safe_n = sanitize(name)
        out = f"[lbl{label_idx}]"
        filter_lines.append(
            f"{current}drawtext=text='{safe_n}':"
            f"fontsize={H//25}:fontcolor=white:borderw=3:bordercolor=black:"
            f"x={xpos}:y=20:"
            f"enable='between(t,{start},{end})'{out}"
        )
        current = out
    
    filter_lines.append(f"{current}null[outv]")
    
    cmd = [
        "ffmpeg", "-y", "-i", str(video_path),
        "-filter_complex", ";".join(filter_lines),
        "-map", "[outv]", "-map", "0:a",
        "-c:v", "libx264", "-preset", "fast", "-crf", "22",
        "-c:a", "aac", "-b:a", "128k",
        str(output_path)
    ]
    
    ok, stderr = run_ffmpeg(cmd)
    if not ok:
        print(f"[ERROR] FFmpeg failed:")
        for line in stderr.strip().split("\n")[-10:]:
            print(f"  {line}")
        return False
    
    return output_path.exists() and output_path.stat().st_size > 1000


def compile_video(
    video_path: Path,
    output_path: Path,
    sections: list,      # [(name, start_sec, end_sec), ...]
    visuals: list,      # [(timestamp, file_path, type), ...]
) -> bool:
    """
    Compile video with FFmpeg.
    
    sections: [(name, start, end), ...]
    visuals: [(timestamp, path, type), ...]  type in ('photo', 'article', 'chart')
    
    The key fix: overlay enable windows are respected. When an overlay's
    time window closes, it stops showing. The chain approach works because
    when overlay N's enable is false, it passes through its first input
    (the accumulated result from previous overlays), which at that point
    should just be the labeled base if all prior enables are also false.
    """
    info = get_video_info(video_path)
    W, H, fps = info["width"], info["height"], info["fps"]
    
    # Sort visuals by timestamp
    visuals = sorted(visuals, key=lambda x: x[0])
    
    # If no visuals, just compile with labels
    if not visuals:
        return compile_labels_and_export(video_path, output_path, sections)
    
    # Filter to only valid visuals
    valid_visuals = [(ts, vp, vt) for (ts, vp, vt) in visuals if vp and Path(vp).exists()]
    if not valid_visuals:
        return compile_labels_and_export(video_path, output_path, sections)
    
    # Build filter complex
    n_streams = 1 + len(valid_visuals)
    filter_lines = [f"[0:v]split={n_streams}[base]"]
    
    # Build label chain: [base] -> ... -> [labeled]
    label_idx = 0
    current = "[base]"
    for (name, start, end) in sections:
        if start >= end or start < 0:
            continue
        xpos = "W-tw-20" if label_idx % 2 == 0 else "20"
        safe_n = sanitize(name)
        out = f"[lbl{label_idx}]"
        filter_lines.append(
            f"{current}drawtext=text='{safe_n}':"
            f"fontsize={H//25}:fontcolor=white:borderw=3:bordercolor=black:"
            f"x={xpos}:y=20:"
            f"enable='between(t,{start},{end})'{out}"
        )
        current = out
        label_idx += 1
    labeled = current
    
    # Chain overlays: each overlay is applied with enable condition.
    # When overlay N's enable is false, it passes through the accumulated
    # result from previous overlays. If all prior overlays are also
    # disabled, this is just the labeled base.
    chain_current = labeled
    overlay_idx = 1
    
    for i, (ts, vpath, vtype) in enumerate(valid_visuals):
        inp = f"[{overlay_idx}:v]"
        ov_out = f"[ov{i}]"
        
        if vtype == "article":
            scaled = f"[scaled{i}]"
            filter_lines.append(f"{inp}scale={W}:{H}:force_original_aspect_ratio=increase{scaled}")
            filter_lines.append(
                f"{chain_current}{scaled}overlay=0:0:enable='between(t,{ts},{ts+4})'{ov_out}"
            )
        else:
            ow = int(W * 0.40)
            cx = W - ow - 20
            cy = H - int(H * 0.40) - 20
            scaled = f"[scaled{i}]"
            filter_lines.append(f"{inp}scale={ow}:-1{scaled}")
            filter_lines.append(
                f"{chain_current}{scaled}overlay={cx}:{cy}:enable='between(t,{ts},{ts+3})'{ov_out}"
            )
        
        chain_current = ov_out
        overlay_idx += 1
    
    filter_lines.append(f"{chain_current}null[outv]")
    
    filter_complex = ";".join(filter_lines)
    
    # Build command
    cmd = ["ffmpeg", "-y", "-i", str(video_path)]
    for (_, vpath, vtype) in visuals:
        if vpath and Path(vpath).exists():
            cmd += ["-i", str(vpath)]
    
    cmd += [
        "-filter_complex", filter_complex,
        "-map", "[outv]",
        "-map", "0:a",
        "-c:v", "libx264", "-preset", "fast", "-crf", "22",
        "-c:a", "aac", "-b:a", "128k",
        str(output_path)
    ]
    
    print(f"[INFO] FFmpeg filter_complex ({len(filter_lines)} stages):")
    for fl in filter_lines[:8]:
        print(f"  {fl[:120]}")
    if len(filter_lines) > 8:
        print(f"  ... and {len(filter_lines)-8} more")
    
    print(f"[INFO] Running FFmpeg...")
    ok, stderr = run_ffmpeg(cmd)
    
    if not ok:
        print(f"[ERROR] FFmpeg failed:")
        for line in stderr.strip().split("\n")[-15:]:
            print(f"  {line}")
        return False
    
    return output_path.exists() and output_path.stat().st_size > 1000


def run_on_current_video() -> Path:
    state = json.load(open(STATE_FILE)) if STATE_FILE.exists() else {}
    
    video_info = state.get("current_video", {})
    video_path = Path(video_info.get("path", ""))
    if not video_path.exists():
        raise FileNotFoundError(f"Video not found: {video_path}")
    
    # Load segmented transcript
    seg_path = Path(state.get("segmented_transcript", {}).get("path", ""))
    if not seg_path.exists():
        raise FileNotFoundError(f"Segmented transcript not found: {seg_path}")
    
    seg = json.load(open(seg_path))
    
    # Extract sections (name, start, end)
    sections = []
    for s in seg.get("sections", []):
        start = s.get("start_time", 0)
        end = s.get("end_time", 0)
        name = s.get("name", "UNKNOWN")
        if end > start:
            sections.append((name, start, end))
    
    # Fallback if no valid sections
    if not sections:
        info = get_video_info(video_path)
        sections = [
            ("SECTION_1", 0, info["duration"] * 0.25),
            ("SECTION_2", info["duration"] * 0.25, info["duration"] * 0.5),
            ("SECTION_3", info["duration"] * 0.5, info["duration"] * 0.75),
            ("SECTION_4", info["duration"] * 0.75, info["duration"]),
        ]
    
    # Extract visuals from sourcing results
    visuals = []
    sourcing_path = Path(state.get("visual_sourcing", {}).get("path", ""))
    if sourcing_path.exists():
        sourcing = json.load(open(sourcing_path))
        for r in sourcing.get("results", []):
            if r.get("status") == "success" and r.get("path"):
                ts = r.get("visual", {}).get("timestamp", 0)
                vtype = r.get("visual", {}).get("visual_type", "photo")
                vtype = "article" if vtype == "article_screenshot" else "photo"
                visuals.append((ts, r["path"], vtype))
    
    # Output path
    date_str = datetime.now().strftime("%Y-%m-%d")
    safe_sec = safe_name(sections[0][0]) if sections else "video"
    COMPLETED_DIR.mkdir(parents=True, exist_ok=True)
    output_path = COMPLETED_DIR / f"{date_str}_{safe_sec}.mp4"
    
    print(f"\n[INFO] === FFmpeg Compiler ===")
    print(f"[INFO] Input:    {video_path.name}")
    print(f"[INFO] Output:    {output_path.name}")
    print(f"[INFO] Sections: {len(sections)}")
    print(f"[INFO] Visuals:  {len(visuals)}")
    
    success = compile_video(video_path, output_path, sections, visuals)
    
    if success:
        state["compilation"] = {
            "path": str(output_path),
            "compiled_at": datetime.now().isoformat(),
            "sections": len(sections),
            "visuals": len(visuals)
        }
        json.dump(state, open(STATE_FILE, "w"), indent=2)
        print(f"\n✅ Compiled: {output_path} ({output_path.stat().st_size:,} bytes)")
        return output_path
    else:
        print("\n❌ Compilation failed")
        return None


if __name__ == "__main__":
    try:
        result = run_on_current_video()
        if not result:
            sys.exit(1)
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)
