---
name: auto-ship
description: "Autonomous issue-to-PR pipeline. Auto-picks eligible Todo items (or a passed subset), classifies into quick-fix / clear-scope / ambiguous, ships everything non-ambiguous into reviewable PRs, records each in a merge queue, and stops at PR open."
version: 1.0.0
author: Varun U
email: varun@zysk.tech
category: engineering-practice
tags:
  - github-issues
  - autonomous
  - pr-creation
  - project-board
  - workflow
product: tms
sprint: 4
tested_with: claude-opus-4-7
user-invocable: true
---

# Auto-Ship

> Autonomous issue-to-PR execution. Resolves a list of issues (either explicitly passed by the user, or auto-picked from project #18's Todo column), implements each one, opens PRs, records them in the merge queue, and stops. **No autonomous merging** — the user reviews PRs in their own time and invokes `/auto-merge` when they want to drain the queue.

**Two invocation modes:**

| Mode | Trigger | What it does |
|---|---|---|
| **Auto-pick** (default) | `/auto-ship` (no args) | Drains all eligible Todo items in priority order |
| **Explicit batch** | `/auto-ship 2780 2779 2768` | Ships only the named issues (surgical override) |

**Pre-condition:** All issues must be pre-scoped. Items reach Todo via `/triage-issues`, which is the upstream gate for "labels are right + ready to be worked." Ambiguous issues found at the body-content level are skipped individually with a `status: needs investigation` label — the rest of the batch continues.

**REQUIRED BASE SKILL:** `ship-issue`

## When to use

- User asks to autonomously ship pre-scoped issues without checkpoints
- User wants to drain the Todo column overnight / unattended
- User passes a surgical subset (`/auto-ship 2780 2779`) they've already chosen

### When NOT to use

- Issues aren't triaged yet → run `/triage-issues` first
- You want to *see* the plan before shipping → `/backlog-burn-down`
- You want to handle one issue interactively → `/ship-issue N`
- You want to merge approved PRs → `/auto-merge`

## Steps

### Step 1 — Create tasks

**MANDATORY.** TaskCreate for each step below. Mark `in_progress` before starting, `completed` when done.

### Step 2 — Resolve issue list and stale-check

#### 2a — Resolve the list of candidate issues

**If the user's invocation includes one or more issue numbers** (e.g., `/auto-ship 2780 2779 2768`): use exactly that list. Skip to 2b.

**Otherwise (no args):** auto-pick from project #18's Todo column. Run a single GraphQL query for everything needed (current Status, labels, assignees, title, body, project item ID, last-update time):

```bash
gh api graphql -f query='
query {
  organization(login: "zyni-ai") {
    projectV2(number: 18) {
      items(first: 200) {
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
              number
              title
              body
              url
              state
              updatedAt
              assignees(first: 10) { nodes { login } }
              labels(first: 20) { nodes { name } }
            }
          }
        }
      }
    }
  }
}'
```

Filter the result client-side to **eligible** items only:

| Eligibility rule | Why |
|---|---|
| Project Status = `Todo` | Backlog isn't ready; In Progress is already in flight |
| Issue state = `OPEN` | Closed issues don't ship |
| Has at least one `type:*` label | Without a type, classification is unreliable |
| Has at least one `priority:*` label | Without a priority, ordering is undefined |
| Does NOT carry `status: needs investigation` | The 3a short-circuit would skip this anyway; filter early so it doesn't pollute the preview |
| Does NOT carry `status: blocked` | Waiting on external — can't ship |
| Assignees list is empty OR includes `@me` (regardless of who else is on it) | Don't steal teammates' work, but do honor pair-assigned items where @me is one of the assignees |

Sort the eligible list by:

1. **Priority ascending:** `priority: critical` (0) → `priority: high` (1) → `priority: medium` (2) → `priority: low` (3)
2. **Within priority, oldest `updatedAt` first** — prevents stale items from starving

To resolve `@me` to a GitHub login (so the assignee filter works), run once at the start: `gh api user --jq '.login'`.

**If the eligible list is empty after filtering:** print `Nothing to ship — Todo column has no eligible items. Run /triage-issues to promote Backlog items, or check existing Todo items for missing labels / blocked status.` and exit cleanly. Do not proceed to Steps 3–7 with an empty list.

#### 2b — Stale-check the resolved list

For each candidate (whether from explicit args or auto-pick), confirm the issue still describes a real problem in the current codebase:

- Use the **Grep tool** (not a Bash grep command) to search for the identifier from the issue title across `src/**/*.ts` and `src/**/*.tsx`. The CLAUDE.md instructs agents to use the Grep tool, not the Bash `grep` command.
- If no clear identifier can be extracted from the issue title (e.g., "Fix incorrect redirect after login"), skip the existence check and proceed to classification.
- Check if already fixed: `git log -S "<identifier>" origin/dev --oneline | head -5` — only run this when an identifier exists.

If stale: close with a verification comment, skip.

```bash
gh issue close <N> --repo zyni-ai/tms-app \
  --comment "Closing as stale — the referenced code no longer exists on origin/dev."
```

#### 2c — Print the resolved batch (informational, non-blocking)

After resolution but before any work, print one line summarizing what will be shipped this run:

```
Auto-ship: 4 issues picked from Todo (priority order)
  #2780 (P1 high, type: bug, security)   — TTS Streaming Aborted During Interview
  #2779 (P1 high, type: bug, security)   — Voice Interview – Video Upload 413
  #2768 (P2 medium, type: tech-debt)     — replace console.warn/error with Sentry
  #2725 (P3 low, type: enhancement)      — discuss: should features/skills/ grow?
Starting now.
```

This is **not** a confirmation gate — execution continues immediately to Step 3, no further prompts. The line exists so the user can Ctrl-C if something looks wrong, and so the run is auditable in the transcript. The list is also provisional: live state is re-checked per issue at Step 5 pre-flight, and any item lost to a race appears in the final report's race-lost section. For explicit-batch mode, print the same shape but label the source: `Auto-ship: 3 issues from explicit args`.

### Step 3 — Classify each issue

For each candidate, evaluate in this order. **First match wins** — the label short-circuit fires before re-reading the body, so previous ambiguity verdicts persist until a human resolves them.

#### 3a — Short-circuit on existing ambiguity verdict

If the issue carries the `status: needs investigation` label, a previous `/auto-ship` (or human triage) already classified it ambiguous. Do **not** re-read the body — skip immediately:

> "Issue #N already flagged ambiguous (`status: needs investigation`). Run `/decision-brief` to clarify, then remove the label. Continuing with remaining issues."

This is a cheap optimization (no body parse) and means the human's "I cleared this" signal is removing the label, not editing the body.

#### 3b — Otherwise, classify by reading the body

| Track | When |
|---|---|
| `quick-fix` | 1–2 line change, obvious, no design decisions |
| `clear-scope` | Explicit fix, scope is obvious, needs a plan to execute |
| `ambiguous` | Unclear requirements or multiple valid approaches |

#### 3c — On ambiguous: write back the verdict, then skip

When this run newly classifies an issue as ambiguous, **persist the verdict on the issue** before skipping:

```bash
gh issue edit <N> --repo zyni-ai/tms-app --add-label "status: needs investigation"
```

Then skip with this message:

> "Issue #N is ambiguous — added `status: needs investigation` label so the verdict persists. Run `/decision-brief` to clarify; the brief skill removes the label on completion, after which `/auto-ship` will pick the issue up next run. Continuing with remaining issues."

Why write back: without the label, the ambiguity verdict only lives in this run's output and disappears. Persisting it means the issue itself carries the state — visible on the project board, searchable via `gh issue list --label "status: needs investigation"`, and the resolution loop closes when `/decision-brief` removes the label.

### Step 4 — Group quick-fixes by mental model

Bundle quick-fix issues that share the same mental model. Same-component fixes bundle; unrelated domain fixes do not.

**Bundle examples:**
- Two missing `aria-label` attributes → bundle (same a11y mental model)
- A missing `aria-label` + a wrong API URL → do not bundle

### Step 5 — Execute sequentially (one bundle or issue at a time)

#### Pre-flight per issue (race-safe handoff)

Step 2 resolved the candidate list at one point in time. Between resolution and execution, a parallel `/auto-ship` invocation, a teammate, or a Ctrl-C'd previous run could have changed the issue's state. Before invoking `/ship-issue` for any candidate, re-read the issue's live state and confirm it's still ours to take:

```bash
gh api graphql -f query='
{
  repository(owner: "zyni-ai", name: "tms-app") {
    issue(number: <N>) {
      assignees(first: 5) { nodes { login } }
      projectItems(first: 5) {
        nodes {
          fieldValues(first: 20) {
            nodes {
              ... on ProjectV2ItemFieldSingleSelectValue {
                field { ... on ProjectV2SingleSelectField { name } }
                name
              }
            }
          }
        }
      }
    }
  }
}'
```

Skip the issue and add it to the "race-loss" list if **any** of:

- Project Status is no longer `Todo` (already moved to `In Progress` by another run)
- Assignees do not include `@me` (e.g., a teammate took it solo and @me was removed)
- The issue is now closed

Pair-assigned items where `@me` is one of multiple assignees are **fine** — the rule is "is @me still on this," not "is @me the only one." Mirrors the Step 2a eligibility rule.

Only when all three checks pass: invoke `/ship-issue`, which will move the board card `Todo → In Progress` as part of its own track step 3. That mutation is the visible commit-of-claim — once it lands, no other parallel run can take this issue.

#### Per-issue execution

For each bundle or issue that passed pre-flight, **invoke `/ship-issue` and run its track from step 1 through the final step.** The per-track todos created at step 2 of `/ship-issue` are *in addition to* the parent task list this skill created in Step 1 — not in place of it. Both lists coexist: the parent tracks the auto-ship pipeline; each `/ship-issue` invocation tracks that issue's own discipline guards (self-review, simplify, verify).

#### Quick-fix bundle

Run `/ship-issue` quick-fix track (steps 1–9). **Override: skip step 9 only** — `🛑 Report to user`, the final user-facing stop. Steps 1–8 are mandatory, including step 1 (first-principles) and step 2 (create per-track tasks).

Worktree: shared `.worktrees/quick-fixes`, new branch off `origin/dev` per bundle. The worktree is reused across runs, so reset it cleanly before branching. Run this idempotent sequence (substitute the absolute repo-root path on Windows):

```bash
# 1. Ensure the worktree exists. No-op if a previous run already created it.
if ! git -C ".worktrees/quick-fixes" rev-parse --git-dir >/dev/null 2>&1; then
  git worktree add .worktrees/quick-fixes origin/dev
fi

# 2. Refresh and verify the worktree is clean. Abort if a prior run left
#    uncommitted changes — do not silently nuke them.
git -C ".worktrees/quick-fixes" fetch origin dev
[ -z "$(git -C '.worktrees/quick-fixes' status --porcelain)" ] || {
  echo "Worktree .worktrees/quick-fixes is dirty — manual cleanup needed before auto-ship can continue."
  exit 1
}

# 3. Detach onto the freshly-fetched origin/dev so the previous bundle's
#    branch is released, then create this bundle's branch.
git -C ".worktrees/quick-fixes" checkout origin/dev
git -C ".worktrees/quick-fixes" checkout -b fix/<descriptive-name>
```

All fixes for this bundle land in one PR.

#### Clear-scope issue

Run `/ship-issue` clear-scope track (steps 1–14). **Override: skip step 7 only** — `🛑 Present scope + plan` checkpoint. Proceed directly from step 6 (plan self-review) to step 8 (implement) without user approval. Steps 1–6 and 8–14 are mandatory, including step 1 (first-principles), step 2 (create per-track tasks), and step 5 (plan via `superpowers:writing-plans`).

The plan artifact produced by `superpowers:writing-plans` at step 5 is canonical — keep it on disk. The step-2 todos remain coarse track-step trackers; add extra todos to mirror plan phases if you want finer tracking, but do not collapse the plan into todos. The plan document persists across context resets; the todo list does not.

Worktree (overrides `/ship-issue` clear-scope step 4's "shared or dedicated" choice — auto-ship always uses **dedicated**):
```bash
git worktree add .worktrees/<branch-name> -b fix/<branch-name> origin/dev
```

One PR per issue.

**Both tracks after implementation:** self-review → simplify → verify → rebase → push → open PR → board `In Progress → In Review`.

### Step 6 — Write queue entry (atomic write)

After `gh pr create` returns the PR number, append the new entry atomically to `.claude/auto-ship-queue.json`. The queue is a list of PRs awaiting the user's review and a future `/auto-merge` invocation.

The entry schema:

```json
{
  "issueNumbers": [<N>],
  "prNumber": <PR number>,
  "branch": "<branch name>",
  "repo": "<owner>/<name>",
  "track": "quick-fix|clear-scope",
  "status": "queued",
  "pushedAt": "<ISO 8601 timestamp>"
}
```

`status: "queued"` is the initial state for every entry — it signals the PR is open and `/auto-merge` has not yet evaluated it. `/auto-merge` re-checks live PR state on every invocation and transitions entries through `merged` / `ci-failed` / `awaiting-review` / `changes-requested` / `needs-rebase-manual` / `rebased` / `abandoned` etc. based on what it finds at drain time. (`queued` is deliberately distinct from `awaiting-review`: the latter is `/auto-merge`'s verdict for `reviewDecision == REVIEW_REQUIRED`, the former just means "not yet evaluated".)

`repo` is included so `/auto-merge` can query each PR without hardcoding `--repo`. Defaults to `zyni-ai/tms-app` for this project.

Use the shared `.claude/scripts/queue-io.js` helper — it handles `.tmp` + rename for the write step (so a concurrent reader can never observe a torn JSON file), file-missing initialization, and required-field validation in one call. Calling it instead of inlining a `node -e` block keeps both `/auto-ship` and `/auto-merge` consistent on the queue contract:

```bash
node .claude/scripts/queue-io.js append \
  "<absolute-queue-path>" \
  '{
    "issueNumbers": [<N>],
    "prNumber": <PR number>,
    "branch": "<branch name>",
    "repo": "zyni-ai/tms-app",
    "track": "quick-fix",
    "status": "queued",
    "pushedAt": "<ISO 8601 timestamp>"
  }'
```

The script auto-creates the queue file with `{ "created": "<ISO timestamp>", "entries": [] }` if it doesn't exist, then appends. Reads fresh on every invocation so concurrent `/auto-merge` runs that pruned terminal entries don't get clobbered. Exits non-zero on any unexpected failure (bad JSON, fs error) so the caller sees hard failures.

**On Windows, use forward slashes** in the absolute path (e.g., `D:/Code/tms-app/.claude/auto-ship-queue.json`, not `D:\Code\tms-app\...`). Git Bash, node, and `gh` all accept forward-slash absolute paths; backslashes break shell quoting and the `.tmp` rename inside the script.

### Step 7 — Report and stop

List each opened PR (number + URL) and the corresponding issue numbers, plus any items skipped this run due to ambiguity. Tell the user the queue file is ready and `/auto-merge` will drain it when invoked. **Do not schedule anything; do not invoke `/auto-merge` automatically.**

**Final report format:**
> "Auto-ship complete. N PRs opened, all `queued`:
> - #PR1 — <URL> — closes #ISSUE_A
> - #PR2 — <URL> — closes #ISSUE_B, #ISSUE_C (bundle)
> ...
>
> Skipped this run — ambiguous (M items, need `/decision-brief`):
> - #ISSUE_X — <title>
> - #ISSUE_Y — <title>
>
> Skipped this run — race lost (K items, picked up by another run):
> - #ISSUE_Z — Status moved to `In Progress` between resolution and pre-flight
>
> Review the PRs at your own pace. When you're ready to merge approved ones, run `/auto-merge` to drain the queue."

Either skipped section is omitted when its count is zero. The race-lost section is rare in single-user single-session use — surface it anyway so an unexpected appearance flags accidental concurrent runs to investigate.

Surfacing skipped items every run prevents the "stuck forever" failure mode where the user labels-and-forgets. To audit at any time outside an `/auto-ship` run:

```bash
gh issue list --repo zyni-ai/tms-app --label "status: needs investigation" --state open
```

Then exit.

## Output

- **Format:** N opened PRs (one per issue or bundle), each appended to `.claude/auto-ship-queue.json` as a `queued` entry; final report at Step 7 lists PR URLs + ambiguous skips + race-loss skips.
- **Location:** GitHub PRs + local `.claude/auto-ship-queue.json` + project board status moves.
- **Side effects:** branches on origin, issue-self-assignment, board card moves (Todo → In Progress → In Review), `status: needs investigation` labels on newly-classified ambiguous items.

## Example

**User says:** "Drain Todo."

**Claude does:** Paginates project Todo items, filters eligible, prints provisional batch, classifies each (label short-circuit + body parse), groups quick-fixes by mental model, pre-flight-checks each candidate's live state, invokes `/ship-issue` per bundle/issue, atomically appends queue entry per PR opened, reports.

**Result:** N PRs opened in priority order, M ambiguous items labelled and skipped, queue ready for `/auto-merge` when the user wants to drain it.

## Recovery from partial-step failures

This skill is not self-healing — a PR that exists on GitHub but is missing from the queue will never be picked up by `/auto-merge`. Document and recover:

| Failure point | Symptom | Recovery |
|---|---|---|
| Worktree commit succeeded, `gh pr create` failed | Local branch has commits, no PR | Re-run `gh pr create` from the worktree; on success, manually run the Step 6 atomic-append snippet with the new PR number |
| Step 6 queue append failed after `gh pr create` succeeded | PR exists on GitHub, no queue entry | Re-run the Step 6 `node .claude/scripts/queue-io.js append` command with the PR number from the failed run's `gh pr create` output. Without the entry, `/auto-merge` will never see this PR. |

## Red flags

Grouped by phase so you can scan quickly when reading mid-flight. Each entry is a "stop and reconsider" signal — if you catch yourself doing the left-hand thing, stop.

### Resolution & setup (Steps 1–2)

- Starting implementation before creating tasks → stop, create tasks first
- Adding eligibility filters in Step 2a that aren't grounded in the rules → the table is the spec. Don't invent "skip if title contains 'WIP'" or similar — if the user wants additional filters they pass explicit issue numbers
- Treating Step 2c as a confirmation gate → it's an informational line. Don't wait for input; execution continues immediately. The user has Ctrl-C if needed
- Auto-picking an issue assigned to a teammate → the eligibility filter excludes assignees that aren't `@me`. Don't override this — taking work from a teammate creates merge conflicts and human friction

### Classification (Step 3)

- Classifying an issue as ambiguous and *not* writing back the `status: needs investigation` label → the verdict only lives in this run's output and disappears. Without the label, you (or future-you) won't know which issues need a `/decision-brief` until you grep the agent transcript. Always persist.
- Re-classifying a `status: needs investigation` issue by re-reading the body → no. The label IS the verdict. Trust it until a human resolves it (the resolution signal is `/decision-brief` removing the label).

### Execution (Step 5)

- Stopping to show the plan to the user for clear-scope issues → skip it, execute internally
- Asking for user approval at any point during shipping → this skill is checkpoint-free by design until PR open

### Queue & report (Steps 6–7)

- Writing queue entry before PR number is confirmed → `gh pr create` output gives the URL; parse the number from it
- Overwriting an existing queue file → always go through `.claude/scripts/queue-io.js append` (it reads fresh, appends, writes via `.tmp` + rename)
- Inlining a `node -e` block instead of calling the script → a concurrent `/auto-merge` reader can observe a half-written JSON and crash; the script's atomic write is the contract
- Treating Step 6 as fire-and-forget → if it fails after `gh pr create`, the PR is invisible to `/auto-merge` forever; see Recovery table above
- Auto-invoking `/auto-merge` after Step 6 → no. The user explicitly invokes `/auto-merge` after reviewing PRs. Auto-ship's job ends at PR open.

### Output presentation (every step)

These apply across every phase whenever you produce user-facing output (plan walk-throughs, final reports, error explanations, etc.).

- Citing memory fragment keys (`feedback_*`) by name in the output → no. Memory keys are internal references the user doesn't read. Embed the rule directly in your prose instead. **Bad:** "out of scope, file follow-up per `feedback_best_practice_file_issue` memory note." **Good:** "out of scope — file a follow-up issue rather than tucking the deferral into the PR body." The agent applies the rule; the user reads the application.
- Compressing the post-implementation step chain into a one-line arrow summary when planning or dry-running → no. The user is verifying that each discipline step is part of your plan, not just listed. Describe each one distinctly: which reviewers run and what each looks for, what `/simplify` examines, the exact verify commands (`tsc`, `lint`, `format:check`, `test:run`), the rebase/push, and **both** board moves (`Todo → In Progress` at Step 3 of the track, `In Progress → In Review` at PR open). The arrow-chain summary (`self-review → simplify → verify → rebase → push → board`) is execution-mode shorthand for the agent's own reference — not user-facing planning output.

## Notes

- Deeply coupled to TMS infrastructure: `organization(login: "zyni-ai")`, `projectV2(number: 18)`, `zyni-ai/tms-app` repo, `.claude/auto-ship-queue.json` file, `.claude/scripts/queue-io.js` helper. Swap all of these for your project's equivalents.
- Pairs with `/ship-issue` (the per-issue executor), `/decision-brief` (the ambiguity-loop closer), `/auto-merge` (the queue drainer), and `/triage-issues` (the upstream Backlog → Todo gate).
- The `status: needs investigation` label is the persistence mechanism for ambiguity verdicts — it's how a half-shipped batch's ambiguity skips survive across runs. Don't remove this without replacing the persistence mechanism.
