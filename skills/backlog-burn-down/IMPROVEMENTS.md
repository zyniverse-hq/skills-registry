# IMPROVEMENTS — backlog-burn-down

> Improvement plan derived from SKILL.md + ANALYSIS.md audit against the agentskills.openml.io spec.

---

## Quick Summary

| | Before | After |
|---|---|---|
| Spec compliance | Partially compliant | Fully compliant |
| Critical violations | 3 | 0 |
| Agent discoverability | Medium | High |
| Portability | Fails | Pass |

---

## Improvement 1 — Move non-standard frontmatter fields under `metadata:`

### What needs to change

Nine non-standard fields (`version`, `author`, `email`, `category`, `tags`, `product`, `sprint`, `tested_with`, `user-invocable`) are currently at the top level of the YAML frontmatter. The spec requires all non-standard fields to be nested under a `metadata:` key. These fields will be silently ignored or cause parse errors in compliant skill loaders that only expect standard top-level keys.

### Before
```yaml
---
name: backlog-burn-down
description: "Scans the Todo column of a GitHub Projects v2 board, stale-checks each issue, classifies into quick-fix / clear-scope / ambiguous tracks, bundles by mental model, and presents a batch plan for the user to pick from."
version: 1.0.0
author: Varun U
email: varun@zysk.tech
category: engineering-practice
tags:
  - project-board
  - github
  - planning
  - triage
  - workflow
product: tms
sprint: 4
tested_with: claude-opus-4-7
user-invocable: true
---
```

### After
```yaml
---
name: backlog-burn-down
description: "Use when the user asks 'what should I work on?', 'plan my day', 'burn down the backlog', or 'show me Todo'. Scans the Todo column of a GitHub Projects v2 board, stale-checks each issue, classifies into quick-fix / clear-scope / ambiguous tracks, bundles by mental model, and presents a batch plan for the user to approve before any execution."
license: MIT
compatibility: "Requires gh CLI (authenticated, Projects v2 scope), git, and a GitHub organisation with a Projects v2 board. Tested with claude-opus-4-7."
metadata:
  version: 1.0.0
  author: Varun U
  email: varun@zysk.tech
  category: engineering-practice
  tags:
    - project-board
    - github
    - planning
    - triage
    - workflow
  product: tms
  sprint: 4
  tested_with: claude-opus-4-7
  user-invocable: true
---
```

### Impact if implemented
- **Agent behaviour:** Compliant skill loaders will correctly parse all fields. Fields that were previously silently dropped (e.g., `tags`, `category`) will be visible to discovery and routing systems.
- **Discoverability:** Tag-based discovery systems can now index `project-board`, `github`, `planning`, `triage`, and `workflow` correctly.
- **Portability:** Any team running a spec-compliant skill registry can import this skill without frontmatter parse errors.
- **Risk reduced:** Prevents silent data loss where a loader accepting only standard top-level keys would discard all nine non-standard fields without warning.

### Existing use (before fix)
Today, when a skill registry loader ingests `backlog-burn-down`, it encounters nine unrecognised top-level YAML keys. Strict loaders reject the skill entirely or strip the non-standard fields silently. The `tags` list — which drives search and category filtering — is lost. A developer searching the registry for skills tagged `github` or `planning` will not find this skill even though it is highly relevant. The `tested_with: claude-opus-4-7` field, which helps agents select skills compatible with their model, is also discarded.

### Improved use (after fix)
After moving all nine fields under `metadata:`, the frontmatter passes spec validation cleanly. Registry loaders index the `tags` list, making the skill discoverable under `github`, `planning`, `triage`, and `project-board` searches. The `tested_with` value is preserved in the metadata block, giving agents a compatibility hint. The frontmatter is now forward-compatible with any agentskills.io-compliant loader.

---

## Improvement 2 — Add the required `license` field

### What needs to change

The `license` field is listed as required by the agentskills.io spec. It is completely absent from the current frontmatter. Without it, spec validators will flag the skill as non-compliant, and downstream systems that enforce licensing policies cannot determine whether this skill may be used, modified, or redistributed.

### Before
```yaml
---
name: backlog-burn-down
description: "Scans the Todo column of a GitHub Projects v2 board..."
version: 1.0.0
author: Varun U
# license field is entirely absent
---
```

### After
```yaml
---
name: backlog-burn-down
description: "..."
license: MIT
---
```

### Impact if implemented
- **Agent behaviour:** Spec validators pass without the "required field missing" error for `license`. CI pipelines that gate on spec compliance will no longer block this skill.
- **Discoverability:** License-filtered registries (e.g., "show me only open-source skills") will include this skill once `license: MIT` is set.
- **Portability:** Teams outside `zyni-ai` can immediately determine whether they are permitted to use or adapt this skill without contacting the author.
- **Risk reduced:** Prevents ambiguous ownership disputes and CI compliance failures caused by a missing required field.

### Existing use (before fix)
Any automated spec validator run against this skill today fails with a "missing required field: license" error. If the registry runs a compliance gate before indexing (common in CI/CD pipelines), this skill is never published to the shared index. Developers browsing the registry by license type cannot filter for it. The author's contact email is present, but that alone is insufficient for compliance purposes.

### Improved use (after fix)
Adding `license: MIT` satisfies the required field check. The skill passes the compliance gate, gets indexed, and is immediately visible to license-filtered searches. Teams evaluating the skill for use in their own projects have a clear, machine-readable signal that MIT terms apply — no author contact required for basic reuse decisions.

---

## Improvement 3 — Add the `compatibility` field documenting runtime prerequisites

### What needs to change

The skill requires `gh` CLI (with GitHub Projects v2 OAuth scope), `git`, and an accessible GitHub organisation with a configured Projects v2 board. None of these prerequisites are declared in the frontmatter. The `compatibility` field is the spec-designated location for this information. Without it, an agent running in an environment without `gh` CLI will invoke the skill, fail at Step 1's GraphQL call with an authentication or command-not-found error, and have no frontmatter-level signal to abort early.

### Before
```yaml
---
name: backlog-burn-down
description: "Scans the Todo column of a GitHub Projects v2 board..."
# compatibility field is entirely absent
---
```

### After
```yaml
---
name: backlog-burn-down
description: "..."
license: MIT
compatibility: "Requires gh CLI (authenticated, Projects v2 scope), git, and a GitHub organisation with a Projects v2 board. Tested with claude-opus-4-7."
---
```

### Impact if implemented
- **Agent behaviour:** Agents and orchestrators can read `compatibility` before invoking the skill and bail out early with a helpful error (e.g., "gh CLI not found — skill requires it") rather than failing mid-execution at Step 1's GraphQL call.
- **Discoverability:** Environments that pre-filter skills by available tools will correctly exclude this skill when `gh` is not installed, preventing mis-invocation.
- **Portability:** Teams evaluating whether to adopt this skill can immediately see all runtime dependencies from the frontmatter without reading the full body.
- **Risk reduced:** Prevents confusing mid-step failures (cryptic GraphQL auth errors) that surface only after the agent has already created TaskCreate items and begun execution.

### Existing use (before fix)
Today, an agent in a fresh environment (e.g., a new developer's machine, a CI container without `gh`) invokes `/backlog-burn-down`. Step 0 creates tasks. Step 1 fires the GraphQL query via `gh api graphql` and receives either a "command not found" error or a "401 Unauthorized" error if `gh` is installed but not authenticated. The agent has no frontmatter signal that `gh` is required — it must parse the error, infer the missing dependency, and surface that to the user after already mutating task state. The user experience is: tasks created, progress started, then a cryptic failure.

### Improved use (after fix)
With `compatibility` declared, an orchestrator or the agent itself checks prerequisites before Step 0. If `gh` is absent or unauthenticated, the skill is skipped with an actionable message: "backlog-burn-down requires gh CLI with Projects v2 scope." No tasks are created, no state is mutated, and the user receives clear guidance on what to install or configure before retrying.

---

## Improvement 4 — Add trigger keywords to the `description` field

### What needs to change

The `description` field currently describes what the skill does mechanically but omits the natural-language trigger phrases that agents use to match user intent. Phrases like "what should I work on?", "plan my day", "burn down the backlog", and "show me Todo" appear only in the body's "When to use" section — which agents typically do not parse for routing decisions. The description is the primary field used for skill-to-intent matching. Without trigger phrases here, agents will miss this skill for the exact user queries it was designed to serve.

### Before
```yaml
description: "Scans the Todo column of a GitHub Projects v2 board, stale-checks each issue, classifies into quick-fix / clear-scope / ambiguous tracks, bundles by mental model, and presents a batch plan for the user to pick from."
```

### After
```yaml
description: "Use when the user asks 'what should I work on?', 'plan my day', 'burn down the backlog', or 'show me Todo'. Scans the Todo column of a GitHub Projects v2 board, stale-checks each issue, classifies into quick-fix / clear-scope / ambiguous tracks, bundles by mental model, and presents a batch plan for the user to approve before any execution."
```

(346 chars — within the 1-1024 limit.)

### Impact if implemented
- **Agent behaviour:** Agents performing description-based skill matching will now trigger this skill when users say "what should I work on?", "plan my day", or "burn down the backlog" — the exact phrases the skill was designed for.
- **Discoverability:** Semantic search over the skill index will surface this skill for planning-intent queries that currently return zero results.
- **Portability:** Teams onboarding the skill to a new registry immediately see its intended trigger context without reading the body.
- **Risk reduced:** Prevents the skill being overlooked in favour of less appropriate skills (e.g., `/auto-ship`) when the user's intent is deliberate review rather than autonomous execution.

### Existing use (before fix)
A user says "what should I work on today?". The agent searches the skill registry by semantic similarity against all `description` fields. The current description — "Scans the Todo column of a GitHub Projects v2 board..." — scores low against a planning-intent query because it describes the mechanism, not the trigger scenario. The agent may instead select `/auto-ship` (which has "ship" connotations) or fail to match any skill, leaving the user without the deliberate review gate this skill provides. The trigger phrases live in the body but are not reachable during description-level routing.

### Improved use (after fix)
After prepending the trigger phrases, an agent matching "what should I work on?" against skill descriptions scores `backlog-burn-down` highly and invokes it correctly. The user gets the batch plan and deliberate review gate. The competing risk — the agent silently routing to `/auto-ship` and draining the board without user confirmation — is eliminated by correct skill selection.

---

## Improvement 5 — Add a bolded "Adapt before use" callout above the hardcoded GraphQL block in Step 1

### What needs to change

The GraphQL query in Step 1 hardcodes `organization(login: "zyni-ai")` and `projectV2(number: 18)`. The stale-close command in Step 2 hardcodes `--repo zyni-ai/tms-app`. The Notes section at the end of the body mentions swapping these values, but the note appears 200 lines after the code block. Developers copy-pasting the query from Step 1 will use `zyni-ai` and project `18` verbatim, silently querying the wrong board or receiving a "not found" error with no indication of why.

### Before
```markdown
### Step 1 — Fetch unassigned Todo items

Paginate with `after: <endCursor>` until `hasNextPage: false`. The board has 200+ items; `first: 100` silently misses the rest.

```bash
gh api graphql -f query='
query($cursor: String) {
  organization(login: "zyni-ai") {
    projectV2(number: 18) {
```
```

### After
```markdown
### Step 1 — Fetch unassigned Todo items

Paginate with `after: <endCursor>` until `hasNextPage: false`. The board has 200+ items; `first: 100` silently misses the rest.

> **Adapt before use:** Replace `"zyni-ai"` with your GitHub organisation login and `18` with your Projects v2 board number. The stale-close command in Step 2 also targets `zyni-ai/tms-app` — update that repo slug to match your repository.

```bash
gh api graphql -f query='
query($cursor: String) {
  organization(login: "zyni-ai") {   # <-- replace with your org login
    projectV2(number: 18) {          # <-- replace with your board number
```
```

### Impact if implemented
- **Agent behaviour:** Agents generating or adapting the query at invocation time will see the callout immediately and substitute the correct values rather than using `zyni-ai` verbatim.
- **Discoverability:** No effect on discoverability, but reduces first-use friction significantly.
- **Portability:** The skill becomes usable by any team without reading the Notes section at the bottom of the file.
- **Risk reduced:** Prevents the silent failure mode where `gh api graphql` returns a "Could not resolve to a ProjectV2" error (or queries the wrong org's board) because the hardcoded org/project values were never changed.

### Existing use (before fix)
A developer at a new org runs `/backlog-burn-down` after copying the skill. The GraphQL call fires against `zyni-ai`'s project board. The `gh` CLI either lacks access (resulting in a 403 error) or silently returns `null` for the organisation node. The developer sees no issues, concludes the board is empty, and misses their entire Todo queue. The Notes section explaining the swap is 200+ lines away and easily missed during setup.

### Improved use (after fix)
The bolded callout appears immediately before the code block. The developer (or agent) sees it before copy-pasting, substitutes `zyni-ai` with their org and `18` with their board number, and the query returns the correct results on the first run. The inline `# <-- replace` comments in the code block reinforce which two values need changing without requiring the reader to cross-reference the Notes section.

---

## Priority Order

| Priority | Improvement | Effort | Impact |
|---|---|---|---|
| 1 | Move non-standard fields under `metadata:` | Low | Critical — spec compliance, tag indexing |
| 2 | Add required `license` field | Low | Critical — spec compliance, CI gate |
| 3 | Add trigger keywords to `description` | Low | High — agent routing, correct skill selection |
| 4 | Add `compatibility` field | Low | High — early failure prevention, portability |
| 5 | Add "Adapt before use" callout in Step 1 | Low | Medium — portability, silent misconfiguration |

---

## Before vs After: Full Skill Experience

### Before (current state)

A developer at a new organisation discovers `backlog-burn-down` in a shared skills registry and tries to use it. The first barrier is invisible: the skill fails spec validation because `license` is missing and nine top-level frontmatter fields are non-standard. If the registry runs a compliance gate, the skill is never published and the developer never sees it. If the gate is lenient, the skill is indexed but its `tags` list is silently dropped — meaning searches for `github`, `planning`, or `triage` return no results for this skill, even though it is the most relevant skill for those queries.

If the developer does find the skill and invokes it with "what should I work on today?", the agent may not match it correctly. The `description` field describes the mechanism ("Scans the Todo column...") rather than the trigger intent, so the semantic router scores it below other skills for planning-intent queries. The agent might invoke `/auto-ship` instead — draining the board autonomously without the deliberate review gate the user wanted. If the agent does invoke the right skill, it proceeds to Step 1 and fires the GraphQL query against `zyni-ai`'s project board (org and project number are hardcoded). In a fresh environment without `gh` CLI, the step fails with a cryptic "command not found" error after TaskCreate has already run. In an environment with `gh` but without `zyni-ai` access, the query silently returns null and the developer concludes their board is empty.

### After (all improvements applied)

With all five improvements applied, the skill passes spec validation cleanly: `license: MIT` satisfies the required field, nine non-standard fields are correctly nested under `metadata:`, and `compatibility` documents the `gh` CLI and GitHub Projects v2 prerequisites. The CI compliance gate publishes the skill to the shared index, and tag-based searches for `github`, `planning`, `triage`, `project-board`, and `workflow` all surface it correctly.

When a user says "what should I work on today?" or "let's plan the backlog", the agent matches the skill accurately because the description now opens with "Use when the user asks 'what should I work on?', 'plan my day', 'burn down the backlog'..." — the exact phrasing the user is likely to use. The correct skill is selected and the deliberate review gate is preserved. Before Step 0 runs, the orchestrator checks `compatibility`, sees that `gh` CLI with Projects v2 scope is required, and either confirms it is present or aborts with a clear "install gh CLI" message — no cryptic mid-step failures, no wasted TaskCreate mutations.

When the skill is adopted by a new team, the bolded "Adapt before use" callout immediately above the Step 1 GraphQL block and the inline `# <-- replace` comments guide the developer to substitute `zyni-ai` and `18` with their own org and board number before the first run. The portability barrier that previously required reading to the Notes section at the bottom of the file is eliminated. The end result is a skill that is fully spec-compliant, correctly discoverable, and immediately runnable by any team with a GitHub Projects v2 board and the `gh` CLI.
