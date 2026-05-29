# ANALYSIS — git-workflow

> Generated against the [agentskills.io](https://agentskills.openml.io) standard.

---

## Overall Verdict

**Partially compliant.** The skill has a solid body structure with clear step-by-step instructions, good examples, and practical edge-case coverage. However, it contains several non-standard frontmatter fields placed at the top level instead of under `metadata:`, and it is missing the required `license` field. The `description` is functional but leans toward "what" rather than providing strong agent-discovery trigger keywords for "when."

---

## Spec Compliance Checklist

| Check | Status | Detail |
|---|---|---|
| `name` field format | ✅ PASS | `git-workflow` — lowercase, hyphens only, no leading/trailing hyphen, 12 chars, matches folder name exactly |
| `description` present & non-empty | ✅ PASS | 150 chars, well within 1–1024 limit |
| `description` describes what it does | ✅ PASS | Clearly states it applies git conventions for branches, commits, merges, PRs, force-pushes, and tags |
| `description` describes when to use it | ⚠️ WARN | Says "whenever Claude runs any git command" but lacks explicit trigger keywords that agents scan for during discovery |
| `license` field | ❌ FAIL | Not present — required field is missing |
| `compatibility` field | — | Not present; skill has no external tool dependencies beyond git, so absence is acceptable |
| `metadata` field structure | ❌ FAIL | Seven non-standard fields (`version`, `author`, `email`, `category`, `tags`, `product`, `sprint`, `tested_with`) are placed at top level instead of nested under `metadata:` |
| `allowed-tools` field | — | Not present (optional) |
| Token budget (body) | ✅ PASS | ~744 tokens — well under the 5000-token recommendation |
| Line budget (body) | ✅ PASS | 86 body lines — well under the 500-line recommendation |
| `scripts/` directory | — | Not present; skill has no scripts (none required) |
| `references/` directory | — | Not present; not needed for this skill |
| `assets/` directory | — | Not present; not needed for this skill |
| Body — step-by-step instructions | ✅ PASS | Six clearly numbered steps covering branch naming, commits, merging, PRs, force-push, and tagging |
| Body — examples | ✅ PASS | Concrete examples given: branch name `feat/login-retry`, commit `Add login retry on 401 #42`, bash snippet for force-with-lease, tag commands |
| Body — edge cases | ✅ PASS | Force-push edge case covered with `--force-with-lease` guidance and team notification requirement |

---

## What the Skill Gets Right

- Clean, numbered step-by-step structure that is easy for an agent to follow in sequence.
- Practical, opinionated guidance (e.g., prefer merge over rebase, never bare `--force`) that prevents common mistakes.
- Concrete examples embedded in each step — branch names, commit messages, and bash code snippets.
- Edge cases are addressed head-on: force-push is explicitly discouraged, then safely handled if unavoidable.
- Body is concise (~744 tokens, 86 lines) with no bloat, well within both budgets.
- `name` exactly matches the folder name and is spec-compliant in format.
- Clear "When to use" and "Do NOT activate when" guidance directly in the body aids agent activation logic.

---

## Violations (Must Fix)

### 1. Non-standard frontmatter fields at top level instead of under `metadata:`

The spec requires that all custom/non-standard fields be nested under `metadata:`. The following seven fields are placed directly at the top level of the frontmatter, which violates the spec:

- `version`
- `author`
- `email`
- `category`
- `tags`
- `product`
- `sprint`
- `tested_with`

**Current (wrong):**
```yaml
---
name: git-workflow
description: Applies this user's git conventions ...
version: 1.0.0
author: Arijit Saha
email: arijit.saha@zysk.tech
category: engineering-practice
tags:
  - git
  - version-control
  - commits
  - branching
  - pull-requests
product: zysk
sprint: 1
tested_with: claude-sonnet-4-6
---
```

**Fix:**
```yaml
---
name: git-workflow
description: Applies this user's git conventions ...
license: MIT
metadata:
  version: 1.0.0
  author: Arijit Saha
  email: arijit.saha@zysk.tech
  category: engineering-practice
  tags:
    - git
    - version-control
    - commits
    - branching
    - pull-requests
  product: zysk
  sprint: 1
  tested_with: claude-sonnet-4-6
---
```

### 2. Missing `license` field

The `license` field is a required field per spec and is absent entirely.

**Fix:** Add `license: MIT` (or the appropriate license) as a top-level frontmatter field.

---

## What's More Than Needed (Consider Restructuring)

The `email` field inside metadata is fine to keep, but be aware it exposes a personal/work email in a potentially public registry. Consider whether `author` alone is sufficient and whether `email` should be omitted or replaced with a GitHub handle or org reference.

---

## What's Missing (Must Add)

### 1. `license` field

Add a top-level `license` field to the frontmatter. Without it, consumers of the skill have no indication of the usage terms.

```yaml
license: MIT
```

### 2. Stronger trigger keywords in `description`

The current description ("whenever Claude runs any git command") works for humans but is weak for automated agent discovery. Agents scan descriptions for specific action keywords. Consider rewriting to include terms like `commit`, `branch`, `merge`, `pull request`, `rebase`, `push`, `tag`, and `version control` explicitly.

**Suggested revision:**
```
Enforces git conventions for branch naming, commit messages, merges, pull requests, force-push safety, and release tags. Use whenever running git commit, branch, merge, push, rebase, or tag commands, or when opening/updating a pull request.
```

---

## Summary Table

| Area | Status | Detail |
|---|---|---|
| `name` field | ✅ Pass | Valid format, matches folder name, 12 chars |
| `description` field | ⚠️ Warn | Present and accurate, but trigger keywords for agent discovery could be stronger |
| `license` field | ❌ Missing | Required field absent |
| `compatibility` field | — | Not required here; no external dependencies beyond git |
| `metadata` structure | ❌ Wrong | 7 non-standard fields placed at top level instead of nested under `metadata:` |
| Token budget | ✅ Pass | ~744 tokens — well under 5000-token limit |
| Line budget | ✅ Pass | 86 body lines — well under 500-line limit |
| Body structure | ✅ Excellent | Clear numbered steps, examples, edge cases, activation guidance |
| Self-containment / portability | ✅ Pass | No external scripts or absolute paths; git is universally available |
