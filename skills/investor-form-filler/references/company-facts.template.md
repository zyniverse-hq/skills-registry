# company-facts.md — Template

> Copy this file to your **project root** as `company-facts.md` and fill in your real
> numbers. This is the single source of truth the form-filler (and the companion
> deck-builder) read at run time. **Numbers live here and nowhere else.**

If any other file ever disagrees with this one, **this file wins** — that's the rule.
A drift-guard script (see your project's `scripts/check_consistency.py`) enforces it.

---

## Company

- **Legal name:** `<Legal Entity Name>`
- **Operating brand:** `<Brand Name>`
- **Website:** `<https://...>`
- **Incorporation:** `<date>`
- **CIN / registration number:** `<...>`
- **Registered address:** `<...>`
- **Domain / sector:** `<e.g. EdTech, FinTech, HealthTech>`

---

## One-line description

> `<One sentence: what you do and the outcome for the user. No buzzwords.>`

## Positioning shorthand

> `<Your "X for Y" line, if any.>`
> `<A second positioning line, e.g. "category-defining" framing.>`

---

## Founders & team

| Name | Role | Background |
|---|---|---|
| `<Name>` | `<Role>` | `<Brief background — prior shipping, education, domain depth.>` |
| `<Name>` | `<Role>` | `<...>` |
| `<Name>` | `<Role>` | `<...>` |

**Team size:** `<N>` people total — `<X>` founders + `<Y>` employees. *State the real number — never round up.*

**Advisory board (only verified):**
- `<Name>` — `<Role>` — `<Affiliation>`
- ...

---

## Canonical numbers (current snapshot)

> Use these in **every** output. If an old deck or doc has different numbers, this file wins.

| Metric | Value |
|---|---|
| `<Top-line user metric>` | `<value>` |
| `<Revenue (period)>` | `<value, with growth rate>` |
| `<Rating / NPS / quality metric>` | `<value, source>` |
| `<Customer count (B2B / B2C)>` | `<value>` |
| `<Revenue streams>` | `<count and short list>` |
| `<Social / reach metrics>` | `<value>` |
| `<Team>` | `<count, structure>` |

---

## Current ask

| | |
|---|---|
| **Raise** | `<amount in words + numerals>` |
| **Pre-money** | `<amount>` |
| **Dilution** | `<%>` |
| **Runway funded** | `<months, scenario>` |
| **Instrument** | `<SAFE / CCPS / equity / other>` |
| **Target investors** | `<who you want: thesis, type, what they bring>` |

**Non-dilutive backing already secured (only what's on books):**
- `<Source>` — `<amount>` — `<status>`
- ...

---

## Product

`<2–3 sentences describing what users actually get.>`

**Verticals / modules:**
1. `<Vertical>` — `<what it does>`
2. `<...>`
3. `<...>`

---

## Technology

- **Stack:** `<languages, frameworks, infra>`
- **AI / ML:** `<approach, model providers, key techniques>`
- **Data:** `<storage, scale, proprietary advantage>`

---

## Moat

`<2–3 distinct barriers that make you hard to copy.>`

1. **`<Barrier 1>`** — `<concrete description>`
2. **`<Barrier 2>`** — `<concrete description>`
3. **`<Barrier 3>`** — `<concrete description>`

---

## Market

- **TAM:** `<value, top-down or bottom-up source>`
- **SAM:** `<value, narrowing assumption>`
- **SOM (Year 1):** `<value, what you're realistically going after>`

---

## Business model

- **`<Stream 1>`:** `<price points, mechanics>`
- **`<Stream 2>`:** `<...>`
- **`<...>`** `<...>`

**Distribution insight (the "why this is efficient" line):**
> `<E.g. "B2B brings users for free; B2C monetises them." — your real flywheel.>`

---

## Revenue trajectory (base case, bottom-up)

| | Year 1 | Year 2 | Year 3 |
|---|---|---|---|
| Total Revenue | `<>` | `<>` | `<>` |
| YoY Growth | — | `<>` | `<>` |
| Exit ARR | `<>` | `<>` | `<>` |
| `<Mix metric (e.g. B2B %)>` | `<>` | `<>` | `<>` |

---

## Brand voice

**We are:** `<3–5 adjectives that describe how you sound — specific, not generic.>`

**We are not:** `<3–5 anti-patterns — hype words you avoid.>`

**Lines that sound like us:**
- *"..."*
- *"..."*

**Lines that do NOT sound like us:**
- "Revolutionising the X landscape" — empty
- "Cutting-edge solutions" — vague
- Any sentence with three adjectives in front of a noun

---

## Visual brand identity

| Token | Hex | Use |
|---|---|---|
| Primary | `#XXXXXX` | Headlines, accent panels, logo |
| Accent | `#XXXXXX` | Highlight bands, key phrases |
| Background | `#XXXXXX` | Default page background |
| Ink (text) | `#XXXXXX` | Body text |
| Ink soft | `#XXXXXX` | Captions, secondary text |

Typography:
- Headlines: `<font + fallback>`
- Body: `<font + fallback>`
- Wordmark: `<lowercase / mixed-case / specific treatment>`

---

## Things to never do

1. Never invent founder details, advisor names, or partnerships not listed above.
2. Never quote a number that conflicts with the canonical table above.
3. Never surface diligence-backup content (cap-table mechanics, founder loans, intercompany items) unless an investor specifically asks about financial diligence.
4. Never overclaim certifications, regulatory status, or partnerships "in flight".
5. Never put placeholder text like `<INVESTOR NAME>` in final outputs — if the investor isn't named, ask before generating.

---

## What goes where

| If you need… | Look in… |
|---|---|
| **Canonical facts & numbers** (the source) | **This file** |
| Form-filling workflow | `investor-form-filler/SKILL.md` |
| Deck-building workflow | `investor-deck-builder/SKILL.md` |
| Q&A prose bank (optional, for question matching) | `references/company-truth.md` |
| Per-audience tone tuning | `references/tone-by-audience.md` |
| Per-investor tuning | `references/investor-tuning.md` |
| Sensitive financials (only if asked) | `references/diligence-backup.md` |
| Slide content & structure | `investor-deck-builder/references/slide-library.md` |
| Verify everything agrees | `scripts/check_consistency.py` (run before sending) |
