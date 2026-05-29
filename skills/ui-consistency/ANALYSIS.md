# ANALYSIS — ui-consistency

> Generated against the [agentskills.io](https://agentskills.openml.io) standard.

---

## Overall Verdict

**Partially compliant.** The skill body is well-structured with clear step-by-step instructions, strong examples, and thorough edge-case coverage — well within both line and token budgets. However, the frontmatter has multiple structural violations: eight non-standard fields (`version`, `author`, `email`, `category`, `tags`, `product`, `sprint`, `tested_with`) are declared at the top level instead of being nested under `metadata:`, and the required `license` and `compatibility` fields are absent entirely.

---

## Spec Compliance Checklist

| Check | Status | Detail |
|---|---|---|
| `name` field format | ✅ PASS | `ui-consistency` — lowercase, hyphens only, no leading/trailing hyphens, 14 chars, matches folder name exactly |
| `description` present & non-empty | ✅ PASS | 179 chars, well within 1–1024 char limit |
| `description` describes what it does | ✅ PASS | Clearly states it handles frontend UI changes with pattern inspection before writing code |
| `description` describes when to use it | ✅ PASS | Includes strong trigger keywords: modals, forms, buttons, tables, layouts, colors, spacing |
| `license` field | ❌ FAIL | Not present — required field is missing |
| `compatibility` field | ❌ FAIL | Not present — skill depends on Glob, Explore agent, and frontend tooling; prerequisites should be captured here |
| `metadata` field structure | ❌ FAIL | 8 non-standard fields (`version`, `author`, `email`, `category`, `tags`, `product`, `sprint`, `tested_with`) are at top level; all must be nested under `metadata:` |
| `allowed-tools` field | — | Not present (optional) |
| Token budget (body) | ✅ PASS | ~2630 tokens — well under the 5000-token recommendation |
| Line budget (body) | ✅ PASS | 165 body lines — well under the 500-line limit |
| `scripts/` directory | — | Not applicable; no external scripts referenced |
| `references/` directory | — | Not applicable |
| `assets/` directory | — | Not applicable |
| Body — step-by-step instructions | ✅ PASS | Five clearly numbered, sequential steps with detailed sub-steps and decision branches |
| Body — examples | ✅ PASS | Concrete end-to-end example with user prompt, agent actions, and expected result |
| Body — edge cases | ✅ PASS | Common Mistakes table covers 6 specific failure modes with fixes; multi-state modal coverage is explicit |

---

## What the Skill Gets Right

- The `name` field is perfectly formatted and matches the folder name exactly.
- The `description` is concise, action-oriented, and packed with discovery keywords (modals, forms, buttons, tables, layouts, colors, spacing) that help agents identify relevant tasks.
- The body follows a clear 5-step progressive structure that is easy for an agent to follow sequentially.
- The Pattern Inventory output format (Step 2) is well-specified with a concrete template — reduces ambiguity about what to extract.
- Step 3c ("Check ALL interactive states") explicitly calls out the most commonly missed behaviour, directly preventing a known class of consistency bugs.
- The Common Mistakes table is a strong, practical addition that maps failure modes to targeted fixes.
- The body is self-contained: no external file references, no absolute paths, no dependency on resources outside the skill folder.
- Token (~2630) and line (165) budgets are comfortably within spec limits, leaving room for future additions.

---

## Violations (Must Fix)

### 1. Non-Standard Frontmatter Fields at Top Level

Eight fields are declared directly in the frontmatter but are not part of the agentskills spec's recognised top-level fields (`name`, `description`, `license`, `compatibility`, `metadata`, `allowed-tools`). All custom fields must be nested under `metadata:`.

**Current (wrong):**
```yaml
version: 1.0.0
author: Ruthu Bahubali Jain
email: ruthu.jain@zysk.tech
category: "engineering-practice"
tags:
  - frontend
  - ui
  - css
  - components
  - consistency
product: zysk
sprint: 1
tested_with: claude-sonnet-4-6
```

**Fix:**
```yaml
metadata:
  version: 1.0.0
  author: Ruthu Bahubali Jain
  email: ruthu.jain@zysk.tech
  category: engineering-practice
  tags:
    - frontend
    - ui
    - css
    - components
    - consistency
  product: zysk
  sprint: 1
  tested_with: claude-sonnet-4-6
```

### 2. Missing `license` Field

The `license` field is a required field per the spec and is entirely absent.

**Fix:** Add a license declaration immediately after `description`:
```yaml
license: MIT
```
(Replace `MIT` with the actual applicable license for this skill.)

### 3. Missing `compatibility` Field

The skill has real environment prerequisites — it dispatches an `Explore` agent, uses `Glob`, and requires access to a frontend source directory. These constraints belong in `compatibility` so that agents and users can evaluate fit before activation.

**Fix:**
```yaml
compatibility: "Requires access to a frontend source directory (resources/js/, src/, assets/, or equivalent). Depends on Glob tool and an Explore sub-agent. Tested with claude-sonnet-4-6. Compatible with Vue, React (JSX/TSX), Svelte, and Blade projects using Tailwind or Bootstrap."
```

---

## What's More Than Needed (Consider Restructuring)

The `## Notes` section at the bottom repeats guidance already present in Steps 4 and 5 ("inline styles are legacy", "Pattern Inventory is the source of truth"). This duplication is minor but could be trimmed or folded into the relevant steps to reduce redundancy as the skill grows.

---

## What's Missing (Must Add)

### 1. `license` Field

Must be added as a top-level frontmatter field. Choose an appropriate open-source license (e.g., MIT, Apache-2.0) or a proprietary designation if this is internal-only.

### 2. `compatibility` Field

Must be added to document the runtime prerequisites: the `Explore` agent dependency, the `Glob` tool requirement, the frontend directory assumption, and the tested model. This is especially important since the skill will silently fail if dispatched against a back-end-only project or an environment without sub-agent support.

---

## Summary Table

| Area | Status | Detail |
|---|---|---|
| `name` field | ✅ Pass | `ui-consistency` — valid format, matches folder name, within length limit |
| `description` field | ✅ Pass | 179 chars, strong trigger keywords, explains what and when |
| `license` field | ❌ Missing | Required field not present |
| `compatibility` field | ❌ Missing | Required context for a skill with external tool and directory dependencies |
| `metadata` structure | ❌ Wrong | 8 custom fields at top level; all must be nested under `metadata:` |
| Token budget | ✅ Pass | ~2630 tokens — well under 5000-token recommendation |
| Line budget | ✅ Pass | 165 body lines — well under 500-line limit |
| Body structure | ✅ Excellent | 5 numbered steps, decision branches, output spec, example, edge cases, self-check checklist |
| Self-containment / portability | ✅ Pass | No absolute paths, no external file references, all instructions are inline |
