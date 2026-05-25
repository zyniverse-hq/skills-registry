---
name: ship-issue
description: "Executes a single GitHub issue end-to-end on one of three tracks (quick-fix / clear-scope / ambiguous) with mandatory first-principles, self-review, simplify, verify, and board-move discipline."
version: 1.0.0
author: Varun U
email: varun@zysk.tech
category: engineering-practice
tags:
  - github-issues
  - workflow
  - pr-creation
  - code-review
  - tdd
product: tms
sprint: 4
tested_with: claude-opus-4-7
user-invocable: true
---

# Ship Issue

> Rigid per-issue execution process. **Invoke this each time you start a new issue** so the steps are fresh in context. Tracks: quick-fix, clear-scope, ambiguous.

**REQUIRED:** `superpowers:receiving-code-review` for handling reviewer feedback during self-review.

## When to use

- Starting work on a specific GitHub issue
- Picking up a Todo item from the project board
- Asked to implement / fix / ship a single issue from the backlog
- Always invoke per issue, never per batch (even when called from `/auto-ship`)

## Steps

### Track selection

Pick one track and follow it end-to-end. **Every track starts with steps 1–2 (first-principles + create-tasks)** — even when invoked from a parent skill like `/auto-ship`.

The parent's task list does not satisfy step 2 of the track. This skill's per-track todos must be created separately so the inner discipline guards (self-review, simplify, verify) cannot be skipped.

### Quick-fix track

1. **First-principles check.** Every issue is a *proposed* answer — challenge the question before implementing. Is the proposed fix the right fix? Does the file/function still exist? Does the bug still reproduce? Is there a stdlib primitive or existing dep that eliminates the need for new code? Would deletion solve this better than a fix? The right answer is often smaller than what was asked.
2. **Create tasks (MANDATORY).** TaskCreate one todo per remaining step (3–9). Mark `in_progress` before starting each, `completed` when done. **Do not collapse into the parent skill's task list — these are this track's anti-skip mechanism.**
3. In shared worktree: `git checkout -b <branch> origin/dev`. Assign issue (`gh issue edit N --add-assignee @me`). Board `Todo → In Progress`.
4. Implement. Atomic commit.
5. **Self-review:** `pr-review-toolkit:code-reviewer` + `pr-review-toolkit:silent-failure-hunter` in parallel. Triage: in-scope / out-of-scope / YAGNI. Reviewer finds a sibling pattern? Audit, bundle or file follow-up.
6. **Simplify (conditional):** run `/simplify` on the diff **if** diff > 20 lines OR touches > 1 file. Triage findings into the same commit chain. Skip for trivial one-liners.
7. **Verify:** `npx tsc --noEmit`, `npm run lint`, `npm run format:check`, `npm run test:run`.
8. Re-review gate if commits added after step 5. Rebase onto `origin/dev`. Push. Open PR. Board `In Progress → In Review`.
9. 🛑 Report to user.

### Clear-scope track

1. **First-principles check.** Same as quick-fix step 1.
2. **Create tasks (MANDATORY).** TaskCreate one todo per remaining step (3–14). **Do not collapse into the parent skill's task list.**
3. File deferrals as follow-up issues.
4. Worktree (shared or dedicated). Assign. Board `Todo → In Progress`.
5. Plan via `superpowers:writing-plans`. Scope tests proportional to blast radius.
6. Plan self-review.
7. 🛑 **Present scope + plan** (one checkpoint). Wait for approval.
8. Implement. Atomic commits.
9. **Self-review:** code-reviewer + silent-failure-hunter. Triage findings.
10. **Simplify:** run `/simplify` on the diff. Triage findings (reuse, quality, efficiency) into the same commit chain. Mandatory — this step catches a different class of issues (duplicated helpers, comment bloat, unbounded loops) than the reviewers.
11. **Verify:** type-check, lint, format, tests.
12. Re-review gate. Rebase, push, PR, board `In Progress → In Review`.
13. Update memory if something non-obvious surfaced.
14. 🛑 Report.

### Ambiguous track

Same as clear-scope but with an extra checkpoint before planning.

1. **First-principles check.** Same as quick-fix step 1.
2. **Create tasks (MANDATORY).** TaskCreate one todo per remaining step (3–8). **Do not collapse into the parent skill's task list.**
3. File deferrals.
4. 🛑 **Scope checkpoint** — invoke `/decision-brief` to produce a structured brief (problem, approach, alternatives, risks, scope boundary). Saves to `docs/decisions/`. Get approval before investing in implementation.
5. Worktree, assign, board.
6. Plan + self-review.
7. 🛑 **Plan review** (second checkpoint).
8. Implement → self-review → **simplify** → verify → push → PR → board → memory → 🛑 report.

### Rules

- **Never skip self-review or verification** — even for 1-line changes.
- **Board moves are mandatory** — Todo → In Progress (at start), In Progress → In Review (at push). Use paginated GraphQL queries.
- Fix all review findings in one pass, push once.
- Best practice but out of scope? File a follow-up issue.
- When implementing, use `next-best-practices` and `vercel-react-best-practices` for Next.js/React code.
- When re-review lands with comments, invoke `/handle-review` to process them.

## Output

- **Format:** A merged PR plus the report shape below; atomic commits; follow-up issues filed for out-of-scope work.
- **Location:** GitHub PR + filed follow-up issues + project board status moves.
- **Side effects:** new branch on origin, project-board card moves (Todo → In Progress → In Review), self-assignment, follow-up issues for out-of-scope findings.

### Report shape

Each track ends at the 🛑 Report step. Use this shape so the user can scan a single ship-issue run quickly and so reports are consistent across runs:

```
Shipped #<N> as PR #<M> — <PR URL>
Track: quick-fix | clear-scope | ambiguous
Branch: <branch-name>
Worktree: .worktrees/<dir>

Follow-ups filed (K):
  - #<F1> — <title> — <reason: out-of-scope / pre-existing / deferral>
  - #<F2> — ...

Pre-existing issues surfaced (P):
  - <one-line description, file:line> — not filed (e.g., already-tracked)
  - ...

Memory updates: <none / one-line summary if a non-obvious lesson surfaced>
```

Omit a section when its count is zero. Bundle PRs (multiple issues in one branch) repeat the `Shipped` line per issue closed and use the same PR URL.

## Example

**User says:** "Ship issue #2779 — voice interview video upload 413."

**Claude does:** Runs the clear-scope track: first-principles check on the issue body, creates per-track todos, files deferrals, opens a worktree, plans via `superpowers:writing-plans`, gets scope approval at the 🛑 gate, implements, self-reviews with code-reviewer + silent-failure-hunter, runs `/simplify`, verifies (tsc / lint / format / tests), rebases, pushes, opens PR, moves the board card, reports.

**Result:** One PR per issue with verified implementation, consistent commit-chain hygiene, no skipped discipline guards.

## Recovery from partial-step failures

This skill is not self-healing the way `/auto-merge` is — a half-shipped issue needs explicit recovery. Document and act:

| Failure point | Symptom | Recovery |
|---|---|---|
| Implement step succeeded, self-review (step 5/9) failed mid-run | Worktree has commit, reviewer subagent crashed or timed out | Re-run the reviewers from the worktree CWD (`pr-review-toolkit:code-reviewer` + `silent-failure-hunter`); fold findings into the same commit chain. No need to redo the implement step. |
| Push succeeded, `gh pr create` failed | Branch is on origin, no PR | Re-run `gh pr create` from the worktree. Then run the In Review board move (the track's penultimate sub-step). |
| `gh pr create` succeeded, board move failed | PR exists, board still says `In Progress` | Re-run only the `In Progress → In Review` mutation (per your project board ops doc). The PR is already up; this is just the visible-state catch-up. |
| Reviewer-stage commits exist, never pushed | Worktree has unpushed commits past step 5 | Run verify (`tsc`, `lint`, `format:check`, `test:run`), rebase, push, open PR, board move. Resume the track from step 7-onward. |

The general recovery rule: **inspect the worktree first** (`git -C <wt> status`, `git -C <wt> log origin/dev..HEAD`), identify which step's output is already on disk or on origin, and pick up from the next step. Don't redo earlier steps unless you actually need their output.

## Red flags — you're skipping a step

- Editing code before creating tasks → stop, create tasks first (track step 2)
- Pushing without running reviewers → stop, run self-review
- Pushing a non-trivial diff without `/simplify` → stop, run it
- Pushing without type-check/lint/format/tests → stop, run verify
- Starting implementation without board move → stop, assign + board first
- Merging reviewer suggestion without verifying the claim → stop, use `/handle-review`
- Ordering `/simplify` **before** self-review → stop, self-review first (simplify on reviewer-cleaned code, not on unreviewed work)
- **Invoked from `/auto-ship` and reasoning "tasks already exist in the parent's list, skip step 2"** → no. The parent's list tracks parent steps; track step 2 creates per-track todos that gate inner discipline. Both lists must coexist.
- **A changed line can't be traced to the user's request** → stop. Either the change is out-of-scope (file a follow-up issue) or you've lost sight of the goal (re-read the issue).

## Notes

- Companion skill to `/decision-brief`, `/handle-review`, `/auto-ship`, `/auto-merge`. References `superpowers:writing-plans` and `superpowers:receiving-code-review` — both are part of the official `superpowers` plugin and load alongside this skill.
- The project-board move commands assume the canonical "GitHub Projects v2 single-select Status field" pattern; field IDs are project-specific. Swap in your project's option IDs.
- `next-best-practices` and `vercel-react-best-practices` are optional helpers — skip the references if your project isn't Next.js/React.
