# ANALYSIS — backlog-burn-down

> Generated against the [agentskills.io](https://agentskills.openml.io) standard.

---

## Overall Verdict

**Partially compliant.** The skill has an excellent body — clear step-by-step instructions, a concrete output format, a worked example, good edge-case coverage, and strong anti-skip discipline. However, it carries nine non-standard frontmatter fields (`version`, `author`, `email`, `category`, `tags`, `product`, `sprint`, `tested_with`, `user-invocable`) at the top level instead of nesting them under `metadata:`, and it is missing both the required `license` field and the optional-but-recommended `compatibility` field. The body is also tightly coupled to a single organisation (`zyni-ai`) and project number (`18`), which limits portability.

---

## Spec Compliance Checklist

| Check | Status | Detail |
|---|---|---|
| `name` field format | PASS | `backlog-burn-down` — lowercase, hyphens only, no leading/trailing hyphens, 18 chars, matches folder name exactly |
| `description` present & non-empty | PASS | 222 chars, well within the 1-1024 limit |
| `description` describes what it does | PASS | Clearly explains scanning, stale-checking, classifying, bundling, and presenting a batch plan |
| `description` describes when to use it | WARN | Describes the action but lacks trigger-keyword phrases (e.g. "what should I work on", "plan my day") that appear only in the body |
| `license` field | FAIL | Field is absent; spec lists it as a required field |
| `compatibility` field | FAIL | Field is absent; no environment prerequisites documented (requires `gh` CLI, GitHub Projects v2, `git`) |
| `metadata` field structure | FAIL | Nine non-standard fields (`version`, `author`, `email`, `category`, `tags`, `product`, `sprint`, `tested_with`, `user-invocable`) are at top level instead of nested under `metadata:` |
| `allowed-tools` field | N/A | Not present; optional, not required |
| Token budget (body) | PASS | Body is approx 208 lines / 7,800 chars / 1,950 tokens — well within the 5,000-token budget |
| Line budget (body) | PASS | 208 lines — well within the 500-line limit |
| `scripts/` directory | N/A | No scripts/ directory; skill references external commands (`gh`, `git`) inline, which is acceptable |
| `references/` directory | N/A | No references/ directory; not required |
| `assets/` directory | N/A | No assets/ directory; not required |
| Body — step-by-step instructions | PASS | Five clearly numbered steps (0-5) with explicit actions, commands, and decision tables |
| Body — examples | PASS | Concrete example in the "Example" section and a full sample BATCH PLAN output block |
| Body — edge cases | PASS | "Red flags" section covers eight distinct failure modes; "When NOT to use" covers four mis-invocation cases |

---

## What the Skill Gets Right

- The `name` field is perfectly formatted and matches the folder name exactly.
- The description is concise and informative, summarising the full workflow in one sentence.
- Step 0 (TaskCreate discipline) is explicitly mandated as MANDATORY, enforcing consistency with sibling skills.
- The pagination warning in Step 1 (`first: 100` silently misses items) is a high-value, non-obvious gotcha that prevents silent data loss.
- The "bundle by mental model, not size" rule in Step 4 is well-explained with a concrete four-row example table.
- Step 5's BATCH PLAN output format is specified exactly, down to column labels and spacing, making the output predictable and parseable.
- The "Wait for user input" table maps eight distinct user-intent patterns to concrete next actions — thorough and unambiguous.
- The "Red flags" section is unusually thorough: eight anti-patterns with consequences explained, not just listed.
- The "How this skill compares" table cleanly positions this skill relative to its sibling skills, preventing mis-invocation.
- Token and line budgets are comfortably within limits (~1,950 tokens, 208 lines).

---

## Violations (Must Fix)

### 1. Nine non-standard frontmatter fields at top level (must nest under `metadata:`)

The spec states: "Non-standard frontmatter fields must be nested under `metadata:`, not at top-level." The following fields are non-standard and currently at the top level:

`version`, `author`, `email`, `category`, `tags`, `product`, `sprint`, `tested_with`, `user-invocable`

**Current:**
```yaml
version: 1.0.0
author: Varun U
email: varun@zysk.tech
category: engineering-practice
tags:
  - project-board
  - github
  - planning
  - triage
  - workflow
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
    - project-board
    - github
    - planning
    - triage
    - workflow
  product: tms
  sprint: 4
  tested_with: claude-opus-4-7
  user-invocable: true
```

### 2. `license` field is missing

The spec lists `license` as a required field. Add it to the frontmatter.

**Fix (example):**
```yaml
license: MIT
```

If the skill is proprietary or internal-only, use `license: proprietary` or `license: internal`.

### 3. `compatibility` field is missing

The skill requires `gh` CLI, GitHub Projects v2 access, `git`, and the Grep tool. Without a `compatibility` field, agents cannot determine whether the skill is runnable in the current environment.

**Fix:**
```yaml
compatibility: "Requires gh CLI (authenticated, Projects v2 scope), git, and a GitHub organisation with a Projects v2 board. Tested with claude-opus-4-7."
```

---

## What's More Than Needed (Consider Restructuring)

- The "Worktree strategy" section is one paragraph that defers entirely to `/auto-ship` Step 5. It adds no actionable information to this skill and could be removed or reduced to a single cross-reference line (e.g., "Worktree setup is owned by `/auto-ship`; see that skill for details.").
- The "Operating principle" section is motivational framing. It is useful context but could be folded into the Step 2 introduction to avoid a standalone section that adds no procedural content.

---

## What's Missing (Must Add)

1. **`license` field** — Required by spec. Add `license: <value>` to the frontmatter.

2. **`compatibility` field** — Add a one-line compatibility statement documenting that `gh` CLI (with Projects v2 scope), `git`, and a GitHub organisation/project are required. This is essential for portability.

3. **Trigger keywords in `description`** — The description explains what the skill does but omits the natural-language trigger phrases that agents use to match user intent. Phrases like "what should I work on", "plan my day", "burn down the backlog", and "show me Todo" appear only in the body's "When to use" section. Moving a representative set into the description improves agent discoverability.

   **Suggested description:**
   ```
   Use when the user asks "what should I work on?", "plan my day", "burn down the backlog", or "show me Todo". Scans the Todo column of a GitHub Projects v2 board, stale-checks each issue, classifies into quick-fix / clear-scope / ambiguous tracks, bundles by mental model, and presents a batch plan for the user to approve before any execution.
   ```
   (This is 346 chars, within the 1-1024 limit.)

4. **Portability callout for hardcoded org/project values** — The Notes section mentions swapping `zyni-ai` and project `18`, but the hardcoded values appear in a code block users may copy verbatim. Consider adding a bolded "Adapt before use" callout directly above the GraphQL code block in Step 1 to reduce misconfiguration risk.

---

## Summary Table

| Area | Status | Detail |
|---|---|---|
| `name` field | Pass | Valid format, matches folder name, 18 chars |
| `description` field | Warn | Present and accurate; missing trigger-keyword phrases for agent discovery |
| `license` field | Missing | Required field; completely absent |
| `compatibility` field | Missing | Not present; `gh` CLI, git, and GitHub Projects v2 are prerequisites |
| `metadata` structure | Wrong | Nine non-standard fields at top level; all must move under `metadata:` |
| Token budget | Pass | ~1,950 tokens — well within 5,000-token limit |
| Line budget | Pass | 208 lines — well within 500-line limit |
| Body structure | Excellent | Numbered steps, decision tables, concrete output format, worked example, red flags |
| Self-containment / portability | Fails | GraphQL query and stale-close command hardcode `zyni-ai` org and project `18`; sibling skill dependencies (`/auto-ship`, `/ship-issue`, `/triage-issues`, `/decision-brief`) are not documented as external prerequisites |
