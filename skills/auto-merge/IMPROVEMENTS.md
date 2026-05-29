# IMPROVEMENTS — auto-merge

> Improvement plan derived from SKILL.md + ANALYSIS.md audit against the agentskills.openml.io spec.

---

## Quick Summary

| | Before | After |
|---|---|---|
| Spec compliance | Partially compliant | Fully compliant |
| Critical violations | 4 | 0 |
| Agent discoverability | Medium | High |
| Portability | Fails | Pass |

---

## Improvement 1 — Move Nine Custom Fields Under `metadata:`

### What needs to change

Nine custom frontmatter fields (`version`, `author`, `email`, `category`, `tags`, `product`, `sprint`, `tested_with`, `user-invocable`) sit at the top level of the YAML frontmatter. The spec defines exactly six valid top-level keys: `name`, `description`, `license`, `compatibility`, `metadata`, and `allowed-tools`. Any key outside this set must be nested under `metadata:` as a string value. YAML parsers in agent clients may silently drop or reject non-standard top-level keys, making the skill invisible to the registry.

### Before
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

### After
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

Note: `sprint` and `user-invocable` must be quoted strings under `metadata:` — the spec requires all `metadata` values to be strings, not booleans or integers.

### Impact if implemented
- **Agent behaviour:** Registry YAML parsers can reliably load and index the skill without dropping or erroring on non-standard top-level keys.
- **Discoverability:** Skill becomes queryable by `category`, `tags`, and `author` through registry lookup — these fields are currently invisible to any parser that enforces the strict spec schema.
- **Portability:** Any team consuming skills from the registry gets consistent frontmatter structure across all skills, reducing integration friction.
- **Risk reduced:** Prevents silent skill rejection or incomplete indexing by agent clients that strictly validate top-level frontmatter keys.

### Existing use (before fix)
Today, a developer installs this skill from the registry and their agent client attempts to parse the frontmatter. Because `category`, `tags`, `product`, `sprint`, `tested_with`, and `user-invocable` are non-standard top-level keys, a strict parser either rejects the entire skill or silently strips those fields. The skill may not appear in category-based or tag-based searches. The `user-invocable: true` flag — which controls whether the skill appears in the user-facing command palette — may be dropped entirely, hiding `/auto-merge` from the interface where the user would naturally invoke it.

### Improved use (after fix)
After the fix, the frontmatter is structurally valid. Registry parsers index `category: engineering-practice` and `tags: "github-pr, merge, automation, workflow, queue"` correctly, making the skill findable by topic. The `user-invocable: "true"` flag is preserved inside `metadata`, and agent clients that read it can surface `/auto-merge` in their command palette. The skill installs cleanly on any compliant client without warnings.

---

## Improvement 2 — Add Missing `license` Field

### What needs to change

The `license` field is absent from the frontmatter entirely. Without it, any team pulling this skill from the registry has no signal about whether they are permitted to use, modify, or redistribute it. This is both a spec violation and a practical legal gap for teams outside zysk.tech.

### Before
```yaml
---
name: auto-merge
description: "One-shot drain of an auto-ship PR queue. ..."
version: 1.0.0
author: Varun U
# (no license field)
---
```

### After
```yaml
---
name: auto-merge
description: "..."
license: Proprietary — internal use only (zysk.tech)
compatibility: ...
metadata:
  ...
---
```

### Impact if implemented
- **Agent behaviour:** No direct runtime change, but registry tooling that filters by license (e.g., "show only MIT-licensed skills") can correctly categorise this skill as proprietary and exclude it from open-source bundles.
- **Discoverability:** Skills without a `license` field may be flagged or excluded by enterprise registry policies that require an explicit license declaration before installation.
- **Portability:** Teams outside zysk.tech see an explicit "Proprietary — internal use only" signal before adopting the skill, preventing inadvertent misuse.
- **Risk reduced:** Eliminates ambiguity about usage rights; prevents the skill from being bundled into open-source distributions without the author's consent.

### Existing use (before fix)
Today, a developer browsing the skills registry sees `auto-merge` with no license field. If their organisation has a policy of only installing MIT or Apache-licensed skills, there is no machine-readable way to enforce that filter — the skill either installs silently or is blocked by a blanket "no license = blocked" policy. If the developer is outside zysk.tech and uses the skill in a commercial product, there is no indication that this is not permitted.

### Improved use (after fix)
After adding `license: Proprietary — internal use only (zysk.tech)`, the intent is unambiguous. Registry tooling can filter it out of open-source bundles automatically. Developers from other organisations see immediately that the skill is not freely redistributable and can make an informed decision before installing. The spec compliance check for `license` goes from FAIL to PASS.

---

## Improvement 3 — Add Missing `compatibility` Field

### What needs to change

The skill has hard runtime dependencies on four external systems — GitHub CLI (`gh`), Node.js, git, and the project-local `.claude/scripts/queue-io.js` script — plus a structural dependency on a GitHub Projects v2 board with specific field IDs. None of these are declared in a `compatibility` field. If any dependency is missing, the skill fails at runtime with a cryptic error (e.g., `gh: command not found` at Step 2, `MODULE_NOT_FOUND` at Step 5), not at install time when the gap could be surfaced clearly.

### Before
```yaml
---
name: auto-merge
description: "..."
# (no compatibility field)
---
```

### After
```yaml
compatibility: >
  Requires GitHub CLI (gh), Node.js >= 16, and git.
  Designed for Claude Code. Depends on .claude/scripts/queue-io.js for atomic
  queue writes — this file must exist in the project before invoking the skill.
  Board Done-move uses GitHub Projects v2 single-select Status field; swap field
  IDs for your project before use. Hardcoded to zyni-ai/tms-app — update repo
  and org references in the skill body for use in other projects.
```

### Impact if implemented
- **Agent behaviour:** Agent clients that check `compatibility` before running the skill can warn the user at invocation time ("Node.js not found — skill requires it") rather than failing mid-execution at Step 5 after already merging PRs in Step 4.
- **Discoverability:** Registry users searching for skills compatible with their stack (e.g., "Node.js skills") can find this skill correctly.
- **Portability:** Teams adopting the skill from the registry are told upfront about the `queue-io.js` dependency and the need to swap org/repo values — reducing the "why is it broken?" debugging cycle.
- **Risk reduced:** Prevents the worst failure mode: `gh pr merge` succeeds (PR is merged), but `queue-io.js` fails with `MODULE_NOT_FOUND`, leaving the queue file out of sync with no clear error message visible to the user.

### Existing use (before fix)
Today, a developer on a new machine installs `auto-merge`, invokes it with "drain the queue", and the skill runs through Steps 1–3 cleanly using only `gh` queries. At Step 4, `gh pr merge` fires and the PR is squash-merged on GitHub. Then Step 5 calls `node .claude/scripts/queue-io.js` — and Node.js is not installed, or the script does not exist in the new project. The step fails with an unrelated-looking error. The PR is now merged but the queue file still lists it as `awaiting-review`. The next `/auto-merge` run will attempt to merge it again, and only the `state == "MERGED"` check in Step 3 saves it from a duplicate merge attempt. The user has no idea why the queue file is stale.

### Improved use (after fix)
After adding the `compatibility` field, an agent client checks for `gh`, Node.js, and the `queue-io.js` script before invoking Step 1. If any dependency is missing, the user is told immediately: "This skill requires Node.js and `.claude/scripts/queue-io.js` — please install Node.js and copy the script before retrying." The skill never starts, no PRs are merged in a half-complete state, and the queue file stays consistent. Teams adopting the skill from the registry also see the org/repo warning and know to update the hardcoded values before their first run.

---

## Improvement 4 — Bundle `queue-io.js` Inside the Skill Folder

### What needs to change

Step 5 calls `node .claude/scripts/queue-io.js` — a script that lives outside the skill folder, in the project's shared `.claude/scripts/` directory. The skill is not self-contained without it. Anyone installing `auto-merge` from the registry into a project that lacks the `queue-io.js` script gets a runtime `MODULE_NOT_FOUND` failure at the most critical step — after PRs have already been merged. The spec requires bundled scripts to live in the `scripts/` subdirectory of the skill folder.

### Before

File layout:
```
auto-merge/
└── SKILL.md        ← references .claude/scripts/queue-io.js (external)

.claude/
└── scripts/
    └── queue-io.js ← lives here, outside the skill
```

Step 5 invocation in SKILL.md:
```bash
node .claude/scripts/queue-io.js update-and-prune \
  "<absolute-queue-path>" \
  '[...]'
```

### After

File layout:
```
auto-merge/
├── SKILL.md
└── scripts/
    └── queue-io.js   ← bundled here, inside the skill folder
```

Step 5 invocation updated in SKILL.md:
```bash
# Resolve the skill's own scripts/ directory relative to the queue file location
# or use the absolute path to the installed skill folder
node "<skill-dir>/scripts/queue-io.js" update-and-prune \
  "<absolute-queue-path>" \
  '[...]'
```

Note: The agent must resolve `<skill-dir>` to the absolute path of the installed `auto-merge/` folder. Claude Code exposes this as the skill's source directory at invocation time.

### Impact if implemented
- **Agent behaviour:** Step 5 always has access to `queue-io.js` regardless of whether the project has set up `.claude/scripts/`. The atomic write and prune logic runs reliably on every invocation.
- **Discoverability:** No direct impact on discoverability, but a self-contained skill builds trust — developers are more likely to install and recommend skills that work out of the box.
- **Portability:** Any project can install `auto-merge` and get working queue management without needing to manually copy a separate helper script. The skill goes from "partially portable" to fully portable.
- **Risk reduced:** Eliminates the failure mode where Step 4 merges PRs and Step 5 fails silently because `queue-io.js` is absent, leaving the queue file permanently out of sync.

### Existing use (before fix)
Today, a developer on a new project installs `auto-merge` from the registry. They run `/auto-merge` for the first time. Steps 1–4 complete: two PRs are squash-merged on GitHub. Step 5 fires: `node .claude/scripts/queue-io.js update-and-prune ...` — but the new project has never had `queue-io.js` set up. Node exits with `Error: Cannot find module '/project/.claude/scripts/queue-io.js'`. The skill reports a Step 5 failure, but the two PRs are already merged. The queue file is never updated. Every subsequent `/auto-merge` run will see those PRs as `state == "MERGED"` (self-healing), but the queue file accumulates stale entries until manually cleaned. The developer is confused about why the queue isn't pruning.

### Improved use (after fix)
After bundling `queue-io.js` inside `auto-merge/scripts/`, the script is always present at a known path relative to the installed skill. Step 5 resolves the path at runtime and calls the bundled script directly. The atomic write and prune operation runs on every invocation, regardless of the project's `.claude/scripts/` setup. A developer installing `auto-merge` on a fresh project gets a fully working skill on the first run — no manual script copying, no stale queue entries, no confusing `MODULE_NOT_FOUND` errors after a successful merge batch.

---

## Improvement 5 — Strengthen Trigger Keywords in `description`

### What needs to change

The current `description` is technically valid but unlikely to match natural user phrasings. Users typically invoke this skill by saying "drain the queue", "merge the approved PRs", "run auto-merge", or "what's ready to merge" — none of these phrases appear in the current description. The description reads like a spec summary rather than a trigger-optimised field, reducing the chance that an agent dispatcher routes to this skill on the most common invocations.

### Before
```yaml
description: "One-shot drain of an auto-ship PR queue. Re-checks each PR's CI + merge state + review decision, squash-merges what's MERGEABLE + APPROVED + clean of unaddressed comments, and reports per-entry verdict. No scheduler."
```

### After
```yaml
description: >
  One-shot merge queue drain. Use when the user says "drain the queue",
  "merge approved PRs", "run auto-merge", "what's ready to merge", or wants
  to know what's currently mergeable. Re-checks each PR's live CI status,
  review decision, and merge state; squash-merges what is APPROVED and green;
  skips the rest with a clear per-PR verdict. Reads from
  .claude/auto-ship-queue.json written by /auto-ship. No scheduler —
  user-invoked only.
```

### Impact if implemented
- **Agent behaviour:** The agent dispatcher is more likely to route "drain the queue" or "merge approved PRs" to this skill because the description now contains the exact phrases users say. Without this, the dispatcher may fall back to a generic PR merge tool or ask the user for clarification.
- **Discoverability:** Skills are matched against user intent by semantic similarity to the `description`. Including natural-language trigger phrases ("drain the queue", "what's ready to merge") closes the gap between how users ask and how the skill describes itself.
- **Portability:** Clearer trigger language also helps developers who discover the skill in the registry understand immediately when to use it vs. `/handle-review` or `/auto-ship`.
- **Risk reduced:** Reduces the failure mode where the user says "merge the approved PRs" and the agent runs a different, less structured merge tool instead, bypassing the queue's verdict logic and board moves entirely.

### Existing use (before fix)
Today, a developer types "drain the merge queue" into Claude Code. The dispatcher computes semantic similarity between this phrase and all available skill descriptions. The current description — "One-shot drain of an auto-ship PR queue. Re-checks each PR's CI + merge state + review decision..." — contains "drain" but not "merge queue" as a natural phrase. The dispatcher may return a low confidence score and either ask for clarification ("Did you mean /auto-merge?") or route to a generic `gh pr merge` invocation that bypasses the queue entirely, missing the CI check, verdict logic, and board moves.

### Improved use (after fix)
After adding "drain the queue", "merge approved PRs", and "what's ready to merge" to the description, the dispatcher matches confidently on the most common user phrasings. The developer types "merge the approved PRs" and the agent routes directly to `/auto-merge` without prompting. The full Step 0–6 execution path fires: tasks are created, live PR state is re-checked, only genuinely mergeable PRs are squash-merged, the queue is atomically updated, and the Done/Needs attention/Transient report lands in chat. No ambiguity, no fallback to unstructured `gh pr merge`.

---

## Improvement 6 — Add Configuration Block for Hardcoded Project Values

### What needs to change

The skill body contains hardcoded values (`zyni-ai/tms-app`, `.claude/auto-ship-queue.json`, GitHub Projects v2 field IDs) scattered across Steps 1, 4, 5, and the Notes section. The Notes section mentions these must be swapped for other projects, but the warning is easy to miss. A dedicated `## Configuration` section at the top of the body collects all swap targets in one place, making the skill faster to adapt and reducing the chance of a developer running it with the wrong org/repo and accidentally merging PRs into the wrong repository.

### Before
Hardcoded values appear inline throughout the body:
```markdown
## Notes
- Designed to be the second half of an `/auto-ship` → `/auto-merge` loop. Reads `.claude/auto-ship-queue.json` ...
  Project-board Done-move expects GitHub Projects v2 single-select Status field — swap field IDs for your project.
```
No dedicated configuration section exists. `zyni-ai/tms-app` appears embedded in bash examples without a named constant.

### After
Add a `## Configuration` section immediately after the skill description, before `## When to use`:

```markdown
## Configuration

> Swap these values before using this skill in a new project:
>
> | Value | Where used | Default |
> |---|---|---|
> | Org/repo | Steps 2, 4 (`--repo` flag) | `zyni-ai/tms-app` |
> | Queue file path | Steps 1, 5 | `.claude/auto-ship-queue.json` |
> | Rebase target branch | Step 4 (`rebase origin/dev`) | `dev` |
> | GitHub Projects v2 field IDs | Step 4 (Done-board mutation) | See project board → Settings → Fields |
> | Bundled queue helper | Step 5 | `scripts/queue-io.js` (relative to skill folder) |
```

### Impact if implemented
- **Agent behaviour:** When an agent is asked to adapt this skill for a new project, it has a single authoritative list of swap targets rather than needing to grep the body for hardcoded values. Reduces adaptation errors.
- **Discoverability:** No direct impact on routing, but a clear Configuration section signals to registry browsers that the skill is designed to be adapted, increasing adoption likelihood.
- **Portability:** Developers no longer need to read all 200 lines of the body to find every hardcoded value. The Configuration table is the single source of truth for what needs changing.
- **Risk reduced:** Prevents the dangerous failure mode where a developer copies the skill to a new project, misses the Notes-section warning, and the first `/auto-merge` run fires `gh pr merge` against `zyni-ai/tms-app` — merging PRs into the wrong repository.

### Existing use (before fix)
A developer at a different company finds `auto-merge` in the registry and wants to use it for their own project. They read the skill and note the Step 2 bash snippet uses `--repo "<entry.repo>"` (parameterised via the queue entry — fine), but Step 4's Done-board mutation has hardcoded GitHub Projects v2 field IDs. The Notes section at the bottom mentions "swap field IDs for your project", but the developer has already skimmed past it. They run `/auto-merge` and the board mutation silently fails (wrong field IDs) — PRs merge successfully but issues are never moved to Done. The developer debugs for an hour before finding the hardcoded IDs in Step 4.

### Improved use (after fix)
After adding the Configuration section at the top of the body, the developer reads it immediately and sees "GitHub Projects v2 field IDs — swap before use". They update the IDs before their first run. The board mutation fires correctly, issues move to Done, and the full skill output matches expectations. The adaptation takes five minutes instead of an hour of debugging.

---

## Priority Order

| Priority | Improvement | Effort | Impact |
|---|---|---|---|
| 1 | Move nine custom fields under `metadata:` | Low | Critical — spec violation; causes registry parsing failures |
| 2 | Bundle `queue-io.js` inside the skill folder | Medium | Critical — skill is non-functional on fresh installs without it |
| 3 | Add missing `compatibility` field | Low | High — surfaces hard deps before runtime failures occur |
| 4 | Add missing `license` field | Low | High — required by spec; blocks enterprise registry policies |
| 5 | Strengthen trigger keywords in `description` | Low | High — directly affects agent routing on the most common user phrasings |
| 6 | Add Configuration block for hardcoded project values | Low | Medium — prevents silent wrong-repo/wrong-board failures on adaptation |

---

## Before vs After: Full Skill Experience

### Before (current state)

A developer discovers `auto-merge` in the shared registry and installs it into a new project. Immediately, the registry parser warns about non-standard top-level frontmatter fields (`version`, `author`, `category`, `tags`, `product`, `sprint`, `tested_with`, `user-invocable`) — or worse, silently drops them, making the skill invisible in category and tag searches. The `user-invocable: true` flag may be stripped, hiding `/auto-merge` from the command palette. There is no `license` field, so the developer's organisation's registry policy flags the skill as "license unknown" and may block installation automatically.

Assuming the skill installs, the developer types "merge the approved PRs" into Claude Code. The dispatcher runs semantic matching against the current description — "One-shot drain of an auto-ship PR queue. Re-checks each PR's CI + merge state + review decision..." — and may not match confidently on "merge the approved PRs", asking for clarification or routing to a generic `gh pr merge` instead. If routing does succeed, Steps 1–4 execute correctly: PRs are re-checked and two are squash-merged. Then Step 5 fires `node .claude/scripts/queue-io.js` — but the new project does not have this script. Node exits with `MODULE_NOT_FOUND`. The queue file is never updated, the merged PRs remain listed as `awaiting-review`, and the developer is left with a half-complete run and a confusing error. There is also no `compatibility` field warning them upfront that `queue-io.js` must exist before the skill can run.

### After (all improvements applied)

After all six improvements are applied, the frontmatter is fully spec-compliant: nine custom fields are nested correctly under `metadata:`, `license: Proprietary — internal use only (zysk.tech)` is declared, and `compatibility` lists all four hard dependencies (`gh`, Node.js, git, `queue-io.js`) plus the GitHub Projects v2 board requirement. The registry parser indexes the skill cleanly, `user-invocable: "true"` is preserved, and the skill appears in category, tag, and author searches.

On a fresh install, the bundled `auto-merge/scripts/queue-io.js` is present at a known path. The `compatibility` field allows the agent client to verify all dependencies before Step 1 even starts — if Node.js is absent, the user is told immediately rather than discovering it mid-run after PRs have already been merged. The strengthened `description` field now includes "drain the queue", "merge approved PRs", and "what's ready to merge", so the dispatcher routes confidently on the most natural user phrasings without ambiguity.

When the developer types "drain the queue", the skill runs end-to-end cleanly: live PR state is re-checked for each entry, verdicts are assigned in the defined order, approved-and-green PRs are squash-merged, the bundled `queue-io.js` atomically updates the queue file, and the Done / Needs your attention / Transient report lands in chat with per-PR verdicts. Developers adapting the skill to a new project find the Configuration section immediately at the top of the body, swap the five listed values, and their first run fires against the correct repository and board. The entire experience — from registry discovery to first successful merge batch — is friction-free and self-documenting.
