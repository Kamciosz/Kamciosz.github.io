"""Pobiera wiadomości z wątku STEM Discord i parsuje je w struktury tematyczne.

Wyjście: data/raw/<YYYY-MM-DD>.json
"""
import json
import os
import re
import ssl
import sys
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

THREAD_IDS = ["1512398228384120864", "1513893149502607522"]  # Newsletter, Blog
TOKEN_PATH = Path.home() / ".hermes/discord_user_token.txt"
RAW_DIR = Path(__file__).parent.parent / "data" / "raw"
RAW_DIR.mkdir(parents=True, exist_ok=True)


def load_token() -> str:
    # 1) Env var (GitHub Actions)
    token = os.environ.get("DISCORD_USER_TOKEN", "").strip()
    if token:
        return token
    # 2) Plik (lokalny)
    if TOKEN_PATH.exists():
        token = TOKEN_PATH.read_text().strip()
    if not token:
        sys.exit(f"Token missing: set DISCORD_USER_TOKEN env var or create {TOKEN_PATH}")
    return token


def fetch_messages(token: str, thread_id: str, limit: int = 50) -> list:
    """Pobiera ostatnie `limit` wiadomości z wątku."""
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE
    url = f"https://discord.com/api/v10/channels/{thread_id}/messages?limit={limit}"
    req = urllib.request.Request(
        url,
        headers={"Authorization": token, "User-Agent": "Mozilla/5.0"},
    )
    with urllib.request.urlopen(req, timeout=30, context=ctx) as resp:
        data = json.loads(resp.read())
    return list(reversed(data))


def parse_topic(content: str) -> tuple[str | None, int | None, int | None]:
    """Zwraca (topic_label, topic_index, topic_total) jeśli wiadomość ma prefiks **[N/M]."""
    m = re.match(r"^\*\*\[(\d+)/(\d+)\]\s*(.+?)(?:\s*-\s*|\*\*|$)", content)
    if not m:
        return None, None, None
    label = m.group(3).strip().rstrip("*").strip()
    # Wycinamy "(1/2)", "(2/2)", "(1/5)" etc. z label
    label = re.sub(r"\s*\(\d+/\d+\)\s*$", "", label)
    return label, int(m.group(1)), int(m.group(2))


def group_into_topics(messages: list) -> list[dict]:
    """Grupuje wiadomości w tematy.

    Strategia:
    - parsuj (label, idx, total) z **[N/M]**
    - wyciągnij klucz tematu: label przed " - " (jeśli istnieje)
    - fuzzy match (difflib ratio >= 0.55) scala podobne klucze (np. "AMD MI400 + Helios rack"
      vs "AMD MI400 + Helios")
    """
    from difflib import SequenceMatcher

    parsed: list[dict] = []
    for msg in messages:
        content = msg.get("content", "")
        label, idx, total = parse_topic(content)
        if not label:
            continue
        # Wytnij trailing " - benchmarki (1/2)", " - implikacje", " - co to znaczy"
        if " - " in label:
            topic_key = label.split(" - ", 1)[0].strip()
        else:
            topic_key = label.strip()
        parsed.append(
            {
                "msg_id": msg.get("id"),
                "content": content,
                "label": label,
                "key": topic_key,
                "idx": idx,
                "total": total,
                "ts": msg.get("timestamp"),
            }
        )

    # Fuzzy match keys - scal klucze z ratio >= 0.55
    unique_keys = []
    for p in parsed:
        matched = None
        for uk in unique_keys:
            ratio = SequenceMatcher(None, p["key"].lower(), uk.lower()).ratio()
            if ratio >= 0.55:
                matched = uk
                break
        if matched is None:
            unique_keys.append(p["key"])
        else:
            p["key"] = matched

    # Grupuj
    topics: dict[str, dict] = {}
    for p in parsed:
        if p["key"] not in topics:
            topics[p["key"]] = {
                "key": p["key"],
                "title": p["key"],
                "total_parts": p["total"] or 1,
                "parts": [],
                "msg_ids": [],
                "first_ts": p["ts"],
                "last_ts": p["ts"],
            }
        topics[p["key"]]["parts"].append(
            {"part": p["idx"], "content": p["content"], "msg_id": p["msg_id"], "ts": p["ts"]}
        )
        topics[p["key"]]["msg_ids"].append(p["msg_id"])
        topics[p["key"]]["last_ts"] = p["ts"]

    for t in topics.values():
        t["parts"].sort(key=lambda p: p["part"] or 0)
    return list(topics.values())


def main():
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    out_path = RAW_DIR / f"{today}.json"

    token = load_token()
    all_messages = []
    thread_summary = []
    for tid in THREAD_IDS:
        print(f"Fetching messages from thread {tid}...")
        msgs = fetch_messages(token, tid)
        print(f"  got {len(msgs)} messages")
        for m in msgs:
            m["_thread_id"] = tid
        all_messages.extend(msgs)
        thread_summary.append({"thread_id": tid, "count": len(msgs)})
    print(f"Total: {len(all_messages)} messages across {len(THREAD_IDS)} threads")

    topics = group_into_topics(all_messages)
    print(f"Grouped into {len(topics)} topics")

    out = {
        "date": today,
        "fetched_at": datetime.now(timezone.utc).isoformat(),
        "thread_ids": THREAD_IDS,
        "thread_summary": thread_summary,
        "topic_count": len(topics),
        "message_count": len(all_messages),
        "topics": topics,
    }
    out_path.write_text(json.dumps(out, indent=2, ensure_ascii=False))
    print(f"Saved to {out_path}")


if __name__ == "__main__":
    main()
