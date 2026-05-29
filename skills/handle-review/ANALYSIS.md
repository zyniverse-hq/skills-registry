# ANALYSIS — handle-review

> Generated against the [agentskills.io](https://agentskills.openml.io) standard.

---

## Overall Verdict

**Partially compliant.** The skill body is well-structured, step-by-step, and genuinely useful — the triage workflow, verdict taxonomy, and human-approval gate are all strong. However, it has two significant spec violations: nine non-standard frontmatter fields (`version`, `author`, `email`, `category`, `tags`, `product`, `sprint`, `tested_with`, `user-invocable`) are declared at the top level instead of under a `metadata:` key, and both the required `license` field and the recommended `compatibility` field are absent.

---

## Spec Compliance Checklist

| Check | Status | Detail |
|---|---|---|
| `name` field format | PASS | `handle-review` — lowercase, hyphens only, no leading/trailing hyphen, 13 chars (64 max), matches folder name |
| `description` present & non-empty | PASS | 156 chars, well within 1-1024 range |
| `description` describes what it does | PASS | Clearly explains triage, classify, fix, reply, push-once workflow |
| `description` describes when to use it | PASS | Implies PR review comment context; trigger keywords are present |
| `license` field | FAIL | Field is missing entirely |
| `compatibility` field | FAIL | Field is missing entirely |
| `metadata` field structure | FAIL | Nine non-standard fields (`version`, `author`, `email`, `category`, `tags`, `product`, `sprint`, `tested_with`, `user-invocable`) are at top level, not nested under `metadata:` |
| `allowed-tools` field | N/A | Optional; not present |
| Token budget (body) | PASS | 189 body lines / ~12,098 chars = ~3,025 tokens (well under 5,000 warn threshold) |
| Line budget (body) | PASS | 189 body lines (under 400 warn / 500 fail thresholds) |
| `scripts/` directory | N/A | No scripts bundled; skill uses inline `gh`/`git` commands directly |
| `references/` directory | N/A | Not present; not required |
| `assets/` directory | N/A | Not present; not required |
| Body — step-by-step instructions | PASS | 8 clearly numbered steps with explicit ordering and conditionals |
| Body — examples | PASS | Concrete example with PR number, what Claude does, and expected result |
| Body — edge cases | PASS | Red flags section, auto-filter for already-handled threads, duplicate-reply prevention, round-3+ simplify rule |

---

## What the Skill Gets Right

- **Triage-first philosophy is clearly stated and enforced.** The root problem framing ("fix to re-review to fix loop") is immediately actionable and explains why the workflow matters.
- **Step 4's human-approval gate is excellent.** The response-intent matching table (not exact-string matching) is thoughtful and prevents both over-permissive and over-restrictive parsing.
- **Verdict taxonomy is precise and complete.** Seven distinct verdicts with unambiguous meanings and distinct artifact outputs — no overlap, no ambiguity.
- **Duplicate-reply prevention is non-obvious and well-documented.** The `ALREADY_HANDLED` set construction, including the ordering caveat (don't drop the author's own comments before computing the set), shows real operational experience.
- **Step 6 self-review conditions are explicit.** When to run, when to skip, and the round-3+ escalation path are all specified — no guessing required.
- **Step 8 bucket table.** The verdict-to-bucket mapping prevents undercounting/overcounting when `valid-pre-existing` and `valid-out-of-scope` appear in two buckets simultaneously.
- **Red flags section.** Anti-patterns are named and actionable, not vague.
- **Description is strong.** It includes multiple trigger keywords (PR, review comments, triage, classify, fix, replies, push) that agents can match against user intent.

---

## Violations (Must Fix)

### 1. Non-standard frontmatter fields at top level (not under `metadata:`)

The spec requires all custom fields to be nested under `metadata:`. Currently, nine fields are declared at the top level:

**Current:**
```yaml
---
name: handle-review
description: "..."
version: 1.0.0
author: Varun U
email: varun@zysk.tech
category: engineering-practice
tags:
  - pr-review
  - code-review
  - github
  - triage
  - workflow
product: tms
sprint: 4
tested_with: claude-opus-4-7
user-invocable: true
---
```

**Fix:**
```yaml
---
name: handle-review
description: "..."
license: MIT
compatibility: "Requires gh CLI (authenticated) and git. npm/npx used only for type-check/test steps. Companion skills optional — pr-review-toolkit:code-reviewer, pr-review-toolkit:silent-failure-hunter, simplify, next-best-practices, vercel-react-best-practices."
metadata:
  version: 1.0.0
  author: Varun U
  email: varun@zysk.tech
  category: engineering-practice
  tags:
    - pr-review
    - code-review
    - github
    - triage
    - workflow
  product: tms
  sprint: 4
  tested_with: claude-opus-4-7
  user-invocable: true
---
```

### 2. `license` field is missing

The spec lists `license` as a required field. No license is declared anywhere in the frontmatter.

**Fix:** Add `license: MIT` (or the appropriate license) at the top level of the frontmatter.

### 3. `compatibility` field is missing

The skill references `gh CLI`, `git`, `npm`, `npx vitest`, and optional companion skills (`pr-review-toolkit`, `simplify`, `next-best-practices`, `vercel-react-best-practices`). Without a `compatibility` field, consumers cannot determine prerequisites before activation.

**Fix:** Add a `compatibility` field (max 500 chars) describing the environment requirements, for example:

```yaml
compatibility: "Requires gh CLI (authenticated) and git. npm/npx used for type-check/test steps. Companion skills (pr-review-toolkit:code-reviewer, pr-review-toolkit:silent-failure-hunter, simplify, next-best-practices, vercel-react-best-practices) are optional — substitute project equivalents if unavailable."
```

---

## What's More Than Needed (Consider Restructuring)

- **Step 6 paragraph on round-3+ simplification** is repeated almost verbatim in both Step 6 and the Red Flags section. One of the two can be a cross-reference rather than a full re-statement — this duplication adds ~15 lines without adding new information.
- **The "Output presentation" subsection under Red Flags** is misplaced. Its three bullet points are formatting rules, not anti-patterns. Moving them to a top-level `## Output conventions` section (near the existing `## Output` section) would improve discoverability and logical grouping.
- **Step 1's inline comment filter explanation** is thorough but long. The "Why filter (2)" prose paragraph could be condensed to 2 sentences; the rationale is sound but restates the same point three times.

---

## What's Missing (Must Add)

1. **`license` field** — required by spec; add at the frontmatter top level.
2. **`compatibility` field** — strongly recommended; the skill has real external dependencies (`gh` CLI, `git`, optional npm tooling) that consumers need to know about before activating.
3. **`metadata:` wrapper** — all nine non-standard fields must be nested under `metadata:` to comply with the spec's structure rules.

---

## Summary Table

| Area | Status | Detail |
|---|---|---|
| `name` field | Pass | Valid format, matches folder name, 13 chars |
| `description` field | Pass | Clear, keyword-rich, 156 chars |
| `license` field | Missing | Required field not present |
| `compatibility` field | Missing | Skill has non-trivial external dependencies; field absent |
| `metadata` structure | Wrong | Nine custom fields at top level instead of under `metadata:` |
| Token budget | Pass | ~3,025 tokens (well under 5,000 limit) |
| Line budget | Pass | 189 body lines (under 400 warn / 500 fail) |
| Body structure | Excellent | 8 numbered steps, verdict taxonomy, approval gate, examples, edge cases, red flags |
| Self-containment / portability | Warn | References external companion skills without fallback guidance beyond a single note; `compatibility` field would formalize prerequisites |
