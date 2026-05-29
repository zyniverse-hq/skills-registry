# IMPROVEMENTS — auto-ship

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

## Improvement 1 — Move Custom Frontmatter Fields Under `metadata:`

### What needs to change

Nine custom fields (`version`, `author`, `email`, `category`, `tags`, `product`, `sprint`, `tested_with`, `user-invocable`) sit at the top level of the YAML frontmatter. The agentskills spec defines exactly six top-level keys: `name`, `description`, `license`, `compatibility`, `metadata`, `allowed-tools`. All custom fields must be nested under `metadata:` as string key-value pairs. Arrays (like `tags`) must be flattened to comma-separated strings.

### Before
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

### After
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

### Impact if implemented
- **Agent behaviour:** Parsers that validate frontmatter against the spec schema will no longer reject this skill on load; agents using the registry index will surface the skill correctly.
- **Discoverability:** No direct change to trigger matching, but a correctly-structured skill is indexed without parse warnings, making it consistently available.
- **Portability:** Any team copying this skill into their registry gets a spec-compliant file that doesn't fail frontmatter validation on ingest.
- **Risk reduced:** Prevents silent schema-validation failures in registries that enforce strict frontmatter parsing.

### Existing use (before fix)
Today, any tool or script that validates skill frontmatter against the agentskills spec will encounter nine unknown top-level keys and either reject the skill entirely or surface it with validation warnings. The `tags` field is a YAML list rather than a string, which breaks parsers expecting scalar values under top-level keys. The `sprint: 4` and `user-invocable: true` values are also unquoted non-string scalars. A developer importing this skill into a new project via an automated registry ingestion script will see parse errors and may skip the skill entirely.

### Improved use (after fix)
After moving all nine fields under `metadata:` and quoting non-string values, the frontmatter is fully spec-compliant. Registry ingestion scripts parse the file without warnings. The `tags` string remains searchable via substring match. Developers copying the skill to a new project get a clean import with zero schema violations.

---

## Improvement 2 — Add Missing `license` Field

### What needs to change

The `license` field is required by the spec and is completely absent from the current frontmatter. Without it, any team or developer picking up this skill from the registry has no signal about usage rights — they cannot legally determine whether they can copy, modify, or redistribute the skill.

### Before
```yaml
---
name: auto-ship
description: "Autonomous issue-to-PR pipeline. ..."
version: 1.0.0
author: Varun U
# ... (no license field anywhere in frontmatter)
```

### After
```yaml
---
name: auto-ship
description: "..."
license: Proprietary — internal use only (zysk.tech)
compatibility: ...
metadata:
  ...
```

### Impact if implemented
- **Agent behaviour:** No direct change to execution logic, but the skill passes full spec compliance checks.
- **Discoverability:** Compliant skills are indexed; non-compliant skills may be filtered out of registry searches in stricter implementations.
- **Portability:** Teams evaluating whether to adopt this skill know immediately that it is internal to zysk.tech and must be adapted, not copied verbatim.
- **Risk reduced:** Removes legal ambiguity for any developer who encounters this skill in a shared or public registry.

### Existing use (before fix)
Currently there is no `license` field. A developer browsing the skills registry sees no usage rights signal. If the registry is ever made semi-public or shared across teams, this skill could be copied and used without attribution or awareness that it is proprietary. Spec validators that require `license` will flag this skill as non-compliant on every audit.

### Improved use (after fix)
With `license: Proprietary — internal use only (zysk.tech)` present, developers immediately understand the usage context. Spec validators pass the `license` check. If the skill is ever open-sourced, the field is already in place to update (e.g., to `MIT`).

---

## Improvement 3 — Add Missing `compatibility` Field

### What needs to change

The skill has hard runtime dependencies on the GitHub CLI (`gh`), Node.js, the external script `.claude/scripts/queue-io.js`, GitHub Projects v2 (specifically `projectV2(number: 18)` under `organization(login: "zyni-ai")`), and the `/ship-issue` base skill. None of these are declared in a `compatibility` field. The spec requires this field to surface dependency requirements so users know before running whether their environment can support the skill.

### Before
```yaml
---
name: auto-ship
description: "..."
# no compatibility field
```

The only mention of dependencies is a single sentence buried at the bottom of the Notes section:
> "Deeply coupled to TMS infrastructure: organization(login: \"zyni-ai\"), projectV2(number: 18), zyni-ai/tms-app repo, .claude/auto-ship-queue.json file, .claude/scripts/queue-io.js helper."

### After
```yaml
compatibility: >
  Requires GitHub CLI (gh) authenticated to the target GitHub org and
  Node.js (any LTS version). Designed for Claude Code. Depends on
  scripts/queue-io.js (bundled in skill folder) for atomic queue writes —
  must exist before Step 6 runs. Board operations require GitHub Projects v2;
  defaults to project #18 under organization zyni-ai (swap project number and
  org for your project). Invokes /ship-issue as a required base skill —
  /ship-issue must be installed and accessible. Queue file defaults to
  .claude/auto-ship-queue.json in the project root.
```

### Impact if implemented
- **Agent behaviour:** Agents that pre-check compatibility before invoking a skill can surface a clear error ("Node.js not found" or "`gh` not authenticated") rather than failing mid-execution at Step 6 when the queue write is attempted.
- **Discoverability:** Developers scanning the registry can filter skills by compatibility requirements (e.g., "only skills that work without Node.js").
- **Portability:** Any team adopting this skill sees upfront that they need to swap `projectV2(number: 18)` and `organization(login: "zyni-ai")` — not just in the Notes section after they've already tried to run it.
- **Risk reduced:** Prevents the silent failure mode where `queue-io.js` is missing and the skill executes Steps 1–5 successfully, opens PRs, then fails at Step 6 — leaving PRs that `/auto-merge` will never see.

### Existing use (before fix)
Today, a developer on a new machine or a new project clones the skills registry, sees `auto-ship`, and invokes `/auto-ship`. The skill runs Steps 1–5 without issue (assuming `gh` is installed), opens PRs on GitHub, then crashes at Step 6 when `node .claude/scripts/queue-io.js` cannot find the file. The PRs are now orphaned — they exist on GitHub but have no queue entries, so `/auto-merge` will never drain them. The developer must manually recover using the Recovery table. There is no upfront signal that `queue-io.js` was required.

### Improved use (after fix)
With `compatibility` declared and `queue-io.js` bundled (see Improvement 4), a developer scanning the registry sees the Node.js and `gh` requirements before invoking. If an agent pre-checks the `compatibility` field, it surfaces a clear "Node.js required" message before any execution begins. The bundled script means the queue write never fails due to a missing external dependency.

---

## Improvement 4 — Bundle `queue-io.js` Inside the Skill Folder

### What needs to change

Step 6 calls `.claude/scripts/queue-io.js` — a file that lives outside the skill folder in the project's `.claude/scripts/` directory. This means the skill is not self-contained. Anyone copying `skills/auto-ship/` to a new project without the matching `.claude/scripts/` scaffolding will hit a hard failure at Step 6. The fix is to copy `queue-io.js` into `skills/auto-ship/scripts/queue-io.js` and update all body references.

### Before

Skill folder structure:
```
skills/auto-ship/
└── SKILL.md
```

Step 6 call in SKILL.md:
```bash
node .claude/scripts/queue-io.js append \
  "<absolute-queue-path>" \
  '{ ... }'
```

### After

Skill folder structure:
```
skills/auto-ship/
├── SKILL.md
└── scripts/
    └── queue-io.js
```

Step 6 call in SKILL.md (updated path):
```bash
node "$(dirname "$0")/../../skills/auto-ship/scripts/queue-io.js" append \
  "<absolute-queue-path>" \
  '{ ... }'
```

Or, using an environment variable resolved at skill-load time:
```bash
node "${SKILL_DIR}/scripts/queue-io.js" append \
  "<absolute-queue-path>" \
  '{ ... }'
```

All three occurrences of `.claude/scripts/queue-io.js` in SKILL.md (Step 6 body, the atomic-write paragraph, and the Recovery table) must be updated to the bundled relative path.

### Impact if implemented
- **Agent behaviour:** Step 6 no longer depends on a file that may not exist in the target project. The skill's queue write is reliable regardless of project scaffolding state.
- **Discoverability:** No change to trigger matching, but the skill becomes installable via a simple folder copy — no separate scaffolding step.
- **Portability:** A team on a different project can copy `skills/auto-ship/` and run `/auto-ship` without first setting up `.claude/scripts/`. This is the single largest portability blocker in the current skill.
- **Risk reduced:** Eliminates the "PR opened but queue entry missing" failure mode described in the Recovery table — the root cause of that failure is exactly this missing external script.

### Existing use (before fix)
Today, the skill assumes `.claude/scripts/queue-io.js` exists in the project root's `.claude/scripts/` directory. On the zysk.tech TMS project this is true, so the skill works. But if a developer on a fresh project or a different repo invokes `/auto-ship`, the skill executes all of Steps 1–5 (potentially opening multiple PRs on GitHub), then hits a Node.js `MODULE_NOT_FOUND` error at Step 6. The PRs exist on GitHub with no queue entries. Per the Recovery table, the developer must manually re-run the `queue-io.js append` command — but they don't have the script, so recovery itself fails. The PRs are permanently invisible to `/auto-merge`.

### Improved use (after fix)
With `queue-io.js` bundled at `skills/auto-ship/scripts/queue-io.js`, the skill is fully self-contained. Step 6 resolves the script path relative to the skill folder and runs successfully regardless of whether `.claude/scripts/` exists in the project. A developer copying just the `auto-ship/` folder to a new project gets working queue writes immediately. The Recovery table's "Step 6 queue append failed" row becomes far less likely to be needed.

---

## Improvement 5 — Strengthen Trigger Keywords in `description`

### What needs to change

The current `description` is technically accurate but optimized for someone who already knows the skill name. Users who say "drain Todo", "ship these issues automatically", "batch ship all the bugs", or "run overnight shipment" will not reliably trigger this skill because none of those natural phrasings appear in the description. The description needs to front-load common trigger phrases so agent routing matches on natural user language.

### Before
```yaml
description: "Autonomous issue-to-PR pipeline. Auto-picks eligible Todo items (or a passed subset), classifies into quick-fix / clear-scope / ambiguous, ships everything non-ambiguous into reviewable PRs, records each in a merge queue, and stops at PR open."
```

### After
```yaml
description: >
  Autonomous issue-to-PR pipeline. Use when the user says "drain Todo",
  "ship these issues", "batch ship", "auto-ship", "ship all bugs", "run
  overnight", or wants to autonomously convert pre-triaged Todo items into
  PRs without checkpoints. Auto-picks eligible Todo issues in priority order
  (or ships an explicit subset like /auto-ship 2780 2779), classifies each as
  quick-fix / clear-scope / ambiguous, opens PRs for non-ambiguous items, and
  appends each to the auto-merge queue. Stops at PR open — /auto-merge handles
  the merge step.
```

### Impact if implemented
- **Agent behaviour:** Agent routing logic that matches user utterances against skill descriptions will now hit on "drain Todo", "batch ship", "ship all bugs", "run overnight", and "ship these issues" — the most common natural phrasings for this skill's use case.
- **Discoverability:** Significantly improved. The current description requires the user to already know the term "autonomous issue-to-PR pipeline" — a phrase no one says naturally. The improved version meets users where they are.
- **Portability:** No change to portability, but the skill becomes more useful to teams who don't read documentation before invoking skills.
- **Risk reduced:** Reduces the failure mode where a user says "drain Todo" and the agent picks `/ship-issue` (single issue) or no skill at all, because `/auto-ship`'s description didn't match.

### Existing use (before fix)
A developer says "hey, drain the Todo column overnight." The agent scans skill descriptions. `/auto-ship`'s description says "Autonomous issue-to-PR pipeline" — no match on "drain" or "overnight." The agent either picks the wrong skill or asks the user to clarify. The user is confused because they know `/auto-ship` exists but the agent didn't find it. The skill is effectively invisible to its most natural invocation pattern.

### Improved use (after fix)
The same developer says "drain the Todo column overnight." The agent matches "drain Todo" in the description and routes directly to `/auto-ship`. The explicit invocation modes in the description also clarify that passing issue numbers (e.g., `/auto-ship 2780 2779`) is supported, which users may not discover otherwise. Both the default and explicit-batch modes become naturally discoverable.

---

## Improvement 6 — Add Configuration Block for Hardcoded Project Values

### What needs to change

The values `zyni-ai/tms-app`, `projectV2(number: 18)`, `organization(login: "zyni-ai")`, and `.claude/auto-ship-queue.json` appear in multiple places throughout the body (Step 2a GraphQL query, Step 3c label command, Step 5 pre-flight query, Step 6 queue path, Notes section). A developer adapting this skill for a new project must hunt through every occurrence. A dedicated Configuration section at the top of the body surfaces all swap points in one place.

### Before

Values scattered across body — examples:
```bash
# Step 2a
organization(login: "zyni-ai") {
  projectV2(number: 18) {

# Step 3c
gh issue edit <N> --repo zyni-ai/tms-app --add-label "status: needs investigation"

# Step 5 pre-flight
repository(owner: "zyni-ai", name: "tms-app") {

# Step 6
node .claude/scripts/queue-io.js append \
  "<absolute-queue-path>" \
  '{ ... "repo": "zyni-ai/tms-app" ... }'
```

The Notes section at the bottom says: "Swap all of these for your project's equivalents" — but lists them only once and only at the end.

### After

Add a Configuration section immediately after the introductory table and before "When to use":

```markdown
## Configuration

> Swap these values for your project before use. They appear in Steps 2a, 3c, 5, and 6.

| Variable | Default (TMS) | Where used |
|---|---|---|
| GitHub org | `zyni-ai` | Step 2a GraphQL query, Step 5 pre-flight |
| Repo | `zyni-ai/tms-app` | Step 3c label commands, Step 5 pre-flight, Step 6 queue entry |
| Project board number | `18` | Step 2a GraphQL query |
| Queue file path | `.claude/auto-ship-queue.json` | Step 6 atomic write |
| Queue script path | `scripts/queue-io.js` (bundled) | Step 6 atomic write |
```

### Impact if implemented
- **Agent behaviour:** No change to execution logic, but an agent reading the skill to plan an adaptation can locate all swap points in under 10 seconds instead of scanning ~400 lines.
- **Discoverability:** No change to trigger matching.
- **Portability:** A developer adapting this skill for a new project has a checklist of every value that must change. Reduces the risk of shipping a PR with `zyni-ai/tms-app` hardcoded in Step 5 because the developer forgot to update one occurrence.
- **Risk reduced:** Prevents the silent failure mode where a developer swaps the repo in Step 2a but forgets Step 5's pre-flight query — which then checks the wrong repo and race-skips every issue.

### Existing use (before fix)
A developer adapts `/auto-ship` for their project, updates the obvious Step 2a GraphQL query org/repo, and runs the skill. Step 5's pre-flight query still points to `zyni-ai/tms-app` (one of four separate occurrences the developer missed). Every issue fails the pre-flight check because the query returns no results for the correct repo. The developer sees "race lost" for every issue and has no obvious reason why. They grep the skill body and find three more hardcoded occurrences they missed.

### Improved use (after fix)
The Configuration table at the top of the skill body lists all four swap points with step references. The developer updates the table for documentation, then uses it as a checklist to update each body occurrence. Every occurrence is updated before the first run. The skill executes against the correct repo from the first invocation.

---

## Priority Order

| Priority | Improvement | Effort | Impact |
|---|---|---|---|
| 1 | Bundle `queue-io.js` inside skill folder | Medium | Critical |
| 2 | Move custom frontmatter fields under `metadata:` | Low | Critical |
| 3 | Add missing `compatibility` field | Low | High |
| 4 | Add missing `license` field | Low | High |
| 5 | Strengthen trigger keywords in `description` | Low | High |
| 6 | Add Configuration block for hardcoded project values | Low | Medium |

---

## Before vs After: Full Skill Experience

### Before (current state)

A developer discovers `auto-ship` in the skills registry and wants to use it on their own GitHub project. They copy the `skills/auto-ship/` folder into their project's skills directory. The first sign of trouble comes before they even run the skill: a registry ingestion script flags nine schema violations because `version`, `author`, `email`, `category`, `tags`, `product`, `sprint`, `tested_with`, and `user-invocable` are all at the wrong YAML level. The `tags` field is a YAML list instead of a string, and `sprint: 4` is an unquoted integer. The `license` and `compatibility` fields are entirely missing. The registry validator marks the skill as non-compliant and may exclude it from search results.

Assuming the developer pushes past the validation warnings, they update the GraphQL query in Step 2a to use their org and repo — but the `description` doesn't mention "drain Todo" or "batch ship", so when they say "drain the backlog tonight" the agent doesn't route to this skill. When they finally invoke it by name, Steps 1–5 execute correctly and open PRs on GitHub. Then Step 6 runs `node .claude/scripts/queue-io.js` — a path that doesn't exist in their project because `queue-io.js` was never bundled. The script fails with `MODULE_NOT_FOUND`. Three PRs are now open on GitHub with no queue entries. `/auto-merge` will never see them. The Recovery table tells the developer to re-run the `queue-io.js append` command — but they still don't have the script. Recovery itself fails. The developer must manually manage those PRs outside the queue entirely.

Even on the original TMS project where `queue-io.js` does exist, a developer adapting the skill for a second project misses one of the four occurrences of `zyni-ai/tms-app` (Step 5's pre-flight query), causing every issue to fail the race check silently. The Notes section at the bottom says "swap all of these" but lists them only once and without step references.

### After (all improvements applied)

With all six improvements applied, the developer's experience changes at every stage. The frontmatter is fully spec-compliant: nine custom fields are nested under `metadata:` with quoted scalar values, `license: Proprietary — internal use only (zysk.tech)` declares usage rights, and `compatibility` lists the exact dependencies (Node.js, `gh` CLI, GitHub Projects v2, the bundled `queue-io.js`) before the developer even invokes the skill. Registry ingestion scripts parse the file cleanly with zero warnings.

The strengthened `description` now includes "drain Todo", "batch ship", "ship these issues", and "run overnight" — so the agent routes correctly when the developer uses natural language. The bundled `skills/auto-ship/scripts/queue-io.js` means Step 6 resolves the script path from within the skill folder and executes successfully regardless of whether `.claude/scripts/` exists in the target project. The "PR opened but queue entry missing" failure mode from the Recovery table is effectively eliminated.

The Configuration block at the top of the body gives the developer a four-row checklist (org, repo, project board number, queue file path) with step references. They update all four values once, using the table as a checklist, and every body occurrence is found and updated before the first run. The skill executes against the correct repo from step one, all pre-flight checks return real data, PRs are opened correctly, queue entries are written atomically, and `/auto-merge` can drain the queue when invoked. The full pipeline works on the first attempt on any project that meets the declared compatibility requirements.
