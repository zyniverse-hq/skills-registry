# ANALYSIS — resume-hiring-manager

> Generated against the [agentskills.io](https://agentskills.openml.io) standard.

---

## Overall Verdict

**Partially compliant.** The skill has a well-formed `name`, a clear and keyword-rich `description`, and a well-structured body with good step-by-step instructions. However, it violates the spec's metadata structure rule by placing nine non-standard fields (`version`, `author`, `email`, `category`, `tags`, `product`, `sprint`, `tested_with`, `disable-model-invocation`) directly at the top level of the frontmatter instead of nesting them under `metadata:`. The `license` field is also absent.

---

## Spec Compliance Checklist

| Check | Status | Detail |
|---|---|---|
| `name` field format | ✅ PASS | `resume-hiring-manager` — lowercase, hyphens only, no leading/trailing hyphen, 22 chars (≤64), matches folder name exactly |
| `description` present & non-empty | ✅ PASS | 176 chars, within 1–1024 limit |
| `description` describes what it does | ✅ PASS | Clearly states it runs a mock interview, scores answers, and gives a hireability score |
| `description` describes when to use it | ✅ PASS | Implies activation context (interview prep, hiring manager roleplay) via keywords |
| `license` field | ❌ FAIL | Not present |
| `compatibility` field | — | Not present; skill has no declared external service/tool dependencies, so absence is acceptable |
| `metadata` field structure | ❌ FAIL | Nine non-standard fields (`version`, `author`, `email`, `category`, `tags`, `product`, `sprint`, `tested_with`, `disable-model-invocation`) are at top level; all must be nested under `metadata:` |
| `allowed-tools` field | ✅ PASS | Present — `"*"` (wildcard, experimental) |
| Token budget (body) | ✅ PASS | ~748 tokens — well under the 5000-token recommendation |
| Line budget (body) | ✅ PASS | 61 body lines — well under the 500-line limit |
| `scripts/` directory | — | Not applicable; skill has no scripts |
| `references/` directory | — | Not applicable; no external references required |
| `assets/` directory | — | Not applicable; no assets used |
| Body — step-by-step instructions | ✅ PASS | Clear two-round interview structure with ordered instructions, per-answer scoring steps, and a closing report format |
| Body — examples | ✅ PASS | Output section provides a concrete example of the final report format |
| Body — edge cases | ⚠️ WARN | Missing inputs are handled (ask one at a time), but no guidance on what to do if the user refuses to provide a resume, or how to handle non-English resumes or highly niche roles |

---

## What the Skill Gets Right

- `name` is perfectly formed: lowercase, hyphen-separated, matches folder name exactly, well under the 64-char limit.
- `description` is concise but information-dense, containing strong trigger keywords (`mock interview`, `hiring manager`, `hireability score`, `technical`, `behavioural`) that help agents identify when to activate this skill.
- Body is well under both the line (61 vs. 500) and token (~748 vs. 5000) budgets, leaving significant room for expansion if needed.
- The two-round interview structure (technical + behavioural) is clear and realistic, with explicit per-answer scoring criteria.
- The `When to use` section explicitly calls out a negative activation case (do NOT use for keyword/skills research), which helps agents avoid mis-triggering.
- `allowed-tools: "*"` is declared, satisfying the experimental field requirement.
- Required inputs are clearly enumerated with a fallback instruction (ask one at a time if missing).
- The `Notes` section clarifies that bracketed placeholders are runtime inputs, not template artefacts — a useful guard against misuse.

---

## Violations (Must Fix)

### 1. Non-Standard Frontmatter Fields Must Be Nested Under `metadata:`

The spec mandates that all custom (non-standard) fields be nested under a `metadata:` key. The following fields are currently at the top level of the frontmatter and violate this rule:

`version`, `author`, `email`, `category`, `tags`, `product`, `sprint`, `tested_with`, `disable-model-invocation`

**Current (wrong):**
```yaml
---
name: resume-hiring-manager
description: Runs a realistic mock interview...
version: 1.0.0
author: Arijit Saha
email: arijit.saha@zysk.tech
category: business-sales
tags:
  - resume
  - interview
  - mock-interview
  - career
  - hiring
product: zysk
sprint: 1
tested_with: claude-sonnet-4-6
disable-model-invocation: false
allowed-tools: "*"
---
```

**Fix:**
```yaml
---
name: resume-hiring-manager
description: Runs a realistic mock interview...
license: MIT
allowed-tools: "*"
metadata:
  version: 1.0.0
  author: Arijit Saha
  email: arijit.saha@zysk.tech
  category: business-sales
  tags:
    - resume
    - interview
    - mock-interview
    - career
    - hiring
  product: zysk
  sprint: 1
  tested_with: claude-sonnet-4-6
  disable-model-invocation: false
---
```

### 2. `license` Field Is Missing

The spec lists `license` as an optional field, but its absence means downstream consumers (agents, registries, aggregators) cannot determine usage rights.

**Fix:** Add a `license` field at the top level, for example:
```yaml
license: MIT
```

---

## What's More Than Needed (Consider Restructuring)

The `email` field inside `metadata` exposes a personal/organizational email address in a public skill file. While not a spec violation (once moved under `metadata:`), consider whether this is intentional and appropriate for the distribution context of this registry.

---

## What's Missing (Must Add)

### 1. `license` Field

No licensing terms are declared. Add a `license` field at the top level of the frontmatter to clarify how the skill may be used, shared, or modified.

```yaml
license: MIT
```

### 2. Additional Edge Case Coverage in Body

The body does not address:
- What happens if the user declines to provide a resume (the skill should clarify it can still run with generic questions but will be less tailored).
- How to handle highly niche or non-standard roles where the model may lack domain depth.
- Whether the skill supports non-English input/output.

Adding a brief `## Edge Cases` subsection would improve robustness and portability.

---

## Summary Table

| Area | Status | Detail |
|---|---|---|
| `name` field | ✅ Pass | Valid format, exact folder match, 22 chars |
| `description` field | ✅ Pass | 176 chars, strong trigger keywords, explains what and when |
| `license` field | ❌ Missing | Not present in frontmatter |
| `compatibility` field | — | Not present; no external tool dependencies declared, so acceptable |
| `metadata` structure | ❌ Wrong | 9 non-standard fields at top level; must be nested under `metadata:` |
| Token budget | ✅ Pass | ~748 tokens — well under 5000-token limit |
| Line budget | ✅ Pass | 61 body lines — well under 500-line limit |
| Body structure | ✅ Excellent | Clear rounds, per-answer scoring, closing report, negative activation guard |
| Self-containment / portability | ✅ Pass | No external scripts or file references; all instructions are inline |
