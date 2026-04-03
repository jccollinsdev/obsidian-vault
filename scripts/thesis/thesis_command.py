#!/usr/bin/env python3
"""
/thesis Command — Full Pipeline
Usage: python3 thesis_command.py "gold miners undervalued fed rates" [TICKER]

1. Parse idea → extract ticker if provided
2. Run research (yfinance + macro)
3. Generate PDF (dark theme, 10 sections)
4. Save to vault/theses/active/
5. Upload to Google Drive
6. Update memory.md
7. Return summary + PDF path
"""
import sys
import os
import json
import re
import subprocess
import argparse

# Add scripts path
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
VAULT_DIR  = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
THESES_DIR = os.path.join(VAULT_DIR, "theses", "active")

sys.path.insert(0, SCRIPT_DIR)

from research_module import run_research, get_macro_snapshot
from pdf_generator import make_pdf

# ─────────────────────────────────────────────────────────────────────────────
# Step 1: Parse the idea and extract ticker
# ─────────────────────────────────────────────────────────────────────────────

def extract_ticker(idea: str) -> tuple[str, str]:
    """
    Try to extract a ticker from the idea string.
    Returns (ticker, remaining_idea).
    """
    # Common patterns: "NVDA is", "on Tesla", "$AAPL", "Ticker: GDX"
    ticker_patterns = [
        r'\$([A-Z]{1,5})\b',          # $NVDA
        r'\b([A-Z]{2,5})\s+(?:is|to|for|because)\b',  # NVDA is... / AAPL to...
        r'(?:ticker|stock)[:\s]+([A-Z]{1,5})',
    ]
    idea_upper = idea.upper()
    for pat in ticker_patterns:
        m = re.search(pat, idea_upper)
        if m:
            ticker = m.group(1)
            # Remove the ticker mention from idea
            cleaned = re.sub(pat, '', idea_upper, count=1).strip()
            return ticker, cleaned or idea
    return "", idea


def parse_args():
    parser = argparse.ArgumentParser(description="Thesis command")
    parser.add_argument("idea", nargs='+', help="Investment thesis idea")
    parser.add_argument("--ticker", "-t", default=None, help="Ticker override")
    return parser.parse_args()


# ─────────────────────────────────────────────────────────────────────────────
# Step 2: Run Research
# ─────────────────────────────────────────────────────────────────────────────

def do_research(ticker: str, idea: str) -> dict:
    print(f"\n[Thesis] Researching: {idea}")
    print(f"[Thesis] Ticker: {ticker}")
    research = run_research(ticker, idea)
    return research


# ─────────────────────────────────────────────────────────────────────────────
# Step 3: Generate PDF
# ─────────────────────────────────────────────────────────────────────────────

def generate_pdf(research: dict) -> str:
    ticker = research["ticker"]
    date_str = research["research_time"].split()[0].replace("-", "")  # YYYYMMDD
    filename = f"{ticker}_Thesis_{date_str}.pdf"
    output_path = os.path.join(THESES_DIR, filename)

    print(f"\n[Thesis] Generating PDF: {output_path}")
    path = make_pdf(output_path, research)
    return path


# ─────────────────────────────────────────────────────────────────────────────
# Step 4: Save to Google Drive
# ─────────────────────────────────────────────────────────────────────────────

THESES_FOLDER_ID = "1iY67XB6UrLV0kY0A0WDjUYD1P5xoAj40"

def upload_to_drive(pdf_path: str):
    """Upload PDF to Google Drive in the Josiah Theses folder."""
    print(f"\n[Thesis] Uploading to Google Drive: {pdf_path}")
    try:
        result = subprocess.run(
            ["gog", "drive", "upload", pdf_path,
             "--parent", THESES_FOLDER_ID],
            capture_output=True, text=True, timeout=60,
            env={**os.environ,
                 "GOG_ACCOUNT": "jc.collins.dev@gmail.com",
                 "GOG_KEYRING_PASSWORD": "josiah123"}
        )
        print(f"[Thesis] Drive upload result: {result.stdout.strip() or result.stderr.strip()}")
        return result.stdout.strip()
    except Exception as e:
        print(f"[Thesis] Drive upload failed: {e}")
        return None


# ─────────────────────────────────────────────────────────────────────────────
# Step 5: Update memory.md
# ─────────────────────────────────────────────────────────────────────────────

def update_memory(ticker: str, idea: str, pdf_path: str, research: dict):
    """Add active thesis to memory.md."""
    cp = research.get("ticker_data", {}).get("current_price", 0)
    targets = research.get("price_targets", {})
    bull = targets.get("bull", 0)
    upside = ((bull - cp) / cp * 100) if cp and bull else 0

    entry = (
        f"\n## Active Theses\n"
        f"- **{ticker}** — {idea[:60]}... "
        f"| Price: ${cp:.2f} | Bull: ${bull:.2f} (+{upside:.0f}%) | Status: intact | PDF: {os.path.basename(pdf_path)}"
    )
    print(f"[Thesis] Memory update: {entry.strip()}")
    # In practice, this will be handled by the agent writing to memory.md directly
    return entry


# ─────────────────────────────────────────────────────────────────────────────
# Step 6: Send summary via Telegram
# ─────────────────────────────────────────────────────────────────────────────

def format_summary(research: dict, pdf_path: str) -> str:
    td = research.get("ticker_data", {})
    cp = td.get("current_price", 0)
    targets = research.get("price_targets", {})
    bull = targets.get("bull", 0)
    neutral = targets.get("neutral", 0)

    ticker = research["ticker"]
    company = research["company_name"]
    idea = research["thesis_idea"]

    summary = (
        f"📊 **THESIS GENERATED — {ticker}**\n\n"
        f"**{company} ({ticker})**\n"
        f"{idea}\n\n"
        f"Current Price: ${cp:.2f}\n"
        f"Bear: ${targets.get('bear', 0):.2f} | "
        f"Neutral: ${neutral:.2f} | "
        f"Bull: ${bull:.2f}\n"
        f"Bull upside: +{((bull-cp)/cp*100):.0f}%\n\n"
        f"PDF saved to vault: `theses/active/{os.path.basename(pdf_path)}`"
    )
    return summary


# ─────────────────────────────────────────────────────────────────────────────
# Main
# ─────────────────────────────────────────────────────────────────────────────

def main():
    args = parse_args()
    idea = " ".join(args.idea)

    # Extract or validate ticker
    ticker_extracted, idea_clean = extract_ticker(idea)
    ticker = (args.ticker or ticker_extracted).upper().strip()

    if not ticker:
        print("[Thesis] ERROR: Could not extract ticker. Please provide --ticker TICKER")
        sys.exit(1)

    if not ticker_extracted and args.ticker:
        idea_clean = idea  # use full idea if ticker was forced

    print(f"\n=== THESIS PIPELINE ===")
    print(f"Ticker: {ticker}")
    print(f"Thesis: {idea_clean}")

    # Run research
    research = do_research(ticker, idea_clean)

    # Generate PDF
    pdf_path = generate_pdf(research)

    # Upload to Drive
    upload_to_drive(pdf_path)

    # Memory entry
    memory_entry = update_memory(ticker, idea_clean, pdf_path, research)

    # Summary
    summary = format_summary(research, pdf_path)
    print(f"\n=== SUMMARY ===\n{summary}")

    # Save research json for debugging/audit
    research_path = pdf_path.replace(".pdf", "_research.json")
    with open(research_path, "w") as f:
        json.dump(research, f, default=str, indent=2)
    print(f"\n[Thesis] Research data saved: {research_path}")

    print(f"\n✅ Thesis pipeline complete. PDF: {pdf_path}")
    return pdf_path, summary, memory_entry


if __name__ == "__main__":
    main()
