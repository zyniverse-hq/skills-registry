# ANALYSIS — qa-handoff

> Generated against the [agentskills.io](https://agentskills.openml.io) standard.

---

## Overall Verdict

**Partially compliant.** This is one of the most thorough skills in the registry — three invocation modes, sweep confirmation gate, per-PR loop with risk classification, 10 test-plan variants, mandatory content synthesis with banned phrases, and partial-failure handling. The `allowed-tools` field is correctly used. However, it has critical issues: the body is **504 lines (~6,300 tokens), exceeding both spec limits**. Additionally, ten non-standard frontmatter fields sit at the top level (must be under `metadata:`), `license` is missing, and `compatibility` is missing despite requiring `gh` CLI.

---

## Spec Compliance Checklist

| Check | Status | Detail |
|---|---|---|
| `name` field format | ✅ PASS | `qa-handoff` — 10 chars, lowercase + hyphens, no leading/trailing/consecutive hyphens, matches folder name |
| `description` present & non-empty | ✅ PASS | Present, ~270 chars, under 1024 limit |
| `description` describes what it does | ✅ PASS | Clearly describes the QA test plan generation and GitHub issue filing workflow |
| `description` describes when to use it | ✅ PASS | Explicit trigger phrases: "QA handoff", "notify QA about this PR", "send QA test plan", "tell QA to test PR #N" |
| `license` field | ❌ FAIL | Not present |
| `compatibility` field | ❌ FAIL | Hard dependency on `gh` CLI; requires GitHub repo with `dev` branch — not declared |
| `metadata` field structure | ❌ FAIL | 10 non-standard fields at top level (`version`, `author`, `email`, `category`, `tags`, `product`, `sprint`, `tested_with`, `user-invocable`, `model`) — must be nested under `metadata:` |
| `allowed-tools` field | ✅ PASS | Correctly declared as a list: Bash, Read, Write, Grep, Glob, TaskCreate, TaskUpdate, TaskGet, TaskList, AskUserQuestion |
| Token budget (body) | ❌ FAIL | ~504 body lines × ~50 chars ≈ ~25,200 chars ÷ 4 ≈ **~6,300 tokens — exceeds the 5000-token recommendation** |
| Line budget (body) | ❌ FAIL | **~504 body lines — exceeds the 500-line recommendation** |
| `scripts/` directory | — | Not applicable — no scripts |
| `references/` directory | ✅ PASS | Four reference files properly split: `variants.md`, `project-board.md`, `edge-cases.md`, `smoke-test.md` |
| `assets/` directory | ✅ PASS | Not needed |
| Body — step-by-step instructions | ✅ PASS | Steps 0–8 clearly numbered; sub-steps (0.3, 0.5, 0.7, 7a, 7b, 7c, 7d) with per-PR loop clearly delineated |
| Body — examples | ✅ PASS | Output section includes an example filed issue title |
| Body — edge cases | ✅ PASS | Guardrails section covers 14 explicit rules; partial-failure handling; edge cases in `references/edge-cases.md` |

---

## What the Skill Gets Right

- **`allowed-tools` field correctly declared** — one of the few skills in the registry to use this spec field; the explicit tool allowlist prevents over-broad tool use
- **Three invocation modes** (sweep, targeted, standalone config) — covers the full operator workflow without requiring multiple separate skills
- **Sweep confirmation gate** (Step 0.7) — explicitly prevents high-blast-radius silent filing; requires `AskUserQuestion` before creating 7+ issues
- **Step 4.6 banned phrases** — the most unusual and valuable section; explicitly lists strings that must NEVER appear in filed bodies and provides before/after examples; prevents the most common QA handoff failure mode
- **Per-PR partial-failure handling** — batch doesn't abort on a single PR failure; records failure + reason and continues; critical for sweep mode
- **QA assignee resolution chain** — 5-priority resolution (reset → flag → saved-default → interactive-prompt → abort); config file is gitignored; `--set-default` must be explicit
- **Self-check before Step 5** — 5-question mental checklist forces the agent to verify it can answer concretely before generating the test plan; rare example of meta-cognition guidance in a skill
- **`references/` properly split** — the 10 variant templates (`variants.md`), project board GraphQL (`project-board.md`), and edge cases are large reference artifacts that would blow the body budget if inlined

---

## Violations (Must Fix)

### 1. Body exceeds line and token budgets

At ~504 lines and ~6,300 tokens, the body is over both spec limits (500 lines, ~5,000 tokens). This can cause agents to truncate context or fail to load the full skill.

**Fix:** Move more content to `references/`:
- Step 4.5 variant-selection table (~25 lines) → `references/variants.md` (already exists; add the selection table there)
- Step 5 "Where to test" URL mapping table (~30 lines) → `references/url-mapping.md`
- Step 7a full body template (~35 lines) → `references/issue-template.md`
- Step 8b report mode descriptions → `references/report-templates.md` (already exists; the body just needs to reference it more tersely)

These moves would bring the body under 420 lines while keeping the references discoverable.

---

### 2. Ten non-standard top-level frontmatter fields

The spec defines exactly six frontmatter keys: `name`, `description`, `license`, `compatibility`, `metadata`, `allowed-tools`. All other custom fields must be nested under `metadata:` as string key-value pairs. Note: `allowed-tools` is correctly placed; `model` is not a spec field and should be in `metadata:`.

**Current (wrong):**
```yaml
version: 1.0.0
author: Rajashekhar V
email: rajashekhar.v@zysk.tech
category: qa-testing
tags:
  - qa
  - testing
  - github-issues
  - handoff
  - test-plan
product: tms
sprint: 3
tested_with: claude-sonnet-4-6
user-invocable: true
model: claude-sonnet-4-6
```

**Fix — move all non-spec fields under `metadata:` (values must be strings):**
```yaml
allowed-tools: Bash Read Write Grep Glob TaskCreate TaskUpdate TaskGet TaskList AskUserQuestion
metadata:
  version: "1.0.0"
  author: Rajashekhar V
  email: rajashekhar.v@zysk.tech
  category: qa-testing
  tags: "qa, testing, github-issues, handoff, test-plan"
  product: tms
  sprint: "3"
  tested_with: claude-sonnet-4-6
  user-invocable: "true"
  model: claude-sonnet-4-6
```

---

### 3. Missing `compatibility` field

This skill requires the `gh` CLI and a GitHub repository with a `dev` branch. It also stores config in `.claude/skills/qa-handoff/.qa-assignee.local`.

**Add:**
```yaml
compatibility: >
  Requires GitHub CLI (gh). Designed for Claude Code.
  Expects a GitHub repository with a dev base branch.
  QA assignee config stored in .claude/skills/qa-handoff/.qa-assignee.local
  (gitignored). Project board operations require GitHub Projects v2.
```

---

### 4. Missing `license` field

No license is declared.

**Add:**
```yaml
license: Proprietary — internal use only (zysk.tech)
```

---

## What's More Than Needed (Consider Restructuring)

### Step 5 "Where to test" URL mapping table is very long inline

The URL mapping table in Step 5 (~15 rows, ~30 lines) is detailed enough to warrant moving to `references/url-mapping.md`. This table is reference material, not a procedural step, and the body already references `references/variants.md` for similar reference content.

### Step 4.5 variant selection table could move to `references/variants.md`

The 10-row variant selection table belongs with the variant templates. Moving it into `references/variants.md` as a preamble table would reduce the body by ~25 lines while keeping the decision logic accessible.

### Body template in Step 7a is 45+ lines of markdown

The full issue body template in Step 7a adds significant body length. Consider moving it to `references/issue-template.md` with a one-line reference in the body.

---

## What's Missing (Must Add)

### 1. `license` field
See Violations above.

### 2. `compatibility` field
See Violations above. `gh` CLI dependency and `.claude/` config path should be declared.

### 3. Body reduction to meet line/token budgets
See Violations above. Moving URL mapping, variant selection table, and issue body template to `references/` files would bring the body under the 500-line/5000-token limit.

---

## Summary Table

| Area | Status | Detail |
|---|---|---|
| `name` field | ✅ Pass | Valid format, matches folder name |
| `description` field | ✅ Pass | Present, accurate, good trigger keywords |
| `license` field | ❌ Missing | Not declared |
| `compatibility` field | ❌ Missing | Hard dep on gh CLI + GitHub dev branch — not declared |
| `metadata` structure | ❌ Wrong | 10 non-standard fields at top level (model, user-invocable, etc.); must nest under `metadata:` |
| `allowed-tools` field | ✅ Pass | Correctly declared with 10 tools |
| Token budget | ❌ Fail | ~6,300 tokens — exceeds the 5000-token limit |
| Line budget | ❌ Fail | ~504 body lines — exceeds the 500-line limit |
| `scripts/` bundled | — | Not applicable |
| `references/` split | ✅ Pass | Four reference files properly used (variants, project-board, edge-cases, smoke-test) |
| Body structure | ✅ Excellent | Three modes, per-PR loop, step-by-step, banned phrases, guardrails, partial-failure handling |
| Self-containment / portability | ⚠️ Partial | References project-specific URLs and module paths (zyni-ai/tms-app); adapters must swap these |
