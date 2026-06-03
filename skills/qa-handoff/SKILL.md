---
name: qa-handoff
description: Use after a PR merges to dev to generate a QA test plan inlined into a new GitHub issue assigned to the named QA user. Sets the project status to "Ready for QA" and removes the issue from the auto-added project. QA reads the plan in the issue, ticks a Pass/Fail/Blocked checkbox, and closes the issue. Triggers — "QA handoff", "notify QA about this PR", "send QA test plan", "tell QA to test PR #N".
license: "Proprietary — internal use only (zysk.tech)"
compatibility: >
  Requires GitHub CLI (gh) authenticated to the target GitHub org. Designed for
  Claude Code. Defaults to zyni-ai/tms-app and the dev branch — swap repo, org,
  and branch name before use in other projects. QA assignee config stored in
  .claude/qa-handoff-config.json (gitignored).
metadata:
  version: "1.0.0"
  author: Rajashekhar V
  email: rajashekhar.v@zysk.tech
  category: qa-testing
  tags: "qa, testing, github-issues, handoff, test-plan"
  product: tms
  sprint: "3"
  tested_with: claude-sonnet-4-6
  user-invocable: "true"
  model: claude-sonnet-4-6
allowed-tools: "Bash Read Write Grep Glob TaskCreate TaskUpdate TaskGet TaskList AskUserQuestion"
---

# QA Handoff

After a PR merges to `dev`, generate a structured test plan inlined into a new GitHub issue assigned to the named QA team member. The issue is the entire handoff artifact — no separate file, no commit to dev, no download link. Body = the full plan + a 3-checkbox closing footer (Pass / Fail / Blocked). QA reads in GitHub, tests the change, ticks the matching checkbox, closes the issue. Zero typing for the Pass case.

**Delivery is via GitHub only** — no Teams, no Slack, no copy-paste, **no dev commits**.

## Supporting reference files (loaded only when needed)

- **[references/variants.md](references/variants.md)** — the 10 test-plan variant templates (loaded in Step 4.5)
- **[references/project-board.md](references/project-board.md)** — full GraphQL queries for Step 7d project operations
- **[references/edge-cases.md](references/edge-cases.md)** — arg-parsing edge cases, partial-failure handling, future non-goals
- **[references/smoke-test.md](references/smoke-test.md)** — first-run smoke test procedure for skill edits

## When to use

- A PR (or several PRs) merged to `dev` and need QA verification
- You want to sweep up everything merged recently that doesn't yet have a QA issue
- Skip this skill for `type: docs` or `type: chore` PRs — they don't need QA

## Invocation

The skill runs in one of **three modes**:

```
# Mode A — Sweep (no PR numbers): batch-file QA issues for everything that needs one
/qa-handoff                                       # last 30 merged - already-handed-off - docs/chore
/qa-handoff --dry-run                             # same, but print bodies without filing

# Mode B — Targeted (one or more PR numbers): file issues for exactly these PRs
/qa-handoff 3217                                  # one PR
/qa-handoff 3217 3220 3225                        # explicit batch
/qa-handoff 3217 --qa sarah-test                  # one PR with one-time assignee override
/qa-handoff 3217 3220 --dry-run                   # dry-run multiple PRs

# Mode C — Standalone config (no PR work, just update saved default)
/qa-handoff --qa <new-name> --set-default         # save new default; do nothing else
/qa-handoff --reset-qa                            # clear saved default; do nothing else
/qa-handoff --reset-qa --qa <name> --set-default  # atomic swap; do nothing else
```

The QA assignee is resolved **once per run** (not per-PR in batch mode), in this priority order:

1. **`--qa <name>` flag** — used for this run only (does NOT change saved default unless `--set-default` is also passed).
2. **Saved default** — read from `.claude/skills/qa-handoff/.qa-assignee.local` if present.
3. **Interactive prompt** — only if neither of the above applies (typically first-ever run). Answer is saved to the local file so future runs are silent.

In batch mode (Mode A or B with 2+ PRs), the same assignee applies to **every** issue in the batch. To assign different QA users per PR, run them individually with `--qa <name>`.

Optional flags:
- `--qa <github-username>` — one-time assignee override for this run only (whole batch).
- `--set-default` — only meaningful with `--qa`; saves the override as the new saved default. Use this when the team's QA owner changes permanently.
- `--reset-qa` — delete the saved default. Next run will prompt fresh. Can be combined with `--qa <new-name>` to atomically swap defaults.
- `--dry-run` — generate the body/bodies + print the proposed issue(s). No issues created, no project boards touched.

**Design rationale:** Sweep mode (A) matches the weekly catch-up workflow. Standalone config (C) keeps config changes orthogonal to PR work. `--set-default` is required to change the saved default — matches standard CLI convention (git/npm/AWS); defaults change only on deliberate user action.

## Steps

### Step 0 — Create tasks

`TaskCreate` for each batch-level step (0.3, 0.5, 0.7, 6, 8) AND one per-PR loop task (covering Steps 1-5 + 7 for each PR in the resolved list). Mark `in_progress`/`completed` as you go.

**Step runs once per batch:** 0.3, 0.5, 0.7, 6, 8.
**Step runs per PR (loop body):** 1, 2, 3, 4, 4.5, 4.6, 5, 7.

### Step 0.3 — Parse args + classify run mode

Read the invocation arguments and decide which mode the user is in. **Do this before anything else** — it determines whether to fetch PRs, prompt for confirmation, or just update config and exit.

Args you might see (in any combination): positive integers (= PR numbers), `--qa <name>`, `--set-default`, `--reset-qa`, `--dry-run`.

**Classification rules (check in order):**

| Condition | Mode | What to do |
|---|---|---|
| Only config flags present (`--reset-qa` and/or `--qa <name> --set-default`); no PR numbers | **C — Standalone config** | Apply the config change (Step 6 logic), report what changed, exit. Skip all PR steps. |
| 1+ PR numbers in args | **B — Targeted** | Use the PR numbers as the resolved list. Skip Steps 0.5 and 0.7. |
| No PR numbers AND not standalone config | **A — Sweep** | Run Step 0.5 then Step 0.7 to build the resolved list. |

For ambiguous combinations (`--qa <name>` alone with no PR numbers, mixed flags), see **[references/edge-cases.md](references/edge-cases.md)**.

### Step 0.5 — Resolve PR list (Mode A only)

Skip if Mode B or C — list is already known (or empty).

**0.5a — Fetch last 30 merged PRs to dev:**

```bash
gh pr list --repo <your-org>/<your-repo> --base dev --state merged \
  --limit 30 --json number,title,mergedAt,labels,url \
  --jq 'sort_by(.mergedAt) | reverse'
```

**0.5b — Bulk-fetch existing QA issues** (one query, avoid N+1):

```bash
gh issue list --repo <your-org>/<your-repo> \
  --state all \
  --search 'in:title "[QA] PR #" label:"type: test"' \
  --limit 100 --json title --jq '.[].title'
```

`--state all` is required — `gh issue list` defaults to `--state open`, so closed QA issues (the common case: QA already tested and ticked Pass) would be missed and the sweep would file a duplicate handoff for the same PR. Include open + closed.

Parse each title for the pattern `[QA] PR #(\d+):` and build a Set of "already handed off" PR numbers.

**0.5c — Filter the 30-PR list:** drop a PR if its number is in the "already handed off" Set OR if its ONLY labels are `type: docs` and/or `type: chore`. Sort newest-first by `mergedAt`.

**0.5d — Empty result:** tell the user *"✅ All last-30 merged PRs already have QA issues (or are docs/chore-only). Nothing to do. To re-handoff a specific PR anyway, pass it explicitly: `/qa-handoff <PR-number>`."* Then exit cleanly.

### Step 0.7 — Confirm batch (Mode A only)

If the candidate list has 1+ PRs, **show them to the user and ask for confirmation before filing**. Display the list as plain text first:

```
Found N PRs needing QA handoff:
  • #3216 (refactor(...))    merged 2026-05-16
  • #3217 (refactor(...))    merged 2026-05-16
  ... etc
```

Then ask via `AskUserQuestion` (yes/no): *"File QA issues for all N PRs above? (Assignee: @<resolved>, Label: type: test)"* with options `Yes — file all N issues` / `Cancel — don't file anything`.

If `--dry-run`, ask *"Generate proposed issue bodies for all N PRs (no actual filing)?"* instead.

**Why a confirmation gate:** sweep mode has high blast radius (10+ issues in one shot). The user might have a stale filter or want to handoff a subset. Confirmation makes the batch deliberate.

### Step 1 — Verify the PR is mergeable for handoff *(per-PR loop body)*

```bash
gh pr view <N> --json state,mergedAt,baseRefName,title,body,author,labels,files,url
```

Refuse with a clear message if any of these:
- `state != "MERGED"` — *"PR #N is not merged yet; QA handoff is for merged PRs only."*
- `baseRefName != "dev"` — *"PR #N is not against `dev`; this skill is for dev-bound PRs only."*
- Only labels are `type: docs` or `type: chore` — *"This PR is docs/chore-only; QA handoff skipped."*

### Step 2 — Pull the linked issue (if any)

Parse PR body for `Closes #N`, `Fixes #N`, or `Resolves #N`. Fetch the issue:

```bash
gh issue view <issue-N> --json title,body,labels
```

If no linked issue, proceed using PR body alone and note in the test plan that the *"why"* came from the PR description only.

### Step 3 — Map files to modules

Load **[references/module-map.md](references/module-map.md)** and map each changed file path to its module. Dedupe to a unique sorted list. **Bold the module with the most file changes** — that's the primary module.

### Step 4 — Classify risk

Signals (combine — pick highest):

| Signal | Risk level |
|---|---|
| Touches `src/auth.ts`, `src/lib/auth.ts`, or `src/features/auth/` | **High** |
| Touches `src/app/actions/` (Server Actions) | **Medium-High** |
| Touches `src/lib/env.ts`, `src/lib/http/`, or `src/proxy.ts` | **Medium-High** |
| `type: bug` label + production-critical module | **High** |
| `type: refactor` label (no business logic) | **Medium** (regression sweep) |
| `type: feature` + new UI component(s) | **Medium** (happy + edge + regression) |
| UI-only — `.tsx` files only, no hooks/services touched | **Low** |

### Step 4.5 — Pick the test-plan variant

QA people are not developers. Test plans must be **plain English**, **click-this-see-that**, **no code references**. Pick ONE variant below based on the PR's signals.

| Signal in PR | Variant |
|---|---|
| Touches integration code (`razorpay`, `deepgram`, `openai`, `elevenlabs`, `sentry`) AND `type: feature`/`bug`/`refactor` | **8 — External integration** |
| Touches `src/auth.ts`, `src/lib/auth.ts`, `src/features/auth/`, or premium-gating / role-check logic | **6 — Permission/access** |
| Touches `src/app/[org]/`, tenant-config files, or B2B-only modules (Academic) | **7 — Multi-tenant** |
| Touches onboarding flow (`src/app/(authenticated)/welcome/`, signup, first-time-tour) | **9 — Onboarding** |
| Only text/label/translation changes (no logic, no styling) | **10 — Content/copy** |
| `area: performance` OR DB/API route changes (`src/app/api/`, `src/app/actions/`) | **5 — Performance/data** |
| `area: ui` AND only `.tsx`/`.css`/Tailwind class changes | **4 — UI/styling** |
| `type: bug` | **3 — Bug fix** |
| `type: refactor`/`chore` AND "no behavior change" / "pure relocation" / "git mv" in PR body | **1 — Mechanical refactor** |
| `type: feature` (default for new functionality) | **2 — New feature** |
| Falls through none above | **1 — Mechanical refactor** (safest default) |

**Variant template bodies** are in **[references/variants.md](references/variants.md)**. Load that file now, copy the chosen variant's template, and proceed to Step 4.6 to fill placeholders.

For PRs hitting multiple categories, use the more user-visible variant and borrow sub-sections from others (e.g., a new feature that also touches auth → use Variant 2, add a "Permission checks" sub-section from Variant 6).

### Step 4.6 — Synthesize PR-specific content (MANDATORY before Step 5)

**This is the step that makes the difference between a useful and a useless QA handoff.** Templates have `[bracketed placeholders]`. This step fills them with **concrete, PR-specific content** derived from the actual change — not generic phrases.

### Read enough to actually understand the change

Step 1's fetch already gave you `title`, `body`, `labels`, `files`. Use them.

**Assess whether the PR body alone is enough.** Sufficient = it explains:
- WHAT changed in user-visible terms (not just "fix bug" or "refactor X route")
- For bug fixes: the BEFORE behavior (the symptom users saw) and the AFTER behavior
- For features: what the new UI looks like and where to find it

**If the body is insufficient, read the diff:**

```bash
gh pr diff <N> --repo <your-org>/<your-repo>
```

A body is "insufficient" when ANY hold:
- Less than ~200 characters of substantive content (excluding boilerplate / checklists)
- Just lists files changed without explaining what each does
- Only references an external issue / Slack thread without summarising
- Pure template fill-in with empty sections

The diff tells you EXACTLY what changed. Read the relevant file changes — for UI tweaks look at the component file; for config changes look at the config file; for API/route changes look at the route handler.

**You may never skip a PR for "insufficient body".** If both body and diff together still don't tell you what to test, file a one-line follow-up issue asking the author to clarify the PR description and surface the gap to the user — but never file a weak QA handoff with `"See the PR description"`-style fallback.

### Fill every placeholder with PR-specific content

Replace every `[bracketed placeholder]` with concrete PR-specific content derived from the actual diff and PR body. See **[references/edge-cases.md](references/edge-cases.md)** for bad vs. good fill examples.

**Banned phrases** — stop and re-read if your draft contains any of these:
`See the PR description`, `Reproduce the scenario described in the PR`, `the new, fixed behavior` (without a concrete symptom), `the old broken behavior` (without a concrete symptom), any `[bracketed]` placeholder left literally in the body.

A QA handoff that punts back to the PR description is worse than no handoff — file a clarification request on the PR instead.

### Self-check before Step 5

Before generating the markdown file, mentally answer these out loud, in plain English:

1. **What changed?** — 1-2 sentences a non-developer would understand.
2. **Where do I go to test it?** — Specific URL(s), not "the affected page".
3. **What did it look like BEFORE the change?** (Variants 3/4/5) — The actual symptom or appearance.
4. **What should it look like AFTER?** — Concrete expected behavior.
5. **What's the failure mode I'm looking for?** — Specific symptom = bug.

If you can't answer any of these without saying "see the PR description", you haven't read enough yet. Go back.

### Step 5 — Generate the test plan markdown (working file)

Write to `docs/qa-handoffs/PR-<N>.md` as a **working scratch file**. The file is **never committed** — it's deleted at the end of the run (Step 8). It exists only so `gh issue create --body-file` has a path to read from.

Create the directory if it doesn't exist (`mkdir -p docs/qa-handoffs`).

The `<<VARIANT-TEMPLATE>>` placeholder below gets replaced with the variant chosen in Step 4.5 (template body from `references/variants.md`), with all `[bracketed]` placeholders filled in via Step 4.6.

```markdown
# QA Handoff — PR #<N>: <title>

**Merged:** <mergedAt> · **Author:** @<author> · **Risk:** <Low/Medium/High> · **Variant:** <N — variant name>
**Modules:** <bold-primary>, <others>

## What changed
<1–2 line summary distilled from PR title + body — written in plain English>

## Why
<from linked issue body, or "No linked issue — derived from PR description.">

## Where to test
**ALWAYS list the EXACT URLs to test — never leave it as "the affected page" or "the affected module".** Derive concrete URLs from the changed file paths:

| File path pattern | Affected URL |
|---|---|
| `src/app/(authenticated)/(app)/<segment>/page.tsx` | `https://<dev-url>/<segment>` |
| `src/app/(authenticated)/(app)/<segment>/[id]/page.tsx` | `https://<dev-url>/<segment>/<id>` (use a real id from dev) |
| `src/app/(authenticated)/admin/<segment>/page.tsx` | `https://<dev-url>/admin/<segment>` (admin-only) |
| `src/app/(assessment)/...` | The `/tests/[id]/...` test-taking flow URL |
| `src/features/<feature>/components/<x>.tsx` | Look up mount points in the feature's README/docs "Public API" → "Used by" column |
| `src/app/actions/<name>-actions.ts` | The URL of the page where the caller hook fires the action (grep callers, then read the page route) |
| `src/features/<feature>/hooks/use<X>.ts` | The URL where this hook is mounted — grep usages, then read the page route |

When a PR touches multiple URLs (e.g., student-side AND admin-side), list **all of them** with **per-URL persona requirements**:

```
Test these 2 URLs on dev:
1. Student-side: https://<dev-url>/exams
2. Admin-side: https://<dev-url>/admin/exams

Pre-conditions:
- For URL #1: sign in as any user
- For URL #2: sign in as admin/mentor (this URL is admin-only)
```

In the "What to check" section, repeat each URL as a sub-heading and list the per-URL checks.

**Dev (auto-deploys on merge to dev):** `https://<dev-url>`
**Production (after next prod release):** `https://<prod-url>`

## Pre-conditions
<derived from labels + variant + the URLs identified above — must include the persona required to ACCESS each URL>

<<VARIANT-TEMPLATE — content from references/variants.md with [bracketed placeholders] filled in via Step 4.6>>

## Devices
<Desktop · Mobile · Tablet — include only the devices where responsive code was touched; otherwise note "Desktop primary">

## Out of scope
<modules NOT touched — explicit list so QA doesn't over-test>

## Reference
- PR: <PR-URL>
- Issue: <issue-URL or "none">
- Files changed: <count>
- Affected modules: <list>
- Variant used: <N — name>
```

**Important:**
- The variant's section heading (`## What to check` / `## What to test` / `## What to look at` / `## What was broken (before this fix)`) REPLACES the old `## Test scenarios` heading entirely. Don't add both.
- Variant 3 (Bug fix) has TWO `##`-level sections (`What was broken` + `What to check`). Both go in place of the old `## Test scenarios`.
- **Fill every `[bracketed]` placeholder with concrete PR-specific content from Step 4.6.** No fallback phrases. No `[unclear]` placeholders in committed bodies — if Step 4.6 couldn't resolve it, that PR doesn't get a handoff filed.

### Step 6 — Determine the QA assignee *(runs ONCE per batch)*

The QA assignee is resolved from this priority chain. **In batch mode, the same resolved username applies to every PR's issue** — Step 6 runs once before the per-PR loop starts.

In Mode C (standalone config), Step 6 is the only "real" step that runs — it applies the config change and then jumps to a minimal Step 8 report.

```
config path: .claude/skills/qa-handoff/.qa-assignee.local
```

**Resolution order (first match wins):**

1. **`--reset-qa` flag**: delete the config file first, then continue (this allows `--reset-qa --qa <new-name>` to atomically swap defaults).
2. **`--qa <github-username>` flag**: use this value for this run. If `--set-default` is also passed → overwrite the config file. Otherwise → use for this run only.
3. **Saved default**: read the config file. If it exists and contains a non-empty single-line username, use it silently — the user already chose this once; don't re-ask.
4. **Interactive prompt** (only if all above missed): ask via `AskUserQuestion` — *"Which QA user should test this PR? (Provide GitHub username — not email, not display name. This will be saved as your default; pass `--qa <other>` for one-off overrides.)"*. On answer: validate (see below), then write to the config file.
5. If the user cancels the prompt or provides empty → abort the handoff. Don't write anything to the config file.

**Validate the chosen username** before proceeding (any source):

```bash
gh api users/<username> >/dev/null 2>&1
gh api repos/<your-org>/<your-repo>/collaborators/<username> >/dev/null 2>&1
```

- If `gh api users/<username>` returns 404 and the value came from the saved default → warn the user, treat as if no default exists, fall back to the interactive prompt. After they answer, the prompt's value replaces the bad config.
- If `--qa` flag or prompt → re-ask (or abort if `--qa` flag).
- If not a collaborator → warn but proceed; the issue still gets created, just unassigned.

**Config file format** (intentionally minimal): one line, username only, no JSON.

**Track for Step 8 reporting:** `source = "flag"` / `"saved-default"` / `"prompted"` / `"reset+flag"` / `"reset+prompted"`.

### Step 7 — Build the issue body + file the GitHub issue *(per-PR loop body)*

In batch mode, this step runs once per PR. The resolved QA assignee from Step 6 is reused for every iteration.

**Partial-failure handling:** if any sub-step fails for a given PR, record the failure + error message, and **continue with the next PR in the batch**. Don't abort the whole batch. See `references/edge-cases.md` for recovery messages.

### 7a. Build the full issue body

The issue body = a header block (PR metadata) + the full Step-5 plan inlined + a 3-checkbox closing footer.

Write to the same working file `docs/qa-handoffs/PR-<N>.md` (overwrite Step 5 output).

**Title:** `[QA] PR #<N>: <PR title>`

**Body template:**

```markdown
**Original PR:** #<N> · **Author:** @<author> · **Merged:** <mergedAt>
**Risk:** <Low/Medium/High> · **Variant:** <N — variant name>
**Modules:** <bold-primary>, <others>

🔗 **Tested via PR:** #<N>

---

<<FULL TEST PLAN MARKDOWN FROM STEP 5 — paste it verbatim here, starting from the `# QA Handoff — PR #<N>: <title>` heading.>>

---

## ✅ How to close this issue

When you're done testing, **tick one box below** and then **close the issue** (Close button below):

- [ ] ✅ **Pass** — everything works as described, no regressions
- [ ] ❌ **Fail** — found an issue (please file a bug and link it here as `Blocks #<this-issue>`)
- [ ] 🚫 **Blocked** — can't test right now (please add a one-line comment with why)

Questions on any step? Ping @<author> in this thread.
```

Two non-negotiable formatting rules:
- **`(Close button below)`, NOT `(Close button above)`** — GitHub's Close button is at the very bottom of the issue page.
- **`🔗 Tested via PR: #<N>` at the top** — creates a visible cross-link in the issue's timeline AND in the PR's "Mentioned in" sidebar.
- **Checkbox closing is intentional** — zero typing for the Pass case (~90% of handoffs). Don't reintroduce a "Add a comment" instruction.

### 7b. Dry-run guard

If `--dry-run` was passed, **STOP HERE**: do NOT call `gh issue create`, do NOT touch project boards. Print the proposed issue title + the full body file path. The working file remains in place so the user can re-run without `--dry-run`.

### 7c. File the issue (real run)

```bash
gh issue create \
  --repo <your-org>/<your-repo> \
  --title "[QA] PR #<N>: <PR title>" \
  --body-file docs/qa-handoffs/PR-<N>.md \
  --assignee <qa-username> \
  --label "type: test"
```

Notes:
- Use `--body-file` (not `--body`) — issue bodies routinely exceed inline-arg length limits.
- Add `--label "area: <derived>"` if the primary module maps cleanly to one of the existing `area:` labels.
- If the assignee was dropped (not a collaborator), retry once without `--assignee` — see `references/edge-cases.md`.

Capture the returned issue URL for Step 7d.

### 7d. Project board operations

After the issue is created, two project mutations must run:
1. **Set project status to "Ready for QA"** (`updateProjectV2ItemFieldValue` GraphQL mutation).
2. **Remove the issue from TestMySkills IF PRESENT — MUST BE LAST** (TestMySkills auto-add workflow re-fires on `issues.edited`, so any `gh issue edit` after this delete silently re-adds).

Full GraphQL queries + project IDs + the conditional-delete pseudocode are in **[references/project-board.md](references/project-board.md)**. Status updates via GraphQL don't trigger `issues.edited`, so the status set is safe to run before the delete.

### Step 8 — Cleanup + batch report

### 8a. Delete working files

```bash
rm docs/qa-handoffs/PR-<N>.md   # for each PR in the resolved list
```

The issues are the durable artifact. Skip this in `--dry-run` so the user can review the files.

### 8b. Report format

Report shape varies by mode (A/B/C) and batch size. **Full templates in [references/report-templates.md](references/report-templates.md)** — load that file and pick the one matching the run mode:

- **Mode C** (standalone config) — short config-change confirmation
- **Single-PR success** (Mode B with 1 PR) — full per-issue summary with Development-panel link reminder
- **Batch success** (Mode A, or Mode B with 2+ PRs) — table of PR → issue mappings with success/failure markers
- **Dry-run** (any mode) — list of working-file paths to `cat` for review

Each template includes the assignee-source annotation table and the conditional warnings (dropped assignee, project-board partial failure).

Always include assignee + label + project status confirmations, the manual Development-panel link reminder, and per-PR failure reasons so the user can re-run with `/qa-handoff <failed-PRs>`.

## Output

- **Format:** GitHub issue with full test plan inlined + Pass/Fail/Blocked checkboxes
- **Location:** Target repo issues — assigned to QA user, labeled `type: test`, project status = "Ready for QA"
- **Example:** `[QA] PR #3217: feat(exams): add UPSC subject filter` filed as a new issue with a step-by-step test plan and one-click close footer

## Guardrails

- **Refuse on unmerged PRs, non-dev base branches, and pure docs/chore PRs** — these don't get a handoff.
- **Validate the QA username** (GitHub user + repo collaborator) before creating the issue. `--qa` alone = one-time override; saving requires `--qa <name> --set-default`.
- **Saved default file is gitignored** (`.claude/skills/*/*.local`) — per-user, never committed.
- **Sweep mode requires explicit confirmation before filing** — blast radius (7+ issues) is too high to run silently.
- **Partial failures don't abort the batch.** Record failure + reason and continue.
- **Use bulk queries for "already handed off" detection** (single `gh issue list --search` in Step 0.5b). Always pass `--state all` so closed QA issues count.
- **Pick labels from the existing 25-label set** in `docs/LABELS.md` — never invent new labels.
- **EVERY test plan MUST list concrete URLs in "Where to test".** Never leave `[the affected page(s)]` unfilled.
- **EVERY test plan MUST have PR-specific "What changed" and "What was broken" content.** Step 4.6 banned phrases must NEVER appear in a filed body.
- **NEVER commit or push** anything to `dev`. The working `.md` file is for `gh issue create --body-file` only, then deleted.
- **TestMySkills delete MUST be the last action.** Auto-add re-fires on `issues.edited` — any `gh issue edit` after the delete silently re-adds.
- **Development panel auto-link is NOT supported** by GitHub's GraphQL API. See [references/project-board.md](references/project-board.md).
