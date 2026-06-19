---
name: handle-review
description: "Triages PR review comments (human or bot), classifies each as valid/invalid/needs-human, fixes what's valid in one batch, replies with evidence for the rest, and pushes once."
metadata:
  version: 1.0.0
  author: Varun U
  email: varun@zysk.tech
  category: engineering-practice
  tags:
    - pr-review
    - code-review
    - github
    - triage
    - workflow
  product: tms
  sprint: 4
  tested_with: claude-opus-4-7
  user-invocable: true
---

# Handle Review

> Validate every PR review comment before touching code. Classify, fix what's valid, push back on what's not, push once.

**Root problem:** reacting to comments one-by-one creates a fix → re-review → fix loop. Triage first, act once.

**REQUIRED BACKGROUND:** `superpowers:receiving-code-review`

## When to use

- PR has new review comments (Claude auto-review, CodeRabbit, Copilot, humans)
- Before implementing ANY review suggestion, even if it looks obviously right
- To break out of a fix → re-review → fix loop
- To validate auto-review claims that seem off

## Steps

### Step 0 — Create tasks

**MANDATORY.** TaskCreate for each step (1–8). Mark `in_progress`/`completed`.

### Step 1 — Gather comments

```bash
REPO=$(gh repo view --json nameWithOwner -q .nameWithOwner)
# Issue-level comments (where Claude auto-review posts)
gh pr view <N> --json comments,reviews
# Inline review comments (file:line specific) — `in_reply_to_id` lets us
# detect threads where the PR author already replied (i.e., already handled
# in a prior /handle-review run).
gh api "repos/$REPO/pulls/<N>/comments" --paginate
```

**Auto-filter** — apply to the inline-comments list (the `pulls/<N>/comments` endpoint result; not issue-level comments, which lack `in_reply_to_id` and post fresh per round anyway, so they don't need this filter).

First resolve the PR author and pre-compute the "already replied to" set in one pass over the unfiltered list. The order matters — if you drop the author's own comments first, you delete the very replies you need to detect prior handling.

```bash
AUTHOR=$(gh pr view <N> --json author --jq '.author.login')
```

Then, walking the unfiltered inline-comments list, build:

```
ALREADY_HANDLED = { c.in_reply_to_id  for c in inline_comments
                    if c.in_reply_to_id != null
                    AND c.user.login == AUTHOR }
```

Now drop both kinds of comments from the list:

1. The PR author's own comments (their `user.login == AUTHOR`) — replies, not review items.
2. Comments whose `id ∈ ALREADY_HANDLED` — addressed in a prior `/handle-review` run.

Why filter (2): re-running `/handle-review` after the auto-reviewer fires a second round otherwise re-classifies and re-replies to round-1 comments that didn't trigger code changes (the `invalid-*` verdicts). Step 2's staleness check naturally catches re-runs of `valid-*` verdicts (their fix changed the code, so the comment is now stale), but `invalid-*` verdicts leave code untouched — the staleness check doesn't fire, and you'd post a duplicate bot reply. The `in_reply_to_id` check fixes this without per-PR local state.

If no comments remain after both filters, report "No actionable comments" and stop.

### Step 2 — Classify (adaptive depth)

Start lightweight. Escalate only when needed.

| Layer | Tool | When |
|---|---|---|
| Scope check | `gh pr diff` — is file:line in the diff? | Every comment |
| Claim verify | `Read` + `Grep` on cited code | Every comment |
| Staleness | `git log -p -- <file>` | Code may have changed since comment |
| Bug claims | `npm run type-check`, `npx vitest <file>` | Asserts bug/type error |
| Next.js/React | `next-best-practices`, `vercel-react-best-practices` | RSC/perf claims |

**Do not trust the comment's framing.** Verify every claim with evidence.

### Step 3 — Assign verdict

| Verdict | Meaning | Action |
|---|---|---|
| `valid-in-scope` | Real issue from this PR's diff | Fix. No reply (commit is audit trail) |
| `valid-pre-existing` | Real issue in untouched code | File follow-up, reply with link |
| `valid-out-of-scope` | Real nit, unrelated to PR goal | File follow-up, reply with link |
| `invalid-stale` | Claim no longer holds | Reply with evidence |
| `invalid-wrong` | Factually incorrect | Reply with evidence |
| `invalid-overengineered` | Technically valid but YAGNI | Reply citing reasoning |
| `needs-human` | Genuine design decision | Flag with a recommended option |

### Step 4 — Present triage table and STOP

Table columns: `#`, `author`, `file:line`, `verdict`, `evidence`, `proposed action`.

🛑 **Wait for user approval before any writes.** Acceptable responses (match user intent, not exact wording):

| User says | Action |
|---|---|
| "yes" / "go" / "proceed" / "ship it" / "lgtm" | Execute Step 5 for every row in the table |
| "skip #N" / "drop the #N row" / "everything except #N" | Execute Step 5 for all rows except #N |
| "only fix #X and #Y" / "just #X" | Execute Step 5 only for the named rows |
| "change verdict on #N to <X>" / "#N is actually invalid-stale" | Re-classify the named row, then re-present the updated table |
| "for #N do <X> instead" / "fix #N differently" / "on #N, <alternative action>" | Adjust the proposed action for that row (keep verdict, change action), then re-present the updated table |
| "no" / "cancel" / "stop" / "hold on" | Exit without writes; explain what they'd need to do to resume |

For `needs-human` rows: always pick a recommended option in the table so the user can confirm or override with one word.

### Step 5 — Execute fixes + replies

**Order:** fixes → follow-up issues → PR replies.

- **Fix** `valid-in-scope` items. No replies for fixed items (avoids loop).
- **File issues** for out-of-scope items using your canonical `gh issue create` template.
- **Reply** to `invalid-*` items: `@reviewer — verdict. Evidence. /cc @claude` (omit `/cc @claude` for humans).

### Step 6 — Self-review the fix (conditional)

**When:** diff > 5 lines OR introduces new control flow OR refactors existing code.
**Skip when:** replies-only, pure comment/doc edits, trivial one-liners (e.g., `level: "warning"` → `"error"`, rename).

Run `pr-review-toolkit:code-reviewer` + `pr-review-toolkit:silent-failure-hunter` in parallel on the staged fix. Triage findings into the **same commit chain** (not a new round). If reviewers find new issues, fix them before pushing — mirror `/ship-issue`'s self-review-on-staged-fix discipline.

For diffs > 20 lines or touching > 1 file: also run `/simplify` after the reviewers. Same triage rule — fold findings into the same commit.

**At round 3+ on the same PR, simplify aggressively.** The "diff > 20 lines / > 1 file" rule above is for individual fixes. If you're at the third review round or later, run `/simplify` against the **full PR diff** (`git diff origin/dev`), not just the latest fix. Each round's narrow fix can introduce complexity that seeds the next round of findings — at round 3+ the cumulative changes are usually carrying the kind of complexity that reviewers keep flagging. Often a 20-line replacement for 100 lines of careful guards resolves multiple reviewer flags at once. That's a stronger move than patching each finding in isolation. **Simplification target:** if the full PR diff is 200 lines but could be 50, rewrite — brevity is a sign of understanding; reviewers keep finding issues because the design is too complex to hold, not because the fixes are wrong.

**Hard rule:** fix findings in one pass. Do not push, wait for bot, repeat. That's the fix → review → fix loop this skill exists to prevent.

### Step 7 — Verify + push once

- **Verify:** type-check, lint, format, tests.
- **Push once.**

### Step 8 — Report + memory

**Verdict → bucket assignment** — every verdict has exactly one bucket pair. The `valid-pre-existing` and `valid-out-of-scope` verdicts produce two artifacts (a filed issue + a PR reply with the link), so they appear in both the **Filed** and **Replied** counts. The other verdicts produce exactly one artifact, so they appear in exactly one bucket:

| Verdict | Fixed | Filed (follow-up issue) | Replied | Needs-human |
|---|---|---|---|---|
| `valid-in-scope` | ✓ |  |  |  |
| `valid-pre-existing` |  | ✓ | ✓ (link to filed issue) |  |
| `valid-out-of-scope` |  | ✓ | ✓ (link to filed issue) |  |
| `invalid-stale` |  |  | ✓ (evidence) |  |
| `invalid-wrong` |  |  | ✓ (evidence) |  |
| `invalid-overengineered` |  |  | ✓ (reasoning) |  |
| `needs-human` |  |  |  | ✓ |

```
N fixed, M replied, K filed, P needs-human
  - K of the replied items also link to filed follow-up issues
    (valid-pre-existing + valid-out-of-scope)
  - the other (M − K) replies are pushback on invalid-* verdicts
```

List the follow-up URLs after the counts so the user can audit them.

Update memory only if something non-obvious surfaced (new failure mode, reviewer hallucination pattern, repeatable anti-pattern).

## Output

- **Format:** triage table at Step 4 (file:line / verdict / evidence / proposed action), then a single squashable commit chain + follow-up issues + PR replies + Step 8 grouped counts.
- **Location:** GitHub PR + filed follow-up issues + local git commits.
- **Side effects:** code changes to the PR branch, new GitHub issues for out-of-scope findings, threaded replies on PR comments.

## Example

**User says:** "Handle the review on PR #2900."

**Claude does:** Pulls every inline + issue-level comment, filters already-handled threads, classifies each comment against the live code (Read + Grep + type-check), presents a triage table at the 🛑 gate. On "go", executes fixes in one commit chain, files follow-up issues for out-of-scope items, posts evidence replies on invalid-* items, runs local reviewers on the staged fix, verifies, pushes once.

**Result:** PR moves forward in one push instead of N pushes; reviewer-flagged items either fixed in-scope or have a linked follow-up issue; invalid claims have a documented rebuttal.

## Red flags

- Fixing without reading cited code → stop, verify
- Fixing without `gh pr diff` scope check → could be pre-existing
- Replying to items you're fixing → redundant, triggers loop
- Pushing per-comment → batch and push once
- Accepting "add try-catch / extract constant" without a failure mode → likely `invalid-overengineered`
- **Pushing a substantive fix without local self-review → stop, run step 6** (this is how adjacent issues leak to the next review round)
- Skipping self-review because "the bot already reviewed" → the bot reviews the **next** push, not the current fix. Local reviewers catch a different class of issues (silent failures, reuse gaps).
- Running `/simplify` before the reviewers → reviewers first; simplify reviewer-cleaned code.
- **More than 2 review rounds on one PR → stop fixing, start simplifying.** The pattern: each fix introduces complexity that becomes the seed for the next round of findings. Run `/simplify` on the full diff (`git diff origin/dev`), not just the latest fix. If `/simplify` surfaces a way to collapse the design, prefer that over patching individual reviewer findings — the simpler version usually resolves multiple flags at once. If `/simplify` finds nothing, escalate to the user: the design is wrong upstream of this PR, and continuing to fix at the surface won't break the loop.

### Output presentation (Step 4 triage table, Step 8 report)

- **Don't cite memory keys in user-facing output.** Names like `feedback_no_premature_toasts` are internal — the user shouldn't see them in the triage table or the report. Reference the *content* of the memory ("we agreed not to add toasts in utility functions"), not the file name.
- **Don't compress the triage table into a single block.** Each row is one comment. The user reads it row-by-row to approve, skip, or override. Collapsing rows or merging columns defeats the checkpoint — re-render the full table even if it's long.
- **Don't omit the evidence column to save space.** The "evidence" column is what makes Step 4 a real review gate vs. a rubber-stamp. Without it, the user can't tell `invalid-wrong` from a hallucination.

## Notes

- Companion skill to `/ship-issue`; references `/simplify`, `next-best-practices`, `vercel-react-best-practices`, `pr-review-toolkit:code-reviewer`, and `pr-review-toolkit:silent-failure-hunter` — swap in your project's equivalents if those aren't installed.
