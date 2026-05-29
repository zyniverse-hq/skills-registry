# ANALYSIS — tech-mentor

> Generated against the [agentskills.io](https://agentskills.openml.io) standard.

---

## Overall Verdict

**Partially compliant.** The skill body is well-structured, genuinely useful, and demonstrates strong methodology (stage-first research, mandatory failure-mode section, non-prescriptive voice rules). However, several non-standard frontmatter fields (`version`, `author`, `email`, `category`, `tags`, `product`, `sprint`, `tested_with`) are declared at the top level instead of being nested under `metadata:`, which is a direct spec violation. The `license` and `compatibility` fields are also absent.

---

## Spec Compliance Checklist

| Check | Status | Detail |
|---|---|---|
| `name` field format | ✅ PASS | `tech-mentor` — lowercase, hyphens only, no leading/trailing hyphen, 11 chars (≤64), matches folder name |
| `description` present & non-empty | ✅ PASS | Present and non-empty |
| `description` describes what it does | ✅ PASS | Clearly states it researches industry patterns for engineering decisions |
| `description` describes when to use it | ✅ PASS | "Use when evaluating architecture choices, comparing approaches, or understanding what companies do before building something" |
| `license` field | ❌ FAIL | Not present |
| `compatibility` field | ❌ FAIL | Not present |
| `metadata` field structure | ❌ FAIL | `version`, `author`, `email`, `category`, `tags`, `product`, `sprint`, `tested_with` are all top-level; must be nested under `metadata:` |
| `allowed-tools` field | — | Not present (optional; omission is acceptable) |
| Token budget (body) | ✅ PASS | ~1840 tokens (well under 4000 warn / 5000 fail thresholds) |
| Line budget (body) | ✅ PASS | ~110 lines (well under 400 warn / 500 fail thresholds) |
| `scripts/` directory | — | Not present; skill does not require bundled scripts |
| `references/` directory | — | Not present; not required |
| `assets/` directory | — | Not present; not required |
| Body — step-by-step instructions | ✅ PASS | Six clearly numbered steps covering context gathering, clarification, research, gap analysis, synthesis, and ADR offer |
| Body — examples | ✅ PASS | Concrete end-to-end example with user prompt, agent behaviour, and expected result |
| Body — edge cases | ✅ PASS | "Ask when / Skip when" disambiguation, gap-analysis cycle-stopping rule, ADR optional follow-up |

---

## What the Skill Gets Right

- The `name` value is perfectly spec-compliant and matches the folder name exactly.
- The `description` is concise, contains strong trigger keywords ("architecture choices", "comparing approaches", "industry patterns"), and communicates both what the skill does and when to activate it.
- Body length (110 lines, ~1840 tokens) is well within both budgets, leaving room for future additions.
- Step-by-step structure is clear and numbered, with meaningful sub-guidance inside each step.
- The mandatory failure-modes section and the "what companies publish vs. what they actually run" section are explicitly flagged as non-optional — this is excellent quality guidance.
- The stage-first research ordering principle (startup before enterprise) is a thoughtful, well-explained design choice that directly improves output quality.
- The example is concrete and complete: it shows the trigger phrase, the agent's internal actions, and the expected output format.
- The "Do NOT activate when" guard prevents misuse for implementation/code tasks.
- Eval results are documented inline (`26/26 assertions pass`), providing confidence signal for adopters.

---

## Violations (Must Fix)

### 1. Non-standard frontmatter fields at top level

The spec requires: "Non-standard frontmatter fields must be nested under `metadata:`, not at top-level."

The following fields are currently top-level and must be moved under `metadata:`:

**Current (invalid):**
```yaml
version: 1.0.0
author: Vishnu BV
email: vishnu@testmyskills.ai
category: engineering-practice
tags:
  - architecture
  - research
  - decision-support
  - industry-patterns
product: zyniverse
sprint: 1
tested_with: claude-sonnet-4-6
```

**Fix — nest everything under `metadata:`:**
```yaml
metadata:
  version: 1.0.0
  author: Vishnu BV
  email: vishnu@testmyskills.ai
  category: engineering-practice
  tags:
    - architecture
    - research
    - decision-support
    - industry-patterns
  product: zyniverse
  sprint: 1
  tested_with: claude-sonnet-4-6
```

### 2. Missing `license` field

The spec lists `license` as an optional field but its absence means consumers cannot determine the terms under which they may use or adapt the skill.

**Fix — add a license line to the frontmatter, for example:**
```yaml
license: MIT
```

### 3. Missing `compatibility` field

The spec's `compatibility` field documents environment prerequisites (up to 500 chars). This skill requires web search capability (Step 3 mandates 3-5 searches), which is a non-trivial runtime dependency. Without documenting it, agents running in search-restricted environments may activate the skill and fail silently at Step 3.

**Fix — add a compatibility line, for example:**
```yaml
compatibility: Requires web search capability. Compatible with any LLM that supports tool use and markdown output. No specific language runtime required.
```

---

## What's Missing (Must Add)

1. **`license` field** — Add to frontmatter. Even `license: MIT` or `license: proprietary` is better than omission.
2. **`compatibility` field** — Add to frontmatter. At minimum note the web search dependency so the skill fails loudly rather than silently in restricted environments.
3. **`metadata:` wrapper** — All nine custom fields (`version`, `author`, `email`, `category`, `tags`, `product`, `sprint`, `tested_with`) must be nested under `metadata:`.

---

## What's More Than Needed (Consider Restructuring)

- The **Notes** section at the end largely restates principles already embedded in the Steps (stage-first ordering, non-prescriptive voice, sourcing requirement). These four bullets add marginal value — consider collapsing them into the relevant steps or removing them to reduce duplication.
- The `sprint` field inside `metadata` is likely a project-management artifact (internal to the `zyniverse` product). It has no meaning to external consumers of the skill and could be removed or kept private.

---

## Summary Table

| Area | Status | Detail |
|---|---|---|
| `name` field | ✅ Pass | Spec-compliant, matches folder name |
| `description` field | ✅ Pass | Good trigger keywords, clear scope, under 1024 chars |
| `license` field | ❌ Missing | Not present in frontmatter |
| `compatibility` field | ❌ Missing | Not present; web search dependency undocumented |
| `metadata` structure | ❌ Wrong | 9 custom fields declared at top level, not under `metadata:` |
| Token budget | ✅ Pass | ~1840 tokens (limit: 5000) |
| Line budget | ✅ Pass | ~110 lines (limit: 500) |
| Body structure | ✅ Excellent | Six numbered steps, examples, edge cases, explicit non-optional sections |
| Self-containment / portability | ⚠️ Warn | Web search dependency not declared in `compatibility`; ADR output path (`docs/adr/`) assumes a convention not all projects share |
