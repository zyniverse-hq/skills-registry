---
name: investor-deck-builder
description: Generate a tailored, branded investor pitch deck PDF for a specific investor or program, with audience-selected slides and content driven entirely from a single facts file — no numbers hardcoded.
version: 1.0.0
author: Sarang T S
email: sarang@testmyskills.ai
category: business-sales
tags:
  - pitch-deck
  - fundraising
  - investor-relations
  - pdf-generation
  - reportlab
product: zyniverse
sprint: 1
tested_with: claude-opus-4-7
---

# Investor Deck Builder

> Produce an on-brand PDF pitch deck for any investor / accelerator / grant — the right slides for the audience, populated from a single facts file so it never drifts from your filled application.

## When to use

- Activate when: the user asks for a tailored deck for a specific investor / accelerator / grant / pitch event.
- Activate when: the user just finished filling an application via `investor-form-filler` and wants the matching deck.
- Activate phrases: "build a deck for `<investor>`", "generate the pitch deck for `<program>`", "tailor the deck for `<audience>`".
- Do NOT activate for: editing an existing deck slide-by-slide, customer-facing sales decks, or decks unrelated to investor outreach.

## Prerequisites

- [ ] A `company-facts.md` — the **same source of truth** the form-filler uses. The deck and form never drift because both read this one file.
- [ ] A `references/slide-library.md` describing each slide's structure with a stable `snake_case` slide ID.
- [ ] A `references/slide-selection-rules.md` mapping audience type → ordered slide-ID list.
- [ ] *(Optional)* An `investor-tuning.md` with per-investor adjustments.
- [ ] Python 3.9+ with `reportlab` installed (use a venv — PEP 668 blocks system pip on most Macs/Linux).
- [ ] A `₹`-capable system font for rupee figures: DejaVu (Linux), `Helvetica.ttc` (macOS), Arial (Windows). The generator auto-resolves and degrades `₹`→`Rs ` if none qualifies.

## Steps

### Step 1: Confirm investor + audience type

Get the investor name and infer the audience type (or ask). Five common types and a target slide count:

| Audience type | Target slides |
|---|---|
| Strategic Pre-Seed Investor | 12–13 |
| Accelerator / Residency | 9 |
| Government Grant (regional) | 11–12 |
| Deeptech Grant | 11–12 |
| Pitching Event / Demo Day | 8–9 |

If the user just ran the form-filler for the same investor, reuse that investor snapshot — don't re-research.

### Step 2: Pick the slide list

Open `slide-selection-rules.md` and pull the ordered list of `snake_case` slide IDs for the audience type. Every ID must exist in `slide-library.md` and have a matching renderer in the generator. An unknown ID is a hard error — never a blank "not implemented" slide.

### Step 3: Build the config

For each slide in your selected list:
- Pull the structure from `slide-library.md`.
- Pull the numbers from `company-facts.md`.
- Build a JSON config:

```json
{
  "investor": "<Investor Name>",
  "audience_type": "strategic_investor",
  "presenter": "<Name & Role>",
  "cover_subtitle": "<one-line positioning>",
  "cover_footer": "<round / program label>",
  "brand": {
    "primary":   "#000000",
    "accent":    "#FFD400",
    "background":"#FFFFFF",
    "ink":       "#1A1A1A"
  },
  "slides": ["cover", "problem", "solution", "..."],
  "content": {
    "<slide_id>": { "...slide-specific fields, all numbers..." }
  }
}
```

**Rule:** the generator hardcodes **zero** business numbers. Every figure flows `company-facts.md` → Claude reads → config JSON → generator. A missing number renders a visible `—` placeholder — never a stale or wrong value.

### Step 4: Tune for the specific investor

Apply any block from `investor-tuning.md`:
- Adjust cover subtitle and footer for the round/program label.
- Tune the "Why Invest Now" / "Why This Program" anchor.
- Swap which traction proof points lead (B2B-first for VCs, impact-first for grants, founder-first for accelerators).
- Adjust the ask framing (equity terms for VCs, milestones for grants, no ask for events).

### Step 5: Run the generator

```bash
python3 scripts/generate_deck.py --config /tmp/deck-config.json
# → ./output/<investor-slug>.pdf
```

The generator:
1. Resolves a cross-platform `₹`-capable font (verified by checking the font's `charToGlyph` for U+20B9).
2. Lays out each slide at 16:9 (10" × 5.625").
3. Pulls all content from the config; brand colors from `config.brand`.
4. Writes a PDF and prints JSON: `{"ok": true, "output": "...", "slides": N, "font": "...", "rupee_ok": true|false}`.

If `rupee_ok` is `false`, flag it — the deck shows "Rs " instead of `₹`.

### Step 6: Cross-check with the form

If the form-filler ran earlier in this session for the same investor, confirm:
- Numbers in the deck match numbers in the form.
- "Why now" framing matches.
- Ask is consistent.

If there's a mismatch, fix the deck (the form is usually the primary deliverable; the deck supports it). Then run your project's `check_consistency.py` drift guard.

### Step 7: Offer next steps

1. **Matching application?** — run the companion `investor-form-filler` skill.
2. **Add an investor-tuning block** for this investor so the next deck stays consistent.
3. **Different investor on your shortlist?** — re-run with a new investor name and tuning.

## Output

- **Format:** 16:9 PDF (10" × 5.625"), one slide per page.
- **Location:** `output/<investor-slug>.pdf`.
- **Example:** see the "Example" section below.

## Example

**User says:** *"Build a tailored deck for `<Investor>` — strategic pre-seed."*

**Claude does:**
1. Looks up the 12–13 slide ID list for `strategic_investor` in `slide-selection-rules.md`.
2. Reads `company-facts.md` for every number and `slide-library.md` for slide structure.
3. Applies any `<Investor>` block in `investor-tuning.md`.
4. Builds a content config, runs `generate_deck.py --config ...`.
5. Reports the output path, slide count, resolved font, and `rupee_ok` flag.

**Result:** a branded PDF at `output/<investor-slug>.pdf`, ready to attach to a cover email or upload to DocSend.

## Generator design rules (read before editing)

- **Layout lives in the generator. Numbers do not.** Every business figure (revenue, ask, market sizes, traction stats) reads from the JSON config. Missing → visible `—` placeholder.
- **Static brand copy** (slide headlines, taglines) is OK to bake in — it's not a drift-prone number.
- **Cross-platform fonts.** Font resolver tries Linux → macOS → Windows candidates in order; verifies `₹` glyph at registration time; degrades to `Rs ` gracefully if no font qualifies.
- **Stable slide-ID vocabulary** matching `slide-library.md`, `slide-selection-rules.md`, and the JSON config's `slides` array. Unknown ID raises — never silently fallback.
- **Brand identity from config**, not from constants. The same generator must work for any company — pass `config.brand.primary` / `.accent` / `.background` / `.ink`.

## Honesty constraints — apply to every slide

- **Use only canonical numbers** from `company-facts.md`. No invented metrics.
- **Never overclaim partnerships** — list only verified relationships.
- **Patent status** — be exact: "application to be filed" vs "filed" vs "granted".
- **B2B customer names** — describe by count and category unless cleared.
- **Diligence content never appears on slides** — no cap-table risk acknowledgments, no SISFS/grant gap detail, etc.

## Failure modes to avoid

1. **Generic deck that could be any startup** — every slide should carry specifics from `company-facts.md`.
2. **Inconsistency with the form** — if the form says X, the deck must too. Run the consistency check.
3. **Wrong slide list for the audience** — strategic investors don't need TRL slides; grants don't need 3-year valuation projections; pitching events skip dense financials.
4. **Bloated slide count** — the library is the menu, not the deck. 9–13 slides per audience.
5. **Surfacing diligence content on slides** — never include cap-table risk on a slide.
6. **Hardcoding numbers in Python** — every business number must be passed via config.

## Notes

- Pairs with **investor-form-filler** — both read the same `company-facts.md`. That's the consistency anchor.
- Add a `scripts/check_consistency.py` drift guard at the project root. It should fail if a stale value reappears anywhere, if `company-facts.md` is missing a canonical anchor, or if a slide ID in any config doesn't exist in `SLIDE_RENDERERS`.
- Include a `scripts/md_to_pdf.py` helper to convert filled applications (markdown) into branded PDFs for emailing.
- For full output integrity, also verify the generated PDF embeds `₹` by extracting text with `pypdf` and grepping for the glyph.
