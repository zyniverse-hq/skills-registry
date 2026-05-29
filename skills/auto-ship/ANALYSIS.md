# ANALYSIS — auto-ship

> Generated against the [agentskills.io](https://agentskills.openml.io) standard.

---

## Overall Verdict

**Partially compliant.** The skill content is excellent — a well-structured autonomous issue-to-PR pipeline with clear classification logic, pre-flight race-safety checks, and a thorough recovery table. However, it shares the same structural violations as its sibling `auto-merge`: nine custom frontmatter fields sit at the wrong level (must be nested under `metadata:`), `license` and `compatibility` fields are missing, and the external `queue-io.js` script is referenced but not bundled inside the skill folder. The body is approaching the 500-line limit (~392 lines, ~4,900 tokens).

---

## Spec Compliance Checklist

| Check | Status | Detail |
|---|---|---|
| `name` field format | ✅ PASS | `auto-ship` — 9 chars, lowercase + hyphens, no leading/trailing/consecutive hyphens, matches folder name |
| `description` present & non-empty | ✅ PASS | Present, ~210 chars, under 1024 limit |
| `description` describes what it does | ✅ PASS | Clearly describes the autonomous issue-to-PR pipeline behaviour |
| `description` describes when to use it | ⚠️ WARN | Functional but thin on trigger keywords; users saying "drain Todo", "ship issues automatically", "batch ship" may not trigger reliably |
| `license` field | ❌ FAIL | Not present |
| `compatibility` field | ❌ FAIL | Hard dependencies on `gh` CLI, Node.js, `.claude/scripts/queue-io.js`, GitHub Projects v2 (project #18), zyni-ai org — none declared |
| `metadata` field structure | ❌ FAIL | 9 custom fields sit at top level (`version`, `author`, `email`, `category`, `tags`, `product`, `sprint`, `tested_with`, `user-invocable`) — must be nested under `metadata:` |
| `allowed-tools` field | — | Not present (optional, experimental — acceptable to omit) |
| Token budget (body) | ⚠️ WARN | ~392 body lines × ~50 chars = ~19,600 chars ÷ 4 ≈ ~4,900 tokens — approaching the 5000-token recommendation |
| Line budget (body) | ⚠️ WARN | ~392 body lines — approaching the 500-line recommendation |
| `scripts/` directory | ❌ FAIL | References `.claude/scripts/queue-io.js` (external to skill folder) — not bundled |
| `references/` directory | ✅ PASS | Not needed — body is well structured with inline tables and recovery steps |
| `assets/` directory | ✅ PASS | Not needed |
| Body — step-by-step instructions | ✅ PASS | Steps 1–7 clearly numbered; sub-steps labeled (2a, 2b, 2c, 3a, 3b, 3c) |
| Body — examples | ✅ PASS | Dedicated Example section with user trigger → Claude action → result |
| Body — edge cases | ✅ PASS | Red flags section grouped by phase; Recovery table covers two failure modes |

---

## What the Skill Gets Right

- **Two invocation modes** (auto-pick and explicit batch) with clear trigger conditions — the user can use this naturally without reading the full spec
- **First-match classification table** in Step 3 with label short-circuit — prevents re-reading the body for already-classified issues; ambiguity verdict persists on the issue label
- **Pre-flight race-safety check** in Step 5 — re-queries live state before every execution to prevent stealing teammates' work or double-shipping
- **Atomic queue writes via `queue-io.js`** — concurrent `/auto-merge` reads can never observe a torn JSON file
- **Red flags grouped by phase** — scannable during mid-flight review; each entry is a concrete "stop and reconsider" signal rather than abstract guidance
- **Output presentation guardrails** — explicit ban on citing memory fragment keys by name in user-facing output; detailed examples of how to describe each discipline step (not arrow-chain shorthand)
- **Stale-check step (2b)** — confirms the issue still describes a real problem before classification; closes stale issues with a verification comment

---

## Violations (Must Fix)

### 1. Nine non-standard top-level frontmatter fields

The spec defines exactly six frontmatter keys: `name`, `description`, `license`, `compatibility`, `metadata`, `allowed-tools`. All other custom fields must be nested under `metadata:` as string key-value pairs.

**Current (wrong):**
```yaml
version: 1.0.0
author: Varun U
email: varun@zysk.tech
category: engineering-practice
tags:
  - github-issues
  - autonomous
  - pr-creation
  - project-board
  - workflow
product: tms
sprint: 4
tested_with: claude-opus-4-7
user-invocable: true
```

**Fix — move all under `metadata:` (values must be strings):**
```yaml
metadata:
  version: "1.0.0"
  author: Varun U
  email: varun@zysk.tech
  category: engineering-practice
  tags: "github-issues, autonomous, pr-creation, project-board, workflow"
  product: tms
  sprint: "4"
  tested_with: claude-opus-4-7
  user-invocable: "true"
```

---

### 2. Missing `compatibility` field

This skill will silently fail on any machine without `gh`, Node.js, or the `queue-io.js` script, and on any project without a GitHub Projects v2 board configured.

**Add:**
```yaml
compatibility: >
  Requires GitHub CLI (gh) and Node.js.
  Designed for Claude Code. Depends on .claude/scripts/queue-io.js for atomic
  queue writes — must exist in the project. Board operations require GitHub
  Projects v2 (project #18 for zyni-ai/tms-app — swap project number for your
  project). Invokes /ship-issue as a required base skill.
```

---

### 3. Missing `license` field

No license is declared. Any team picking up this skill from the registry has no signal about usage rights.

**Add:**
```yaml
license: Proprietary — internal use only (zysk.tech)
```

---

### 4. Referenced external script is not bundled

The skill calls `.claude/scripts/queue-io.js` — a file that lives outside the skill folder. If anyone copies or installs this skill without the matching project scaffolding, the queue write step silently breaks.

**Fix:**
1. Copy `queue-io.js` into `auto-ship/scripts/queue-io.js`
2. Update all body references from `.claude/scripts/queue-io.js` to `scripts/queue-io.js`

```
auto-ship/
├── SKILL.md
└── scripts/
    └── queue-io.js    ← move here
```

---

## What's More Than Needed (Consider Restructuring)

### Hardcoded project values throughout the body

`zyni-ai/tms-app`, `projectV2(number: 18)`, `organization(login: "zyni-ai")`, `.claude/auto-ship-queue.json` — these appear in many places. The Notes section mentions to swap them, but adapters can easily miss some. Consider extracting to a config block at the top:

```markdown
## Configuration

> Swap these values for your project before use:
> - **Org/repo:** `zyni-ai/tms-app`
> - **Project board:** `projectV2(number: 18)` under `organization(login: "zyni-ai")`
> - **Queue file:** `.claude/auto-ship-queue.json`
> - **Queue script:** `.claude/scripts/queue-io.js`
```

### Output presentation section is very long

The "Output presentation (every step)" Red flags section contains detailed guidance about avoiding memory fragment key citations and arrow-chain summaries. While valuable, this is implementation-history guidance that could be moved to a `references/design-notes.md` to reduce body length.

---

## What's Missing (Must Add)

### 1. `license` field
See Violations above. Even `license: Proprietary` signals intent.

### 2. `compatibility` field
See Violations above. Hard deps on `gh`, Node.js, `queue-io.js`, GitHub Projects v2 project should be declared.

### 3. Bundled `scripts/queue-io.js`
See Violations above. Skill is not self-contained without it.

### 4. Stronger trigger keywords in `description`

The current description is technically correct but won't trigger on the most natural phrasings.

**Current:**
```yaml
description: "Autonomous issue-to-PR pipeline. Auto-picks eligible Todo items (or a passed subset), classifies into quick-fix / clear-scope / ambiguous, ships everything non-ambiguous into reviewable PRs, records each in a merge queue, and stops at PR open."
```

**Improved:**
```yaml
description: >
  Autonomous issue-to-PR pipeline. Use when the user says "drain Todo",
  "ship these issues", "batch ship", "run auto-ship", or wants to autonomously
  convert pre-triaged Todo items into PRs without checkpoints. Auto-picks
  eligible Todo issues in priority order (or ships an explicit subset), classifies
  each as quick-fix/clear-scope/ambiguous, opens PRs for non-ambiguous items,
  and appends each to the auto-merge queue. Stops at PR open — /auto-merge
  handles the merge step.
```

---

## Summary Table

| Area | Status | Detail |
|---|---|---|
| `name` field | ✅ Pass | Valid format, matches folder name |
| `description` field | ⚠️ Warn | Present and valid; trigger keywords too narrow for natural user phrasings |
| `license` field | ❌ Missing | Not declared |
| `compatibility` field | ❌ Missing | Hard deps on gh, Node.js, queue-io.js, GitHub Projects v2 — none declared |
| `metadata` structure | ❌ Wrong | 9 custom fields at top level; must nest under `metadata:` |
| Token budget | ⚠️ Warn | ~4,900 tokens — approaching the 5000-token limit |
| Line budget | ⚠️ Warn | ~392 body lines — approaching the 500-line limit |
| `scripts/` bundled | ❌ Missing | `queue-io.js` referenced externally; not bundled in skill folder |
| `references/` split | ✅ Not needed | Body is well structured; inline tables and recovery steps are appropriate |
| Body structure | ✅ Excellent | Step-by-step, invocation modes, examples, red flags grouped by phase, recovery table |
| Self-containment / portability | ❌ Fails | External script dependency + hardcoded org/repo/project values |
