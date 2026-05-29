# IMPROVEMENTS — ship-issue

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

## Improvement 1 — Nest Non-Standard Frontmatter Fields Under `metadata:`

### What needs to change
Nine non-standard frontmatter fields (`version`, `author`, `email`, `category`, `tags`, `product`, `sprint`, `tested_with`, `user-invocable`) are declared at the top level of the frontmatter block. The agentskills.io spec requires all non-standard fields to be nested under a `metadata:` key. This is a direct spec violation that affects registry parsing and field validation.

### Before
```yaml
---
name: ship-issue
description: "Executes a single GitHub issue end-to-end on one of three tracks (quick-fix / clear-scope / ambiguous) with mandatory first-principles, self-review, simplify, verify, and board-move discipline."
version: 1.0.0
author: Varun U
email: varun@zysk.tech
category: engineering-practice
tags:
  - github-issues
  - workflow
  - pr-creation
  - code-review
  - tdd
product: tms
sprint: 4
tested_with: claude-opus-4-7
user-invocable: true
---
```

### After
```yaml
---
name: ship-issue
description: "Ship a single GitHub issue end-to-end (quick-fix / clear-scope / ambiguous track). Use when asked to implement, fix, or ship a ticket, start work on an issue, or pick up a backlog item. Enforces self-review, simplify, verify, and board-move discipline on every run."
license: MIT
compatibility: "Requires: gh CLI, Node.js + npm (npx tsc, npm run lint/format/test), git with worktree support, GitHub Projects v2, companion skills: pr-review-toolkit, superpowers, decision-brief, handle-review"
metadata:
  version: 1.0.0
  author: Varun U
  email: varun@zysk.tech
  category: engineering-practice
  tags:
    - github-issues
    - workflow
    - pr-creation
    - code-review
    - tdd
  product: tms
  sprint: 4
  tested_with: claude-opus-4-7
  user-invocable: true
---
```

### Impact if implemented
- **Agent behaviour:** Registry parsers and validators can correctly distinguish standard spec fields from project-specific metadata, preventing field-collision errors during indexing.
- **Discoverability:** Tags like `github-issues`, `workflow`, `pr-creation` become properly indexed under the standard `metadata.tags` path, making the skill searchable via tag-based queries in the registry.
- **Portability:** Consumers who adopt the skill from the registry can strip or override `metadata.product` and `metadata.sprint` without risking interference with spec-required fields.
- **Risk reduced:** Eliminates registry parse failures caused by unexpected top-level keys, which can cause the skill to be skipped or mis-categorised during automated indexing.

### Existing use (before fix)
Today, when a registry indexer processes `ship-issue/SKILL.md`, it encounters nine unexpected top-level keys alongside `name` and `description`. Depending on the indexer's strictness, this either raises a validation error (skill is rejected entirely) or silently discards the unrecognised keys. In either case, the tag list (`github-issues`, `workflow`, etc.) and the `tested_with: claude-opus-4-7` signal are not stored in a queryable location, so tag-based searches for "workflow" skills do not surface this skill. The `product: tms` and `sprint: 4` fields at the top level are invisible dead weight to every team that is not on the TMS project.

### Improved use (after fix)
After the fix, the frontmatter is a clean two-level structure: spec-standard keys at the root, project-specific context under `metadata:`. The registry indexes `metadata.tags` correctly, so a search for "pr-creation" or "code-review" returns this skill. A consumer from a different project can glance at `metadata.product: tms` and `metadata.sprint: 4` and understand these are internal scoping fields that do not affect the skill's behaviour — they can adopt the skill without confusion about whether `product` or `sprint` influences execution logic.

---

## Improvement 2 — Add Required `license` Field

### What needs to change
The `license` field is absent from the frontmatter entirely. The agentskills.io spec quality standard requires all skills to declare their licensing terms so consumers understand the usage rights before adopting a skill from a shared registry.

### Before
```yaml
---
name: ship-issue
description: "Executes a single GitHub issue end-to-end..."
version: 1.0.0
author: Varun U
# ... no license field anywhere
---
```

### After
```yaml
---
name: ship-issue
description: "..."
license: MIT
compatibility: "..."
metadata:
  ...
---
```

### Impact if implemented
- **Agent behaviour:** No runtime change — `license` is a registry-level metadata field, not an execution directive. However, automated compliance checks in the registry pipeline will pass instead of flagging the skill as incomplete.
- **Discoverability:** Skills without a `license` field may be filtered out by registry consumers that only surface openly-licensed skills for adoption. Adding `license: MIT` makes the skill eligible for inclusion in those filtered views.
- **Portability:** Any team evaluating whether to adopt `ship-issue` in their own project now has a clear, machine-readable answer to "can we use this?" without needing to contact the author.
- **Risk reduced:** Prevents legal ambiguity for teams that have open-source compliance policies. Without a declared license, the default in many jurisdictions is "all rights reserved," which could block adoption entirely.

### Existing use (before fix)
Today, a developer at a different company browsing the shared skills registry sees `ship-issue` authored by `varun@zysk.tech` with no license field. Their legal/compliance tooling flags the skill as unlicensed. Either the skill is blocked from adoption, or the developer must manually reach out to the author to confirm usage rights — friction that defeats the purpose of a shared registry. Registry quality checks also fail for this skill, potentially preventing it from appearing in curated "production-ready" skill lists.

### Improved use (after fix)
After adding `license: MIT`, the skill passes all registry quality gates. Automated compliance tools at any consuming organisation can verify usage rights in milliseconds. The skill appears in filtered views that restrict to permissively licensed content. No manual legal review is needed before a team adopts and extends the skill for their own issue-shipping workflow.

---

## Improvement 3 — Add Required `compatibility` Field Documenting External Dependencies

### What needs to change
The skill invokes `gh` CLI, `npx tsc`, `npm run lint`, `npm run format:check`, `npm run test:run`, git worktrees, GitHub Projects v2 GraphQL mutations, and five companion skills (`pr-review-toolkit:code-reviewer`, `pr-review-toolkit:silent-failure-hunter`, `superpowers:writing-plans`, `superpowers:receiving-code-review`, `decision-brief`). None of these prerequisites are declared in a `compatibility` field, leaving consumers to discover dependency failures at runtime rather than before adoption.

### Before
```yaml
---
name: ship-issue
description: "Executes a single GitHub issue end-to-end..."
# No compatibility field
---
```

### After
```yaml
---
name: ship-issue
description: "..."
license: MIT
compatibility: "Requires: gh CLI (authenticated), Node.js + npm (npx tsc, npm run lint, npm run format:check, npm run test:run), git >= 2.5 (worktree support), GitHub Projects v2 with Status field configured; companion skills: pr-review-toolkit (code-reviewer + silent-failure-hunter), superpowers (writing-plans + receiving-code-review), decision-brief, handle-review"
---
```

### Impact if implemented
- **Agent behaviour:** An orchestrating agent (e.g., `/auto-ship`) can pre-flight check whether all prerequisites are available before invoking `ship-issue`, surfacing a clear error ("gh CLI not authenticated") rather than a cryptic mid-step failure.
- **Discoverability:** Consumers searching for skills compatible with their stack (Node.js, GitHub) can filter by `compatibility` contents. A team that does not use GitHub Projects v2 can see up front that the board-move steps will not work for them.
- **Portability:** Eliminates the hidden "works on the author's machine" problem. A new adopter reads the `compatibility` field and knows exactly what to provision before the first run.
- **Risk reduced:** Prevents silent mid-execution failures on step 8 (board move GraphQL mutation fails silently if Projects v2 is not configured) and step 9 (verify step fails if `npm run test:run` is not in `package.json`).

### Existing use (before fix)
Today, a developer adopts `ship-issue` on a project that uses Jira (not GitHub Projects) and Python (not Node.js). They invoke the skill on issue #42. Steps 1–4 succeed. Step 5 (self-review) calls `pr-review-toolkit:code-reviewer` — if that companion skill is not installed, the invocation fails silently or errors. Step 7 runs `npx tsc --noEmit` on a Python repo — it errors. Step 8 runs the GitHub Projects v2 GraphQL board move — it fails because there is no Projects v2 board. None of these failures were predictable from reading the frontmatter alone. The developer wasted time on a partially-executed workflow.

### Improved use (after fix)
After adding the `compatibility` field, the developer reads it before adopting the skill and immediately sees "GitHub Projects v2 with Status field configured" and "companion skills: pr-review-toolkit, superpowers." They know this skill is not a fit for their Jira/Python stack without running a single step. If they are on a compatible stack, the preflight checklist is explicit: authenticate `gh`, confirm `npm run test:run` is in `package.json`, install the four companion skills. When `/auto-ship` invokes `ship-issue`, it can programmatically parse the `compatibility` field and abort with a helpful error message before any steps execute.

---

## Improvement 4 — Strengthen Trigger Keywords in `description` for Agent Discoverability

### What needs to change
The current `description` is written in implementation language ("Executes a single GitHub issue end-to-end on one of three tracks..."). While accurate, it does not include the natural-language phrases a user or orchestrating agent would actually say when they want this skill. Phrases like "ship issue #42", "implement this ticket", "start work on", "fix this bug from the board", or "pick up issue" are absent. An agent doing semantic matching against user input like "ship issue #2779" has to infer the match — it is not explicit.

### Before
```
description: "Executes a single GitHub issue end-to-end on one of three tracks (quick-fix / clear-scope / ambiguous) with mandatory first-principles, self-review, simplify, verify, and board-move discipline."
```

### After
```
description: "Ship a single GitHub issue end-to-end (quick-fix / clear-scope / ambiguous track). Use when asked to implement, fix, or ship a ticket, start work on an issue, pick up a backlog item, or resolve a GitHub issue. Enforces first-principles check, self-review, simplify, verify, and board-move discipline on every run."
```

### Impact if implemented
- **Agent behaviour:** Semantic skill-selection agents match user utterances ("ship issue #42", "implement this ticket", "start work on issue", "fix this from the board") directly to the description, reducing false-negative misses where the correct skill is available but not selected.
- **Discoverability:** Registry full-text search surfaces this skill for queries like "ship ticket", "implement issue", "start on backlog item" — none of which would have matched the original description.
- **Portability:** Teams adopting the skill can verify at a glance whether the trigger condition matches their workflow vocabulary (GitHub-centric teams use "issue"; Jira teams use "ticket" — the updated description covers both).
- **Risk reduced:** Prevents the failure mode where a user says "implement issue #42" and the agent selects a generic `dev-assistant` skill instead of the disciplined `ship-issue` workflow, bypassing the mandatory self-review and board-move steps entirely.

### Existing use (before fix)
Today, a user invokes their Claude Code session with "implement issue #42 from the backlog." The agent's skill matcher compares that phrase against `description: "Executes a single GitHub issue end-to-end..."`. The word "implement" does not appear; "issue" appears once but in implementation context, not trigger context. The matcher may fall back to `dev-assistant` or ask the user to clarify. The user who knows about `ship-issue` must explicitly type `/ship-issue` rather than relying on natural-language routing. The disciplined three-track workflow with mandatory self-review is bypassed silently.

### Improved use (after fix)
After updating the description to include "Ship a single GitHub issue", "implement, fix, or ship a ticket", "start work on an issue", and "pick up a backlog item", the semantic matcher correctly routes "implement issue #42" and "ship issue #2779" to this skill without user intervention. The mandatory self-review, simplify, verify, and board-move steps are guaranteed to execute because the right skill was selected. Teams that have standardised on `/ship-issue` discipline can rely on natural-language invocation working correctly for all team members, not just those who know the slash command.

---

## Improvement 5 — Remove or Scope Project-Specific Fields (`product`, `sprint`, `email`)

### What needs to change
The fields `product: tms`, `sprint: 4`, and `email: varun@zysk.tech` are project-specific internal metadata from the TMS project at zysk.tech. In a shared skills registry, these fields convey no value to other consumers and actively reduce portability by implying the skill is scoped to a specific product and sprint. The `email` field in a shared registry artifact is a personal contact that belongs in a CONTRIBUTORS file, not in every consumer's copy of the skill.

### Before
```yaml
product: tms
sprint: 4
email: varun@zysk.tech
```
(all at the top level, as shown in the current frontmatter)

### After
```yaml
metadata:
  version: 1.0.0
  author: Varun U
  category: engineering-practice
  tags:
    - github-issues
    - workflow
    - pr-creation
    - code-review
    - tdd
  tested_with: claude-opus-4-7
  user-invocable: true
  # product, sprint, email removed from shared registry copy
  # Maintainer contact: see CONTRIBUTORS.md in the skills-registry root
```

### Impact if implemented
- **Agent behaviour:** No runtime change — these fields are not read during skill execution. However, removing them prevents a hypothetical future agent from misinterpreting `product: tms` as a scope restriction ("this skill only applies to the TMS product").
- **Discoverability:** Skills with project-specific identifiers like `sprint: 4` signal "this may be stale" to evaluators. Removing them makes the skill appear current and general-purpose to registry browsers.
- **Portability:** A team adopting `ship-issue` no longer needs to decide whether to delete `product: tms` and `sprint: 4` from their local copy. The skill is clean out of the box.
- **Risk reduced:** Prevents confusion about whether `sprint: 4` means the skill was last verified in Sprint 4 (implying it may be outdated) or is scoped to Sprint 4 (implying it should not be used in Sprint 5+).

### Existing use (before fix)
A developer at a company unrelated to zysk.tech or TMS downloads `ship-issue` from the registry. They see `product: tms` and `sprint: 4` at the top level of the frontmatter. They are unsure: is this skill only tested against the TMS codebase? Is `sprint: 4` a version indicator or a scope restriction? They ping the author at `varun@zysk.tech` for clarification — friction that should not exist for a shared, general-purpose skill. They may abandon adoption in favour of a skill with cleaner metadata.

### Improved use (after fix)
After removing the project-specific fields from the shared registry copy, the skill reads as general-purpose engineering practice. A consumer from any organisation sees `category: engineering-practice`, `tags: [github-issues, workflow, pr-creation, code-review, tdd]`, `tested_with: claude-opus-4-7`, and `user-invocable: true` — all of which are universally meaningful. If the original TMS team needs to track product/sprint in their local copy, they can add those fields back under `metadata:` in their fork without polluting the shared registry.

---

## Priority Order

| Priority | Improvement | Effort | Impact |
|---|---|---|---|
| 1 | Nest non-standard frontmatter fields under `metadata:` | Low | Critical |
| 2 | Add required `license` field | Low | Critical |
| 3 | Add required `compatibility` field documenting external dependencies | Low | High |
| 4 | Strengthen trigger keywords in `description` for agent discoverability | Low | High |
| 5 | Remove or scope project-specific fields (`product`, `sprint`, `email`) | Low | Medium |

---

## Before vs After: Full Skill Experience

### Before (current state)

A developer on a new project finds `ship-issue` in the shared skills registry and wants to adopt it. The first thing they see is a frontmatter block with nine non-standard fields scattered at the top level alongside `name` and `description`. There is no `license` field, so their organisation's open-source compliance tooling flags the skill as unlicensed and blocks adoption until someone manually contacts `varun@zysk.tech`. If they push through that friction, they still have no `compatibility` field — they cannot tell from the frontmatter alone that the skill requires `gh` CLI authentication, `npm run test:run` in their `package.json`, GitHub Projects v2 with a configured Status field, and four companion skills (`pr-review-toolkit`, `superpowers`, `decision-brief`, `handle-review`). They invoke the skill, steps 1–4 run fine, and then the verify step (`npx tsc --noEmit`) fails silently on their Python repo. The board-move GraphQL mutation fails because they use Jira. Half-executed, the issue is stuck in "In Progress" on a board that never moves.

For users who are already on a compatible stack, natural-language routing is unreliable. Saying "implement issue #42" may not trigger `ship-issue` because the description uses implementation language ("Executes a single GitHub issue") rather than trigger language ("ship", "implement", "start work on"). The agent selects `dev-assistant` instead, bypassing the mandatory self-review, simplify, and verify guards entirely. The developer gets code shipped without the disciplined three-track workflow — the entire purpose of the skill is silently defeated. The `product: tms` and `sprint: 4` fields at the top level add noise for every consumer who is not on the TMS/Sprint 4 project, raising unanswered questions about whether the skill is still current or is scoped to a specific project iteration.

### After (all improvements applied)

After all five improvements are applied, the skill frontmatter is a clean, spec-compliant two-level structure. The `license: MIT` field is present and machine-readable, so compliance tooling passes immediately. The `compatibility` field enumerates every external dependency — `gh` CLI, Node.js + npm, git worktree support, GitHub Projects v2, and all four companion skills — so a developer can evaluate fit before adopting, and an orchestrating agent like `/auto-ship` can pre-flight check prerequisites and surface a clear error rather than a mid-step failure. All nine non-standard fields are correctly nested under `metadata:`, making the frontmatter parse cleanly in any spec-compliant registry tool.

The updated `description` now includes natural-language trigger phrases: "ship a single GitHub issue", "implement, fix, or ship a ticket", "start work on an issue", "pick up a backlog item." A user who says "implement issue #42" is reliably routed to `ship-issue` by semantic skill-selection, ensuring the mandatory self-review, simplify, verify, and board-move guards are always executed. The project-specific fields `product: tms`, `sprint: 4`, and `email: varun@zysk.tech` are removed from the shared registry copy, so every consumer sees a clean, general-purpose engineering-practice skill with no ambiguity about scope or staleness. Teams that need to track their own product/sprint context can add those fields back under `metadata:` in their local fork without affecting other consumers. The result is a fully spec-compliant, portable, discoverable skill that executes its three-track workflow reliably on any compatible stack.
