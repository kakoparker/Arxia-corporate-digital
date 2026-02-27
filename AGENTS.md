# AGENTS.md

## Cursor Cloud specific instructions

### Project overview
This is a static corporate deck website for **Arxia** ("Technology for Sovereign Nations"). The codebase consists of:
- `arxia-corporate-deck.html` — Self-contained single-file HTML presentation (all CSS/JS/images inline)
- `generate-pdf.py` — Python script that generates a PDF of the deck using Playwright (headless Chromium)
- `_redirects` — Netlify deployment config (`/` → `/arxia-corporate-deck.html`)
- `assets/` — Source image assets

### Running the site locally
Serve with any static file server, e.g.:
```
python3 -m http.server 8080
```
Then open `http://localhost:8080/arxia-corporate-deck.html`. The site requires internet access for CDN resources (Lucide icons from `unpkg.com`, Google Fonts).

### PDF generation
```
python3 generate-pdf.py
```
Requires `playwright` Python package and Chromium browser installed via `playwright install chromium --with-deps`.

### Notes
- There is no build system, linter, or test suite — this is a static HTML project.
- The HTML file is ~2MB due to embedded base64 images.
- The site supports three languages (EN/FR/ES) via a built-in i18n toggle in the navigation bar.
- No `package.json`, `requirements.txt`, or other dependency manifests exist in the repo.
