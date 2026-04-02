# Wednesday Market Recap — Pipeline Docs

**Purpose:** Produce a polished midweek market recap video for Sansar's YouTube channel.

---

## Workflow Overview

1. Trigger: user runs `/wednesday`
2. Research — scrape market news, get price data, find chart images
3. Script — write in Sansar's voice, label [SECTION: X] throughout
4. Visuals — source photos, take article screenshots, pull charts
5. Assemble — build Remotion video with sections, overlays, labels
6. Deliver — script to Notion, email link to sansarkarki10@gmail.com
7. Render — output to `vault/videos/completed/`

---

## Step-by-Step

### 1. Research

**News sources (preferred):**
- AP News — `apnews.com`
- CNBC — `cnbc.com`
- The National — `thenationalnews.com`
- CNN Business — `edition.cnn.com/business`
- NBC News — `nbcnews.com/business`

**BLOCKED:** Reuters (advanced bot blocking — do not use)

**Article screenshots:** Use `article_screenshot.py` (see below).

**Stock charts:** Search Bing for `[TICKER] stock chart April 2026` — pull via Bing scraper or screenshot from Yahoo Finance / Google Finance.

**Price data:** Web search for current prices and market data. Never invent numbers.

### 2. Script

- Write in Sansar's voice — chill, punchy, data-grounded, mild edge
- Label every section with `[SECTION: TOPIC NAME]` (no numbers)
- Lead with real headlines — name specific stories
- End with TLDR: that has color and opinion
- Standard disclaimer at the end

**Delivery:**
- Put script in Notion first
- Email ONLY the Notion link to `sansarkarki10@gmail.com`
- Subject: `📹 [Date] — Wednesday Script`
- Never paste full script in email body

### 3. Visuals

#### Stock Photos (Bing Scraper)
```bash
python3 /home/openclaw/google-image-scraper/bing_scraper.py \
  "SEARCH QUERY" 5 /path/to/output_folder
```

**Rules:**
- Always verify images are REAL PHOTOGRAPHS — use the `image` tool to analyze before using
- AI-generated images are common for queries like "SpaceX IPO", "stock market future", "crypto"
- Look for: real launches (SpaceX), real trading floors, real people, real charts
- Avoid: concept art, floating charts in space, fake candlesticks, illustrative graphics

#### Article Screenshots
```bash
python3 /home/openclaw/.openclaw/vault/scripts/pipeline/article_screenshot.py
```

Edit `ARTICLE_URLS` dict inside the script to set the 4 URLs for that week's stories.

**Stealth settings baked in:**
- Viewport: 1920×1080
- User Agent: Mac Chrome (realistic)
- Init script patches: `navigator.webdriver`, `navigator.plugins`, `navigator.languages`, `window.chrome`, `navigator.permissions`

**Output:** PNG screenshots saved to `remotion-video/public/`

### 4. Remotion Video Assembly

**Config file:** `vault/scripts/pipeline/remotion-video/src/Root.tsx`

```tsx
const SLIDES = [
  { imagePath: "photo_IRAN/image_002.jpg", title: "Iran Ceasefire Rally" },
  { imagePath: "photo_OIL/image_002.jpg", title: "Oil Shock Reversal" },
  // ...
];
```

**Component:** `vault/scripts/pipeline/remotion-video/src/Video.tsx`
- `Slideshow` — centered image + title, 3s display, 1s gap
- `CenteredSlide` — fade in/out, subtle scale animation
- `SectionLabel` — bold white uppercase, semi-transparent bg, alternating corners
- `CornerOverlay` — photo at bottom-right with slide-in and fade effects
- `FullScreenOverlay` — article screenshot full-frame takeover
- `FaceZoom` — Ken Burns-style zoom on face moments

**Preview server:**
```bash
cd vault/scripts/pipeline/remotion-video
npm run start -- --port 3000 --force-new
# Live at http://localhost:3000
```

**Render:**
```bash
npx remotion render SansarSlideshow /path/to/output.mp4 --fps 25
# or for full video composition:
npx remotion render SansarVideo /path/to/output.mp4 --fps 25
```

**Output:** `vault/videos/completed/YYYY-MM-DD_WEDNESDAY_vX.mp4`

### 5. Folder Structure

```
vault/scripts/pipeline/remotion-video/
├── public/
│   ├── photo_IRAN/       # stock photos
│   ├── photo_OIL/
│   ├── photo_SPACEX/
│   ├── photo_LILLY/
│   ├── article_IRAN.png  # article screenshots
│   ├── article_OIL.png
│   ├── article_SPACEX.png
│   ├── article_LILLY.png
│   └── test_dummy_20260402.mp4  # base video
├── src/
│   ├── Video.tsx         # React components
│   └── Root.tsx          # composition config
└── package.json

vault/videos/
├── completed/
│   └── YYYY-MM-DD_*.mp4  # rendered output
└── in_progress/
```

---

## Current Test State (Apr 2, 2026)

Working slideshow format: centered image + title, 3s per slide, 1s gap.
- `2026-04-02_SLIDESHOW_v2.mp4` — latest working render
- Server: `http://localhost:3000`

Real SpaceX Falcon 9 launch photo confirmed good.
AI-generated image detection working — always verify with `image` tool.

---

## Photo Sourcing Rules

| Query Type | Risk | Action |
|------------|------|--------|
| Real company/event | Low | Verify with image analysis |
| IPO/concept/future | High | Almost always AI — find alternative angle |
| Charts/graphs | Medium | Prefer real screenshots, not Bing scraper |
| People | Medium | Verify — AI faces common |

**Preferred sources for photos:**
- SpaceX: `SpaceX Falcon rocket launch real photo`
- Oil/energy: `oil refinery real photo`
- Markets/trading: `NYSE trading floor real photo`
- Pharma: `Eli Lilly factory real photo`

---

## Key Docs

- [[../../README]] — vault entry point
- [[../../memory]] — Josiah's memory
- [[../wednesday/2026-04-02_midweek_recap]] — today's script (example output)
