---
name: auto-merge
description: "One-shot drain of an auto-ship PR queue. Re-checks each PR's CI + merge state + review decision, squash-merges what's MERGEABLE + APPROVED + clean of unaddressed comments, and reports per-entry verdict. No scheduler."
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
---

# Auto-Merge

> One-shot queue drain. Process every entry in `.claude/auto-ship-queue.json`, merge whatever is cleanly approved, skip the rest with a clear reason. Pure user-triggered — there is no wake-up loop, no rescheduling, and no review-comment handling. The user invokes the skill when they want to merge currently-green PRs and accepts that the rest stay in the queue until they're addressed.

## When to use

- After reviewing one or more open PRs created by `/auto-ship` and approving the ones you want merged
- To check what's currently mergeable in the queue (the report tells you, even if nothing actually merges this run)

### When NOT to use

- To handle review comments — that's `/handle-review`'s job, on a per-PR basis
- To wait for CI — invoke after CI is green; this skill does not poll
- To resolve conflicts — `BEHIND` / `CONFLICTING` PRs get a clean rebase attempt, but conflicts are reported and skipped

## Steps

### Step 0 — Create tasks

**MANDATORY.** TaskCreate one todo per remaining step (1–6). Mark `in_progress`/`completed`. **This is how step-skipping is prevented — do not collapse into a parent skill's task list if invoked from one.**

### Step 1 — Load queue

Read `.claude/auto-ship-queue.json`. If the user provided an absolute path in the invocation prompt, use it exactly as passed. Otherwise resolve relative to the current repo root.

- File missing → "No queue file found at <path>. Nothing to drain." Exit cleanly.
- File present, zero entries → "Queue is empty." Exit cleanly.

Do not filter by status at this step — every entry gets re-checked against live PR state, since a previous run's status is just the last-seen snapshot.

### Step 2 — Gather PR state for each entry

For each entry, gather everything needed for the verdict in a single `gh` query:

```bash
gh pr view <prNumber> --repo "<entry.repo>" \
  --json mergeStateStatus,reviewDecision,statusCheckRollup,state \
  -q '{
    state,
    mergeStateStatus,
    reviewDecision,
    ciFailing: ([.statusCheckRollup[]? | select(.conclusion == "FAILURE" or .conclusion == "CANCELLED")] | length) > 0,
    ciRunning: ([.statusCheckRollup[]? | select(.status == "IN_PROGRESS" or .status == "QUEUED")] | length) > 0
  }'
```

`reviewDecision == "APPROVED"` is the single signal we trust for "comments addressed" — by the time a human approves, they've already weighed in on any open auto-review comments. We deliberately do not count bot comments separately, because `gh pr view --json comments` does not expose resolution state (that's only on `reviewThreads.isResolved` via GraphQL), so a count would mark every APPROVED PR with historical bot chatter as `comments-pending` forever.

### Step 3 — Assign a verdict per entry

Verdict rules, evaluated in order. First match wins.

| Condition | Verdict | Final action |
|---|---|---|
| `state == "MERGED"` | `merged` | Mark + prune (already done) |
| `state == "CLOSED"` (not merged) | `abandoned` | Mark + prune |
| `ciFailing == true` | `ci-failed` | Skip; user must fix CI |
| `ciRunning == true` | `ci-running` | Skip; re-run `/auto-merge` after CI completes |
| `mergeStateStatus == "BEHIND"` or `"CONFLICTING"` | `needs-rebase` | Attempt clean rebase (Step 4); on conflict, mark `rebase-conflict`; if no local worktree for the branch, mark `needs-rebase-manual` |
| `reviewDecision == "CHANGES_REQUESTED"` | `changes-requested` | Skip; user must address |
| `reviewDecision == "REVIEW_REQUIRED"` | `awaiting-review` | Skip; no human review yet |
| `mergeStateStatus == "MERGEABLE"` AND (`reviewDecision == "APPROVED"` OR no review required) | `mergeable` | Squash merge (Step 4) |
| `mergeStateStatus == "BLOCKED"` (other reason) | `blocked` | Skip; report raw `mergeStateStatus` for the user to investigate |
| Anything else | `unknown` | Skip; log the raw state for debugging |

The order matters: `MERGED`/`CLOSED` short-circuits even if CI failed (the PR is gone), and `ci-failed` short-circuits before `needs-rebase` (no point rebasing a broken build).

### Step 4 — Execute the actionable verdicts

Two verdicts trigger writes; the rest are reporting-only — *except* the Done-board move, which also fires for already-merged PRs (see below).

**`mergeable` → squash merge:**
```bash
gh pr merge <prNumber> --squash --repo "<entry.repo>"
```
On success: set `entry.status = "merged"` and run the Done-board move (graphql mutation per issue number — see your project board ops doc). On failure: set `entry.status = "merge-failed"` and capture the error in the report.

**`merged` (state was already MERGED before this run) → fire the Done-board move idempotently:**

Externally-merged PRs (merged via GitHub UI, another tool, or recovery from a prior Step 5 write failure) skip the squash merge — the PR is already merged. But still fire the same Done-board mutation per issue number. The mutation is idempotent (moving an already-Done item to Done is a no-op), so the cost is one extra graphql call per issue. The benefit is the board stays consistent regardless of how the merge happened — without this, issues whose PRs were merged outside the skill could stay stuck in In Review on the board indefinitely.

**`needs-rebase` → clean rebase attempt:**

Resolve the branch's worktree from `git worktree list --porcelain`. If no worktree is registered for the branch (auto-ship may have recycled the shared `.worktrees/quick-fixes` directory and released this branch), do **not** attempt to rebase from the main repo CWD — that would switch the main checkout to a different branch and risk destroying unrelated local state. Instead, set `entry.status = "needs-rebase-manual"` and tell the user to rebase manually.

If the worktree exists:
```bash
WT=$(git worktree list --porcelain | awk -v b="refs/heads/<branch>" '/^worktree / {wt=$2} /^branch / {if ($2==b) print wt}')
git -C "$WT" fetch origin dev
git -C "$WT" rebase origin/dev
```
- Rebase clean → `git -C "$WT" push --force-with-lease`; set `entry.status = "rebased"` (CI will re-run; the user invokes `/auto-merge` again later to retry).
- Rebase conflict → `git -C "$WT" rebase --abort`; set `entry.status = "rebase-conflict"`; report the branch and tell the user to handle manually.

For all other verdicts, just update `entry.status` to the verdict name. No git or GitHub writes.

### Step 5 — Update queue file (atomic write + prune)

Use the shared `.claude/scripts/queue-io.js` helper. Pass the list of `(prNumber, status)` pairs this run determined; the script reads fresh, merges status changes, prunes only `merged` and `abandoned`, and writes atomically:

```bash
node .claude/scripts/queue-io.js update-and-prune \
  "<absolute-queue-path>" \
  '[
    {"prNumber": 1234, "status": "merged"},
    {"prNumber": 5678, "status": "ci-failed"},
    {"prNumber": 9012, "status": "rebase-conflict"}
  ]'
```

What the script does:

1. **Re-reads the queue fresh.** A concurrent `/auto-ship` run may have appended entries since Step 1; the merge in step 2 below operates on the live state, not the stale read.
2. **Merges status changes** by `prNumber`. Updates that don't match a current entry print a warning and are skipped rather than failing the whole run.
3. **Prunes only `merged` and `abandoned`.** Every other status (`ci-failed`, `changes-requested`, `awaiting-review`, `rebase-conflict`, `needs-rebase-manual`, `merge-failed`, `blocked`, etc.) stays in the queue so the next `/auto-merge` run re-checks it. The user expects to see what's still pending until they actively clean up.
4. **Atomic write** via `.tmp` + `renameSync`. If the queue file disappeared mid-run (manual cleanup), the script exits 0 with a notice instead of recreating it.

**Stuck entries:** `rebase-conflict`, `needs-rebase-manual`, and `merge-failed` won't auto-resolve on a future invocation if the underlying state hasn't changed; once the user fixes them out-of-band (manual rebase + push, or close the PR), the next `/auto-merge` will pick up the new live state and either merge or prune.

### Step 6 — Report

Output a single grouped table. Lead with what's done (the win), then what needs the user's attention, then what's transient. The user reads this top-down, so high-signal entries come first.

**Bucket assignment by verdict** — every verdict has exactly one home. This table is the source of truth; if you find yourself debating where to put something, re-check here:

| Verdict | Bucket | Why |
|---|---|---|
| `merged` | Done | PR is on `dev` — whether merged this run or externally, user just wants "what's done" |
| `abandoned` | Done | PR is closed without merge — terminal, no follow-up needed |
| `ci-failed` | Needs your attention | User must fix CI |
| `changes-requested` | Needs your attention | User must address reviewer |
| `rebase-conflict` | Needs your attention | User must rebase manually |
| `needs-rebase-manual` | Needs your attention | No worktree found — user must rebase manually |
| `merge-failed` | Needs your attention | API-layer merge failure; investigate |
| `blocked` | Needs your attention | Branch protection blocking — investigate raw `mergeStateStatus` |
| `ci-running` | Transient | Re-run after CI completes |
| `awaiting-review` | Transient | Re-run after review lands |
| `rebased` | Transient | Push succeeded; CI re-running; re-run later to merge |
| `unknown` | Needs your attention | Log raw state; user investigates |

```
Auto-merge complete.

Done (N):
  - #PR1 — merged — closes #ISSUE_A
  - #PR2 — merged — closes #ISSUE_B, #ISSUE_C
  - #PR3 — abandoned — closes #ISSUE_D (PR closed without merging)

Needs your attention (N):
  - #PR4 — changes-requested by @reviewer
  - #PR5 — ci-failed — see <CI URL>
  - #PR6 — rebase-conflict — manual rebase needed on branch <branch>
  - #PR7 — blocked — mergeStateStatus=BLOCKED (e.g., required check not yet posted) — investigate

Transient — re-run `/auto-merge` later (N):
  - #PR8 — ci-running
  - #PR9 — awaiting-review
  - #PR10 — rebased and pushed (CI re-running)
```

If nothing actionable happened, say so plainly: "Queue scanned, nothing mergeable right now. Re-run after CI completes / reviews land."

**Merged externally**: If a PR's live state was already `MERGED` before this run started (i.e., merged outside the skill — direct GitHub merge, another tool, etc.), still list it under Done. The user's mental model is "what's the queue done with?" not "what did this skill do?". Calling out "(merged externally)" inline is fine if it's useful context, but don't invent a separate bucket for it.

## Output

- **Format:** Single grouped report at Step 6 (Done / Needs your attention / Transient buckets) with per-PR verdict + link.
- **Location:** Printed to chat; squash merges on GitHub; project board card moves to Done; atomic write to `.claude/auto-ship-queue.json`.
- **Side effects:** PR merges, board moves, queue file pruning (only `merged` and `abandoned` entries are removed).

## Example

**User says:** "Drain the queue."

**Claude does:** Reads `.claude/auto-ship-queue.json`, re-checks each PR's live state (state / mergeStateStatus / reviewDecision / CI), assigns a verdict per entry, squash-merges what's `mergeable`, attempts clean rebases for `needs-rebase`, atomically updates the queue file (prunes only terminal entries), reports per-bucket.

**Result:** Approved-and-green PRs land on `dev` in one batch; everything else stays in the queue with a fresh verdict so the user knows why.

## Recovery from partial-step failures

This skill is largely self-correcting because every invocation re-checks live PR state.

| Failure point | Symptom | Recovery |
|---|---|---|
| Step 4 squash merge succeeded, Step 5 queue write failed | PR is `MERGED` on GitHub, queue still has entry as previous status | Re-run `/auto-merge` — Step 3 sees `state == "MERGED"`, marks `merged`, prunes. |
| Step 4 rebase pushed, Step 5 queue write failed | Branch is rebased on origin, queue still says `awaiting-review` (or whatever) | Re-run `/auto-merge` after CI re-runs — Step 3 picks up the new state. |
| Step 5 atomic write itself failed | Queue is unchanged from Step 1's read | Re-run `/auto-merge` — entries get re-checked, new statuses applied. Worst case: terminal entries stay one extra cycle before pruning. |
| Step 4 squash merge failed (e.g., merge conflict appeared at the API layer) | PR is still open, status set to `merge-failed` | Investigate manually; common cause is an upstream change between Step 3 and Step 4. |

## Red flags

- Mutating PR state without first re-checking it via Step 2 → don't trust the queue's last-seen `status`; always re-query before action
- Pruning anything other than `merged` or `abandoned` → user expects to see pending entries until they're addressed
- Auto-rescheduling this skill via `/schedule` or any wake-up mechanism → no. Auto-merge is one-shot user-invoked by design. If the user wants to retry, they invoke it again.
- Auto-handling review comments inline → no. `/handle-review` exists for that, per-PR, with the user's oversight.
- Skipping Step 0 (Create tasks) when invoked from another skill → step 0's todos coexist with the parent's task list, never replace them. Same anti-skip discipline as `/ship-issue`.
- Writing the queue file directly (no `.tmp`) → a concurrent `/auto-ship` reader can observe a half-written JSON and crash

## Notes

- Designed to be the second half of an `/auto-ship` → `/auto-merge` loop. Reads `.claude/auto-ship-queue.json` written by `/auto-ship`; depends on `.claude/scripts/queue-io.js` for atomic-write semantics. Project-board Done-move expects GitHub Projects v2 single-select Status field — swap field IDs for your project.
- The "no scheduler, user-invoked only" stance is deliberate. Earlier drafts polled CI in a background loop; that turned out to waste credits and confused the user about what was running when. This skill is now strictly one-shot — the user invokes it whenever they want a fresh drain.
- Self-healing across invocations: every run re-checks live state, so a failed queue-write last run will be corrected the next time the skill runs.
