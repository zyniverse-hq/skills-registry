---
name: ship-issue
description: "Executes a single GitHub issue end-to-end on one of three tracks (quick-fix / clear-scope / ambiguous) with mandatory first-principles, self-review, simplify, verify, and board-move discipline. Includes preflight dependency validation and automatic stack detection for language-appropriate best practices. Use for one issue at a time with interactive checkpoints; for autonomous batch shipping across many issues, use auto-ship."
metadata:
  version: 2.0.1
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

---

## Preflight — run this before selecting a track

Before doing anything else, run these two checks. If either fails, stop and tell the user what is missing. Do not proceed to track selection.

### Check 1 — Required plugins

Verify the following plugins are available in the current session:

| Plugin | Used in |
|--------|---------|
| `pr-review-toolkit:code-reviewer` | Self-review step (all tracks) |
| `pr-review-toolkit:silent-failure-hunter` | Self-review step (all tracks) |
| `superpowers:writing-plans` | Clear-scope and ambiguous tracks |
| `superpowers:receiving-code-review` | Re-review gate (all tracks) |

If any plugin is missing, stop immediately and output:

```
Preflight failed — missing required plugins:
  - <plugin-name> (used at: <step>)
  - ...

Install the missing plugins before running /ship-issue.
Do not proceed until all plugins are available.
```

Do not guess or skip — a missing plugin at step 5 wastes all prior work.

### Check 2 — Stack detection

Read the project root to identify the language and framework. This determines which best practices apply when implementing.

Check these files in order, first match wins:

| File found | Stack | Best practices to apply |
|------------|-------|------------------------|
| `package.json` | Node.js | Read `dependencies` and `devDependencies`. If `next` is present → Next.js/React best practices. If `react` (no next) → React best practices. If `vue` → Vue best practices. If `express` / `fastify` / `koa` → Node.js API best practices. Otherwise → general JavaScript/TypeScript best practices. |
| `requirements.txt` / `pyproject.toml` / `setup.py` / `setup.cfg` | Python | If `django` present → Django best practices. If `fastapi` / `flask` present → apply the matching framework's conventions. Otherwise → general Python (PEP8, type hints, virtual env hygiene). |
| `pom.xml` / `build.gradle` / `build.gradle.kts` | Java / Kotlin | If `spring-boot` present → Spring Boot best practices. Otherwise → general Java/Kotlin conventions. |
| `go.mod` | Go | General Go best practices (idiomatic Go, error wrapping, context propagation). |
| `Cargo.toml` | Rust | General Rust best practices (ownership, error handling with `?`, clippy conventions). |
| `*.csproj` / `*.sln` | C# / .NET | If `Microsoft.AspNetCore` present → ASP.NET Core best practices. Otherwise → general C# conventions. |
| None of the above | Unknown | Apply general clean-code principles. Note the unknown stack in the report. |

Save the detected stack as **`<detected-stack>`**. Reference it at every implement step: "Applying `<detected-stack>` best practices."

If `package.json` exists but is unreadable or empty, treat as unknown stack.

---

## Steps

### Track selection

Pick one track and follow it end-to-end. **Every track starts with steps 1–2 (first-principles + create-tasks)** — even when invoked from a parent skill like `/auto-ship`.

The parent's task list does not satisfy step 2 of the track. This skill's per-track todos must be created separately so the inner discipline guards (self-review, simplify, verify) cannot be skipped.

### Quick-fix track

1. **First-principles check.** Every issue is a *proposed* answer — challenge the question before implementing. Is the proposed fix the right fix? Does the file/function still exist? Does the bug still reproduce? Is there a stdlib primitive or existing dep that eliminates the need for new code? Would deletion solve this better than a fix? The right answer is often smaller than what was asked.
2. **Create tasks (MANDATORY).** TaskCreate one todo per remaining step (3–9). Mark `in_progress` before starting each, `completed` when done. **Do not collapse into the parent skill's task list — these are this track's anti-skip mechanism.**
3. In shared worktree: `git checkout -b <branch> origin/dev`. Assign issue (`gh issue edit N --add-assignee @me`). Board `Todo → In Progress`.
4. Implement. Atomic commit. Apply **`<detected-stack>`** best practices from the preflight stack detection.
5. **Self-review:** `pr-review-toolkit:code-reviewer` + `pr-review-toolkit:silent-failure-hunter` in parallel. Triage: in-scope / out-of-scope / YAGNI. Reviewer finds a sibling pattern? Audit, bundle or file follow-up.
6. **Simplify (conditional):** run `/simplify` on the diff **if** diff > 20 lines OR touches > 1 file. Triage findings into the same commit chain. Skip for trivial one-liners.
7. **Verify:** run each command below. Skip gracefully if the script is not defined in the project. Fail hard if the script exists but returns a non-zero exit code.
   - `npx tsc --noEmit` — skip if no `tsconfig.json` found
   - `npm run lint` — skip if `lint` script not in `package.json`
   - `npm run format:check` — skip if `format:check` script not in `package.json`
   - `npm run test:run` — skip if `test:run` script not in `package.json`
   - For non-Node stacks, run the equivalent: `pytest` (Python), `mvn test` (Java/Maven), `gradle test` (Gradle), `go test ./...` (Go), `cargo test` (Rust), `dotnet test` (.NET).
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
8. Implement. Atomic commits. Apply **`<detected-stack>`** best practices from the preflight stack detection.
9. **Self-review:** code-reviewer + silent-failure-hunter. Triage findings.
10. **Simplify:** run `/simplify` on the diff. Triage findings (reuse, quality, efficiency) into the same commit chain. Mandatory — this step catches a different class of issues (duplicated helpers, comment bloat, unbounded loops) than the reviewers.
11. **Verify:** same rules as quick-fix step 7 — skip gracefully if script absent, fail hard if script present and exits non-zero.
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
8. Implement → self-review → **simplify** → verify → push → PR → board → memory → 🛑 report. Apply **`<detected-stack>`** best practices at the implement sub-step.

### Rules

- **Never skip self-review or verification** — even for 1-line changes.
- **Board moves are mandatory** — Todo → In Progress (at start), In Progress → In Review (at push). Use paginated GraphQL queries.
- Fix all review findings in one pass, push once.
- Best practice but out of scope? File a follow-up issue.
- Apply the best practices for **`<detected-stack>`** as identified in the preflight. Do not apply framework-specific patterns to the wrong stack (e.g., do not apply Next.js conventions to a Django project).
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
Stack detected: <detected-stack>

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

**Claude does:** Runs preflight — confirms all plugins are present, reads `package.json`, detects Next.js stack. Then runs the clear-scope track: first-principles check on the issue body, creates per-track todos, files deferrals, opens a worktree, plans via `superpowers:writing-plans`, gets scope approval at the 🛑 gate, implements using Next.js best practices, self-reviews with code-reviewer + silent-failure-hunter, runs `/simplify`, verifies (tsc / lint / format / tests — skipping any absent scripts), rebases, pushes, opens PR, moves the board card, reports with stack in the header.

**Result:** One PR per issue with verified implementation, consistent commit-chain hygiene, no skipped discipline guards, and best practices matched to the actual stack.

## Recovery from partial-step failures

This skill is not self-healing the way `/auto-merge` is — a half-shipped issue needs explicit recovery. Document and act:

| Failure point | Symptom | Recovery |
|---|---|---|
| Preflight plugin check failed | Skill stopped before track selection | Install missing plugins, then re-invoke `/ship-issue`. No worktree or branch was created. |
| Implement step succeeded, self-review (step 5/9) failed mid-run | Worktree has commit, reviewer subagent crashed or timed out | Re-run the reviewers from the worktree CWD (`pr-review-toolkit:code-reviewer` + `silent-failure-hunter`); fold findings into the same commit chain. No need to redo the implement step. |
| Push succeeded, `gh pr create` failed | Branch is on origin, no PR | Re-run `gh pr create` from the worktree. Then run the In Review board move (the track's penultimate sub-step). |
| `gh pr create` succeeded, board move failed | PR exists, board still says `In Progress` | Re-run only the `In Progress → In Review` mutation (per your project board ops doc). The PR is already up; this is just the visible-state catch-up. |
| Reviewer-stage commits exist, never pushed | Worktree has unpushed commits past step 5 | Run verify (skip absent scripts, fail on present non-zero), rebase, push, open PR, board move. Resume from step 7-onward. |

The general recovery rule: **inspect the worktree first** (`git -C <wt> status`, `git -C <wt> log origin/dev..HEAD`), identify which step's output is already on disk or on origin, and pick up from the next step. Don't redo earlier steps unless you actually need their output.

## Red flags — you're skipping a step

- Editing code before creating tasks → stop, create tasks first (track step 2)
- Skipping the preflight → stop, run preflight first — missing plugins at step 5 wastes all prior work
- Pushing without running reviewers → stop, run self-review
- Pushing a non-trivial diff without `/simplify` → stop, run it
- Pushing without running verify → stop, run it (even if some scripts are skipped)
- Starting implementation without board move → stop, assign + board first
- Merging reviewer suggestion without verifying the claim → stop, use `/handle-review`
- Applying Next.js or React patterns to a Python or Java project → stop, re-check `<detected-stack>` from preflight
- Ordering `/simplify` **before** self-review → stop, self-review first (simplify on reviewer-cleaned code, not on unreviewed work)
- **Invoked from `/auto-ship` and reasoning "tasks already exist in the parent's list, skip step 2"** → no. The parent's list tracks parent steps; track step 2 creates per-track todos that gate inner discipline. Both lists must coexist.
- **A changed line can't be traced to the user's request** → stop. Either the change is out-of-scope (file a follow-up issue) or you've lost sight of the goal (re-read the issue).

## Notes

- Companion skill to `/decision-brief`, `/handle-review`, `/auto-ship`, `/auto-merge`. References `superpowers:writing-plans` and `superpowers:receiving-code-review` — both are part of the official `superpowers` plugin and load alongside this skill.
- The project-board move commands assume the canonical "GitHub Projects v2 single-select Status field" pattern; field IDs are project-specific. Swap in your project's option IDs.
- Stack detection uses Claude's built-in knowledge of each framework's conventions — no external reference files required. If your project has internal conventions that differ from standard practices, document them in a `CLAUDE.md` file at the project root and Claude will incorporate them automatically.
