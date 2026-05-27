---
name: backlog-burn-down
description: "Scans the Todo column of a GitHub Projects v2 board, stale-checks each issue, classifies into quick-fix / clear-scope / ambiguous tracks, bundles by mental model, and presents a batch plan for the user to pick from. Works with any GitHub org, repo, and project — auto-detects context from the current git repo."
version: 1.1.0
author: Varun U
email: varun@zysk.tech
category: engineering-practice
tags:
  - project-board
  - github
  - planning
  - triage
  - workflow
tested_with: claude-opus-4-7
user-invocable: true
---

# Backlog Burn-Down

> Deliberate batch planning. Scan unassigned `Todo` issues, stale-check, classify, present a batch plan, and stop. The user picks what to ship; execution is `/ship-issue` per issue (or `/auto-ship <N1> <N2>` for the chosen subset).

## When to use

- The user asks "what should I work on?", "show me Todo", "let's burn down the backlog", "plan my day", "what's in flight?"
- Before a focus block, to size up what's actually ready to ship

### When NOT to use

- You already know which issues to ship → `/auto-ship 1234 5678`
- You want to ship everything in Todo without choosing → `/auto-ship`
- You're handling a single specific issue → `/ship-issue N` directly
- Triaging Backlog → Todo → `/triage-issues`'s job

### How this skill compares

| Skill | What it does | Stops for user input? |
|---|---|---|
| `/triage-issues` | Promote `Backlog` → `Todo` (set Priority/Area/Module from labels) | Yes — confirmation gate before mutations |
| `/backlog-burn-down` | Scan `Todo`, classify, present a batch plan | **Yes — this skill is the deliberate review gate** |
| `/auto-ship` (no args) | Drain `Todo` autonomously, ship everything eligible | No |
| `/auto-ship N1 N2` | Ship a specific subset autonomously | No |
| `/ship-issue N` | Execute one issue end-to-end (full track) | At track checkpoints |

Use `/backlog-burn-down` when you want to *see and choose*. Use `/auto-ship` when you've already decided.

## Operating principle

Every issue is a *proposed* answer — challenge the question before implementing. The right answer is often smaller than what was asked. Carry this lens through stale-check and classify so you spot already-fixed bugs, duplicates, and "why are we even doing this" entries before sinking time into them.

## Steps

### Step 0 — Create tasks

**MANDATORY.** TaskCreate one todo per remaining step (1–5). Mark `in_progress`/`completed`. Anti-skip discipline — same as `/ship-issue`, `/auto-ship`, etc.

### Step 1 — Resolve project context

Before fetching issues, resolve the org, repo, and project number from the current environment. Do this once and use the resolved values in all subsequent steps.

**Resolve org and repo** from the current git remote:

```bash
gh repo view --json owner,name --jq '"\(.owner.login)/\(.name)"'
```

This gives `<ORG>/<REPO>`. If it fails (not inside a git repo with a GitHub remote), ask the user: "Which GitHub repo should I scan? (e.g. `myorg/myrepo`)"

**Resolve project number** — list the org's projects and let the user pick:

```bash
gh project list --owner <ORG> --format json --jq '.projects[] | "#\(.number) \(.title)"'
```

If the user already stated a project number in their message (e.g. "burn down project 5"), use that directly without asking. If there's only one project, use it automatically. Otherwise ask: "Which project number should I scan?" and show the list.

**Resolve the current GitHub login** (for `@me` filtering):

```bash
gh api user --jq '.login'
```

Store `ORG`, `REPO`, `PROJECT_NUMBER`, and `MY_LOGIN` — use them in every command below.

**Fetch unassigned Todo items** — paginate with `after: <endCursor>` until `hasNextPage: false`. Project boards commonly exceed 100 items; `first: 100` without pagination silently misses the rest.

```bash
gh api graphql -f query='
query($org: String!, $num: Int!, $cursor: String) {
  organization(login: $org) {
    projectV2(number: $num) {
      items(first: 100, after: $cursor) {
        pageInfo { hasNextPage endCursor }
        nodes {
          id
          fieldValues(first: 20) {
            nodes {
              ... on ProjectV2ItemFieldSingleSelectValue {
                field { ... on ProjectV2SingleSelectField { name } }
                name
              }
            }
          }
          content {
            ... on Issue {
              number title body url state updatedAt
              assignees(first: 10) { nodes { login } }
              labels(first: 20) { nodes { name } }
            }
          }
        }
      }
    }
  }
}' -f org="<ORG>" -F num=<PROJECT_NUMBER> -f cursor=""
```

Filter client-side to:

- Project Status = `Todo`
- Issue state = `OPEN`
- Assignees: empty OR includes `<MY_LOGIN>` (don't take teammates' work)

Sort by Priority (`priority: critical` → `high` → `medium` → `low`), then `updatedAt` ascending within priority.

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
| Ambiguous body | Defer with note suggesting `/decision-brief` |
| Carries `status: needs investigation` label | Defer (already flagged ambiguous by a prior `/auto-ship`) |
| Blocked dependency | Defer with note explaining the block |
| Otherwise | Proceed to classify |

`/triage-issues` already produces a stale report for items still in `Backlog`, so this skill only needs to recheck items that already made it to `Todo`. The two stale checks complement each other: triage flags Backlog noise, burn-down catches Todo items that went stale post-promotion (e.g., the underlying bug got fixed by an unrelated PR).

Stale-close command:

```bash
gh issue close <N> --repo <ORG>/<REPO> \
  --comment "Closing as stale — the referenced code no longer exists on origin/dev."
```

### Step 3 — Classify each surviving candidate

| Track | When | Execution |
|---|---|---|
| **Quick-fix** | 1-2 line change, obvious, no design decisions | Shared worktree; can bundle same-theme issues |
| **Clear-scope** | Explicit fix, 1-3 files, scope obvious | Dedicated worktree; one checkpoint |
| **Ambiguous** | Unclear requirements, multiple design options | Defer from this batch — needs `/decision-brief` first |

### Step 4 — Bundle quick-fixes by mental model

Bundle by **same mental model**, not same size. Two `aria-label` fixes bundle cleanly; an unrelated bug + refactor don't — they split reviewer attention.

| Example pair | Bundle? | Why |
|---|---|---|
| Two missing `aria-label` attributes | Yes | Same a11y mental model |
| Two `console.error` → `Sentry` swaps | Yes | Same observability mental model |
| `aria-label` fix + wrong API URL | No | Unrelated domains |
| Bug fix + scope-creep refactor | No | Different intents |

### Step 5 — Present batch plan and STOP

Print this exact shape (copy the headings, fill in the data):

```
BATCH PLAN — <date>
====================
Scanned:         N Todo items
Stale (closed):  N issues
Deferred:        N issues (ambiguous / blocked)
Ready to ship:   N issues

QUICK-FIX BUNDLES
-----------------
Bundle A (2 issues, a11y mental model)
  #2780  fix(adaptive-test): missing aria-label on submit button
  #2784  fix(exam): missing aria-label on results panel

CLEAR-SCOPE
-----------
  #2779  P1  fix(proctoring): video upload 413 — switch to presigned S3 URL
  #2772  P2  refactor(auth): extract OTP verification helper

DEFERRED
--------
  #2725  ambiguous — body asks "should features/skills/ grow?" — run /decision-brief
  #2640  blocked — waits on backend session-refresh endpoint

CLOSED THIS RUN (stale)
-----------------------
  #2501  closed — referenced helper deleted in #2489
```

🛑 **Wait for user input.** Acceptable responses (match intent, not exact wording):

| User says | Next step |
|---|---|
| "ship all" / "go" / "lgtm" | If `/auto-ship` is available, run `/auto-ship N1 N2 N3 ...`. If not, print issue numbers in a copy-friendly list and suggest running `/ship-issue N` per issue. |
| "ship only Bundle A" / "just #2779" | Same fallback logic — `/auto-ship` for the named subset if available, otherwise `/ship-issue` per issue. |
| "skip #N" / "everything except #N" | Same fallback logic for the remaining subset. |
| "ship Bundle A as a quick-fix bundle" | Hand off the bundle list to `/ship-issue` quick-fix track (one PR for the bundle). |
| "decision-brief on #2725 first" | Run `/decision-brief` on the named issue, then re-invoke this skill. |
| "no" / "cancel" / "looks fine for now" | Exit without action. |
| Anything else / unclear | Ask: "Did you want to ship, defer, or cancel? I can also explain or re-check any issue." |

## Output

- **Format:** Single grouped batch-plan block printed at Step 5 (counts header, Quick-fix bundles, Clear-scope, Deferred, Closed-this-run).
- **Location:** Printed to chat. No file written, no GitHub mutations except stale-closes from Step 2.
- **Side effects:** Stale issues are auto-closed with a verification comment.

## Example

**User says:** "What's in my queue today?"

**Claude does:** Paginates project Todo items, filters to unassigned + open, stale-checks each via Grep + `git log -S`, classifies into quick-fix / clear-scope / ambiguous / deferred, bundles quick-fixes by mental model, presents the BATCH PLAN block.

**Result:** A scannable plan the user can act on in one word ("ship all" / "skip #2725" / "decision-brief on #2725 first").

## Worktree strategy

This skill hands off to `/auto-ship` (or `/ship-issue` directly), which own the worktree convention. See `/auto-ship` Step 5 for the canonical setup — shared `.worktrees/quick-fixes` for bundles, dedicated `.worktrees/<branch-name>` for clear-scope work.

## Red flags

- Skipping Step 0 (Create tasks) when invoked from another skill → step 0's todos coexist with the parent's task list
- Using `first: 100` without pagination → silently misses 100+ items on the board; the boards in this org commonly exceed that count
- Skipping stale-check on items that "look obvious" → the obvious ones include already-fixed bugs, redesigned-around problems, and stalled threads. Stale-check is the highest-leverage step in the skill.
- Bundling unrelated mental models because the diffs are all small → splits reviewer attention; ship them as separate PRs even if quick-fix-tracked
- Auto-shipping the batch after presenting the plan → no, this skill is the *deliberate alternative* to `/auto-ship`. Stop at Step 5 and wait. If the user wants no-checkpoint, they'd have invoked `/auto-ship` directly.
- Including ambiguous-bodied items in a quick-fix bundle → they need `/decision-brief` first; bundling them risks `/ship-issue` failing mid-batch
- Closing an issue as stale without the verification comment → leaves no audit trail for why it was closed; future reviewers can't tell "actually fixed" from "noise"
- Treating Step 5's STOP as a checkpoint to skip when invoked from a parent skill → no. The whole point of this skill is the deliberate gate. If a parent wants to skip the gate, it should have called `/auto-ship` instead.

## Notes

- Works with any GitHub org, repo, and project — context is resolved automatically from the current git remote at Step 1. No config needed.
- If the repo has no GitHub remote or you're outside a git directory, the skill will ask for `org/repo` and project number explicitly.
- Pairs with `/triage-issues` (Backlog → Todo), `/auto-ship` (autonomous drain), `/ship-issue` (single-issue execution). Standalone if you only want the batch-plan view.
