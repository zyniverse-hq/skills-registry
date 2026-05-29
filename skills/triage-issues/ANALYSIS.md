# ANALYSIS — triage-issues

> Generated against the [agentskills.io](https://agentskills.openml.io) standard.

---

## Overall Verdict

**Partially compliant.** The skill body is well-structured with clear step-by-step instructions, a useful approval gate, and strong edge-case coverage (pagination caps, mutation ordering, duplicate detection). However, numerous non-standard frontmatter fields (`version`, `author`, `email`, `category`, `tags`, `product`, `sprint`, `tested_with`, `user-invocable`) are placed at the top level instead of under `metadata:`, and the required `license` and `compatibility` fields are absent. The skill is also highly TMS-specific (hardcoded org, project number, and field IDs), which limits portability despite the advisory note in the body.

---

## Spec Compliance Checklist

| Check | Status | Detail |
|---|---|---|
| `name` field format | PASS | `triage-issues` — lowercase, hyphens only, no leading/trailing hyphens, 13 chars, matches folder name exactly |
| `description` present and non-empty | PASS | 221 chars, well within the 1-1024 char limit |
| `description` describes what it does | PASS | Clearly states it promotes Backlog issues to Todo, derives fields from labels, and flags duplicates |
| `description` describes when to use it | WARN | Implies use via context but lacks explicit trigger phrases like "triage", "backlog", "weekly triage", "project board hygiene" that agents can match on |
| `license` field | FAIL | Missing — required field not present |
| `compatibility` field | FAIL | Missing — `gh` CLI, GitHub Projects v2 access, and GraphQL API access are all prerequisites and should be documented |
| `metadata` field structure | FAIL | `version`, `author`, `email`, `category`, `tags`, `product`, `sprint`, `tested_with`, `user-invocable` are all at top level; spec requires non-standard fields nested under `metadata:` |
| `allowed-tools` field | N/A | Not present — optional, acceptable to omit |
| Token budget (body) | PASS | ~4001 tokens estimated (body: 16,004 chars / 4); within the ~5000-token budget |
| Line budget (body) | PASS | 340 lines — under the 400-line warn threshold and well under the 500-line hard limit |
| `scripts/` directory | N/A | Not present — not required; skill uses inline `gh api graphql` commands directly |
| `references/` directory | N/A | Not present — not required |
| `assets/` directory | N/A | Not present — not required |
| Body — step-by-step instructions | PASS | Steps 0-8 are explicitly numbered and sequenced; each step has a clear action |
| Body — examples | PASS | "Example" section has a concrete user-says / Claude-does / result walkthrough |
| Body — edge cases | PASS | Red flags section covers 7 distinct failure modes including pagination cap, mutation ordering, duplicate handling |

---

## What the Skill Gets Right

- **Step 0 mandatory task creation** is a good anti-skip discipline for multi-step workflows — explicitly enforced before any reads or writes.
- **Approval gate at Step 6** before any writes is excellent UX; it shows the triage table and lists acceptable user responses precisely.
- **Pagination loop** for GitHub Projects v2 is correctly specified with cursor-based pagination and the `first: 100` hard cap clearly documented.
- **Mutation sequencing** is well-reasoned: field mutations before status promotion, sequential not parallel, with per-item partial-failure tracking.
- **Jaccard similarity heuristic** for duplicate detection is concrete and implementable, with the `min >= 5` token guard and explicit decision to never auto-close.
- **"Leave unset" philosophy** for Module and Severity is clearly justified and repeated in both the step instructions and the Red flags section — prevents confidently-wrong data.
- **Stale report** is correctly scoped to read-only — defers to existing repo automation, does not interfere.
- **Output section** clearly distinguishes what is printed vs. what is mutated vs. side effects.
- **Notes section** explicitly acknowledges TMS-specific hardcoded values and tells adapters what to swap.

---

## Violations (Must Fix)

### 1. Non-standard frontmatter fields at top level (spec violation)

The spec requires all non-standard fields to be nested under `metadata:`. The following fields are non-standard and placed at top level: `version`, `author`, `email`, `category`, `tags`, `product`, `sprint`, `tested_with`, `user-invocable`.

**Current (abbreviated):**
```yaml
version: 1.0.0
author: Varun U
tags: [...]
product: tms
```

**Fix — wrap all non-standard fields:**
```yaml
metadata:
  version: 1.0.0
  author: Varun U
  email: varun@zysk.tech
  category: engineering-practice
  tags:
    - project-board
    - github
    - triage
    - graphql
    - workflow
  product: tms
  sprint: 4
  tested_with: claude-opus-4-7
  user-invocable: true
```

### 2. Missing `license` field

The `license` field is required by the spec. Add to frontmatter:
```yaml
license: MIT
```

### 3. Missing `compatibility` field

The skill requires `gh` CLI with GitHub Projects v2 access and GraphQL API permissions. These are non-trivial prerequisites. Add to frontmatter:
```yaml
compatibility: "Requires gh CLI (v2.20+) authenticated with a token scoped to read:org, project, write:org. GitHub Projects v2 only. Target org and project number must be updated for non-TMS deployments."
```

---

## What Is More Than Needed (Consider Restructuring)

- **Hardcoded GraphQL IDs in the body** (`PVT_kwDOCrP2y84BUSTb`, `PVTSSF_*`, `c2b8c846`) appear directly in Step 7 mutation blocks. The skill itself states in Red flags that "IDs live in CLAUDE.md as the single source of truth." This is a contradiction: the mutation code embeds the IDs while the text says not to duplicate them. Replace hardcoded IDs in code blocks with placeholders like `<fieldId-from-CLAUDE.md>`, or add a note that the blocks are illustrative only.

- **Step 2 Priority table duplicates CLAUDE.md.** The option ID table (four priority rows with hex IDs) is exactly the kind of data the body says should live only in CLAUDE.md. Removing it reduces drift risk and shortens the body.

- **Red flags section is slightly repetitive** with Step instructions — for example, "Running mutations in parallel" is already addressed in Step 7. The section is useful as a summary but some bullets re-explain rather than add new information.

---

## What Is Missing (Must Add)

1. **`license` field in frontmatter** — required by spec. Add `license: MIT` (or whichever license applies).

2. **`compatibility` field in frontmatter** — document `gh` CLI version requirement, required GitHub token scopes, and Projects v2 constraint.

3. **`metadata:` wrapper for all non-standard fields** — move `version`, `author`, `email`, `category`, `tags`, `product`, `sprint`, `tested_with`, `user-invocable` under `metadata:`.

4. **Trigger keywords in `description`** — add terms like "triage", "backlog", "weekly triage", "project board" so agent discovery can match on common phrases. Example improvement:
   > "Triage GitHub Projects v2 Backlog: promotes issues to Todo, derives Priority/Area/Module from labels and title heuristics, flags missing labels and suspected duplicates, requires user approval before any mutations. Use for weekly triage cadence or pre-sprint board hygiene."

5. **Resolution of the CLAUDE.md reference dependency** — the skill explicitly depends on an external `CLAUDE.md` file for field IDs and option IDs, limiting self-containment. Either inline the required ID table, or add a clear statement in `compatibility` that this skill requires a properly configured `CLAUDE.md` in the repo root with the "Project Board Operations" section present.

---

## Summary Table

| Area | Status | Detail |
|---|---|---|
| `name` field | Pass | Valid format, matches folder name `triage-issues` |
| `description` field | Warn | Descriptive but lacks trigger keywords for agent discovery |
| `license` field | Missing | Not present; required by spec |
| `compatibility` field | Missing | Not present; `gh` CLI + GitHub Projects v2 + token scopes are undocumented prerequisites |
| `metadata` structure | Wrong | 9 non-standard fields sit at top level instead of under `metadata:` |
| Token budget | Pass | ~4001 tokens estimated; within the ~5000-token budget |
| Line budget | Pass | 340 lines; under the 400-line warn threshold |
| Body structure | Excellent | Numbered steps, approval gate, examples, edge cases, red flags — thorough and well-organized |
| Self-containment / portability | Fails | Depends on external `CLAUDE.md` for all field/option IDs; hardcoded org, project, and field IDs throughout |