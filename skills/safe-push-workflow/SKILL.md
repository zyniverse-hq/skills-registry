---
name: safe-push-workflow
description: Detects git conflicts before pushing a feature branch to any target branch by fetching remote state and diffing divergent changes. Use when the user asks to push code, push to qa/uat/main/staging, send a branch to remote, or create a PR. For branch, commit, and PR conventions, use git-workflow.
version: 1.1.1
author: Ananth Raj L
email: ananth@zysk.tech
category: pre-deploy-safety
tags:
  - git
  - push-safety
  - conflict-detection
  - pull-request
product: zysk
sprint: 1
tested_with: claude-sonnet-4-6
allowed-tools: Bash
---

# Safe Push Workflow

> Runs a pre-push conflict detection sequence before any git push or PR — so conflicts appear in your terminal, not on GitHub.

## When to use

- Activate when: user asks to push code, push to qa, push to uat, create a PR, or send a branch to remote
- Activate when: user confirms a push with "yes", "go ahead", or "do it" after Claude proposes it
- Do NOT activate when: push is mentioned as a future plan alongside another task (e.g. "fix this, then I'll push")
- Do NOT activate when: user is only pulling or fetching without pushing

## Prerequisites

- [ ] Git repository with a configured remote
- [ ] `gh` CLI installed (for PR creation in Step 8)
- [ ] Feature branch with commits ready to push
- [ ] A companion CLAUDE.md rule so pushes reliably invoke this skill — keyword matching alone
      will not catch a bare "yes" confirmation. Add: "Before executing any git push, always
      invoke the safe-push-workflow skill."

## Steps

### Step 1: Save current state

```bash
git branch --show-current
git status
```

If uncommitted changes exist, stash first:

```bash
git stash --include-untracked
```

### Step 2: Fetch all remote state

```bash
git fetch --all
```

This updates local knowledge of ALL remote branches without touching working files.

### Step 3: Pull latest on current branch

```bash
git pull origin <current-branch>
```

Resolve any conflicts here before proceeding. Branch must be clean first.

### Step 4: See what the target branch has that you don't

```bash
git log HEAD..origin/<target-branch> --oneline
```

Lists every commit teammates pushed to `<target-branch>` that you haven't seen. Read them — understand what changed.

### Step 5: Preview conflict zones

```bash
git diff HEAD...origin/<target-branch> --stat
```

Shows which files diverged between your branch and target. If any overlap with your changes, conflicts will happen on merge — fix them now.

For detailed diff:

```bash
git diff HEAD...origin/<target-branch>
```

### Step 6: Report status to user

Print this before any push:

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
 SAFE PUSH REPORT
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
 Your branch   : <current-branch>
 Target branch : <target-branch>
 Your commits  : X ahead of target
 Target commits: Y commits you haven't pulled
 Conflicting files: [list or "None"]

 Status: ✅ CLEAN — safe to push
       OR
         ⚠️  CONFLICTS DETECTED — resolve before pushing
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

If conflicts detected — STOP. List the files. Wait for user to resolve before proceeding.

### Step 7: Push

```bash
git push origin <current-branch>
```

### Step 8: Create PR

```bash
gh pr create \
  --base <target-branch> \
  --head <current-branch> \
  --title "<descriptive title>" \
  --body "## Summary
- <what changed>

## Test Plan
- [ ] Tested locally
- [ ] No conflicts with <target-branch>"
```

### Step 9: Restore stash (if stashed in Step 1)

```bash
git stash pop
```

## Output

- **Format:** Terminal report + git push + GitHub PR
- **Location:** Terminal (Safe Push Report), GitHub (PR link)
- **Example:** `✅ CLEAN — safe to push` followed by push and PR creation

## Example

**User says:** "push this to qa"

**Claude does:** Fetches all remote refs, pulls latest on current branch, diffs against `origin/qa`, prints the Safe Push Report showing clean status or conflicting files, then pushes the branch and creates a PR targeting qa.

**Result:** PR open on GitHub with zero conflict risk — or a clear conflict report stopping the push before damage is done.

## Notes

- Use `HEAD...origin/target` (three dots) not `HEAD..origin/target` (two dots) — three dots shows only divergent changes, two dots includes shared history and gives misleading results
- A bare "yes" reply will not re-trigger this skill via keyword matching — pair this skill with a CLAUDE.md global rule: "Before executing any git push, always invoke the safe-push-workflow skill"
- Saves ~6–7 hours/month vs pushing blind (based on ~16 pushes/month with 30% conflict rate resolving to 45–90 min per incident)
- Works for any target branch dynamically — qa, uat, main, staging
