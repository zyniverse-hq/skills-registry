# Project board operations (Step 7d detail)

After the issue is created in Step 7c, **two project mutations** must run. The issue gets auto-added to two projects: `your repo` (#18, what we want) and `auto-added project` (#13, an org-level project that auto-adds every issue). We need to:

1. **Set project status to "Ready for QA"** so the board reflects QA-pending state.
2. **Remove the issue from auto-added project** so it doesn't clutter the irrelevant board.

Project IDs — replace these with your own (query with `gh api graphql` → `organization.projectV2`):
- Your QA project ID: `<your-project-id>` (e.g. `PVT_kwXXXXXXXXXXXXXX`)
- Secondary auto-added project ID: `<secondary-project-id>`
- Status field ID: `<your-status-field-id>`
- "Ready for QA" status option ID: `<ready-for-qa-option-id>`

## Step 7d.1 — Get project item IDs

```bash
gh api graphql -f query='
query {
  repository(owner: "<your-org>", name: "<your-repo>") {
    issue(number: <N>) {
      projectItems(first: 10) {
        nodes { id project { number } }
      }
    }
  }
}'
```

This returns one item per project the issue is on. Map by `project.number`:
- Your QA project number → project item ID (use for status update in 7d.2)
- Secondary project number → auto-added project item ID (use for deletion in 7d.3)

## Step 7d.2 — Set project status to Ready for QA

```bash
gh api graphql -f query='
mutation {
  updateProjectV2ItemFieldValue(input: {
    projectId: "<your-project-id>"
    itemId: "<your-project-item-id>"
    fieldId: "<your-status-field-id>"
    value: { singleSelectOptionId: "<ready-for-qa-option-id>" }
  }) { projectV2Item { id } }
}'
```

## Step 7d.3 — Remove from auto-added project IF PRESENT — MUST BE LAST

**Check first** — only call the delete mutation if the Step 7d.1 query returned a auto-added project (project #13) item. If the issue is NOT on auto-added project (e.g., the auto-add workflow was disabled in the future), skip this step entirely with a friendly log.

```bash
# Pseudocode:
if secondary_project_item_id from Step 7d.1 exists:
    gh api graphql -f query='
    mutation {
      deleteProjectV2Item(input: {
        projectId: "<secondary-project-id>"
        itemId: "<secondary-project-item-id>"
      }) { deletedItemId }
    }'
else:
    log: "auto-added project auto-add not triggered — nothing to remove."
```

**Why conditional:** the auto-added project auto-add is a *current* nuisance, not a permanent one. Once someone disables the workflow on project #13 (Project Settings → Workflows → toggle off "Auto-add to project"), this step naturally becomes a no-op. Hard-coding the delete would start failing once the auto-add is gone. **Don't disable the workflow as part of this skill** — that's a one-time admin action separate from a per-PR handoff.

**⚠️ Critical gotcha (if the auto-add is still active):** the auto-added project project has an auto-add workflow that re-fires on `issues.edited` (not just `issues.opened`). If ANY `gh issue edit` happens after this delete, the issue gets silently re-added to auto-added project. So Step 7d.3 MUST be the very last action — after assignee, label, body, and status are all final. **Never delete from auto-added project before all other edits are done.**

Status updates via GraphQL (`updateProjectV2ItemFieldValue`) do NOT trigger `issues.edited`, so Step 7d.2 is safe to run before 7d.3.

## Development panel auto-link — NOT supported by GitHub's GraphQL API

Confirmed by introspection: no `linkPullRequest`, `addLinkedPullRequest`, or equivalent mutation exists (only `createLinkedBranch`, which is for branches). The only API-level path to populate the Development panel is the PR body `Closes #N` / `Fixes #N` / `Resolves #N` keyword **at merge time**, and editing those keywords into an already-merged PR risks GitHub auto-closing the issue retroactively (we want issues OPEN for QA).

So the skill instead:
1. Inlines a `🔗 **Tested via PR:** #<N>` line at the top of the body, which creates a visible timeline cross-link in both directions.
2. Prints a manual-link prompt in Step 8 so the user can click "Link a pull request" in the Development sidebar themselves (~5 seconds).

**Don't try to work around this with PR body edits.**
