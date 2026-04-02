#!/usr/bin/env python3
"""
Component 4 — Visual Proposer
For each section in the segmented transcript, identifies 3 moments where a visual
would strengthen the point. Outputs: timestamp, what's being said, and a specific
visual idea (article screenshot, chart, stock photo, or data graphic).
"""

import json
import sys
import re
from pathlib import Path

VAULT_DIR = Path.home() / ".openclaw" / "vault"
STATE_FILE = VAULT_DIR / "scripts" / "pipeline" / "pipeline_state.json"


def load_state() -> dict:
    if STATE_FILE.exists():
        with open(STATE_FILE) as f:
            return json.load(f)
    return {}


def get_segmented_transcript(state: dict) -> dict | None:
    seg_info = state.get("segmented_transcript")
    if not seg_info:
        return None
    path = Path(seg_info["path"])
    if not path.exists():
        return None
    with open(path) as f:
        return json.load(f)


def propose_visuals(segmented: dict) -> dict:
    """
    For each section, identify 3 key moments for visuals.
    
    Strategy:
    - For each section, look at the words and their timestamps
    - Identify moments with strong claims, data points, or key phrases
    - Match visual types to content:
      - Article screenshots for news/events
      - Stock photos for concepts/explainer moments
      - Charts for data/financial information
      - Data graphics for specific numbers/percentages
    """
    
    visual_plan = {
        "generated_at": segmented.get("generated_at", ""),
        "video_path": segmented.get("video_path", ""),
        "script_path": segmented.get("script_path", ""),
        "sections": []
    }
    
    for section in segmented.get("sections", []):
        section_name = section["name"]
        section_words = [w for w in segmented.get("words", []) if w["section"] == section_name]
        
        if not section_words:
            # No words for this section - generate placeholder visuals
            visual_plan["sections"].append({
                "section": section_name,
                "start_time": section.get("start_time", 0),
                "end_time": section.get("end_time", 0),
                "visuals": [
                    {
                        "timestamp": 0,
                        "description": "Section opener - stock market visual",
                        "visual_type": "stock_photo",
                        "visual_idea": "Stock market trading floor with screens showing market data",
                        "keywords": ["market", "trading", "stocks"]
                    },
                    {
                        "timestamp": 0,
                        "description": "Mid-section data point",
                        "visual_type": "chart",
                        "visual_idea": "Line chart showing relevant market movement",
                        "keywords": ["data", "chart", "market"]
                    },
                    {
                        "timestamp": 0,
                        "description": "Section closer with key takeaway",
                        "visual_type": "article_screenshot",
                        "visual_idea": "News headline related to the topic",
                        "keywords": ["news", "headline", "market"]
                    }
                ]
            })
            continue
        
        # Find key moments in this section's words
        # Look for:
        # 1. Specific numbers/percentages (data moments)
        # 2. Company/product names
        # 3. Key phrases like "worst part", "here's the kicker", "this matters"
        # 4. Transitions like "and then", "but", "however"
        
        words = section_words
        total_duration = words[-1]["end"] - words[0]["start"] if len(words) > 1 else 1
        section_start = words[0]["start"]
        
        # Find key moments (data points, names, key phrases)
        moments = []
        
        for i, w in enumerate(words):
            word = w["word"]
            word_lower = word.lower()
            
            # Check for data indicators
            is_data = bool(re.search(r'\d+%|\$\d+|\d+\.\d+|[MBTK]\$|\d+ [MmBbKk]', word))
            
            # Check for key phrase indicators
            is_key_phrase = any(kp in word_lower for kp in [
                "worst", "kicker", "matters", "important", "here's", "but", 
                "however", "actually", "specifically", "exactly", "literally",
                "billion", "trillion", "million", "percent", "drop", "jump",
                "surged", "fell", "gained", "climbed", "ripped", "crashed"
            ])
            
            # Check for company/person names (capitalized)
            is_name = bool(re.match(r'^[A-Z][a-z]+$', word) and len(word) > 2)
            
            if is_data or is_key_phrase:
                moments.append({
                    "word": word,
                    "start": w["start"],
                    "end": w["end"],
                    "is_data": is_data,
                    "is_key_phrase": is_key_phrase,
                    "is_name": is_name,
                    "context": " ".join(w2["word"] for w2 in words[max(0,i-3):i+4])
                })
        
        # Pick 3 moments spread across the section
        if len(moments) >= 3:
            # Pick first, middle, last significant moments
            selected = [moments[0], moments[len(moments)//2], moments[-1]]
        elif len(moments) >= 1:
            # Repeat the moments with time offsets
            selected = []
            for i in range(3):
                idx = min(i * len(moments) // 3, len(moments) - 1)
                selected.append(moments[idx])
        else:
            # No specific moments - use section start, middle, end
            selected = [
                {"word": words[0]["word"], "start": words[0]["start"], "context": words[0]["word"]},
                {"word": words[len(words)//2]["word"], "start": words[len(words)//2]["start"], "context": words[len(words)//2]["word"]},
                {"word": words[-1]["word"], "start": words[-1]["start"], "context": words[-1]["word"]}
            ]
        
        # Assign visual types to each moment
        section_visuals = []
        for i, moment in enumerate(selected):
            ts = moment.get("start", section_start + i * (total_duration / 3))
            context = moment.get("context", "")
            
            # Determine visual type based on content
            visual_type, visual_idea, keywords = suggest_visual_type(context, section_name, moment)
            
            section_visuals.append({
                "timestamp": round(ts, 2),
                "description": f'"{context[:80]}"',
                "visual_type": visual_type,
                "visual_idea": visual_idea,
                "keywords": keywords
            })
        
        visual_plan["sections"].append({
            "section": section_name,
            "start_time": section_start,
            "end_time": section.get("end_time", 0),
            "visuals": section_visuals
        })
    
    return visual_plan


def suggest_visual_type(context: str, section_name: str, moment: dict) -> tuple:
    """Determine the best visual type for a given moment."""
    context_lower = context.lower()
    section_lower = section_name.lower()
    combined = f"{section_lower} {context_lower}"
    
    # Check for article/news keywords
    news_kw = ["news", "report", "announced", "reported", "filed", "approved", 
               "said", "according to", "source", "confirmed", "broke"]
    
    # Check for chart/data keywords
    data_kw = ["percent", "%", "$", "million", "billion", "trillion", "points",
               "dropped", "gained", "climbed", "fell", "jumped", "surged",
               "rose", "fell", "trading", "index", "close", "market"]
    
    # Check for stock photo concepts
    concept_kw = ["oil", "war", "peace", "deal", "merger", "ipo", "rally",
                  "selloff", "correction", "election", "federal", "president",
                  "country", "world", "global", "spacex", "tesla", " GLP-1"]
    
    news_score = sum(1 for kw in news_kw if kw in combined)
    data_score = sum(1 for kw in data_kw if kw in combined)
    concept_score = sum(1 for kw in concept_kw if kw in combined)
    
    # If it's data-related, use chart
    if data_score >= 2 or moment.get("is_data"):
        return (
            "chart",
            f"Chart or graph showing the data mentioned: {context[:60]}",
            ["chart", "data", "graph", "market"]
        )
    
    # If it's news-related, use article screenshot
    elif news_score >= 2 or "filed" in combined or "approved" in combined:
        return (
            "article_screenshot",
            f"News article screenshot: {context[:60]}",
            ["news", "article", "source"]
        )
    
    # If it's a concept/explainer moment, use stock photo
    elif concept_score >= 1 or moment.get("is_name"):
        if "oil" in combined or "energy" in combined:
            return (
                "stock_photo",
                "Oil barrels or energy-related imagery",
                ["oil", "energy", "petroleum"]
            )
        elif "spacex" in combined or "space" in combined or "rocket" in combined:
            return (
                "stock_photo",
                "Space/rocket/technology imagery",
                ["space", "rocket", "technology"]
            )
        elif "glp-1" in combined or "lilly" in combined or "drug" in combined:
            return (
                "stock_photo",
                "Healthcare/pharmaceutical imagery",
                ["healthcare", "pharmaceutical", "medicine"]
            )
        elif "ipo" in combined or "stock" in combined or "market" in combined:
            return (
                "stock_photo",
                "Stock market / IPO imagery",
                ["stock market", "IPO", "finance"]
            )
        else:
            return (
                "stock_photo",
                f"Concept illustration: {context[:50]}",
                ["concept", "illustration"]
            )
    
    # Default to article screenshot for news
    else:
        return (
            "article_screenshot",
            f"Relevant news article: {context[:60]}",
            ["news", "market", "source"]
        )


def run_on_current_video() -> dict | None:
    """Run the visual proposer on the current video's segmented transcript."""
    state = load_state()
    segmented = get_segmented_transcript(state)
    
    if not segmented:
        print("[ERROR] No segmented transcript found. Run Component 3 first.")
        return None
    
    visual_plan = propose_visuals(segmented)
    
    # Save the visual plan
    video_path = Path(state.get("current_video", {}).get("path", "unknown"))
    output_path = video_path.parent / f"{video_path.stem}_visual_plan.json"
    
    with open(output_path, "w") as f:
        json.dump(visual_plan, f, indent=2)
    
    print(f"[OK] Visual plan saved: {output_path}")
    
    # Update state
    state["visual_plan"] = {
        "path": str(output_path),
        "sections": len(visual_plan["sections"]),
        "total_visuals": sum(len(s["visuals"]) for s in visual_plan["sections"])
    }
    with open(STATE_FILE, "w") as f:
        json.dump(state, f, indent=2)
    
    # Print summary
    print("\n[VISUAL PLAN SUMMARY]")
    for sec in visual_plan["sections"]:
        print(f"\n  [{sec['section']}]")
        for i, v in enumerate(sec["visuals"], 1):
            print(f"    {i}. [{v['timestamp']:.1f}s] {v['visual_type']}: {v['description'][:60]}")
    
    return visual_plan


if __name__ == "__main__":
    result = run_on_current_video()
    if result:
        print(f"\nVisual plan generated: {result['sections']} sections, "
              f"{sum(len(s['visuals']) for s in result['sections'])} total visuals")
    else:
        print("Visual plan generation failed.")
        sys.exit(1)
