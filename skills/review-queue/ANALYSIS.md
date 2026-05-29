# ANALYSIS — review-queue

> Generated against the [agentskills.io](https://agentskills.openml.io) standard.

---

## Overall Verdict

**Partially compliant.** The skill body is exceptionally well-structured — clear step-by-step instructions, concrete examples, thorough edge-case handling, and strong action discipline. However, it fails spec compliance on two structural fronts: the `license` and `compatibility` fields are absent, and nine non-standard frontmatter fields (`version`, `author`, `email`, `category`, `tags`, `product`, `sprint`, `tested_with`, `user-invocable`) are declared at the top level instead of being nested under `metadata:` as required.

---

## Spec Compliance Checklist

| Check | Status | Detail |
|---|---|---|
| `name` field format | ✅ PASS | `review-queue` — lowercase, hyphens only, no leading/trailing hyphens, 12 chars, matches folder name |
| `description` present & non-empty | ✅ PASS | 234 chars, well within 1–1024 range |
| `description` describes what it does | ✅ PASS | Clearly states read-only digest of open PRs, classification into readiness buckets, and factual summaries |
| `description` describes when to use it | ✅ PASS | Trigger phrases "requested reviewer", "digest", "triage", "review queue" are all present |
| `license` field | ❌ FAIL | Field is absent entirely |
| `compatibility` field | ❌ FAIL | Field is absent; requires `gh` CLI with auth — environment prerequisites undocumented |
| `metadata` field structure | ❌ FAIL | Nine non-standard fields (`version`, `author`, `email`, `category`, `tags`, `product`, `sprint`, `tested_with`, `user-invocable`) are at top-level; spec requires all custom fields nested under `metadata:` |
| `allowed-tools` field | — | Not present; optional field, no violation |
| Token budget (body) | ✅ PASS | ~3,000 tokens estimated (body ~12,000 chars / 4); well under the 5,000-token limit |
| Line budget (body) | ✅ PASS | 273 lines (lines 19–291); well under the 500-line hard limit and the 400-line soft warning |
| `scripts/` directory | — | No scripts directory; skill uses inline bash commands, which is acceptable |
| `references/` directory | — | Not present; not required |
| `assets/` directory | — | Not present; not required |
| Body — step-by-step instructions | ✅ PASS | Five numbered steps with clear sequence, each self-contained and actionable |
| Body — examples | ✅ PASS | Concrete PR-title-to-summary examples in Step 4; full invocation example in the Example section; sample digest output in Step 5 |
| Body — edge cases | ✅ PASS | Draft filtering, own-PR false positives, race-condition on closed PRs, path-filter causing missing auto-review, classifier uncertainty, per-PR query timeout — all handled |

---

## What the Skill Gets Right

- **Step structure is exemplary.** Steps 0–5 are logically sequenced, individually actionable, and the mandatory TaskCreate in Step 0 enforces anti-skip discipline.
- **Classification matrix is precise.** The 10-verdict decision table with first-match semantics eliminates ambiguity; the bucket-assignment reference table resolves any tie-breaking debates.
- **Auto-review classifier rationale is sound.** The prose-based classifier (not regex) with explicit tie-breaking rules (explicit positive verdict wins over mixed nits) handles the real-world messiness of bot comment formats.
- **Factual summary guidelines are concrete.** The diff-size buckets (tiny/small/medium/large), anti-pattern list, and quote-don't-paraphrase rule are directly actionable.
- **Red-flags section is thorough.** Covers action discipline, classification rigor, and output presentation — the three most common failure modes for this class of skill.
- **Portability note is present.** The Notes section explicitly flags the TMS-specific repo and bot username, and tells the reader what to swap for their project.
- **Recovery table is well thought out.** Idempotency of the read-only skill is called out, and each failure point maps to a concrete recovery action.
- **description field is strong.** The description encodes the most likely user queries ("review queue", "requested reviewer", "digest") and the key constraint ("never approves, never comments") that differentiates this skill from action-taking alternatives.

---

## Violations (Must Fix)

### 1. Non-standard frontmatter fields must be nested under `metadata:`

**Current:**
```yaml
version: 1.0.0
author: Varun U
email: varun@zysk.tech
category: engineering-practice
tags:
  - github-pr
  - code-review
  - triage
  - workflow
  - digest
product: tms
sprint: 4
tested_with: claude-opus-4-7
user-invocable: true
```

**Fix — move all custom fields under `metadata:`:**
```yaml
metadata:
  version: 1.0.0
  author: Varun U
  email: varun@zysk.tech
  category: engineering-practice
  tags:
    - github-pr
    - code-review
    - triage
    - workflow
    - digest
  product: tms
  sprint: 4
  tested_with: claude-opus-4-7
  user-invocable: true
```

The spec is explicit: "Non-standard frontmatter fields must be nested under `metadata:`, not at top level."

### 2. `license` field is missing

**Fix — add a license field after `description`:**
```yaml
license: MIT
```

Or whichever license applies to this skill. If the skill is proprietary/internal, use `license: proprietary` or an appropriate SPDX identifier.

### 3. `compatibility` field is missing

This skill has a hard runtime dependency on the `gh` CLI being authenticated. That is an environment prerequisite that must be documented.

**Fix — add a compatibility field:**
```yaml
compatibility: "Requires gh CLI (>=2.40) authenticated with a GitHub account that has read access to the target repository. The --review-requested flag requires gh >=2.23."
```

---

## What's More Than Needed (Consider Restructuring)

- **"Bucket assignment by verdict" table (lines 229–245) largely duplicates Step 3.** The verdict-to-bucket mapping appears twice — once in the classification matrix (Step 3) and once in the standalone reference table. The reference table adds value as a quick lookup, but the "Why" column repeats rationale already present in Step 3. Consider trimming the Why column to a one-word label rather than a full sentence.
- **"Red flags" section is comprehensive but long.** At 25 lines it is valuable, but some items (e.g., "Citing memory keys") are suite-wide conventions that do not need to live in every skill. If the suite has a shared conventions document, a single reference link would save ~8 lines.

---

## What's Missing (Must Add)

1. **`license` field** — required by spec; see Violation 2 above.
2. **`compatibility` field** — required for skills with external tool dependencies; see Violation 3 above.
3. **`metadata:` wrapper** — all nine custom frontmatter fields must move under `metadata:`; see Violation 1 above.

---

## Summary Table

| Area | Status | Detail |
|---|---|---|
| `name` field | ✅ Pass | Valid format, matches folder name `review-queue` |
| `description` field | ✅ Pass | Clear, concise, good trigger keywords, within length limit |
| `license` field | ❌ Missing | Must be added |
| `compatibility` field | ❌ Missing | `gh` CLI dependency and auth requirement are undocumented |
| `metadata` structure | ❌ Wrong | Nine custom fields at top level; all must move under `metadata:` |
| Token budget | ✅ Pass | ~3,000 tokens; well within the 5,000-token limit |
| Line budget | ✅ Pass | 273 lines; well within the 500-line hard limit |
| Body structure | ✅ Excellent | Clear steps, classifier tables, anti-patterns, recovery guide, red flags |
| Self-containment / portability | ✅ Pass | Repo and bot-username swap-points are explicitly called out in Notes |
