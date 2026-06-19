---
name: backlog-burn-down
description: "Scans a GitHub Projects v2 Todo column, stale-checks and classifies issues, then assigns each to a developer with a board move and comment. Use to plan a sprint or pick the team's next work. To first promote Backlog items into Todo, use triage-issues."
version: 1.2.1
author: Varun U
email: varun@zysk.tech
category: engineering-practice
tags:
  - project-board
  - github
  - planning
  - triage
  - team-management
tested_with: claude-opus-4-7
user-invocable: true
---

# Backlog Burn-Down

> PM planning tool. Scan unassigned `Todo` issues, stale-check, classify by track, present a batch plan, then walk the PM through assigning each issue to a developer — moving it to In Progress on the board and leaving a comment on each.

## When to use

- The PM asks "assign today's work to the team", "burn down the backlog", "what should the devs work on?", "plan the sprint", "let's assign the queue"
- Before a sprint or focus block, to distribute ready issues across the team
- When the PM wants a clear picture of what's in Todo and who should own what

### When NOT to use

- Triaging `Backlog` → `Todo` — that's `/triage-issues`'s job
- The PM already knows exactly which issue to assign and to whom — do it directly via `gh`

## Configuration

The skill reads team and project details from `~/.claude/skills/backlog-burn-down/config.local.json`. Copy `assets/config.example.json` to that path and fill in your team. This file is set once and reused on every run — it never needs to change unless the team or project changes.

```json
{
  "sprint": 4,
  "team": [
    { "name": "Alice",   "github": "alice-gh" },
    { "name": "Bob",     "github": "bob-gh" },
    { "name": "Charlie", "github": "charlie-gh" }
  ]
}
```

If the config file doesn't exist, the skill will ask for sprint number and team roster on first run and write the file. Org, repo, and project number are always resolved dynamically from the git remote (see Step 1) — they don't belong in config because they change per-repo.

## Operating principle

Every issue is a *proposed* answer — challenge the question before implementing. The right answer is often smaller than what was asked. Carry this lens through stale-check and classify so you spot already-fixed bugs, duplicates, and "why are we even doing this" entries before sinking time into them.

## Steps

### Step 0 — Create tasks

**MANDATORY.** TaskCreate one todo per remaining step (1–5). Mark `in_progress`/`completed`. Don't skip steps — each one feeds the next.

### Step 1 — Fetch unassigned Todo items

Run the bundled collector. Resolve its absolute path from the skill's own directory so it works regardless of which repo the PM invokes the skill from:

```bash
SKILL_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
python3 "$SKILL_DIR/scripts/fetch_backlog.py" --pretty
```

The script:
- Auto-detects org and repo from the current git remote
- Lists available projects and auto-selects if there is only one, otherwise prompts
- Paginates until all items are fetched (boards commonly exceed 100 items)
- Filters to: Status = `Todo`, state = `OPEN`, assignees empty or includes the current user
- Sorts by priority (`critical` → `high` → `medium` → `low`), then `updatedAt` ascending

If the script exits with a non-zero code, print the last line of stderr and ask: *"The backlog fetch failed — do you want to enter issues manually instead?"*

The output JSON includes `org`, `repo`, `project_number`, `my_login`, and an `issues` array. Each issue carries `item_id`, `project_id`, and `field_meta` needed for Step 5's board mutations — keep this data in context through the end of the skill.

### Step 2 — Per-issue first-principles + stale-check

For each candidate, evaluate:

- **Does the file/function the issue names still exist on `origin/dev`?** Use the **Grep tool** (per CLAUDE.md), not Bash grep.
- **Has it already been fixed?** `git log -S "<identifier>" origin/dev --oneline | head -5`.
- **Has the codebase redesigned around the problem?** (file deleted, architecture changed, alternative shipped)
- **Does the body look ambiguous?** Multiple valid approaches, missing context, or "we should think about X" framing.
- **Does it depend on an unmerged PR or backend change?**

Dispositions:

| Finding | Action |
|---|---|
| Stale (already fixed / file gone) | Close with verification comment, drop from batch |
| Ambiguous body | Defer with note — needs PM or tech lead to clarify before assigning |
| Carries `status: needs investigation` label | Defer (already flagged ambiguous) |
| Blocked dependency | Defer with note explaining the block |
| Otherwise | Proceed to classify |

`/triage-issues` already produces a stale report for items still in `Backlog`, so this skill only needs to recheck items that already made it to `Todo`. The two stale checks complement each other: triage flags Backlog noise, burn-down catches Todo items that went stale post-promotion (e.g., the underlying bug got fixed by an unrelated PR).

Stale-close command:

```bash
gh issue close <N> --repo <ORG>/<REPO> \
  --comment "Closing as stale — the referenced code no longer exists on origin/dev."
```

### Step 3 — Classify each surviving candidate

Read `references/classification.md` for full track definitions and stale-check dispositions. Summary:

- **Quick-fix** — 1–2 line change, obvious fix, no design decisions needed
- **Clear-scope** — explicit fix, up to 3 files, one clear outcome
- **Ambiguous** — unclear requirements or multiple valid approaches → defer, do not assign

When in doubt, defer. An ambiguously assigned issue wastes a dev's time.

### Step 4 — Bundle quick-fixes by mental model

Read `references/classification.md` (Bundling Rules section) for full guidance. Summary:

Bundle quick-fixes that share the same **mental model** — issues a dev would naturally fix together in one focused session. Do not bundle by size alone. Unrelated domains, mixed bug-fix + refactor, or anything that would make a PR harder to review should ship as separate items.

### Step 5 — Present batch plan, assign to developers, and comment

**5a — Print the batch plan:**

```
BATCH PLAN — <date>
====================
Scanned:         N Todo items
Stale (closed):  N issues
Deferred:        N issues (ambiguous / blocked)
Ready to assign: N issues

QUICK-FIX BUNDLES
-----------------
Bundle A (2 issues, a11y mental model)
  #2780  P2  fix(adaptive-test): missing aria-label on submit button
  #2784  P2  fix(exam): missing aria-label on results panel

CLEAR-SCOPE
-----------
  #2779  P1  fix(proctoring): video upload 413 — switch to presigned S3 URL
  #2772  P2  refactor(auth): extract OTP verification helper

DEFERRED
--------
  #2725  ambiguous — body needs clarification before assigning
  #2640  blocked — waits on backend session-refresh endpoint

CLOSED THIS RUN (stale)
-----------------------
  #2501  closed — referenced helper deleted in #2489
```

**5b — Show the team roster and ask the PM to assign:**

Display the team roster from config (see Configuration section). Then walk through each ready-to-assign issue in priority order, one at a time:

```
TEAM ROSTER
-----------
1. @alice
2. @bob
3. @charlie

[1/4] #2779 P1 — fix(proctoring): video upload 413 (clear-scope)
Assign to (name or number, or 'skip'):
```

Wait for the PM's response before moving to the next issue. Accept names, numbers from the roster, or GitHub handles directly.

**5c — Execute each assignment immediately after the PM confirms:**

For each assigned issue:

1. Move to In Progress on the board:
```bash
gh project item-edit --id <ITEM_ID> --project-id <PROJECT_ID> \
  --field-id <STATUS_FIELD_ID> --single-select-option-id <IN_PROGRESS_OPTION_ID>
```

2. Set the assignee on the issue:
```bash
gh issue edit <N> --repo <ORG>/<REPO> --add-assignee <github-login>
```

3. Drop a comment on the issue:
```
Picked up for Sprint <N> — assigned to @<dev>.
Track: <quick-fix | clear-scope> | ETA: <1–2 days | 3–5 days>
```

ETA defaults: quick-fix = 1–2 days, clear-scope = 3–5 days. Sprint number comes from config if set, otherwise ask the PM once at the start of Step 5b.

**5d — Print an assignment summary when done:**

```
ASSIGNMENTS — <date>
====================
#2779 → @alice   (In Progress, clear-scope, ETA 3–5 days)
#2780 → @bob     (In Progress, quick-fix, ETA 1–2 days)
#2784 → @bob     (In Progress, quick-fix, ETA 1–2 days)
#2772 → skipped
```

## Output

- **Format:** Batch plan block + per-issue assignment prompts + assignment summary
- **GitHub mutations:** Stale-closes (Step 2), status moves to In Progress, assignee set, comment dropped per issue
- **No files written**

## Example

**User says:** "Assign today's work to the team"

**Claude does:** Paginates project Todo items, stale-checks, classifies, presents the BATCH PLAN, shows the team roster, walks the PM through assigning each issue in priority order, moves each to In Progress, assigns the dev, and drops a comment.

**Result:** Every ready issue has an owner, is In Progress on the board, and has a comment the dev can read when they pick it up.

## Red flags

- Skipping Step 0 (Create tasks) — each step feeds the next; skipping breaks the flow
- Using `first: 100` without pagination — silently misses 100+ items; boards in active orgs commonly exceed that count
- Skipping stale-check on items that "look obvious" — already-fixed bugs and redesigned-around problems hide here; stale-check is the highest-leverage step
- Bundling unrelated mental models because the diffs are small — splits reviewer attention; keep bundles thematically tight
- Assigning ambiguous or deferred issues — they need clarification first; assigning them puts a dev in a no-win situation
- Closing an issue as stale without the verification comment — leaves no audit trail; future reviewers can't tell "actually fixed" from "accidentally closed"

## Files in this skill

- `SKILL.md` — this file
- `scripts/fetch_backlog.py` — fetches and filters Todo issues from GitHub Projects v2, handles pagination and sorting
- `references/classification.md` — track definitions, stale-check dispositions, bundling rules, ETA defaults
- `assets/config.example.json` — copy to `~/.claude/skills/backlog-burn-down/config.local.json` and fill in sprint + team roster

## Notes

- Works with any GitHub org, repo, and project — context is resolved automatically from the current git remote at Step 1.
- If the repo has no GitHub remote or you're outside a git directory, the skill will ask for `org/repo` and project number explicitly.
- Pairs with `/triage-issues` (Backlog → Todo promotion). Standalone if you only want the batch-plan + assignment flow.
