---
name: workflow-map
description: Explains the Zyniverse engineering pipeline these bundled skills compose — when to reach for each one across triage, decision, shipping, review, and merge — and the one-time marketplace prerequisite. Use to orient on the workflow or decide which skill fits the current step.
metadata:
  version: 1.0.0
  author: Varun U
  email: varun@zysk.tech
  category: engineering-practice
  tags:
    - workflow
    - pipeline
    - onboarding
    - github
  product: zysk
  tested_with: claude-opus-4-8
---

# Engineering Workflow Map

> The guide skill for the `engineering-workflow` bundle. It doesn't perform actions itself — it routes you to the right skill at each stage of the issue-to-merge pipeline.

## When to use

- Activate when: someone asks "how does our engineering workflow fit together?" or "which skill do I use for X?"
- Activate when: onboarding to the bundle and orienting on the pipeline.
- Activate when: you've finished one stage and want the next step.
- Do NOT activate when: you already know the skill you need — invoke it directly.

## Prerequisites

- [ ] The `engineering-workflow` plugin is installed (it auto-installs the registry skills below).
- [ ] **Cross-marketplace dependencies are available.** Two members (`ship-issue`, `handle-review`) rely on the `superpowers` and `pr-review-toolkit` plugins from the **`claude-plugins-official`** marketplace. Claude Code only auto-installs a cross-marketplace dependency if that marketplace is already added. If it isn't, add it once:
  - `/plugin marketplace add claude-plugins-official`
  - then re-run the install (or `/plugin install superpowers@claude-plugins-official` and `/plugin install pr-review-toolkit@claude-plugins-official`).
- [ ] `gh` CLI authenticated for the GitHub-driven stages.

## Steps

Walk the pipeline. Each stage names the skill that owns it; invoke that skill to do the work.

### 1. Triage — get issues board-ready
- **`triage-issues`** — promote `Backlog` → `Todo`, derive Priority/Area/Module, flag duplicates.

### 2. Decide — resolve ambiguity before building
- **`decision-brief`** — for ambiguous-track issues, produce a lightweight decision record and clear the `status: needs investigation` flag.

### 3. Ship — issue to PR
- **`ship-issue`** — one issue end-to-end (first-principles → plan → implement → self-review → verify → PR), with interactive checkpoints. Depends on `superpowers` + `pr-review-toolkit`.
- **`auto-ship`** — autonomous batch: drains eligible `Todo` items through `ship-issue`, records each in the merge queue, stops at PR open.

### 4. Review — handle inbound and outbound review
- **`review-queue`** — read-only digest of PRs awaiting *your* review, classified by readiness.
- **`handle-review`** — triage and resolve review comments on *your own* PR in one batch. Depends on `pr-review-toolkit`.

### 5. Merge — drain what's approved
- **`auto-merge`** — one-shot drain of the `auto-ship` queue: squash-merges what's MERGEABLE + APPROVED + clean.

## Output

- **Format:** guidance message naming the next skill to invoke.
- **Location:** inline in the conversation.
- **Example:** "You're at the review stage with comments on your own PR → use `handle-review`."

## Example

**User says:** "I've triaged the board, what's next?"
**Claude does:** Consults this map — triage is done, so the next stage is decide/ship.
**Result:** "Next: pick a Todo issue. For a clear-scope issue use `ship-issue`; to batch several autonomously use `auto-ship`. If any issue is ambiguous, run `decision-brief` first."

## Notes

- The pipeline is **directional but not rigid** — skip stages that don't apply (e.g. a trivial fix may go straight to `ship-issue`).
- This bundle is curated; the individual skills remain independently installable from the `zyniverse-skills` marketplace.
- If a member skill reports a missing dependency at runtime, it stops with an actionable message — follow it (usually the marketplace prerequisite above).
