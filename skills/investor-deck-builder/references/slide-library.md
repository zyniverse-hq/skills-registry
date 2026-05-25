# Slide Library

Structure and content schema for every standard slide. The deck-builder selects from this library based on audience type (see `slide-selection-rules.md`), then populates each slide from a JSON config built from `company-facts.md`.

> **Numbers are passed via config — never baked into `slide-library.md` or the generator.** This file describes *what fields each slide expects*. Missing fields render as a visible `—` placeholder.

## Slide ID reference

Every slide has a stable `snake_case` ID. These IDs are the contract between this file, `slide-selection-rules.md`, the JSON config's `slides` array, and `generate_deck.py`'s `SLIDE_RENDERERS`.

| ID | Slide | Common audiences |
|---|---|---|
| `cover` | Cover | all |
| `about_company` | About the Company (formal entity details) | grants, formal applications |
| `problem` | The Problem (single-stat) | all |
| `problem_stakeholders` | The Problem — 3-stakeholder pain | strategic, events |
| `solution` | Solution + positioning | all |
| `product` | Product overview (verticals / modules) | all |
| `tech_core` | Tech / AI core (3-pillar moat) | all |
| `tech_deep` | Tech deep-dive (algorithm / framework detail) | deeptech grants |
| `traction` | Traction (4-stat strip + testimonial) | all |
| `distribution` | Distribution advantage / GTM | strategic, events |
| `market` | Market opportunity (TAM/SAM/SOM) | strategic, grants |
| `business_model` | Business model / pricing | strategic, grants |
| `revenue_trajectory` | 3-year revenue trajectory | strategic, deeptech |
| `why_team` | Why this team (founders + advisors) | all |
| `use_of_funds` | Use of funds (allocation) | strategic, grants |
| `milestones` | Project milestones (2-column timeline) | grants |
| `why_invest_now` | Why invest now (3 reasons) | strategic |
| `competitive_landscape` | Competitive landscape (table) | strategic, events |
| `csr_impact` | CSR / SDG impact alignment | government grants |
| `why_this_program` | Why this program (3 reasons) | accelerators |
| `closing` | Closing (vision + ask + contacts) | all |

**21 slide IDs.** Every ID must have a renderer in `generate_deck.py`. An unknown ID makes the generator error out — there are no blank "renderer not implemented" slides.

---

## Content schema per slide

What `config.content.<slide_id>` should contain. Anything marked **required** must come from `company-facts.md`. Anything marked *optional* has a sensible default in the renderer.

### `cover`

Pulls top-level config fields, not `content.cover`:
- `investor` (required) — used in footer
- `presenter`, `presenter_role` (required)
- `cover_subtitle` (required) — positioning line
- `cover_footer` (required) — round/program label

### `about_company`

```json
{
  "company": "<Legal entity name>",
  "website": "<https://...>",
  "address": "<...>",
  "contact": "<email · phone>",
  "doi": "<date of incorporation>",
  "cin": "<CIN / registration number>",
  "directors": [{"name": "<>", "din": "<>", "shares": "<>"}]
}
```

### `problem`

```json
{
  "headline": "<single big headline, e.g. 'Certificates != Competence'>",
  "body": ["<line 1>", "<line 2>", "<line 3>"],
  "stat": "<single highlighted statistic with source>",
  "source": "<source citation>"
}
```

### `problem_stakeholders`

Three stakeholder rows, each with title + a one-line quote + a one-line detail:

```json
{
  "rows": [
    {"title": "<Stakeholder 1>", "quote": "<their pain>", "detail": "<context>"},
    {"title": "<Stakeholder 2>", "quote": "<>",            "detail": "<>"},
    {"title": "<Stakeholder 3>", "quote": "<>",            "detail": "<>"}
  ],
  "gap_line": "<bottom synthesis line>"
}
```

### `solution`

```json
{
  "tagline": "<Your 'X for Y' positioning line>",
  "body": ["<paragraph 1>", "<paragraph 2>"],
  "pills": ["<benefit 1>", "<benefit 2>", "<benefit 3>"],
  "image_caption": "<text shown in the placeholder image area>"
}
```

### `product`

2×2 grid of product cards:

```json
{
  "subtitle": "<one line under the headline>",
  "cards": [
    {"title": "<Vertical 1>", "body": "<short description>"},
    {"title": "<Vertical 2>", "body": "<>"},
    {"title": "<Vertical 3>", "body": "<>"},
    {"title": "<Vertical 4>", "body": "<>"}
  ],
  "roadmap_line": "<optional italic line at the bottom>"
}
```

### `tech_core`

3 pillar cards:

```json
{
  "pillars": [
    {"title": "<Pillar 1>", "body": "<one paragraph>"},
    {"title": "<Pillar 2>", "body": "<>"},
    {"title": "<Pillar 3>", "body": "<>"}
  ],
  "strapline": "<bottom one-liner — your moat in one sentence>"
}
```

### `tech_deep` *(deeptech grants only)*

Multi-pill flow describing the proprietary algorithm/framework:

```json
{
  "subtitle": "<framework name + tagline>",
  "pills": [
    {"label": "<Step name>", "body": "<one-line description>"},
    "... up to ~6 ..."
  ],
  "patent_status": "<e.g. 'Application to be filed'>",
  "definitions": "<glossary of acronyms used>"
}
```

### `traction`

Bottom dark stat strip + a testimonial card above:

```json
{
  "stats": [
    {"big": "<value>", "label": "<short label>", "detail": "<one-line context>"},
    "... 4 stats total ..."
  ],
  "testimonial": {"quote": "<user/customer quote>", "author": "<name or role>"}
}
```

### `distribution`

Stakeholder distribution table:

```json
{
  "headline": "Distribution Advantage",
  "rows": [
    {"stakeholder": "<>", "gets_free": "<>", "pays_for": "<>", "brings": "<>", "is_revenue": false},
    "...",
    {"stakeholder": "<End users>", "gets_free": "<>", "pays_for": "<>", "brings": "REVENUE", "is_revenue": true}
  ],
  "strapline": "<bottom synthesis line>"
}
```

### `market`

3 segment pyramids + bottom totals:

```json
{
  "pyramids": [
    {
      "title": "<Segment 1>",
      "tam": "<value\\n+ source>",
      "sam": "<value\\n+ source>",
      "som": "<value>"
    },
    "... 3 segments ..."
  ],
  "total_line": "<TAM ... · SAM ... · SOM Year 1 ...>",
  "sources": "<comma-separated source list>"
}
```

### `business_model`

4 revenue-stream cards:

```json
{
  "cards": [
    {"title": "<Stream 1>", "body": "<pricing / mechanics>"},
    "... 4 streams ..."
  ],
  "synthesis_line": "<one-line distribution insight>"
}
```

### `revenue_trajectory`

Trajectory headline + supporting highlights + 3-year bars:

```json
{
  "trajectory": "<Y0 → Y1 → Y2 → Y3>",
  "highlights": ["<conversion improvement>", "<ticket size improvement>", "<mix shift>"],
  "bars": [["Y1", <number>], ["Y2", <number>], ["Y3", <number>]]
}
```

### `why_team`

Founder cards + advisor list:

```json
{
  "founders": [
    {"name": "<>", "role": "<>", "bio": "<one short paragraph>"},
    "... up to 3 ..."
  ],
  "advisors": [
    {"name": "<>", "role": "<role · affiliation>"},
    "... up to 4 ..."
  ],
  "banner_line": "<one-line synthesis: 'Why this team' summary>"
}
```

### `use_of_funds`

Ask line + allocation bars:

```json
{
  "headline": "Funding Requirements",
  "body": "<one paragraph explaining the round>",
  "allocation": [
    {"label": "<Bucket 1>", "pct": <number>},
    "... up to ~8 ..."
  ]
}
```

### `milestones`

2-column timeline:

```json
{
  "m1": {"title": "<Months 1-6 phase>", "items": ["<>", "<>"]},
  "m2": {"title": "<Months 7-12 phase>", "items": ["<>", "<>"]}
}
```

### `why_invest_now`

3 reason cards on a banner:

```json
{
  "reasons": [
    {"title": "<Reason 1>", "body": "<paragraph>"},
    {"title": "<Reason 2>", "body": "<>"},
    {"title": "<Reason 3>", "body": "<>"}
  ]
}
```

### `competitive_landscape`

Comparison table:

```json
{
  "rows": [
    {"name": "<Competitor 1>", "limit": "<their limitation>", "edge": "<your edge>"},
    "..."
  ],
  "strapline": "<bottom synthesis>"
}
```

### `csr_impact` *(government grants only)*

Two-column CSR + SDG list:

```json
{
  "csr": ["<CSR clause 1>", "<bullet>", "<CSR clause 2>", "<bullet>"],
  "sdg": ["<SDG 1>", "<SDG 2>", "<SDG 3>"],
  "footer": "<source citation>"
}
```

### `why_this_program` *(accelerators only)*

```json
{
  "program": "<Program name>",
  "cards": [
    {"title": "What we need", "body": "<>"},
    {"title": "Why us for you", "body": "<>"},
    {"title": "The mutual win", "body": "<>"}
  ]
}
```

### `closing`

```json
{
  "vision_lines": ["<line 1>", "<line 2>"],
  "headline": "Let's Build This Together",
  "ask": "<one-line ask — e.g. amount · pre-money · dilution · instrument>",
  "contacts": [
    ["Website:", "<url>"],
    ["Phone:",   "<>"],
    ["Email:",   "<>"]
  ]
}
```

---

## Brand configuration

The generator pulls brand colors from `config.brand` (with neutral fallbacks). Pass your real brand here:

```json
{
  "brand": {
    "primary":    "#XXXXXX",
    "accent":     "#XXXXXX",
    "background": "#XXXXXX",
    "ink":        "#1A1A1A",
    "ink_soft":   "#5C544A",
    "wordmark":   "<your lowercase wordmark text>"
  }
}
```

If `brand` is omitted, the generator falls back to a neutral monochrome palette.

---

## How the deck-builder uses this file

For each slide in the selected list (from `slide-selection-rules.md`):
1. Pull the structure described above.
2. Build a `content.<slide_id>` block in the config, filled from `company-facts.md` + any investor-tuning overrides.
3. Pass the full config to `generate_deck.py`.
4. The renderer reads `content.<slide_id>.<field>` for every value; missing → visible `—`.
