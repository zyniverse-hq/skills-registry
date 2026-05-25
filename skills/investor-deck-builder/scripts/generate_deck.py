#!/usr/bin/env python3
"""
generate_deck.py — generic branded deck generator for the investor-deck-builder skill.

Produces a 16:9 PDF pitch deck using reportlab.

Design rules:
  * LAYOUT lives here. NUMBERS do not. Every business figure (revenue, ask, market
    sizes, mix, traction stats) is read from the JSON config under `content.<slide_id>`.
    If a number is missing from the config the slide renders a visible "—" placeholder
    — never a stale or wrong value.
  * Static brand copy (slide section labels, button labels) is OK to bake in — it is
    not a drift-prone number. Anything company-specific must come from config.
  * Brand colors come from `config.brand` with neutral defaults.
  * Fonts resolve across macOS / Linux / Windows and are verified to contain the
    rupee glyph (U+20B9). If no font qualifies, `money()` degrades "₹" -> "Rs ".

Usage:
    python3 generate_deck.py --config config.json --output out.pdf
    python3 generate_deck.py --config config.json            # -> ./output/<slug>.pdf
    python3 generate_deck.py --font-info                     # print resolved font + ₹ support
"""

import argparse
import json
import re
import sys
from pathlib import Path

from reportlab.lib.colors import HexColor, white
from reportlab.lib.units import inch
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

# ============================================================================
# Fonts — cross-platform, rupee-aware
# ============================================================================
_RUPEE_CP = 0x20B9
_FONT_GROUPS = [
    ("DejaVu",
     ("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 0),
     ("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 0),
     ("/usr/share/fonts/truetype/dejavu/DejaVuSans-Oblique.ttf", 0)),
    ("HelveticaMac",
     ("/System/Library/Fonts/Helvetica.ttc", 0),
     ("/System/Library/Fonts/Helvetica.ttc", 1),
     ("/System/Library/Fonts/Helvetica.ttc", 2)),
    ("ArialWin",
     ("C:/Windows/Fonts/arial.ttf", 0),
     ("C:/Windows/Fonts/arialbd.ttf", 0),
     ("C:/Windows/Fonts/ariali.ttf", 0)),
    ("Liberation",
     ("/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf", 0),
     ("/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf", 0),
     ("/usr/share/fonts/truetype/liberation/LiberationSans-Italic.ttf", 0)),
]

_FONT_REGULAR = "Helvetica"
_FONT_BOLD = "Helvetica-Bold"
_FONT_ITALIC = "Helvetica-Oblique"
RUPEE_OK = False


def _try_register(name, path, idx):
    if not Path(path).exists():
        return None
    try:
        f = TTFont(name, path, subfontIndex=idx)
    except Exception:
        return None
    pdfmetrics.registerFont(f)
    return _RUPEE_CP in getattr(f.face, "charToGlyph", {})


def _resolve_fonts():
    global _FONT_REGULAR, _FONT_BOLD, _FONT_ITALIC, RUPEE_OK
    fallback = None
    for name, reg, bold, ital in _FONT_GROUPS:
        ok = _try_register(f"Deck-{name}", reg[0], reg[1])
        if ok is None:
            continue
        b = _try_register(f"Deck-{name}-B", bold[0], bold[1])
        i = _try_register(f"Deck-{name}-I", ital[0], ital[1])
        fam = (f"Deck-{name}",
               f"Deck-{name}-B" if b is not None else f"Deck-{name}",
               f"Deck-{name}-I" if i is not None else f"Deck-{name}",
               bool(ok))
        if ok:
            _FONT_REGULAR, _FONT_BOLD, _FONT_ITALIC, RUPEE_OK = fam
            return
        fallback = fallback or fam
    if fallback:
        _FONT_REGULAR, _FONT_BOLD, _FONT_ITALIC, RUPEE_OK = fallback


_resolve_fonts()


def money(s):
    if s is None:
        return ""
    s = str(s)
    return s if RUPEE_OK else s.replace("₹", "Rs ")


# ============================================================================
# Brand defaults (overridden per-deck via config.brand)
# ============================================================================
DEFAULT_BRAND = {
    "primary":    "#1A1A1A",  # neutral monochrome by default
    "accent":     "#FFD400",  # safe accent yellow
    "background": "#FFFFFF",
    "ink":        "#1A1A1A",
    "ink_soft":   "#5C544A",
    "panel":      "#2A2520",
    "wordmark":   "your-wordmark",
}


def brand(cfg, key):
    return HexColor((cfg.get("brand") or {}).get(key, DEFAULT_BRAND[key])) \
        if key != "wordmark" else (cfg.get("brand") or {}).get(key, DEFAULT_BRAND[key])


SLIDE_WIDTH = 10 * inch
SLIDE_HEIGHT = 5.625 * inch
PAGE_SIZE = (SLIDE_WIDTH, SLIDE_HEIGHT)
MARGIN = 0.5 * inch
LOGO_Y = SLIDE_HEIGHT - 0.7 * inch
PLACEHOLDER = "—"
WHITE = white


# ============================================================================
# Content access helpers
# ============================================================================
def T(content, key, default=PLACEHOLDER):
    val = content.get(key, default)
    return money(val if val is not None else default)


def L(content, key, default=None):
    v = content.get(key)
    return v if isinstance(v, list) and v else (default if default is not None else [])


def D(content, key, default=None):
    v = content.get(key)
    return v if isinstance(v, dict) and v else (default if default is not None else {})


# ============================================================================
# Primitives
# ============================================================================
def fill_background(c, color):
    c.setFillColor(color)
    c.rect(0, 0, SLIDE_WIDTH, SLIDE_HEIGHT, fill=1, stroke=0)


def draw_wordmark(c, x, y, scale, color, text):
    c.setFillColor(color)
    c.setFont(_FONT_BOLD, 16 * scale)
    c.drawString(x, y, text)


def draw_accent_bar(c, x, y, width, height, color):
    c.setFillColor(color)
    c.rect(x, y, width, height, fill=1, stroke=0)


def wrap_text(text, max_chars):
    words = str(text).split()
    lines, current, current_len = [], [], 0
    for word in words:
        if current_len + len(word) + 1 > max_chars and current:
            lines.append(" ".join(current))
            current, current_len = [word], len(word)
        else:
            current.append(word)
            current_len += len(word) + 1
    if current:
        lines.append(" ".join(current))
    return lines


def footer_strip(c, color, height=0.08 * inch):
    c.setFillColor(color)
    c.rect(0, 0, SLIDE_WIDTH, height, fill=1, stroke=0)


def chrome(c, ctx, dark=False):
    cfg = ctx["config"]
    primary = brand(cfg, "primary")
    fg = WHITE if dark else primary
    wm = brand(cfg, "wordmark")
    draw_wordmark(c, MARGIN, LOGO_Y + 0.05 * inch, 0.7, fg, wm)
    footer_strip(c, color=primary)
    c.setFillColor(WHITE if dark else brand(cfg, "ink_soft"))
    c.setFont(_FONT_REGULAR, 8)
    c.drawRightString(SLIDE_WIDTH - MARGIN, 0.18 * inch, f"{ctx['num']} / {ctx['total']}")


def section_title(c, ctx, label, title, dark=False):
    cfg = ctx["config"]
    c.setFillColor(brand(cfg, "accent") if dark else brand(cfg, "primary"))
    c.setFont(_FONT_BOLD, 11)
    c.drawString(MARGIN, SLIDE_HEIGHT - 1.25 * inch, label)
    c.setFillColor(WHITE if dark else brand(cfg, "ink"))
    c.setFont(_FONT_BOLD, 32)
    c.drawString(MARGIN, SLIDE_HEIGHT - 1.85 * inch, title)


def card_row(c, ctx, cards, top, height):
    cfg = ctx["config"]
    accent = brand(cfg, "accent")
    ink = brand(cfg, "ink")
    n = len(cards)
    gap = 0.2 * inch
    card_w = (SLIDE_WIDTH - 2 * MARGIN - (n - 1) * gap) / n
    for i, (title, body) in enumerate(cards):
        x = MARGIN + i * (card_w + gap)
        c.setFillColor(WHITE)
        c.setStrokeColor(HexColor("#E0DED4"))
        c.setLineWidth(0.8)
        c.roundRect(x, top - height, card_w, height, 0.14 * inch, fill=1, stroke=1)
        c.setFillColor(accent)
        c.roundRect(x + 0.22 * inch, top - 0.5 * inch, card_w - 0.44 * inch, 0.4 * inch,
                    0.2 * inch, fill=1, stroke=0)
        c.setFillColor(ink)
        c.setFont(_FONT_BOLD, 11)
        c.drawCentredString(x + card_w / 2, top - 0.37 * inch, title)
        c.setFillColor(ink)
        c.setFont(_FONT_REGULAR, 8.5)
        by = top - 0.75 * inch
        for line in wrap_text(body, int(card_w / inch * 11)):
            c.drawCentredString(x + card_w / 2, by, line)
            by -= 0.16 * inch


def kv_table(c, ctx, rows, top, label_w=2.6 * inch):
    cfg = ctx["config"]
    y = top
    for k, v in rows:
        c.setFillColor(brand(cfg, "ink_soft"))
        c.setFont(_FONT_BOLD, 10)
        c.drawString(MARGIN, y, str(k))
        c.setFillColor(brand(cfg, "ink"))
        c.setFont(_FONT_REGULAR, 10)
        for line in wrap_text(money(v), 70):
            c.drawString(MARGIN + label_w, y, line)
            y -= 0.22 * inch
        y -= 0.06 * inch
    return y


# ============================================================================
# Slide renderers — signature render_x(c, ctx)
# ============================================================================
def render_cover(c, ctx):
    cfg = ctx["config"]
    fill_background(c, brand(cfg, "background"))
    primary = brand(cfg, "primary")
    accent = brand(cfg, "accent")
    ink = brand(cfg, "ink")

    draw_wordmark(c, MARGIN, SLIDE_HEIGHT - 1.2 * inch, 2.2, primary, brand(cfg, "wordmark"))

    c.setFillColor(ink)
    c.setFont(_FONT_BOLD, 36)
    sub = cfg.get("cover_subtitle", "<positioning line>")
    for i, line in enumerate(wrap_text(sub, 36)[:2]):
        c.drawString(MARGIN, SLIDE_HEIGHT - 2.6 * inch - i * 0.7 * inch, line)

    tw = c.stringWidth(sub, _FONT_BOLD, 36) if len(wrap_text(sub, 36)) == 1 else 0
    if tw:
        draw_accent_bar(c, MARGIN - 0.05 * inch, SLIDE_HEIGHT - 2.75 * inch,
                        min(tw + 0.2 * inch, SLIDE_WIDTH - 2 * MARGIN), 0.65 * inch, accent)
        c.setFillColor(ink)
        c.setFont(_FONT_BOLD, 36)
        c.drawString(MARGIN, SLIDE_HEIGHT - 2.6 * inch, sub)

    c.setStrokeColor(primary)
    c.setLineWidth(2)
    c.line(MARGIN, 1.0 * inch, SLIDE_WIDTH - MARGIN, 1.0 * inch)

    c.setFillColor(ink)
    c.setFont(_FONT_BOLD, 10)
    c.drawString(MARGIN, 0.7 * inch, "Presented by:")
    c.setFont(_FONT_REGULAR, 10)
    c.drawString(MARGIN, 0.5 * inch, cfg.get("presenter", "<Presenter Name>"))
    c.drawString(MARGIN, 0.32 * inch, cfg.get("presenter_role", "<Role>"))

    c.setFont(_FONT_BOLD, 10)
    c.setFillColor(primary)
    c.drawCentredString(SLIDE_WIDTH / 2, 0.5 * inch, money(cfg.get("cover_footer", "<round label>")))

    c.setFillColor(brand(cfg, "ink_soft"))
    c.setFont(_FONT_ITALIC, 9)
    c.drawRightString(SLIDE_WIDTH - MARGIN, 0.5 * inch, cfg.get("investor", ""))


def render_about_company(c, ctx):
    cfg = ctx["config"]
    fill_background(c, brand(cfg, "background"))
    chrome(c, ctx)
    section_title(c, ctx, "Company Profile", "About the Company")
    d = ctx["content"]
    rows = [
        ("Company Name", T(d, "company")),
        ("Website", T(d, "website")),
        ("Address", T(d, "address")),
        ("Contact", T(d, "contact")),
        ("Incorporated", T(d, "doi")),
        ("Reg / CIN", T(d, "cin")),
    ]
    y = kv_table(c, ctx, rows, SLIDE_HEIGHT - 2.4 * inch)
    directors = L(d, "directors")
    if directors:
        c.setFillColor(brand(cfg, "primary"))
        c.setFont(_FONT_BOLD, 10)
        c.drawString(MARGIN, y, "Directors")
        y -= 0.22 * inch
        c.setFillColor(brand(cfg, "ink"))
        c.setFont(_FONT_REGULAR, 9)
        for dr in directors:
            c.drawString(MARGIN + 0.2 * inch, y,
                         f"{dr.get('name', '')} · {dr.get('din', '')} · {dr.get('shares', '')}")
            y -= 0.2 * inch


def render_problem(c, ctx):
    cfg = ctx["config"]
    fill_background(c, brand(cfg, "background"))
    chrome(c, ctx)
    d = ctx["content"]

    c.setFillColor(brand(cfg, "primary"))
    c.setFont(_FONT_BOLD, 11)
    c.drawString(MARGIN, SLIDE_HEIGHT - 1.4 * inch, "Problem Statement")

    c.setFillColor(brand(cfg, "ink"))
    c.setFont(_FONT_BOLD, 42)
    headline = T(d, "headline", "<Headline>")
    for i, line in enumerate(wrap_text(headline, 22)[:2]):
        c.drawString(MARGIN, SLIDE_HEIGHT - 2.3 * inch - i * 0.6 * inch, line)

    by = SLIDE_HEIGHT - 3.5 * inch
    c.setFillColor(brand(cfg, "ink"))
    c.setFont(_FONT_REGULAR, 12)
    for line in L(d, "body"):
        c.drawString(MARGIN, by, money(line))
        by -= 0.22 * inch

    stat = T(d, "stat", "")
    if stat:
        cy = 1.05 * inch
        c.setFillColor(brand(cfg, "accent"))
        c.circle(MARGIN + 0.18 * inch, cy + 0.12 * inch, 0.16 * inch, fill=1, stroke=0)
        c.setFillColor(brand(cfg, "primary"))
        c.setFont(_FONT_BOLD, 16)
        c.drawCentredString(MARGIN + 0.18 * inch, cy + 0.04 * inch, "!")
        c.setFillColor(brand(cfg, "ink"))
        c.setFont(_FONT_BOLD, 11)
        ly = cy + 0.18 * inch
        for line in wrap_text(stat, 80):
            c.drawString(MARGIN + 0.5 * inch, ly, line)
            ly -= 0.2 * inch

    src = T(d, "source", "")
    if src:
        c.setFillColor(brand(cfg, "ink_soft"))
        c.setFont(_FONT_ITALIC, 8)
        c.drawString(MARGIN, 0.3 * inch, "Source: " + src)


def render_problem_stakeholders(c, ctx):
    cfg = ctx["config"]
    fill_background(c, brand(cfg, "background"))
    chrome(c, ctx)
    d = ctx["content"]

    c.setFillColor(brand(cfg, "primary"))
    c.setFont(_FONT_BOLD, 11)
    c.drawString(MARGIN, SLIDE_HEIGHT - 1.3 * inch, "Problem Statement")
    c.setFillColor(brand(cfg, "ink"))
    c.setFont(_FONT_BOLD, 36)
    c.drawRightString(SLIDE_WIDTH - MARGIN, SLIDE_HEIGHT - 1.4 * inch, "The Core Pain")

    rows = L(d, "rows")
    palettes = [
        (brand(cfg, "primary"), WHITE, None),
        (brand(cfg, "panel"), WHITE, None),
        (brand(cfg, "background"), brand(cfg, "ink"), brand(cfg, "accent")),
    ]
    rh = 0.85 * inch
    ry = SLIDE_HEIGHT - 2.1 * inch - rh
    for i, row in enumerate(rows[:3]):
        bg, fg, border = palettes[i] if i < len(palettes) else palettes[-1]
        if border:
            c.setStrokeColor(border)
            c.setLineWidth(2)
            c.setFillColor(bg)
            c.roundRect(MARGIN, ry, SLIDE_WIDTH - 2 * MARGIN, rh, 0.1 * inch, fill=1, stroke=1)
        else:
            c.setFillColor(bg)
            c.roundRect(MARGIN, ry, SLIDE_WIDTH - 2 * MARGIN, rh, 0.1 * inch, fill=1, stroke=0)
        c.setFillColor(fg)
        c.setFont(_FONT_BOLD, 16)
        c.drawString(MARGIN + 0.35 * inch, ry + rh / 2 - 0.05 * inch, row.get("title", ""))
        qx = MARGIN + 2.2 * inch
        qy = ry + rh - 0.3 * inch
        c.setFillColor(brand(cfg, "accent"))
        qt = f'"{row.get("quote", "")}"'
        c.setFont(_FONT_ITALIC, 9)
        qw = c.stringWidth(qt, _FONT_ITALIC, 9) + 0.15 * inch
        c.roundRect(qx, qy - 0.05 * inch, qw, 0.22 * inch, 0.06 * inch, fill=1, stroke=0)
        c.setFillColor(brand(cfg, "ink"))
        c.drawString(qx + 0.075 * inch, qy, qt)
        c.setFillColor(fg)
        c.setFont(_FONT_REGULAR, 9)
        dy = ry + rh - 0.6 * inch
        for line in wrap_text(row.get("detail", ""), 75):
            c.drawString(qx, dy, line)
            dy -= 0.16 * inch
        ry -= rh + 0.1 * inch

    gap = T(d, "gap_line", "")
    if gap:
        c.setFillColor(brand(cfg, "ink"))
        c.setFont(_FONT_REGULAR, 11)
        c.drawString(MARGIN, 0.6 * inch, gap)


def render_solution(c, ctx):
    cfg = ctx["config"]
    fill_background(c, brand(cfg, "background"))
    chrome(c, ctx)
    d = ctx["content"]
    primary = brand(cfg, "primary")
    accent = brand(cfg, "accent")
    ink = brand(cfg, "ink")

    pills = L(d, "pills")[:3]
    for i, label in enumerate(pills):
        px = MARGIN + 0.2 * inch + i * 1.55 * inch
        py = SLIDE_HEIGHT - 1.6 * inch
        c.setFillColor(accent)
        c.roundRect(px, py, 1.45 * inch, 0.3 * inch, 0.15 * inch, fill=1, stroke=0)
        c.setFillColor(ink)
        c.setFont(_FONT_BOLD, 9)
        c.drawCentredString(px + 0.725 * inch, py + 0.1 * inch, str(label))

    panel_x, panel_y = MARGIN, 0.5 * inch
    panel_w, panel_h = 3.5 * inch, 2.3 * inch
    c.setFillColor(primary)
    c.roundRect(panel_x, panel_y, panel_w, panel_h, 0.15 * inch, fill=1, stroke=0)
    c.setFillColor(WHITE)
    c.setFont(_FONT_BOLD, 18)
    tagline = T(d, "tagline", "<Tagline>")
    ty = panel_y + panel_h - 0.6 * inch
    for line in wrap_text(tagline, 22)[:3]:
        c.drawString(panel_x + 0.3 * inch, ty, line)
        ty -= 0.4 * inch

    rx, ry = 4.3 * inch, SLIDE_HEIGHT - 1.7 * inch
    c.setFillColor(ink)
    c.setFont(_FONT_REGULAR, 11)
    y = ry
    for para in L(d, "body"):
        for line in wrap_text(money(para), 55):
            c.drawString(rx, y, line)
            y -= 0.22 * inch
        y -= 0.12 * inch

    c.setFillColor(brand(cfg, "panel"))
    c.roundRect(4.3 * inch, 0.6 * inch, 5.0 * inch, 1.8 * inch, 0.1 * inch, fill=1, stroke=0)
    c.setFillColor(brand(cfg, "background"))
    c.setFont(_FONT_ITALIC, 9)
    c.drawCentredString(6.8 * inch, 1.45 * inch, T(d, "image_caption", "[ image placeholder ]"))


def render_product(c, ctx):
    cfg = ctx["config"]
    fill_background(c, brand(cfg, "background"))
    chrome(c, ctx)
    section_title(c, ctx, "Product", T(ctx["content"], "headline", "Product Overview"))
    sub = T(ctx["content"], "subtitle", "")
    if sub:
        c.setFillColor(brand(cfg, "ink_soft"))
        c.setFont(_FONT_ITALIC, 9)
        c.drawString(MARGIN, SLIDE_HEIGHT - 2.15 * inch, sub)
    cards = [(card.get("title", ""), money(card.get("body", "")))
             for card in L(ctx["content"], "cards")[:4]]
    if cards:
        card_row(c, ctx, cards, SLIDE_HEIGHT - 2.4 * inch, 1.7 * inch)
    rm = T(ctx["content"], "roadmap_line", "")
    if rm:
        c.setFillColor(brand(cfg, "ink_soft"))
        c.setFont(_FONT_ITALIC, 8.5)
        c.drawCentredString(SLIDE_WIDTH / 2, 0.35 * inch, rm)


def render_tech_core(c, ctx):
    cfg = ctx["config"]
    fill_background(c, brand(cfg, "primary"))
    draw_wordmark(c, MARGIN, LOGO_Y + 0.05 * inch, 0.7, WHITE, brand(cfg, "wordmark"))
    c.setFillColor(WHITE)
    c.setFont(_FONT_BOLD, 48)
    c.drawString(MARGIN, SLIDE_HEIGHT - 2.2 * inch, T(ctx["content"], "headline", "Tech at the Core"))
    pillars = L(ctx["content"], "pillars")[:3]
    cy, ch, cw, gap = 1.3 * inch, 1.7 * inch, 2.9 * inch, 0.2 * inch
    start_x = (SLIDE_WIDTH - (3 * cw + 2 * gap)) / 2
    accent = brand(cfg, "accent")
    ink = brand(cfg, "ink")
    for i, p in enumerate(pillars):
        x = start_x + i * (cw + gap)
        c.setFillColor(WHITE)
        c.roundRect(x, cy, cw, ch, 0.15 * inch, fill=1, stroke=0)
        c.setFillColor(accent)
        c.roundRect(x + 0.3 * inch, cy + ch - 0.55 * inch, cw - 0.6 * inch, 0.4 * inch,
                    0.2 * inch, fill=1, stroke=0)
        c.setFillColor(ink)
        c.setFont(_FONT_BOLD, 12)
        c.drawCentredString(x + cw / 2, cy + ch - 0.4 * inch, p.get("title", ""))
        c.setFillColor(ink)
        c.setFont(_FONT_REGULAR, 9.5)
        by = cy + ch - 0.85 * inch
        for line in wrap_text(money(p.get("body", "")), 38):
            c.drawCentredString(x + cw / 2, by, line)
            by -= 0.17 * inch
    strap = T(ctx["content"], "strapline", "")
    if strap:
        c.setFillColor(accent)
        c.roundRect(MARGIN + 0.5 * inch, 0.6 * inch, SLIDE_WIDTH - 2 * MARGIN - 1 * inch,
                    0.55 * inch, 0.05 * inch, fill=1, stroke=0)
        c.setFillColor(ink)
        c.setFont(_FONT_BOLD, 9.5)
        lines = wrap_text(strap, 100)[:2]
        for i, line in enumerate(lines):
            c.drawCentredString(SLIDE_WIDTH / 2, 0.92 * inch - i * 0.2 * inch, line)
    footer_strip(c, color=brand(cfg, "primary"))
    c.setFillColor(brand(cfg, "background"))
    c.setFont(_FONT_REGULAR, 8)
    c.drawRightString(SLIDE_WIDTH - MARGIN, 0.22 * inch, f"{ctx['num']} / {ctx['total']}")


def render_tech_deep(c, ctx):
    cfg = ctx["config"]
    fill_background(c, brand(cfg, "background"))
    chrome(c, ctx)
    section_title(c, ctx, "Deep Tech", T(ctx["content"], "subtitle", "Framework Detail"))
    pills = L(ctx["content"], "pills")[:6]
    top = SLIDE_HEIGHT - 2.2 * inch
    col_w = (SLIDE_WIDTH - 2 * MARGIN - 2 * 0.2 * inch) / 3
    row_h = 1.05 * inch
    accent = brand(cfg, "accent")
    soft = HexColor("#F2A653")
    for i, p in enumerate(pills):
        col, row = i % 3, i // 3
        x = MARGIN + col * (col_w + 0.2 * inch)
        y = top - row * (row_h + 0.15 * inch)
        c.setFillColor(accent if i % 2 == 0 else soft)
        c.roundRect(x, y - row_h, col_w, row_h, 0.1 * inch, fill=1, stroke=0)
        c.setFillColor(brand(cfg, "ink"))
        c.setFont(_FONT_BOLD, 11)
        c.drawString(x + 0.15 * inch, y - 0.28 * inch, p.get("label", ""))
        c.setFont(_FONT_REGULAR, 8.5)
        yy = y - 0.5 * inch
        for line in wrap_text(money(p.get("body", "")), int(col_w / inch * 12)):
            c.drawString(x + 0.15 * inch, yy, line)
            yy -= 0.15 * inch
    c.setFillColor(brand(cfg, "ink_soft"))
    c.setFont(_FONT_ITALIC, 8)
    footer_bits = []
    if T(ctx["content"], "patent_status", ""):
        footer_bits.append(T(ctx["content"], "patent_status", ""))
    if T(ctx["content"], "definitions", ""):
        footer_bits.append(T(ctx["content"], "definitions", ""))
    if footer_bits:
        c.drawString(MARGIN, 0.3 * inch, "  ·  ".join(footer_bits))


def render_traction(c, ctx):
    cfg = ctx["config"]
    fill_background(c, brand(cfg, "background"))
    chrome(c, ctx)
    accent = brand(cfg, "accent")
    ink = brand(cfg, "ink")

    c.setFillColor(ink)
    c.setFont(_FONT_BOLD, 48)
    c.drawString(MARGIN, SLIDE_HEIGHT - 1.9 * inch, "Traction")

    c.setFillColor(accent)
    c.roundRect(MARGIN, SLIDE_HEIGHT - 2.4 * inch, 1.8 * inch, 0.3 * inch, 0.15 * inch, fill=1, stroke=0)
    c.setFillColor(ink)
    c.setFont(_FONT_BOLD, 10)
    c.drawCentredString(MARGIN + 0.9 * inch, SLIDE_HEIGHT - 2.25 * inch, "Traction & Milestones")

    t = D(ctx["content"], "testimonial")
    if t:
        bx, by = 5.0 * inch, SLIDE_HEIGHT - 2.7 * inch
        c.setFillColor(WHITE)
        c.setStrokeColor(ink)
        c.setLineWidth(1)
        c.roundRect(bx, by, 4.5 * inch, 1.0 * inch, 0.1 * inch, fill=1, stroke=1)
        c.setFillColor(ink)
        c.setFont(_FONT_ITALIC, 8.5)
        ty = by + 0.8 * inch
        for line in wrap_text(f'"{t.get("quote", "")}"', 65):
            c.drawString(bx + 0.15 * inch, ty, line)
            ty -= 0.17 * inch
        c.setFont(_FONT_BOLD, 9)
        c.drawString(bx + 0.15 * inch, by + 0.1 * inch, f'— {t.get("author", "")}')

    band_y, band_h = 0.15 * inch, 2.0 * inch
    c.setFillColor(brand(cfg, "panel"))
    c.rect(0, band_y, SLIDE_WIDTH, band_h, fill=1, stroke=0)
    stats = L(ctx["content"], "stats", [
        {"big": PLACEHOLDER, "label": "", "detail": ""},
        {"big": PLACEHOLDER, "label": "", "detail": ""},
        {"big": PLACEHOLDER, "label": "", "detail": ""},
        {"big": PLACEHOLDER, "label": "", "detail": ""},
    ])[:4]
    col_w = SLIDE_WIDTH / 4
    for i, s in enumerate(stats):
        cx = i * col_w + col_w / 2
        c.setFillColor(accent)
        c.circle(cx, band_y + band_h - 0.15 * inch, 0.06 * inch, fill=1, stroke=0)
        c.setFillColor(WHITE)
        c.setFont(_FONT_BOLD, 22)
        c.drawCentredString(cx, band_y + band_h - 0.65 * inch, money(s.get("big", PLACEHOLDER)))
        c.setFont(_FONT_BOLD, 14)
        c.drawCentredString(cx, band_y + band_h - 0.95 * inch, str(s.get("label", "")))
        c.setFillColor(brand(cfg, "background"))
        c.setFont(_FONT_REGULAR, 8.5)
        for li, line in enumerate(wrap_text(money(s.get("detail", "")), 26)):
            c.drawCentredString(cx, band_y + band_h - 1.3 * inch - li * 0.16 * inch, line)


def render_distribution(c, ctx):
    cfg = ctx["config"]
    fill_background(c, brand(cfg, "background"))
    chrome(c, ctx)
    primary = brand(cfg, "primary")
    ink = brand(cfg, "ink")

    banner_h = 1.0 * inch
    banner_y = SLIDE_HEIGHT - banner_h
    c.setFillColor(primary)
    c.rect(0, banner_y, SLIDE_WIDTH, banner_h, fill=1, stroke=0)
    draw_wordmark(c, MARGIN, banner_y + 0.4 * inch, 0.7, WHITE, brand(cfg, "wordmark"))
    c.setFillColor(WHITE)
    c.setFont(_FONT_BOLD, 28)
    c.drawCentredString(SLIDE_WIDTH / 2, banner_y + 0.3 * inch,
                        T(ctx["content"], "headline", "Distribution Advantage"))

    rows = L(ctx["content"], "rows")
    table_top = banner_y - 0.3 * inch
    col_xs = [MARGIN, MARGIN + 2.0 * inch, MARGIN + 4.5 * inch, MARGIN + 7.0 * inch]
    headers = ["Stakeholder", "What they get FREE", "What they pay for", "What they bring"]
    c.setFont(_FONT_BOLD, 10)
    c.setFillColor(ink)
    for i, h in enumerate(headers):
        c.drawString(col_xs[i] + 0.08 * inch, table_top - 0.25 * inch, h)
    c.setStrokeColor(ink)
    c.setLineWidth(1)
    c.line(MARGIN, table_top - 0.4 * inch, SLIDE_WIDTH - MARGIN, table_top - 0.4 * inch)
    row_h = 0.6 * inch
    ry = table_top - 0.4 * inch - row_h
    green = HexColor("#A8E63C")
    for r in rows[:5]:
        c.setFont(_FONT_BOLD, 10)
        c.setFillColor(ink)
        c.drawString(col_xs[0] + 0.08 * inch, ry + 0.35 * inch, r.get("stakeholder", ""))
        c.setFont(_FONT_REGULAR, 9)
        for i, line in enumerate(str(r.get("gets_free", "")).split("\n")):
            c.drawString(col_xs[1] + 0.08 * inch, ry + 0.35 * inch - i * 0.18 * inch, money(line))
        for i, line in enumerate(str(r.get("pays_for", "")).split("\n")):
            c.drawString(col_xs[2] + 0.08 * inch, ry + 0.35 * inch - i * 0.18 * inch, money(line))
        if r.get("is_revenue"):
            c.setFillColor(green)
            c.rect(col_xs[3] + 0.08 * inch, ry + 0.2 * inch, 1.8 * inch, 0.3 * inch, fill=1, stroke=0)
            c.setFillColor(ink)
            c.setFont(_FONT_BOLD, 11)
            c.drawCentredString(col_xs[3] + 0.98 * inch, ry + 0.3 * inch, str(r.get("brings", "REVENUE")))
        else:
            for i, line in enumerate(str(r.get("brings", "")).split("\n")):
                c.drawString(col_xs[3] + 0.08 * inch, ry + 0.35 * inch - i * 0.18 * inch, money(line))
        c.setStrokeColor(brand(cfg, "ink_soft"))
        c.setLineWidth(0.3)
        c.line(MARGIN, ry, SLIDE_WIDTH - MARGIN, ry)
        ry -= row_h

    strap = T(ctx["content"], "strapline", "")
    if strap:
        c.setFillColor(ink)
        c.setFont(_FONT_BOLD, 13)
        c.drawCentredString(SLIDE_WIDTH / 2, 0.4 * inch, strap)


def render_market(c, ctx):
    cfg = ctx["config"]
    fill_background(c, brand(cfg, "background"))
    chrome(c, ctx)
    primary = brand(cfg, "primary")
    accent = brand(cfg, "accent")
    ink = brand(cfg, "ink")
    soft = HexColor("#F2A653")

    banner_h = 1.0 * inch
    banner_y = SLIDE_HEIGHT - banner_h
    c.setFillColor(primary)
    c.rect(0, banner_y, SLIDE_WIDTH, banner_h, fill=1, stroke=0)
    draw_wordmark(c, MARGIN, banner_y + 0.4 * inch, 0.7, WHITE, brand(cfg, "wordmark"))
    c.setFillColor(WHITE)
    c.setFont(_FONT_BOLD, 30)
    c.drawRightString(SLIDE_WIDTH - MARGIN, banner_y + 0.3 * inch, "Market Opportunity")

    pyramids = L(ctx["content"], "pyramids")[:3]
    pyr_w = (SLIDE_WIDTH - 2 * MARGIN) / 3
    top = banner_y - 0.4 * inch
    for i, pyr in enumerate(pyramids):
        cx = MARGIN + i * pyr_w + pyr_w / 2
        c.setFillColor(ink)
        c.setFont(_FONT_BOLD, 11)
        c.drawCentredString(cx, top - 0.1 * inch, str(pyr.get("title", "")))
        tiers = [
            (primary, WHITE, pyr.get("tam", ""), 0.6 * inch, 0.6 * inch, 1.4 * inch, 7),
            (accent, ink, pyr.get("sam", ""), 0.35 * inch, 1.4 * inch, 1.9 * inch, 7),
            (soft, ink, pyr.get("som", ""), 0.3 * inch, 1.9 * inch, 2.3 * inch, 7.5),
        ]
        ty = top - 0.5 * inch
        for fill, txt_col, label, h, tw, bw, fs in tiers:
            c.setFillColor(fill)
            p = c.beginPath()
            p.moveTo(cx - tw / 2, ty)
            p.lineTo(cx + tw / 2, ty)
            p.lineTo(cx + bw / 2, ty - h)
            p.lineTo(cx - bw / 2, ty - h)
            p.close()
            c.drawPath(p, fill=1, stroke=0)
            c.setFillColor(txt_col)
            c.setFont(_FONT_REGULAR, fs)
            yy = ty - 0.16 * inch
            for line in str(label).split("\n"):
                c.drawCentredString(cx, yy, money(line))
                yy -= 0.13 * inch
            ty -= h

    c.setFillColor(ink)
    c.setFont(_FONT_BOLD, 11)
    c.drawCentredString(SLIDE_WIDTH / 2, 0.55 * inch,
                        money(T(ctx["content"], "total_line", "")))
    c.setFont(_FONT_ITALIC, 7)
    c.setFillColor(brand(cfg, "ink_soft"))
    c.drawCentredString(SLIDE_WIDTH / 2, 0.35 * inch, T(ctx["content"], "sources", ""))


def render_business_model(c, ctx):
    cfg = ctx["config"]
    fill_background(c, brand(cfg, "background"))
    chrome(c, ctx)
    section_title(c, ctx, "How We Make Money", "Business Model")
    cards = [(card.get("title", ""), money(card.get("body", "")))
             for card in L(ctx["content"], "cards")[:4]]
    if cards:
        card_row(c, ctx, cards, SLIDE_HEIGHT - 2.3 * inch, 1.9 * inch)
    syn = T(ctx["content"], "synthesis_line", "")
    if syn:
        c.setFillColor(brand(cfg, "primary"))
        c.setFont(_FONT_BOLD, 12)
        c.drawCentredString(SLIDE_WIDTH / 2, 0.4 * inch, syn)


def render_revenue_trajectory(c, ctx):
    cfg = ctx["config"]
    fill_background(c, brand(cfg, "background"))
    chrome(c, ctx)
    section_title(c, ctx, "Improving unit economics with every cohort", "3-Year Revenue Trajectory")
    c.setFillColor(brand(cfg, "primary"))
    c.setFont(_FONT_BOLD, 16)
    c.drawString(MARGIN, SLIDE_HEIGHT - 2.4 * inch, money(T(ctx["content"], "trajectory", "")))
    y = SLIDE_HEIGHT - 2.9 * inch
    c.setFillColor(brand(cfg, "ink"))
    c.setFont(_FONT_REGULAR, 11)
    for r in L(ctx["content"], "highlights"):
        c.drawString(MARGIN + 0.1 * inch, y, "• " + money(r))
        y -= 0.28 * inch
    bars = L(ctx["content"], "bars")
    if bars:
        maxv = max([b[1] for b in bars] + [1])
        bx, bw, base = 5.5 * inch, 0.9 * inch, 0.7 * inch
        for i, item in enumerate(bars):
            lbl, val = item[0], item[1]
            h = (val / maxv) * 2.6 * inch
            x = bx + i * (bw + 0.5 * inch)
            c.setFillColor(brand(cfg, "primary"))
            c.rect(x, base, bw, h, fill=1, stroke=0)
            c.setFillColor(brand(cfg, "ink"))
            c.setFont(_FONT_BOLD, 9)
            c.drawCentredString(x + bw / 2, base + h + 0.08 * inch, money(str(val)))
            c.setFont(_FONT_REGULAR, 9)
            c.drawCentredString(x + bw / 2, base - 0.2 * inch, str(lbl))


def render_why_team(c, ctx):
    cfg = ctx["config"]
    fill_background(c, brand(cfg, "background"))
    chrome(c, ctx)
    primary = brand(cfg, "primary")
    ink = brand(cfg, "ink")
    accent = brand(cfg, "accent")

    c.setFillColor(ink)
    c.setFont(_FONT_BOLD, 28)
    c.drawString(MARGIN, SLIDE_HEIGHT - 1.5 * inch, T(ctx["content"], "headline", "Why This Team"))

    founders = L(ctx["content"], "founders")[:3]
    cw, ch, gap = 1.85 * inch, 2.4 * inch, 0.1 * inch
    cy = 0.95 * inch
    for i, f in enumerate(founders):
        cx = MARGIN + i * (cw + gap)
        c.setFillColor(WHITE)
        c.setStrokeColor(HexColor("#E0DED4"))
        c.setLineWidth(0.5)
        c.roundRect(cx, cy, cw, ch, 0.08 * inch, fill=1, stroke=1)
        c.setFillColor(HexColor("#D8D2C0"))
        c.roundRect(cx + 0.1 * inch, cy + ch - 1.3 * inch, cw - 0.2 * inch, 1.2 * inch,
                    0.05 * inch, fill=1, stroke=0)
        c.setFillColor(brand(cfg, "ink_soft"))
        c.setFont(_FONT_ITALIC, 7)
        c.drawCentredString(cx + cw / 2, cy + ch - 0.75 * inch, "[ photo ]")
        c.setFillColor(ink)
        c.setFont(_FONT_BOLD, 10)
        c.drawString(cx + 0.12 * inch, cy + ch - 1.5 * inch, f.get("name", ""))
        c.setFillColor(primary)
        c.setFont(_FONT_REGULAR, 8)
        c.drawString(cx + 0.12 * inch, cy + ch - 1.66 * inch, f.get("role", ""))
        c.setFillColor(ink)
        c.setFont(_FONT_REGULAR, 7)
        yy = cy + ch - 1.85 * inch
        for line in wrap_text(money(f.get("bio", "")), 33):
            c.drawString(cx + 0.12 * inch, yy, line)
            yy -= 0.13 * inch

    advisors = L(ctx["content"], "advisors")[:4]
    adv_x = MARGIN + 3 * (cw + gap) + 0.15 * inch
    c.setFillColor(accent)
    c.roundRect(adv_x, SLIDE_HEIGHT - 1.55 * inch, 1.5 * inch, 0.3 * inch, 0.15 * inch, fill=1, stroke=0)
    c.setFillColor(ink)
    c.setFont(_FONT_BOLD, 10)
    c.drawCentredString(adv_x + 0.75 * inch, SLIDE_HEIGHT - 1.45 * inch, "Advisory Board")
    ay = SLIDE_HEIGHT - 2.0 * inch
    for a in advisors:
        c.setFillColor(ink)
        c.setFont(_FONT_BOLD, 8)
        c.drawString(adv_x, ay, a.get("name", ""))
        c.setFillColor(brand(cfg, "ink_soft"))
        c.setFont(_FONT_REGULAR, 7)
        c.drawString(adv_x, ay - 0.13 * inch, a.get("role", ""))
        ay -= 0.42 * inch

    c.setFillColor(primary)
    c.rect(0, 0.15 * inch, SLIDE_WIDTH, 0.55 * inch, fill=1, stroke=0)
    c.setFillColor(WHITE)
    c.setFont(_FONT_BOLD, 11)
    c.drawString(MARGIN, 0.42 * inch, "Why This Team:")
    c.setFont(_FONT_REGULAR, 10)
    c.drawString(MARGIN + 1.4 * inch, 0.42 * inch, T(ctx["content"], "banner_line", ""))


def render_use_of_funds(c, ctx):
    cfg = ctx["config"]
    fill_background(c, brand(cfg, "background"))
    chrome(c, ctx)
    section_title(c, ctx, "Use of Funds", T(ctx["content"], "headline", "Funding Requirements"))
    c.setFillColor(brand(cfg, "ink"))
    c.setFont(_FONT_REGULAR, 11)
    by = SLIDE_HEIGHT - 2.25 * inch
    for line in wrap_text(money(T(ctx["content"], "body", "")), 60):
        c.drawString(MARGIN, by, line)
        by -= 0.2 * inch
    allocation = L(ctx["content"], "allocation")
    if not allocation:
        return
    ly = SLIDE_HEIGHT - 2.7 * inch
    maxpct = max([a.get("pct", 0) for a in allocation] + [1])
    for a in allocation:
        pct = a.get("pct", 0)
        c.setFillColor(brand(cfg, "ink"))
        c.setFont(_FONT_REGULAR, 9)
        c.drawString(MARGIN, ly, str(a.get("label", "")))
        c.setFillColor(brand(cfg, "primary"))
        bw = (pct / maxpct) * 3.0 * inch
        c.rect(MARGIN + 2.4 * inch, ly - 0.02 * inch, bw, 0.13 * inch, fill=1, stroke=0)
        c.setFillColor(brand(cfg, "ink"))
        c.setFont(_FONT_BOLD, 9)
        c.drawString(MARGIN + 2.4 * inch + bw + 0.06 * inch, ly, f"{pct}%")
        ly -= 0.27 * inch


def render_milestones(c, ctx):
    cfg = ctx["config"]
    fill_background(c, brand(cfg, "background"))
    chrome(c, ctx)
    section_title(c, ctx, "Plan", "Project Milestones")
    primary = brand(cfg, "primary")
    cols = [
        D(ctx["content"], "m1", {"title": "<Phase 1>", "items": []}),
        D(ctx["content"], "m2", {"title": "<Phase 2>", "items": []}),
    ]
    col_w = (SLIDE_WIDTH - 2 * MARGIN - 0.3 * inch) / 2
    for i, col in enumerate(cols):
        x = MARGIN + i * (col_w + 0.3 * inch)
        c.setFillColor(primary)
        c.roundRect(x, SLIDE_HEIGHT - 2.5 * inch, col_w, 0.4 * inch, 0.08 * inch, fill=1, stroke=0)
        c.setFillColor(WHITE)
        c.setFont(_FONT_BOLD, 10)
        c.drawString(x + 0.15 * inch, SLIDE_HEIGHT - 2.38 * inch, col.get("title", ""))
        c.setFillColor(brand(cfg, "ink"))
        c.setFont(_FONT_REGULAR, 9)
        yy = SLIDE_HEIGHT - 2.8 * inch
        for it in col.get("items", []):
            for line in wrap_text("• " + money(it), int(col_w / inch * 11)):
                c.drawString(x + 0.1 * inch, yy, line)
                yy -= 0.18 * inch


def render_why_invest_now(c, ctx):
    cfg = ctx["config"]
    fill_background(c, brand(cfg, "background"))
    chrome(c, ctx)
    primary = brand(cfg, "primary")
    accent = brand(cfg, "accent")
    ink = brand(cfg, "ink")

    banner_h = 2.5 * inch
    banner_y = SLIDE_HEIGHT - banner_h
    c.setFillColor(primary)
    c.rect(0, banner_y, SLIDE_WIDTH, banner_h, fill=1, stroke=0)
    draw_wordmark(c, MARGIN, banner_y + banner_h - 0.45 * inch, 0.7, WHITE, brand(cfg, "wordmark"))
    c.setFillColor(WHITE)
    c.setFont(_FONT_BOLD, 44)
    c.drawCentredString(SLIDE_WIDTH / 2, banner_y + 0.7 * inch, "Why Invest Now")

    reasons = L(ctx["content"], "reasons")[:3]
    cw, ch, gap = 2.9 * inch, 2.0 * inch, 0.15 * inch
    start_x = (SLIDE_WIDTH - (3 * cw + 2 * gap)) / 2
    for i, r in enumerate(reasons):
        x = start_x + i * (cw + gap)
        c.setFillColor(WHITE)
        c.setStrokeColor(ink)
        c.setLineWidth(0.8)
        c.roundRect(x, 0.5 * inch, cw, ch, 0.15 * inch, fill=1, stroke=1)
        c.setFillColor(accent)
        c.roundRect(x + 0.3 * inch, 0.5 * inch + ch - 0.55 * inch, cw - 0.6 * inch, 0.42 * inch,
                    0.2 * inch, fill=1, stroke=0)
        c.setFillColor(ink)
        c.setFont(_FONT_BOLD, 11)
        c.drawCentredString(x + cw / 2, 0.5 * inch + ch - 0.38 * inch, r.get("title", ""))
        c.setFillColor(ink)
        c.setFont(_FONT_REGULAR, 8.5)
        yy = 0.5 * inch + ch - 0.85 * inch
        for line in wrap_text(money(r.get("body", "")), 42):
            c.drawCentredString(x + cw / 2, yy, line)
            yy -= 0.15 * inch

    c.setFillColor(ink)
    c.setFont(_FONT_REGULAR, 10)
    c.drawCentredString(SLIDE_WIDTH / 2, 0.27 * inch, "Three reasons this is the right moment")


def render_competitive_landscape(c, ctx):
    cfg = ctx["config"]
    fill_background(c, brand(cfg, "background"))
    chrome(c, ctx)
    section_title(c, ctx, "Competition", "Competitive Landscape")
    primary = brand(cfg, "primary")
    ink = brand(cfg, "ink")

    headers = ["Competitor", "Their limitation", "Our edge"]
    xs = [MARGIN, MARGIN + 3.0 * inch, MARGIN + 6.0 * inch]
    c.setFillColor(ink)
    c.setFont(_FONT_BOLD, 10)
    for i, h in enumerate(headers):
        c.drawString(xs[i], SLIDE_HEIGHT - 2.3 * inch, h)
    c.setStrokeColor(ink)
    c.setLineWidth(1)
    c.line(MARGIN, SLIDE_HEIGHT - 2.45 * inch, SLIDE_WIDTH - MARGIN, SLIDE_HEIGHT - 2.45 * inch)
    y = SLIDE_HEIGHT - 2.75 * inch
    for r in L(ctx["content"], "rows"):
        c.setFillColor(ink)
        c.setFont(_FONT_BOLD, 9.5)
        c.drawString(xs[0], y, str(r.get("name", "")))
        c.setFont(_FONT_REGULAR, 9)
        c.setFillColor(brand(cfg, "ink_soft"))
        c.drawString(xs[1], y, money(str(r.get("limit", ""))))
        c.setFillColor(primary)
        c.setFont(_FONT_BOLD, 9)
        c.drawString(xs[2], y, money(str(r.get("edge", ""))))
        y -= 0.45 * inch

    strap = T(ctx["content"], "strapline", "")
    if strap:
        c.setFillColor(ink)
        c.setFont(_FONT_BOLD, 12)
        c.drawCentredString(SLIDE_WIDTH / 2, 0.4 * inch, strap)


def render_csr_impact(c, ctx):
    cfg = ctx["config"]
    fill_background(c, brand(cfg, "background"))
    chrome(c, ctx)
    section_title(c, ctx, "Impact", "Impact Beyond Profit")
    c.setFillColor(brand(cfg, "primary"))
    c.setFont(_FONT_BOLD, 12)
    c.drawString(MARGIN, SLIDE_HEIGHT - 2.3 * inch, "CSR Alignment")
    c.drawString(SLIDE_WIDTH / 2 + 0.2 * inch, SLIDE_HEIGHT - 2.3 * inch, "SDG Alignment")
    c.setFillColor(brand(cfg, "ink"))
    c.setFont(_FONT_REGULAR, 10)
    y = SLIDE_HEIGHT - 2.6 * inch
    for line in L(ctx["content"], "csr"):
        c.drawString(MARGIN, y, money(line))
        y -= 0.24 * inch
    y = SLIDE_HEIGHT - 2.6 * inch
    for line in L(ctx["content"], "sdg"):
        c.drawString(SLIDE_WIDTH / 2 + 0.2 * inch, y, line)
        y -= 0.24 * inch
    footer = T(ctx["content"], "footer", "")
    if footer:
        c.setFillColor(brand(cfg, "ink_soft"))
        c.setFont(_FONT_ITALIC, 8)
        c.drawString(MARGIN, 0.3 * inch, footer)


def render_why_this_program(c, ctx):
    cfg = ctx["config"]
    fill_background(c, brand(cfg, "background"))
    chrome(c, ctx)
    program = T(ctx["content"], "program", ctx.get("investor", "this program"))
    section_title(c, ctx, "Program Fit", f"Why {program}")
    cards = [(card.get("title", ""), money(card.get("body", "")))
             for card in L(ctx["content"], "cards")[:3]]
    if cards:
        card_row(c, ctx, cards, SLIDE_HEIGHT - 2.4 * inch, 2.0 * inch)


def render_closing(c, ctx):
    cfg = ctx["config"]
    fill_background(c, brand(cfg, "background"))
    chrome(c, ctx)
    primary = brand(cfg, "primary")
    accent = brand(cfg, "accent")
    ink = brand(cfg, "ink")

    cx = SLIDE_WIDTH / 2
    draw_wordmark(c, cx - 1.5 * inch, SLIDE_HEIGHT - 1.3 * inch, 2.4, primary, brand(cfg, "wordmark"))

    vision = L(ctx["content"], "vision_lines")
    c.setFillColor(ink)
    c.setFont(_FONT_BOLD, 22)
    for i, line in enumerate(vision[:2]):
        c.drawCentredString(cx, SLIDE_HEIGHT - 2.5 * inch - i * 0.35 * inch, line)

    headline = T(ctx["content"], "headline", "Let's Build This Together")
    c.setFillColor(ink)
    c.setFont(_FONT_BOLD, 32)
    parts = headline.split()
    if parts:
        # render last word with accent highlight
        last = parts[-1]
        prefix = " ".join(parts[:-1])
        pw = c.stringWidth(prefix + " ", _FONT_BOLD, 32) if prefix else 0
        lw = c.stringWidth(last, _FONT_BOLD, 32)
        total = pw + lw
        start_x = cx - total / 2
        if prefix:
            c.drawString(start_x, SLIDE_HEIGHT - 3.55 * inch, prefix)
        tx = start_x + pw
        draw_accent_bar(c, tx - 0.05 * inch, SLIDE_HEIGHT - 3.6 * inch,
                        lw + 0.1 * inch, 0.5 * inch, accent)
        c.setFillColor(ink)
        c.drawString(tx, SLIDE_HEIGHT - 3.55 * inch, last)

    ask = T(ctx["content"], "ask", "")
    if ask:
        c.setFillColor(ink)
        c.setFont(_FONT_BOLD, 13)
        c.drawCentredString(cx, SLIDE_HEIGHT - 4.2 * inch, ask)

    c.setStrokeColor(primary)
    c.setLineWidth(2)
    c.line(MARGIN, 1.0 * inch, SLIDE_WIDTH - MARGIN, 1.0 * inch)

    contacts = L(ctx["content"], "contacts")[:4]
    col_w = SLIDE_WIDTH / max(len(contacts), 1)
    for i, pair in enumerate(contacts):
        lx = i * col_w + col_w / 2
        c.setFillColor(ink)
        c.setFont(_FONT_BOLD, 9)
        c.drawCentredString(lx, 0.7 * inch, str(pair[0]))
        c.setFont(_FONT_REGULAR, 9)
        c.drawCentredString(lx, 0.5 * inch, str(pair[1]))


# ============================================================================
# Dispatch
# ============================================================================
SLIDE_RENDERERS = {
    "cover": render_cover,
    "about_company": render_about_company,
    "problem": render_problem,
    "problem_stakeholders": render_problem_stakeholders,
    "solution": render_solution,
    "product": render_product,
    "tech_core": render_tech_core,
    "tech_deep": render_tech_deep,
    "traction": render_traction,
    "distribution": render_distribution,
    "market": render_market,
    "business_model": render_business_model,
    "revenue_trajectory": render_revenue_trajectory,
    "why_team": render_why_team,
    "use_of_funds": render_use_of_funds,
    "milestones": render_milestones,
    "why_invest_now": render_why_invest_now,
    "competitive_landscape": render_competitive_landscape,
    "csr_impact": render_csr_impact,
    "why_this_program": render_why_this_program,
    "closing": render_closing,
}

DEFAULT_SLIDES = [
    "cover", "problem", "solution", "product", "tech_core", "distribution",
    "traction", "market", "business_model", "why_team", "why_invest_now", "closing",
]


def build_deck(config, output_path):
    slides = config.get("slides") or DEFAULT_SLIDES
    unknown = [s for s in slides if s not in SLIDE_RENDERERS]
    if unknown:
        raise ValueError(f"Unknown slide id(s): {unknown}. Valid: {sorted(SLIDE_RENDERERS)}")
    content = config.get("content", {})
    c = canvas.Canvas(str(output_path), pagesize=PAGE_SIZE)
    total = len(slides)
    for i, slide_id in enumerate(slides, 1):
        ctx = {
            "config": config,
            "content": content.get(slide_id, {}),
            "num": i,
            "total": total,
            "investor": config.get("investor", ""),
            "audience": config.get("audience_type", "strategic_investor"),
        }
        SLIDE_RENDERERS[slide_id](c, ctx)
        c.showPage()
    c.save()
    return output_path


def slugify(name):
    return re.sub(r"[^a-z0-9]+", "-", str(name).lower()).strip("-") or "deck"


def main():
    ap = argparse.ArgumentParser(description="Generate a branded pitch deck PDF")
    ap.add_argument("--config", help="JSON config file")
    ap.add_argument("--config-json", help="JSON config as a string")
    ap.add_argument("--output", help="Output PDF path (default: ./output/<slug>.pdf)")
    ap.add_argument("--font-info", action="store_true",
                    help="Print resolved font + rupee support and exit")
    args = ap.parse_args()

    if args.font_info:
        print(json.dumps({"regular": _FONT_REGULAR, "bold": _FONT_BOLD,
                          "italic": _FONT_ITALIC, "rupee_ok": RUPEE_OK}))
        return

    if args.config:
        config = json.loads(Path(args.config).read_text())
    elif args.config_json:
        config = json.loads(args.config_json)
    else:
        print(json.dumps({"error": "Pass --config or --config-json"}), file=sys.stderr)
        sys.exit(1)

    out = Path(args.output) if args.output else \
        Path("output") / f"{slugify(config.get('investor', 'deck'))}.pdf"
    out.parent.mkdir(parents=True, exist_ok=True)

    try:
        build_deck(config, out)
    except ValueError as e:
        print(json.dumps({"error": str(e)}), file=sys.stderr)
        sys.exit(1)

    print(json.dumps({
        "ok": True, "output": str(out),
        "slides": len(config.get("slides") or DEFAULT_SLIDES),
        "investor": config.get("investor"),
        "audience": config.get("audience_type"),
        "font": _FONT_REGULAR, "rupee_ok": RUPEE_OK,
    }))


if __name__ == "__main__":
    main()
