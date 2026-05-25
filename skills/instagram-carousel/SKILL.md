---
name: instagram-carousel
description: Generates a self-contained, swipeable HTML Instagram carousel with export-ready 1080x1350px slides, deriving brand colors, typography, and slide layout.
version: 1.0.0
author: Arijit Saha
email: arijit.saha@zysk.tech
category: comms
tags:
  - instagram
  - carousel
  - social-media
  - marketing
  - design
product: zysk
sprint: 1
tested_with: claude-sonnet-4-6
disable-model-invocation: false
allowed-tools: "*"
---

# Instagram Carousel Generator

> Builds a swipeable HTML carousel whose every slide exports as an Instagram-ready 1080x1350px image.

## When to use

- Activate when: the user runs `/instagram-carousel`.
- Activate when: the user says "create carousel", "make instagram carousel", or "generate carousel".
- Do NOT activate when: the user wants a single static image or a non-Instagram layout - this skill is specific to multi-slide IG carousels.

## Steps

You are an Instagram carousel design system. When a user asks you to create a carousel, generate a fully self-contained, swipeable HTML carousel where **every slide is designed to be exported as an individual image** for Instagram posting.

### Step 1: Collect brand details

Before generating any carousel, ask the user for the following (if not already provided):

1. **Brand name** - displayed on the first and last slides
2. **Instagram handle** - shown in the IG frame header and caption
3. **Primary brand color** - the main accent color (hex code, or describe it and you'll pick one)
4. **Logo** - ask if they have an SVG path, want to use their brand initial, or skip the logo
5. **Font preference** - serif headings + sans body (editorial), all sans-serif (modern/clean), or specific Google Fonts
6. **Tone** - professional, casual, playful, bold, minimal, etc.
7. **Images** - any images to include (profile photo, screenshots, product images, etc.)

If the user provides a website URL or brand assets, derive the colors and style from those. If the user just says "make me a carousel about X" without brand details, ask before generating. Don't assume defaults.

### Step 2: Derive the full color system

From the user's **single primary brand color**, generate the full 6-token palette:

```
BRAND_PRIMARY = {user's color}        // Main accent — progress bar, icons, tags
BRAND_LIGHT  = {primary lightened ~20%}  // Secondary accent — tags on dark, pills
BRAND_DARK   = {primary darkened ~30%}   // CTA text, gradient anchor
LIGHT_BG     = {warm or cool off-white}  // Light slide background (never pure #fff)
LIGHT_BORDER = {slightly darker than LIGHT_BG}  // Dividers on light slides
DARK_BG      = {near-black with brand tint}     // Dark slide background
```

**Rules for deriving colors:**
- LIGHT_BG should be a tinted off-white that complements the primary (warm primary → warm cream, cool primary → cool gray-white)
- DARK_BG should be near-black with a subtle tint matching the brand temperature (warm → #1A1918, cool → #0F172A)
- LIGHT_BORDER is always ~1 shade darker than LIGHT_BG
- The brand gradient used on gradient slides is: `linear-gradient(165deg, BRAND_DARK 0%, BRAND_PRIMARY 50%, BRAND_LIGHT 100%)`

### Step 3: Set up typography

Based on the user's font preference, pick a **heading font** and **body font** from Google Fonts.

**Suggested pairings:**

| Style | Heading Font | Body Font |
|-------|-------------|-----------|
| Editorial / premium | Playfair Display | DM Sans |
| Modern / clean | Plus Jakarta Sans (700) | Plus Jakarta Sans (400) |
| Warm / approachable | Lora | Nunito Sans |
| Technical / sharp | Space Grotesk | Space Grotesk |
| Bold / expressive | Fraunces | Outfit |
| Classic / trustworthy | Libre Baskerville | Work Sans |
| Rounded / friendly | Bricolage Grotesque | Bricolage Grotesque |

**Font size scale (fixed across all brands):**
- Headings: 28–34px, weight 600, letter-spacing -0.3 to -0.5px, line-height 1.1–1.15
- Body: 14px, weight 400, line-height 1.5–1.55
- Tags/labels: 10px, weight 600, letter-spacing 2px, uppercase
- Step numbers: heading font, 26px, weight 300
- Small text: 11–12px

Apply via CSS classes `.serif` (heading font) and `.sans` (body font) throughout all slides.

### Step 4: Build the slide architecture

**Format:** Aspect ratio **4:5** (Instagram carousel standard). Each slide is self-contained - all UI elements baked into the image. Alternate LIGHT_BG and DARK_BG backgrounds for visual rhythm.

**Required elements embedded in every slide:**

#### Progress bar (bottom of every slide)

- Position: absolute bottom, full width, 28px horizontal padding, 20px bottom padding
- Track: 3px height, rounded corners
- Fill width: `((slideIndex + 1) / totalSlides) * 100%`
- Light slides: `rgba(0,0,0,0.08)` track, BRAND_PRIMARY fill, `rgba(0,0,0,0.3)` counter
- Dark slides: `rgba(255,255,255,0.12)` track, `#fff` fill, `rgba(255,255,255,0.4)` counter
- Counter label beside the bar: "1/7" format, 11px, weight 500

```javascript
function progressBar(index, total, isLightSlide) {
  const pct = ((index + 1) / total) * 100;
  const trackColor = isLightSlide ? 'rgba(0,0,0,0.08)' : 'rgba(255,255,255,0.12)';
  const fillColor = isLightSlide ? BRAND_PRIMARY : '#fff';
  const labelColor = isLightSlide ? 'rgba(0,0,0,0.3)' : 'rgba(255,255,255,0.4)';
  return `
    <div style="position:absolute;bottom:0;left:0;right:0;padding:16px 28px 20px;z-index:10;display:flex;align-items:center;gap:10px;">
      <div style="flex:1;height:3px;background:${trackColor};border-radius:2px;overflow:hidden;">
        <div style="height:100%;width:${pct}%;background:${fillColor};border-radius:2px;"></div>
      </div>
      <span style="font-size:11px;color:${labelColor};font-weight:500;">${index + 1}/${total}</span>
    </div>
  `;
}
```

#### Swipe arrow (right edge — every slide EXCEPT the last)

A subtle chevron on the right edge telling the user to keep swiping. On the **last slide it is removed** so the user knows they've reached the end.

- Position: absolute right, full height, 48px wide
- Background: gradient fade from transparent → subtle tint
- Chevron: 24×24 SVG, rounded strokes
- Light slides: `rgba(0,0,0,0.06)` bg, `rgba(0,0,0,0.25)` stroke
- Dark slides: `rgba(255,255,255,0.08)` bg, `rgba(255,255,255,0.35)` stroke

```javascript
function swipeArrow(isLightSlide) {
  const bg = isLightSlide ? 'rgba(0,0,0,0.06)' : 'rgba(255,255,255,0.08)';
  const stroke = isLightSlide ? 'rgba(0,0,0,0.25)' : 'rgba(255,255,255,0.35)';
  return `
    <div style="position:absolute;right:0;top:0;bottom:0;width:48px;z-index:9;display:flex;align-items:center;justify-content:center;background:linear-gradient(to right,transparent,${bg});">
      <svg width="24" height="24" viewBox="0 0 24 24" fill="none">
        <path d="M9 6l6 6-6 6" stroke="${stroke}" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"/>
      </svg>
    </div>
  `;
}
```

**Layout rules:** Content padding `0 36px` standard; bottom-aligned slides with progress bar `0 36px 52px` to clear the bar. Hero/CTA slides `justify-content: center`; content-heavy slides `justify-content: flex-end`.

**Tag / category label** - small uppercase label above the heading:

```
<span style="display:inline-block;padding:4px 10px;background:${BRAND_PRIMARY}20;color:${isLightSlide ? BRAND_PRIMARY : BRAND_LIGHT};font-size:10px;font-weight:600;letter-spacing:2px;text-transform:uppercase;border-radius:4px;">
  {TAG TEXT}
</span>
```
Light slides: color = BRAND_PRIMARY. Dark slides: color = BRAND_LIGHT. Brand gradient slides: color = `rgba(255,255,255,0.6)`.

**Logo lockup (first and last slides):** brand icon + brand name. Logo icon → 40px circle (BRAND_PRIMARY bg) with icon centered, name beside it. Initials → 40px circle with first letter in white. Brand name: 13px, weight 600, letter-spacing 0.5px.

**Watermark (optional):** if a logo icon is provided, use it as a subtle background watermark on key slides (hero, CTA, brand gradient) at opacity 0.04–0.06. Skip if no logo.

### Step 5: Follow the standard slide sequence

Follow this narrative arc. The number of slides can flex (5–10), but 7 is ideal.

| # | Type | Background | Purpose |
|---|------|------------|---------|
| 1 | Hero | LIGHT_BG | Hook — bold statement, logo lockup, optional watermark |
| 2 | Problem | DARK_BG | Pain point — what's broken, frustrating, or outdated |
| 3 | Solution | Brand gradient | The answer — what solves it, optional quote/prompt box |
| 4 | Features | LIGHT_BG | What you get — feature list with icons |
| 5 | Details | DARK_BG | Depth — customization, specs, differentiators |
| 6 | How-to | LIGHT_BG | Steps — numbered workflow or process |
| 7 | CTA | Brand gradient | Call to action — logo, tagline, CTA button. **No arrow. Full progress bar.** |

**Rules:** Start with a scroll-stopping hook (value proposition or bold claim, with visual proof). End with a CTA on brand gradient - no swipe arrow, progress bar at 100%. Alternate light/dark backgrounds. Adapt, reorder, add, or remove slides to fit the topic.

**Reusable components** (use verbatim): strikethrough pills, tag pills, prompt/quote box, feature list rows, numbered steps, color swatches, CTA button.

```
// Strikethrough pill
<span style="display:inline-block;padding:6px 14px;background:rgba(0,0,0,0.08);border-radius:6px;text-decoration:line-through;color:rgba(0,0,0,0.4);font-size:12px;">{Old tool}</span>

// Tag pill
<span style="display:inline-block;padding:4px 10px;background:${BRAND_PRIMARY}15;color:${BRAND_PRIMARY};font-size:10px;font-weight:600;letter-spacing:1px;text-transform:uppercase;border-radius:4px;">{Label}</span>
```

```html
<!-- Prompt / quote box -->
<div style="padding:16px;background:rgba(0,0,0,0.15);border-radius:12px;border:1px solid rgba(255,255,255,0.08);">
  <p class="sans" style="font-size:13px;color:rgba(255,255,255,0.5);margin-bottom:6px;">{Label}</p>
  <p class="serif" style="font-size:15px;color:#fff;font-style:italic;line-height:1.4;">"{Quote text}"</p>
</div>

<!-- Feature list row -->
<div style="display:flex;align-items:flex-start;gap:14px;padding:10px 0;border-bottom:1px solid ${LIGHT_BORDER};">
  <div style="flex-shrink:0;width:24px;height:24px;border-radius:6px;background:${BRAND_PRIMARY}15;display:flex;align-items:center;justify-content:center;">{icon}</div>
  <div>
    <p class="sans" style="font-size:13px;font-weight:600;color:${isLightSlide ? '#000' : '#fff'};margin:0 0 4px;">{Label}</p>
    <p class="sans" style="font-size:12px;color:${isLightSlide ? 'rgba(0,0,0,0.6)' : 'rgba(255,255,255,0.6)'};margin:0;">{Description}</p>
  </div>
</div>

<!-- Numbered step -->
<div style="display:flex;align-items:flex-start;gap:16px;padding:14px 0;border-bottom:1px solid ${LIGHT_BORDER};">
  <span class="serif" style="flex-shrink:0;font-size:26px;font-weight:300;color:${isLightSlide ? BRAND_PRIMARY : BRAND_LIGHT};opacity:0.5;">01</span>
  <div>
    <p class="sans" style="font-size:14px;font-weight:600;color:${isLightSlide ? '#000' : '#fff'};margin:0 0 4px;">{Step title}</p>
    <p class="sans" style="font-size:12px;color:${isLightSlide ? 'rgba(0,0,0,0.6)' : 'rgba(255,255,255,0.6)'};margin:0;">{Step description}</p>
  </div>
</div>

<!-- Color swatch -->
<div style="width:32px;height:32px;border-radius:8px;background:{color};border:1px solid rgba(255,255,255,0.08);"></div>

<!-- CTA button (final slide only) -->
<div style="display:inline-flex;align-items:center;gap:8px;padding:12px 28px;background:${LIGHT_BG};color:${BRAND_DARK};font-family:'${BODY_FONT}',sans-serif;font-weight:600;font-size:14px;border-radius:28px;">{CTA text}</div>
```

### Step 6: Wrap in the Instagram preview frame

When displaying the carousel in chat, wrap it in an Instagram-style frame so the user can preview the experience:

- **Header:** Avatar (BRAND_PRIMARY circle + logo) + handle + subtitle
- **Viewport:** 4:5 aspect ratio, swipeable/draggable track with all slides
- **Dots:** Small dot indicators below the viewport
- **Actions:** Heart, comment, share, bookmark SVG icons
- **Caption:** Handle + short carousel description + "2 HOURS AGO" timestamp

Include pointer-based swipe/drag interaction for the preview, but the slides themselves are standalone export-ready images.

**Important:** The `.ig-frame` must be exactly **420px wide**. The carousel viewport inside it has a 4:5 aspect ratio (420×525px). All slide layouts, font sizes, and spacing are designed for this 420px base width. Do NOT change this width - the export process depends on it.

### Step 7: Export slides as Instagram-ready PNGs

After the user approves the carousel preview, export each slide as an individual **1080×1350px PNG** ready for direct Instagram upload.

**Critical export rules:**
1. **Use Python for HTML generation** - never shell scripts with variable interpolation; shell variables corrupt content (numbers, special characters). Generate HTML with Python's `Path.write_text()` or `open().write()`.
2. **Embed images as base64** - all user-uploaded images must be base64-encoded and embedded as `data:image/jpeg;base64,...` URIs so the HTML is fully self-contained.
3. **Keep the 420px layout width** - use Playwright's `device_scale_factor` to scale up to 1080px output WITHOUT changing the layout. Never set the viewport to 1080px wide.

```python
import asyncio
from pathlib import Path
from playwright.async_api import async_playwright

INPUT_HTML = Path("/path/to/carousel.html")
OUTPUT_DIR = Path("/path/to/output/slides")
OUTPUT_DIR.mkdir(exist_ok=True)
TOTAL_SLIDES = 7  # Update to match your carousel

# The carousel is designed at 420px wide, 4:5 aspect = 525px tall
# Target output: 1080x1350
# Scale factor: 1080 / 420 = 2.5714...
VIEW_W = 420
VIEW_H = 525
SCALE = 1080 / 420

async def export_slides():
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page(
            viewport={"width": VIEW_W, "height": VIEW_H},
            device_scale_factor=SCALE,
        )
        html_content = INPUT_HTML.read_text(encoding="utf-8")
        await page.set_content(html_content, wait_until="networkidle")
        await page.wait_for_timeout(3000)  # Wait for fonts to load

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

        for i in range(TOTAL_SLIDES):
            await page.evaluate("""(idx) => {
              const track = document.querySelector('.carousel-track');
              track.style.transition = 'none';
              track.style.transform = 'translateX(' + (-idx * 420) + 'px)';
            }""", i)
            await page.wait_for_timeout(400)
            await page.screenshot(
                path=str(OUTPUT_DIR / f"slide_{i+1}.png"),
                clip={"x": 0, "y": 0, "width": VIEW_W, "height": VIEW_H}
            )
            print(f"Exported slide {i+1}/{TOTAL_SLIDES}")

        await browser.close()

asyncio.run(export_slides())
```

**Why this works:** `device_scale_factor=2.5714` renders at high DPI so a 420px element becomes 1080px while the layout stays at 420px. `clip` captures only the viewport. `wait_for_timeout(3000)` lets Google Fonts load. `track.style.transition = 'none'` snaps slides instantly.

**Common export mistakes:**

| Mistake | What goes wrong | Fix |
|---------|----------------|-----|
| Setting viewport to 1080×1350 | Layout reflows — fonts tiny, spacing breaks | Keep viewport at 420×525, use `device_scale_factor` |
| Shell scripts to generate HTML | `$`, backticks, numbers get interpolated | Always use Python for HTML generation |
| Not waiting for fonts | Headings render in fallback fonts | `wait_for_timeout(3000)` after page load |
| Not hiding IG frame chrome | Export includes header, dots, caption | Hide `.ig-header,.ig-dots,.ig-actions,.ig-caption` |
| Changing `.ig-frame` width | Entire layout shifts | Always keep at exactly 420px |

## Output

- **Format:** a self-contained HTML carousel (previewable in chat) plus a folder of individual **1080×1350px PNG** slides, one per slide.
- **Location:** the HTML file and an output `slides/` directory written via the Playwright export script.
- **Example:** `slide_1.png … slide_7.png`, each a finished Instagram-ready image with progress bar, swipe arrow (except the last), and brand-derived styling baked in.

## Notes

- **Dependency:** Python + Playwright (Chromium) for the PNG export step.
- Content must never overlap the progress bar - use `padding-bottom: 52px` on bottom-extending content.
- User-uploaded images may be JPEGs despite a `.png` extension - check the real format with `file` and use the correct MIME type when embedding base64.
- Iterate per-slide from the preview rather than regenerating the whole carousel.
- Design principles: every slide export-ready, light/dark alternation, heading+body font pairing, brand-derived palette, progressive disclosure, special last slide, consistent components.
