"""Generuje statyczne strony HTML z data/news.json.

Wyjście: index.html + news/<slug>.html
"""
import html
import json
import re
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).parent.parent
DATA_FILE = ROOT / "data" / "news.json"
NEWS_DIR = ROOT / "news"
NEWS_DIR.mkdir(parents=True, exist_ok=True)
INDEX_FILE = ROOT / "index.html"
RSS_FILE = ROOT / "rss.xml"


def render_markdown(text: str) -> str:
    """Prosty renderer: **bold**, [text](url), nowe linie."""
    # Najpierw escape HTML
    out = []
    for line in text.split("\n"):
        if not line.strip():
            out.append("")
            continue
        # Nagłówki **...**
        m = re.match(r"^\*\*([^*]+)\*\*$", line.strip())
        if m:
            out.append(f'<h3>{html.escape(m.group(1).strip())}</h3>')
            continue
        # Bullets
        if line.lstrip().startswith("- "):
            content = line.lstrip()[2:]
            content = inline_format(content)
            out.append(f"<li>{content}</li>")
            continue
        # Zwykła linia
        out.append(f"<p>{inline_format(line)}</p>")
    # Zgrupuj <li> w <ul>
    html_text = "\n".join(out)
    html_text = re.sub(r"(<li>.*?</li>\n?)+", lambda m: f"<ul>\n{m.group(0)}</ul>", html_text, flags=re.S)
    return html_text


def inline_format(text: str) -> str:
    """Formatowanie inline: **bold**, [text](url), zachowuje HTML escape."""
    # Escape najpierw
    text = html.escape(text, quote=False)
    # Bold
    text = re.sub(r"\*\*([^*]+)\*\*", r"<strong>\1</strong>", text)
    # Linki [text](url) - URL był już escaped, więc de-escape samego URL
    def link_replace(m):
        url = m.group(2).replace("&amp;", "&")
        return f'<a href="{url}" target="_blank" rel="noopener noreferrer">{m.group(1)}</a>'
    text = re.sub(r"\[([^\]]+)\]\((https?://[^\)]+)\)", link_replace, text)
    # Auto-linkowanie gołych URLs (które nie są w <a>)
    text = re.sub(
        r'(?<!["\'])(https?://[^\s<\)]+)(?!["\'])',
        lambda m: f'<a href="{m.group(1)}" target="_blank" rel="noopener noreferrer">{m.group(1)[:60]}{"..." if len(m.group(1)) > 60 else ""}</a>',
        text,
    )
    return text


def estimate_reading_time(text: str) -> int:
    return max(1, len(text) // 1200)  # ~1200 chars/min


def base_template(title: str, body: str, extra_head: str = "") -> str:
    return f"""<!DOCTYPE html>
<html lang="pl">
<head>
<meta charset="utf-8">
<base href="/stem-news-site/">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{html.escape(title)} — STEM News</title>
<meta name="description" content="STEM News — codzienny przegląd AI, security, hardware i open source.">
<link rel="icon" type="image/svg+xml" href="assets/img/favicon.svg">
<link rel="alternate" type="application/rss+xml" title="STEM News RSS" href="rss.xml">
<link rel="stylesheet" href="assets/css/style.css">
{extra_head}
</head>
<body>
<header class="topbar">
  <div class="container topbar-inner">
    <a href="/" class="logo"><span class="logo-bracket">[</span>stem<span class="logo-bracket">]</span></a>
    <nav class="nav">
      <a href="/?filter=all">Wszystkie</a>
      <a href="/?filter=ai">AI/ML</a>
      <a href="/?filter=security">Security</a>
      <a href="/?filter=hardware">Hardware</a>
      <a href="/?filter=opensource">Open source</a>
      <a href="/rss.xml">RSS</a>
    </nav>
    <button class="theme-toggle" id="themeToggle" aria-label="Przełącz motyw">◐</button>
  </div>
</header>
<main class="container">
{body}
</main>
<footer class="footer">
  <div class="container">
    <p>STEM News · auto-publikowane z wątku Discord 1512398228384120864 · GitHub Actions daily</p>
    <p class="muted">Rozszerzane przez <code>gpt-5.5-pro20x</code> (vsllm) · Vanilla HTML+CSS · GitHub Pages</p>
  </div>
</footer>
<script src="/assets/js/main.js"></script>
</body>
</html>"""


def render_index(news: list) -> str:
    body_parts = ['<section class="hero">']
    body_parts.append('<h1>STEM News</h1>')
    body_parts.append(f'<p class="lead">Codzienny przegląd AI, security, hardware i open source. '
                      f'{len(news)} tematów · auto-publikowane z Discord.</p>')
    body_parts.append('</section>')
    body_parts.append('<section class="news-list">')
    body_parts.append('<h2 class="section-title">Najnowsze</h2>')
    for i, entry in enumerate(news):
        slug = entry["slug"]
        title = entry["title"]
        date = entry.get("last_ts", "")[:10]
        tags = get_tags(entry.get("original_key", ""))
        # Weź pierwszy AKTUALNY akapit (nie nagłówek bold)
        paragraphs = [p.strip() for p in entry["expanded_content"].split("\n\n") if p.strip()]
        summary = ""
        for p in paragraphs:
            # Pomiń nagłówki bold (krótkie < 50 znaków i tylko **...**)
            if re.match(r"^\*\*[^*]{1,50}\*\*$", p):
                continue
            # Weź tekst bez ** **
            clean = re.sub(r"\*\*([^*]+)\*\*", r"\1", p)
            summary = clean[:240].strip()
            break
        read_time = estimate_reading_time(entry["expanded_content"])
        sources = entry.get("source_urls", [])
        body_parts.append(f"""<article class="news-item" data-index="{i}" data-tags="{",".join(tags)}">
  <div class="news-meta">
    <span class="news-date">{html.escape(date)}</span>
    <span class="news-source-count">{len(sources)} źródeł</span>
    <span class="news-read-time">{read_time} min</span>
  </div>
  <h3 class="news-title"><a href="/news/{slug}.html">{html.escape(title)}</a></h3>
  <p class="news-summary">{html.escape(summary)}{'…' if len(summary) == 240 else ''}</p>
  <div class="news-footer">
    <a href="/news/{slug}.html" class="read-more">Czytaj dalej →</a>
    <span class="news-parts">{entry.get('original_parts', 1)} part Discord</span>
  </div>
</article>""")
    body_parts.append('</section>')
    return base_template("STEM News — przegląd AI/security/hardware", "\n".join(body_parts))


def render_article(entry: dict) -> str:
    title = entry["title"]
    date = entry.get("last_ts", "")[:10]
    sources = entry.get("source_urls", [])
    # Wytnij sekcję **Źródła** z expanded_content (bo mamy dedykowany blok na końcu)
    expanded = entry["expanded_content"]
    sources_marker = re.search(r"\*\*[^*]*[Źź]r[oó]d[łl]a[^*]*\*\*", expanded)
    if sources_marker:
        expanded = expanded[: sources_marker.start()].rstrip()
    content_html = render_markdown(expanded)
    read_time = estimate_reading_time(expanded)

    sources_html = ""
    if sources:
        sources_html = '<div class="sources"><h3>Źródła</h3><ul>'
        for url in sources[:8]:
            display = url.replace("https://", "").replace("http://", "")[:60]
            sources_html += f'<li><a href="{html.escape(url)}" target="_blank" rel="noopener noreferrer">{html.escape(display)}</a></li>'
        sources_html += '</ul></div>'

    body = f"""<article class="article">
  <header class="article-header">
    <div class="article-meta">
      <span>{html.escape(date)}</span>
      <span>·</span>
      <span>{read_time} min czytania</span>
      <span>·</span>
      <span>{len(sources)} źródeł</span>
    </div>
    <h1>{html.escape(title)}</h1>
  </header>
  <div class="article-body">
{content_html}
{sources_html}
  </div>
  <footer class="article-footer">
    <a href="/" class="back-link">← Wszystkie newsy</a>
    <div class="discord-refs">
      <span>Discord msg IDs:</span>
      <code>{', '.join(entry.get('original_msg_ids', []))}</code>
    </div>
  </footer>
</article>"""
    return base_template(title, body)


def render_rss(news: list) -> str:
    items = []
    for entry in news[:30]:
        title = html.escape(entry["title"])
        link = f"https://stem-news.example/news/{entry['slug']}.html"
        pub = entry.get("last_ts", datetime.utcnow().isoformat())
        desc = re.sub(r"\*\*([^*]+)\*\*", "", entry["expanded_content"][:500])
        desc = html.escape(desc)
        items.append(f"""    <item>
      <title>{title}</title>
      <link>{link}</link>
      <guid>{link}</guid>
      <pubDate>{pub}</pubDate>
      <description>{desc}</description>
    </item>""")
    return f"""<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0">
  <channel>
    <title>STEM News</title>
    <link>https://stem-news.example/</link>
    <description>Codzienny przegląd AI, security, hardware i open source.</description>
    <language>pl</language>
{chr(10).join(items)}
  </channel>
</rss>"""


def clean_title(key: str, expanded: str = "") -> str:
    """Czyści original_key do ładnego tytułu. Jeśli key za krótki, próbuje z expanded_content."""
    if not key:
        return "Temat"
    clean = re.sub(r"\s*\(\d+/\d+\)\s*$", "", key).strip() or "Temat"
    # Hardcoded overrides dla krótkich topic keys
    OVERRIDES = {
        "mac m": "Mac M-series + llama.cpp — 70B LLM w 32GB RAM",
    }
    override = OVERRIDES.get(clean.lower())
    if override:
        return override
    # Jeśli key za krótki (< 20 znaków), szukaj dłuższego tytułu w expanded_content
    if len(clean) < 20 and expanded:
        # Szukaj wzorca: "W tym [artykule/przewodniku]..." lub "Przewodnik: ..."
        # Bierz całe zdanie do kropki
        m = re.search(r"((?:W tym (?:artykule|przewodniku)|Przewodnik(?: po)?|Jak (?:uruchomić|postawić|skonfigurować|zainstalować|odpalić)|Setup (?:kompletny|komplet)?)[:\s][^.]{10,150}\.)", expanded, re.I)
        if m:
            return m.group(1).strip()
        # Alternatywa: weź zdanie z "**Co się stało**" (pierwsze)
        m2 = re.search(r"\*\*Co się stało\*\*\s*\n+([^.]{20,250}\.)", expanded)
        if m2:
            return m2.group(1).strip()
    return clean


def _slugify_local(text: str) -> str:
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


def get_tags(topic_key: str) -> list[str]:
    """Mapowanie topic_key → list tagów (do client-side filtra)."""
    k = topic_key.lower()
    tags = []
    if any(w in k for w in ["claude", "gpt", "openai", "gemini", "mythos", "gpt-oss"]):
        tags.append("ai")
    if "security" in k or "cve" in k or "spring" in k:
        tags.append("security")
    if any(w in k for w in ["mi400", "helios", "amd", "gpu", "hardware"]):
        tags.append("hardware")
    if any(w in k for w in ["wwdc", "ios 27", "siri", "apple", "antigravity", "google i/o"]):
        tags.append("ai")
        if "wwdc" in k or "ios 27" in k or "siri" in k or "apple" in k:
            tags.append("hardware")
    if "gpt-oss" in k or "openai" in k:
        tags.append("opensource")
    return list(set(tags)) or ["ai"]


def main():
    if not DATA_FILE.exists():
        print(f"ERROR: {DATA_FILE} missing - run fetch + expand first")
        return
    news = json.loads(DATA_FILE.read_text())
    # Upewnij się że title/slug są z original_key (nie z "Co się stało")
    for entry in news:
        ok_title = clean_title(entry.get("original_key", ""), entry.get("expanded_content", ""))
        if entry.get("title", "").lower() in {"co się stało", "co sie stalo", ""} or \
           not entry.get("title"):
            entry["title"] = ok_title
        entry["slug"] = _slugify_local(ok_title)
        # Post-process: wyczyść cenzurę vsllm "[用户触发屏蔽词]" i podobne placeholdery
        if "expanded_content" in entry:
            entry["expanded_content"] = (
                entry["expanded_content"]
                .replace("[用户触发屏蔽词]", "")  # chiński placeholder od vsllm
                .replace("[censored]", "")
                .replace("[REDACTED]", "")
            )
    print(f"Loaded {len(news)} entries")

    # Index
    INDEX_FILE.write_text(render_index(news))
    print(f"Generated {INDEX_FILE}")

    # Articles
    seen_slugs = set()
    for entry in news:
        slug = entry["slug"]
        if slug in seen_slugs:
            print(f"  WARN: duplicate slug {slug}, appending suffix")
            slug = slug + "-" + entry.get("last_ts", "")[:10]
        seen_slugs.add(slug)
        article_path = NEWS_DIR / f"{slug}.html"
        article_path.write_text(render_article(entry))
    print(f"Generated {len(news)} articles in {NEWS_DIR}")

    # RSS
    RSS_FILE.write_text(render_rss(news))
    print(f"Generated {RSS_FILE}")


if __name__ == "__main__":
    main()
