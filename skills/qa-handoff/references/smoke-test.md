# First-run smoke test

Load this file when validating an edit to the skill. Run all four scenarios in order — they're additive (Mode C is safest, Mode A sweep-for-real is the biggest blast radius).

## Mode C — Standalone config (safest, no side effects)

```
/qa-handoff --reset-qa
```

**Expected:** prints "Saved default cleared", does nothing else. Verify the file `.claude/skills/qa-handoff/.qa-assignee.local` was deleted.

Then:

```
/qa-handoff --qa Rochanay --set-default
```

**Expected:** prints "Saved default set to @Rochanay", does nothing else. Verify the file exists and contains `Rochanay`.

## Mode B — Single PR dry-run

```
/qa-handoff <N> --dry-run
```

**Expected:** generates `docs/qa-handoffs/PR-<N>.md`, prints the proposed issue title + file path. Nothing filed; no project boards touched. Review with `cat docs/qa-handoffs/PR-<N>.md`. Verify:

1. The markdown plan is accurate (modules, risk, variant, scenarios all sensible).
2. The proposed issue title looks right.
3. The header block (Original PR / Author / Merged / Risk / Variant / Modules) is correct + has the `🔗 Tested via PR: #<N>` line.
4. The closing checkbox section says `(Close button below)` and has 3 checkboxes (Pass / Fail / Blocked).
5. There is NO download link in the body (delivery is via inlined plan only).
6. No banned phrases from Step 4.6 in the body (`See the PR description`, `the new fixed behavior` without specifics, etc.).
7. **Where to test** contains concrete URLs (not `[the affected page(s)]` placeholder).

## Mode B — Multi-PR dry-run

```
/qa-handoff <N1> <N2> --dry-run
```

**Expected:** generates both `docs/qa-handoffs/PR-<N1>.md` and `PR-<N2>.md`. Prints a list of both. No filing.

## Mode A — Sweep dry-run

```
/qa-handoff --dry-run
```

**Expected:** fetches last 30 merged PRs, filters out already-handed-off and docs/chore-only, shows the candidate list as text, prompts for confirmation. On Yes → generates all the `.md` files but files nothing.

## Mode A — Sweep for real (last)

```
/qa-handoff
```

The big one. Files actual issues for every PR needing handoff. Test this LAST, after the dry-runs look correct.

**Verify:**
- Batch report at the end lists each `PR → issue` mapping.
- Walk through each issue's manual Development-panel link step (per #N → ~5s each).
- Confirm each issue's your project status is "Ready for QA".
- Confirm each issue was removed from the auto-added project project (if auto-add fired).

## Failure-mode checks

Pick one filed issue at random and verify:
- Title matches `[QA] PR #<N>: <PR title>`.
- Label `type: test` is present.
- Assignee is the QA user.
- Body opens with `🔗 **Tested via PR:** #<N>`.
- Body ends with 3 checkboxes + "Close button below".
- No banned phrases anywhere.
