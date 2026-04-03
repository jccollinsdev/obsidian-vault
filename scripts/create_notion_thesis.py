#!/usr/bin/env python3
import json
import os

NOTION_TOKEN = open(os.path.expanduser("~/.config/openclaw/notion.env")).readlines()[0].strip().split("=")[1]

url = "https://api.notion.com/v1/pages"

payload = {
    "parent": {"page_id": "336b951f-a902-8190-b31f-f40e436418cb"},
    "properties": {
        "title": {"title": [{"text": {"content": "GDX — Gold Miners Bullish Thesis (Apr 2, 2026)"}}]}
    },
    "children": [
        {"object": "block", "type": "heading_2", "heading_2": {"rich_text": [{"text": {"content": "The Thesis"}}]}},
        {"object": "block", "type": "paragraph", "paragraph": {"rich_text": [{"text": {"content": "GDX is the leveraged play on a gold bull market driven by four forces hitting at once: stagflation, active Middle East conflict, oil-driven inflation shock, and Fed rate cuts. Gold surged past $4,769/oz on April 1 after a brutal March crash that wiped 15% off — that dip is the entry."}}]}},
        {"object": "block", "type": "heading_2", "heading_2": {"rich_text": [{"text": {"content": "Key Data"}}]}},
        {"object": "block", "type": "bulleted_list_item", "bulleted_list_item": {"rich_text": [{"text": {"content": "Gold: $4,769+/oz (Apr 1, 2026) — recovered after 15% March crash"}}]}},
        {"object": "block", "type": "bulleted_list_item", "bulleted_list_item": {"rich_text": [{"text": {"content": "GDX: ~$88 post-crash, vs ~$115 all-time highs six weeks prior"}}]}},
        {"object": "block", "type": "bulleted_list_item", "bulleted_list_item": {"rich_text": [{"text": {"content": "Gold rose 23.9% in the month before the Iran war — fastest pre-conflict spike since 1979"}}]}},
        {"object": "block", "type": "bulleted_list_item", "bulleted_list_item": {"rich_text": [{"text": {"content": "Iran conflict closed Strait of Hormuz briefly, crushed Middle East energy output"}}]}},
        {"object": "block", "type": "bulleted_list_item", "bulleted_list_item": {"rich_text": [{"text": {"content": "Fed signaling 2026 rate cuts — reduces opportunity cost of holding gold"}}]}},
        {"object": "block", "type": "bulleted_list_item", "bulleted_list_item": {"rich_text": [{"text": {"content": "Top holdings: Newmont (NEM), Agnico Eagle (AEM) — printing cash at $4,700+ gold"}}]}},
        {"object": "block", "type": "heading_2", "heading_2": {"rich_text": [{"text": {"content": "Bull Case"}}]}},
        {"object": "block", "type": "bulleted_list_item", "bulleted_list_item": {"rich_text": [{"text": {"content": "Stagflation: gold thrives in slow growth + hot inflation — exactly 2026"}}]}},
        {"object": "block", "type": "bulleted_list_item", "bulleted_list_item": {"rich_text": [{"text": {"content": "Miners have 2-3x leverage to gold price movement"}}]}},
        {"object": "block", "type": "bulleted_list_item", "bulleted_list_item": {"rich_text": [{"text": {"content": "March crash = panic exit = smart money entry at $88"}}]}},
        {"object": "block", "type": "bulleted_list_item", "bulleted_list_item": {"rich_text": [{"text": {"content": "Central banks buying gold at record pace — structural floor"}}]}},
        {"object": "block", "type": "heading_2", "heading_2": {"rich_text": [{"text": {"content": "Risks"}}]}},
        {"object": "block", "type": "bulleted_list_item", "bulleted_list_item": {"rich_text": [{"text": {"content": "Iran de-escalation = gold retraces"}}]}},
        {"object": "block", "type": "bulleted_list_item", "bulleted_list_item": {"rich_text": [{"text": {"content": "Oil shock could force Fed to hold — cuts slower than expected"}}]}},
        {"object": "block", "type": "bulleted_list_item", "bulleted_list_item": {"rich_text": [{"text": {"content": "Dollar strength caps near-term gold"}}]}},
        {"object": "block", "type": "heading_2", "heading_2": {"rich_text": [{"text": {"content": "Vault Link"}}]}},
        {"object": "block", "type": "paragraph", "paragraph": {"rich_text": [{"text": {"content": "theses/GDX_Bullish_Gold_Miners.md"}}]}}
    ]
}

import urllib.request
req = urllib.request.Request(
    url,
    data=json.dumps(payload).encode(),
    headers={
        "Authorization": f"Bearer {NOTION_TOKEN}",
        "Content-Type": "application/json",
        "Notion-Version": "2022-06-28"
    },
    method="POST"
)
with urllib.request.urlopen(req) as resp:
    result = json.load(resp)
    print("URL:", result.get("url", "no url"))
    print("ID:", result.get("id", "no id"))
