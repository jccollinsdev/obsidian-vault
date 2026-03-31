# MEMORY.md — Long-Term Memory

> **Primary source:** This file is the curated long-term memory for OpenClaw. It is the distilled essence of important decisions, context, and lessons — not raw session logs. Daily raw logs go in `Daily/` folder.

## Who I'm Helping

**Name:** Sansar Karki (also known as Josiah Collins as AI persona)
**Age:** 8th grader (young founder)
**Location:** Andover, Massachusetts
**Timezone:** America/New_York (EST/EDT)
**Pronouns:** he/him
**Email:** SansarKarki10@gmail.com

## CURRENT FOCUS: Investment Analysis Content Pipeline ⚠️

**Status (2026-03-31): COMPLETE RESTRUCTURE — Obsidian is now primary, Notion is dashboard.**

Sansar has 5 years of investing experience in energy markets and stocks. Building a content brand around investment theses. I (the AI) handle all the content production grunt work.

### The Flywheel
1. Thesis → OpenClaw generates report via `/thesis [ticker]`
2. Report approved → talking points pulled every 2 days
3. Sansar records voice (talking through talking points)
4. Whisper transcribes audio → text
5. B-roll planned by OpenClaw
6. Remotion renders animated video
7. Sansar's audio synced to video
8. FFmpeg final edit
9. Auto-upload to YouTube
10. Daily thesis monitoring → email to Sansar

### Daily Thesis Monitoring
- I monitor investment theses every day
- Send clean organized email to sansarkarki10@gmail.com with news + developments

### Content Outputs Per Thesis
- YouTube video (5 min, animated)
- Blog post (SEO-optimized)
- Twitter/X thread
- Discord update
- Newsletter section

**Platform:** YouTube (primary/top of funnel) — auto-upload via YouTube API
**Email:** SansarKarki10@gmail.com

### ⚠️ Memory Gap Prevention
When session resets via `/new`, I lose recent conversation history. After any big decision or pivot, ALWAYS update this file immediately and save session summary to Obsidian.

## Active Portfolio Theses

| Ticker | Rating | Price | Target | Date | Status |
|--------|--------|-------|--------|------|--------|
| EWY | BUY | $120.71 | $135-$158 | 2026-03-31 | Active |
| GDX | BUY | $91.08 | $105-$140 | 2026-03-31 | Active |
| NVO | BUY | $36.39 | $55-$78 | 2026-03-31 | Active |

## Tech Stack

| Tool | Purpose | Status |
|------|---------|--------|
| FFmpeg | Video editing | ✅ Working |
| thesis-researcher skill | Live market data + PDF thesis reports | ✅ Working |
| YouTube Data API | Auto-upload | ❌ Pending OAuth setup |
| Gmail (gog) | Email sending/receiving | ✅ Working |
| Whisper | Audio transcription | ❌ Not installed |
| Remotion | Animated video rendering | ✅ Working |
| Obsidian CLI | Vault management | ✅ Working |

## Obsidian Knowledge Base ✅

**Vault:** `/home/openclaw/obsidian-vault`
**GitHub:** https://github.com/jccollinsdev/knowledge-base
**Structure:**
- `000-Projects/` — active projects
- `100-Memory/` — long-term memory + sessions + daily logs
- `200-Knowledge/` — tech stack, skills, how things work
- `300-Investment-Theses/` — all thesis notes + PDFs
- `400-Daily-Logs/` — daily logs

## Video Production Workflow

**Trigger phrase:** "make a video"
**Tool:** Remotion (React-based animated video)
**Refine loop:** Render → show Sansar → refine → repeat
**Output:** `/home/openclaw/obsidian-vault/videos/`
**Remotion project:** `/home/openclaw/remotion-projects/thesis-video/`
**Style:** Discrete scenes + spring animations. NOT continuous camera. NOT PowerPoint.

## Skills Built

### Thesis Researcher
- Location: `/home/openclaw/.openclaw/workspace/skills/thesis-researcher/`
- Usage: `/thesis [ticker] [optional thesis description]`
- Pulls yfinance data: ticker, gold, oil, DXY, 10Y yield
- Generates hedge-fund quality PDF thesis reports (7 sections)

## Andover Digital — Our Company

**Business:** Investment Analysis Content Brand
**GitHub:** https://github.com/jccollinsdev/kobrain
**Note:** Pivoted from Kobrain AI Teammate Platform

## Kobrain — ON HOLD (not deleted)

**One-liner:** "Your AI teammate. Has an inbox. Does the work."
**Landing:** https://kobrain-deploy.vercel.app
**GitHub:** https://github.com/jccollinsdev/kobrain

## My Setup

- **Gateway:** Running at ws://127.0.0.1:18789
- **Workspace:** /home/openclaw/.openclaw/workspace
- **Display:** :2 (1920x1080) — Orange Pi 5B
- **Telegram bot token:** `8720329434:AAFcrWBeF8NGHTqN9XdllGkCsdGg6B84HHo`

## Integrations

| Service | Status | Account |
|---------|--------|---------|
| Google Workspace | ✅ Working | jc.collins.dev@gmail.com |
| Notion | ✅ Working | Bot account (API key in secrets) — dashboard only |
| GitHub | ✅ Working | jccollinsdev |
| Vercel | ✅ Working | jccollinsdev |
| YouTube | ❌ Pending | OAuth setup needed |
| Gmail | ✅ Working | Via gog CLI |
| Obsidian | ✅ Working | Vault at /home/openclaw/obsidian-vault |

## Preferences

- **No eagle emoji** at end of messages
- **Discrete scenes + spring animations** — preferred video style
- **Concise responses** — no corporate filler
- **Session summaries** — write to Obsidian first, then push a summary to Notion

## Key Dates

- **2026-03-24:** Discovered Sansar, Kobrain project started
- **2026-03-28:** PIVOT DAY — Kobrain shelved, investment content pipeline launched
- **2026-03-30:** Coinbase ad + Kobrain logo + video production refinements
- **2026-03-31:** Complete restructure — Obsidian primary, Notion dashboard
