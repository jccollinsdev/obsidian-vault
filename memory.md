# Josiah Memory

## /THESIS WORKFLOW — CALIBRATION (Apr 3, 2026)

**CRITICAL: Sansar's calibration for all thesis work**

- Be **CONSERVATIVE and HARSH** when evaluating ideas
- Not all ideas Sansar suggests will work — it's my job to find the ones that don't
- Model **CORRECTLY first** — don't let assumptions drift to make the thesis look better
- Run **consistency check** on every thesis before presenting
- If the model says "this doesn't work" — say so. Say it clearly. Don't sugarcoat.
- The goal is a thesis that **survives scrutiny**, not one that sounds good
- This calibration is **locked in** — it applies to every /thesis run going forward

---

## Active Theses
- **GDX** (VanEck Gold Miners ETF) — Bullish (v2, consistency-corrected) — Rebuilt Apr 3, 2026
  - Vault: theses/GDX_Bullish_Gold_Miners.md (honest BUY call)
  - Key finding: GDX at $94.59 is FAIR VALUE at current gold $4,651. Not undervalued now. BUY is a 12-month catalyst trade: target $102–107 if gold reaches $4,800 (+8–13% upside). Bull case $5,500 → $120–130 (+27–37%).
  - Scripts: scripts/gdx_model.py (all 9 model steps), scripts/gdx_consistency_check.py (consistency verification)
  - CONSISTENCY ISSUES FOUND: Original scenario targets were hardcoded wrong. BUY threshold check showed only 2.2% upside at current gold (not 10%+). All reconciled in v2.

## Recent Lessons (Monday content)
— none yet —

## Pipeline State
— none yet —

## Pending
- **Mon Apr 6:** Monday thesis video -- Sansar will pick the stock/idea. Need a thesis brief from him first.
- **Fri Apr 3:** Friday "Week in Review" pipeline + script still to build
- **Apr 3 PM:** Sansar requested full internal thesis generation prompt/pipeline documentation -- to be shared with him

## Script Formatting Rules (locked in Apr 2, 2026)
- Section labels: NO numbers -- use [SECTION: TOPIC NAME] not [SECTION: 1 -- TOPIC NAME]
- Opening line: Name specific headlines, don't be vague. Match Sansar's blog style -- lead with the actual stories.
  - [OBSOLETE -- See Writing Style Rules below]
- Photos need approval. Articles and charts are auto-approved.
- Always end scripts with standard disclaimer.

## WRITING STYLE RULES -- NON-NEGOTIABLE (added Apr 3, 2026)
All thesis outputs must follow these rules (also in THESIS_PIPELINE.md):
- Goldman/JPMorgan institutional sector note voice -- not a newsletter
- Every sentence: number, source, or specific claim -- no filler
- No rhetorical questions
- Banned phrases: "here's what most investors miss", "the real story", "the truth about", anything Seeking Alpha / Motley Fool
- Inverted pyramid: conclusion first, then support
- Explicit hedges: "we estimate", "subject to", "based on", "assuming"
- Zero exclamation points
- Ban the word "moment" -- state actual catalyst instead
- Retail newsletter filter: rewrite if it could appear in Seeking Alpha

## Script Delivery Preference
- Put script in Notion FIRST
- Email ONLY the Notion link to sansarkarki10@gmail.com — NEVER paste full script text in email body
- Notion page already exists for most content types
- Email subject line: 📹 [Date] — [Script Type] Script

## Post-Recording Video Pipeline (built Apr 2, 2026)
- Location: vault/scripts/pipeline/
- Orchestrator: run_pipeline.py (runs all 7 components in sequence)
- Components:
  1. Email Monitor → watches Gmail for recording emails, downloads video
  2. Whisper Runner → transcribes with word-level timestamps
  3. Topic Segmenter → maps transcript words to script [SECTION: X] labels
  4. Visual Proposer → proposes 3 visuals per section (article/chart/photo)
  5. Visual Sourcer → Crawl4AI for articles/charts, Bing Images for stock photos
  6. Telegram Approval Gate → sends photos to Sansar for approval
  7. FFmpeg Compiler → compiles final video with labels, overlays, zoom effects
- Usage: `python3 scripts/pipeline/run_pipeline.py --dry-run` (test) or `--component N` to start from N
- State file: scripts/pipeline/pipeline_state.json (shared between components)
- OAuth: uses gog refresh token for Gmail API (stored at scripts/pipeline/.gog_token_cache.json)
- Telegram bot: AIJosiah_bot (token:8744451750:AAHXNX2UIeVJ7dsGwOp_HnJTKXw4h989CSE)

## Notes
- First boot complete. Tools set up. Vault initialized.
- Pipeline spec received and filed in vault/pipeline/
- System prompt filed in vault/pipeline/
- Full vault folder structure created and committed
- Script delivery workflow set up Apr 2, 2026
- Thesis calibration (conservative/harsh) locked in Apr 3, 2026

## Vault Structure
- [[README]] — vault entry point
- [[pipeline/Josiah_System_Prompt]] — my identity and rules
- [[scripts/pipeline/WEDNESDAY_PIPELINE]] — Wednesday workflow
- [[scripts/wednesday/2026-04-02_midweek_recap]] — today's script
