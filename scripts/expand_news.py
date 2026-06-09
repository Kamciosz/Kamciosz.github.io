"""Ekspansja tematów z data/raw/*.json przez gpt-5.5-pro20x (vsllm).

Wyjście: data/news.json (aktywna lista) + data/archive/<date>.json (snapshot).
"""
import json
import os
import re
import ssl
import sys
import time
import urllib.request
import urllib.error
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).parent.parent
RAW_DIR = ROOT / "data" / "raw"
ARCHIVE_DIR = ROOT / "data" / "archive"
DATA_FILE = ROOT / "data" / "news.json"
ARCHIVE_DIR.mkdir(parents=True, exist_ok=True)

VSLLM_BASE = "https://vsllm.com/v1"
VSLLM_MODEL = "gpt-5.5-pro20x"

# SSL context (Python na macOS często ma problem z certyfikatami)
_SSL_CTX = ssl.create_default_context()
_SSL_CTX.check_hostname = False
_SSL_CTX.verify_mode = ssl.CERT_NONE

EXPANSION_PROMPT = """Jesteś redaktorem serwisu STEM news. Dostajesz artykuł newsowy
wysłany na Discorda (po polsku, z **[N/M]** prefix). Twoim zadaniem: rozwinąć go do
pełnego artykułu blogowego.

Zasady:
- Output **TYLKO po polsku**
- Output 5000-7500 znaków (artykuł blog-style, skondensowany i rozwinięty)
- Zachowaj WSZYSTKIE twarde liczby, daty, nazwy, URLs
- Struktura (użyj nagłówków **bold**):
  1. **Co się stało** (2-3 zdania, sedno)
  2. **Kontekst** (background, dlaczego to ważne teraz, co było wcześniej - 2-3 akapity)
  3. **Kluczowe liczby** (bullet list 5-8 punktów z konkretnymi metrykami)
  4. **Dlaczego to ważne** (implikacje - dla kogo, jak zmienia rynek/produkt/ryzyko, 2-3 akapity)
  5. **Praktyczne rekomendacje** (jak to zastosować, na co uważać, 2-3 akapity - TYLKO dla blog-style)
  6. **Źródła** (lista URLs, taka sama jak w input)
- NIE dodawaj informacji spoza inputu - tylko rozwijaj to co jest
- NIE zgaduj, NIE wymyślaj - jeśli czegoś nie ma w input, pomiń
- NIE zaczynaj od "Cześć", "Witaj" itp - zaczynaj bezpośrednio od treści
- NIE używaj emoji
- Pisz w stylu technicznym, peer-to-peer, bez hype'u

Input do rozwinięcia:
---
{input}
---

Output (TYLKO artykuł, bez metakomentarzy):"""


def call_llm(input_text: str, max_retries: int = 3) -> str:
    api_key = os.environ.get("VSLLM_API_KEY")
    if not api_key:
        sys.exit("VSLLM_API_KEY env var required")
    url = f"{VSLLM_BASE}/responses"
    payload = {
        "model": VSLLM_MODEL,
        "input": EXPANSION_PROMPT.format(input=input_text),
        "max_output_tokens": 4000,
        "reasoning": {"effort": "low"},
    }
    data = json.dumps(payload).encode()
    for attempt in range(max_retries):
        try:
            req = urllib.request.Request(
                url,
                data=data,
                headers={
                    "Authorization": f"Bearer {api_key}",
                    "Content-Type": "application/json",
                },
            )
            with urllib.request.urlopen(req, timeout=180, context=_SSL_CTX) as resp:
                result = json.loads(resp.read())
            # Extract text from responses API
            for item in result.get("output", []):
                if item.get("type") == "message":
                    for content in item.get("content", []):
                        if content.get("type") == "output_text":
                            return content["text"].strip()
            return ""
        except (urllib.error.URLError, urllib.error.HTTPError) as e:
            print(f"  attempt {attempt+1} failed: {e}", file=sys.stderr)
            if attempt < max_retries - 1:
                time.sleep(5 * (attempt + 1))
    return ""


def slugify(text: str) -> str:
    """Tworzy URL-safe slug z tytułu (lowercase, ascii, hyphens)."""
    # Prosty transliteration PL → ASCII
    pl_map = {
        "ą": "a", "ć": "c", "ę": "e", "ł": "l", "ń": "n",
        "ó": "o", "ś": "s", "ź": "z", "ż": "z",
        "Ą": "A", "Ć": "C", "Ę": "E", "Ł": "L", "Ń": "N",
        "Ó": "O", "Ś": "S", "Ź": "Z", "Ż": "Z",
    }
    for pl, ascii_ in pl_map.items():
        text = text.replace(pl, ascii_)
    text = text.lower()
    text = re.sub(r"[^a-z0-9]+", "-", text)
    return text.strip("-")[:80]


def extract_urls(text: str) -> list[str]:
    return re.findall(r"https?://\S+", text)


def extract_title(topic_key: str, content: str) -> str:
    """Wyciąga tytuł: preferuje topic_key (z Discorda), fallback do pierwszego bold."""
    # 1) Pierwszy wybór: topic_key z Discorda
    if topic_key and topic_key.strip():
        # Wyczyść trailing (1/2) itp
        clean = re.sub(r"\s*\(\d+/\d+\)\s*$", "", topic_key).strip()
        return clean
    # 2) Fallback: pierwszy bold w content
    m = re.search(r"\*\*([^*]+)\*\*", content)
    if m:
        title = m.group(1).strip()
        # Ignoruj generyczne nagłówki szablonu
        if title.lower() not in {"co się stało", "co sie stalo", "kontekst",
                                  "kluczowe liczby", "dlaczego to ważne",
                                  "dlaczego to wazne", "źródła", "zrodla"}:
            return title
    # 3) Ostateczny fallback
    return topic_key or "Temat"


def expand_topic(topic: dict) -> dict:
    """Łączy parts i wysyła do LLM."""
    combined = "\n\n---\n\n".join(p["content"] for p in topic["parts"])
    print(f"Expanding: {topic['key'][:60]} ({len(combined)} chars input)")
    expanded = call_llm(combined)
    if not expanded:
        print(f"  WARN: empty expansion for {topic['key']}", file=sys.stderr)
        return None
    return {
        "title": extract_title(topic["key"], expanded),
        "slug": slugify(extract_title(topic["key"], expanded)),
        "original_key": topic["key"],
        "original_parts": len(topic["parts"]),
        "original_msg_ids": topic["msg_ids"],
        "first_ts": topic["first_ts"],
        "last_ts": topic["last_ts"],
        "source_urls": list(set(extract_urls(combined))),
        "expanded_content": expanded,
        "expanded_chars": len(expanded),
        "input_chars": len(combined),
    }


def main():
    raw_files = sorted(RAW_DIR.glob("*.json"))
    if not raw_files:
        sys.exit(f"No raw files in {RAW_DIR}")

    # Bierz najnowszy raw
    latest_raw = raw_files[-1]
    print(f"Reading {latest_raw.name}")
    raw = json.loads(latest_raw.read_text())
    today = raw["date"]

    # Załaduj istniejący news.json (jeśli istnieje) żeby nie duplikować
    existing = []
    if DATA_FILE.exists():
        existing = json.loads(DATA_FILE.read_text())
    existing_keys = {e.get("original_key") for e in existing}

    # Ekspansja nowych tematów
    new_expanded = []
    for topic in raw["topics"]:
        if topic["key"] in existing_keys:
            print(f"  skip (already expanded): {topic['key'][:50]}")
            continue
        result = expand_topic(topic)
        if result:
            new_expanded.append(result)
            # Inkrementalny zapis po każdym temacie (żeby nie stracić postępu)
            all_news = new_expanded + existing
            DATA_FILE.write_text(json.dumps(all_news, indent=2, ensure_ascii=False))
            print(f"  [saved] {len(all_news)} total ({len(new_expanded)} new)")
        time.sleep(2)  # rate limit buffer

    # Final write
    all_news = new_expanded + existing
    DATA_FILE.write_text(json.dumps(all_news, indent=2, ensure_ascii=False))
    print(f"Updated {DATA_FILE} with {len(all_news)} total entries ({len(new_expanded)} new)")

    # Zapisz snapshot archiwum
    archive_path = ARCHIVE_DIR / f"{today}.json"
    archive_data = {
        "date": today,
        "snapshot_at": datetime.now(timezone.utc).isoformat(),
        "topic_count": len(all_news),
        "topics": all_news,
    }
    archive_path.write_text(json.dumps(archive_data, indent=2, ensure_ascii=False))
    print(f"Saved archive: {archive_path}")


if __name__ == "__main__":
    main()
