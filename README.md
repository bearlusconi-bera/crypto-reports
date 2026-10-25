# 📈 Weekly Crypto Reports

A mobile-first static site that publishes Mattia's weekly crypto market
intelligence reports so they can be read from a phone. A new report is
published every **Saturday at 11:00 (Europe/Paris)** and covers the
**previous 7 days**.

**Live site:** https://bearlusconi-bera.github.io/crypto-reports/

> Reports up to 2026-10-21 are the earlier **daily** reports (24-hour window).
> From Saturday 2026-10-31 the report is **weekly**: 7-day window, a Top 10
> instead of a Top 5, and up to 10 items per section.

## How it works

- Reports are written by the `DailyCryptoReport` skill (now run weekly) into
  the personal knowledge vault:
  `~/Documents/personal-knowledge-vault/raw/reports/crypto/*.md`.
  The skill, not this repo, owns the 7-day window and the item counts.
- `publish.sh` copies those markdown files into [`reports/`](reports/),
  regenerates [`manifest.json`](manifest.json), and pushes to GitHub.
- GitHub Pages serves the static site. The front end (`index.html` + `app.js`)
  reads `manifest.json`, lists reports newest-first, and renders the selected
  markdown in the browser with [marked](https://marked.js.org/) +
  [DOMPurify](https://github.com/cure53/DOMPurify). No build step, no Jekyll
  (`.nojekyll`).
- Report files keep the `YYYY-MM-DD.md` name (the Saturday run date for weekly
  reports), so the manifest, routing (`#/<date>`) and history are unchanged.

## Files

| File | Purpose |
|------|---------|
| `index.html` | App shell + mobile viewport + CDN libs |
| `style.css` | Mobile-first dark reader theme |
| `app.js` | List + report rendering, hash routing (`#/<date>`), weekly freshness banner |
| `generate_manifest.py` | Builds `manifest.json` (title + preview per report) |
| `publish.sh` | Copy reports → regenerate manifest → commit-if-changed → push |
| `reports/*.md` | Published report markdown (mirror of the vault) |

## Publish manually

```bash
./publish.sh
```

It only commits/pushes when there is an actual change, so it is safe to run
repeatedly.

## Weekly automation

The report runs **once a week, on Saturday at 11:00 Europe/Paris**
(cron: `0 11 * * 6` with `TZ=Europe/Paris`). There is no daily run any more.
The `DailyCryptoReport` skill runs `publish.sh` as its final step, so every
report (manual or scheduled) is published automatically.

The site's freshness banner follows the weekly cadence: up to 7 days old is
on schedule, 8–10 days shows a warning, and more than 10 days flags a missed run.
