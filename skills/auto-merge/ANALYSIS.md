# ANALYSIS — auto-merge

> Generated against the [agentskills.io](https://agentskills.io) standard.

---

## Overall Verdict

**Partially compliant.** The content quality is excellent — step-by-step execution, ordered verdict rules, exact output format templates, strong Red flags section, and a self-healing design that re-checks live state on every invocation. However, it shares the same structural spec violations as its sibling skill `auto-ship`: nine custom frontmatter fields sit at the wrong level (must be nested under `metadata:`), the `compatibility` and `license` fields are missing, and the external `queue-io.js` script is referenced but not bundled inside the skill folder. The body is comfortably within token budget (~2500 tokens, well under the 5000 limit).

---

## Spec Compliance Checklist

| Check | Status | Detail |
|---|---|---|
| `name` field format | ✅ PASS | `auto-merge` — 10 chars, lowercase + hyphens, no leading/trailing/consecutive hyphens, matches folder name |
| `description` present & non-empty | ✅ PASS | Present, ~210 chars, under 1024 limit |
| `description` describes what it does | ✅ PASS | Clearly describes the one-shot queue drain behaviour |
| `description` describes when to use it | ⚠️ WARN | Functional but thin on trigger keywords; users saying "drain the queue" or "merge approved PRs" may not trigger this reliably |
| `license` field | ❌ FAIL | Not present |
| `compatibility` field | ❌ FAIL | Skill has hard dependencies (GitHub CLI `gh`, Node.js, git, GitHub Projects v2, `.claude/scripts/queue-io.js`) — none declared |
| `metadata` field structure | ❌ FAIL | 9 custom fields sit at the top level of frontmatter instead of nested under `metadata:` — see Violations section |
| `allowed-tools` field | — | Not present (optional, experimental — acceptable to omit) |
| Token budget (body) | ✅ PASS | ~206 body lines, estimated ~2500 tokens — well under the 5000-token recommendation |
| Line budget (body) | ✅ PASS | ~206 body lines — under the 500-line recommendation |
| `scripts/` directory | ❌ FAIL | References `.claude/scripts/queue-io.js` (external) — not bundled inside the skill folder |
| `references/` directory | ✅ PASS | Not needed — body is compact enough; Recovery and Red flags sections are appropriately sized inline |
| `assets/` directory | ✅ PASS | Not needed |
| Body — step-by-step instructions | ✅ PASS | Steps 0–6 clearly numbered and sequenced |
| Body — examples | ✅ PASS | Dedicated Example section with user trigger → Claude action → result |
| Body — edge cases | ✅ PASS | Red flags section and verdict ordering table cover edge cases thoroughly |

---

## What the Skill Gets Right

- **Ordered verdict rules (first-match)** — the Step 3 table is unambiguous; the agent can't invent a new ordering or misclassify a PR
- **Exact output format template** — Step 6 shows the Done / Needs attention / Transient bucket structure with inline examples; agents pattern-match against concrete structure reliably
- **Self-healing across invocations** — every run re-reads live PR state rather than trusting cached queue status; a failed queue write last run is transparently corrected next run
- **Gotchas / Red flags section** — lists the six most dangerous failure modes concisely, grouped logically
- **Recovery table** — four concrete failure scenarios with exact recovery steps
- **No-scheduler stance documented with rationale** — explains *why* it's one-shot (credits, user confusion from earlier polling design); an agent that understands the purpose follows the rule more reliably
- **Idempotent board move for externally-merged PRs** — catches the case where a PR was merged outside the skill and prevents issues from getting stuck in In Review permanently
- **`needs-rebase` branch guard** — refuses to switch the main CWD checkout; only rebases via an existing worktree path, preventing silent destruction of unrelated local state

---

## Violations (Must Fix)

### 1. Nine non-standard top-level frontmatter fields

The spec defines exactly six frontmatter keys: `name`, `description`, `license`, `compatibility`, `metadata`, `allowed-tools`. All other custom fields must be nested under `metadata:` as string key-value pairs. Having them at the top level can cause YAML parsers in agent clients to reject or silently drop the skill.

**Current (wrong):**
```yaml
version: 1.0.0
author: Varun U
email: varun@zysk.tech
category: engineering-practice
tags:
  - github-pr
  - merge
  - automation
  - workflow
  - queue
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
  tags: "github-pr, merge, automation, workflow, queue"
  product: tms
  sprint: "4"
  tested_with: claude-opus-4-7
  user-invocable: "true"
```

---

### 2. Missing `compatibility` field

This skill will silently fail on any machine that lacks `gh`, Node.js, or git, and on any project that hasn't set up `.claude/scripts/queue-io.js` or a GitHub Projects v2 board. The spec's `compatibility` field exists to declare exactly these constraints.

**Add:**
```yaml
compatibility: >
  Requires GitHub CLI (gh), Node.js, and git.
  Designed for Claude Code. Depends on .claude/scripts/queue-io.js for atomic
  queue writes — this file must exist in the project. Board Done-move uses
  GitHub Projects v2 single-select Status field; swap field IDs for your project.
  Hardcoded to zyni-ai/tms-app — update repo and org references before use elsewhere.
```

---

### 3. Missing `license` field

No license is declared. Any team that picks up this skill from the registry has no signal about usage rights.

**Add (at minimum):**
```yaml
license: Proprietary — internal use only (zysk.tech)
```

---

### 4. Referenced external script is not bundled

The skill calls `.claude/scripts/queue-io.js` — a file that lives in the project's `.claude/scripts/` directory, outside the skill folder. If anyone copies or installs this skill without the matching project scaffolding, the queue write step silently breaks with a Node.js `MODULE_NOT_FOUND` error at runtime.

The spec requires that bundled scripts live in the `scripts/` subdirectory of the skill and be self-contained.

**Fix:**
1. Copy `queue-io.js` into `auto-merge/scripts/queue-io.js`
2. Update all references in the body from `.claude/scripts/queue-io.js` to `scripts/queue-io.js`

```
auto-merge/
├── SKILL.md
└── scripts/
    └── queue-io.js    ← move here
```

---

## What's More Than Needed (Consider Restructuring)

### Hardcoded project values throughout the body

`zyni-ai/tms-app`, GitHub Projects v2 field IDs, `.claude/auto-ship-queue.json` — these appear in multiple places. The Notes section mentions to swap them, but that's easy to miss. Since the skill is in a shared registry, consider extracting these to a config block at the top of the body body so adapters know exactly what to change:

```markdown
## Configuration

> Swap these values for your project before use:
> - **Org/repo:** `zyni-ai/tms-app`
> - **Queue file:** `.claude/auto-ship-queue.json`
> - **Project board field IDs:** see GitHub Projects v2 → Settings → Fields
```

### "No scheduler" implementation note in Notes section

The explanation of why the polling design was abandoned is good reasoning — but it's implementation history, not skill instructions. Move it to a comment or a `references/design-notes.md` if it needs to be preserved. It adds length without helping the agent execute the skill.

---

## What's Missing (Must Add)

### 1. `license` field
See Violations above. Even `license: Proprietary` signals intent.

### 2. `compatibility` field
See Violations above. Hard deps on `gh`, Node.js, git, and specific project setup should be declared.

### 3. Bundled `scripts/queue-io.js`
See Violations above. Skill is not self-contained without it.

### 4. Stronger trigger keywords in `description`

The current description is valid but unlikely to trigger on the most natural user phrasings. Users typically say things like "drain the queue", "merge the approved PRs", "run auto-merge", or "what's in the merge queue" — none of these phrases appear in the description.

**Current:**
```yaml
description: "One-shot drain of an auto-ship PR queue. Re-checks each PR's CI + merge state + review decision, squash-merges what's MERGEABLE + APPROVED + clean of unaddressed comments, and reports per-entry verdict. No scheduler."
```

**Improved:**
```yaml
description: >
  One-shot merge queue drain. Use when the user says "drain the queue",
  "merge approved PRs", "run auto-merge", or wants to know what's currently
  mergeable. Re-checks each PR's live CI status, review decision, and merge
  state; squash-merges what is APPROVED and clean; skips the rest with a clear
  verdict. Reads from .claude/auto-ship-queue.json written by /auto-ship.
  No scheduler — user-invoked only.
```

---

## Summary Table

| Area | Status | Detail |
|---|---|---|
| `name` field | ✅ Pass | Valid format, matches folder name |
| `description` field | ⚠️ Warn | Present and valid; trigger keywords too narrow for natural user phrasings |
| `license` field | ❌ Missing | Not declared |
| `compatibility` field | ❌ Missing | Hard deps on gh, Node.js, git, queue-io.js, specific project setup — none declared |
| `metadata` structure | ❌ Wrong | 9 custom fields at top level; must nest under `metadata:` |
| Token budget | ✅ Pass | ~2500 tokens — well under the 5000-token limit |
| Line budget | ✅ Pass | ~206 body lines — under 500-line limit |
| `scripts/` bundled | ❌ Missing | `queue-io.js` referenced externally; not bundled in skill folder |
| `references/` split | ✅ Not needed | Body is compact; inline recovery and red flags are appropriate |
| Body structure | ✅ Excellent | Step-by-step, examples, edge cases, recovery table |
| Self-containment / portability | ❌ Fails | External script dependency + hardcoded org/repo/project values |
