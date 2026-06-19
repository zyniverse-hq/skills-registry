---
name: triage-issues
description: "Promotes Backlog issues to Todo on a GitHub Projects v2 board — derives Priority/Area/Module from labels + title heuristics, flags missing labels and suspected duplicates, requires user approval before mutations. To assign Todo issues to developers for a sprint, use backlog-burn-down."
metadata:
  version: 2.0.0
  author: Varun U
  email: varun@zysk.tech
  category: engineering-practice
  tags:
    - project-board
    - github
    - triage
    - graphql
    - workflow
  tested_with: claude-opus-4-7
  user-invocable: true
---

# Triage Issues

> Board hygiene for any GitHub Projects v2 board. Auto-add commonly drops new issues at `Status = Backlog` with no fields set. This skill walks the Backlog, fills in Priority/Area/Module from the issue's labels and title, flags items that can't be triaged automatically (missing required labels, no module signal, suspected duplicates), and on your approval promotes well-labelled items to `Todo`.

## When to use

- Weekly triage cadence to drain the Backlog
- After a batch of new issues lands (e.g., post `/auto-ship` if you opened parent issues)
- Before sprint planning, to make sure board fields reflect reality

### When NOT to use

- To work on a Todo issue — that's `/backlog-burn-down` or `/ship-issue`
- To enforce template completeness — that's `/gsd-inbox` (different concern)
- To handle stale issues — the `status: stale` label automation auto-applies at 60+ days and auto-closes after another 14. This skill only **reports** stale candidates.

## Prerequisites

- `gh` CLI authenticated with access to the org and its Projects v2 board (`gh auth status`).
- Run from inside a git repo whose remote points at the target org (org/repo and project are resolved automatically — see Step 1). Outside a git repo, pass `--org`/`--project` to the fetch script.
- The target board should have single-select fields named **Priority**, **Area**, **Module**, and **Status** for full triage. The skill resolves field ids and option ids dynamically by name (Step 1's `field_meta`) — nothing is hardcoded. **If an expected field or option name is absent from `field_meta`, skip that mutation and flag it for the user** (graceful degradation) rather than failing the run. At minimum, `Status` with a `Todo` option must exist to promote anything.
- Option names used in this skill (e.g. `P0 (Critical)`, `Todo`) are illustrative conventions. The mutation step resolves whatever option names the board actually defines — adapt the label→option-name maps in Step 2 to match your board's option names.

## Steps

### Step 0 — Create tasks

**MANDATORY.** TaskCreate one todo per remaining step (1–8). Mark `in_progress`/`completed`. Anti-skip discipline.

### Step 1 — Fetch Backlog items + project field metadata

Run the bundled collector. Resolve its absolute path from the skill's own directory so it works regardless of which repo the user invokes the skill from:

```bash
SKILL_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
python3 "$SKILL_DIR/scripts/fetch_triage.py" --pretty
```

The script:
- Auto-detects org and repo from the current git remote
- Lists available projects and auto-selects if there is only one, otherwise prompts (pass `--project N` to pick)
- Paginates until all items are fetched. **GitHub caps `first:` at 100** and active boards commonly carry 400+ items across all statuses, so the loop is mandatory — one page would miss most of the Backlog
- Filters to: Status = `Backlog`, state = `OPEN`

If the script exits with a non-zero code, print the last line of stderr and ask the user whether to enter issues manually or pass `--org`/`--project` explicitly.

The output JSON includes:
- `org`, `repo`, `project_number`, `project_id`, `my_login`
- `field_meta` — every single-select field on the board, keyed by name:
  `{ "<Field Name>": { "field_id": "...", "options": { "<Option Name>": "<id>" } } }`.
  This is the **single source of truth for ids** in Step 7 — resolve `project_id`, every `field_id`, and every option id from here BY NAME. Never hardcode an id.
- `backlog_issues[]` — each carries `item_id`, `number`, `title`, `body`, `url`, `state`, `labels`, `assignees`, `status`.

Keep `field_meta` and `project_id` in context through Step 7's mutations.

If `backlog_issues` is empty, exit cleanly: "Backlog is empty — nothing to triage."

This mirrors the collector pattern in `/backlog-burn-down` Step 1 — same auto-detection, same pagination contract, same failure handling.

### Step 2 — Derive intended field values

For each Backlog item, build a derivation table from the issue's labels and title.

Derive the intended **option name** for each field, then resolve the option id from `field_meta["<Field>"].options["<Option Name>"]` at mutation time (Step 7). Map labels → option names semantically; do not embed ids here.

#### Priority (required)

From the `priority:` label. Map the label to the board's Priority option name:

| Label | Priority option name |
|---|---|
| `priority: critical` | P0 (Critical) |
| `priority: high` | P1 (High) |
| `priority: medium` | P2 (Medium) |
| `priority: low` | P3 (Low) |

These option names are a common convention; if the board's `field_meta["Priority"].options` uses different names (e.g. just `Critical`/`High`/`Medium`/`Low`), match against those instead. Resolve the chosen name against `field_meta["Priority"].options` to get the id. If the name isn't found, flag it and skip the Priority mutation for that item.

If no `priority:` label is present, mark the item `needs-labels` and skip promotion.

#### Severity (skip — user sets manually)

Severity is the bug's impact magnitude (data loss, blocks login, crash for 5% of users) — orthogonal to Priority (when we schedule it). It is **not** derivable from labels: a bug can be Severity High + Priority Low (workaround exists) or Severity Low + Priority Critical (cosmetic but blocks a launch). A heuristic that just copies Priority into Severity adds no information and writes confidently-wrong values.

Leave Severity unset. The user fills it in when reviewing the bug, where they can read the body and judge impact.

#### Area (optional)

From the `area:` label, mapped 1:1 to the board's Area option of the same name (resolve via `field_meta["Area"].options`). If multiple `area:` labels exist (rare), pick the first; flag in the report. If the board has no `Area` field or the option name isn't found, skip the Area mutation and note it.

#### Module (heuristic — see table below)

The repo has no `module:` label, so this comes from the issue title's conventional-commit scope or body content. **Evaluate the table top-down, first match wins.** If no row matches cleanly, **leave Module unset** rather than guess — a wrong Module routes sprint planning incorrectly, while unset is recoverable manually.

The peer-modality / peer-capability features (proctoring, voice-runner, adaptive-test) are intentionally **not** mapped — they're shared infrastructure used across multiple runners, so the same scope can legitimately mean different Modules depending on the bug's context. The user picks the Module manually for those.

| Title scope or body keyword | Module |
|---|---|
| `(referral)`, "invite user", "referral" | Invite Users |
| `(certifications)`, "certification" | Certifications |
| `(challenges)`, "challenge" | Challenges |
| `(practice-zone)`, "practice zone" | Practice Zone |
| `(preparatory)`, "preparatory assessment" | Preparatory Assessment |
| `(interview/practice)`, `(interviews)`, `(interview)`, "mock interview", "voice interview" | Interviews |
| `(exam)`, `(competitive)`, "GATE", "CAT", "NEET", "KCET", "COMEDK", "UPSC", "JEE" | Competitive Exams |
| `(skills)` AND body mentions "skill assessment" | Skill Assessment |
| `(auth)`, `(otp)`, `(session)`, "login", "sign in" | Core |
| `(observability)`, `(sentry)`, "telemetry", "logging" | Internals |
| `(types)` AND no other module signal | Internals |
| `(mentor)`, `(shared)`, "common helper" | Common |
| `(proctoring)`, `(voice-runner)`, `(adaptive-test)` | **leave unset** — peer features, ambiguous |
| Any other scope or no scope | **leave unset** |

The "leave unset" rows are deliberate: not setting Module is better than setting the wrong one, and these features are routinely used across multiple runners.

The Module heuristic table above is taxonomy-specific (it reflects one product's modules). Adapt the rows to your board's Module options. When a row matches, resolve the Module **name** against `field_meta["Module"].options` to get the id at mutation time; if the board has no `Module` field or the option name isn't found, skip the Module mutation and note it.

#### Environment (skip)

Default `Environment` to unset. It's a runtime field (Dev/QA/Prod) used to mark *where bugs were observed*, which can't be derived from labels. The user sets it manually if relevant.

#### Status target

- All required fields derivable (`priority:` label present) → target `Todo`
- Any required field missing → leave at `Backlog`, flag `needs-labels`

### Step 3 — Detect items missing required labels

Required: at least one `type:*` AND at least one `priority:*`. Optional but warn-on-missing: `area:*`.

For each Backlog item:

| Issue | Has `type:*`? | Has `priority:*`? | Has `area:*`? | Verdict |
|---|---|---|---|---|
| ✓ | ✓ | ✓ | OK to promote |
| ✓ | ✓ | ✗ | OK to promote, recommend area label |
| ✗ or ✗ | — | — | `needs-labels` — defer |

`needs-labels` items don't get promoted this run. They show up in the report so the user can label them and re-invoke.

### Step 4 — Detect suspected duplicates

For each Backlog item, compare its title against every *other* open issue on the project (Backlog + Todo + In Progress). Use a simple Jaccard-similarity heuristic on title tokens:

```
tokens(t) = lowercase(t) split on whitespace, filter to words ≥ 3 chars,
            strip conventional-commit scope `(...)`, strip leading `fix:`/`feat:`/etc.

similarity(a, b) = |tokens(a) ∩ tokens(b)| / |tokens(a) ∪ tokens(b)|

flag pairs where:
  similarity ≥ 0.75
  AND min(|tokens(a)|, |tokens(b)|) ≥ 5    # require enough signal
  AND at least one shared label
```

The `min ≥ 5` guard avoids over-flagging short bug titles, where the post-strip token set shrinks to 4 words and any 3-word overlap trips the ratio. Even with this guard, expect noisy pairs — the user adjudicates anyway.

Surface suspected duplicate pairs in the report. Do **not** auto-close — duplicate decisions are user calls.

### Step 5 — Stale report (read-only)

Count and list items currently carrying the `status: stale` label. Do not modify them. Just surface:

```
Stale items (auto-close pending):
  #N  | last update <date>  | <title>
```

The repo has automation that auto-applies the label at 60 days inactivity and auto-closes after another 14 days. This skill defers entirely.

### Step 6 — Print triage table and STOP

Show four sections in this order. **🛑 Wait for user approval before any writes.**

```
TRIAGE TABLE — project #<project_number> — <date>
=====================================
Backlog items scanned:    <N>
To be promoted to Todo:   <N>
Need labels (defer):      <N>
Suspected duplicates:     <N pairs>
Stale (FYI only):         <N>

PROMOTING TO TODO
-----------------
#  | type        | priority | area     | module     | title
#42| bug         | high     | security | (unset)    | fix(proctoring): camera shutter not detected
#38| tech-debt   | low      | dx       | Internals  | refactor: extract toError() helper
...

NEEDS LABELS (deferred)
-----------------------
#  | missing       | title
#80| priority:*    | Voice Interview – Video Upload Failure
#75| type:*        | (no labels at all) Investigate flaky test on dev
...

SUSPECTED DUPLICATES (review)
-----------------------------
#42 ↔ #65   sim=0.82   bug,security   "fix(proctoring): camera shutter not detected"
                                       "fix(proctoring): camera detection failure on shutter close"

STALE (FYI — auto-closing per repo automation)
----------------------------------------------
#101 | last activity 67 days ago | Old discussion about adaptive feedback
```

🛑 **Wait for user approval.** Acceptable responses:
- "yes" / "go" / "proceed" → execute Step 7 for all "PROMOTING TO TODO" items
- "skip #N" or "promote only #X, #Y" → execute Step 7 for the named subset
- "no" / "cancel" → exit without writes

### Step 7 — Execute mutations

**All ids come from Step 1's output — never hardcode them.** For each mutation, resolve:

- `projectId` ← `project_id` from the script output
- field id ← `field_meta["<Field>"].field_id`
- option id ← `field_meta["<Field>"].options["<Option Name>"]` (the option name you derived in Step 2)
- `itemId` ← the issue's `item_id`

**Graceful degradation:** before each field mutation, check that the field name exists in `field_meta` and the target option name exists in its `options` map. If either is missing, **skip that mutation and record it as a flag** (report it in Step 8) — do not abort the whole run. The `Status` → `Todo` promotion (step 4 below) is the one mutation that gates promotion: if `field_meta["Status"]` or its `Todo` option is absent, the item cannot be promoted — leave it at `Backlog` and flag it.

Run mutations sequentially per item (parallel risks GraphQL rate limits and makes failure attribution harder). Substitute the resolved values into each call (shown here as shell vars `$PROJECT_ID`, `$ITEM_ID`, `$PRIORITY_FIELD_ID`, etc.):

```bash
# 1. Set Priority field
#    PRIORITY_FIELD_ID  = field_meta["Priority"].field_id
#    PRIORITY_OPTION_ID = field_meta["Priority"].options["<P0 (Critical) | P1 (High) | ...>"]
gh api graphql -f query='
mutation {
  updateProjectV2ItemFieldValue(input: {
    projectId: "'"$PROJECT_ID"'"
    itemId: "'"$ITEM_ID"'"
    fieldId: "'"$PRIORITY_FIELD_ID"'"
    value: { singleSelectOptionId: "'"$PRIORITY_OPTION_ID"'" }
  }) { projectV2Item { id } }
}'

# 2. Set Area (only if area:* label present AND field_meta["Area"] + option exist)
#    AREA_FIELD_ID  = field_meta["Area"].field_id
#    AREA_OPTION_ID = field_meta["Area"].options["<area name>"]
gh api graphql -f query='
mutation {
  updateProjectV2ItemFieldValue(input: {
    projectId: "'"$PROJECT_ID"'"
    itemId: "'"$ITEM_ID"'"
    fieldId: "'"$AREA_FIELD_ID"'"
    value: { singleSelectOptionId: "'"$AREA_OPTION_ID"'" }
  }) { projectV2Item { id } }
}'

# 3. Set Module (only if the heuristic matched unambiguously AND field_meta["Module"] + option exist)
#    MODULE_FIELD_ID  = field_meta["Module"].field_id
#    MODULE_OPTION_ID = field_meta["Module"].options["<module name>"]
gh api graphql -f query='
mutation {
  updateProjectV2ItemFieldValue(input: {
    projectId: "'"$PROJECT_ID"'"
    itemId: "'"$ITEM_ID"'"
    fieldId: "'"$MODULE_FIELD_ID"'"
    value: { singleSelectOptionId: "'"$MODULE_OPTION_ID"'" }
  }) { projectV2Item { id } }
}'

# 4. Move Status to Todo (final — only after all field-setting mutations succeed)
#    STATUS_FIELD_ID = field_meta["Status"].field_id
#    TODO_OPTION_ID  = field_meta["Status"].options["Todo"]
gh api graphql -f query='
mutation {
  updateProjectV2ItemFieldValue(input: {
    projectId: "'"$PROJECT_ID"'"
    itemId: "'"$ITEM_ID"'"
    fieldId: "'"$STATUS_FIELD_ID"'"
    value: { singleSelectOptionId: "'"$TODO_OPTION_ID"'" }
  }) { projectV2Item { id } }
}'
```

Track per-item success. If a field mutation fails partway, skip the Status promotion for that item and report the partial state — do not promote to `Todo` with broken fields. The user can re-run the skill to retry.

### Step 8 — Report

```
TRIAGE COMPLETE — project #18 — <date>
========================================
Promoted to Todo:        <N> items
Failed mid-mutation:     <N> items (Status not promoted; fields partially set)
Deferred (needs-labels): <N> items
Suspected duplicates:    <N pairs surfaced — your decision
Stale (FYI):             <N items — automation handles

PROMOTED
--------
#42  http://...  →  Todo (priority: P1 High, area: security, module: unset — peer feature)
#38  http://...  →  Todo (priority: P3 Low, area: dx, module: Internals)

DEFERRED
--------
#80  needs `priority:*` — please label and re-invoke /triage-issues

PARTIAL
-------
#92  set priority, FAILED at area mutation: <error>
     Re-invoke to retry.

FLAGGED (field/option missing on board — skipped)
-------------------------------------------------
#55  no `Module` field on board — promoted without Module
#61  Priority option "P0 (Critical)" not found in field_meta — Priority left unset

Suggested follow-ups:
  - Label and re-run on the deferred items
  - Review the duplicate pairs above
  - For partial items, investigate the error before re-running
  - For flagged items, add the missing field/option to the board (or adjust the label→name map) and re-run
```

## Output

- **Format:** Triage table at Step 6 (PROMOTING / NEEDS LABELS / SUSPECTED DUPLICATES / STALE) + final report at Step 8 (PROMOTED / DEFERRED / PARTIAL / FLAGGED).
- **Location:** Printed to chat; mutations to GitHub Projects v2 fields (Priority / Area / Module / Status) on approved items.
- **Side effects:** Backlog → Todo status promotions, Priority/Area/Module field sets on the project board.

## Example

**User says:** "Triage the Backlog."

**Claude does:** Runs `fetch_triage.py` (auto-detecting org/repo/project and capturing `field_meta`), filters to open + Backlog status, derives Priority from `priority:*` labels, Area from `area:*` labels, Module from title-scope heuristics, flags missing-label items and suspected duplicates, surfaces a triage table at the 🛑 gate. On "go", resolves field/option ids from `field_meta` by name and runs the sequential mutations per item, reporting promoted / deferred / partial / flagged counts.

**Result:** Backlog drains into Todo with consistent field values, no guessed Modules, no auto-closed duplicates (user decides) — on any org's board, with zero hardcoded ids.

## Red flags

- Skipping Step 0 (Create tasks) when invoked from another skill → step 0's todos coexist with the parent's task list, never replace them. Same anti-skip discipline as `/ship-issue`.
- Hardcoding field/option/project IDs instead of resolving them from Step 1's `field_meta` → ids are board-specific; this skill's whole portability rests on resolving them dynamically by name. A hardcoded id breaks the moment the skill runs against a different board.
- Promoting an item to `Todo` despite a failed field mutation → no. The whole point of `Todo` is "fields set, ready to be picked up". Leave at `Backlog` if any required field setter failed.
- Aborting the run because a field or option name is missing from `field_meta` → degrade gracefully: skip that single mutation, flag the item, and continue. Only a missing `Status`/`Todo` blocks promotion of that one item.
- Auto-closing duplicates → never. Surface and let the user decide; titles can be similar without being duplicates (e.g., adjacent fixes in the same area).
- Acting on `status: stale` items → defer to the repo's automation. This skill only reports them.
- Setting `Module` from a guess → if the heuristic table doesn't match cleanly, leave Module unset. A wrong Module is worse than no Module.
- Running mutations in parallel → sequential per-item, sequential field-then-status. Easier to attribute failures and respects GraphQL rate limits.
- Re-implementing the GraphQL fetch + pagination by hand instead of running `fetch_triage.py` → the script handles the per-page cap (100), the pagination loop, and field-metadata capture. Hand-rolling it reintroduces the `EXCESSIVE_PAGINATION` / silently-empty-Backlog failure mode the script exists to prevent.

## Files in this skill

- `SKILL.md` — this file
- `scripts/fetch_triage.py` — auto-detects org/repo/project, paginates all items, filters to open Backlog issues, and emits `field_meta` (every single-select field's id + option name→id map) so the skill resolves all ids dynamically

## Notes

- **Portable:** org, repo, and project number are resolved from the git remote (or `--org`/`--project`); every project/field/option id is resolved at mutation time from `field_meta` BY NAME. There are no hardcoded ids. The Module heuristic table and the Priority/Area option names are taxonomy conventions — adapt them to your board's option names.
- Requires single-select `Priority`/`Area`/`Module`/`Status` fields for full triage; missing fields/options degrade gracefully (skip + flag) rather than failing. A `Status` field with a `Todo` option is the minimum for promotion.
- The "leave Module unset" decision is deliberate — wrong Module routes sprint planning incorrectly. Carry this principle into any adapted version.
- Pairs with `/backlog-burn-down` (Todo → batch plan) and `/auto-ship` (Todo → PRs).
