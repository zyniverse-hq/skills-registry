# ANALYSIS — daily-status

> Generated against the [agentskills.io](https://agentskills.openml.io) standard.

---

## Overall Verdict

**Partially compliant.** The skill has a well-written description with clear trigger keywords, excellent body structure with step-by-step instructions, good examples, and properly bundled supporting files. However, it is missing required `license` and `compatibility` fields, and eight non-standard top-level frontmatter fields (`version`, `author`, `email`, `category`, `tags`, `product`, `sprint`, `tested_with`) must be nested under `metadata:` per spec rules.

---

## Spec Compliance Checklist

| Check | Status | Detail |
|---|---|---|
| `name` field format | PASS | `daily-status` lowercase+hyphens only, no leading/trailing hyphen, 12 chars (<=64), exactly matches folder name |
| `description` present & non-empty | PASS | 270 chars, well within 1-1024 char limit |
| `description` describes what it does | PASS | Clearly states it generates an end-of-day client status report by scanning git commits, uncommitted changes, and GitHub PRs |
| `description` describes when to use it | PASS | Includes explicit trigger phrases: "daily status", "EOD report", "client update", "/daily-status" |
| `license` field | FAIL | Not present — required field is missing |
| `compatibility` field | FAIL | Not present — skill has external dependencies (python3, git, gh CLI) that should be documented here |
| `metadata` field structure | FAIL | 8 non-standard fields at top level (version, author, email, category, tags, product, sprint, tested_with) must be nested under metadata: |
| `allowed-tools` field | N/A | Not present (optional) |
| Token budget (body) | PASS | ~2603 tokens — well under the 5000-token recommendation |
| Line budget (body) | PASS | 165 body lines — well under the 500-line recommendation |
| `scripts/` directory | PASS | scripts/collect_activity.py is bundled inside the skill folder |
| `references/` directory | PASS | references/example-report.md is present |
| `assets/` directory | PASS | assets/report-template.txt and assets/config.example.json are present |
| Body — step-by-step instructions | PASS | Five clearly numbered and titled steps with sub-steps (Step 2a) |
| Body — examples | PASS | Example section with trigger phrase, expected Claude behavior, and pointer to worked output |
| Body — edge cases | PASS | Covers: zero items detected, gh unavailable, uncommitted-only work, missing config file |

---

## What the Skill Gets Right

- The name field is correctly formatted and exactly matches the folder name daily-status.
- The description is concise and packs in multiple high-value trigger keywords (daily status, EOD report, client update, /daily-status) while also stating what the skill does.
- Body structure is exemplary: five ordered steps, a dedicated sub-step (2a) for an important edge case, an Output section, a Rules section, an Example section, and a Files manifest — all under 165 lines.
- Edge cases are handled explicitly: no git activity today, gh CLI not authenticated, uncommitted-only work, and missing config file.
- Supporting files (scripts/, assets/, references/) are all bundled inside the skill folder and referenced with relative paths, making the skill fully self-contained and portable.
- The rationale for design decisions (why a script instead of inline bash, why one question at a time) is included inline, which aids agent understanding.

---

## Violations (Must Fix)

### 1. Eight non-standard fields are at top level instead of under metadata:

The spec requires that all custom/non-standard frontmatter fields be nested under metadata:. Fields version, author, email, category, tags, product, sprint, and tested_with are not part of the spec defined top-level fields and must be moved.

**Current (wrong):**
```yaml
---
name: daily-status
description: ...
version: 1.2.0
author: Shilpa VP
email: shilpa@zysk.tech
category: comms
tags:
  - daily-status
  - eod-report
  - git
  - github
  - reporting
product: zysk
sprint: 1
tested_with: claude-opus-4-7
---
```

**Fix:**
```yaml
---
name: daily-status
description: Generate the end-of-day client status report by scanning today's git commits, uncommitted changes, and GitHub PRs, then interviewing the user to classify each item. Use whenever the user asks for their daily status, EOD report, or client update — or types /daily-status.
license: MIT
compatibility: Requires Python 3.8+, git CLI, and optionally gh CLI (GitHub CLI). Runs on macOS/Linux. Windows support untested.
metadata:
  version: 1.2.0
  author: Shilpa VP
  email: shilpa@zysk.tech
  category: comms
  tags:
    - daily-status
    - eod-report
    - git
    - github
    - reporting
  product: zysk
  sprint: 1
  tested_with: claude-opus-4-7
---
```

### 2. license field is missing

The license field is a defined spec field and is absent from the frontmatter.

**Fix:** Add a license field to the frontmatter. Example:
```yaml
license: MIT
```

### 3. compatibility field is missing despite external tool dependencies

The skill requires python3, git, and optionally gh CLI — environmental prerequisites that are not documented in the frontmatter. The spec requires compatibility when such prerequisites exist.

**Fix:** Add a compatibility field (max 500 chars) describing the runtime requirements. Example:
```yaml
compatibility: Requires Python 3.8+, git CLI, and optionally gh CLI (GitHub CLI) for PR data. Tested on macOS and Linux. Windows support is untested.
```

---

## What is More Than Needed (Consider Restructuring)

The inline rationale paragraphs ("Why a script instead of inline bash", "Why one at a time") are valuable for human readers but add token cost. Consider condensing them to a single sentence each, or moving them to a Design Notes section at the end so the step-by-step flow reads more cleanly on first activation.

---

## What is Missing (Must Add)

### 1. license field
Add a license field at the top level of the frontmatter (e.g., license: MIT).

### 2. compatibility field
Add a compatibility field documenting that python3 (3.8+), git, and optionally gh CLI are required. This prevents silent failures when the skill is used in an environment that lacks these tools.

---

## Summary Table

| Area | Status | Detail |
|---|---|---|
| `name` field | Pass | Valid format, matches folder name |
| `description` field | Pass | 270 chars, clear what+when, strong trigger keywords |
| `license` field | Missing | Must be added at frontmatter top level |
| `compatibility` field | Missing | Must be added; skill has python3/git/gh CLI dependencies |
| `metadata` structure | Wrong | 8 non-standard fields at top level must move under metadata: |
| Token budget | Pass | ~2603 tokens — well under 5000-token recommendation |
| Line budget | Pass | 165 body lines — well under 500-line recommendation |
| Body structure | Excellent | Numbered steps, sub-steps, edge cases, examples, rules, files manifest |
| Self-containment / portability | Pass | All scripts and assets bundled in skill folder; relative paths used throughout |
