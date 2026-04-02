#!/usr/bin/env python3
"""
Component 3 — Topic Segmenter
Reads the Whisper transcript JSON and the script file for that video.
Matches [SECTION: X] labels from script to transcript using timestamps.
Outputs a segmented transcript where every word knows which section it belongs to.
"""

import json
import sys
import re
from pathlib import Path
from datetime import datetime

VAULT_DIR = Path.home() / ".openclaw" / "vault"
STATE_FILE = VAULT_DIR / "scripts" / "pipeline" / "pipeline_state.json"


def load_state() -> dict:
    if STATE_FILE.exists():
        with open(STATE_FILE) as f:
            return json.load(f)
    return {}


def find_script_for_video(state: dict) -> Path | None:
    """Find the script file that matches the current video."""
    video_path = state.get("current_video", {}).get("path")
    if not video_path:
        return None
    
    video_name = Path(video_path).stem
    
    # Try to match script by date in filename
    # Video: test_dummy_20260402.mp4 -> script with 2026-04-02
    date_match = re.search(r'(\d{4})(\d{2})(\d{2})', video_name)
    if date_match:
        year, month, day = date_match.groups()
        date_str = f"{year}-{month}-{day}"
        
        # Search in scripts/ folder
        scripts_dir = VAULT_DIR / "scripts"
        for subdir in ["wednesday", "friday", "monday", "thesis"]:
            script_dir = scripts_dir / subdir
            if not script_dir.exists():
                continue
            for script_file in script_dir.glob("*.md"):
                if date_str in script_file.name:
                    return script_file
    
    # Fallback: find most recent script
    scripts_dir = VAULT_DIR / "scripts"
    all_scripts = []
    for subdir in scripts_dir.iterdir():
        if subdir.is_dir():
            for script_file in subdir.glob("*.md"):
                all_scripts.append(script_file)
    
    if all_scripts:
        return sorted(all_scripts, key=lambda p: p.stat().st_mtime).pop()
    
    return None


def parse_script_sections(script_path: Path) -> list[dict]:
    """Parse the script file and extract [SECTION: X] labels with their positions."""
    with open(script_path) as f:
        content = f.read()
    
    sections = []
    # Find all [SECTION: X] labels
    pattern = r'\[SECTION:\s*([^\]]+)\]'
    
    for match in re.finditer(pattern, content):
        section_name = match.group(1).strip()
        char_pos = match.start()
        sections.append({
            "name": section_name,
            "char_pos": char_pos,
            "text": content[match.start():match.end()]
        })
    
    return sections


def extract_section_texts(script_path: Path) -> list[dict]:
    """Extract the text content between [SECTION: X] labels."""
    with open(script_path) as f:
        content = f.read()
    
    # Find all section boundaries
    pattern = r'\[SECTION:\s*([^\]]+)\]'
    matches = list(re.finditer(pattern, content))
    
    sections = []
    for i, match in enumerate(matches):
        section_name = match.group(1).strip()
        start = match.end()
        
        # End is either the next section or end of file
        if i + 1 < len(matches):
            end = matches[i + 1].start()
        else:
            end = len(content)
        
        section_text = content[start:end].strip()
        sections.append({
            "name": section_name,
            "text": section_text
        })
    
    return sections


def segment_transcript(transcript_path: Path, script_path: Path) -> dict:
    """
    Map transcript words to script sections.
    
    Strategy:
    1. Extract text from each script section
    2. Build a combined text per section
    3. For each word in the transcript, find which section's text best matches
       the surrounding context
    4. Use a simple keyword matching approach to assign words to sections
    """
    # Load transcript
    with open(transcript_path) as f:
        transcript = json.load(f)
    
    # Get section texts from script
    sections = extract_section_texts(script_path)
    
    # Build word-level segmented transcript
    segmented = {
        "video_path": str(transcript_path),
        "script_path": str(script_path),
        "generated_at": datetime.now().isoformat(),
        "sections": [],
        "words": []
    }
    
    # Process each word in the transcript
    words = []
    for seg in transcript.get("segments", []):
        seg_start = seg.get("start", 0)
        seg_end = seg.get("end", 0)
        seg_text = seg.get("text", "").strip()
        
        seg_words = seg.get("words", [])
        
        if seg_words:
            # Use word-level timestamps
            for w in seg_words:
                words.append({
                    "word": w.get("word", "").strip(),
                    "start": w.get("start", 0),
                    "end": w.get("end", 0),
                    "probability": w.get("probability", 0),
                    "segment_text": seg_text
                })
        else:
            # No word-level timestamps - estimate positions
            # Just use the segment text with segment timing
            words.append({
                "word": seg_text,
                "start": seg_start,
                "end": seg_end,
                "probability": 1.0,
                "segment_text": seg_text
            })
    
    # Now assign each word to a section
    # Strategy: match based on the segment text containing section-specific keywords
    # For each word, figure out which section context it belongs to
    
    # Build section keyword index
    section_keywords = {}
    for section in sections:
        section_text = section["text"].lower()
        # Extract significant words (filter out common words)
        words_in_section = re.findall(r'\b[a-z]+\b', section_text)
        significant = [w for w in words_in_section if len(w) > 3]
        section_keywords[section["name"]] = set(significant)
    
    # Assign each transcript word to a section
    assigned_words = []
    current_section = sections[0]["name"] if sections else "UNKNOWN"
    
    for w in words:
        word_text = w["word"].lower().strip()
        word_start = w["start"]
        
        # Try to find which section this word belongs to
        # by looking at which section has the most keyword matches
        # in nearby words
        
        best_section = current_section
        best_score = 0
        
        for section in sections:
            section_name = section["name"]
            section_text = section["text"].lower()
            
            # Simple scoring: count how many significant words from section
            # appear near this word's timestamp
            score = section_text.count(word_text)
            
            if score > best_score:
                best_score = score
                best_section = section_name
        
        # If no clear match, try keyword matching
        if best_score == 0:
            # Check if this word's context (the segment text) matches a section
            seg_text = w.get("segment_text", "").lower()
            
            for section in sections:
                section_text = section["text"].lower()
                # Check for overlapping significant words
                section_words = set(re.findall(r'\b[a-z]+\b', section_text))
                word_words = set(re.findall(r'\b[a-z]+\b', seg_text))
                overlap = section_words & word_words
                
                # Also check if the section name keywords appear in segment text
                section_kw = section_keywords.get(section["name"], set())
                context_overlap = word_words & section_kw
                
                if len(context_overlap) > best_score:
                    best_score = len(context_overlap)
                    best_section = section["name"]
        
        # Default to previous section if no match
        if best_score == 0 and current_section != "UNKNOWN":
            best_section = current_section
        else:
            current_section = best_section
        
        assigned_words.append({
            "word": w["word"],
            "start": word_start,
            "end": w["end"],
            "probability": w.get("probability", 1.0),
            "section": best_section
        })
    
    segmented["words"] = assigned_words
    
    # Also create per-section summaries
    section_word_map = {}
    for w in assigned_words:
        sec = w["section"]
        if sec not in section_word_map:
            section_word_map[sec] = []
        section_word_map[sec].append(w)
    
    for section in sections:
        sec_name = section["name"]
        sec_words = section_word_map.get(sec_name, [])
        
        start_time = sec_words[0]["start"] if sec_words else 0
        end_time = sec_words[-1]["end"] if sec_words else 0
        
        segmented["sections"].append({
            "name": sec_name,
            "word_count": len(sec_words),
            "start_time": start_time,
            "end_time": end_time,
            "duration": end_time - start_time,
            "sample_text": " ".join(w["word"] for w in sec_words[:10]) + "..."
        })
    
    return segmented


def run_on_current_video() -> dict | None:
    """Run the segmenter on the current video's transcript and script."""
    state = load_state()
    
    transcript_info = state.get("transcript")
    if not transcript_info:
        print("[ERROR] No transcript found. Run Component 2 first.")
        return None
    
    transcript_path = Path(transcript_info["path"])
    if not transcript_path.exists():
        print(f"[ERROR] Transcript not found at {transcript_path}")
        return None
    
    script_path = find_script_for_video(state)
    if not script_path:
        print("[ERROR] Could not find script for this video.")
        return None
    
    print(f"[INFO] Using script: {script_path}")
    
    # Parse script sections
    sections = parse_script_sections(script_path)
    print(f"[INFO] Found {len(sections)} sections in script: {[s['name'] for s in sections]}")
    
    # Segment the transcript
    segmented = segment_transcript(transcript_path, script_path)
    
    # Save segmented transcript
    video_path = Path(state.get("current_video", {}).get("path", "unknown"))
    output_path = video_path.parent / f"{video_path.stem}_segmented.json"
    
    with open(output_path, "w") as f:
        json.dump(segmented, f, indent=2)
    
    print(f"[OK] Segmented transcript saved: {output_path}")
    
    # Update state
    state["segmented_transcript"] = {
        "path": str(output_path),
        "sections": len(segmented["sections"]),
        "total_words": len(segmented["words"]),
        "generated_at": segmented["generated_at"]
    }
    with open(STATE_FILE, "w") as f:
        json.dump(state, f, indent=2)
    
    # Print summary
    print("\n[SEGMENT SUMMARY]")
    for sec in segmented["sections"]:
        print(f"  [{sec['name']}] {sec['word_count']} words, "
              f"{sec['start_time']:.1f}s - {sec['end_time']:.1f}s "
              f"({sec['duration']:.1f}s)")
        print(f"    Sample: {sec['sample_text'][:80]}")
    
    return segmented


if __name__ == "__main__":
    result = run_on_current_video()
    if result:
        print(f"\nSegmented {len(result['words'])} words into {len(result['sections'])} sections")
    else:
        print("Segmentation failed.")
        sys.exit(1)
