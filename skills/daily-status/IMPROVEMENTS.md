# IMPROVEMENTS — daily-status

> Improvement plan derived from SKILL.md + ANALYSIS.md audit against the agentskills.openml.io spec.

---

## Quick Summary

| | Before | After |
|---|---|---|
| Spec compliance | Partially compliant | Fully compliant |
| Critical violations | 3 | 0 |
| Agent discoverability | Medium | High |
| Portability | Partial | Pass |

---

## Improvement 1 — Move Non-Standard Frontmatter Fields Under `metadata:`

### What needs to change
Eight non-standard top-level frontmatter fields (`version`, `author`, `email`, `category`, `tags`, `product`, `sprint`, `tested_with`) must be nested under a `metadata:` key. The spec only allows a defined set of fields at the top level; all custom fields must live under `metadata:`.

### Before
```yaml
---
name: daily-status
description: Generate the end-of-day client status report by scanning today's git commits, uncommitted changes, and GitHub PRs, then interviewing the user to classify each item. Use whenever the user asks for their daily status, EOD report, or client update — or types /daily-status.
version: 1.2.0
author: Shilpa VP
email: shilpa@zysk.tech
category: comms
tags:
  - daily-status
  - eod-report
  - git
  - github
  - reporting
product: zysk
sprint: 1
tested_with: claude-opus-4-7
---
```

### After
```yaml
---
name: daily-status
description: Generate the end-of-day client status report by scanning today's git commits, uncommitted changes, and GitHub PRs, then interviewing the user to classify each item. Use whenever the user asks for their daily status, EOD report, or client update — or types /daily-status.
license: MIT
compatibility: Requires Python 3.8+, git CLI, and optionally gh CLI (GitHub CLI) for PR data. Tested on macOS and Linux. Windows support is untested.
metadata:
  version: 1.2.0
  author: Shilpa VP
  email: shilpa@zysk.tech
  category: comms
  tags:
    - daily-status
    - eod-report
    - git
    - github
    - reporting
  product: zysk
  sprint: 1
  tested_with: claude-opus-4-7
---
```

### Impact if implemented
- **Agent behaviour:** Parsers and registry tooling that validate frontmatter against the spec schema will no longer reject this skill. Fields like `version` and `author` will be accessible via the standard `metadata.*` path used by indexers.
- **Discoverability:** Registry indexers that filter by `metadata.tags` or `metadata.category` will correctly surface this skill for queries like "comms" or "eod-report".
- **Portability:** Any team ingesting this skill into their own registry will not encounter schema validation failures caused by stray top-level keys.
- **Risk reduced:** Prevents silent data loss where indexers ignore unrecognised top-level keys, making `version`, `author`, and `tested_with` invisible to tooling.

### Existing use (before fix)
Today, when the skills registry runs its index generation step (e.g., the `regenerate-index` workflow), it reads each SKILL.md frontmatter block. Because `version`, `author`, `email`, `category`, `tags`, `product`, `sprint`, and `tested_with` are at the top level rather than under `metadata:`, any spec-compliant parser will either reject them as unknown keys or silently drop them. A developer searching the registry for skills tagged `eod-report` or filtered by `category: comms` will get no result for `daily-status` even though those values are present in the file.

### Improved use (after fix)
After nesting all eight fields under `metadata:`, the frontmatter is fully spec-compliant. The `regenerate-index` workflow picks up `metadata.tags`, `metadata.category`, and `metadata.version` correctly. Searching the registry for `comms` skills or filtering by `eod-report` tag returns `daily-status` as expected. The `tested_with: claude-opus-4-7` value is also preserved and queryable, which helps teams decide whether the skill is safe to run on their current model version.

---

## Improvement 2 — Add Missing `license` Field

### What needs to change
The `license` field is a required top-level field in the agentskills.io spec and is entirely absent from the current frontmatter. Without it, the skill cannot be safely published to a shared registry because consuming teams have no legal clarity on reuse rights.

### Before
```yaml
---
name: daily-status
description: Generate the end-of-day client status report by scanning today's git commits, uncommitted changes, and GitHub PRs, then interviewing the user to classify each item. Use whenever the user asks for their daily status, EOD report, or client update — or types /daily-status.
version: 1.2.0
author: Shilpa VP
# ... (no license field present)
---
```

### After
```yaml
---
name: daily-status
description: Generate the end-of-day client status report by scanning today's git commits, uncommitted changes, and GitHub PRs, then interviewing the user to classify each item. Use whenever the user asks for their daily status, EOD report, or client update — or types /daily-status.
license: MIT
# ... remaining fields
---
```

### Impact if implemented
- **Agent behaviour:** No direct change to runtime behaviour, but automated spec-compliance checkers (including the ANALYSIS.md validator used to produce this audit) will no longer flag this as a critical violation.
- **Discoverability:** Registry UI tools that display license badges or filter by license type will now show this skill correctly instead of showing "Unknown" or hiding it from filtered views.
- **Portability:** Other teams and contributors can safely adopt, modify, and redistribute the skill without ambiguity about permitted use. This is especially relevant for `scripts/collect_activity.py`, which is a bundled Python script.
- **Risk reduced:** Eliminates the legal ambiguity that blocks enterprise teams from adopting skills that lack an explicit license declaration.

### Existing use (before fix)
Currently, when a developer at another organisation discovers `daily-status` in the public registry and wants to adapt `scripts/collect_activity.py` for their own EOD workflow, they have no licence declaration to rely on. The registry audit tool marks the skill as "Partially compliant" specifically because of this missing field. Any automated gate that requires `license` to be present before publishing to a production registry will block this skill from being promoted.

### Improved use (after fix)
With `license: MIT` in the frontmatter, the skill passes the required-field check. Teams can adopt and fork the bundled `scripts/collect_activity.py` with confidence. The registry compliance score moves from "Partially compliant" to "Fully compliant" once the other violations are also fixed, and automated promotion gates no longer block the skill.

---

## Improvement 3 — Add Missing `compatibility` Field for External Tool Dependencies

### What needs to change
The skill depends on three external tools — `python3` (version 3.8+), `git`, and optionally `gh` CLI — none of which are documented in the frontmatter `compatibility` field. The spec requires this field when a skill has runtime prerequisites. Without it, users in environments that lack Python 3 or `git` will encounter silent failures with no guidance.

### Before
```yaml
---
name: daily-status
description: Generate the end-of-day client status report by scanning today's git commits, uncommitted changes, and GitHub PRs, then interviewing the user to classify each item. Use whenever the user asks for their daily status, EOD report, or client update — or types /daily-status.
version: 1.2.0
# ... (no compatibility field present)
---
```

### After
```yaml
---
name: daily-status
description: Generate the end-of-day client status report by scanning today's git commits, uncommitted changes, and GitHub PRs, then interviewing the user to classify each item. Use whenever the user asks for their daily status, EOD report, or client update — or types /daily-status.
license: MIT
compatibility: Requires Python 3.8+, git CLI, and optionally gh CLI (GitHub CLI) for PR data. Tested on macOS and Linux. Windows support is untested.
metadata:
  ...
---
```

### Impact if implemented
- **Agent behaviour:** When the skill is loaded in an environment without Python 3, the agent can surface the compatibility note before attempting Step 1 (`python3 scripts/collect_activity.py --pretty`), giving the user an actionable error rather than a cryptic `command not found`.
- **Discoverability:** Registry search tools that filter by platform or runtime requirements (e.g., "skills that work on Linux") will correctly include or exclude `daily-status`.
- **Portability:** Windows users, who are most likely to lack `python3` in PATH or use a different `gh` CLI setup, are explicitly warned in the frontmatter rather than discovering the limitation mid-workflow.
- **Risk reduced:** Prevents the silent failure where Step 1 aborts with a Python error and the agent has no spec-backed signal to explain why, leaving the user with a broken EOD workflow and no diagnostics.

### Existing use (before fix)
Today, a developer on a Windows machine (or a fresh macOS machine without Homebrew) triggers `/daily-status`, and the agent proceeds to Step 1 where it runs `python3 scripts/collect_activity.py --pretty`. If `python3` is not in PATH, the command fails immediately. The agent has no frontmatter signal that Python is required, so it either retries, surfaces a generic error, or falls through the step silently. The user is left wondering why the skill produced no git activity data. Similarly, the note in the SKILL.md body that "gh CLI auth is optional" is buried in the Notes section at the bottom, not surfaced as a frontmatter prerequisite.

### Improved use (after fix)
With `compatibility: Requires Python 3.8+, git CLI, and optionally gh CLI (GitHub CLI) for PR data. Tested on macOS and Linux. Windows support is untested.` in the frontmatter, agents and registry tooling can pre-flight check dependencies before Step 1 runs. A Windows user sees an upfront warning. A macOS user on a fresh machine is told to install Python 3.8+. The optional nature of `gh` CLI is documented at the spec level, reinforcing the runtime note already in the SKILL.md body.

---

## Improvement 4 — Condense Inline Rationale Paragraphs to Reduce Token Cost

### What needs to change
Two inline rationale blocks add token overhead without contributing to agent execution. The paragraph under Step 1 ("Why a script instead of inline bash: doing this in shell required ~5 commands per repo...") and the paragraph under Step 4 ("Why one at a time: when these are batched, users skim and drop the Need Discussion items...") are useful to human authors but increase the per-activation token cost. The ANALYSIS.md recommends condensing them to a single sentence each or moving them to a dedicated Design Notes section.

### Before
```markdown
### Step 1 — Collect git activity

Run the bundled collector:

```bash
python3 scripts/collect_activity.py --pretty
```

It reads the config, runs `git log` / `git status` / `git diff` / `git branch` per repo in parallel, calls `gh pr list` when `gh` is authenticated, filters noise commits and noise files (`.DS_Store` etc.), and emits one JSON document covering every configured repo.

Why a script instead of inline bash: doing this in shell required ~5 commands per repo plus manual JSON stitching on every invocation. The script does it once, in parallel, with consistent filtering — so this skill stays focused on judgment (classify, summarize, interview) rather than orchestration.
```

and

```markdown
### Step 4 — Free-text extras

Ask these three questions **one at a time**, in order, waiting for each reply before moving on.

Why one at a time: when these are batched, users skim and drop the **Need Discussion** items, which are the most valuable part of the report — they surface the blockers and decisions the client owes you. Ask every question even if the previous answer was empty; *"no meetings today"* and *"no discussion points"* are still answers, and silently skipping a section creates ambiguity for the client.
```

### After
```markdown
### Step 1 — Collect git activity

Run the bundled collector:

```bash
python3 scripts/collect_activity.py --pretty
```

It reads the config, runs `git log` / `git status` / `git diff` / `git branch` per repo in parallel, calls `gh pr list` when `gh` is authenticated, filters noise commits and noise files (`.DS_Store` etc.), and emits one JSON document covering every configured repo. The script handles parallel execution and JSON stitching so this skill stays focused on classifying and summarising work.
```

and

```markdown
### Step 4 — Free-text extras

Ask these three questions **one at a time**, in order, waiting for each reply before moving on. Batching them causes users to skip **Need Discussion** items — ask each question even if the previous answer was empty.
```

And add a new section at the bottom of the skill body:

```markdown
## Design Notes

- **Script over inline bash (Step 1):** Running git log / git status / git diff / git branch per repo in plain bash required ~5 commands per repo plus manual JSON stitching on every invocation. The Python script does it once, in parallel, with consistent filtering.
- **One question at a time (Step 4):** Batching the free-text questions causes users to skim and drop Need Discussion items, which are the highest-value part of the report. Asking sequentially ensures each section gets a deliberate answer.
```

### Impact if implemented
- **Agent behaviour:** Each skill invocation loads fewer tokens, which reduces the risk of hitting context limits when the skill is composed with other tools or invoked in a long session. The step-by-step instructions remain complete and actionable.
- **Discoverability:** No change to discoverability — rationale text does not affect search indexing.
- **Portability:** Human authors reviewing or forking the skill still have access to the design rationale, now consolidated in one place at the end rather than scattered mid-step.
- **Risk reduced:** Prevents token bloat from accumulating as the skill is iterated on; a Design Notes section makes it easier to update rationale independently from executable instructions.

### Existing use (before fix)
Today, every time an agent activates `daily-status`, it loads the full SKILL.md body including both rationale paragraphs. The Step 1 rationale is ~60 tokens and the Step 4 rationale is ~70 tokens. While the skill is currently well under the 5000-token recommendation (~2603 tokens), these inline paragraphs break the flow of the numbered steps — a reader (or agent) following Step 1 encounters an explanatory detour before moving to Step 2. The same issue occurs in Step 4, where the rationale paragraph precedes the actual question list, adding cognitive overhead before the agent reaches the actionable instructions.

### Improved use (after fix)
After condensing the rationale to one sentence per step and moving the detailed explanation to a Design Notes section, the numbered steps read as clean, sequential instructions. An agent executing the skill processes Steps 1 through 5 without detours. Authors and reviewers who want to understand the design decisions can find them consolidated in Design Notes at the end. The overall token count drops by approximately 100-130 tokens, providing headroom for future step additions without approaching the budget ceiling.

---

## Priority Order

| Priority | Improvement | Effort | Impact |
|---|---|---|---|
| 1 | Move non-standard fields under `metadata:` | Low | Critical |
| 2 | Add missing `license` field | Low | Critical |
| 3 | Add missing `compatibility` field | Low | High |
| 4 | Condense inline rationale paragraphs | Medium | Medium |

---

## Before vs After: Full Skill Experience

### Before (current state)

A developer discovers `daily-status` in the skills registry and wants to use it for their EOD reporting workflow. Before they even trigger the skill, the registry's index generator has already silently dropped the `tags`, `category`, and `version` fields because they sit at the top level of the frontmatter instead of under `metadata:`. A search for skills tagged `eod-report` returns nothing, so the developer has to find the skill by browsing directly. When they inspect the frontmatter to check compatibility, there is no `license` field and no `compatibility` field — they cannot tell whether the skill is safe to redistribute, nor whether their environment (a Windows dev machine without `python3` in PATH) will even run it.

The developer triggers `/daily-status` anyway. The agent loads the SKILL.md, processes the step-by-step instructions, and reaches Step 1: `python3 scripts/collect_activity.py --pretty`. On their Windows machine, `python3` is not in PATH. The command fails. The agent has no frontmatter signal that Python 3.8+ is a prerequisite, so it surfaces a generic error with no actionable guidance. The developer is stuck and has to read the Notes section at the bottom of the SKILL.md to piece together what went wrong.

Even for developers on macOS or Linux where the skill runs successfully, the inline rationale paragraphs in Steps 1 and 4 interrupt the flow of the numbered instructions. An agent following Step 1 reads a 60-token explanation of why a Python script was chosen before it can move on — and similarly for Step 4. These paragraphs are valuable context but are placed where they add friction rather than clarity, and they consume token budget that will matter as the skill grows.

### After (all improvements applied)

With all four improvements applied, the `daily-status` skill is fully spec-compliant. The registry index generator correctly picks up `metadata.tags` (including `eod-report` and `git`), `metadata.category: comms`, and `metadata.version: 1.2.0`. A developer searching for `comms` skills or filtering by `eod-report` immediately finds `daily-status`. The `license: MIT` field removes any ambiguity about redistribution rights, and the `compatibility` field — "Requires Python 3.8+, git CLI, and optionally gh CLI (GitHub CLI) for PR data. Tested on macOS and Linux. Windows support is untested." — gives both agents and humans an upfront signal about runtime requirements before Step 1 is ever attempted.

On a Windows machine, the agent reads the `compatibility` field at skill load time and surfaces a clear prerequisite warning: Python 3.8+ is required and Windows support is untested. The developer can install the dependency or switch to a compatible environment before proceeding, instead of hitting a cryptic failure mid-workflow. On macOS and Linux, the skill runs exactly as before but now with a spec-compliant frontmatter that passes automated compliance gates, enabling the skill to be promoted to production registries without manual review exceptions.

The condensed rationale in Steps 1 and 4 keeps each step's instructions tight and sequential. The full design reasoning is preserved in the new Design Notes section at the end of the skill body, where it serves as reference material without interrupting the execution flow. An agent activating the skill processes approximately 100-130 fewer tokens per invocation, providing headroom for future enhancements. Human contributors who want to understand why the skill uses a Python script instead of inline bash, or why Step 4 asks questions one at a time, find the explanation immediately in Design Notes rather than having to hunt through the numbered steps.
