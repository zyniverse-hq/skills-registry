# ANALYSIS — resume-recruiter

> Generated against the [agentskills.io](https://agentskills.openml.io) standard.

---

## Overall Verdict

**Partially compliant.** The skill has a well-structured body with clear steps, good use-case framing, and a helpful output spec. However, it has significant frontmatter violations: multiple non-standard fields (`version`, `author`, `email`, `category`, `tags`, `product`, `sprint`, `tested_with`, `disable-model-invocation`) are declared at the top level instead of being nested under `metadata:`, and the required `license` field is absent.

---

## Spec Compliance Checklist

| Check | Status | Detail |
|---|---|---|
| `name` field format | PASS | "resume-recruiter" — lowercase, hyphens only, no leading/trailing hyphens, 15 chars, matches folder name exactly |
| `description` present & non-empty | PASS | 163 chars — within the 1-1024 char limit |
| `description` describes what it does | PASS | Clearly states it surfaces top keywords, flags missing ones, names trending skills, and lists buzzwords to cut |
| `description` describes when to use it | WARN | Implies resume/recruiter context but does not explicitly state trigger phrases an agent would match on (e.g., "optimize my resume", "ATS keywords", "keyword gap") |
| `license` field | FAIL | Not present — required by spec |
| `compatibility` field | FAIL | Not present; skill uses `allowed-tools: "*"` indicating broad tool access with no documented environment prerequisites |
| `metadata` field structure | FAIL | Nine non-standard fields (`version`, `author`, `email`, `category`, `tags`, `product`, `sprint`, `tested_with`, `disable-model-invocation`) are at the top level instead of nested under `metadata:` |
| `allowed-tools` field | WARN | Present as `"*"` (wildcard string) — spec defines this as a space-separated list of named tools; a wildcard is experimental and undocumented in the spec |
| Token budget (body) | PASS | ~525 tokens — well under the 5000-token recommendation |
| Line budget (body) | PASS | ~47 body lines — well under the 500-line limit |
| `scripts/` directory | N/A | Not present (no scripts needed for this skill) |
| `references/` directory | N/A | Not present (not required) |
| `assets/` directory | N/A | Not present (not required) |
| Body — step-by-step instructions | PASS | Five numbered steps clearly guide the agent through the analysis |
| Body — examples | WARN | Output section describes example content but no concrete sample output is shown |
| Body — edge cases | WARN | Only one negative case covered ("do NOT activate when"); missing edges like partial resumes, multi-role searches, or non-English resumes |

---

## What the Skill Gets Right

- The `name` field is perfectly formatted and matches the folder name exactly.
- The description is concise and accurately conveys the skill's purpose.
- The body has a clear, numbered step sequence that gives the agent an unambiguous execution path.
- The "When to use / Do NOT activate when" framing is a good pattern for agent disambiguation.
- Required inputs are explicitly listed with a "collect one at a time" instruction, reducing interaction errors.
- The output section specifies format, delivery location, and example content — all useful for agent and user alignment.
- Token and line budgets are comfortably within limits, leaving room for future expansion.

---

## Violations (Must Fix)

### 1. Non-standard frontmatter fields not nested under `metadata:`

The spec states: "Non-standard frontmatter fields MUST be nested under `metadata:`, not at top-level." The following nine fields are currently at the top level and must be moved under a `metadata:` key: `version`, `author`, `email`, `category`, `tags`, `product`, `sprint`, `tested_with`, `disable-model-invocation`.

Current (wrong):

  version: 1.0.0
  author: Arijit Saha
  email: arijit.saha@zysk.tech
  category: business-sales
  tags:
    - resume
    - recruiter
    - keywords
    - career
    - ats
  product: zysk
  sprint: 1
  tested_with: claude-sonnet-4-6
  disable-model-invocation: false

Fix:

  metadata:
    version: 1.0.0
    author: Arijit Saha
    email: arijit.saha@zysk.tech
    category: business-sales
    tags:
      - resume
      - recruiter
      - keywords
      - career
      - ats
    product: zysk
    sprint: 1
    tested_with: claude-sonnet-4-6
    disable-model-invocation: false

---

### 2. `license` field is absent

The spec lists `license` as an optional but important field. Omitting it leaves downstream users with no clarity on usage rights.

Fix — add after `description`:

  license: MIT

---

### 3. `allowed-tools: "*"` uses an undocumented wildcard format

The spec defines `allowed-tools` as "a space-separated list of pre-approved tools." A bare `"*"` wildcard is not part of the documented format and is marked experimental. Using it grants all tools without enumeration, which reduces auditability.

Current:

  allowed-tools: "*"

Fix — either remove it (let the runtime decide) or enumerate tools actually needed:

  allowed-tools: Read Write Bash

---

## What's More Than Needed (Consider Restructuring)

The `Output` section largely restates what was already said in `Steps`. The "Example" sub-bullet under Output is a prose description of the output rather than an actual sample. Consider either replacing it with a short concrete example or merging the output spec into the Steps section to avoid duplication.

---

## What's Missing (Must Add)

### 1. `compatibility` field

The skill uses `allowed-tools: "*"` which implies broad tool access. The `compatibility` field should document any environment prerequisites so consumers know where the skill can run.

Suggested addition after `license`:

  compatibility: Requires a Claude model with tool-use support. Tested with claude-sonnet-4-6. No external APIs or file system access needed; all analysis is performed in-context.

### 2. Concrete example output in the body

The spec requires examples of how/when to use the skill. The current "Example" text describes the structure but shows no sample data. Add a short illustrative snippet — even a 5-item mock keyword list — so users and agents can calibrate expectations.

### 3. Additional edge cases

Only one negative case is documented. Consider adding:
- What to do if the user pastes a resume in a language other than English.
- What to do if the target role is very niche or emerging (few live job posts to pattern-match against).
- How to handle a user who provides multiple target roles.

---

## Summary Table

| Area | Status | Detail |
|---|---|---|
| `name` field | Pass | Perfectly formatted, matches folder name |
| `description` field | Warn | Present and accurate but lacks explicit agent-trigger keywords |
| `license` field | Missing | Must be added |
| `compatibility` field | Missing | No environment prerequisites documented despite broad tool access |
| `metadata` structure | Wrong | Nine non-standard fields at top level; must be nested under `metadata:` |
| Token budget | Pass | ~525 tokens — well within the 5000-token limit |
| Line budget | Pass | ~47 body lines — well within the 500-line limit |
| Body structure | Adequate | Clear steps and output spec; weak on concrete examples and edge cases |
| Self-containment / portability | Pass | No external file references; all instructions are inline |
