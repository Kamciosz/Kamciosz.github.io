# STEM News

Auto-publikowany blog z newsami ze wątku Discord 1512398228384120864 (STEM pipeline).
Rozszerzane przez `gpt-5.5-pro20x` (vsllm) do 1800-2600 znaków. Deploy: GitHub Pages.

## Struktura

```
stem-news-site/
├── .github/workflows/update-news.yml   # daily 08:00 UTC
├── scripts/
│   ├── fetch_discord.py                # pobiera wiadomości z wątku
│   ├── expand_news.py                  # LLM expansion
│   └── generate_pages.py               # generuje index + artykuły + RSS
├── data/
│   ├── news.json                       # aktywna lista tematów
│   ├── raw/                            # surowe z Discord (gitignored)
│   └── archive/                        # snapshoty dzienne (gitignored)
├── news/                               # artykuły HTML
├── index.html                          # homepage
├── rss.xml                             # RSS feed
├── assets/css/style.css
└── assets/js/main.js
```

## Setup

### 1. Repo

```bash
cd ~/Desktop/stem-news-site
git init
git add .
git commit -m "feat: initial site"
gh repo create Kamciosz.github.io --public --source=. --push  # WAŻNE: nazwa musi być <user>.github.io żeby strona poszła pod root
```

### 2. GitHub Secrets

W `Settings → Secrets and variables → Actions`:
- `DISCORD_USER_TOKEN` - token użytkownika Discord (file: `~/.hermes/discord_user_token.txt`)
- `VSLLM_API_KEY` - API key vsllm (env: `VSLLM_API_KEY`)

### 3. GitHub Pages

W `Settings → Pages`:
- Source: `Deploy from a branch`
- Branch: `main` / `(root)`

Site będzie na `https://kamciosz.github.io/` (repo nazwane `Kamciosz.github.io` = user GH Pages root)

### 4. Pierwszy manual run

W GitHub → Actions → Update STEM News → Run workflow.

## Lokalne uruchomienie

```bash
cd ~/Desktop/stem-news-site

export DISCORD_USER_TOKEN=$(cat ~/.hermes/discord_user_token.txt)
export VSLLM_API_KEY=*** python3 scripts/fetch_discord.py
python3 scripts/expand_news.py
python3 scripts/generate_pages.py

# Otwórz w przeglądarce
open index.html
```

## Konwencje

- **Discord source:** wiadomości z prefiksem `**[N/M]** Topic ... (X/Y)**` grupowane w tematy
- **Expansion:** każdy temat → 1 artykuł blogowy 1800-2600 znaków, 100% po polsku
- **Slug:** generowany z tytułu (transliteracja PL → ASCII, lowercase, hyphens)
- **Update schedule:** codziennie 08:00 UTC, po 07:00 STEM pipeline
- **Theme:** dark mode default (LocalStorage), follow system preference

## Modele

- **Frontend (strona):** Vanilla HTML + CSS + JS, zero build, działa na GitHub Pages bez niczego
- **Backend (LLM):** gpt-5.5-pro20x przez https://vsllm.com/v1/responses (kodowania + reasoning effort: low)
- **Discord:** REST API bez biblioteki (urllib stdlib)

## Roadmap

- [ ] Tagowanie tematów (ai/security/hardware/opensource) - automatyczne z LLM
- [ ] Wyszukiwarka client-side (Fuse.js)
- [ ] Newsletter email digest
- [ ] Komentarze przez Giscus
- [ ] i18n (EN/PL toggle)
