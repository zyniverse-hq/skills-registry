# Edge cases + future enhancements (non-blocking reference)

Load this file only when an edge case fires or someone asks "does this skill do X?".

## Step 0.3 — Edge cases in arg parsing

- **`/qa-handoff --qa <name>` with no PR numbers AND no `--set-default`**: ambiguous on first read. Re-read carefully — this IS legitimate: it's **Mode A with a one-time assignee override for the whole sweep batch**. So **accept**.
  - Only refuse if `--set-default` is also present without a PR number AND `--reset-qa` is NOT present (= no work to do beyond saving config, but the `--set-default` semantics require `--qa <name>`).
- **`/qa-handoff --dry-run` alone**: Mode A in dry-run. Fetch + filter + show candidates + prompt; on Yes, generate the markdown files but don't file issues.
- **`/qa-handoff 3217 --reset-qa`**: Mode B (run handoff for #3217) PLUS reset config as a side-effect. Both happen — handled by Step 6's normal resolution chain (the reset runs first; if no flag/saved-default follows, the interactive prompt fires for the saved-default replacement).

## Step 7c — Assignee dropped at filing time

If `gh issue create` fails because the assignee was dropped (not a collaborator):
1. Retry once **without** `--assignee`.
2. Surface a warning to the user: *"⚠ Assignee dropped — @<qa-username> is not a collaborator on <your-org>/<your-repo>. Issue filed unassigned. Add the user to the repo to enable auto-assignment."*
3. Continue with Step 7d (project ops) using the issue number that was returned.

## Step 7d — Partial failures on project ops

If 7d.1 / 7d.2 / 7d.3 fails for a given issue, record the failure with the issue number + sub-step + error message, and **continue to the next PR in the batch**. Don't abort the batch. Step 8 reports per-issue outcome at the end.

Manual recovery messages to surface in Step 8:
- 7d.2 (status set) failed → *"#<issue-N>: project status NOT set — set manually to Ready for QA"*
- 7d.3 (auto-added project delete) failed → *"#<issue-M>: auto-added project removal failed — delete the card manually"*

## What this skill does NOT do (deliberate non-goals)

The following are deliberately out of scope for v1. Add only after v1 is validated on 5+ real merges and a clear pain point emerges:

- **Bundle multiple PRs into ONE release-scoped QA issue.** Current batch mode creates one issue per PR. QA closes them individually — easier tracking, simpler audit trail.
- **Route to different QA assignees per module via a config table.** Today: one assignee per batch.
- **Auto-detect QA outcome by parsing the closing checkbox state.** Reading which checkbox QA ticked would let us auto-classify pass/fail/blocked, but the GitHub API doesn't expose checkbox state cleanly.
- **Wire into `/auto-merge` as a post-merge step.** "One-click ship → QA" is appealing but requires `/auto-merge` to know which PRs need QA (vs docs-only PRs).
- **Cross-reference QA-filed defect issues back to the handoff issue automatically.** Currently QA links them manually via `Blocks #<this-issue>`.
- **Disable the auto-added project auto-add workflow at the source.** Would need a repo admin to edit the workflow file in the auto-added project project's repo. Out of scope for this skill — the conditional check in Step 7d.3 keeps the skill working whether the auto-add is active or disabled.
- **Populate the Development panel programmatically.** No GraphQL mutation exists. See `references/project-board.md` for the introspection result.

## Why the skill is structured this way

- **Three modes (A/B/C) instead of one all-purpose mode**: Mode A's blast radius (10+ issues in one sweep) is high; Mode C's blast radius (zero PR work, just config) is zero. Bundling them with different default behaviors would surprise users.
- **Saved default in a local file (`.qa-assignee.local`)**: GitHub username stays per-user, gitignored, no PII committed. JSON would be overkill for a single string.
- **Inline plan in issue body (not a download link)**: QA reads in GitHub. No "click here to download a file" friction. The body is the durable handoff artifact.
- **Three-checkbox closing footer (Pass/Fail/Blocked) + Close button**: ~90% of handoffs are Pass cases. Tick one box, click Close. Zero typing. Don't reintroduce a "Add a comment" instruction — that adds friction without value.
