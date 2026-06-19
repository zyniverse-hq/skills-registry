---
name: git-workflow
description: Applies this user's git conventions for branches, commits, merges, pull requests, force-pushes, and release tags whenever Claude runs any git command. For pre-push conflict detection before a push or PR, use safe-push-workflow.
metadata:
  version: 2.0.1
  author: Arijit Saha
  email: arijit.saha@zysk.tech
  category: engineering-practice
  tags:
    - git
    - version-control
    - commits
    - branching
    - pull-requests
  product: zysk
  sprint: 1
  tested_with: claude-sonnet-4-6
---

# Git Workflow

> Git conventions to load before running any git command - branches, commits, merges, PRs, force-push, and tags.

## When to use

- Activate when: the user asks Claude to run any git command (commit, branch, merge, push, rebase, tag).
- Activate when: the user asks Claude to open, update, or handle a pull request.
- Activate proactively when: a task involves version control in any way, before acting.
- Do NOT activate when: the task has no git/version-control component (pure reading, non-repo edits).

## Steps

### Step 1: Name the branch

**Always fetch before branching** — your local copy of the remote may be stale. Branching from old code causes merge conflicts later.

```bash
git fetch origin
```

Then create your branch off the freshly fetched remote:

```bash
git checkout -b <branch-name> origin/<base-branch>
```

Pattern: `type/short-description` (20 chars max including prefix).

| Type | Prefix |
|------|--------|
| Feature | `feat/` |
| Bug fix | `bugfix/` |
| Refactor | `refactor/` |
| Docs | `docs/` |

Keep the description part short and kebab-case. If it won't fit in 20 chars, abbreviate the description - not the prefix.

### Step 2: Write the commit

- Present tense ("Add auth", not "Added auth")
- Concise - no padding, no vague verbs like "update" or "fix stuff"
- Reference issues/tickets when relevant: `Add login validation #42`

### Step 3: Merge correctly

Never merge locally. The flow is:
1. Push source branch to remote
2. Merge happens on remote via PR only — never run `git merge` locally

Do not run `git checkout main && git merge feature` or `git merge origin/main` locally. Both are local merges and both are wrong. The PR is the merge.

Prefer merge over rebase — preserves history and avoids rewriting shared commits.

### Step 4: Open the pull request

Every PR must have:
- Clear title (imperative, describes the change)
- Description explaining what and why
- Linked issues/tickets
- Labels
- Reviewers assigned

### Step 5: Force-push only as a last resort

Default: never. No `git push --force`.

If truly unavoidable (removing secrets, purging binaries, pre-PR history cleanup on a solo branch):
1. Use `--force-with-lease` - never bare `--force`
2. **Notify the team before pushing** - regardless of whether you think it's a solo branch. Someone else may have fetched it; CI may have pushed to it.

```bash
git push --force-with-lease origin <branch>
# Then: message teammates with branch name and what changed
```

### Step 6: Tag releases

Annotated tags only for releases:

```bash
git tag -a v1.0.0 -m "Release v1.0.0"
git push origin v1.0.0
```

Follow semantic versioning: `v1.0.0`, `v1.0.1`, `v2.0.0`.

## Output

- **Format:** git actions executed according to these conventions, plus any branch names, commit messages, and PR text Claude produces.
- **Location:** the active git repository and its remote.
- **Example:** a feature branch `feat/login-retry`, a commit `Add login retry on 401 #42`, and a PR with title, what/why description, linked issue, labels, and reviewers.

## Notes

- Merge is preferred over rebase to avoid rewriting shared history.
- `--force` is never bare; `--force-with-lease` plus a team heads-up is the only sanctioned override.
- These are conventions, not tooling - no external dependencies required.
