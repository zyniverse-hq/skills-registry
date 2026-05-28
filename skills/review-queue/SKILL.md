---
name: review-queue
description: "Read-only digest of open PRs where you're a requested reviewer. Classifies each by readiness (ready-to-approve / needs your attention / waiting / stale) with one-line factual summaries, and stops — never approves, never comments. Use whenever the user asks what PRs are waiting on them, wants to triage their review queue, or says 'show me my reviews'."
version: 1.1.0
author: Varun U
email: varun@zysk.tech
category: engineering-practice
tags:
  - github-pr
  - code-review
  - triage
  - workflow
  - digest
tested_with: claude-opus-4-7
user-invocable: true
---

# Review Queue

> Read-only digest of incoming review work. Find every open PR where you're a requested reviewer, classify each by readiness to approve, and produce a single grouped digest the user can scan in under a minute.

**This skill takes no actions on PRs** — no `gh pr review`, no comments, no approvals. It surfaces what's waiting and the user acts in their own time.

## When to use

- "What PRs are waiting on me?" / "Show me my review queue" / "Triage my reviews" / "Go through the PRs where I'm the reviewer"
- Start of the day, after lunch, end-of-week — whenever the user wants to clear the review backlog
- Before a focus block, to know what they can knock out quickly vs. what needs deep attention

### When NOT to use

- The user is handling comments on their **own** PR → `/handle-review`
- The user wants to **act on** a PR (write a review, post a comment, approve) → do it directly with `gh pr review`; this skill is digest-only
- The user wants a deep code review of a single PR → `pr-review-toolkit:review-pr`

## Operating principle

The user retypes the same review-triage prompt repeatedly. The value of this skill is **consistent classification** + **factual summaries**. That means:

- Same criteria fire the same verdict every run (no drift between Tuesday and Friday).
- Summaries describe *what changed*, not *how exciting it is*. Editorial framing ("this delights users", "unlocks X") is reviewer hallucination unless the PR description literally says it. Stick to the diff and the PR body.

## Steps

### Step 0 — Create tasks

**MANDATORY.** TaskCreate one todo per remaining step (1–4). Mark `in_progress`/`completed`. Don't skip steps — each one feeds the next.

### Step 1 — Fetch PRs awaiting your review

Run the bundled collector. Resolve its absolute path from the skill's own directory so it works regardless of which repo the user invokes the skill from:

```bash
SKILL_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
python3 "$SKILL_DIR/scripts/fetch_review_queue.py" --pretty
```

The script resolves `@me` — your authenticated GitHub login — once at the start via `gh api user --jq '.login'`. This login is used throughout:

- **Search filter:** `gh search prs --review-requested "@me"` returns only PRs where you are a requested reviewer
- **Own-PR filter:** drops any PR where `author.login == @me` (defense-in-depth against false positives)
- **`youAlreadyReviewed` field:** checks whether `@me` has already submitted a review on each PR — if true and the author hasn't pushed since, the verdict becomes `awaiting-author`

The script also gathers all per-PR state needed for classification: CI rollup, unresolved review threads, latest Claude auto-review comment body, and closing issue references.

If the script exits non-zero, print the last stderr line and offer to let the user enter PRs manually.

If the filtered list is empty: print `No PRs in your review queue right now.` and exit cleanly.

The output JSON includes `repo`, `me` (the resolved login), and a `prs` array — keep this in context through Step 3.

### Step 2 — Classify each PR

Read `references/verdict-matrix.md` for the full verdict matrix, auto-review comment classifier, and bucket mapping.

Apply the verdict matrix to each PR. Verdicts are evaluated in order — first match wins. The key fields from the script output that drive verdicts:

- `ciFailing` / `ciRunning` — CI state
- `youAlreadyReviewed` — `@me` already submitted a review and author hasn't pushed since
- `unresolvedThreads` — count of unresolved inline review threads
- `latestClaudeComment` — prose body of the last auto-review comment (`null` if bot hasn't run yet)
- `updatedAt` — for stale detection (> 7 days with no activity)

### Step 3 — Build factual summaries

Read the Factual Summary Guidelines in `references/verdict-matrix.md`. For each PR, construct a one-line summary from: type/scope (from title), diff size, closing issues, author. Quote the PR description if it has a clear "why now" — don't paraphrase.

### Step 4 — Present digest and STOP

Output a single grouped digest. Lead with what the user can act on fastest.

```
Review queue — N PRs awaiting your review (as of <date>)
========================================================

READY TO APPROVE (N) — your spot-check is the last gate
-------------------------------------------------------
#PR1  <one-line summary>
       <pr URL>

NEEDS YOUR ATTENTION (N) — read before approving
------------------------------------------------
#PR3  auto-review-flagged    <one-line summary>
       Concerns: <one-line snippet from auto-review>
       <pr URL>
#PR4  unresolved-threads     <one-line summary>
       <N> open threads — see PR for details
       <pr URL>

WAITING (N) — not ready for you yet
-----------------------------------
#PR5  ci-running          <one-line summary>
       <pr URL>
#PR6  ci-failing          <one-line summary>
       Author needs to fix CI first
       <pr URL>
#PR7  awaiting-author     <one-line summary>
       You reviewed; author hasn't pushed since
       <pr URL>
#PR8  pending-auto-review <one-line summary>
       Auto-reviewer hasn't run (likely path-filter — manual review needed)
       <pr URL>

STALE (N) — sitting > 7 days
----------------------------
#PR9  stale  <one-line summary>
       Last update <X> days ago — approve or ping author
       <pr URL>
```

Omit any section with zero entries. After printing, **stop** — do not invoke `gh pr review`, do not post comments, do not call other skills.

## Output

- **Format:** Grouped digest (READY TO APPROVE / NEEDS YOUR ATTENTION / WAITING / STALE) with per-PR factual summary + URL
- **GitHub mutations:** None — strictly read-only
- **No files written**

## Example

**User says:** "What's in my review queue?"

**Claude does:** Runs `fetch_review_queue.py` (resolves `@me`, fetches PRs where `@me` is a requested reviewer, gathers per-PR state), classifies each via the verdict matrix in `references/verdict-matrix.md`, builds factual summaries, prints the grouped digest.

**Result:** A scannable list sorted into action buckets — the user clicks through and acts manually.

## Recovery from partial-step failures

This skill doesn't mutate state, so most failures are recoverable by re-running.

| Failure point | Symptom | Recovery |
|---|---|---|
| Step 1 script returns empty when PRs exist | Likely auth issue | `gh auth status` to verify |
| Step 2 per-PR query times out on one PR | Some PRs have large `comments` / `reviewThreads` blobs | Re-run; the script fetches fresh state each time |
| Step 2 classifier uncertain about an auto-review comment | Bot wrote something unusual | Surface the PR under `unknown` with the raw comment quoted; let the user decide |

## Red flags

- Calling `gh pr review --approve` from this skill — auto-approval is forbidden; this skill is digest-only
- Posting a comment on a PR — the digest tells the user; they decide whether to comment
- Skipping the auto-review comment classifier and trusting `reviewDecision` — the Claude bot doesn't submit a GitHub review (`reviewDecision`); its verdict lives in prose comments only
- Treating `pending-auto-review` as a blocker — it's `WAITING`, not blocked; spec-only and docs-only PRs often skip the bot entirely and still need manual review
- Calling a PR `ready-to-approve` when `unresolvedThreads > 0` — an active human thread means there's an open conversation regardless of CI or bot status
- Omitting the PR URL on each row — the whole point is the user clicks through to act
- Surfacing PRs where `@me` is not a requested reviewer — the Step 1 filter is the contract
- Surfacing your own PRs — `author == @me` is a defense-in-depth drop in the script

## Files in this skill

- `SKILL.md` — this file
- `scripts/fetch_review_queue.py` — resolves `@me`, fetches PRs and per-PR state from GitHub, outputs JSON
- `references/verdict-matrix.md` — verdict matrix, auto-review classifier, bucket mapping, summary guidelines

## Notes

- Works with any GitHub repo — auto-detected from the current git remote at Step 1. No config needed.
- The auto-review classifier is tuned to the Claude auto-review action prose patterns. Other bots (CodeRabbit, Copilot) emit different shapes and would need their own classifier rows added to `references/verdict-matrix.md`.
- Pairs with `/triage-issues` and `/backlog-burn-down` for a full daily triage workflow.
