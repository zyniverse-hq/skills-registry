# ANALYSIS — investor-deck-builder

> Generated against the [agentskills.io](https://agentskills.openml.io) standard.

---

## Overall Verdict

**Partially compliant.** The content quality is strong — a well-scoped 7-step workflow with audience-type classification, a config-driven design that keeps all numbers in `company-facts.md`, honesty constraints, and explicit failure modes. The bundled `scripts/generate_deck.py` and `references/` files are correctly structured. The structural issues are: eight custom frontmatter fields at the wrong level (must be under `metadata:`), missing `license`, and missing `compatibility` (the skill has hard Python/reportlab dependencies). Body is compact and well under budgets.

---

## Spec Compliance Checklist

| Check | Status | Detail |
|---|---|---|
| `name` field format | ✅ PASS | `investor-deck-builder` — 21 chars, lowercase + hyphens, no leading/trailing/consecutive hyphens, matches folder name |
| `description` present & non-empty | ✅ PASS | Present, ~175 chars, under 1024 limit |
| `description` describes what it does | ✅ PASS | Clearly describes the PDF pitch deck generation with audience selection |
| `description` describes when to use it | ⚠️ WARN | Activate phrases are in the body's When to use section but not surfaced in the description itself for agent discovery |
| `license` field | ❌ FAIL | Not present |
| `compatibility` field | ❌ FAIL | Hard dependencies on Python 3.9+, `reportlab`, and a `₹`-capable system font — none declared |
| `metadata` field structure | ❌ FAIL | 8 custom fields at top level (`version`, `author`, `email`, `category`, `tags`, `product`, `sprint`, `tested_with`) — must be nested under `metadata:` |
| `allowed-tools` field | — | Not present (optional, experimental — acceptable to omit) |
| Token budget (body) | ✅ PASS | ~157 body lines × ~55 chars ≈ ~8,635 chars ÷ 4 ≈ ~2,159 tokens — well under the 5000-token recommendation |
| Line budget (body) | ✅ PASS | ~157 body lines — well under the 500-line recommendation |
| `scripts/` directory | ✅ PASS | `scripts/generate_deck.py` is bundled inside the skill folder |
| `references/` directory | ✅ PASS | `references/slide-library.md` and `references/slide-selection-rules.md` are referenced and bundled |
| `assets/` directory | ✅ PASS | Not needed |
| Body — step-by-step instructions | ✅ PASS | Steps 1–7 clearly numbered with decision tables and config schema |
| Body — examples | ✅ PASS | Dedicated Example section with user trigger → Claude action → result |
| Body — edge cases | ✅ PASS | Failure modes section covers 6 common mistakes; generator design rules; honesty constraints |

---

## What the Skill Gets Right

- **Config-driven design** — zero business numbers hardcoded in the generator; every figure flows `company-facts.md` → Claude → config JSON → generator; missing numbers render a visible `—` placeholder rather than silently failing
- **Audience-type classification table** — 5 audience types with target slide counts; prevents bloated or under-scoped decks for the wrong venue
- **Bundled `scripts/generate_deck.py`** — the script lives inside the skill folder; the skill is self-contained for the generation step
- **Cross-platform font resolver** — graceful `₹` → `Rs ` degradation is explicitly documented; prevents silent font failures on CI/Windows/Linux
- **Honesty constraints section** — explicit rules about canonical numbers only, patent status precision, B2B customer anonymisation; protects the user from investor-deck credibility issues
- **Companion skill workflow** — clear integration with `investor-form-filler`; both read from `company-facts.md` as single source of truth, preventing drift between the form and the deck
- **`references/` properly split** — slide library and selection rules are large reference artifacts that don't belong inline; the body stays compact by delegating to them

---

## Violations (Must Fix)

### 1. Eight non-standard top-level frontmatter fields

The spec defines exactly six frontmatter keys: `name`, `description`, `license`, `compatibility`, `metadata`, `allowed-tools`. All other custom fields must be nested under `metadata:` as string key-value pairs.

**Current (wrong):**
```yaml
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
```

**Fix — move all under `metadata:` (values must be strings):**
```yaml
metadata:
  version: "1.0.0"
  author: Sarang T S
  email: sarang@testmyskills.ai
  category: business-sales
  tags: "pitch-deck, fundraising, investor-relations, pdf-generation, reportlab"
  product: zyniverse
  sprint: "1"
  tested_with: claude-opus-4-7
```

---

### 2. Missing `compatibility` field

This skill requires Python 3.9+, the `reportlab` library, and a font with Unicode Rupee glyph support. Without declaring these, users on minimal environments will encounter failures only when `generate_deck.py` runs.

**Add:**
```yaml
compatibility: >
  Requires Python 3.9+ with reportlab installed (pip install reportlab).
  Use a venv — PEP 668 blocks system pip on most Macs/Linux.
  Needs a ₹-capable system font: DejaVu (Linux), Helvetica.ttc (macOS),
  Arial (Windows). Designed for Claude Code on macOS/Linux/Windows.
  Depends on bundled scripts/generate_deck.py and references/slide-library.md,
  references/slide-selection-rules.md, and a project-level company-facts.md.
```

---

### 3. Missing `license` field

No license is declared.

**Add:**
```yaml
license: Proprietary — internal use only (testmyskills.ai / zyniverse)
```

---

## What's More Than Needed (Consider Restructuring)

### Generator design rules section adds length without being step guidance

The "Generator design rules (read before editing)" section is targeted at developers editing `generate_deck.py`, not at agents executing the skill workflow. Consider moving this to a `references/generator-design.md` so it's available when needed without consuming body budget.

### `scripts/md_to_pdf.py` and `scripts/check_consistency.py` mentioned in Notes but not bundled

The Notes section references two additional scripts (`check_consistency.py`, `md_to_pdf.py`) as recommendations. If these are needed for the skill to fully work, they should either be bundled or removed from the Notes. If they are optional companion scripts, clarify that they are not part of the core skill.

---

## What's Missing (Must Add)

### 1. `license` field
See Violations above.

### 2. `compatibility` field
See Violations above. Python + reportlab + font requirements should be declared.

### 3. Trigger keywords in `description`

The body has good activate phrases ("build a deck for `<investor>`", "generate the pitch deck for `<program>`") but they don't appear in the `description` where agent discovery happens.

**Current:**
```yaml
description: Generate a tailored, branded investor pitch deck PDF for a specific investor or program, with audience-selected slides and content driven entirely from a single facts file — no numbers hardcoded.
```

**Improved:**
```yaml
description: >
  Generate a tailored, branded investor pitch deck PDF for a specific investor or
  program. Use when the user says "build a deck for <investor>", "generate the pitch
  deck for <program>", "tailor the deck for <audience>", or just finished filling
  an application via investor-form-filler. Selects the right slides for the
  audience type (strategic investor, accelerator, grant, demo day), populates all
  content from company-facts.md, and runs generate_deck.py to produce a 16:9 PDF.
```

---

## Summary Table

| Area | Status | Detail |
|---|---|---|
| `name` field | ✅ Pass | Valid format, matches folder name |
| `description` field | ⚠️ Warn | Clear and accurate; activate phrases are in body but not in description for discovery |
| `license` field | ❌ Missing | Not declared |
| `compatibility` field | ❌ Missing | Hard deps on Python 3.9+, reportlab, system font — none declared |
| `metadata` structure | ❌ Wrong | 8 custom fields at top level; must nest under `metadata:` |
| Token budget | ✅ Pass | ~2,159 tokens — well under the 5000-token limit |
| Line budget | ✅ Pass | ~157 body lines — well under 500-line limit |
| `scripts/` bundled | ✅ Pass | `generate_deck.py` bundled inside skill folder |
| `references/` split | ✅ Pass | Slide library and selection rules are properly split into reference files |
| Body structure | ✅ Good | Step-by-step, config schema, examples, honesty constraints, failure modes |
| Self-containment / portability | ⚠️ Partial | Scripts bundled; but `company-facts.md` and `investor-tuning.md` are project-level deps not bundled in skill |
