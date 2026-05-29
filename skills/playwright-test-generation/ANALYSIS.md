# ANALYSIS — playwright-test-generation

> Generated against the [agentskills.io](https://agentskills.openml.io) standard.

---

## Overall Verdict

**Partially compliant.** The skill body is well-structured, self-contained, and genuinely useful — step-by-step instructions, a concrete example, and thorough test-coverage checklists are all strong. However, multiple non-standard frontmatter fields (`version`, `author`, `email`, `category`, `tags`, `product`, `sprint`, `tested_with`) are placed at the top level instead of being nested under `metadata:` as the spec requires, and the mandatory `license` and `compatibility` fields are absent.

---

## Spec Compliance Checklist

| Check | Status | Detail |
|---|---|---|
| `name` field format | ✅ PASS | `playwright-test-generation` — lowercase, hyphens only, no leading/trailing hyphens, 26 chars (≤64), matches folder name exactly |
| `description` present & non-empty | ✅ PASS | 130 chars, well within 1–1024 limit |
| `description` describes what it does | ✅ PASS | Clearly states: generating structured Playwright E2E tests, producing helpers, spec files, and a summary report |
| `description` describes when to use it | ⚠️ WARN | Covers the output well but lacks explicit trigger keywords such as "write", "automate", "generate tests", "e2e", "page" in the description itself — those only appear in the body's "When to use" section |
| `license` field | ❌ FAIL | Not present |
| `compatibility` field | ❌ FAIL | Not present — prerequisites (Playwright, TypeScript, live URL) are documented in the body but not in the frontmatter `compatibility` field |
| `metadata` field structure | ❌ FAIL | `version`, `author`, `email`, `category`, `tags`, `product`, `sprint`, and `tested_with` are all top-level frontmatter keys; the spec requires all non-standard fields to be nested under `metadata:` |
| `allowed-tools` field | — | Not present; optional, acceptable |
| Token budget (body) | ✅ PASS | ~1428 estimated tokens (≤5000 limit); well within budget |
| Line budget (body) | ✅ PASS | 134 lines (≤500 limit); well within budget |
| `scripts/` directory | — | No scripts referenced or needed; absence is acceptable |
| `references/` directory | — | Not present; not required |
| `assets/` directory | — | Not present; not required |
| Body — step-by-step instructions | ✅ PASS | Five clearly numbered steps covering exploration, helpers file, spec file, config, and report generation |
| Body — examples | ✅ PASS | Concrete "User says / Claude does / Result" example for the login page scenario |
| Body — edge cases | ✅ PASS | Explicit edge-case checklist: whitespace trimming, clipboard paste, XSS, SQL injection, keyboard interaction, protected-route redirect |

---

## What the Skill Gets Right

- Name is perfectly formatted and matches the folder name exactly.
- Description is concise and clearly conveys the output (helpers, spec files, summary report).
- Body is well within both the line budget (134/500) and token budget (~1428/5000), leaving room for future additions.
- Step-by-step structure is logical and easy to follow (explore → helpers → spec → config → report).
- Test-coverage checklist is comprehensive, covering positive, negative, and edge-case categories.
- The "When to use / Do NOT activate when" section gives agents clear disambiguation guidance.
- The complete `playwright.config.ts` snippet is self-contained — an agent can use it immediately without external lookups.
- Output locations follow a consistent, predictable naming convention (`tests/<feature-name>/`, `reports/`).
- The concrete login-page example makes the expected workflow tangible.
- The "Notes" section reinforces critical conventions (helpers vs. spec separation, mandatory report).

---

## Violations (Must Fix)

### 1. Non-standard frontmatter fields not nested under `metadata:`

The spec states: "Non-standard frontmatter fields must be nested under `metadata:`, not at top-level."

The following fields are top-level but are not part of the recognized spec fields (`name`, `description`, `license`, `compatibility`, `metadata`, `allowed-tools`):

**Current (violating):**

```yaml
version: 1.0.1
author: Deepikaa Naganathan
email: deepikaa.n@zysk.tech
category: qa-testing
tags:
  - playwright
  - e2e-testing
  - test-generation
  - automation
product: zysk | tms | zyni
sprint: 1
tested_with: claude-sonnet-4-6
```

**Fix — nest all of these under `metadata:`:**

```yaml
metadata:
  version: 1.0.1
  author: Deepikaa Naganathan
  email: deepikaa.n@zysk.tech
  category: qa-testing
  tags:
    - playwright
    - e2e-testing
    - test-generation
    - automation
  product: zysk | tms | zyni
  sprint: 1
  tested_with: claude-sonnet-4-6
```

### 2. `license` field is missing

The spec lists `license` as an optional but recognized field. It is absent entirely.

**Fix — add a license declaration:**

```yaml
license: MIT
```

(or whichever license applies to this skill)

### 3. `compatibility` field is missing

Environment prerequisites are documented in the body under "Prerequisites" but are not surfaced in the frontmatter `compatibility` field, which is where agents look for environment requirements before activation.

**Fix — add a `compatibility` field (max 500 chars):**

```yaml
compatibility: Requires Playwright installed (npx playwright install), TypeScript configured in the project, a live URL accessible at runtime, and Microsoft Edge available for the default config. Node.js 18+ recommended.
```

---

## What's More Than Needed (Consider Restructuring)

- The **Prerequisites** section in the body duplicates what should live in `compatibility`. Once `compatibility` is added to the frontmatter, the body's prerequisites checklist can be shortened or removed to reduce redundancy.
- The **Notes** section at the end largely repeats constraints already stated in the individual steps (e.g., "helpers file, never the spec file" appears in both Step 2 and Notes). Consider consolidating into the steps themselves to keep the body DRY.

---

## What's Missing (Must Add)

1. **`license` field** — Add to frontmatter. Without it, consumers cannot determine usage terms.
2. **`compatibility` field** — Add to frontmatter. Prerequisites are buried in the body; they must also appear in `compatibility` so agents can assess environment fit before loading the full skill.
3. **`metadata:` wrapper** — All non-standard fields (`version`, `author`, `email`, `category`, `tags`, `product`, `sprint`, `tested_with`) must be moved under `metadata:`.
4. **Trigger keywords in `description`** — The description is accurate but slightly passive. Adding trigger verbs ("write", "generate", "automate", "create Playwright tests") directly into the description string improves agent-discovery matching. Example: `"Generate or write structured Playwright E2E tests by exploring the live UI first, then producing helpers, spec files, and a summary report. Use when asked to automate, test, or create e2e tests for any page or feature."`

---

## Summary Table

| Area | Status | Detail |
|---|---|---|
| `name` field | ✅ Pass | Valid format, matches folder name, 26 chars |
| `description` field | ⚠️ Warn | Present and accurate; trigger keywords could be stronger in the description itself |
| `license` field | ❌ Missing | Not present in frontmatter |
| `compatibility` field | ❌ Missing | Not present in frontmatter; prerequisites only exist in body |
| `metadata` structure | ❌ Wrong | 8 non-standard fields are top-level instead of nested under `metadata:` |
| Token budget | ✅ Pass | ~1428 tokens — well within 5000-token limit |
| Line budget | ✅ Pass | 134 lines — well within 500-line limit |
| Body structure | ✅ Excellent | Clear numbered steps, checklists, example, and notes |
| Self-containment / portability | ✅ Pass | Full config snippet included; output paths and naming conventions are explicit; no external script dependencies |
