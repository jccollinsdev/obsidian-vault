#!/usr/bin/env python3
"""
Component 5 — Visual Sourcer
Executes the visual plan:
- Article visuals: use Crawl4AI to find the article and screenshot it
- Stock photos: use Bing Image Scraper via Playwright to find and download
- Charts/data graphics: use Crawl4AI to find and screenshot them
Saves all visuals to videos/in_progress/[video_name]/visuals/
Auto-approves articles and charts. Flags photos for approval.
"""

import json
import os
import subprocess
import sys
import asyncio
import crawl4ai
from crawl4ai import AsyncWebCrawler, CrawlerRunConfig
from pathlib import Path
from datetime import datetime

VAULT_DIR = Path.home() / ".openclaw" / "vault"
STATE_FILE = VAULT_DIR / "scripts" / "pipeline" / "pipeline_state.json"
BING_SCRAPER = Path("/home/openclaw/google-image-scraper/bing_scraper.py")


def load_state() -> dict:
    if STATE_FILE.exists():
        with open(STATE_FILE) as f:
            return json.load(f)
    return {}


def get_visual_plan(state: dict) -> dict | None:
    vp_info = state.get("visual_plan")
    if not vp_info:
        return None
    path = Path(vp_info["path"])
    if not path.exists():
        return None
    with open(path) as f:
        return json.load(f)


def ensure_dir(path: Path):
    path.mkdir(parents=True, exist_ok=True)


async def _crawl4ai_screenshot(url: str, output_path: Path) -> dict:
    """Use Crawl4AI to screenshot a URL."""
    result_data = {"success": False, "path": None, "error": None}
    
    try:
        config = CrawlerRunConfig(screenshot=True, verbose=False)
        async with AsyncWebCrawler() as crawler:
            result = await crawler.arun(url=url, config=config)
            
            if result.success and result.screenshot:
                # Screenshot can be bytes or base64 string - handle both
                screenshot_data = result.screenshot
                if isinstance(screenshot_data, str):
                    # It's base64 encoded - decode it
                    import base64
                    screenshot_data = base64.b64decode(screenshot_data)
                # Save screenshot
                with open(output_path, "wb") as f:
                    f.write(screenshot_data)
                result_data["success"] = True
                result_data["path"] = str(output_path)
            else:
                result_data["error"] = "Crawl failed or no screenshot"
    except Exception as e:
        result_data["error"] = str(e)
    
    return result_data


async def _find_article_url(query: str) -> str | None:
    """Search for an article URL using DuckDuckGo."""
    search_url = f"https://duckduckgo.com/?q={query.replace(' ', '+')}&t=hpc&ia=web"
    
    try:
        config = CrawlerRunConfig(
            verbose=False
        )
        async with AsyncWebCrawler() as crawler:
            result = await crawler.arun(url=search_url, config=config)
            
            if result.success and result.html:
                # Try to find the first news article link
                import re
                # Look for news article patterns
                links = re.findall(r'href="(https://[^"]*(?:news|article)[^"]*)"', result.html)
                for link in links[:5]:
                    if any(safe in link.lower() for safe in ['cnbc', 'bloomberg', 'reuters', 'wsj', 'ft', 'marketwatch', 'yahoo']):
                        return link
                
                # Fall back to any reasonable link
                if links:
                    return links[0]
    except Exception as e:
        print(f"[WARN] Search failed: {e}")
    
    return None


async def source_article_screenshot_async(visual: dict, staging_dir: Path, section_name: str) -> dict:
    """Use Crawl4AI to find and screenshot an article."""
    result = {
        "visual": visual,
        "section": section_name,
        "status": "pending",
        "path": None,
        "approval_needed": False,  # Articles auto-approved
        "source_url": None,
        "error": None
    }
    
    keywords = visual.get("keywords", [])
    query = " ".join(keywords[:5]) + " news"
    
    # Find article URL
    print(f"      Searching for article: {query[:50]}...")
    article_url = await _find_article_url(query)
    
    if not article_url:
        result["error"] = "No article URL found"
        return result
    
    result["source_url"] = article_url
    print(f"      Found article: {article_url[:60]}...")
    
    # Screenshot the article
    ts = visual.get("timestamp", 0)
    output_path = staging_dir / f"article_{ts:.0f}s.png"
    
    print(f"      Screenshotting article...")
    screenshot_result = await _crawl4ai_screenshot(article_url, output_path)
    
    if screenshot_result["success"]:
        result["path"] = screenshot_result["path"]
        result["status"] = "success"
    else:
        result["error"] = screenshot_result.get("error", "Screenshot failed")
    
    return result


async def source_chart_screenshot_async(visual: dict, staging_dir: Path, section_name: str) -> dict:
    """Use Crawl4AI to find and screenshot a chart."""
    result = {
        "visual": visual,
        "section": section_name,
        "status": "pending",
        "path": None,
        "approval_needed": False,  # Charts auto-approved
        "source_url": None,
        "error": None
    }
    
    keywords = visual.get("keywords", [])
    query = " ".join(keywords[:4]) + " stock chart"
    
    # Find chart/image URL via image search
    search_url = f"https://duckduckgo.com/?q={query.replace(' ', '+')}&t=hpi&iax=1&ia=images"
    
    try:
        config = CrawlerRunConfig(verbose=False)
        async with AsyncWebCrawler() as crawler:
            result_search = await crawler.arun(url=search_url, config=config)
            
            if result_search.success and result_search.html:
                import re
                # Find image src
                images = re.findall(r'src="(https://[^"]*\.(?:png|jpg|jpeg|webp)[^"]*)"', result_search.html)
                images += re.findall(r'data-src="(https://[^"]*\.(?:png|jpg|jpeg|webp)[^"]*)"', result_search.html)
                
                if images:
                    chart_url = images[0]
                    result["source_url"] = chart_url
                    print(f"      Found chart image: {chart_url[:60]}...")
                    
                    # Screenshot the chart image
                    ts = visual.get("timestamp", 0)
                    output_path = staging_dir / f"chart_{ts:.0f}s.png"
                    
                    screenshot_result = await _crawl4ai_screenshot(chart_url, output_path)
                    
                    if screenshot_result["success"]:
                        result["path"] = screenshot_result["path"]
                        result["status"] = "success"
                    else:
                        result["error"] = screenshot_result.get("error", "Screenshot failed")
                else:
                    result["error"] = "No chart images found"
            else:
                result["error"] = "Image search failed"
    except Exception as e:
        result["error"] = str(e)
    
    return result


def source_stock_photo(visual: dict, staging_dir: Path, section_name: str) -> dict:
    """Use Bing Image Scraper to find and download a stock photo."""
    result = {
        "visual": visual,
        "section": section_name,
        "status": "pending",
        "path": None,
        "approval_needed": True,  # Photos need approval
        "source_url": None,
        "error": None
    }
    
    visual_idea = visual.get("visual_idea", "")
    keywords = visual.get("keywords", [])
    query = visual_idea if visual_idea else " ".join(keywords[:5])
    
    # Bing scraper creates a directory with this name
    output_dir = staging_dir / f"photo_{visual['timestamp']:.0f}s"
    
    try:
        cmd = [
            "python3", str(BING_SCRAPER),
            query,  # search query (positional)
            "1",     # limit (positional)
            str(output_dir)  # output directory (positional)
        ]
        
        print(f"      Searching Bing Images: {query[:50]}...")
        proc = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
        
        # Find the downloaded image inside the output directory
        if output_dir.exists() and output_dir.is_dir():
            image_files = list(output_dir.glob("*.jpg")) + list(output_dir.glob("*.jpeg")) + list(output_dir.glob("*.png"))
            if image_files:
                # Use the first image
                image_file = sorted(image_files, key=lambda p: p.stat().st_mtime)[-1]
                if image_file.stat().st_size > 5000:
                    result["path"] = str(image_file)
                    result["status"] = "success"
                    result["approval_needed"] = True
                else:
                    result["error"] = f"Downloaded file too small ({image_file.stat().st_size} bytes)"
            else:
                result["error"] = f"No image files in output directory"
        else:
            result["error"] = f"Output directory not created"
            
    except subprocess.TimeoutExpired:
        result["error"] = "Timeout"
    except Exception as e:
        result["error"] = str(e)
    
    return result


async def run_on_current_video_async() -> dict | None:
    """Execute the visual plan (async version for Crawl4AI)."""
    state = load_state()
    visual_plan = get_visual_plan(state)
    
    if not visual_plan:
        print("[ERROR] No visual plan found. Run Component 4 first.")
        return None
    
    video_path = Path(state.get("current_video", {}).get("path", "unknown"))
    video_stem = video_path.stem
    
    staging_dir = video_path.parent / f"{video_stem}_visuals"
    ensure_dir(staging_dir)
    
    print(f"[INFO] Sourcing visuals to: {staging_dir}")
    
    all_results = []
    
    for sec in visual_plan.get("sections", []):
        section_name = sec["section"]
        print(f"\n[INFO] Processing section: {section_name}")
        
        for i, visual in enumerate(sec.get("visuals", []), 1):
            visual_type = visual.get("visual_type", "unknown")
            ts = visual.get("timestamp", 0)
            
            print(f"  [{i}] {visual_type} @ {ts:.1f}s: {visual.get('description','')[:50]}...")
            
            if visual_type == "article_screenshot":
                result = await source_article_screenshot_async(visual, staging_dir, section_name)
            elif visual_type == "stock_photo":
                result = source_stock_photo(visual, staging_dir, section_name)
            elif visual_type == "chart":
                result = await source_chart_screenshot_async(visual, staging_dir, section_name)
            else:
                result = {
                    "visual": visual,
                    "section": section_name,
                    "status": "failed",
                    "error": f"Unknown visual type: {visual_type}",
                    "approval_needed": True
                }
            
            status_str = "✓" if result["status"] == "success" else "✗"
            approval_str = " [PENDING APPROVAL]" if result.get("approval_needed") else " [AUTO-APPROVED]"
            print(f"      {status_str} {result.get('error', 'OK')}{approval_str}")
            
            all_results.append(result)
    
    # Save the sourcing results
    output_path = staging_dir / "sourcing_results.json"
    sourcing_results = {
        "generated_at": datetime.now().isoformat(),
        "staging_dir": str(staging_dir),
        "results": all_results,
        "total": len(all_results),
        "success": sum(1 for r in all_results if r["status"] == "success"),
        "failed": sum(1 for r in all_results if r["status"] != "success"),
        "pending_approval": sum(1 for r in all_results if r.get("approval_needed"))
    }
    
    with open(output_path, "w") as f:
        json.dump(sourcing_results, f, indent=2)
    
    print(f"\n[OK] Sourcing complete: {sourcing_results['success']}/{sourcing_results['total']} successful")
    print(f"[INFO] {sourcing_results['pending_approval']} visuals need approval")
    print(f"[INFO] Results saved: {output_path}")
    
    # Update state
    state["visual_sourcing"] = {
        "path": str(output_path),
        "staging_dir": str(staging_dir),
        "success": sourcing_results["success"],
        "total": sourcing_results["total"],
        "pending_approval": sourcing_results["pending_approval"]
    }
    with open(STATE_FILE, "w") as f:
        json.dump(state, f, indent=2)
    
    return sourcing_results


def run_on_current_video() -> dict | None:
    """Execute the visual plan."""
    return asyncio.run(run_on_current_video_async())


if __name__ == "__main__":
    result = run_on_current_video()
    if result:
        print(f"\nSourcing complete: {result['success']}/{result['total']} successful")
    else:
        print("Visual sourcing failed.")
        sys.exit(1)
