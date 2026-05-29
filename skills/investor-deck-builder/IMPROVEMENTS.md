# IMPROVEMENTS — investor-deck-builder

> Improvement plan derived from SKILL.md + ANALYSIS.md audit against the agentskills.openml.io spec.

---

## Quick Summary

| | Before | After |
|---|---|---|
| Spec compliance | Partially compliant | Fully compliant |
| Critical violations | 3 | 0 |
| Agent discoverability | Medium | High |
| Portability | Partial | Pass |

---

## Improvement 1 — Move Custom Frontmatter Fields Under `metadata:`

### What needs to change

Eight custom fields (`version`, `author`, `email`, `category`, `tags`, `product`, `sprint`, `tested_with`) are declared at the top level of the frontmatter. The agentskills.io spec allows exactly six top-level keys: `name`, `description`, `license`, `compatibility`, `metadata`, and `allowed-tools`. All custom fields must be nested under `metadata:` as string key-value pairs. The `tags` list must be flattened to a comma-separated string because `metadata` values must be strings.

### Before
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

### After
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

### Impact if implemented
- **Agent behaviour:** Frontmatter parsers that enforce the spec schema will no longer reject or silently misparse the skill file; the eight fields become readable metadata instead of parse noise.
- **Discoverability:** Registry indexers that scan `metadata.*` for tagging and search will now surface this skill under `business-sales`, `pitch-deck`, `reportlab`, etc.
- **Portability:** Any team cloning this skill into their registry will get a valid file; currently their validator would flag 8 violations on import.
- **Risk reduced:** Prevents silent field-level collisions if a future spec version adds a top-level key with the same name as one of these eight (e.g., `category` or `version`).

### Existing use (before fix)
Today, a developer who imports `investor-deck-builder` into a spec-compliant registry will trigger 8 frontmatter validation errors on first parse. Automated registry tooling (such as the `index.json` regeneration script already used in this repo) may silently drop or misinterpret the non-standard top-level fields. The `tags` field declared as a YAML list is especially risky: tools expecting a string will either throw a type error or skip tag-based search indexing entirely. The sprint number (`sprint: 1`) is stored as an integer, which further breaks the "metadata values must be strings" rule.

### Improved use (after fix)
After the fix, the skill file passes spec validation on first import. The registry indexer reads all eight metadata fields correctly under `metadata.*`. Tag-based search for "pitch-deck" or "reportlab" or "fundraising" returns this skill. The `sprint` and `version` fields are properly quoted strings, satisfying strict YAML string-type requirements. Any team forking this skill for their own product registry gets a clean, valid file.

---

## Improvement 2 — Add Missing `license` Field

### What needs to change

The `license` field is a required top-level frontmatter key per the agentskills.io spec. It is entirely absent from the current frontmatter. Without it, registry indexers cannot determine redistribution rights, and spec validators will flag the file as non-compliant.

### Before
```yaml
---
name: investor-deck-builder
description: Generate a tailored, branded investor pitch deck PDF for a specific investor or program, with audience-selected slides and content driven entirely from a single facts file — no numbers hardcoded.
version: 1.0.0
author: Sarang T S
# ... no license field present
---
```

### After
```yaml
---
name: investor-deck-builder
description: ...
license: Proprietary — internal use only (testmyskills.ai / zyniverse)
compatibility: ...
metadata:
  ...
---
```

### Impact if implemented
- **Agent behaviour:** No direct runtime change, but registry tooling that gates skill loading on license presence will now allow this skill to load cleanly.
- **Discoverability:** License-filtered searches (e.g., "show me all open-source skills" vs "proprietary only") will correctly classify this skill.
- **Portability:** Other teams inspecting this skill to assess whether they can reuse it will immediately see it is proprietary and internal — preventing accidental redistribution.
- **Risk reduced:** Removes the ambiguity of "no license = unknown rights", which in a shared registry defaults to the most restrictive assumption and blocks legitimate internal use.

### Existing use (before fix)
Currently any spec-compliant validator run against this skill file will report a `license` field missing error and mark the skill as non-compliant. Teams evaluating this skill for adoption into their own registry have no clear signal about redistribution rights. A developer unfamiliar with the skill's origin might assume it is open to reuse, leading to unintended copying of proprietary company positioning content.

### Improved use (after fix)
After adding `license: Proprietary — internal use only (testmyskills.ai / zyniverse)`, the skill passes the required-field check. Registry consumers see at a glance that this skill is internal to testmyskills.ai/zyniverse and not for open redistribution. The spec validator moves from non-compliant to compliant on this axis.

---

## Improvement 3 — Add Missing `compatibility` Field Declaring Python/reportlab/Font Dependencies

### What needs to change

This skill has three hard runtime dependencies that are invisible in the frontmatter: Python 3.9+, the `reportlab` library, and a Unicode Rupee-capable system font (DejaVu on Linux, `Helvetica.ttc` on macOS, Arial on Windows). These are declared in the body prose but not in the `compatibility` field, which is the machine-readable location where agents and tooling look for environment requirements. Without `compatibility`, an agent running this skill on a minimal CI container will get a runtime crash from `generate_deck.py` with no prior warning.

### Before
```yaml
# No compatibility field present in frontmatter
```

The dependency information exists only buried in body prose under "Prerequisites":
```markdown
- [ ] Python 3.9+ with `reportlab` installed (use a venv — PEP 668 blocks system pip on most Macs/Linux).
- [ ] A `₹`-capable system font for rupee figures: DejaVu (Linux), `Helvetica.ttc` (macOS), Arial (Windows).
```

### After
```yaml
compatibility: >
  Requires Python 3.9+ with reportlab installed (pip install reportlab).
  Use a venv — PEP 668 blocks system pip on most Macs/Linux.
  Needs a ₹-capable system font: DejaVu (Linux), Helvetica.ttc (macOS),
  Arial (Windows). Designed for Claude Code on macOS/Linux/Windows.
  Depends on bundled scripts/generate_deck.py and references/slide-library.md,
  references/slide-selection-rules.md, and a project-level company-facts.md.
```

### Impact if implemented
- **Agent behaviour:** Before running Step 5 (`python3 scripts/generate_deck.py`), an agent can read `compatibility` and pre-check the environment, surfacing a clear error message rather than a raw Python traceback.
- **Discoverability:** Registry filters for "Python skills" or "PDF generation skills" will now surface this skill because `reportlab` and `Python 3.9+` appear in the machine-readable compatibility field.
- **Portability:** A new developer cloning this skill into a fresh project sees the dependency contract upfront in the frontmatter, not on first runtime failure.
- **Risk reduced:** Eliminates silent `ModuleNotFoundError: reportlab` or garbled `₹` rendering failures in CI/CD pipelines that lack the system font — the agent can bail early with a meaningful message.

### Existing use (before fix)
Today, when an agent or developer runs this skill in a fresh environment (e.g., a new GitHub Actions runner, a Windows machine without DejaVu, or a Python 3.8 environment), the failure mode is deferred entirely to Step 5 when `generate_deck.py` is executed. The error surfaces as a Python traceback (`ImportError`, `FontError`, or garbled PDF output) with no connection back to the skill's documented prerequisites. The agent has no way to pre-validate the environment before beginning the 5-step workflow.

### Improved use (after fix)
With `compatibility` declared in frontmatter, an agent can inspect it before starting Step 1 and surface: "This skill requires Python 3.9+, reportlab, and a ₹-capable font. Your environment has Python 3.8 — please upgrade before continuing." The 5-step workflow only begins once the environment is validated, preventing wasted work on config generation that cannot be executed.

---

## Improvement 4 — Add Trigger Keywords to `description` for Agent Discovery

### What needs to change

The skill's activate phrases ("build a deck for `<investor>`", "generate the pitch deck for `<program>`", "tailor the deck for `<audience>`") are documented in the body's "When to use" section but do not appear in the `description` field. Agent routing systems that use `description` for skill matching will not recognise these trigger phrases. The description should surface the most distinctive activation signals directly.

### Before
```yaml
description: Generate a tailored, branded investor pitch deck PDF for a specific investor or program, with audience-selected slides and content driven entirely from a single facts file — no numbers hardcoded.
```

Trigger phrases exist only in body prose:
```markdown
- Activate phrases: "build a deck for `<investor>`", "generate the pitch deck for `<program>`", "tailor the deck for `<audience>`".
```

### After
```yaml
description: >
  Generate a tailored, branded investor pitch deck PDF for a specific investor or
  program. Use when the user says "build a deck for <investor>", "generate the pitch
  deck for <program>", "tailor the deck for <audience>", or just finished filling
  an application via investor-form-filler. Selects the right slides for the
  audience type (strategic investor, accelerator, grant, demo day), populates all
  content from company-facts.md, and runs generate_deck.py to produce a 16:9 PDF.
```

### Impact if implemented
- **Agent behaviour:** Routing agents that perform fuzzy-match on skill descriptions will correctly trigger `investor-deck-builder` when a user says "build a deck for Y Combinator" or "generate the pitch deck for Surge" — phrases that currently pass through without a match.
- **Discoverability:** Semantic search over skill descriptions will now surface this skill for investor/fundraising/deck queries. The current description mentions "PDF pitch deck" but not "build a deck", "generate pitch deck", or "investor-form-filler" companion context.
- **Portability:** Teams importing this skill into a different routing infrastructure will have the trigger contract encoded in the portable `description` field, not in body prose that may be ignored by their agent framework.
- **Risk reduced:** Prevents the skill being bypassed silently when the exact activation phrase is used, forcing the user to manually invoke it rather than having the agent route to it automatically.

### Existing use (before fix)
Today, if a user tells their Claude Code agent "build a deck for Sequoia — strategic pre-seed", the agent must scan the full skill body to find the "Activate phrases" section before determining this skill applies. Routing systems that rely on `description`-level matching will not trigger this skill automatically. The user may receive a generic response or need to explicitly name the skill, reducing the seamless companion-skill experience with `investor-form-filler`.

### Improved use (after fix)
After the description update, an agent routing layer immediately matches "build a deck for Sequoia" against the description phrase "build a deck for <investor>" and routes to `investor-deck-builder` without body scanning. The companion workflow — user fills a form via `investor-form-filler`, then asks "now build the matching deck" — triggers automatically because the description now references `investor-form-filler` as a handoff context signal.

---

## Improvement 5 — Move "Generator Design Rules" Section to `references/generator-design.md`

### What needs to change

The "Generator design rules (read before editing)" section contains guidance for developers modifying `generate_deck.py`, not instructions for agents executing the skill workflow. It consumes body budget on content that is irrelevant during normal execution. This section should be extracted to `references/generator-design.md` and replaced with a single pointer line in the body, consistent with how `slide-library.md` and `slide-selection-rules.md` are handled.

### Before
```markdown
## Generator design rules (read before editing)

- **Layout lives in the generator. Numbers do not.** Every business figure (revenue, ask, market sizes, traction stats) reads from the JSON config. Missing → visible `—` placeholder.
- **Static brand copy** (slide headlines, taglines) is OK to bake in — it's not a drift-prone number.
- **Cross-platform fonts.** Font resolver tries Linux → macOS → Windows candidates in order; verifies `₹` glyph at registration time; degrades to `Rs ` gracefully if no font qualifies.
- **Stable slide-ID vocabulary** matching `slide-library.md`, `slide-selection-rules.md`, and the JSON config's `slides` array. Unknown ID raises — never silently fallback.
- **Brand identity from config**, not from constants. The same generator must work for any company — pass `config.brand.primary` / `.accent` / `.background` / `.ink`.
```

### After

In `SKILL.md` body, replace the full section with:
```markdown
## Generator design rules

See `references/generator-design.md` for layout, font resolution, and slide-ID conventions to follow when editing `scripts/generate_deck.py`.
```

And create `references/generator-design.md` with the full content extracted above, plus the notes about `check_consistency.py` and `md_to_pdf.py` that currently appear in the Notes section.

### Impact if implemented
- **Agent behaviour:** The executing agent no longer scans developer-targeted content during normal workflow runs. The body becomes purely execution instructions.
- **Discoverability:** Reduces body token count by ~80 tokens, keeping it further from the 5000-token budget limit as the skill grows.
- **Portability:** A developer wanting to extend `generate_deck.py` finds all design contracts in one reference file rather than split between the body and the Notes section.
- **Risk reduced:** Prevents the "Generator design rules" section from drifting out of sync with the actual `generate_deck.py` implementation, since the reference file is co-located with the other `references/` artifacts that developers are expected to maintain.

### Existing use (before fix)
Today, an agent executing the 7-step workflow reads the "Generator design rules" section on every invocation, consuming context window budget on content it has no reason to act on (it is not editing `generate_deck.py`). A developer who wants to add a new slide renderer must cross-reference the body section, the `references/slide-library.md`, and the `Notes` section for the `check_consistency.py` requirement — three separate locations.

### Improved use (after fix)
The executing agent reads a single pointer line and moves on. A developer extending the generator opens `references/generator-design.md` and finds all design contracts (layout rules, font resolver behaviour, slide-ID vocabulary, consistency guard requirements) in one place. The body stays focused on the 7-step execution workflow.

---

## Priority Order

| Priority | Improvement | Effort | Impact |
|---|---|---|---|
| 1 | Move custom frontmatter fields under `metadata:` | Low | Critical — 8 spec violations fixed, registry indexing unblocked |
| 2 | Add missing `license` field | Low | Critical — required field; spec compliance restored |
| 3 | Add missing `compatibility` field | Low | Critical — prevents silent runtime failures on fresh environments |
| 4 | Add trigger keywords to `description` | Low | High — agent routing and companion-skill handoff unlocked |
| 5 | Move Generator Design Rules to `references/` | Medium | Medium — body clarity improved, developer UX improved |

---

## Before vs After: Full Skill Experience

### Before (current state)

A developer importing `investor-deck-builder` into any spec-compliant registry today will immediately encounter eight frontmatter validation errors — `version`, `author`, `email`, `category`, `tags`, `product`, `sprint`, and `tested_with` are all at the wrong level. The `tags` field is a YAML list where a string is required, and `sprint` is an integer where a string is required. The missing `license` field adds a ninth violation. The missing `compatibility` field means there is no machine-readable declaration of the Python 3.9+, `reportlab`, and system-font requirements. A developer who clones this skill into a fresh Linux CI container and runs it will reach Step 5 before discovering that `reportlab` is not installed, or that the `₹` glyph renders as `Rs ` without any prior warning from the skill file itself.

From a routing perspective, an agent that receives a user message like "build a deck for Andreessen Horowitz — strategic pre-seed" must scan the full skill body to find the "Activate phrases" section before determining this skill applies. The `description` field contains accurate but trigger-phrase-free prose, so description-level routing will miss the activation signal. The "Generator design rules" section is present inline in the body, consuming context window budget during every execution even though it is developer documentation, not agent instructions. A developer wanting to extend the generator must hunt across the body, `Notes`, and two separate `references/` files to piece together all design contracts.

### After (all improvements applied)

With all five improvements applied, `investor-deck-builder` passes spec validation on first import: frontmatter has exactly the six permitted top-level keys (`name`, `description`, `license`, `compatibility`, `metadata`, `allowed-tools` omitted as optional), all eight custom fields are correctly nested under `metadata:` as strings, and the `license` and `compatibility` fields are present and populated. A developer importing this skill into any registry gets a clean file with no validation errors. The `compatibility` field gives agents and CI tooling a pre-flight check target: before starting Step 1, an agent can confirm Python 3.9+, `reportlab`, and font availability, surfacing a clear error rather than a mid-workflow traceback.

Agent routing now works automatically. The updated `description` contains the trigger phrases "build a deck for `<investor>`", "generate the pitch deck for `<program>`", and "tailor the deck for `<audience>`", as well as a reference to the `investor-form-filler` companion context. An agent routing layer matches these phrases at description level without body scanning, enabling the seamless "fill the form, then build the deck" workflow that the skill was designed around. The body is cleaner: the "Generator design rules" section is replaced by a one-line pointer to `references/generator-design.md`, where all generator extension contracts and consistency guard requirements live together. The executing agent reads only what it needs; the developer extending `generate_deck.py` finds everything in one reference file.

