# Step 8 report templates

Load this file when generating the Step 8 batch report. Pick the template that matches the mode + count.

## Mode C — Standalone config (no PR work)

```
✅ Config updated: <description of what changed>

  Saved default assignee:  @<name>  (or "(cleared)" after --reset-qa)
  File:                    .claude/skills/qa-handoff/.qa-assignee.local

To file a QA handoff: /qa-handoff <PR-number>
```

## Single-PR success (Mode B with 1 PR)

```
✅ Issue filed:     <issue-URL>
✅ Assigned to:     @<qa-username>  (<source>)
✅ Label:           type: test
✅ Project status:  Ready for QA (your repo)
<one of these two auto-added project lines:>
✅ Removed from:    auto-added project project (auto-add cleanup)
ℹ  auto-added project:    not auto-added (workflow disabled — no cleanup needed)
   Module(s): <list> · Risk: <level> · Variant: <N — name>

📌 Manual one-step to fully wire the Development panel:
   Open <issue-URL> → Development sidebar → "Link a pull request"
   → search "#<N>" → tick the box. (~5 seconds. GitHub's GraphQL API
   has no equivalent mutation, so this is the only way.)

QA will:
  1. Open the issue from their assigned-to-me view
  2. Read the plan inline
  3. Test the changes on dev: https://<dev-url>
  4. Tick Pass / Fail / Blocked checkbox + close the issue
```

## Batch success (Mode A, or Mode B with 2+ PRs)

```
Batch QA handoff complete — <S>/<N> succeeded:

✅ #3216 → issue #<X> (https://github.com/<your-org>/<your-repo>/issues/<X>)
✅ #3217 → issue #<X+1> (https://...)
✅ #3219 → issue #<X+2> (https://...)
❌ #3220 → FAILED: <reason — e.g. "PR not merged yet (state: OPEN)" or "gh API 422">
✅ #3221 → issue #<X+3> (https://...)
…

Assignee:        @<qa-username>  (<source>)
Label:           type: test (on every successful issue)
Project status:  Ready for QA (set on every successful issue)
auto-added project:    removed from all successful issues
  (or:           not auto-added — workflow disabled — no cleanup needed)

📌 Manual Development-panel linking still needed PER ISSUE (~5s each).
   No GraphQL API for this. The list of issue URLs above is all you need
   to walk through them.

Failures: re-run the skill targeting just the failed PRs:
   /qa-handoff <failed-PR-number> [<more>]

QA workflow per issue:
  1. Open assigned-to-me view (will show all <S> new issues)
  2. Test each on dev: https://<dev-url>
  3. Tick Pass / Fail / Blocked + close the issue
```

## Dry-run (any mode)

```
ℹ️  Dry-run — N proposed issue(s), nothing filed, no project changes:

  • PR #3217 → docs/qa-handoffs/PR-3217.md  (Risk: Medium-High, Variant 5)
  • PR #3220 → docs/qa-handoffs/PR-3220.md  (Risk: Low, Variant 1)
  …

Review with:  cat docs/qa-handoffs/PR-<N>.md
To run for real, drop --dry-run.
```

## Assignee source annotations

Used in the `(<source>)` slot of the success reports:

| Source                | Annotation                                              |
| --------------------- | ------------------------------------------------------- |
| `saved-default`       | `(saved default)`                                       |
| `prompted`            | `(prompted — saved as new default)`                     |
| `flag`                | `(--qa one-time override)`                              |
| `flag` + set-default  | `(--qa override + saved as new default)`                |
| `reset+flag`          | `(default reset → --qa used; not saved)`                |
| `reset+prompted`      | `(default reset → prompted — new default saved)`        |

## Conditional warnings (append to any report)

If the issue was filed without the assignee (because the QA user isn't a repo collaborator):

```
⚠  Assignee dropped — @<qa-username> is not a collaborator on <your-org>/<your-repo>.
   Issue(s) filed unassigned. Add the user to the repo to enable auto-assignment.
```

If Step 7d (project ops) partially failed on one or more issues:

```
⚠  Project board step incomplete on these issues:
   - #<issue-N>: project status NOT set — set manually to "Ready for QA"
   - #<issue-M>: auto-added project removal failed — delete the card manually
```
