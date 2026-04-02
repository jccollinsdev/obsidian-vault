#!/usr/bin/env python3
"""
Component 1 — Email Monitor
Watches jc.collins.dev@gmail.com for an email from Sansar saying recording is done.
When found, downloads the attached video file to videos/in_progress/.
"""

import os
import json
import subprocess
import time
import re
import base64
import requests
from pathlib import Path
from datetime import datetime

GMAIL_ACCOUNT = "jc.collins.dev@gmail.com"
VAULT_DIR = Path.home() / ".openclaw" / "vault"
IN_PROGRESS_DIR = VAULT_DIR / "videos" / "in_progress"
STATE_FILE = VAULT_DIR / "scripts" / "pipeline" / "pipeline_state.json"
TOKEN_CACHE = VAULT_DIR / "scripts" / "pipeline" / ".gog_token_cache.json"
POLL_INTERVAL = 60  # seconds

# gog OAuth2 credentials
GOG_CLIENT_ID = "753225460608-bd3lku25q7csopediqmqmaidqq061u2h.apps.googleusercontent.com"
GOG_CLIENT_SECRET = "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"

RECORDING_DONE_KEYWORDS = [
    "recording done", "recording is done", "done recording",
    "video ready", "here's the recording", "attached is the recording",
    "recording attached", "video attached", "recordings attached"
]


def get_gog_refresh_token() -> str | None:
    """Export the gog refresh token from keyring."""
    try:
        result = subprocess.run(
            ["gog", "auth", "tokens", "export", GMAIL_ACCOUNT,
             "--account", GMAIL_ACCOUNT,
             "--out", "/tmp/gog_refresh_token.json",
             "--overwrite"],
            capture_output=True, text=True,
            env={**os.environ, "GOG_KEYRING_PASSWORD": "josiah123"},
            timeout=10
        )
        if result.returncode == 0 and Path("/tmp/gog_refresh_token.json").exists():
            with open("/tmp/gog_refresh_token.json") as f:
                data = json.load(f)
            return data.get("refresh_token")
    except Exception as e:
        print(f"[ERROR] Could not export gog refresh token: {e}")
    return None


def get_access_token() -> str | None:
    """Get a fresh OAuth2 access token using the cached gog refresh token."""
    # Load cached token if still valid
    if TOKEN_CACHE.exists():
        with open(TOKEN_CACHE) as f:
            cache = json.load(f)
        if cache.get("expires_at", 0) > time.time() + 60:
            return cache["access_token"]
    
    # Get fresh token
    refresh_token = get_gog_refresh_token()
    if not refresh_token:
        return None
    
    try:
        resp = requests.post(
            "https://oauth2.googleapis.com/token",
            data={
                "client_id": GOG_CLIENT_ID,
                "client_secret": GOG_CLIENT_SECRET,
                "refresh_token": refresh_token,
                "grant_type": "refresh_token"
            },
            timeout=10
        )
        if resp.status_code == 200:
            data = resp.json()
            access_token = data.get("access_token")
            expires_in = data.get("expires_in", 3600)
            
            # Cache the token
            TOKEN_CACHE.parent.mkdir(parents=True, exist_ok=True)
            with open(TOKEN_CACHE, "w") as f:
                json.dump({
                    "access_token": access_token,
                    "expires_at": time.time() + expires_in
                }, f)
            
            return access_token
    except Exception as e:
        print(f"[ERROR] Failed to get access token: {e}")
    return None


def gmail_api_get(endpoint: str, token: str, params: dict = None):
    """Make an authenticated GET request to the Gmail API."""
    headers = {"Authorization": f"Bearer {token}", "Accept": "application/json"}
    resp = requests.get(f"https://gmail.googleapis.com/gmail/v1{endpoint}",
                        headers=headers, params=params, timeout=30)
    if resp.status_code == 401:
        # Token expired - clear cache and retry once
        if TOKEN_CACHE.exists():
            TOKEN_CACHE.unlink()
        token = get_access_token()
        if token:
            headers["Authorization"] = f"Bearer {token}"
            resp = requests.get(f"https://gmail.googleapis.com/gmail/v1{endpoint}",
                              headers=headers, params=params, timeout=30)
    return resp


def load_state() -> dict:
    if STATE_FILE.exists():
        with open(STATE_FILE) as f:
            return json.load(f)
    return {"processed_message_ids": [], "current_video": None}


def save_state(state: dict):
    STATE_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(STATE_FILE, "w") as f:
        json.dump(state, f, indent=2)


def search_for_recording_emails(token: str) -> list[dict]:
    """Search for recent emails from Sansar."""
    query = "from:sansarkarki10@gmail.com newer_than:7d"
    resp = gmail_api_get("/users/me/messages", token, {"q": query, "maxResults": 10})
    if resp.status_code != 200:
        print(f"[WARN] Gmail search failed: {resp.status_code} {resp.text[:200]}")
        return []
    
    messages = resp.json().get("messages", [])
    results = []
    
    for msg_ref in messages:
        msg_id = msg_ref["id"]
        msg_resp = gmail_api_get(f"/users/me/messages/{msg_id}",
                                 token, {"format": "metadata",
                                        "metadataHeaders": ["Subject", "From", "Snippet"]})
        if msg_resp.status_code == 200:
            msg = msg_resp.json()
            payload = msg.get("payload", {})
            headers = {h["name"]: h["value"] for h in payload.get("headers", [])}
            results.append({
                "id": msg_id,
                "threadId": msg.get("threadId"),
                "subject": headers.get("Subject", ""),
                "from": headers.get("From", ""),
                "snippet": msg.get("snippet", "")
            })
    
    return results


def looks_like_recording_email(email: dict) -> bool:
    """Check if an email looks like a recording-done notification."""
    text = f"{email.get('subject', '')} {email.get('snippet', '')}".lower()
    for kw in RECORDING_DONE_KEYWORDS:
        if kw.lower() in text:
            return True
    return False


def download_video_attachment(token: str, message_id: str) -> Path | None:
    """Download the first video attachment from a Gmail message."""
    msg_resp = gmail_api_get(f"/users/me/messages/{message_id}", token, {"format": "full"})
    if msg_resp.status_code != 200:
        print(f"[ERROR] Could not fetch message: {msg_resp.status_code}")
        return None
    
    msg_data = msg_resp.json()
    payload = msg_data.get("payload", {})
    
    attachments = []
    
    def walk_parts(part):
        mime_type = part.get("mimeType", "")
        filename = part.get("filename", "")
        att_id = part.get("body", {}).get("attachmentId", "")
        
        if att_id and filename:
            video_exts = [".mp4", ".mov", ".avi", ".mkv", ".webm", ".m4v", ".MOV", ".MP4"]
            if any(filename.lower().endswith(ext.lower()) for ext in video_exts):
                attachments.append({"id": att_id, "filename": filename, "mimeType": mime_type})
        
        if "parts" in part:
            for sp in part["parts"]:
                walk_parts(sp)
    
    if "parts" in payload:
        for part in payload["parts"]:
            walk_parts(part)
    else:
        walk_parts(payload)
    
    if not attachments:
        print(f"[WARN] No video attachments found in message {message_id}")
        return None
    
    att = attachments[0]
    att_id = att["id"]
    original_filename = att["filename"]
    
    # Clean filename
    safe_name = re.sub(r'[^\w\s\-\.]', '_', original_filename)
    safe_name = re.sub(r'_+', '_', safe_name).strip('_-')
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_filename = f"{timestamp}_{safe_name}"
    output_path = IN_PROGRESS_DIR / output_filename
    IN_PROGRESS_DIR.mkdir(parents=True, exist_ok=True)
    
    # Download attachment
    headers = {"Authorization": f"Bearer {token}", "Accept": "application/json"}
    att_resp = requests.get(
        f"https://gmail.googleapis.com/gmail/v1/users/me/messages/{message_id}/attachments/{att_id}",
        headers=headers, timeout=60
    )
    if att_resp.status_code != 200:
        print(f"[ERROR] Could not download attachment: {att_resp.status_code}")
        return None
    
    att_data = att_resp.json()
    data_b64 = att_data.get("data", "")
    if not data_b64:
        print(f"[ERROR] No data in attachment response")
        return None
    
    file_data = base64.urlsafe_b64decode(data_b64 + "==")
    
    with open(output_path, "wb") as f:
        f.write(file_data)
    
    file_size = output_path.stat().st_size
    print(f"[OK] Downloaded '{original_filename}' ({file_size:,} bytes) -> {output_path}")
    return output_path


def poll_for_new_recordings(state: dict) -> Path | None:
    """Poll Gmail for new recording emails and download any found."""
    token = get_access_token()
    if not token:
        print("[ERROR] Could not get OAuth token")
        return None
    
    emails = search_for_recording_emails(token)
    print(f"[INFO] Checked {len(emails)} recent emails from Sansar")
    
    for email in emails:
        msg_id = email.get("id", "")
        if msg_id in state["processed_message_ids"]:
            continue
        
        if not looks_like_recording_email(email):
            continue
        
        print(f"[INFO] Recording email found: {email.get('subject', '')}")
        
        video_path = download_video_attachment(token, msg_id)
        
        if video_path and video_path.exists():
            state["processed_message_ids"].append(msg_id)
            state["current_video"] = {
                "path": str(video_path),
                "message_id": msg_id,
                "subject": email.get("subject", ""),
                "downloaded_at": datetime.now().isoformat()
            }
            save_state(state)
            return video_path
    
    return None


def run_once() -> Path | None:
    """Run the email monitor once (non-blocking)."""
    state = load_state()
    return poll_for_new_recordings(state)


def run_forever():
    """Run the email monitor in a continuous loop until a video is found."""
    print("[INFO] Component 1 — Email Monitor started (polling every 60s)")
    print(f"[INFO] Watching {GMAIL_ACCOUNT} for recordings from Sansar...")
    
    while True:
        state = load_state()
        result = poll_for_new_recordings(state)
        if result:
            print(f"[INFO] Video downloaded: {result}")
            return result
        time.sleep(POLL_INTERVAL)


if __name__ == "__main__":
    import sys
    if "--watch" in sys.argv:
        result = run_forever()
        if result:
            print(f"New recording detected: {result}")
    else:
        result = run_once()
        if result:
            print(f"New recording found: {result}")
        else:
            print("No new recording found.")
