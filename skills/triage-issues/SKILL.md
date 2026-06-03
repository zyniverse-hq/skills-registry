---
name: triage-issues
description: >
  Triage GitHub issues. Use when the user says "triage issues", "backlog
  triage", "weekly triage", "promote backlog to Todo", "sort the backlog",
  or "project board hygiene". Promotes Backlog issues to Todo on a GitHub
  Projects v2 board — derives Priority/Area/Module from labels + title
  heuristics, flags missing labels and suspected duplicates, requires user
  approval before mutations.
license: "Proprietary — internal use only (zysk.tech)"
compatibility: >
  Requires GitHub CLI (gh) with GraphQL API access and GitHub Projects v2
  board access. Designed for Claude Code. Defaults to zyni-ai org, tms-app
  repo, and project board #18 — swap org, repo, and project number before
  use in other projects.
metadata:
  version: "1.0.0"
  author: Varun U
  email: varun@zysk.tech
  category: engineering-practice
  tags: "project-board, github, triage, graphql, workflow"
  product: tms
  sprint: "4"
  tested_with: claude-opus-4-7
  user-invocable: "true"
---

# Triage Issues

> Board hygiene for project #18. Auto-add already drops new issues at `Status = Backlog` with no fields set. This skill walks the Backlog, fills in Priority/Severity/Area/Module from the issue's labels and title, flags items that can't be triaged automatically (missing required labels, no module signal, suspected duplicates), and on your approval promotes well-labelled items to `Todo`.

## When to use

- Weekly triage cadence to drain the Backlog
- After a batch of new issues lands (e.g., post `/auto-ship` if you opened parent issues)
- Before sprint planning, to make sure board fields reflect reality

### When NOT to use

- To work on a Todo issue — that's `/backlog-burn-down` or `/ship-issue`
- To enforce template completeness — that's `/gsd-inbox` (different concern)
- To handle stale issues — the `status: stale` label automation auto-applies at 60+ days and auto-closes after another 14. This skill only **reports** stale candidates.

**REFERENCES:** Field IDs and option IDs live in `CLAUDE.md` "Project Board Operations" → "Field IDs". Do not duplicate them here.

## Steps

### Step 0 — Create tasks

**MANDATORY.** TaskCreate one todo per remaining step (1–8). Mark `in_progress`/`completed`. Anti-skip discipline.

### Step 1 — Fetch Backlog items + their current field values

Paginate with `after: <endCursor>` until `hasNextPage: false`, accumulating nodes across pages. **GitHub caps `first:` at 100** (anything higher returns `EXCESSIVE_PAGINATION` and silently yields zero results). And the project board commonly carries 400+ items across all statuses; one page of 100 in insertion order will only cover a fraction of the Backlog. Without the loop, you'd miss most items.

```bash
gh api graphql -f query='
query($cursor: String) {
  organization(login: "zyni-ai") {
    projectV2(number: 18) {
      items(first: 100, after: $cursor) {
        pageInfo { hasNextPage endCursor }
        nodes {
          id
          fieldValues(first: 20) {
            nodes {
              ... on ProjectV2ItemFieldSingleSelectValue {
                field { ... on ProjectV2SingleSelectField { name } }
                name
                optionId
              }
            }
          }
          content {
            ... on Issue {
              number
              title
              body
              url
              state
              labels(first: 20) { nodes { name } }
            }
          }
        }
      }
    }
  }
}' -f cursor=""
```

After collecting nodes from every page, filter for triage candidates:

```bash
# Apply this to the accumulated nodes from all pages:
.[]
  | select(.content.state == "OPEN")
  | select(.fieldValues.nodes[]? | select(.field.name == "Status" and .name == "Backlog"))
```

If, after pagination + filtering, the Backlog set is empty, exit cleanly: "Backlog is empty — nothing to triage."

This matches the pagination pattern documented in `/backlog-burn-down` Step 1 — same project, same per-page cap, same failure mode if you skip the loop.

### Step 2 — Derive intended field values

For each Backlog item, build a derivation table from the issue's labels and title.

#### Priority (required)

From the `priority:` label. 1:1 mapping — see CLAUDE.md "Priority" table:

| Label | Board option | Option ID |
|---|---|---|
| `priority: critical` | P0 (Critical) | `550bedbb` |
| `priority: high` | P1 (High) | `b2eca0ce` |
| `priority: medium` | P2 (Medium) | `f05645b9` |
| `priority: low` | P3 (Low) | `d2302afe` |

If no `priority:` label is present, mark the item `needs-labels` and skip promotion.

#### Severity (skip — user sets manually)

Severity is the bug's impact magnitude (data loss, blocks login, crash for 5% of users) — orthogonal to Priority (when we schedule it). It is **not** derivable from labels: a bug can be Severity High + Priority Low (workaround exists) or Severity Low + Priority Critical (cosmetic but blocks a launch). A heuristic that just copies Priority into Severity adds no information and writes confidently-wrong values.

Leave Severity unset. The user fills it in when reviewing the bug, where they can read the body and judge impact.

#### Area (optional)

From the `area:` label. 1:1 mapping — see CLAUDE.md "Area" table. If multiple `area:` labels exist (rare), pick the first; flag in the report.

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
TRIAGE TABLE — project #18 — <date>
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

For each approved item, run mutations sequentially (parallel risks GraphQL rate limits and makes failure attribution harder). Sequence per item:

```bash
# 1. Set Priority field
gh api graphql -f query='
mutation {
  updateProjectV2ItemFieldValue(input: {
    projectId: "PVT_kwDOCrP2y84BUSTb"
    itemId: "<projectItemId>"
    fieldId: "PVTSSF_lADOCrP2y84BUSTbzhBbiuk"
    value: { singleSelectOptionId: "<priorityOptionId>" }
  }) { projectV2Item { id } }
}'

# 2. Set Area (only if area:* label present)
gh api graphql -f query='
mutation {
  updateProjectV2ItemFieldValue(input: {
    projectId: "PVT_kwDOCrP2y84BUSTb"
    itemId: "<projectItemId>"
    fieldId: "PVTSSF_lADOCrP2y84BUSTbzhBbiuo"
    value: { singleSelectOptionId: "<areaOptionId>" }
  }) { projectV2Item { id } }
}'

# 3. Set Module (only if heuristic matched unambiguously)
gh api graphql -f query='
mutation {
  updateProjectV2ItemFieldValue(input: {
    projectId: "PVT_kwDOCrP2y84BUSTb"
    itemId: "<projectItemId>"
    fieldId: "PVTSSF_lADOCrP2y84BUSTbzhBcsv0"
    value: { singleSelectOptionId: "<moduleOptionId>" }
  }) { projectV2Item { id } }
}'

# 4. Move Status to Todo (final — only after all field-setting mutations succeed)
gh api graphql -f query='
mutation {
  updateProjectV2ItemFieldValue(input: {
    projectId: "PVT_kwDOCrP2y84BUSTb"
    itemId: "<projectItemId>"
    fieldId: "PVTSSF_lADOCrP2y84BUSTbzhBbik0"
    value: { singleSelectOptionId: "c2b8c846" }
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
#92  set priority + severity, FAILED at area mutation: <error>
     Re-invoke to retry.

Suggested follow-ups:
  - Label and re-run on the deferred items
  - Review the duplicate pairs above
  - For partial items, investigate the error before re-running
```

## Output

- **Format:** Triage table at Step 6 (PROMOTING / NEEDS LABELS / SUSPECTED DUPLICATES / STALE) + final report at Step 8 (PROMOTED / DEFERRED / PARTIAL).
- **Location:** Printed to chat; mutations to GitHub Projects v2 fields (Priority / Area / Module / Status) on approved items.
- **Side effects:** Backlog → Todo status promotions, Priority/Area/Module field sets on the project board.

## Example

**User says:** "Triage the Backlog."

**Claude does:** Paginates every project item, filters to open + Backlog status, derives Priority from `priority:*` labels, Area from `area:*` labels, Module from title-scope heuristics, flags missing-label items and suspected duplicates, surfaces a triage table at the 🛑 gate. On "go", runs the sequential mutations per item, reports promoted / deferred / partial counts.

**Result:** Backlog drains into Todo with consistent field values, no guessed Modules, no auto-closed duplicates (user decides).

## Red flags

- Skipping Step 0 (Create tasks) when invoked from another skill → step 0's todos coexist with the parent's task list, never replace them. Same anti-skip discipline as `/ship-issue`.
- Hardcoding field/option IDs from this skill instead of referencing CLAUDE.md → IDs live in CLAUDE.md as the single source of truth. Drift here breaks every board-touching skill.
- Promoting an item to `Todo` despite a failed field mutation → no. The whole point of `Todo` is "fields set, ready to be picked up". Leave at `Backlog` if any required field setter failed.
- Auto-closing duplicates → never. Surface and let the user decide; titles can be similar without being duplicates (e.g., adjacent fixes in the same area).
- Acting on `status: stale` items → defer to the repo's automation. This skill only reports them.
- Setting `Module` from a guess → if the heuristic table doesn't match cleanly, leave Module unset. A wrong Module is worse than no Module.
- Running mutations in parallel → sequential per-item, sequential field-then-status. Easier to attribute failures and respects GraphQL rate limits.
- Using `first: 200` or omitting the pagination loop on the Step 1 query → **GitHub's per-page cap is 100**; `first: 200` returns `EXCESSIVE_PAGINATION` and yields zero items, which the skill silently treats as "Backlog is empty." Even `first: 100` without pagination only fetches the first page, missing most of the Backlog when the project carries 400+ items. The pagination loop (`after: <endCursor>` until `hasNextPage: false`) is the contract — same failure mode `/backlog-burn-down` already documents.

## Notes

- TMS-flavored: GraphQL targets `organization(login: "zyni-ai")` and `projectV2(number: 18)`; project + field IDs (`PVT_kwDOCrP2y84BUSTb`, `PVTSSF_*`) are TMS-specific. The Module heuristic table is TMS-specific too. Swap all of these for your org / project / field IDs / module taxonomy.
- The "leave Module unset" decision is deliberate — wrong Module routes sprint planning incorrectly. Carry this principle into any adapted version.
- Pairs with `/backlog-burn-down` (Todo → batch plan) and `/auto-ship` (Todo → PRs).
