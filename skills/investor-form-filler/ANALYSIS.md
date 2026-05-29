# ANALYSIS — investor-form-filler

> Generated against the [agentskills.io](https://agentskills.openml.io) standard.

---

## Overall Verdict

**Partially compliant.** The skill has excellent body content — clear 8-step workflow, a concrete example, an honesty-constraints section, and a well-scoped failure-modes list. However, it has a significant structural violation: eight non-standard frontmatter fields (`version`, `author`, `email`, `category`, `tags`, `product`, `sprint`, `tested_with`) are placed at the top level instead of being nested under `metadata:` as the spec requires. The `license` and `compatibility` fields are also absent. Fixing the frontmatter structure is the only mandatory change; the body is production-quality.

---

## Spec Compliance Checklist

| Check | Status | Detail |
|---|---|---|
| `name` field format | PASS | `investor-form-filler` — lowercase, hyphens only, no leading/trailing hyphen, 20 chars, matches folder name exactly |
| `description` present & non-empty | PASS | 163 chars, well within the 1-1024 char range |
| `description` describes what it does | PASS | Clearly states: fills investor application forms from a facts file |
| `description` describes when to use it | PASS | Mentions VC, accelerator, grant contexts; financials gate signals scope |
| `license` field | FAIL | Not present in frontmatter |
| `compatibility` field | FAIL | Not present; skill depends on WebSearch and WebFetch tools but documents no environment prerequisites |
| `metadata` field structure | FAIL | `version`, `author`, `email`, `category`, `tags`, `product`, `sprint`, `tested_with` are all at the top level — must be nested under `metadata:` |
| `allowed-tools` field | N/A | Not present; optional, but skill uses WebSearch and WebFetch — listing them would improve discoverability |
| Token budget (body) | PASS | ~2168 tokens estimated (body is 8,674 chars at ~4 chars/token); well under the 5,000-token limit |
| Line budget (body) | PASS | 155 body lines; well under the 500-line limit |
| `scripts/` directory | PASS | `scripts/match_question.py` is present and bundled inside the skill folder |
| `references/` directory | PASS | `references/tone-by-audience.md` and `references/company-facts.template.md` are present |
| `assets/` directory | N/A | Not present; not required for this skill type |
| Body — step-by-step instructions | PASS | Eight clearly numbered steps covering the full workflow from investor identification to output and next steps |
| Body — examples | PASS | Concrete end-to-end example in the "Example" section with user input and agent actions |
| Body — edge cases | PASS | Failure modes section covers 5 specific anti-patterns; diligence gate is explicitly scoped; reconstructed-form case is handled |

---

## What the Skill Gets Right

- The `name` field is perfectly formed: lowercase, hyphen-separated, matches the folder name, and is well under 64 characters.
- The `description` is concise and contains strong trigger keywords: "investor application forms", "VC", "accelerator", "grant", "facts file", "financials gate" — all terms an agent would match against user intent.
- The 8-step workflow is genuinely step-by-step and covers the entire happy path with clear sequencing.
- The diligence gate (Step 6) is a strong safety design: it explicitly names the six triggers that unlock sensitive data, preventing accidental disclosure.
- The investor-type tuning table (Step 5) gives concrete, actionable guidance without requiring external lookup.
- The output template (Step 7) is provided inline so the agent always produces a consistent artifact shape.
- The honesty-constraints section adds trust guardrails that are rare in skills of this type.
- The failure-modes section prevents the five most common failure patterns in LLM-generated investor content.
- `scripts/match_question.py` is bundled in `scripts/` (correct location, stdlib-only) and `references/` contains both a tone guide and a company-facts template.
- File path references throughout the body are relative, not absolute — fully portable.

---

## Violations (Must Fix)

### 1. Non-standard frontmatter fields are not nested under `metadata:`

The spec is explicit: "Non-standard frontmatter fields MUST be nested under `metadata:`, not at top-level." Eight fields violate this rule.

Current (violating):

    name: investor-form-filler
    description: Fill investor application forms ...
    version: 1.0.0
    author: Sarang T S
    email: sarang@testmyskills.ai
    category: business-sales
    tags:
      - investor-forms
      - fundraising
      - applications
      - sales-automation
      - pre-seed
    product: zyniverse
    sprint: 1
    tested_with: claude-opus-4-7

Fixed:

    name: investor-form-filler
    description: Fill investor application forms (VC, accelerator, grant) from a single facts file, tuned per investor type, with sensitive financials kept behind an explicit gate.
    license: MIT
    compatibility: Requires WebSearch and WebFetch tool access. Expects a company-facts.md at the project root. Optional scripts/match_question.py requires Python 3.8+ (stdlib only).
    metadata:
      version: 1.0.0
      author: Sarang T S
      email: sarang@testmyskills.ai
      category: business-sales
      tags:
        - investor-forms
        - fundraising
        - applications
        - sales-automation
        - pre-seed
      product: zyniverse
      sprint: 1
      tested_with: claude-opus-4-7

### 2. `license` field is missing

The spec lists `license` as an optional field, but its absence is a gap for a published skill. A license must be added.

Fix: Add `license: MIT` (or the appropriate license) at the top level of the frontmatter, as shown in the fixed block above.

### 3. `compatibility` field is missing

The skill depends on WebSearch and WebFetch tool availability and on the presence of `company-facts.md`. None of this is declared in the frontmatter, only in the body's "Prerequisites" section. The frontmatter `compatibility` field is the machine-readable contract; the body section is human guidance.

Fix: Add a `compatibility` field (under 500 chars) declaring tool dependencies and the `company-facts.md` requirement, as shown in the fixed block above.

---

## What is More Than Needed (Consider Restructuring)

- The "Notes" section at the bottom references `scripts/check_consistency.py` as something to "pair with your project" — but this script is not included in `scripts/`. Either bundle it or remove the reference to avoid implying the skill provides something it does not.
- Step 8 ("Offer next steps") lists the companion `investor-deck-builder` skill. This cross-skill dependency is fine as a recommendation, but it creates a runtime assumption the skill cannot fulfill if the other skill is not installed. Consider softening the language to "if the investor-deck-builder skill is available" rather than implying it is always present.

---

## What is Missing (Must Add)

1. `license` field in frontmatter — any OSI-approved identifier (MIT, Apache-2.0, etc.) or a proprietary declaration.

2. `compatibility` field in frontmatter — declare that WebSearch and WebFetch are required, Python 3.8+ is needed for the optional script, and `company-facts.md` must exist at the project root. Keep it under 500 chars.

3. `metadata:` wrapper around all non-standard fields — `version`, `author`, `email`, `category`, `tags`, `product`, `sprint`, `tested_with` must all move under a `metadata:` block.

4. `scripts/check_consistency.py` — the body's "Notes" section recommends this script and implies it is part of the skill, but it is not present in `scripts/`. Either add it or remove the reference.

---

## Summary Table

| Area | Status | Detail |
|---|---|---|
| `name` field | Pass | Perfectly formed; matches folder name |
| `description` field | Pass | 163 chars; strong trigger keywords; covers what and when |
| `license` field | Missing | Not present in frontmatter |
| `compatibility` field | Missing | Tool and file dependencies undeclared in frontmatter |
| `metadata` structure | Wrong | 8 non-standard fields at top level; must all move under `metadata:` |
| Token budget | Pass | ~2168 tokens estimated; comfortably under 5000-token limit |
| Line budget | Pass | 155 body lines; well under 500-line limit |
| Body structure | Excellent | 8 numbered steps, output template, example, honesty constraints, failure modes |
| Self-containment / portability | Pass | Relative paths throughout; scripts bundled; references bundled; one missing script (`check_consistency.py`) noted |
