---
name: review-queue
description: "Read-only digest of open PRs where you're a requested reviewer. Classifies each by readiness (ready-to-approve / needs your attention / waiting / stale) with one-line factual summaries, and stops — never approves, never comments."
license: "Proprietary — internal use only (zysk.tech)"
compatibility: >
  Requires GitHub CLI (gh) authenticated to the target GitHub org. Designed for
  Claude Code. Defaults to zyni-ai/tms-app repo and the @zyniverse-bot reviewer
  username — swap repo and bot username before use in other projects.
metadata:
  version: "1.0.0"
  author: Varun U
  email: varun@zysk.tech
  category: engineering-practice
  tags: "github-pr, code-review, triage, workflow, digest"
  product: tms
  sprint: "4"
  tested_with: claude-opus-4-7
  user-invocable: "true"
---

# Review Queue

> Read-only digest of incoming review work. Find every open PR in `zyni-ai/tms-app` where the user (`@me`) is a requested reviewer, classify each by readiness to approve, and produce a single grouped table the user can scan in under a minute.

**This skill takes no actions on PRs** — no `gh pr review`, no comments, no approvals. It surfaces what's waiting and the user acts in their own time. Same deliberate-gate philosophy as `/backlog-burn-down`.

## When to use

- "What PRs are waiting on me?" / "Show me my review queue" / "Triage my reviews" / "Go through the PRs where I'm the reviewer"
- Start of the day, after lunch, end-of-week — whenever the user wants to clear the review backlog
- Before a focus block, to know what they can knock out quickly vs. what needs deep attention

### When NOT to use

- The user is handling comments on their **own** PR → `/handle-review`
- The user wants to merge their own PRs that have already been approved → `/auto-merge`
- The user wants to **act on** a PR (write a review, post a comment, approve) → do it directly with `gh pr review`; this skill is digest-only
- The user wants a deep code review of a single PR → `pr-review-toolkit:review-pr`

## Operating principle

The user retypes the same review-triage prompt repeatedly. The value of this skill is **consistent classification** + **factual summaries**. That means:

- Same criteria fire the same verdict every run (no drift between Tuesday and Friday).
- Summaries describe *what changed*, not *how exciting it is*. Editorial framing ("this delights users", "unlocks X") is reviewer hallucination unless the PR description literally says it. Stick to the diff and the PR body.

## Steps

### Step 0 — Create tasks

**MANDATORY.** TaskCreate one todo per remaining step (1–5). Mark `in_progress`/`completed`. Anti-skip discipline — same as the rest of the suite.

### Step 1 — Fetch PRs awaiting your review

Resolve `@me` once at the start, then list every open PR where `@me` is in the requested-reviewers list:

```bash
ME=$(gh api user --jq '.login')

gh search prs \
  --repo zyni-ai/tms-app \
  --state open \
  --review-requested "@me" \
  --json number,title,author,isDraft,updatedAt,url
```

Filter the result client-side to drop:

| Filter | Why |
|---|---|
| `isDraft == true` | Drafts aren't ready for review by definition |
| `author.login == $ME` | You can't be requested as reviewer on your own PR, but the search occasionally returns false positives — defense-in-depth |

If the filtered list is empty: print `No PRs in your review queue right now.` and exit cleanly.

### Step 2 — Gather state per PR

For each PR, gather everything the verdict matrix needs in a single per-PR query. The two pieces of state that aren't on the PR object directly:

1. **The latest Claude auto-review comment** — the bot posts a fresh comment per push, so we want the chronologically last one from the `claude` user.
2. **Linked closing issues** — what issues this PR closes, used in the factual summary.

```bash
gh pr view <prNumber> --repo "zyni-ai/tms-app" \
  --json mergeStateStatus,reviewDecision,statusCheckRollup,state,isDraft,additions,deletions,changedFiles,title,body,author,headRefName,updatedAt,closingIssuesReferences,reviewThreads,comments \
  -q '{
    state,
    isDraft,
    mergeStateStatus,
    reviewDecision,
    title,
    author: .author.login,
    branch: .headRefName,
    updatedAt,
    additions, deletions, changedFiles,
    closes: [.closingIssuesReferences.nodes[]?.number],
    ciFailing: ([.statusCheckRollup[]? | select(.conclusion == "FAILURE" or .conclusion == "CANCELLED")] | length) > 0,
    ciRunning: ([.statusCheckRollup[]? | select(.status == "IN_PROGRESS" or .status == "QUEUED")] | length) > 0,
    unresolvedThreads: ([.reviewThreads.nodes[]? | select(.isResolved == false)] | length),
    youAlreadyReviewed: ([.reviews[]? | select(.author.login == "<your-login>")] | length) > 0,
    latestClaudeComment: (
      [.comments[]? | select(.author.login == "claude")] | sort_by(.createdAt) | last | .body
    )
  }'
```

Substitute `<your-login>` with the value of `$ME` from Step 1.

**Notes on each field:**
- `latestClaudeComment` — the body is prose (not a structured verdict). Step 3's classifier reads it directly. If `null`, the auto-reviewer hasn't run yet (often because the workflow's path filter — `src/**/*.{ts,tsx,js,jsx}`, `next.config.ts`, `package.json` — didn't match the PR's files; common for spec-only or docs-only PRs).
- `unresolvedThreads` — count of inline threads where `isResolved == false`. Resolved threads don't block.
- `youAlreadyReviewed` — boolean. If you've already submitted a review and the author hasn't pushed since, the PR is waiting on the author, not you.

### Step 3 — Classify each PR

Verdicts, evaluated **in order**. First match wins.

| Condition | Verdict | Rationale |
|---|---|---|
| `state != "OPEN"` | `closed` | PR was closed/merged between Step 1 and Step 2 (race) — drop |
| `isDraft == true` | `draft` | Should have been filtered in Step 1; this is defense-in-depth |
| `ciFailing == true` | `ci-failing` | CI is red — author's job to fix before you spend time |
| `ciRunning == true` | `ci-running` | CI hasn't finished; come back when it has |
| `youAlreadyReviewed == true AND no new push since your review` | `awaiting-author` | Ball is in author's court — they haven't addressed your prior review |
| `unresolvedThreads > 0` | `unresolved-threads` | Active conversation, not ready for your final approval |
| `latestClaudeComment` parses as **flagging concerns** (see classifier below) | `auto-review-flagged` | Read the bot's findings before approving |
| `latestClaudeComment == null` | `pending-auto-review` | Bot hasn't run yet; if path filter excludes (e.g., spec-only PR), surface so user can manually inspect |
| `ciFailing == false AND latestClaudeComment` parses as **approving** AND `unresolvedThreads == 0` | `ready-to-approve` | All gates green — your spot-check is the last step |
| `updatedAt > 7 days ago` AND none of the above | `stale` | Sitting in your queue too long; either approve or ask the author to revive |
| Anything else | `unknown` | Surface raw state for debugging |

#### Classifier: is the latest Claude auto-review approving?

The auto-reviewer posts prose, not a structured field. Read the body and classify:

| Body contains... | Verdict |
|---|---|
| Explicit positive verdict — `PR is good to merge`, `Summary — PR is good to merge`, `Looks good`, `LGTM`, `No concerns`, `Ready to merge` | **approving** |
| Findings under a heading like `Concerns`, `Issues`, `Bugs`, `Critical`, `High severity`, `Must fix`, `Blocker`, or framed as `worth confirming before merging` / `should fix` | **flagging concerns** |
| Mixed — the bot lists minor nits but explicitly says it's still safe to merge | **approving** (the explicit verdict wins) |
| The comment exists but is purely informational (no verdict, no concerns) | **approving** (absence of concerns reads as approval) |

The classifier is judgment, not regex. Read the comment body the way you'd read a teammate's review and ask: *would I be comfortable approving based on this?*

### Step 4 — Build the factual summary per PR

For each PR (regardless of verdict), construct a one-line summary that captures **what changed**, not **why it's exciting**. Stick to:

- **Type/scope from the title** — `fix(auth)` → "auth bug fix"; `feat(exam)` → "exam feature"; `refactor(test-runner)` → "test-runner refactor"
- **Diff size** — `<10` lines = "tiny"; `10–50` = "small"; `50–200` = "medium"; `>200` = "large"
- **Linked issues** — pull from `closes`; `closes: [2820]` → "closes #2820"
- **Author** — useful when scanning to know who to ping

**Example summaries:**

| PR title | Summary |
|---|---|
| `fix(observability): replace console.warn/error with Sentry in useTestSubmission cleanup paths` | observability fix, small (1 file, 27/11), closes #2724, by @author |
| `feat(exam): add timer drift correction for cross-tab pauses` | exam feature, medium (3 files, 142/8), closes #2812, by @author |
| `chore(deps): bump @xmldom/xmldom to 0.9.10 (4 high-severity CVEs)` | dependency security fix, tiny (2 files, 5/13), closes #(none), by @dependabot |

**Anti-patterns — don't do these:**
- "This will significantly improve user experience" — editorial; nothing in the diff or PR body says this
- "Critical fix for production" — unverified urgency framing
- "Cleans up technical debt" — only say this if the PR title/body literally calls it out

If the PR description has a clear "why now" or "value" statement, you can quote it briefly (e.g., `closes #2820 (per author: "blocks user signup on iOS Safari")`). Quote, don't paraphrase.

### Step 5 — Present digest and STOP

Output a single grouped table. The user reads top-down, so lead with what they can knock out fast.

```
Review queue — N PRs awaiting your review (as of <date>)
========================================================

READY TO APPROVE (N) — your spot-check is the last gate
-------------------------------------------------------
#PR1  <one-line summary>
       <pr URL>
#PR2  <one-line summary>
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

Omit any section with zero entries. After printing, **stop** — do not invoke `gh pr review`, do not post comments, do not call other skills. The user picks what to act on.

## Output

- **Format:** Single grouped digest at Step 5 (READY TO APPROVE / NEEDS YOUR ATTENTION / WAITING / STALE buckets) with per-PR factual summary + URL.
- **Location:** Printed to chat. No mutations to GitHub.
- **Side effects:** None — this skill is strictly read-only.

## Example

**User says:** "What's in my review queue?"

**Claude does:** Resolves `@me`, fetches every open PR where `@me` is a requested reviewer, filters drafts + own-PR false positives, gathers per-PR state (CI / mergeStateStatus / reviewDecision / unresolvedThreads / latestClaudeComment / whether you already reviewed), classifies via the 10-verdict matrix, builds factual one-line summaries, prints the grouped digest.

**Result:** A scannable list of PRs sorted into "your spot-check is the last gate" / "you need to read this first" / "not ready for you yet" / "stale" — the user clicks through and acts manually.

## Bucket assignment by verdict

Every verdict has exactly one bucket. The classifier in Step 3 produces the verdict; this table maps it to the report section. If you find yourself debating placement, this table is authority.

| Verdict | Bucket | Why |
|---|---|---|
| `ready-to-approve` | READY TO APPROVE | Your spot-check is the only thing missing |
| `auto-review-flagged` | NEEDS YOUR ATTENTION | Bot found concerns — read before approving |
| `unresolved-threads` | NEEDS YOUR ATTENTION | Active discussion |
| `pending-auto-review` | WAITING | Bot hasn't weighed in (path filter or workflow lag) |
| `ci-running` | WAITING | Wait for CI |
| `ci-failing` | WAITING | Author's turn to fix |
| `awaiting-author` | WAITING | You already reviewed; ball in author's court |
| `stale` | STALE | Aged > 7 days; revisit |
| `draft` | (filtered, not surfaced) | Should have been dropped in Step 1 |
| `closed` | (filtered, not surfaced) | Race-loss; PR closed between fetch and view |
| `unknown` | NEEDS YOUR ATTENTION | Log raw state for the user to investigate |

## Recovery from partial-step failures

This skill doesn't mutate state, so most failures are recoverable by re-running. Note the few exceptions:

| Failure point | Symptom | Recovery |
|---|---|---|
| Step 1 search returns empty when you know there are PRs | Likely token/auth issue — `gh search` needs auth | `gh auth status` to verify |
| Step 2 per-PR query times out on one PR | Some PRs have huge `comments` / `reviewThreads` blobs | Drop the heaviest fields and re-fetch only what's needed for the verdict |
| Step 3 classifier is uncertain about an auto-review comment | Edge case — bot wrote something unusual | Surface the PR under `unknown` with the raw comment quoted; let the user decide |
| Step 5 prints partial digest because Step 2 errored mid-loop | Some PRs missing | Re-run; this skill is read-only and idempotent |

## Red flags

### Action discipline (the skill is read-only)

- Calling `gh pr review --approve` from this skill → no. Auto-approval is forbidden by design — the user explicitly chose option (a) read-only digest. If they want auto-approve, they'll change the spec.
- Posting a comment on a PR ("just flagging this for you") → no. Use the digest to tell the user; they decide whether to comment.
- Invoking `/handle-review` from inside this skill → no. `/handle-review` is for *your own* PR. This skill surfaces *others'* PRs.

### Classification rigor

- Skipping the auto-review comment classifier and just trusting `reviewDecision` → no. The Claude bot doesn't submit a GitHub review (`reviewDecision`); it leaves prose comments. The whole reason for Step 3's classifier is that the verdict isn't in a structured field.
- Treating `pending-auto-review` as a blocker → no, it's `WAITING`. Some PRs (spec-only, docs-only) never get an auto-review because of the workflow's path filter. The user can still review those manually — the skill just can't lean on the bot for them.
- Calling a PR `ready-to-approve` when there are unresolved threads → no. Even if CI is green and the auto-review approved, an unresolved human thread means there's an active conversation. Surface it under NEEDS YOUR ATTENTION.

### Output presentation

These are the same Sonnet output failure modes documented across the suite — no skill is exempt:

- **Citing memory keys** in the digest (e.g., `feedback_*` filenames) → no. The user doesn't read those names. Embed the rule in your prose.
- **Compressing the digest into a single block** → no. Each PR is one row. The user reads it row-by-row to decide what to act on. Collapsing rows defeats the digest.
- **Editorial summaries** ("game-changing", "delights users") → no. Stick to factual: type, size, closes, author. The user does the value framing.
- **Omitting the PR URL on each row** → no. The whole point is the user clicks through to act. Surface the URL on every row.

### Scope discipline

- Surfacing PRs where you're not a requested reviewer → no. The Step 1 filter is the contract. If a teammate-assigned PR is interesting, that's `/backlog-burn-down`'s territory, not this skill.
- Surfacing your own PRs → no. You can't be requested-reviewer on your own PR; if Step 1 returns one, drop it (defense-in-depth filter).

## Notes

- TMS-flavored: targets `zyni-ai/tms-app` in `gh search prs --repo` and the `latestClaudeComment` author filter. Swap the repo for your project; the rest of the logic is generic.
- The auto-review classifier (Step 3 sub-table) is tuned to the prose patterns of the Claude auto-review action (`claude-code-review.yml`); other bots (CodeRabbit, Copilot) emit different shapes and would need their own classifier rows.
- This skill is the *deliberate-gate* counterpart to `/handle-review` (your-own-PR) and `/auto-merge` (own approved PRs). Together they cover all three positions on a PR (author / reviewer / merger).
