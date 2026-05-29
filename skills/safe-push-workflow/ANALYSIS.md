# ANALYSIS — safe-push-workflow

> Generated against the [agentskills.io](https://agentskills.openml.io) standard.

---

## Overall Verdict

**Partially compliant.** The skill has a clear purpose, well-structured step-by-step body, and good examples, but it has several spec violations: multiple non-standard frontmatter fields are placed at the top level instead of under `metadata:`, and the required `license` and `compatibility` fields are absent. The description is functional but skewed toward "what" rather than "when", weakening agent trigger-keyword discovery.

---

## Spec Compliance Checklist

| Check | Status | Detail |
|---|---|---|
| `name` field format | PASS | `safe-push-workflow` — lowercase, hyphens only, no leading/trailing hyphens, 18 chars, exactly matches folder name |
| `description` present & non-empty | PASS | 130 chars, well within 1-1024 limit |
| `description` describes what it does | PASS | Clearly describes conflict detection before push |
| `description` describes when to use it | WARN | Explains the mechanism but lacks explicit trigger phrases ("push to qa", "create a PR", "send a branch") that agents use for discovery |
| `license` field | FAIL | Not present — field is missing |
| `compatibility` field | FAIL | Not present — skill has external dependencies (git, gh CLI) that must be documented here |
| `metadata` field structure | FAIL | `version`, `author`, `email`, `category`, `tags`, `product`, `sprint`, `tested_with` are all non-standard fields placed at the top level; they must be nested under `metadata:` |
| `allowed-tools` field | N/A | Not present (optional) |
| Token budget (body) | PASS | ~1041 tokens — well under the 5000-token recommendation |
| Line budget (body) | PASS | 140 body lines — well under the 500-line limit |
| `scripts/` directory | N/A | No scripts referenced; not applicable |
| `references/` directory | N/A | Not present; not applicable |
| `assets/` directory | N/A | Not present; not applicable |
| Body — step-by-step instructions | PASS | 9 numbered steps with bash commands and clear intent per step |
| Body — examples | PASS | Concrete example with user input to Claude action to result |
| Body — edge cases | WARN | Mentions stashing uncommitted changes and stopping on conflicts, but does not cover: detached HEAD state, no configured remote, gh CLI not authenticated, or branches that do not exist on remote yet |

---

## What the Skill Gets Right

- The `name` field is valid and exactly matches the folder name `safe-push-workflow`.
- Body is well within both the 500-line and 5000-token budgets (~140 lines, ~1041 tokens).
- Step-by-step instructions are clear, sequential, and include concrete bash commands.
- The "When to use / Do NOT activate" section is excellent — it helps agents avoid false-positive activation.
- The example section is concrete and traces a full user-to-result flow.
- The Notes section includes practical advice on three-dot vs two-dot diff syntax, which prevents a common mistake.
- The Safe Push Report template is a strong UX pattern — clear, structured, and actionable.

---

## Violations (Must Fix)

### 1. Non-standard frontmatter fields at top level (must be under `metadata:`)

The spec states: "Non-standard frontmatter fields MUST be nested under `metadata:`, not at top-level." The following fields are non-standard and currently placed at the top level: `version`, `author`, `email`, `category`, `tags`, `product`, `sprint`, `tested_with`.

**Current (wrong):**

```yaml
name: safe-push-workflow
description: Detects git conflicts before pushing a feature branch to any target branch by fetching remote state and diffing divergent changes.
version: 1.0.0
author: Ananth Raj L
email: ananth@zysk.tech
category: pre-deploy-safety
tags:
  - git
  - push-safety
  - conflict-detection
  - pull-request
product: zysk
sprint: 1
tested_with: claude-sonnet-4-6
```

**Fix:**

```yaml
name: safe-push-workflow
description: Detects git conflicts before pushing a feature branch to any target branch by fetching remote state and diffing divergent changes.
license: MIT
compatibility: Requires git >= 2.x and gh CLI >= 2.x installed and authenticated. Works on any OS with a bash-compatible shell.
metadata:
  version: 1.0.0
  author: Ananth Raj L
  email: ananth@zysk.tech
  category: pre-deploy-safety
  tags:
    - git
    - push-safety
    - conflict-detection
    - pull-request
  product: zysk
  sprint: 1
  tested_with: claude-sonnet-4-6
```

---

### 2. Missing `license` field

The spec lists `license` as a recognized top-level field. Omitting it leaves the skill without licensing terms, which is required for registry compliance.

**Fix:** Add `license: MIT` (or the appropriate license) as a top-level frontmatter field.

---

### 3. Missing `compatibility` field despite hard external dependencies

The skill explicitly requires `git` and `gh` CLI (Step 8). Without a `compatibility` field, agents and users have no machine-readable signal about prerequisites. The spec flags this as a failure when external tool dependencies exist.

**Fix:**

```yaml
compatibility: Requires git >= 2.x and gh CLI >= 2.x installed and authenticated on the system. Tested with claude-sonnet-4-6.
```

---

## What's More Than Needed (Consider Restructuring)

The `Notes` section contains one bullet that is largely a business justification ("Saves ~6-7 hours/month vs pushing blind..."). While interesting for a README, it adds marginal value to an agent executing the skill and could be moved to `metadata:` or removed from the body to keep the body focused on instructions.

---

## What's Missing (Must Add)

### 1. Trigger keywords in `description`

The description explains the mechanism well but does not include the specific trigger phrases agents look for. The body's "When to use" section has excellent trigger phrases ("push to qa", "create a PR", "push this to"), but agents use `description` for initial discovery — those keywords need to appear there too.

**Suggested description:**

```
Detects git conflicts before pushing or creating a PR. Activate when user says "push to qa", "push to uat", "create a PR", "send this branch to remote", or confirms a push with "yes" / "go ahead". Fetches remote state and diffs divergent changes so conflicts appear in your terminal, not on GitHub.
```

### 2. Edge case coverage in body

The following scenarios are not addressed:

- **Detached HEAD state:** `git branch --show-current` returns empty; the skill should detect this and abort with a message.
- **No remote configured:** `git fetch --all` will fail silently or error; the skill should check for a configured remote first.
- **Branch does not exist on remote yet:** `git pull origin <current-branch>` will fail on a first push; the skill should detect that `--set-upstream` is needed.
- **gh CLI not authenticated:** Step 8 will fail; the skill should instruct the user to run `gh auth login` if unauthenticated.

---

## Summary Table

| Area | Status | Detail |
|---|---|---|
| `name` field | Pass | Valid format, matches folder name exactly |
| `description` field | Warn | Present and descriptive, but lacks trigger keywords for agent discovery |
| `license` field | Missing | Not present anywhere in frontmatter |
| `compatibility` field | Missing | Not present; skill has hard dependencies on git and gh CLI |
| `metadata` structure | Wrong | 8 non-standard fields (version, author, email, category, tags, product, sprint, tested_with) placed at top level instead of under metadata: |
| Token budget | Pass | ~1041 tokens — well under the 5000-token limit |
| Line budget | Pass | 140 body lines — well under the 500-line limit |
| Body structure | Excellent | 9 clear numbered steps, bash commands, output template, example, notes |
| Self-containment / portability | Warn | No external file references, but edge cases for missing git/gh setup are unhandled |
