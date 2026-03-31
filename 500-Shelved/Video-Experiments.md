# Video Production Experiments — Shelved

## Remotion Cinematic Skill
**Built:** March 28, 2026
**Deleted:** March 30, 2026
**Why:** Too complex for the content pipeline — simplified to direct Remotion/FFmpeg workflow.

## Python/PIL Video Renderer
**Built:** March 30, 2026 for Password Heist ad
**Still usable:** Yes — good for simple animated ads without React/Remotion overhead
**Location:** `/tmp/kobrain-ad.py` (source), `/videos/kobrain-password-heist-ad.mp4` (output)

## Remotion Studio (Node 20 Fix)
**Issue:** `@remotion/studio/renderEntry` resolution failed on Node v24
**Fix:** Node 20 LTS installed alongside v24
**Status:** Working — Remotion Studio runs on port 3000 via Node 20
**Note:** `node:worker_threads` and `node:zlib` webpack errors are non-fatal

## Coinbase Ad (FFmpeg Pipeline)
**Built:** March 30, 2026
**Output:** `/videos/coinbase-ad-2026-03-30.mp4` (30s, 1080x1920, 4.1MB)
**Pipeline:** AI image generation → FFmpeg composition → H.264 encode
**Status:** Template still valid for future vertical ads

## All Video Files
- `/videos/coinbase-ad-2026-03-30.mp4`
- `/videos/kobrain-password-heist-ad.mp4`
- `/videos/kobrain-logo-concept-1.png` through `kobrain-logo-concept-4.png`
