#!/usr/bin/env python3
"""Generate manifest.json for the Daily Crypto Reports site.

Scans ./reports/*.md and produces a manifest the SPA reads:
  - daily reports (filenames like 2026-06-05.md) sorted by date, newest first
  - everything else (e.g. 2026-45-DAY-SUMMARY.md) listed afterwards as "other"

For each report it extracts a title (first "# " heading) and a short preview.
No third-party dependencies — standard library only.
"""

import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPORTS_DIR = os.path.join(HERE, "reports")
OUT_PATH = os.path.join(HERE, "manifest.json")

DATE_RE = re.compile(r"^(\d{4}-\d{2}-\d{2})\.md$")
H1_RE = re.compile(r"^#\s+(.+?)\s*$")
BOLD_ITEM_RE = re.compile(r"\*\*(.+?)\*\*")


def clean(text: str) -> str:
    """Strip markdown emphasis/links to plain text for previews."""
    text = re.sub(r"\[([^\]]+)\]\([^)]*\)", r"\1", text)  # links -> label
    text = text.replace("**", "").replace("*", "").replace("`", "")
    text = re.sub(r"\s+", " ", text).strip()
    return text


def extract_title_and_preview(path: str, fallback: str):
    title = fallback
    preview = ""
    try:
        with open(path, "r", encoding="utf-8") as fh:
            lines = fh.read().splitlines()
    except OSError:
        return title, preview

    got_title = False
    for line in lines:
        s = line.strip()
        if not got_title:
            m = H1_RE.match(s)
            if m:
                title = clean(m.group(1))
                got_title = True
            continue
        # After the title, find the first meaningful line for the preview.
        if not s or s.startswith("**Generated") or s.startswith("---") \
                or s.startswith("**Sources") or s.startswith(">"):
            continue
        if s.startswith("#"):
            continue
        bold = BOLD_ITEM_RE.search(s)
        preview = clean(bold.group(1)) if bold else clean(s)
        if preview:
            break

    if len(preview) > 160:
        preview = preview[:157].rstrip() + "…"
    return title, preview


def build():
    if not os.path.isdir(REPORTS_DIR):
        os.makedirs(REPORTS_DIR, exist_ok=True)

    daily, other = [], []
    for name in os.listdir(REPORTS_DIR):
        if not name.endswith(".md"):
            continue
        path = os.path.join(REPORTS_DIR, name)
        m = DATE_RE.match(name)
        if m:
            date = m.group(1)
            title, preview = extract_title_and_preview(path, date)
            daily.append({
                "id": date, "date": date, "file": name,
                "title": title, "preview": preview, "type": "daily",
            })
        else:
            stem = name[:-3]
            title, preview = extract_title_and_preview(path, stem)
            other.append({
                "id": stem, "date": "", "file": name,
                "title": title, "preview": preview, "type": "other",
            })

    daily.sort(key=lambda r: r["date"], reverse=True)
    other.sort(key=lambda r: r["file"], reverse=True)

    # "latest" is content-derived (newest report date), NOT wall-clock time,
    # so re-running with no new reports produces an identical manifest and
    # publish.sh can truly no-op.
    manifest = {
        "latest": daily[0]["date"] if daily else "",
        "count": len(daily) + len(other),
        "reports": daily + other,
    }

    with open(OUT_PATH, "w", encoding="utf-8") as fh:
        json.dump(manifest, fh, ensure_ascii=False, indent=2)
        fh.write("\n")

    print(f"manifest.json: {len(daily)} daily + {len(other)} other = "
          f"{manifest['count']} reports")
    return manifest["count"]


if __name__ == "__main__":
    try:
        n = build()
    except Exception as exc:  # noqa: BLE001
        print(f"ERROR generating manifest: {exc}", file=sys.stderr)
        sys.exit(1)
    sys.exit(0 if n >= 0 else 1)
