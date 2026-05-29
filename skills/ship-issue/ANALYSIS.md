# ANALYSIS — ship-issue

> Generated against the [agentskills.io](https://agentskills.openml.io) standard.

---

## Overall Verdict

**Partially compliant.** The skill has a well-structured body with clear step-by-step instructions, good examples, recovery procedures, and edge-case coverage. However, several non-standard frontmatter fields (`version`, `author`, `email`, `category`, `tags`, `product`, `sprint`, `tested_with`, `user-invocable`) are placed at the top level instead of being nested under `metadata:`, which is a direct spec violation. The `license` and `compatibility` fields are also absent.

---

## Spec Compliance Checklist

| Check | Status | Detail |
|---|---|---|
| `name` field format | ✅ PASS | `ship-issue` — lowercase, hyphens only, no leading/trailing hyphen, 10 chars (≤64), matches folder name exactly |
| `description` present & non-empty | ✅ PASS | 168 chars, within 1–1024 limit |
| `description` describes what it does | ✅ PASS | Clearly states end-to-end GitHub issue execution with three named tracks |
| `description` describes when to use it | ⚠️ WARN | Implicit ("executes a single GitHub issue") but lacks explicit trigger keywords like "ship issue", "implement issue", "fix issue", "start work on" that an agent would match against user input |
| `license` field | ❌ FAIL | Not present |
| `compatibility` field | ❌ FAIL | Not present — skill depends on `gh`, `npm`, `npx tsc`, git worktrees, GitHub Projects v2, and companion skills (`pr-review-toolkit`, `superpowers`, `decision-brief`), none of which are documented |
| `metadata` field structure | ❌ FAIL | `version`, `author`, `email`, `category`, `tags`, `product`, `sprint`, `tested_with`, `user-invocable` are all top-level frontmatter fields; spec requires all non-standard fields to be nested under `metadata:` |
| `allowed-tools` field | — | Not present (optional; no penalty) |
| Token budget (body) | ✅ PASS | Body is ~5,800 chars ≈ 1,450 tokens (well under the 5,000-token warn threshold) |
| Line budget (body) | ✅ PASS | Body is approximately 148 lines (well under the 400-line warn threshold and 500-line hard limit) |
| `scripts/` directory | — | No scripts referenced or bundled; not applicable |
| `references/` directory | — | No references directory; not applicable |
| `assets/` directory | — | No assets directory; not applicable |
| Body — step-by-step instructions | ✅ PASS | Three tracks each have numbered, sequential steps with clear actions per step |
| Body — examples | ✅ PASS | Concrete "Ship issue #2779" example with full before/after narrative |
| Body — edge cases | ✅ PASS | Recovery table covers four distinct failure points; "Red flags" section covers nine skip-step scenarios |

---

## What the Skill Gets Right

- **Three-track model is well-defined.** Quick-fix, clear-scope, and ambiguous tracks each have distinct numbered steps, making it easy for an agent to follow the correct path without ambiguity.
- **Recovery procedures are thorough.** The failure-point table maps each symptom to a precise recovery action rather than a vague "retry" instruction.
- **Red flags section is actionable.** Each red flag states the bad behavior and the corrective action in a single line — easy to scan and enforce.
- **Report shape is machine-parseable.** The fixed-format report block with consistent field names lets parent skills (e.g., `/auto-ship`) consume output reliably.
- **Anti-skip mechanism is explicit.** The skill calls out the "tasks already exist in the parent's list" reasoning failure by name, closing a real loophole.
- **Companion skill references are named.** `superpowers:writing-plans`, `pr-review-toolkit:code-reviewer`, `/decision-brief`, `/handle-review` are all referenced explicitly so an agent knows what to invoke.
- **Token and line budgets are comfortably under limits.** The body is lean (~1,450 tokens, ~148 lines) despite covering three full workflows.

---

## Violations (Must Fix)

### 1. Non-standard frontmatter fields must be nested under `metadata:`

The spec states: "Non-standard frontmatter fields must be nested under `metadata:`, not at top-level." Nine fields violate this.

**Current:**
```yaml
version: 1.0.0
author: Varun U
email: varun@zysk.tech
category: engineering-practice
tags:
  - github-issues
  - workflow
  - pr-creation
  - code-review
  - tdd
product: tms
sprint: 4
tested_with: claude-opus-4-7
user-invocable: true
```

**Fix:**
```yaml
metadata:
  version: 1.0.0
  author: Varun U
  email: varun@zysk.tech
  category: engineering-practice
  tags:
    - github-issues
    - workflow
    - pr-creation
    - code-review
    - tdd
  product: tms
  sprint: 4
  tested_with: claude-opus-4-7
  user-invocable: true
```

### 2. `license` field is missing

All skills should declare their licensing terms.

**Fix — add to frontmatter:**
```yaml
license: MIT
```
(or whichever license applies)

### 3. `compatibility` field is missing

The skill has hard external dependencies that must be documented so consumers know the prerequisites.

**Fix — add to frontmatter:**
```yaml
compatibility: "Requires: gh CLI, Node.js + npm (npx tsc, npm run lint/format/test), git with worktree support, GitHub Projects v2, companion skills: pr-review-toolkit, superpowers, decision-brief, handle-review"
```

---

## What's More Than Needed (Consider Restructuring)

- **`product: tms` and `sprint: 4`** are project-specific internal metadata that reduce portability. If the skill is intended for the skills registry (a shared resource), these fields convey no value to other consumers. Move them under `metadata:` (per violation #1) and document that they are project-scoped.
- **`email: varun@zysk.tech`** is a personal contact in a shared registry artifact. Consider whether this belongs here or only in a CONTRIBUTORS file.
- **Next.js/React helpers** (`next-best-practices`, `vercel-react-best-practices`) are referenced in the Rules section but guarded by "skip if not Next.js/React." This is appropriate as a conditional but could become a separate optional extension rather than inline noise for non-React consumers.

---

## What's Missing (Must Add)

1. **`license` field** — Required by spec quality standards. Add a license declaration to the frontmatter.
2. **`compatibility` field** — The skill invokes `gh`, `npx tsc`, `npm run lint`, `npm run format:check`, `npm run test:run`, git worktrees, and GitHub Projects v2 GraphQL mutations. None of these prerequisites are documented for a consumer evaluating whether to adopt the skill.
3. **`metadata:` wrapper for non-standard fields** — All nine custom frontmatter fields must be moved under `metadata:`.
4. **Stronger trigger keywords in `description`** — The description is accurate but written in implementation language. An agent matching user input like "ship issue #42", "implement this ticket", "start on issue", or "fix this bug from the board" would benefit from those phrases appearing in the description. Consider:

   ```
   "Ship a single GitHub issue end-to-end (quick-fix / clear-scope / ambiguous track). Use when asked to implement, fix, or ship a ticket, start work on an issue, or pick up a backlog item. Enforces self-review, simplify, verify, and board-move discipline on every run."
   ```

---

## Summary Table

| Area | Status | Detail |
|---|---|---|
| `name` field | ✅ Pass | Correct format, matches folder name |
| `description` field | ⚠️ Warn | Present and accurate; trigger keywords for agent discovery could be stronger |
| `license` field | ❌ Missing | Not declared anywhere in frontmatter |
| `compatibility` field | ❌ Missing | Significant external dependencies undocumented |
| `metadata` structure | ❌ Wrong | 9 non-standard fields at top level instead of under `metadata:` |
| Token budget | ✅ Pass | ~1,450 tokens (limit: 5,000) |
| Line budget | ✅ Pass | ~148 lines (limit: 500) |
| Body structure | ✅ Excellent | Step-by-step for all three tracks, examples, recovery table, red-flags checklist |
| Self-containment / portability | ⚠️ Warn | Companion skill references are named but not bundled; project-specific metadata (`product`, `sprint`) reduces portability |
