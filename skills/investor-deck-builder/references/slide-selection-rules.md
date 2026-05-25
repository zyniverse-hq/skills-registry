# Slide Selection Rules

Maps audience type → ordered list of **canonical slide IDs** (the same IDs used in `slide-library.md`, the JSON config's `slides` array, and `generate_deck.py`'s `SLIDE_RENDERERS`). Use this AFTER identifying the audience type from `tone-by-audience.md`.

The `slides` array you build is exactly the `Slide ID` column, top to bottom.

---

## 1. Strategic Pre-Seed Investor — 12 slides

For generalist pre-seed funds, angel networks, founder syndicates.

| # | Slide ID | Notes |
|---|---|---|
| 1 | `cover` | Footer = "<round-name> · <ask-summary>" |
| 2 | `problem` | The macro pain (single stat) |
| 3 | `solution` | Positioning + tagline |
| 4 | `product` | The verticals / modules |
| 5 | `tech_core` | High-level moat, skip deep tech |
| 6 | `distribution` | The capital-efficiency / GTM story |
| 7 | `traction` | Lead with B2B numbers if you have them |
| 8 | `market` | TAM / SAM / SOM |
| 9 | `business_model` | Revenue streams |
| 10 | `why_team` | Founders + advisors |
| 11 | `why_invest_now` | Three reasons |
| 12 | `closing` | Ask + contacts |

**If you must shorten:** drop `product` first, then `business_model`. Don't drop `traction`.

---

## 2. Accelerator / Residency — 9 slides

For founder residencies, sector accelerators, cohort programs.

| # | Slide ID | Notes |
|---|---|---|
| 1 | `cover` | Footer = "For `<Program Name>` · `<Year>`" |
| 2 | `problem` | |
| 3 | `solution` | |
| 4 | `why_team` | Lead with founder strength — most important slide here |
| 5 | `tech_core` | High-level |
| 6 | `traction` | |
| 7 | `distribution` | |
| 8 | `why_this_program` | Tuned per program — what about THEIR program specifically? |
| 9 | `closing` | Vision-led; ask is "capital + network + operator support" |

---

## 3. Government Grant — 12 slides

For state innovation funds, AICTE-linked programs, central-government schemes, CSR-linked grants.

| # | Slide ID | Notes |
|---|---|---|
| 1 | `cover` | Subtitle / footer includes region (e.g. "Built in `<City>`") |
| 2 | `about_company` | CIN, address — formal requirement |
| 3 | `problem` | |
| 4 | `solution` | |
| 5 | `tech_core` | |
| 6 | `traction` | Include region-specific traction |
| 7 | `market` | |
| 8 | `business_model` | |
| 9 | `milestones` | Months 1-6 + Months 7-12 |
| 10 | `use_of_funds` | |
| 11 | `csr_impact` | Critical for CSR-linked grants |
| 12 | `closing` | "Thank You" variant; no equity ask |

---

## 4. Deeptech Grant — 11 slides

For deeptech-specific funds (BIRAC, NIDHI-PRAYAS, DST schemes, state deeptech).

| # | Slide ID | Notes |
|---|---|---|
| 1 | `cover` | Footer = "Deeptech R&D Round" |
| 2 | `about_company` | Formal requirement |
| 3 | `problem` | |
| 4 | `solution` | |
| 5 | `tech_core` | Lead with technical depth |
| 6 | `tech_deep` | Full algorithm / framework breakdown; patent status in footer |
| 7 | `traction` | Frame as TRL progression |
| 8 | `why_team` | Highlight R&D credentials |
| 9 | `use_of_funds` | R&D-heavy allocation (e.g. 40%+ to R&D) |
| 10 | `milestones` | Critical for grants |
| 11 | `closing` | "Thank You" variant |

---

## 5. Pitching Event / Demo Day — 9 slides

For demo days, pitching contests, ecosystem festivals.

| # | Slide ID | Notes |
|---|---|---|
| 1 | `cover` | Presenter line picks the person actually pitching |
| 2 | `problem_stakeholders` | More memorable than the single-stat problem |
| 3 | `solution` | Strong analogy / single-sentence positioning |
| 4 | `product` | |
| 5 | `tech_core` | Light version — one line on moat |
| 6 | `distribution` | |
| 7 | `traction` | |
| 8 | `competitive_landscape` | "We built the full stack" type closer |
| 9 | `closing` | Vision-led, no ask, no terms |

---

## How to choose audience type

```
Is it a government scheme / state grant?
├── YES, deeptech focus (BIRAC, NIDHI-PRAYAS, state deeptech)   → Deeptech Grant
└── YES, general (state innovation, AICTE, CSR grants)          → Government Grant

Is it a 3-week+ residency / accelerator program?               → Accelerator / Residency
Is it a pitching event / demo day with an audience?            → Pitching Event
Otherwise (VC, angel, syndicate, family office)                → Strategic Pre-Seed Investor
```

**If unclear, ask the user.**

---

## Slide ordering principles

- **Always** start with the problem, end with `closing`.
- **Investors:** problem → solution → product → moat → distribution → traction → market → model → team → why-now → ask.
- **Grants:** problem → solution → impact → tech → traction → plan → milestones → CSR/SDG.
- **Accelerators:** problem → solution → team → tech → traction → program-fit.
- **Pitching events:** problem → solution → product → moat → distribution → traction → vision.

---

## When to deviate

Override the default selection if:
- The user explicitly asks for a specific slide ("include `tech_deep`")
- The audience has unusual emphasis (a generalist VC known for deeptech — borrow `tech_deep`)
- There's a strict slide limit (organiser says 5 max → `cover`, `problem`, `solution`, `traction`, `closing`)

When deviating, log it in the response: *"Adjusted slide list because <reason>."* Every ID you choose must exist in `slide-library.md` — an unknown ID makes `generate_deck.py` error out.
