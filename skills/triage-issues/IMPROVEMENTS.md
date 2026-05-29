# IMPROVEMENTS — triage-issues

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

## Improvement 1 — Wrap Non-Standard Frontmatter Fields Under `metadata:`

### What needs to change
Nine non-standard fields (`version`, `author`, `email`, `category`, `tags`, `product`, `sprint`, `tested_with`, `user-invocable`) are placed at the top level of the frontmatter. The spec requires all non-standard fields to be nested under a `metadata:` key. This breaks spec compliance and may cause registry tooling to misparse or reject the skill.

### Before
```yaml
---
name: triage-issues
description: "Promotes Backlog issues to Todo on a GitHub Projects v2 board — derives Priority/Area/Module from labels + title heuristics, flags missing labels and suspected duplicates, requires user approval before mutations."
version: 1.0.0
author: Varun U
email: varun@zysk.tech
category: engineering-practice
tags:
  - project-board
  - github
  - triage
  - graphql
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
name: triage-issues
description: "Triage GitHub Projects v2 Backlog: promotes issues to Todo, derives Priority/Area/Module from labels and title heuristics, flags missing labels and suspected duplicates, requires user approval before any mutations. Use for weekly triage cadence or pre-sprint board hygiene."
license: MIT
compatibility: "Requires gh CLI (v2.20+) authenticated with a token scoped to read:org, project, write:org. GitHub Projects v2 only. Requires a CLAUDE.md in the repo root with a 'Project Board Operations' section containing field/option IDs. Target org login and project number must be updated for non-TMS deployments."
metadata:
  version: 1.0.0
  author: Varun U
  email: varun@zysk.tech
  category: engineering-practice
  tags:
    - project-board
    - github
    - triage
    - graphql
    - workflow
  product: tms
  sprint: 4
  tested_with: claude-opus-4-7
  user-invocable: true
---
```

### Impact if implemented
- **Agent behaviour:** Registry tooling can correctly parse and index the skill without tripping on unexpected top-level keys.
- **Discoverability:** Cleaner frontmatter means tag-based and category-based discovery works as intended; the `tags` array under `metadata` is still surfaced by registry indexers that understand the spec structure.
- **Portability:** Other teams adapting the skill see a standard frontmatter shape they recognise, lowering onboarding friction.
- **Risk reduced:** Prevents silent parse failures in any tooling that validates strict top-level frontmatter shape.

### Existing use (before fix)
Today, when the skills registry indexes `triage-issues`, it encounters nine unexpected top-level keys alongside `name` and `description`. Depending on the registry parser's strictness, this either silently ignores the extra keys or raises a validation warning. Fields like `tags`, `category`, and `user-invocable` that agents or discovery tools rely on for routing are in the wrong place and may not be read at all. Anyone comparing this skill's frontmatter against the spec immediately sees a structural mismatch, and the `license` and `compatibility` fields are entirely absent.

### Improved use (after fix)
After the fix, the frontmatter is fully spec-compliant. All non-standard fields sit under `metadata:`, `license` and `compatibility` are present at the correct top level, and the `description` includes trigger keywords. Registry tooling parses without warnings, tag-based routing works, and any developer or agent reading the frontmatter can immediately understand the skill's prerequisites and intended invocation context.

---

## Improvement 2 — Add Missing `license` and `compatibility` Fields

### What needs to change
Both `license` and `compatibility` are required fields per the spec and are entirely absent from the current frontmatter. The `compatibility` field is especially important here because `triage-issues` requires a specific `gh` CLI version, non-trivial GitHub token scopes (`read:org`, `project`, `write:org`), Projects v2 (not v1), and a pre-configured `CLAUDE.md` with board field IDs. Without documenting this, agents that invoke the skill in an under-provisioned environment will fail partway through Step 7 mutations with opaque GraphQL errors.

### Before
```yaml
# license and compatibility fields are entirely absent from the frontmatter
name: triage-issues
description: "Promotes Backlog issues to Todo on a GitHub Projects v2 board ..."
version: 1.0.0
author: Varun U
```

### After
```yaml
name: triage-issues
description: "Triage GitHub Projects v2 Backlog: promotes issues to Todo, derives Priority/Area/Module from labels and title heuristics, flags missing labels and suspected duplicates, requires user approval before any mutations. Use for weekly triage cadence or pre-sprint board hygiene."
license: MIT
compatibility: "Requires gh CLI (v2.20+) authenticated with a token scoped to read:org, project, write:org. GitHub Projects v2 only. Requires a CLAUDE.md in the repo root with a 'Project Board Operations' section containing field/option IDs. Target org login (currently 'zyni-ai') and project number (currently 18) must be updated for non-TMS deployments."
```

### Impact if implemented
- **Agent behaviour:** Agents and human operators can check prerequisites before invoking the skill, avoiding mid-run failures. A pre-flight check against `compatibility` can be added to Step 0 or Step 1.
- **Discoverability:** The `license` field satisfies the registry's required-field check, preventing the skill from being excluded from public or shared indexes.
- **Portability:** The `compatibility` note explicitly calls out what must be swapped for non-TMS use (org login, project number, CLAUDE.md structure), turning a vague advisory into a concrete migration checklist.
- **Risk reduced:** Prevents users from invoking the skill with an under-scoped token and only discovering the missing scope at Step 7 when the `updateProjectV2ItemFieldValue` mutation returns a permission error after all the read work is done.

### Existing use (before fix)
Today, a developer setting up `triage-issues` in a new environment has no frontmatter signal about what the skill needs to run. They will likely discover missing token scopes only when the Step 7 mutations fail with `"Resource not accessible by integration"` or similar. The `license` field being absent also means the skill cannot be published to any registry that enforces required fields, silently blocking distribution.

### Improved use (after fix)
After the fix, the `compatibility` field gives any operator a one-paragraph checklist: install `gh` CLI v2.20+, authenticate with the right scopes, ensure a `CLAUDE.md` with the correct section is present, and update the org/project number. The `license: MIT` field satisfies registry validation. A future Step 0 pre-flight can reference the `compatibility` string to auto-check `gh auth status` and `gh auth token` scopes before doing any GraphQL work.

---

## Improvement 3 — Add Trigger Keywords to `description`

### What needs to change
The `description` field is descriptive but lacks the explicit trigger phrases that agents use for skill matching. Terms like "triage", "backlog", "weekly triage", "project board hygiene", and "GitHub Projects" are common ways users and orchestration agents would invoke this skill — but none of them appear literally in the `description`. The current description reads like internal documentation rather than a matchable surface for agent routing.

### Before
```yaml
description: "Promotes Backlog issues to Todo on a GitHub Projects v2 board — derives Priority/Area/Module from labels + title heuristics, flags missing labels and suspected duplicates, requires user approval before mutations."
```

### After
```yaml
description: "Triage GitHub Projects v2 Backlog: promotes issues to Todo, derives Priority/Area/Module from labels and title heuristics, flags missing labels and suspected duplicates, requires user approval before any mutations. Use for weekly triage cadence, pre-sprint board hygiene, or after a batch of new issues lands."
```

### Impact if implemented
- **Agent behaviour:** Agent routers that match on `description` now correctly resolve phrases like "triage the backlog", "do weekly triage", "clean up the board", or "run pre-sprint triage" to this skill.
- **Discoverability:** Keyword matches on "triage", "backlog", "weekly triage", "board hygiene", and "pre-sprint" are all present. The description is now both human-readable and machine-matchable.
- **Portability:** The improved description is still generic enough that non-TMS teams can read it and understand the skill's purpose without knowing what "project #18" means.
- **Risk reduced:** Reduces the chance of agents falling back to a generic task-runner when the user says "triage the backlog", which could skip the approval gate and run mutations without the structured Step 6 display.

### Existing use (before fix)
Today, if an agent receives the instruction "run the weekly triage on the backlog", it may not match `triage-issues` because the description uses "Promotes Backlog issues to Todo" rather than "triage" as a verb. The agent might route to a more generic skill or ask the user to clarify, adding unnecessary friction to a workflow that should be a single invocation.

### Improved use (after fix)
After the fix, "triage", "weekly triage", "backlog", "board hygiene", and "pre-sprint" all appear in the `description`. Agent routing confidently matches the skill on natural phrasing like "triage the backlog before sprint planning" or "clean up the project board". The improved description also makes the approval gate explicit ("requires user approval") so agents and users know upfront that this is an interactive workflow, not a silent automation.

---

## Improvement 4 — Resolve Contradiction Between Red Flags and Step 7 Hardcoded IDs

### What needs to change
The skill's own Red flags section states: "Hardcoding field/option IDs from this skill instead of referencing CLAUDE.md → IDs live in CLAUDE.md as the single source of truth. Drift here breaks every board-touching skill." Yet Step 7 embeds the exact IDs (`PVT_kwDOCrP2y84BUSTb`, `PVTSSF_lADOCrP2y84BUSTbzhBbiuk`, `PVTSSF_lADOCrP2y84BUSTbzhBbiuo`, `PVTSSF_lADOCrP2y84BUSTbzhBcsv0`, `PVTSSF_lADOCrP2y84BUSTbzhBbik0`, `c2b8c846`) directly in the mutation code blocks. This is the exact violation the Red flags section warns against. Additionally, the Step 2 Priority table duplicates the option ID table that supposedly lives only in CLAUDE.md.

### Before
```bash
# Step 7, mutation 1 — hardcoded IDs embedded directly:
gh api graphql -f query='
mutation {
  updateProjectV2ItemFieldValue(input: {
    projectId: "PVT_kwDOCrP2y84BUSTb"
    itemId: "<projectItemId>"
    fieldId: "PVTSSF_lADOCrP2y84BUSTbzhBbiuk"
    value: { singleSelectOptionId: "<priorityOptionId>" }
  }) { projectV2Item { id } }
}'
```

And in Step 2:
```markdown
| `priority: critical` | P0 (Critical) | `550bedbb` |
| `priority: high`     | P1 (High)     | `b2eca0ce` |
| `priority: medium`   | P2 (Medium)   | `f05645b9` |
| `priority: low`      | P3 (Low)      | `d2302afe` |
```

### After
```bash
# Step 7, mutation 1 — read IDs from CLAUDE.md "Project Board Operations":
# projectId, fieldId, and optionIds must be sourced from CLAUDE.md.
# The blocks below are illustrative; substitute values from CLAUDE.md at runtime.
gh api graphql -f query='
mutation {
  updateProjectV2ItemFieldValue(input: {
    projectId: "<projectId-from-CLAUDE.md>"
    itemId: "<projectItemId>"
    fieldId: "<priority-fieldId-from-CLAUDE.md>"
    value: { singleSelectOptionId: "<priorityOptionId-from-CLAUDE.md>" }
  }) { projectV2Item { id } }
}'
```

And in Step 2, replace the Priority table with:
```markdown
#### Priority (required)

From the `priority:` label. See CLAUDE.md "Project Board Operations → Priority" for the full label-to-option-ID mapping table. Do not duplicate the table here — it is the single source of truth.
```

### Impact if implemented
- **Agent behaviour:** Agents reading Step 7 are directed to CLAUDE.md for IDs rather than using the (potentially stale) values embedded in the skill body. If IDs change after a board migration, only CLAUDE.md needs updating — the skill stays correct.
- **Discoverability:** No change to discoverability, but the skill becomes a reliable reference rather than a source of drift.
- **Portability:** Non-TMS teams adapting the skill no longer need to hunt down every hardcoded ID in code blocks — the placeholder pattern makes it obvious where substitutions are needed.
- **Risk reduced:** Eliminates the contradiction that undermines trust in the skill's own Red flags guidance. Prevents silent promotion to Todo with wrong field values after a board schema migration.

### Existing use (before fix)
Today, the Step 7 code blocks contain the actual TMS project and field IDs. If the project board is migrated or a field is recreated (which resets the option IDs), any agent following these code blocks verbatim will send mutations with stale IDs. The GraphQL API will return errors, but the error messages for invalid option IDs are not always clear. Meanwhile, the Red flags section warns against exactly this pattern — creating a confusing contradiction that erodes trust in the skill's guidance.

### Improved use (after fix)
After the fix, Step 7 code blocks use placeholder tokens like `<projectId-from-CLAUDE.md>` and direct the agent to fetch values from CLAUDE.md at runtime. The Step 2 Priority table is removed from the skill body with a pointer to CLAUDE.md. The contradiction with the Red flags section is resolved. When IDs change, only CLAUDE.md needs updating, and all board-touching skills (`triage-issues`, `backlog-burn-down`, `ship-issue`) remain consistent without requiring coordinated edits across multiple skill files.

---

## Improvement 5 — Add CLAUDE.md Pre-Flight Check to Step 0 or Step 1

### What needs to change
The skill depends entirely on an external `CLAUDE.md` file containing "Project Board Operations → Field IDs" for all GraphQL mutations. This dependency is mentioned in the body but never validated at runtime. If `CLAUDE.md` is absent or missing the required section, the skill proceeds through Steps 1-6 (potentially minutes of GraphQL pagination) before failing silently at Step 7 with missing IDs. A pre-flight check in Step 0 or Step 1 would catch this immediately and surface a clear error.

### Before
```markdown
### Step 1 — Fetch Backlog items + their current field values

Paginate with `after: <endCursor>` until `hasNextPage: false`, accumulating nodes across pages.
```
(No check for CLAUDE.md presence or "Project Board Operations" section before starting.)

### After
```markdown
### Step 1 — Pre-flight checks + Fetch Backlog items

**Before making any GraphQL calls**, verify:

1. `CLAUDE.md` exists in the repo root.
2. `CLAUDE.md` contains a "Project Board Operations" section with "Field IDs" subsection.
3. `gh auth status` shows an authenticated session with `read:org` and `project` scopes.

If any check fails, exit immediately with a clear message, e.g.:
```
Pre-flight failed: CLAUDE.md missing "Project Board Operations → Field IDs" section.
Add the section with projectId, fieldId values before invoking /triage-issues.
```

If all checks pass, proceed to paginate Backlog items...
```

### Impact if implemented
- **Agent behaviour:** The agent exits with a useful error message at Step 1 rather than failing silently mid-mutation at Step 7. The user gets actionable guidance ("add the section to CLAUDE.md") instead of a raw GraphQL error.
- **Discoverability:** No change, but the skill gains a reputation as a reliable tool that fails fast and clearly rather than wasting time on a doomed run.
- **Portability:** Adapters setting up the skill in a new environment get immediate feedback if their CLAUDE.md is incomplete, rather than discovering the gap during a live triage session.
- **Risk reduced:** Prevents partial triage runs where some items are promoted to Todo with incomplete field values because Step 7 ran out of IDs partway through.

### Existing use (before fix)
Today, if `CLAUDE.md` is absent or the "Project Board Operations" section is missing, the skill runs Steps 1-6 successfully (pagination, derivation, duplicate detection, triage table display), waits for user approval, then fails at the first Step 7 mutation with a confusing error. The user has invested time reviewing the triage table and approving promotions, only to find the mutations fail. There is no recovery path short of fixing CLAUDE.md and re-running the entire skill from Step 1.

### Improved use (after fix)
After the fix, Step 1 runs a three-point pre-flight before any GraphQL calls. If CLAUDE.md is missing or incomplete, the skill exits in under two seconds with a message pointing directly at what needs to be added. The user fixes the prerequisite once and re-runs. No wasted pagination, no misleading triage tables shown for items that cannot be promoted, no approval prompt for a run that is guaranteed to fail.

---

## Priority Order

| Priority | Improvement | Effort | Impact |
|---|---|---|---|
| 1 | Wrap non-standard frontmatter fields under `metadata:` + add `license` + `compatibility` | Low | Critical |
| 2 | Add trigger keywords to `description` | Low | High |
| 3 | Resolve Red flags vs Step 7 hardcoded IDs contradiction | Medium | High |
| 4 | Add CLAUDE.md pre-flight check to Step 1 | Low | Medium |
| 5 | Remove Step 2 Priority table duplication (pointer to CLAUDE.md only) | Low | Medium |

---

## Before vs After: Full Skill Experience

### Before (current state)

A developer discovers `triage-issues` in the registry and reads the frontmatter. Nine fields sit at the top level with no `metadata:` wrapper, and both `license` and `compatibility` are absent. The registry validator flags three required-field violations and the non-standard structure warning. The `description` says "Promotes Backlog issues to Todo" — technically accurate but missing words like "triage" or "backlog hygiene" that would let an agent route to this skill on natural phrasing. An agent receiving "run the weekly triage" may not match this skill at all.

When the developer does invoke the skill, there is no pre-flight check. If their `CLAUDE.md` is missing the "Project Board Operations" section — common in a fresh clone or non-TMS adaptation — the skill happily paginates all 400+ project items, runs duplicate detection, builds the triage table, waits for approval, and then fails at the first Step 7 mutation with a GraphQL permission or "field not found" error. Meanwhile, Step 7's code blocks embed the actual TMS field IDs (`PVT_kwDOCrP2y84BUSTb`, `PVTSSF_lADOCrP2y84BUSTbzhBbiuk`, etc.) — the exact pattern the skill's own Red flags section warns against. A non-TMS adapter must manually hunt down every hardcoded ID in the code blocks, with no placeholder pattern to guide substitution.

The Step 2 Priority table duplicates the label-to-option-ID mapping that supposedly lives only in CLAUDE.md, creating a second source of truth. If option IDs change after a board migration, both CLAUDE.md and the skill body need updating, and the two can silently drift apart. The Red flags section warns against this duplication but the body itself commits the violation.

### After (all improvements applied)

After all improvements, the frontmatter is fully spec-compliant: `license: MIT` and `compatibility` are present at the top level, all nine non-standard fields are nested under `metadata:`, and the `description` leads with "Triage GitHub Projects v2 Backlog" and includes "weekly triage cadence", "pre-sprint board hygiene", and "after a batch of new issues lands" — phrases that agent routers match confidently on natural user input.

When the skill is invoked, Step 1 runs a three-point pre-flight (CLAUDE.md presence, "Project Board Operations" section, `gh auth` scopes) before any GraphQL calls. A missing CLAUDE.md surfaces as a one-line actionable error in under two seconds, not as a cryptic mutation failure after ten minutes of pagination. Step 7's code blocks use placeholders (`<projectId-from-CLAUDE.md>`, `<priority-fieldId-from-CLAUDE.md>`) that make the CLAUDE.md dependency explicit and tell non-TMS adapters exactly where to substitute. The Step 2 Priority table is removed from the skill body with a pointer to CLAUDE.md, eliminating the drift risk and resolving the Red flags contradiction.

The overall skill experience is tighter and more trustworthy: fail fast on missing prerequisites, single source of truth for all IDs, no internal contradictions, and a description that routes correctly from natural language. Teams adapting the skill for their own org find a clear migration checklist in the `compatibility` field and placeholder patterns throughout the mutation blocks, rather than a wall of TMS-specific hex IDs to hunt and replace.
