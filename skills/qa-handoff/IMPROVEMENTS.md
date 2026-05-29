# IMPROVEMENTS — qa-handoff

> Improvement plan derived from SKILL.md + ANALYSIS.md audit against the agentskills.openml.io spec.

---

## Quick Summary

| | Before | After |
|---|---|---|
| Spec compliance | Partially compliant | Fully compliant |
| Critical violations | 4 | 0 |
| Agent discoverability | Medium | High |
| Portability | Partial | Pass |

---

## Improvement 1 — Move non-standard frontmatter fields under `metadata:`

### What needs to change

Ten custom fields (`version`, `author`, `email`, `category`, `tags`, `product`, `sprint`, `tested_with`, `user-invocable`, `model`) sit at the top level of the frontmatter. The spec allows exactly six top-level keys: `name`, `description`, `license`, `compatibility`, `metadata`, and `allowed-tools`. All non-standard fields must be nested under `metadata:` as string key-value pairs.

### Before
```yaml
version: 1.0.0
author: Rajashekhar V
email: rajashekhar.v@zysk.tech
category: qa-testing
tags:
  - qa
  - testing
  - github-issues
  - handoff
  - test-plan
product: tms
sprint: 3
tested_with: claude-sonnet-4-6
user-invocable: true
model: claude-sonnet-4-6
allowed-tools:
  - Bash
  - Read
  - Write
  - Grep
  - Glob
  - TaskCreate
  - TaskUpdate
  - TaskGet
  - TaskList
  - AskUserQuestion
```

### After
```yaml
allowed-tools:
  - Bash
  - Read
  - Write
  - Grep
  - Glob
  - TaskCreate
  - TaskUpdate
  - TaskGet
  - TaskList
  - AskUserQuestion
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
```

### Impact if implemented
- **Agent behaviour:** Agents and registry tooling that validate against the spec schema will no longer reject the frontmatter. Parsers that expect only standard top-level keys will no longer silently drop `version`, `author`, and `tags`.
- **Discoverability:** Registry indexing tools that filter by `category` or `tags` will find this skill only if those fields are in the correct location. A misplaced `category: qa-testing` field may be ignored entirely.
- **Portability:** Other teams that import this skill into their registry will not get validation warnings or schema errors on install.
- **Risk reduced:** Prevents silent metadata loss where tools read the spec keys only and discard the unrecognised top-level fields.

### Existing use (before fix)
Today, any registry tool or CI check that parses SKILL.md against the agentskills spec schema will emit warnings or errors for the ten unrecognised top-level keys. The `tags` field is a YAML list, but the spec expects `metadata:` values to be strings — this type mismatch can cause parse failures in strict validators. The `model: claude-sonnet-4-6` field at top level is particularly problematic because some loaders interpret top-level unknown keys as override directives and may silently ignore them, meaning the intended model hint never reaches the agent runtime.

### Improved use (after fix)
After the fix, the frontmatter passes spec validation cleanly. Registry indexers can read `metadata.category` and `metadata.tags` to surface this skill under the `qa-testing` category. The `allowed-tools` list remains at the correct top level, and no information is lost — all ten fields are preserved, just relocated under `metadata:`.

---

## Improvement 2 — Add missing `license` field

### What needs to change

The `license` field is required by the spec and is entirely absent from the frontmatter. Without it, registry tooling cannot determine distribution rights, and teams adopting this skill have no guidance on whether they can modify or redistribute it.

### Before
```yaml
---
name: qa-handoff
description: Use after a PR merges to dev to generate a QA test plan inlined into a new GitHub issue assigned to the named QA user. ...
version: 1.0.0
author: Rajashekhar V
# ... (no license field)
---
```

### After
```yaml
---
name: qa-handoff
description: Use after a PR merges to dev to generate a QA test plan inlined into a new GitHub issue assigned to the named QA user. Sets the project status to "Ready for QA" and removes the issue from the auto-added project. QA reads the plan in the issue, ticks a Pass/Fail/Blocked checkbox, and closes the issue. Triggers — "QA handoff", "notify QA about this PR", "send QA test plan", "tell QA to test PR #N".
license: Proprietary — internal use only (zysk.tech)
# ... rest of frontmatter
---
```

### Impact if implemented
- **Agent behaviour:** No direct effect on runtime agent behaviour, but registry tooling that gates skill installation on license presence will no longer block this skill.
- **Discoverability:** Skills without a `license` field may be filtered out of public or shared registries that require explicit licensing.
- **Portability:** Teams evaluating whether they can adapt this skill for their own org now have a clear signal — "Proprietary — internal use only (zysk.tech)" tells them they need to fork and re-license rather than adopt directly.
- **Risk reduced:** Prevents accidental redistribution of proprietary QA workflow logic developed for zysk.tech's TMS product.

### Existing use (before fix)
Today, any developer browsing the skills registry to find a QA handoff skill sees no license information. They cannot tell whether they are allowed to copy the step logic, adapt the variant templates, or publish a derivative. Registry validators that enforce the spec's required fields will flag this skill as incomplete on every lint run.

### Improved use (after fix)
After adding the `license` field, the spec compliance check passes for this field. Teams browsing the registry immediately understand the distribution terms. The registry lint step stops flagging this skill, and CI for the skills-registry repo no longer includes this skill in its list of incomplete entries.

---

## Improvement 3 — Add missing `compatibility` field

### What needs to change

The skill has a hard dependency on the `gh` CLI, a GitHub repository with a `dev` base branch, GitHub Projects v2, and a `.claude/skills/qa-handoff/.qa-assignee.local` config path. None of these requirements are declared in the frontmatter. The spec `compatibility` field exists precisely to surface runtime prerequisites so agents and operators can verify the environment before invoking a skill.

### Before
```yaml
---
name: qa-handoff
description: ...
# (no compatibility field)
---
```

### After
```yaml
---
name: qa-handoff
description: ...
license: Proprietary — internal use only (zysk.tech)
compatibility: >
  Requires GitHub CLI (gh) authenticated with repo write access.
  Designed for Claude Code. Expects a GitHub repository with a dev
  base branch. QA assignee config stored in
  .claude/skills/qa-handoff/.qa-assignee.local (gitignored).
  Project board operations require GitHub Projects v2.
  Tested with claude-sonnet-4-6.
---
```

### Impact if implemented
- **Agent behaviour:** Agents that check `compatibility` before invoking a skill can bail early with a clear error message if `gh` is not installed or not authenticated, rather than failing mid-run at Step 0.5 with a confusing `gh` CLI error.
- **Discoverability:** Teams searching for skills that work with GitHub CLI or GitHub Projects v2 can use the `compatibility` field as a filter.
- **Portability:** A team adopting this skill for a repository that uses `main` as the merge target (not `dev`) can immediately see from the `compatibility` field that they need to adapt Step 1's `baseRefName` check and Step 0.5a's `--base dev` flag.
- **Risk reduced:** Prevents silent failures where the skill starts running, creates TaskCreate entries, then fails at the first `gh pr list` call because `gh` is not installed — leaving orphaned task entries with no completion path.

### Existing use (before fix)
Today, an operator invoking `/qa-handoff 3217` on a machine where `gh` is not installed gets no upfront warning. The skill proceeds through Step 0 (TaskCreate calls succeed), then fails at Step 0.5a with a raw shell error from the missing `gh` binary. The error message gives no guidance on what to install. Similarly, a developer adopting this skill for a repo that uses `main` instead of `dev` has no way to know from the frontmatter that Step 1 will refuse every PR because `baseRefName != "dev"`.

### Improved use (after fix)
After adding `compatibility`, agents and operators can read the prerequisites before invocation. A pre-flight check in the agent runtime can verify `gh` is present and authenticated before any tasks are created. Developers adopting the skill for a non-`dev`-branch repo immediately see they need to adapt Step 1 and Step 0.5a. The `.claude/skills/qa-handoff/.qa-assignee.local` path is documented so operators know where to pre-seed the QA assignee config in automated environments.

---

## Improvement 4 — Reduce body length by moving inline reference tables to `references/` files

### What needs to change

The body is approximately 504 lines (~6,300 tokens), exceeding both the 500-line and 5,000-token spec limits. Three large inline blocks drive most of the overrun and are pure reference material — not procedural steps — making them candidates for extraction into `references/` files that the body links to (matching the pattern already used for `references/variants.md` and `references/project-board.md`):

1. **Step 4.5 variant selection table** (~25 lines) — belongs in `references/variants.md` as a preamble before the variant templates.
2. **Step 5 "Where to test" URL mapping table** (~30 lines) — should move to a new `references/url-mapping.md`.
3. **Step 7a full issue body template** (~45 lines of markdown-in-markdown) — should move to a new `references/issue-template.md`.

### Before

Step 4.5 inline (25 lines in body):
```markdown
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
```

Step 5 URL mapping table inline (~30 lines):
```markdown
| File path pattern | Affected URL |
|---|---|
| `src/app/(authenticated)/(app)/<segment>/page.tsx` | `https://<dev-url>/<segment>` |
| `src/app/(authenticated)/(app)/<segment>/[id]/page.tsx` | `https://<dev-url>/<segment>/<id>` (use a real id from dev) |
| `src/app/(authenticated)/admin/<segment>/page.tsx` | `https://<dev-url>/admin/<segment>` (admin-only) |
| `src/app/(assessment)/...` | The `/tests/[id]/...` test-taking flow URL |
| `src/features/<feature>/components/<x>.tsx` | Look up mount points in the feature's README/docs "Public API" → "Used by" column |
| `src/app/actions/<name>-actions.ts` | The URL of the page where the caller hook fires the action (grep callers, then read the page route) |
| `src/features/<feature>/hooks/use<X>.ts` | The URL where this hook is mounted — grep usages, then read the page route |
```

Step 7a issue body template (~45 lines):
```markdown
**Original PR:** #<N> · **Author:** @<author> · **Merged:** <mergedAt>
**Risk:** <Low/Medium/High> · **Variant:** <N — variant name>
...
## ✅ How to close this issue
When you're done testing, **tick one box below** and then **close the issue**...
- [ ] ✅ **Pass** — everything works as described, no regressions
- [ ] ❌ **Fail** — found an issue ...
- [ ] 🚫 **Blocked** — can't test right now ...
```

### After

**Step 4.5 in body (4 lines, replaces 25):**
```markdown
### Step 4.5 — Pick the test-plan variant

Load **[references/variants.md](references/variants.md)**. The file begins with a variant-selection table mapping PR signals (labels, file paths, PR body keywords) to one of the 10 variants. Pick the variant matching the highest-priority signal, copy its template, and proceed to Step 4.6 to fill placeholders.
```

**Step 5 URL mapping in body (4 lines, replaces 30):**
```markdown
**ALWAYS list EXACT URLs — never leave `[the affected page(s)]` unfilled.** Derive concrete URLs from changed file paths using the mapping table in **[references/url-mapping.md](references/url-mapping.md)**. List per-URL persona requirements when multiple URLs apply.
```

**Step 7a in body (4 lines, replaces 45):**
```markdown
### 7a. Build the full issue body

Issue body = header block + full Step-5 plan inlined + 3-checkbox closing footer. Full template (title format, header block, `🔗 Tested via PR` line, closing footer with Pass/Fail/Blocked checkboxes) is in **[references/issue-template.md](references/issue-template.md)**. Write to `docs/qa-handoffs/PR-<N>.md` (overwrite Step 5 output).
```

**New `references/url-mapping.md`** (extracted content):
```markdown
# URL Mapping — qa-handoff

Map changed file paths to testable URLs on dev.

| File path pattern | Affected URL |
|---|---|
| `src/app/(authenticated)/(app)/<segment>/page.tsx` | `https://<dev-url>/<segment>` |
| `src/app/(authenticated)/(app)/<segment>/[id]/page.tsx` | `https://<dev-url>/<segment>/<id>` (use a real id from dev) |
| `src/app/(authenticated)/admin/<segment>/page.tsx` | `https://<dev-url>/admin/<segment>` (admin-only) |
| `src/app/(assessment)/...` | The `/tests/[id]/...` test-taking flow URL |
| `src/features/<feature>/components/<x>.tsx` | Look up mount points in feature README "Public API" → "Used by" |
| `src/app/actions/<name>-actions.ts` | URL of the page where the caller hook fires the action |
| `src/features/<feature>/hooks/use<X>.ts` | URL where this hook is mounted — grep usages, then read the page route |

When a PR touches multiple URLs, list all with per-URL persona requirements:
- Student-side: sign in as any user
- Admin-side: sign in as admin/mentor
```

**New `references/issue-template.md`** (extracted content):
```markdown
# Issue Body Template — qa-handoff

## Title format
`[QA] PR #<N>: <PR title>`

## Body

**Original PR:** #<N> · **Author:** @<author> · **Merged:** <mergedAt>
**Risk:** <Low/Medium/High> · **Variant:** <N — variant name>
**Modules:** <bold-primary>, <others>

🔗 **Tested via PR:** #<N>

---

<<FULL TEST PLAN MARKDOWN FROM STEP 5>>

---

## ✅ How to close this issue

When you're done testing, **tick one box below** and then **close the issue** (Close button below):

- [ ] ✅ **Pass** — everything works as described, no regressions
- [ ] ❌ **Fail** — found an issue (please file a bug and link it here as `Blocks #<this-issue>`)
- [ ] 🚫 **Blocked** — can't test right now (please add a one-line comment with why)

Questions on any step? Ping @<author> in this thread.

## Non-negotiable formatting rules
- `(Close button below)` NOT `(Close button above)` — GitHub's Close button is at the bottom.
- `🔗 Tested via PR: #<N>` at the top — creates cross-link in issue timeline and PR's "Mentioned in" sidebar.
- Checkbox closing is intentional — zero typing for the Pass case (~90% of handoffs).
```

These changes bring the body from ~504 lines to approximately ~400 lines.

### Impact if implemented
- **Agent behaviour:** Agents loading this skill stay well within context window limits. The full skill body loads in a single pass without truncation risk, ensuring Steps 4.5, 5, and 7a are not partially cut off.
- **Discoverability:** No change to discoverability — the `description` and trigger keywords remain intact.
- **Portability:** Teams adapting this skill can update the URL mapping table and issue template in isolated `references/` files without touching the procedural step logic.
- **Risk reduced:** Prevents context truncation mid-run where the agent loads the skill, processes up to Step 4 correctly, then loses Steps 5–8 because the body was cut off at the token limit. This is a silent failure — the agent continues running with an incomplete skill definition.

### Existing use (before fix)
Today, with ~6,300 tokens in the body, an agent loading this skill on top of a conversation with moderate context usage risks truncating the body before reaching Step 7 or Step 8. In practice this means the `gh issue create` command in Step 7c, the project board operations in Step 7d, and the cleanup in Step 8 may never be seen by the agent. The skill appears to run — tasks are created, PRs are fetched — but issues are never filed and working files are never cleaned up. The failure is silent because the agent simply doesn't know those steps exist.

### Improved use (after fix)
After extraction, the ~400-line body loads reliably within budget. The agent processes all steps including the project board GraphQL mutations in Step 7d and the batch report in Step 8. The three new `references/` files are loaded on demand (Step 4.5 loads `variants.md` and the selection table, Step 5 loads `url-mapping.md`, Step 7a loads `issue-template.md`), keeping total loaded content proportional to what's actually needed per run.

---

## Improvement 5 — Add `--report-templates` reference file entry to Step 8b

### What needs to change

Step 8b references `references/report-templates.md` for batch report templates but the body does not link to it consistently — the reference is mentioned once without the same `(loaded in Step X)` annotation pattern used for `variants.md` and `project-board.md` in the "Supporting reference files" section at the top of the body. The reference file is either missing from the directory or not documented in the skill header.

### Before
```markdown
## Supporting reference files (loaded only when needed)

- **[references/variants.md](references/variants.md)** — the 10 test-plan variant templates (loaded in Step 4.5)
- **[references/project-board.md](references/project-board.md)** — full GraphQL queries for Step 7d project operations
- **[references/edge-cases.md](references/edge-cases.md)** — arg-parsing edge cases, partial-failure handling, future non-goals
- **[references/smoke-test.md](references/smoke-test.md)** — first-run smoke test procedure for skill edits
```

Step 8b body text:
```markdown
**Full templates in [references/report-templates.md](references/report-templates.md)** — load that file and pick the one matching the run mode
```

### After
```markdown
## Supporting reference files (loaded only when needed)

- **[references/variants.md](references/variants.md)** — the 10 test-plan variant templates + variant selection table (loaded in Step 4.5)
- **[references/project-board.md](references/project-board.md)** — full GraphQL queries for Step 7d project operations (loaded in Step 7d)
- **[references/edge-cases.md](references/edge-cases.md)** — arg-parsing edge cases, partial-failure handling, future non-goals
- **[references/smoke-test.md](references/smoke-test.md)** — first-run smoke test procedure for skill edits
- **[references/report-templates.md](references/report-templates.md)** — batch report templates for Mode A, B, C, and dry-run (loaded in Step 8b)
- **[references/url-mapping.md](references/url-mapping.md)** — file-path-to-URL mapping table (loaded in Step 5)
- **[references/issue-template.md](references/issue-template.md)** — full issue body template with closing footer (loaded in Step 7a)
```

### Impact if implemented
- **Agent behaviour:** The agent can scan the "Supporting reference files" section at the top of the skill to understand the full reference graph before starting. It knows which files to load at which step, and can pre-fetch them if context budget allows.
- **Discoverability:** Developers reading the skill header get a complete map of all supporting files in one place, rather than discovering `report-templates.md` only when they reach Step 8b.
- **Portability:** Teams forking the skill can identify all files they need to copy/adapt from the header section alone, without reading every step.
- **Risk reduced:** Prevents the agent from reaching Step 8b and finding `references/report-templates.md` is missing (because no one knew it needed to exist), then silently skipping the report or generating a freeform summary that omits key fields.

### Existing use (before fix)
Today, `references/report-templates.md` is referenced in Step 8b but not listed in the "Supporting reference files" header. A developer setting up this skill for the first time copies the four listed reference files (`variants.md`, `project-board.md`, `edge-cases.md`, `smoke-test.md`) and misses `report-templates.md`. The skill runs correctly through Steps 1–7, then fails at Step 8b when the agent cannot find the report template file. The run completes without a structured report, and the developer has no easy way to know which file is missing.

### Improved use (after fix)
After adding all reference files to the header section (including the two new files from Improvement 4), a developer setting up this skill copies all seven reference files in one pass. The agent can also use the header to verify its reference file graph before starting a run, and can surface a clear error message if any file is absent rather than failing silently mid-run.

---

## Priority Order

| Priority | Improvement | Effort | Impact |
|---|---|---|---|
| 1 | Reduce body length by moving inline tables to `references/` files | Medium | Critical — prevents silent context truncation that causes Steps 7–8 to never execute |
| 2 | Move non-standard frontmatter fields under `metadata:` | Low | High — fixes spec compliance, enables registry indexing by category/tags |
| 3 | Add missing `compatibility` field | Low | High — surfaces `gh` CLI and `dev` branch requirements before invocation failures |
| 4 | Add missing `license` field | Low | Medium — required by spec; blocks registry lint; clarifies distribution rights |
| 5 | Add `report-templates.md` and new reference files to header section | Low | Medium — prevents missing-file failures at Step 8b; gives developers complete setup checklist |

---

## Before vs After: Full Skill Experience

### Before (current state)

A developer invoking `/qa-handoff 3217` today encounters a skill that is functionally sophisticated — three modes, 10 test-plan variants, banned phrases, partial-failure handling — but fragile at the infrastructure level. The frontmatter has ten fields at the wrong level, meaning any registry tooling that validates against the spec schema flags this skill as non-compliant on every CI run. The missing `license` field means the registry lint step never passes for this skill. The missing `compatibility` field means an operator on a machine without `gh` CLI gets no upfront warning — the skill creates TaskCreate entries, starts fetching PR metadata, and then crashes at the first `gh pr list` call with a raw shell error that gives no guidance on what to install.

More critically, the 504-line body is 4 lines over the spec limit and approximately 1,300 tokens over the token budget. In practice, an agent loading this skill on top of a conversation with moderate prior context — a common scenario in a multi-step workflow — risks truncating the body before reaching Step 7. The truncation is silent: the agent processes Steps 0–6 correctly, creates tasks, fetches PR data, generates the test plan variant, then simply stops because it never saw Steps 7 and 8. No issues are filed, no project board status is updated, no working files are cleaned up, and the agent reports success because it completed everything it knew about.

### After (all improvements applied)

After all five improvements, the skill is spec-compliant and operationally reliable. The frontmatter passes validation: `name`, `description`, `license`, `compatibility`, `metadata`, and `allowed-tools` are the only top-level keys; the ten custom fields are correctly nested under `metadata:`. Registry lint passes cleanly. Operators adopting the skill see the `compatibility` field immediately and know they need `gh` CLI with repo write access, a `dev` base branch, and GitHub Projects v2 — before they copy a single file.

The body is reduced to approximately 400 lines by extracting the Step 4.5 variant selection table into `references/variants.md`, the Step 5 URL mapping table into a new `references/url-mapping.md`, and the Step 7a issue body template into a new `references/issue-template.md`. All three are loaded on demand at the step that needs them, keeping context proportional to what's actually running. The agent now reliably reaches Step 7 and Step 8 on every invocation, meaning issues are actually filed, project board status is actually set to "Ready for QA", working files are actually cleaned up, and the batch report is actually generated. The "Supporting reference files" header section lists all seven reference files with their load-step annotations, giving both developers and the agent runtime a complete manifest of what needs to exist before the skill can run.
