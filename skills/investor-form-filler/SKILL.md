---
name: investor-form-filler
description: Fill investor application forms (VC, accelerator, grant) from a single facts file, tuned per investor type, with sensitive financials kept behind an explicit gate.
license: MIT
compatibility: >
  Requires WebSearch and WebFetch tools for investor research (Step 2). Uses
  scripts/match_question.py (bundled in skill folder, stdlib-only — no pip
  install needed) and references/company-facts.template.md. Designed for
  Claude Code.
metadata:
  version: "1.0.0"
  author: Sarang T S
  email: sarang@testmyskills.ai
  category: business-sales
  tags: "investor-forms, fundraising, applications, sales-automation, pre-seed"
  product: zyniverse
  sprint: "1"
  tested_with: claude-opus-4-7
---

# Investor Form Filler

> Turn a pasted list of investor questions into a copy-paste-ready, on-brand application draft — grounded in your own facts file, tuned per investor type, with sensitive financials gated.

## When to use

- Activate when: the user pastes investor application questions (Google Form, Typeform, accelerator, grant, pitch-event intake).
- Activate when: the user says "fill this `<investor>` form", "answer these investor questions", or "help me apply to `<investor>`".
- Activate when: the user names a specific investor and asks for draft answers.
- Do NOT activate for: general pitch coaching, writing cold investor emails, or building a pitch deck from scratch (pair with `investor-deck-builder` for that).

## Prerequisites

- [ ] A `company-facts.md` at the project root — the **single source of truth** for every number, founder bio, ask, market sizing, and traction metric. All numbers live here and nowhere else.
- [ ] A `references/tone-by-audience.md` describing how to shift emphasis per audience type (strategic VC, accelerator, government grant, deeptech grant, pitching event).
- [ ] *(Optional)* An `investor-tuning.md` with per-investor blocks (thesis, what to emphasize, what to de-emphasize). Grows over time as you work with more investors.
- [ ] *(Optional, gated)* A `diligence-backup.md` with sensitive financials (cap-table, runway, founder loans, intercompany items). **Never loaded by default** — only when the form explicitly asks about financial diligence.

## Steps

### Step 1: Identify the investor

Confirm the investor's name before doing anything else. If only a partial name is given, ask (e.g. *"the `<Fund Name>` flagship program, or a different `<Fund Name>` track?"*). The investor changes the tone, the proof points that lead, and how the ask is framed. Never put a `<INVESTOR NAME>` placeholder into a final output — ask first.

### Step 2: Research the investor (2–4 web searches max)

Use WebSearch to gather:
- Thesis / sector focus
- Recent portfolio (last 12–18 months)
- Stage focus and ticket size
- Decision style (fast / committee / cohort / warm-intro-only)
- Anything specific (operator-led, accelerator program, accepts cold inbound, application format)

Stop at 4 searches. Build enough context to tune tone — not a full dossier. Note a 3-line investor snapshot to carry into the output.

### Step 3: Get the questions

Get them from one of:
- User-pasted text
- A linked form (use WebFetch if shareable; if login-gated, ask the user to paste)
- An uploaded screenshot / PDF (extract the questions verbatim)

Number them. Note any word/character limits and dropdown options. If the fund has no fixed public form (lightweight intake, warm-intro-only), reconstruct a representative pre-seed application set and clearly label the doc *"reconstructed — verify against the live form"*.

### Step 4: Match each question to your canonical facts

For each question:
1. Identify the closest canonical answer in `company-facts.md` (or a topic-tagged Q&A bank if you maintain one).
2. Pull the canonical content.
3. Reshape it for the new question's exact wording and length limit.
4. If no match, write from scratch using only `company-facts.md` + the investor research — never invent.

*Optional deterministic matcher:* drop the `scripts/match_question.py` helper into your project's `scripts/` folder. It scores a new question against a tagged Q&A bank using weighted token overlap + tag bonuses. Stdlib only, no installs.

### Step 5: Tune for the investor

Apply the matching audience profile from `tone-by-audience.md`:

| Audience type | Lead with | De-emphasize |
|---|---|---|
| Strategic Pre-Seed VC | Traction, distribution, capital efficiency, path to next round | Long science explanations, TRL framing |
| Accelerator / Residency | Founder strength, learning velocity, fit with *this* program | "Fully figured out" posturing |
| Government Grant | Regional impact, employability, SDG/CSR alignment | Valuation, dilution, Series A |
| Deeptech Grant | Scientific moat, IP/patent status, TRL progression, academic partnerships | Pure business framing |
| Pitching Event | Punchy framing, memorable hook, vision over ask | Dense financial tables |

Then apply any investor-specific block from `investor-tuning.md`. If no block exists for this investor, optionally run a research subagent to produce one and offer to save it.

### Step 6: Honor the diligence gate

**Default: never surface `diligence-backup.md`.** Load it only if the form explicitly asks about:
- Cap-table mechanics
- Runway month-by-month
- Cash position
- Founder loans
- Intercompany transactions
- Prior funding terms

If asked, lead with the prepared narrative. Never speculate. Never invent numbers.

### Step 7: Generate the output document

Write a clean markdown doc with this shape:

```markdown
# <Company> — <Investor Name> Application Response
*Generated <date> · numbers per company-facts.md*

## Investor Snapshot
[3-line profile from Step 2]
**Tuning applied:** [what got front-loaded, what got de-emphasized]

## Answers
### Q1: [question text exactly as posed]
[answer, tuned for investor + length-appropriate]

### Q2: ...

## Notes before you submit
- [Fields requiring human input — bank details, phones, GST]
- [Honesty calls — what you withheld and why]
- [Consistency check — confirm numbers match the deck/source]
```

The user copy-pastes from this into the actual form.

### Step 8: Offer next steps

1. **Matching deck?** — run the companion `investor-deck-builder` skill so the deck and form use the same numbers and framing.
2. **Diligence pack?** — only if the investor asks for financials.
3. **Save an investor-tuning block** — so the next application to the same investor is consistent.

## Output

- **Format:** markdown document, copy-paste-ready by question.
- **Location:** `output/<investor-slug>-application-FILLED.md` (or your project's output convention).
- **Example:** see the "Example" section below.

## Example

**User says:** *"Fill this `<Investor>` application: 1. Company name 2. What do you do? 3. Top traction metrics. 4. How much are you raising? ..."*

**Claude does:**
1. Confirms `<Investor>`, runs 3 WebSearches on their thesis and recent portfolio.
2. Loads `company-facts.md` for the numbers and `tone-by-audience.md` for the right voice.
3. Matches each question to the canonical content; reshapes for length; tunes for `<Investor>`.
4. Withholds anything in `diligence-backup.md` (the form didn't ask).
5. Writes `output/<investor-slug>-application-FILLED.md` with answers + a Notes block flagging bank details and any USER-TO-FILL items.

**Result:** a copy-paste-ready document. The user reviews the Notes, fills any human-input fields, then pastes answer-by-answer into the live form.

## Honesty constraints — apply to every answer

- **Never invent** customers, partnerships, or numbers. Every figure must trace back to `company-facts.md`.
- **Patent status:** say what's true ("application to be filed" vs "filed" vs "granted"). Never inflate.
- **B2B customer names:** describe by count and category unless explicitly cleared by the user.
- **Team size:** use what's in `company-facts.md` — never round up.
- **Diligence-backup content:** never surface unprompted.
- **Word/character limits:** never exceed them — investors mark down for overflow.

## Failure modes to avoid

1. **Generic answers** that could be any startup — rewrite with company specifics.
2. **The same phrase across multiple questions** — investors notice copy-paste.
3. **Saying "we don't know"** when the answer is in `company-facts.md` — re-check before giving up.
4. **Surfacing diligence info unprompted** — the user controls when that comes out.
5. **Fabricating field labels** when you don't have the live form — reconstruct conservatively, label "reconstructed".

## Notes

- This skill pairs with **investor-deck-builder**. Both should read the same `company-facts.md` — that's how the deck and form never drift on numbers.
- Pair with a `scripts/check_consistency.py` drift guard in your project. It should fail if a banned/stale value reappears (an old valuation, an old team size), if `company-facts.md` is missing a canonical anchor, or if any artifact references a fact that has changed. Prose can't be fully DRY; the guard is the safety net.
- For a stable Q&A bank with topic tags, `scripts/match_question.py` (included) gives deterministic matching — useful for batch mode across many questions.
- Filled forms can be turned into PDFs for emailing via a small markdown→PDF helper (the deck-builder skill includes one).
