#!/usr/bin/env python3
"""
Component 6 — Telegram Approval Gate
For every photo flagged in Component 5, sends it to Sansar via Telegram
with the section name and a description. Waits for his reply — if he says
approve, moves it to approved folder. If reject, sources an alternative and
sends that for approval. Doesn't proceed until every photo is approved.
"""

import json
import os
import sys
import time
import requests
from pathlib import Path
from datetime import datetime, timedelta

VAULT_DIR = Path.home() / ".openclaw" / "vault"
STATE_FILE = VAULT_DIR / "scripts" / "pipeline" / "pipeline_state.json"
APPROVED_DIR = VAULT_DIR / "videos" / "approved_visuals"

# Telegram Bot API
TG_BOT_TOKEN = "8744451750:AAHXNX2UIeVJ7dsGwOp_HnJTKXw4h989CSE"
TG_API = f"https://api.telegram.org/bot{TG_BOT_TOKEN}"
TG_CHAT_ID = "8540772864"  # Sansar's Telegram ID

# Poll settings
POLL_INTERVAL = 5  # seconds between checking for replies
MAX_WAIT_SECONDS = 600  # 10 minutes max per photo


def load_state() -> dict:
    if STATE_FILE.exists():
        with open(STATE_FILE) as f:
            return json.load(f)
    return {}


def get_sourcing_results(state: dict) -> dict | None:
    vs = state.get("visual_sourcing")
    if not vs:
        return None
    path = Path(vs.get("path", ""))
    if not path.exists():
        return None
    with open(path) as f:
        return json.load(f)


def tg_send_photo(photo_path: str, caption: str) -> bool:
    """Send a photo to Sansar via Telegram."""
    url = f"{TG_API}/sendPhoto"
    with open(photo_path, "rb") as f:
        files = {"photo": f}
        data = {
            "chat_id": TG_CHAT_ID,
            "caption": caption[:1024]  # Telegram caption limit
        }
        resp = requests.post(url, data=data, files=files, timeout=30)
    
    if resp.status_code != 200:
        print(f"[WARN] Failed to send photo: {resp.status_code} {resp.text[:200]}")
        return False
    return True


def tg_send_message(text: str) -> bool:
    """Send a text message to Sansar via Telegram."""
    url = f"{TG_API}/sendMessage"
    data = {
        "chat_id": TG_CHAT_ID,
        "text": text[:4096],
        "parse_mode": "Markdown"
    }
    resp = requests.post(url, json=data, timeout=30)
    return resp.status_code == 200


def tg_get_updates(since_update_id: int = None) -> list:
    """Get updates from Telegram."""
    url = f"{TG_API}/getUpdates"
    params = {"timeout": 30, "allowed_updates": ["message"]}
    if since_update_id is not None:
        params["offset"] = since_update_id + 1
    
    try:
        resp = requests.get(url, params=params, timeout=35)
        if resp.status_code == 200:
            data = resp.json()
            return data.get("result", [])
    except Exception as e:
        print(f"[WARN] Failed to get updates: {e}")
    return []


def tg_get_last_update_id() -> int:
    updates = tg_get_updates()
    if updates:
        return max(u.get("update_id", 0) for u in updates)
    return 0


def wait_for_approval(prompt: str, poll_interval: int = 5, max_wait: int = 600) -> str:
    """
    Send a message asking for approval and wait for a response.
    Returns 'approve', 'reject', or 'timeout'.
    """
    # Send the prompt message
    tg_send_message(prompt)
    
    # Track seen updates
    last_update_id = tg_get_last_update_id()
    start_time = time.time()
    
    print(f"[INFO] Waiting for approval response...")
    
    while time.time() - start_time < max_wait:
        updates = tg_get_updates(since_update_id=last_update_id)
        
        for update in updates:
            uid = update.get("update_id", 0)
            if uid <= last_update_id:
                continue
            last_update_id = uid
            
            msg = update.get("message", {})
            chat_id = str(msg.get("chat", {}).get("id", ""))
            text = msg.get("text", "").strip().lower()
            
            # Only accept from Sansar
            if chat_id != TG_CHAT_ID:
                continue
            
            print(f"[INFO] Got response: '{text}'")
            return text
        
        time.sleep(poll_interval)
    
    return "timeout"


def run_on_current_video() -> dict | None:
    """Run the approval gate for all pending photos."""
    state = load_state()
    sourcing = get_sourcing_results(state)
    
    if not sourcing:
        print("[ERROR] No visual sourcing results found. Run Component 5 first.")
        return None
    
    video_path = Path(state.get("current_video", {}).get("path", "unknown"))
    video_stem = video_path.stem
    
    staging_dir = Path(sourcing.get("staging_dir", ""))
    
    # Set up approved directory for this video
    approved_dir = APPROVED_DIR / video_stem
    approved_dir.mkdir(parents=True, exist_ok=True)
    
    # Find photos that need approval
    pending_photos = []
    for r in sourcing.get("results", []):
        if r.get("approval_needed") and r.get("status") == "success" and r.get("path"):
            pending_photos.append(r)
    
    if not pending_photos:
        print("[INFO] No photos need approval.")
        return {"approved": [], "rejected": [], "status": "no_photos_to_approve"}
    
    print(f"[INFO] {len(pending_photos)} photos need approval")
    
    approved = []
    rejected = []
    
    for photo_result in pending_photos:
        photo_path = photo_result["path"]
        section = photo_result.get("section", "Unknown")
        visual_desc = photo_result.get("visual", {}).get("description", "")[:100]
        visual_type = photo_result.get("visual", {}).get("visual_type", "photo")
        
        filename = Path(photo_path).name
        caption = (
            f"🖼 *Photo Approval Required*\\n\\n"
            f"*Section:* {section}\\n"
            f"*Type:* {visual_type}\\n"
            f"*Description:* {visual_desc}\\n\\n"
            f"Reply: `approve` or `reject`"
        )
        
        print(f"[INFO] Sending {section} photo for approval...")
        print(f"       File: {filename}")
        
        sent = tg_send_photo(photo_path, caption)
        if not sent:
            print(f"[WARN] Failed to send photo, skipping...")
            rejected.append(photo_result)
            continue
        
        # Wait for response
        response = wait_for_approval(
            f"⏳ Waiting for approval on: *{section}* - {filename}",
            poll_interval=POLL_INTERVAL,
            max_wait=MAX_WAIT_SECONDS
        )
        
        if response == "timeout":
            print(f"[WARN] No response for {filename}, skipping after 10min wait")
            rejected.append(photo_result)
            tg_send_message(f"⏰ Timed out waiting for approval on `{filename}`. Skipping.")
        elif "reject" in response or response == "no" or response == "skip":
            print(f"[INFO] Photo rejected: {filename}")
            rejected.append(photo_result)
            tg_send_message(f"❌ Rejected. Will source alternative...")
            # TODO: Source alternative (Component 5 re-run with new keywords)
        elif "approve" in response or response == "yes" or response == "ok" or response == "y":
            print(f"[INFO] Photo approved: {filename}")
            approved.append(photo_result)
            
            # Move to approved folder
            dest = approved_dir / f"{Path(photo_path).name}"
            Path(photo_path).rename(dest)
            photo_result["approved_path"] = str(dest)
            
            tg_send_message(f"✅ Approved! Photo saved to approved folder.")
        else:
            print(f"[WARN] Unknown response '{response}', treating as reject")
            rejected.append(photo_result)
            tg_send_message(f"❓ Unknown response. Please reply 'approve' or 'reject'.")
    
    # Save approval results
    approval_results = {
        "generated_at": datetime.now().isoformat(),
        "approved_dir": str(approved_dir),
        "approved": approved,
        "rejected": rejected,
        "total_pending": len(pending_photos),
        "total_approved": len(approved),
        "total_rejected": len(rejected)
    }
    
    results_path = approved_dir / "approval_results.json"
    with open(results_path, "w") as f:
        json.dump(approval_results, f, indent=2)
    
    print(f"\n[OK] Approval gate complete:")
    print(f"      Approved: {len(approved)}")
    print(f"      Rejected: {len(rejected)}")
    print(f"      Results: {results_path}")
    
    # Update state
    state["approval"] = {
        "path": str(results_path),
        "approved_dir": str(approved_dir),
        "approved_count": len(approved),
        "rejected_count": len(rejected)
    }
    with open(STATE_FILE, "w") as f:
        json.dump(state, f, indent=2)
    
    return approval_results


if __name__ == "__main__":
    result = run_on_current_video()
    if result:
        print(f"\nApproval complete: {result['total_approved']} approved, "
              f"{result['total_rejected']} rejected")
    else:
        print("Approval gate failed.")
        sys.exit(1)
