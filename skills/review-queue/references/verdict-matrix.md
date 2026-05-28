# Verdict Matrix & Classifier Reference

Used by Step 3 and Step 4 of `review-queue`.

---

## Verdict Matrix

Evaluated **in order**. First match wins.

| Condition | Verdict | Rationale |
|---|---|---|
| `state != "OPEN"` | `closed` | PR was closed/merged between fetch and view (race) — drop silently |
| `isDraft == true` | `draft` | Should have been filtered in Step 1; defense-in-depth |
| `ciFailing == true` | `ci-failing` | CI is red — author's job to fix before you spend time |
| `ciRunning == true` | `ci-running` | CI hasn't finished; come back when it has |
| `youAlreadyReviewed == true` AND no new push since your review | `awaiting-author` | Ball is in author's court — they haven't addressed your prior review |
| `unresolvedThreads > 0` | `unresolved-threads` | Active conversation, not ready for your final approval |
| `latestClaudeComment` parses as **flagging concerns** (see Classifier below) | `auto-review-flagged` | Read the bot's findings before approving |
| `latestClaudeComment == null` | `pending-auto-review` | Bot hasn't run yet — likely path filter excluded this PR (e.g. spec-only, docs-only) |
| `ciFailing == false` AND `latestClaudeComment` parses as **approving** AND `unresolvedThreads == 0` | `ready-to-approve` | All gates green — your spot-check is the last step |
| `updatedAt > 7 days ago` AND none of the above | `stale` | Sitting in your queue too long; approve or ask author to revive |
| Anything else | `unknown` | Surface raw state for the user to investigate |

---

## Auto-Review Comment Classifier

The auto-reviewer posts prose, not a structured field. Read the `latestClaudeComment` body and classify:

| Body contains... | Classification |
|---|---|
| Explicit positive verdict — `PR is good to merge`, `Looks good`, `LGTM`, `No concerns`, `Ready to merge` | **approving** |
| Findings under headings like `Concerns`, `Issues`, `Bugs`, `Critical`, `High severity`, `Must fix`, `Blocker`, or phrases like `worth confirming before merging` / `should fix` | **flagging concerns** |
| Mixed — minor nits but explicitly says safe to merge | **approving** (explicit verdict wins) |
| Purely informational — no verdict, no concerns | **approving** (absence of concerns reads as approval) |

This is judgment, not regex. Read the comment the way you'd read a teammate's review and ask: *would I be comfortable approving based on this?*

---

## Bucket Mapping

Every verdict maps to exactly one output bucket. If you find yourself debating placement, this table is the authority.

| Verdict | Bucket |
|---|---|
| `ready-to-approve` | READY TO APPROVE |
| `auto-review-flagged` | NEEDS YOUR ATTENTION |
| `unresolved-threads` | NEEDS YOUR ATTENTION |
| `unknown` | NEEDS YOUR ATTENTION |
| `pending-auto-review` | WAITING |
| `ci-running` | WAITING |
| `ci-failing` | WAITING |
| `awaiting-author` | WAITING |
| `stale` | STALE |
| `draft` | (filtered — not surfaced) |
| `closed` | (filtered — not surfaced) |

---

## Factual Summary Guidelines

For each PR, construct a one-line summary that captures **what changed**, not **why it's exciting**.

Include:
- **Type/scope** from the title — `fix(auth)` → "auth bug fix"; `feat(exam)` → "exam feature"
- **Diff size** — `<10` lines = "tiny"; `10–50` = "small"; `50–200` = "medium"; `>200` = "large"
- **Linked issues** — `closes: [2820]` → "closes #2820"
- **Author** — useful for knowing who to ping

**Examples:**

| PR title | Summary |
|---|---|
| `fix(observability): replace console.warn with Sentry in cleanup paths` | observability fix, small (1 file, 27/11), closes #2724, by @author |
| `feat(exam): add timer drift correction for cross-tab pauses` | exam feature, medium (3 files, 142/8), closes #2812, by @author |
| `chore(deps): bump @xmldom/xmldom (4 high-severity CVEs)` | dependency security fix, tiny (2 files, 5/13), by @dependabot |

**Anti-patterns:**
- "This will significantly improve user experience" — editorial; nothing in the diff says this
- "Critical fix for production" — unverified urgency framing
- "Cleans up technical debt" — only say this if the PR title/body literally calls it out

If the PR description has a clear "why now" statement, quote it briefly rather than paraphrasing.
