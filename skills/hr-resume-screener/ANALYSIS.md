# ANALYSIS — hr-resume-screener

> Generated against the [agentskills.io](https://agentskills.openml.io) standard.

---

## Overall Verdict

**Partially compliant.** The skill has a solid body structure with clear step-by-step instructions, good edge case coverage, and a well-formed name field. However, it is missing the required `license` field, lacks a `compatibility` field, and has multiple non-standard frontmatter fields (`version`, `author`, `email`, `category`, `tags`, `product`, `sprint`, `tested_with`) that must be nested under `metadata:` rather than placed at the top level.

---

## Spec Compliance Checklist

| Check | Status | Detail |
|---|---|---|
| `name` field format | PASS | `hr-resume-screener` — lowercase, hyphens only, no leading/trailing hyphens, 18 chars (within 64), matches folder name exactly |
| `description` present & non-empty | PASS | 189 chars, well within 1-1024 char limit |
| `description` describes what it does | PASS | Clearly states: screen resume against JD, return FIT/PARTIAL FIT/NOT A FIT verdict with requirement match, strengths, gaps, salary check, Excel-ready row |
| `description` describes when to use it | WARN | Description explains the output well but does not explicitly call out trigger phrases; trigger keywords are present (resume, screening, JD) but "when to use" context is weak in the one-liner |
| `license` field | FAIL | Not present — required field is missing |
| `compatibility` field | FAIL | Not present — skill references file uploads (PDF, Word .docx) which implies tool/environment dependencies; should document required capabilities |
| `metadata` field structure | FAIL | Non-standard fields `version`, `author`, `email`, `category`, `tags`, `product`, `sprint`, `tested_with` are placed at the top level instead of nested under `metadata:` |
| `allowed-tools` field | — | Not present (optional) |
| Token budget (body) | PASS | ~1583 tokens — well under the 5000-token recommendation |
| Line budget (body) | PASS | 188 body lines — well under the 500-line recommendation |
| `scripts/` directory | — | No scripts referenced or needed; not applicable |
| `references/` directory | — | No references directory; not applicable |
| `assets/` directory | — | No assets directory; not applicable |
| Body — step-by-step instructions | PASS | Five clearly numbered steps (Step 0-5) with explicit instructions at each stage |
| Body — examples | PASS | Inline examples provided in the report template (Step 5), verdict logic table, salary band table, and Excel row format |
| Body — edge cases | PASS | Dedicated edge case table covering 5 scenarios: vague JD, thin resume, overqualified candidate, missing salary, non-English resume |

---

## What the Skill Gets Right

- The `name` field is perfectly formatted: lowercase, hyphens only, matches the folder name `hr-resume-screener` exactly.
- The body is well under both the 500-line and 5000-token budgets (~188 lines, ~1583 tokens), leaving ample room for growth.
- Step-by-step instructions are excellent — numbered steps 0 through 5 guide the agent through input collection, extraction, matching, salary check, and report generation with no ambiguity.
- The verdict logic is codified in a clear decision table (Step 3) rather than left to agent interpretation, which greatly reduces inconsistent outputs.
- Edge cases are comprehensively covered in a structured table with concrete handling instructions.
- The output template (Step 5) is detailed and prescriptive, ensuring consistent report formatting across every invocation.
- The "Do NOT activate when" guard clause in the "When to use" section prevents the skill from partially running with incomplete inputs.
- The Excel row summary is a practical, high-value deliverable that distinguishes this skill from a generic resume-review prompt.

---

## Violations (Must Fix)

### 1. Missing `license` Field

The spec requires a `license` field. The current frontmatter does not include one.

**Current (wrong):**
```yaml
name: hr-resume-screener
description: Screen a candidate resume...
version: 1.0.0
author: Deepak Padmanabha
```

**Fix:**
```yaml
name: hr-resume-screener
description: Screen a candidate resume...
license: MIT
```

---

### 2. Non-Standard Fields at Top Level Instead of Under `metadata:`

The spec states: "Non-standard frontmatter fields MUST be nested under `metadata:`, not at top-level." The following fields are non-standard and are currently at the top level: `version`, `author`, `email`, `category`, `tags`, `product`, `sprint`, `tested_with`.

**Current (wrong):**
```yaml
name: hr-resume-screener
description: Screen a candidate resume...
version: 1.0.0
author: Deepak Padmanabha
email: deepak@zysk.tech
category: business-sales
tags:
  - hr
  - resume
  - screening
  - jd-matching
  - recruitment
product: zysk
sprint: 1
tested_with: claude-sonnet-4-6
```

**Fix:**
```yaml
name: hr-resume-screener
description: Screen a candidate resume...
license: MIT
metadata:
  version: 1.0.0
  author: Deepak Padmanabha
  email: deepak@zysk.tech
  category: business-sales
  tags:
    - hr
    - resume
    - screening
    - jd-matching
    - recruitment
  product: zysk
  sprint: 1
  tested_with: claude-sonnet-4-6
```

---

### 3. Missing `compatibility` Field

The skill explicitly references PDF and Word (.docx) file uploads, which requires multimodal file-reading capabilities. The spec requires documenting environment prerequisites when a skill has external tool dependencies.

**Current (wrong):**
```yaml
# no compatibility field present
```

**Fix:**
```yaml
compatibility: Requires a multimodal LLM capable of reading uploaded PDF and Word (.docx) files, or text pasted directly in chat. No external API or tool integrations required.
```

---

## What's More Than Needed (Consider Restructuring)

The output template in Step 5 embeds the full report scaffold (including emoji headers, horizontal rules, and every table) inline in the instructions. While functional, this makes the instructions section visually heavy. Consider moving the report template to a dedicated `## Output Template` section after the steps, keeping the steps focused on logic and the template focused on formatting. This is a stylistic suggestion, not a spec violation.

---

## What's Missing (Must Add)

### 1. `license` Field

Add a `license` field to the frontmatter. Choose an appropriate license (e.g., `MIT`, `Apache-2.0`, or a proprietary label if applicable).

### 2. `compatibility` Field

Add a `compatibility` field documenting that file-upload capability (PDF/Word) is needed, or that the skill works with pasted text as a fallback. Keep it under 500 chars.

### 3. Move All Non-Standard Fields Under `metadata:`

Wrap `version`, `author`, `email`, `category`, `tags`, `product`, `sprint`, and `tested_with` under a single `metadata:` key as shown in the fix above.

---

## Summary Table

| Area | Status | Detail |
|---|---|---|
| `name` field | Pass | Lowercase, hyphens only, matches folder name, 18 chars |
| `description` field | Warn | Present and descriptive; trigger keywords could be stronger for agent discovery |
| `license` field | Missing | Required field absent from frontmatter |
| `compatibility` field | Missing | Skill has file-upload dependencies; prerequisites not documented |
| `metadata` structure | Wrong | 8 non-standard fields placed at top level instead of under `metadata:` |
| Token budget | Pass | ~1583 tokens — well under 5000-token recommendation |
| Line budget | Pass | 188 body lines — well under 500-line recommendation |
| Body structure | Excellent | Numbered steps, verdict logic table, salary band table, output template, edge case table |
| Self-containment / portability | Pass | No external scripts, API keys, or absolute paths; fully self-contained |
