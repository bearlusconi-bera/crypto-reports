# 📈 Daily Crypto Reports

A mobile-first static site that publishes Mattia's daily crypto market
intelligence reports so they can be read from a phone. New reports are
pushed automatically every day.

**Live site:** https://bearlusconi-bera.github.io/crypto-reports/

## How it works

- Reports are written by the `DailyCryptoReport` skill into the personal
  knowledge vault: `~/Documents/personal-knowledge-vault/raw/reports/crypto/*.md`.
- `publish.sh` copies those markdown files into [`reports/`](reports/),
  regenerates [`manifest.json`](manifest.json), and pushes to GitHub.
- GitHub Pages serves the static site. The front end (`index.html` + `app.js`)
  reads `manifest.json`, lists reports newest-first, and renders the selected
  markdown in the browser with [marked](https://marked.js.org/) +
  [DOMPurify](https://github.com/cure53/DOMPurify). No build step, no Jekyll
  (`.nojekyll`).

## Files

| File | Purpose |
|------|---------|
| `index.html` | App shell + mobile viewport + CDN libs |
| `style.css` | Mobile-first dark reader theme |
| `app.js` | List + report rendering, hash routing (`#/<date>`) |
| `generate_manifest.py` | Builds `manifest.json` (title + preview per report) |
| `publish.sh` | Copy reports → regenerate manifest → commit-if-changed → push |
| `reports/*.md` | Published report markdown (mirror of the vault) |

## Publish manually

```bash
./publish.sh
```

It only commits/pushes when there is an actual change, so it is safe to run
repeatedly.

## Daily automation

The `DailyCryptoReport` skill runs `publish.sh` as its final step, so every
report (manual or scheduled at 10am) is published automatically.
