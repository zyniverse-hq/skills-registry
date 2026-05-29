# ANALYSIS — edd

> Generated against the [agentskills.io](https://agentskills.openml.io) standard.

---

## Overall Verdict

**Partially compliant.** The content quality is outstanding — a thorough eval-first methodology with a triage gate, structured EDD Plan artifact, four evaluator types, and detailed anti-pattern sections. The description is unusually long but packed with trigger keywords, which is the right trade-off for this type of meta-skill. The main structural issues are: nine custom frontmatter fields at the wrong level (must be under `metadata:`), missing `license` field, and no `compatibility` declared. Body is well within token and line budgets.

---

## Spec Compliance Checklist

| Check | Status | Detail |
|---|---|---|
| `name` field format | ✅ PASS | `edd` — 3 chars, lowercase, no hyphens, matches folder name |
| `description` present & non-empty | ✅ PASS | Present, ~740 chars, under 1024 limit |
| `description` describes what it does | ✅ PASS | Thoroughly describes EDD methodology and trigger scenarios |
| `description` describes when to use it | ✅ PASS | Explicit trigger phrases: "building X", "refactoring Y", "new feature", "starting work on…" — excellent discovery |
| `license` field | ❌ FAIL | Not present |
| `compatibility` field | — | No hard external tool dependencies; methodology-only skill — acceptable to omit |
| `metadata` field structure | ❌ FAIL | 8 custom fields at top level (`version`, `author`, `email`, `category`, `tags`, `product`, `sprint`, `tested_with`) — must be nested under `metadata:` |
| `allowed-tools` field | — | Not present (optional, experimental — acceptable to omit) |
| Token budget (body) | ✅ PASS | ~213 body lines × ~50 chars ≈ ~10,650 chars ÷ 4 ≈ ~2,663 tokens — well under the 5000-token recommendation |
| Line budget (body) | ✅ PASS | ~213 body lines — well under the 500-line recommendation |
| `scripts/` directory | — | Not applicable — methodology skill; no scripts |
| `references/` directory | ✅ PASS | Not needed — reference sections (EDD vs TDD table, anti-patterns, cooperating skills) are compact and inline-appropriate |
| `assets/` directory | ✅ PASS | Not needed |
| Body — step-by-step instructions | ✅ PASS | Steps 1–7 clearly labeled with triage gate, interviews, artifact generation, CI lock-in |
| Body — examples | ✅ PASS | Dedicated Example section with user trigger → Claude action → result |
| Body — edge cases | ✅ PASS | Anti-patterns section, cooperating skills, behavioural guidance for mixed deterministic/LLM tasks |

---

## What the Skill Gets Right

- **Triage gate in Step 1** — explicitly declares when EDD does NOT apply (pure deterministic code) and tells the agent to say so plainly; builds trust and prevents the skill from being over-applied
- **Description as a trigger surface** — at ~740 chars, it front-loads the trigger phrases ("building X", "refactoring Y", "new node", "how should I approach this") so discovery is reliable across many natural phrasings
- **EDD Plan template** — a concrete 10–30 line markdown artifact the agent produces; agents pattern-match against structure reliably
- **Four evaluator types with clear selection criteria** — programmatic, LLM-judge, reference-based, human spot-check; each tied to a failure mode category
- **"Evaluator that always passes is broken" rule** — explicitly called out; prevents false confidence from uncalibrated evaluators
- **Cooperating skills section** — delineates boundaries cleanly (`langsmith-evaluator`, `run-eval`); prevents scope creep and re-implementation
- **Behavioural guidance section** — tells the agent how to handle mid-flow activations, partial invocations ("I just wanted to know what EDD was"), and honest out-of-scope calls; rare and valuable
- **Anti-pattern reference section** — "Writing the eval after shipping", "No baseline", "Letting the dataset rot" — concrete failure modes the agent can flag when the user exhibits them

---

## Violations (Must Fix)

### 1. Eight non-standard top-level frontmatter fields

The spec defines exactly six frontmatter keys: `name`, `description`, `license`, `compatibility`, `metadata`, `allowed-tools`. All other custom fields must be nested under `metadata:` as string key-value pairs.

**Current (wrong):**
```yaml
version: 1.0.0
author: Sharath S Rao
email: sharath.rao@zysk.tech
category: engineering-practice
tags:
  - eval
  - tdd
  - llm-evaluation
  - development-practice
product: tms
sprint: 1
tested_with: claude-sonnet-4-6
```

**Fix — move all under `metadata:` (values must be strings):**
```yaml
metadata:
  version: "1.0.0"
  author: Sharath S Rao
  email: sharath.rao@zysk.tech
  category: engineering-practice
  tags: "eval, tdd, llm-evaluation, development-practice"
  product: tms
  sprint: "1"
  tested_with: claude-sonnet-4-6
```

---

### 2. Missing `license` field

No license is declared. Any team picking up this skill from the registry has no signal about usage rights.

**Add:**
```yaml
license: Proprietary — internal use only (zysk.tech)
```

---

## What's More Than Needed (Consider Restructuring)

### Description length approaching the upper bound

At ~740 chars the description is 72% of the 1024-char limit. The length is justified — this is a meta-skill that activates on implicit signals ("starting work on…", "how should I approach this") rather than explicit commands. However, if the description needs to grow further, it will hit the limit. Consider trimming the "The skill starts with a triage step…" sentence (the body already covers this) to create headroom:

```yaml
description: >
  INVOKE THIS SKILL whenever the user is about to start a new feature, refactor
  existing code, change a prompt, or modify an agent/node — any work whose quality
  is hard to assert with a binary unit test. EDD (Evaluation-Driven Development)
  is the eval-first counterpart to TDD: define success criteria and evaluators
  BEFORE writing code, baseline current behavior, then iterate against measurable
  scores. Triggers on: 'building X', 'refactoring Y', 'improving the prompt for Z',
  'new node', 'new feature', 'how should I approach this', 'starting work on…',
  'change the LLM behavior'. Use even when the user doesn't say 'eval'.
```

### Reference sections could move to `references/` if body grows

The three Reference tables at the end (EDD vs TDD comparison, anti-patterns, cooperating skills) are high quality but add ~60 lines. If the body approaches 400+ lines in future iterations, these are natural candidates for `references/edd-vs-tdd.md`, `references/anti-patterns.md`.

---

## What's Missing (Must Add)

### 1. `license` field
See Violations above. Even `license: Proprietary` signals intent to registry consumers.

### 2. `metadata` structure correction
See Violations above. Top-level custom fields can cause YAML parsers in agent clients to reject or silently drop the skill.

---

## Summary Table

| Area | Status | Detail |
|---|---|---|
| `name` field | ✅ Pass | Valid format, matches folder name |
| `description` field | ✅ Pass | Rich trigger keywords; approaches 1024-char limit but under it |
| `license` field | ❌ Missing | Not declared |
| `compatibility` field | — | No hard tool deps; methodology-only — acceptable to omit |
| `metadata` structure | ❌ Wrong | 8 custom fields at top level; must nest under `metadata:` |
| Token budget | ✅ Pass | ~2,663 tokens — well under the 5000-token limit |
| Line budget | ✅ Pass | ~213 body lines — well under 500-line limit |
| `scripts/` bundled | — | Not applicable |
| `references/` split | ✅ Not needed | Reference sections are compact and inline-appropriate |
| Body structure | ✅ Excellent | Triage gate, step-by-step, artifact templates, anti-patterns, behavioural guidance |
| Self-containment / portability | ✅ Pass | Methodology skill; no external dependencies |
