# Friday Proof of Knowledge — Pipeline Docs

**Purpose:** Produce a weekly proof-of-knowledge video where Sansar shows real trades, real PNL, and his real decisions going into the next week. The Friday video is accountability journalism — not a newsletter, not a recap. It's evidence.

---

## Core Identity

**The job:** "Here's what happened to my REAL trade, here's the proof, here's what I'm doing next."

Nobody else on YouTube does this at 14. That's the hook.

---

## Workflow Overview

1. Trigger: user runs `/friday`
2. Research — scrape market news RELATING to the sector/position (not broad market)
3. Script — write in Sansar's voice, label [SECTION: X] throughout, position decision at end
4. Visuals — IBKR PNL screenshot (full-frame takeover), inline charts, news screenshots
5. Assemble — Remotion video with face cam overlay, screenshot takeovers, section labels
6. Deliver — script to Notion, email link to sansarkarki10@gmail.com
7. Render — output to `vault/videos/completed/`

---

## Step-by-Step

### 1. Research

**Rule:** Only news that affected the position or sector. Focused. Not a broad market dump.

**Sources (preferred):**
- AP News — `apnews.com`
- CNBC — `cnbc.com`
- The National — `thenationalnews.com`
- CNN Business — `edition.cnn.com/business`
- NBC News — `nbcnews.com/business`

**BLOCKED:** Reuters (advanced bot blocking — do not use)

**Research angle:**
- What news dropped that affected this stock/sector this week?
- Did the company's own announcements move it (earnings, FDA, regulatory, leadership)?
- Macro factors: rate decisions, commodity moves, sector ETF performance?
- Sentiment: what did the market collectively think happened?

**Stock charts:** Search Bing for `[TICKER] stock chart April 2026` — pull via Bing scraper or screenshot from Yahoo Finance / Google Finance.

**Price data:** Web search for current prices and performance data. Never invent numbers.

### 2. Script

**Structure:**

```
[SECTION: MARKET CONTEXT]
What happened this week that matters for [SECTOR/STOCK].
Named headlines. Specific data. No fluff.

[SECTION: POSITION REVIEW]
IBKR screenshot takeover — full screen.
Walk through: entry price, current price, P&L %, dollar amount.
Real numbers only.

[SECTION: WHAT I'M DOING NEXT WEEK]
Hold / Add / Sell — and WHY.
Specific reasoning based on what you learned this week.
```

**Rules:**
- Write in Sansar's voice — chill, punchy, data-grounded, mild edge
- Label every section with `[SECTION: TOPIC NAME]` (no numbers)
- Lead with specific headlines — name the actual stories
- Face zoom at 1–2 peak moments only (not every section)
- End with TLDR: that has colour and opinion — not just "up X% this week"
- Standard disclaimer at the end

**Delivery:**
- Put script in Notion first
- Email ONLY the Notion link to `sansarkarki10@gmail.com`
- Subject: `📹 [Date] — Friday Proof of Knowledge`
- Never paste full script in email body

### 3. Visuals

**IBKR Screenshot (POSITION REVIEW section):**
- Sansar sends via email/Telegram — download and save to `remotion-video/public/photo_POSITION/`
- Full-frame takeover while he's on screen talking through it
- No zoom effect on this — hard cut to screenshot

**Stock Photos (Bing Scraper)**
```bash
python3 /home/openclaw/google-image-scraper/bing_scraper.py \
  "SEARCH QUERY" 5 /path/to/output_folder
```

**Rules:**
- Always verify images are REAL PHOTOGRAPHS — use the `image` tool to analyze before using
- AI-generated images are common for queries like "SpaceX IPO", "stock market future", "crypto"
- Look for: real launches, real trading floors, real people, real charts
- Avoid: concept art, floating charts in space, fake candlesticks, illustrative graphics

**Article Screenshots:**
```bash
python3 /home/openclaw/.openclaw/vault/scripts/pipeline/article_screenshot.py
```

Edit `ARTICLE_URLS` dict inside the script to set the URLs for that week's relevant stories.

**Stealth settings baked in:**
- Viewport: 1920×1080
- User Agent: Mac Chrome (realistic)
- Init script patches: `navigator.webdriver`, `navigator.plugins`, `navigator.languages`, `window.chrome`, `navigator.permissions`

**Output:** PNG screenshots saved to `remotion-video/public/`

### 4. Remotion Video Assembly

**Config file:** `vault/scripts/pipeline/remotion-video/src/Root.tsx`

```tsx
const SLIDES = [
  { imagePath: "photo_MARKET/image_001.jpg", title: "MARKET CONTEXT" },
  { imagePath: "photo_POSITION/ibkr_screenshot.png", title: "POSITION REVIEW" },
  { imagePath: "photo_DECISION/image_001.jpg", title: "NEXT WEEK" },
  // ...
];
```

**Component:** `vault/scripts/pipeline/remotion-video/src/Video.tsx`

**Friday Overlay Rules (distinct from Wednesday):**
- Face cam: **bottom-left corner** (distinct from Wednesday — Sansar can alternate if needed)
- Section label: **top-right corner** (opposite face cam — per video style rule)
- Position screenshot: **full-frame takeover** — hard cut, no fade, no animation — just the IBKR screenshot filling the screen while Sansar walks through it
- Charts inline: appear as you mention them
- Article screenshots: full-frame takeover between sections

**Preview server:**
```bash
cd vault/scripts/pipeline/remotion-video
npm run start -- --port 3000 --force-new
# Live at http://localhost:3000
```

**Render:**
```bash
npx remotion render SansarVideo /path/to/output.mp4 --fps 25
```

**Output:** `vault/videos/completed/YYYY-MM-DD_FRIDAY_vX.mp4`

### 5. Folder Structure

```
vault/scripts/pipeline/remotion-video/
├── public/
│   ├── photo_MARKET/       # sector/stock photos
│   ├── photo_POSITION/     # IBKR screenshot (sent by Sansar)
│   ├── photo_DECISION/    # decision-relevant visuals
│   ├── article_MARKET.png  # article screenshots
│   ├── article_STOCK.png
│   └── test_dummy_20260402.mp4  # base video
├── src/
│   ├── Video.tsx         # React components
│   └── Root.tsx          # composition config
└── package.json

vault/videos/
├── completed/
│   └── YYYY-MM-DD_FRIDAY_vX.mp4  # rendered output
└── in_progress/
```

---

## Key Differences from Wednesday

| Element | Wednesday | Friday |
|---------|----------|--------|
| Purpose | Market recap | Proof of knowledge |
| Breadth | Broad market news | News only affecting position |
| Face cam | Alternating (left/right per section) | Bottom-left fixed |
| PNL section | Inline charts | Full-frame IBKR screenshot takeover |
| Decision segment | No | Yes — hold/add/sell with reasoning |
| TLDR tone | Market summary | Personal verdict |

---

## Photo Sourcing Rules

| Query Type | Risk | Action |
|------------|------|--------|
| Real company/event | Low | Verify with image analysis |
| IPO/concept/future | High | Almost always AI — find alternative angle |
| Charts/graphs | Medium | Prefer real screenshots, not Bing scraper |
| People | Medium | Verify — AI faces common |

---

## Key Docs

- [[../../README]] — vault entry point
- [[../../memory]] — Josiah's memory
- [[../wednesday/WEDNESDAY_PIPELINE]] — Wednesday workflow (reference)
- [[../monday/MONDAY_PIPELINE]] — Monday workflow (reference)
- [[../thesis/THESIS_PIPELINE]] — Thesis workflow (reference)
