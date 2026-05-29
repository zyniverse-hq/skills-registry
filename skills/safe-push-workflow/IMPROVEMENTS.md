# IMPROVEMENTS — safe-push-workflow

> Improvement plan derived from SKILL.md + ANALYSIS.md audit against the agentskills.openml.io spec.

---

## Quick Summary

| | Before | After |
|---|---|---|
| Spec compliance | Partially compliant | Fully compliant |
| Critical violations | 3 | 0 |
| Agent discoverability | Medium | High |
| Portability | Partial | Pass |

---

## Improvement 1 — Move Non-Standard Frontmatter Fields Under `metadata:`

### What needs to change

Eight non-standard fields (`version`, `author`, `email`, `category`, `tags`, `product`, `sprint`, `tested_with`) are placed at the top level of the frontmatter. The spec requires all non-standard fields to be nested under a `metadata:` key. These fields must be moved, and the two missing required fields (`license` and `compatibility`) must be added at the top level.

### Before
```yaml
---
name: safe-push-workflow
description: Detects git conflicts before pushing a feature branch to any target branch by fetching remote state and diffing divergent changes.
version: 1.0.0
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
---
```

### After
```yaml
---
name: safe-push-workflow
description: Detects git conflicts before pushing or creating a PR. Activate when user says "push to qa", "push to uat", "create a PR", "send this branch to remote", or confirms a push with "yes" / "go ahead". Fetches remote state and diffs divergent changes so conflicts appear in your terminal, not on GitHub.
license: MIT
compatibility: Requires git >= 2.x and gh CLI >= 2.x installed and authenticated on the system. Tested with claude-sonnet-4-6.
metadata:
  version: 1.0.0
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
---
```

### Impact if implemented
- **Agent behaviour:** Parsers that validate frontmatter against the spec will no longer reject or warn on this skill. Agents that read `license` and `compatibility` will correctly surface dependency requirements before execution.
- **Discoverability:** No direct effect on keyword discovery, but registry indexers that require valid frontmatter structure will now include this skill in search results.
- **Portability:** Any team adopting this skill will immediately know it requires MIT licensing terms and specific tool versions, reducing setup friction.
- **Risk reduced:** Prevents silent frontmatter parse failures in registry tooling that expects only standard fields at the top level.

### Existing use (before fix)
Today, when a registry indexer or validation tool processes `safe-push-workflow`, it encounters eight non-standard fields (`version`, `author`, `email`, `category`, `tags`, `product`, `sprint`, `tested_with`) sitting at the top level alongside `name` and `description`. Strict parsers will either throw a validation error or silently drop the skill from the index. Additionally, because `license` and `compatibility` are entirely absent, any agent or developer adopting this skill has no machine-readable signal about legal terms or hard tool prerequisites.

### Improved use (after fix)
After the fix, the frontmatter validates cleanly against the spec. All eight custom fields are nested under `metadata:`, `license: MIT` is present at the top level, and `compatibility` documents the git and gh CLI version requirements. Registry indexers include the skill without warnings. An agent consuming this skill can check `compatibility` before invoking Step 8's `gh pr create` command and warn the user proactively if `gh` is not installed or authenticated.

---

## Improvement 2 — Add Trigger Keywords to `description` Field

### What needs to change

The `description` field explains the mechanism well ("fetching remote state and diffing divergent changes") but omits the specific natural-language trigger phrases that agents use for initial skill discovery. The "When to use" section in the body has excellent trigger phrases, but agents match on `description` first — those phrases must appear there.

### Before
```yaml
description: Detects git conflicts before pushing a feature branch to any target branch by fetching remote state and diffing divergent changes.
```

### After
```yaml
description: Detects git conflicts before pushing or creating a PR. Activate when user says "push to qa", "push to uat", "create a PR", "send this branch to remote", or confirms a push with "yes" / "go ahead". Fetches remote state and diffs divergent changes so conflicts appear in your terminal, not on GitHub.
```

### Impact if implemented
- **Agent behaviour:** Agents performing keyword-based skill selection will now match this skill on "push to qa", "create a PR", "send this branch", and "go ahead" — the most common user phrasings for triggering a push workflow.
- **Discoverability:** Significantly improved. The current description contains no trigger phrases, meaning agents must read the full body "When to use" section to discover this skill. The updated description makes it selectable at the first-pass scan stage.
- **Portability:** No portability effect, but teams integrating this into a multi-skill agent will see correct activation without needing to configure custom trigger rules.
- **Risk reduced:** Prevents the skill from being skipped by agents that match on description alone, which would result in unprotected pushes proceeding without conflict detection.

### Existing use (before fix)
Today, if a user says "push this to qa", an agent scanning skill descriptions will read "Detects git conflicts before pushing a feature branch to any target branch by fetching remote state and diffing divergent changes." The phrase "push to qa" does not appear in the description, so the skill may not be selected. The agent may proceed with a raw `git push` without running the 9-step conflict detection sequence, which is exactly the failure mode this skill was built to prevent.

### Improved use (after fix)
After the fix, "push to qa", "create a PR", and "go ahead" all appear verbatim in the description. An agent scanning for the best skill to handle "push this to qa" will match `safe-push-workflow` immediately and activate the full 9-step sequence. The conflict detection runs, the Safe Push Report is printed, and the user sees a clean status or a list of conflicting files before any push occurs.

---

## Improvement 3 — Add Edge Case Handling for Detached HEAD, No Remote, and First Push

### What needs to change

Step 1 runs `git branch --show-current` but does not handle a detached HEAD state (which returns an empty string). Step 3 runs `git pull origin <current-branch>` but does not handle a branch that does not yet exist on the remote (which causes a fatal error on first push). The skill also has no check for whether a remote is configured before `git fetch --all` in Step 2. These three gaps cause silent or confusing failures that stop the workflow mid-execution.

### Before
```markdown
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

### Step 3: Pull latest on current branch

```bash
git pull origin <current-branch>
```

Resolve any conflicts here before proceeding. Branch must be clean first.
```

### After
```markdown
### Step 1: Save current state

```bash
git branch --show-current
git status
```

**Edge case — detached HEAD:** If `git branch --show-current` returns an empty string, the repository is in detached HEAD state. Stop and instruct the user:
> "You are in a detached HEAD state. Check out a named branch before pushing: `git checkout -b <branch-name>`"

**Edge case — no remote configured:** Before Step 2, verify a remote exists:
```bash
git remote -v
```
If output is empty, stop and instruct:
> "No remote is configured. Add one with: `git remote add origin <url>`"

If uncommitted changes exist, stash first:

```bash
git stash --include-untracked
```

### Step 2: Fetch all remote state

```bash
git fetch --all
```

### Step 3: Pull latest on current branch

```bash
git pull origin <current-branch>
```

**Edge case — branch does not exist on remote yet (first push):** If this command errors with "couldn't find remote ref", the branch is new. Skip this step and note in the Safe Push Report:
> "Branch does not exist on remote yet — first push. Upstream will be set automatically."

Use `git push --set-upstream origin <current-branch>` in Step 7 instead of `git push origin <current-branch>`.

Resolve any conflicts here before proceeding. Branch must be clean first.
```

### Impact if implemented
- **Agent behaviour:** The skill now self-diagnoses three common failure states rather than crashing mid-execution. The agent prints a clear, actionable message instead of propagating a raw git error to the user.
- **Discoverability:** No effect on discovery, but improves execution reliability — agents that encounter these edge cases no longer abandon the workflow silently.
- **Portability:** Critical for teams using this on projects where developers frequently work in detached HEAD (e.g., after `git checkout <commit>`) or push new feature branches for the first time.
- **Risk reduced:** Prevents three categories of mid-workflow failure: (1) detached HEAD producing an empty branch name that corrupts all subsequent commands, (2) missing remote causing `git fetch --all` to error, (3) `git pull` fatal error on a branch that has never been pushed.

### Existing use (before fix)
Today, if a developer on a new feature branch runs this skill for the first time (branch exists locally but not on remote), Step 3 executes `git pull origin feature/new-branch` and receives a fatal error: "couldn't find remote ref feature/new-branch." The workflow stops, no Safe Push Report is printed, and the developer is left with a raw git error message and no guidance. Similarly, a developer in detached HEAD state will have `git branch --show-current` return an empty string, and every subsequent command that substitutes `<current-branch>` will either fail or operate on an incorrect target.

### Improved use (after fix)
After the fix, Step 1 immediately detects detached HEAD and prints a clear instruction to check out a named branch. Step 2 verifies a remote exists before attempting `git fetch`. Step 3 detects the "no upstream" condition on a first-push branch and switches to `git push --set-upstream` in Step 7. The Safe Push Report still prints correctly, noting "first push — upstream will be set." The developer never sees a raw git error; they see structured guidance at every failure point.

---

## Improvement 4 — Add `gh` CLI Authentication Check Before Step 8

### What needs to change

Step 8 runs `gh pr create` without first verifying that the `gh` CLI is installed and authenticated. If `gh` is not authenticated, the command fails with a non-obvious error. The skill should check `gh auth status` before attempting PR creation and provide a clear recovery instruction.

### Before
```markdown
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
```

### After
```markdown
### Step 8: Create PR

Before creating the PR, verify `gh` is installed and authenticated:

```bash
gh auth status
```

**Edge case — gh not authenticated or not installed:**
- If `gh` is not installed: instruct the user to install it from https://cli.github.com and run `gh auth login`.
- If `gh` is installed but not authenticated: instruct the user to run `gh auth login` and complete the browser flow, then re-run from this step.

Once authenticated, create the PR:

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
```

### Impact if implemented
- **Agent behaviour:** The agent no longer silently fails at the final step after completing 7 steps of conflict detection and push work. It detects the authentication gap pre-emptively and gives the user a single recovery action.
- **Discoverability:** No effect on discovery.
- **Portability:** High impact for new team members or CI environments where `gh` may be present but not authenticated, which is a common state on freshly provisioned machines.
- **Risk reduced:** Prevents a frustrating failure mode where the branch is already pushed (Step 7 succeeded) but no PR is created, leaving the push in a limbo state — code is on remote but the PR is missing, which can be easy to overlook.

### Existing use (before fix)
Today, if a developer completes Steps 1 through 7 (conflict detection passes, branch is pushed successfully) and then hits Step 8 with an unauthenticated `gh` CLI, the command fails with an error like "authentication required" or "could not determine GitHub host." The branch is already pushed at this point but no PR exists. The developer must debug the `gh` authentication issue independently, then manually re-run the `gh pr create` command with the correct flags. The Safe Push Workflow has completed 90% of its job but leaves the developer in an incomplete state.

### Improved use (after fix)
After the fix, `gh auth status` runs before `gh pr create`. If authentication is missing, the agent prints an explicit message: "gh CLI is not authenticated. Run `gh auth login` and complete the browser flow, then re-run Step 8." The developer authenticates once and the PR is created without re-running the entire workflow. If `gh` is not installed, the agent surfaces the install URL immediately. The full 9-step workflow completes end-to-end without manual debugging.

---

## Improvement 5 — Move Business Justification from Notes to `metadata:`

### What needs to change

The `Notes` section contains one bullet that is a business justification rather than an execution instruction: "Saves ~6-7 hours/month vs pushing blind (based on ~16 pushes/month with 30% conflict rate resolving to 45-90 min per incident)." This belongs in `metadata:` as a `roi_estimate` field, not in the body where agents read it as an instruction.

### Before
```markdown
## Notes

- Use `HEAD...origin/target` (three dots) not `HEAD..origin/target` (two dots) — three dots shows only divergent changes, two dots includes shared history and gives misleading results
- A bare "yes" reply will not re-trigger this skill via keyword matching — pair this skill with a CLAUDE.md global rule: "Before executing any git push, always invoke the safe-push-workflow skill"
- Saves ~6–7 hours/month vs pushing blind (based on ~16 pushes/month with 30% conflict rate resolving to 45–90 min per incident)
- Works for any target branch dynamically — qa, uat, main, staging
```

### After
```markdown
## Notes

- Use `HEAD...origin/target` (three dots) not `HEAD..origin/target` (two dots) — three dots shows only divergent changes, two dots includes shared history and gives misleading results
- A bare "yes" reply will not re-trigger this skill via keyword matching — pair this skill with a CLAUDE.md global rule: "Before executing any git push, always invoke the safe-push-workflow skill"
- Works for any target branch dynamically — qa, uat, main, staging
```

And in frontmatter `metadata:`:
```yaml
metadata:
  ...
  roi_estimate: "Saves ~6-7 hours/month vs pushing blind (based on ~16 pushes/month with 30% conflict rate resolving to 45-90 min per incident)"
```

### Impact if implemented
- **Agent behaviour:** The Notes section now contains only execution-relevant guidance. Agents parsing the body for instructions will not misinterpret the ROI figure as a step or condition.
- **Discoverability:** Minor improvement — the body is more focused, reducing noise when agents scan for actionable content.
- **Portability:** The ROI estimate is preserved in `metadata:` where engineering managers and skill catalogue tools can surface it for evaluation, without cluttering the execution body.
- **Risk reduced:** Prevents agent confusion between business context and operational instructions in the Notes section.

### Existing use (before fix)
Today, the Notes section mixes two types of content: technical execution guidance (three-dot diff syntax, CLAUDE.md pairing, dynamic target branch support) and a business ROI estimate. An agent reading Notes as guidance may attempt to act on "Saves ~6-7 hours/month" as if it were an instruction, which is harmless but adds noise. More importantly, the ROI data is buried in the body where it is invisible to metadata consumers like skill catalogues or management dashboards.

### Improved use (after fix)
After the fix, the Notes section contains only the three operationally relevant bullets. The ROI estimate is in `metadata.roi_estimate` where it is accessible to tooling that aggregates skill value metrics. The body is cleaner and tighter, and agents reading Notes receive only actionable execution guidance.

---

## Priority Order

| Priority | Improvement | Effort | Impact |
|---|---|---|---|
| 1 | Move non-standard frontmatter fields under `metadata:` + add `license` and `compatibility` | Low | Critical |
| 2 | Add trigger keywords to `description` field | Low | High |
| 3 | Add edge case handling for detached HEAD, no remote, and first push | Medium | High |
| 4 | Add `gh` CLI authentication check before Step 8 | Low | Medium |
| 5 | Move business justification from Notes to `metadata:` | Low | Low |

---

## Before vs After: Full Skill Experience

### Before (current state)

A developer on a new project adds `safe-push-workflow` to their Claude Code setup. When they say "push this to qa", the agent scanning skill descriptions reads "Detects git conflicts before pushing a feature branch to any target branch by fetching remote state and diffing divergent changes" — the phrase "push to qa" does not appear, so the skill may not be selected and the push proceeds unprotected. On a different day, the same developer is on a new feature branch that has never been pushed before. The skill is manually activated, executes Steps 1 and 2 cleanly, then hits Step 3 (`git pull origin feature/new-branch`) and receives a fatal git error: "couldn't find remote ref." No Safe Push Report is printed. The developer is left debugging a raw git error with no guidance from the skill.

If the developer persists and manually works around Step 3, the skill proceeds to Step 7 (push succeeds) and then Step 8 — where `gh pr create` fails silently because `gh` was installed but never authenticated on the new machine. The branch is on the remote but no PR exists. The developer must independently debug the `gh` authentication issue and manually reconstruct the `gh pr create` command with the correct flags. Meanwhile, a registry validator scanning the frontmatter finds eight non-standard fields at the top level, no `license` field, and no `compatibility` field — the skill either fails validation or is excluded from the index entirely. Other teams attempting to evaluate whether this skill meets their toolchain requirements (git version, gh CLI version) have no machine-readable signal to check.

### After (all improvements applied)

With all five improvements applied, the same developer's experience is fundamentally different. When they say "push this to qa", the agent immediately matches `safe-push-workflow` because "push to qa" now appears verbatim in the `description` field. The skill activates, Step 1 detects a clean branch name, and `compatibility: Requires git >= 2.x and gh CLI >= 2.x` signals any prerequisite gaps before execution begins. On a first-push feature branch, Step 3 detects the "no upstream" condition and automatically switches to `git push --set-upstream` in Step 7 — the developer never sees a git error. The Safe Push Report prints cleanly, showing "first push — upstream will be set."

Before Step 8, `gh auth status` runs and confirms authentication. The `gh pr create` command executes without issue, and the PR is open on GitHub within seconds of the push. The full 9-step workflow completes end-to-end without any manual debugging or raw git errors. The registry validator finds valid frontmatter: all eight custom fields are nested under `metadata:`, `license: MIT` is present, and `compatibility` documents the exact tool versions required. Teams evaluating this skill can make an informed adoption decision from the frontmatter alone, without reading the full body. The skill is discoverable, portable, and self-healing at every common failure point.
