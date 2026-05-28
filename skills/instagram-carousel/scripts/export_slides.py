#!/usr/bin/env python3
"""Export an Instagram carousel HTML file to 1080x1350 PNG slides.

Run it, don't read it. Example:
    python scripts/export_slides.py --input carousel.html --output slides --slides 7

Why this works:
- The carousel is laid out at 420px wide (4:5 -> 525px tall). We render at that width and
  use Playwright's device_scale_factor (1080/420 ~= 2.5714) to scale UP to 1080px output
  WITHOUT reflowing the layout. Never set the viewport to 1080px wide.
- `clip` captures only the slide viewport, excluding the Instagram frame chrome.
- A 3s wait lets Google Fonts load; disabling the track transition snaps slides instantly.

Requires: Python + Playwright (Chromium). Install once with:
    pip install playwright && python -m playwright install chromium
"""
import argparse
import asyncio
from pathlib import Path

from playwright.async_api import async_playwright

VIEW_W = 420
VIEW_H = 525
SCALE = 1080 / 420  # ~2.5714 -> 1080x1350 output


async def export_slides(input_html: Path, output_dir: Path, total_slides: int) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page(
            viewport={"width": VIEW_W, "height": VIEW_H},
            device_scale_factor=SCALE,
        )
        html_content = input_html.read_text(encoding="utf-8")
        await page.set_content(html_content, wait_until="networkidle")
        await page.wait_for_timeout(3000)  # wait for fonts to load

        # Hide the Instagram frame chrome, show only the slide viewport
        await page.evaluate("""() => {
          document.querySelectorAll('.ig-header,.ig-dots,.ig-actions,.ig-caption')
            .forEach(el => el.style.display='none');
          const frame = document.querySelector('.ig-frame');
          frame.style.cssText = 'width:420px;height:525px;max-width:none;border-radius:0;box-shadow:none;overflow:hidden;margin:0;';
          const viewport = document.querySelector('.carousel-viewport');
          viewport.style.cssText = 'width:420px;height:525px;aspect-ratio:unset;overflow:hidden;cursor:default;';
          document.body.style.cssText = 'padding:0;margin:0;display:block;overflow:hidden;';
        }""")
        await page.wait_for_timeout(500)

        for i in range(total_slides):
            await page.evaluate("""(idx) => {
              const track = document.querySelector('.carousel-track');
              track.style.transition = 'none';
              track.style.transform = 'translateX(' + (-idx * 420) + 'px)';
            }""", i)
            await page.wait_for_timeout(400)
            await page.screenshot(
                path=str(output_dir / f"slide_{i + 1}.png"),
                clip={"x": 0, "y": 0, "width": VIEW_W, "height": VIEW_H},
            )
            print(f"Exported slide {i + 1}/{total_slides}")

        await browser.close()


def main() -> None:
    parser = argparse.ArgumentParser(description="Export carousel HTML to 1080x1350 PNGs.")
    parser.add_argument("--input", required=True, type=Path, help="Path to the carousel HTML file.")
    parser.add_argument("--output", default=Path("slides"), type=Path, help="Output directory for PNGs.")
    parser.add_argument("--slides", required=True, type=int, help="Total number of slides in the carousel.")
    args = parser.parse_args()
    asyncio.run(export_slides(args.input, args.output, args.slides))


if __name__ == "__main__":
    main()
