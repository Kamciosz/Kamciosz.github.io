#!/bin/bash
# Daily STEM News update - runs at 10:00 local time (= 08:00 UTC)
# 1) fetch from Discord
# 2) expand with LLM
# 3) generate static pages
# 4) commit and push to GitHub

set -e
export HOME=~  # dla ~ w ścieżkach
SITE_DIR=/Users/szymonsosnowski/Desktop/stem-news-site
ENV_FILE=/Users/szymonsosnowski/.hermes/.env
TOKEN_FILE=~/.hermes/discord_user_token.txt
LOG_DIR=${SITE_DIR}/logs
mkdir -p ${LOG_DIR}

cd ${SITE_DIR}
echo "[$(date -u +%Y-%m-%dT%H:%M:%SZ)] Daily update started" >> ${LOG_DIR}/daily-update.log

# Source VSLLM env
set -a
source ${ENV_FILE}
set +a

# Load Discord token from file if not in env
if [ -z "${DISCORD_USER_TOKEN}" ] && [ -f ${TOKEN_FILE} ]; then
    { read -r DISCORD_USER_TOKEN; export DISCORD_USER_TOKEN="${DISCORD_USER_TOKEN}"; } < ${TOKEN_FILE}
fi

# 1) Fetch
echo "[$(date -u +%H:%M:%S)] Step 1: fetch" >> ${LOG_DIR}/daily-update.log
python3 scripts/fetch_discord.py >> ${LOG_DIR}/daily-update.log 2>&1

# 2) Expand
echo "[$(date -u +%H:%M:%S)] Step 2: expand" >> ${LOG_DIR}/daily-update.log
python3 scripts/expand_news.py >> ${LOG_DIR}/daily-update.log 2>&1

# 3) Generate
echo "[$(date -u +%H:%M:%S)] Step 3: generate" >> ${LOG_DIR}/daily-update.log
rm -f news/*.html
python3 scripts/generate_pages.py >> ${LOG_DIR}/daily-update.log 2>&1

# 4) Commit + push
echo "[$(date -u +%H:%M:%S)] Step 4: commit" >> ${LOG_DIR}/daily-update.log
git add data/ news/ index.html rss.xml 2>> ${LOG_DIR}/daily-update.log

if git diff --cached --quiet; then
    echo "  No changes to commit" >> ${LOG_DIR}/daily-update.log
else
    git config user.name "Kamciosz" 2>> ${LOG_DIR}/daily-update.log
    git config user.email "kamciosz@users.noreply.github.com" 2>> ${LOG_DIR}/daily-update.log
    git commit -m "chore: daily update $(date -u +%Y-%m-%d)" >> ${LOG_DIR}/daily-update.log 2>&1
    git push >> ${LOG_DIR}/daily-update.log 2>&1
    echo "  Pushed" >> ${LOG_DIR}/daily-update.log
fi

echo "[$(date -u +%T)] Done" >> ${LOG_DIR}/daily-update.log
