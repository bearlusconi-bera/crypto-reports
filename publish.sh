#!/usr/bin/env bash
# Publish daily crypto reports to the GitHub Pages site.
#
# Idempotent: copies *.md from the vault into ./reports, regenerates
# manifest.json, and commits + pushes ONLY when something changed.
# Safe to run manually or from the daily scheduled task.
set -euo pipefail

REPO_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SRC="${CRYPTO_REPORTS_SRC:-$HOME/Documents/personal-knowledge-vault/raw/reports/crypto}"
BRANCH="${CRYPTO_REPORTS_BRANCH:-main}"

cd "$REPO_DIR"

if [ ! -d "$SRC" ]; then
  echo "ERROR: source reports dir not found: $SRC" >&2
  exit 1
fi

mkdir -p reports

# Copy only markdown reports (source is markdown-only; never touches the vault).
copied=0
shopt -s nullglob
for f in "$SRC"/*.md; do
  cp -f "$f" reports/
  copied=$((copied + 1))
done
shopt -u nullglob
echo "Copied $copied markdown report(s) from: $SRC"

# Regenerate the manifest the site reads.
python3 generate_manifest.py

# Commit + push only if there is a change.
git add -A
if git diff --cached --quiet; then
  echo "No changes to publish."
  exit 0
fi

git commit -m "Publish reports $(date +%Y-%m-%d)"
git push origin "$BRANCH"
echo "Published to origin/$BRANCH."
