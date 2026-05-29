# ANALYSIS — decision-brief

> Generated against the [agentskills.io](https://agentskills.openml.io) standard.

---

## Overall Verdict

**Partially compliant.** The skill has a well-structured, high-quality body with excellent step-by-step instructions, a detailed template, a concrete example, and useful red-flag guidance. However, it fails on a structural spec requirement: multiple non-standard frontmatter fields (`version`, `author`, `email`, `category`, `tags`, `product`, `sprint`, `tested_with`, `user-invocable`) are declared at top-level instead of being nested under `metadata:`. The required `license` and optional `compatibility` fields are also absent.

---

## Spec Compliance Checklist

| Check | Status | Detail |
|---|---|---|
| `name` field format | PASS | `decision-brief` — lowercase, hyphens only, no leading/trailing hyphen, 14 chars (64 max), matches folder name |
| `description` present & non-empty | PASS | 188 chars, well within 1-1024 limit |
| `description` describes what it does | PASS | Clearly states it produces a lightweight decision record before implementing ambiguous work |
| `description` describes when to use it | PASS | Mentions scoping features, evaluating design options, deciding approach before writing code |
| `license` field | FAIL | Not present — required by spec |
| `compatibility` field | FAIL | Not present — optional but recommended for portability |
| `metadata` field structure | FAIL | `version`, `author`, `email`, `category`, `tags`, `product`, `sprint`, `tested_with`, `user-invocable` are all top-level fields; spec requires non-standard fields to be nested under `metadata:` |
| `allowed-tools` field | — | Not present; optional, no scripts requiring specific tools are invoked by the agent directly |
| Token budget (body) | PASS | ~1813 estimated tokens (body is 7,252 chars); well under 5000 token budget |
| Line budget (body) | PASS | 135 lines; well under 500-line limit |
| `scripts/` directory | — | No `scripts/` directory; the bash snippet in Step 5 is inlined in the skill body, not bundled as a script |
| `references/` directory | — | Not present; not required |
| `assets/` directory | — | Not present; not required |
| Body — step-by-step instructions | PASS | Clear numbered 5-step process covering the full workflow from drafting to label cleanup |
| Body — examples | PASS | One concrete end-to-end example with user input, Claude action, and result |
| Body — edge cases | PASS | "When NOT to use" section, "Red flags" section, and "Notes" section all address edge cases and misuse scenarios |

---

## What the Skill Gets Right

- The `name` field is perfectly formatted and matches the folder name exactly.
- The `description` is concise, specific, and includes good trigger keywords (`decision record`, `ADR`, `ambiguous work`, `scoping features`, `design options`, `before writing code`).
- The body is well under both the line budget (135/500) and token budget (~1813/5000), leaving room for future growth.
- The "When to use / When NOT to use" section provides clear, actionable scope guardrails.
- The numbered Steps section is unambiguous and covers the full lifecycle including the GitHub label side-effect.
- The embedded template is thorough and includes every section a useful decision record needs (Problem, Current State, Approach, Alternatives, Risks, Scope boundary, Decision, References).
- The "Red flags" section is genuinely useful — it teaches the agent not just what to do but what to avoid, with honest reasoning behind each flag.
- The "Quality check" section provides a self-verification checklist the agent can run before delivering output.
- The "Notes" section explicitly calls out the project-specific coupling (`tms-app`, `/auto-ship`) and tells users how to adapt the skill to their own context.
- The inline bash snippet for label removal includes error handling that distinguishes benign label-not-found cases from real failures — a good practice for automation scripts.

---

## Violations (Must Fix)

### 1. Non-standard frontmatter fields not nested under `metadata:`

The spec requires that all custom fields be nested under `metadata:`. The following fields are currently at top level and must be moved:

**Current:**
```yaml
version: 1.0.0
author: Varun U
email: varun@zysk.tech
category: engineering-practice
tags:
  - decision-record
  - scoping
  - planning
  - adr
  - github-issues
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
    - decision-record
    - scoping
    - planning
    - adr
    - github-issues
  product: tms
  sprint: 4
  tested_with: claude-opus-4-7
  user-invocable: true
```

### 2. Missing `license` field

The spec lists `license` as a required field. The skill has no license declaration.

**Fix:** Add a `license` field to the frontmatter, for example:
```yaml
license: MIT
```

---

## What's More Than Needed (Consider Restructuring)

- **Step 5 inline bash snippet:** The error-handling bash command in Step 5 is detailed and project-specific (`zyni-ai/tms-app`). For a portable skill, this is borderline too implementation-specific to live in the body. Consider moving it to `scripts/remove-investigation-label.sh` and referencing it from the body, which would also make the step easier to adapt per-project.
- **"Red flags" and "Quality check" sections:** Both are valuable, but they overlap slightly (e.g., both mention Current State and alternatives). This is minor and acceptable given the body is far under the line budget.

---

## What's Missing (Must Add)

1. **`license` field** — Required by spec. Add `license: MIT` (or appropriate license) to the frontmatter.
2. **`metadata:` nesting** — All non-standard frontmatter fields must move under `metadata:`. This is a structural spec violation affecting `version`, `author`, `email`, `category`, `tags`, `product`, `sprint`, `tested_with`, and `user-invocable`.
3. **`compatibility` field (recommended)** — The skill shells out to `gh` (GitHub CLI) in Step 5. Documenting this dependency helps users assess whether the skill will work in their environment. Example:
   ```yaml
   compatibility: "Requires GitHub CLI (gh) for label removal in Step 5. Step 5 can be skipped if gh is unavailable or /auto-ship is not in use."
   ```

---

## Summary Table

| Area | Status | Detail |
|---|---|---|
| `name` field | Pass | Correctly formatted, matches folder name |
| `description` field | Pass | Clear, specific, good trigger keywords |
| `license` field | Missing | Not present; required by spec |
| `compatibility` field | Missing | Not present; gh CLI dependency undocumented |
| `metadata` structure | Wrong | 9 non-standard fields declared at top level instead of under `metadata:` |
| Token budget | Pass | ~1813 tokens estimated; well under 5000 |
| Line budget | Pass | 135 lines; well under 500 |
| Body structure | Excellent | Step-by-step instructions, full template, example, quality checklist, red flags, edge cases |
| Self-containment / portability | Warn | Bash snippet and example hardcode `zyni-ai/tms-app`; Notes section mitigates this but portability could be improved by parameterising or scripting the repo reference |
