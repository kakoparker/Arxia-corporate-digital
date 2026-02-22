"""
Generate PDF of Arxia Corporate Deck.
Uses Playwright locally for both measurement and rendering — same engine,
so content height is pixel-perfect with no blank trailing space.
"""

import asyncio
import base64
import re
import sys
from pathlib import Path
from playwright.async_api import async_playwright

BASE = Path(__file__).parent
HTML_FILE = BASE / "arxia-corporate-deck.html"
PDF_FILE = BASE / "arxia-corporate-deck.pdf"

PAGE_WIDTH_MM = 297  # A4 landscape width

MIME_TYPES = {
    ".png": "image/png",
    ".jpg": "image/jpeg",
    ".jpeg": "image/jpeg",
    ".gif": "image/gif",
    ".svg": "image/svg+xml",
    ".webp": "image/webp",
}


def embed_local_images(html: str) -> str:
    def replace_src(match):
        prefix = match.group(1)
        src = match.group(2)
        if src.startswith(("http://", "https://", "data:")):
            return match.group(0)
        filepath = BASE / src
        if not filepath.exists():
            print(f"  WARN: Missing file: {src}")
            return match.group(0)
        ext = filepath.suffix.lower()
        mime = MIME_TYPES.get(ext, "application/octet-stream")
        data = base64.b64encode(filepath.read_bytes()).decode("ascii")
        print(f"  Embedded: {src} ({filepath.stat().st_size:,} bytes)")
        return f'{prefix}data:{mime};base64,{data}"'
    return re.sub(r'(src\s*=\s*")([^"]+)"', replace_src, html)


PDF_CSS = """
<style id="pdf-overrides">
  body {
    -webkit-print-color-adjust: exact !important;
    print-color-adjust: exact !important;
    color-adjust: exact !important;
  }
  *, *::before, *::after {
    animation-duration: 0s !important;
    animation-delay: 0s !important;
    transition-duration: 0s !important;
    transition-delay: 0s !important;
  }
  .animate-on-scroll {
    opacity: 1 !important;
    transform: none !important;
  }
  .nav { display: none !important; }
  .section, .section-short {
    min-height: 0 !important;
    height: auto !important;
  }
  #cover .cover-content { opacity: 1 !important; }
  #cover .accent-line { width: 48px !important; }
  #cover .cover-bottom {
    opacity: 1 !important;
    position: relative !important;
    bottom: auto !important;
    left: auto !important;
    right: auto !important;
    margin-top: 48px;
    width: 100%;
  }
  .map-ring {
    opacity: 0.4 !important;
    transform: scale(1.5) !important;
  }
</style>
"""


async def generate_pdf():
    print(f"Source: {HTML_FILE}")
    print(f"Output: {PDF_FILE}")

    print("\n1. Reading HTML...")
    html = HTML_FILE.read_text(encoding="utf-8")

    print("\n2. Embedding local images as base64...")
    html = embed_local_images(html)

    print("\n3. Injecting PDF styles...")
    html = html.replace("</head>", PDF_CSS + "\n</head>")

    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page(viewport={"width": 1123, "height": 800})

        print("\n4. Loading HTML in headless browser...")
        await page.set_content(html, wait_until="networkidle")
        await page.wait_for_timeout(3000)

        await page.evaluate("""() => {
            document.querySelectorAll('.animate-on-scroll').forEach(el => {
                el.classList.add('visible');
                el.style.opacity = '1';
                el.style.transform = 'none';
            });
            if (typeof lucide !== 'undefined') lucide.createIcons();
        }""")
        await page.wait_for_timeout(500)

        print("\n5. Measuring content height...")
        content_height = await page.evaluate("() => document.body.scrollHeight")
        height_mm = content_height * 25.4 / 96
        print(f"   {content_height}px = {height_mm:.0f}mm")

        print(f"\n6. Generating PDF ({PAGE_WIDTH_MM}mm x {height_mm:.0f}mm)...")
        await page.pdf(
            path=str(PDF_FILE),
            width=f"{PAGE_WIDTH_MM}mm",
            height=f"{height_mm:.0f}mm",
            print_background=True,
            margin={"top": "0", "right": "0", "bottom": "0", "left": "0"},
        )

        await browser.close()

    size_mb = PDF_FILE.stat().st_size / (1024 * 1024)
    print(f"\n   Saved: {PDF_FILE}")
    print(f"   Size:  {size_mb:.1f} MB")
    print("\nDone!")


if __name__ == "__main__":
    asyncio.run(generate_pdf())
