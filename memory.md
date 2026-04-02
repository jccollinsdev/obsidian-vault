# Josiah Memory
Last updated: 2026-04-02

## Active Theses
— none yet —

## Recent Lessons (Monday content)
— none yet —

## Pipeline State
— none yet —

## Pending
— none yet —

## Script Formatting Rules (locked in Apr 2, 2026)
- Section labels: NO numbers — use [SECTION: TOPIC NAME] not [SECTION: 1 — TOPIC NAME]
- Opening line: Name specific headlines, don't be vague. Match Sansar's blog style — lead with the actual stories.
  - ✅ "Iran ceasefire, SpaceX IPO, oil at $111, and an FDA approval that just kicked off the GLP-1 wars — it's your midweek recap and we've got a lot to cover."
  - ❌ "So this week in the markets was basically a geopolitical roller coaster..."
- Photos need approval. Articles and charts are auto-approved.
- Always end scripts with standard disclaimer.

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

## Vault Structure
- [[README]] — vault entry point
- [[pipeline/Josiah_System_Prompt]] — my identity and rules
- [[scripts/pipeline/WEDNESDAY_PIPELINE]] — Wednesday workflow
- [[scripts/wednesday/2026-04-02_midweek_recap]] — today's script
