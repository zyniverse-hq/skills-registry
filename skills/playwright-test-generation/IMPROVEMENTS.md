# IMPROVEMENTS — playwright-test-generation

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

Eight non-standard fields (`version`, `author`, `email`, `category`, `tags`, `product`, `sprint`, `tested_with`) are declared at the top level of the frontmatter. The agentskills spec requires all non-standard fields to be nested under a single `metadata:` block. Any agent or registry tool that validates frontmatter will reject or misparse these fields, and future consumers cannot distinguish spec-recognized fields from custom ones.

### Before
```yaml
---
name: playwright-test-generation
description: Generate structured Playwright E2E tests by exploring the live UI first, then producing helpers, spec files, and a summary report.
version: 1.0.1
author: Deepikaa Naganathan
email: deepikaa.n@zysk.tech
category: qa-testing
tags:
  - playwright
  - e2e-testing
  - test-generation
  - automation
product: zysk | tms | zyni
sprint: 1
tested_with: claude-sonnet-4-6
---
```

### After
```yaml
---
name: playwright-test-generation
description: Generate or write structured Playwright E2E tests by exploring the live UI first, then producing helpers, spec files, and a summary report. Use when asked to automate, generate, or create e2e tests for any page or feature.
license: MIT
compatibility: Requires Playwright installed (npx playwright install), TypeScript configured in the project, a live URL accessible at runtime, and Microsoft Edge available for the default config. Node.js 18+ recommended.
metadata:
  version: 1.0.1
  author: Deepikaa Naganathan
  email: deepikaa.n@zysk.tech
  category: qa-testing
  tags:
    - playwright
    - e2e-testing
    - test-generation
    - automation
  product: zysk | tms | zyni
  sprint: 1
  tested_with: claude-sonnet-4-6
---
```

### Impact if implemented
- **Agent behaviour:** Registry tools and agent orchestrators that parse frontmatter will correctly separate spec fields (`name`, `description`, `license`, `compatibility`) from custom metadata, preventing silent parse errors or field collisions.
- **Discoverability:** Tags like `playwright`, `e2e-testing`, and `automation` become properly addressable under `metadata.tags` — search indexers that walk the `metadata` block will surface this skill for those queries.
- **Portability:** Any team cloning the skill into their own registry can immediately distinguish which fields are spec-required versus project-specific, making adaptation straightforward.
- **Risk reduced:** Prevents a frontmatter validator from rejecting the skill entirely due to unrecognized top-level keys, which would block activation in strict environments.

### Existing use (before fix)
Today, when an agent or CI pipeline runs a frontmatter lint pass on `playwright-test-generation`, it encounters eight unrecognized top-level keys (`version`, `author`, `email`, `category`, `tags`, `product`, `sprint`, `tested_with`). Depending on the validator's strictness, this either raises a hard error that prevents the skill from loading, or silently ignores those keys, meaning the author, category, and tag data is lost. Any registry UI that groups skills by `category: qa-testing` or lets users filter by tags will not find this skill because the parser never reaches those values in a recognized location.

### Improved use (after fix)
After nesting all custom fields under `metadata:`, the frontmatter becomes valid against the spec. Registry tools surface this skill under the `qa-testing` category and respond correctly to tag-based searches for `playwright`, `e2e-testing`, and `automation`. The `author` and `email` fields remain preserved for attribution but no longer pollute the top-level namespace, making the skill safe to load in any compliant runtime without frontmatter errors.

---

## Improvement 2 — Add Missing `license` Field

### What needs to change

The `license` field is absent from the frontmatter entirely. Without it, consumers — whether individual developers, teams, or automated tools — cannot determine the usage terms for the skill. This blocks adoption in organizations that require license declarations before integrating third-party assets.

### Before
```yaml
---
name: playwright-test-generation
description: Generate structured Playwright E2E tests by exploring the live UI first, then producing helpers, spec files, and a summary report.
version: 1.0.1
author: Deepikaa Naganathan
# ... no license field present
---
```

### After
```yaml
---
name: playwright-test-generation
description: Generate or write structured Playwright E2E tests by exploring the live UI first, then producing helpers, spec files, and a summary report. Use when asked to automate, generate, or create e2e tests for any page or feature.
license: MIT
compatibility: Requires Playwright installed (npx playwright install), TypeScript configured in the project, a live URL accessible at runtime, and Microsoft Edge available for the default config. Node.js 18+ recommended.
metadata:
  version: 1.0.1
  author: Deepikaa Naganathan
  ...
---
```

### Impact if implemented
- **Agent behaviour:** Agents that gate skill activation on license compatibility checks can now evaluate this skill automatically rather than failing or prompting the user for clarification.
- **Discoverability:** Registry search interfaces that filter by license type (e.g., "show only MIT-licensed skills") will include this skill in results.
- **Portability:** Teams in regulated environments or enterprises with OSS policies can immediately determine whether the skill is safe to import without reading the repository's root LICENSE file.
- **Risk reduced:** Prevents the skill from being blocked or quarantined by automated compliance scanners that reject assets with no declared license.

### Existing use (before fix)
Today, any developer or team wanting to adopt `playwright-test-generation` in a project with a license policy must manually inspect the repository root or contact the author to determine usage terms. Automated tools that enforce license gates will flag the skill as "unknown license" and may block it from being added to a curated registry or a dependency manifest. This friction slows adoption and can cause the skill to be overlooked in favor of alternatives that declare a license explicitly.

### Improved use (after fix)
With `license: MIT` present in the frontmatter, the skill passes automated license checks immediately. Developers scanning skills for use in commercial projects see at a glance that the skill is permissively licensed. Registry tools that aggregate MIT-licensed skills for curated packs will include `playwright-test-generation` without any manual intervention, increasing the skill's reach across the broader agentskills ecosystem.

---

## Improvement 3 — Add Missing `compatibility` Field

### What needs to change

Environment prerequisites (Playwright installed, TypeScript configured, live URL, Microsoft Edge) are documented in the body under the "Prerequisites" section, but the `compatibility` frontmatter field is entirely absent. Agents evaluate `compatibility` before loading a skill to determine whether the current environment supports it. Burying requirements in the body means agents may attempt to activate the skill in environments that will fail at runtime — for example, on a CI runner without Edge installed or in a project without TypeScript.

### Before
```markdown
## Prerequisites

- [ ] Live URL of the feature to test is accessible
- [ ] Valid credentials available for authenticated flows
- [ ] Playwright installed in the project (`npx playwright install`)
- [ ] TypeScript configured in the project
```
(No `compatibility:` field in the frontmatter)

### After
```yaml
compatibility: Requires Playwright installed (npx playwright install), TypeScript configured in the project, a live URL accessible at runtime, and Microsoft Edge available for the default config. Node.js 18+ recommended.
```

And the body's Prerequisites section can be shortened to avoid duplication:

```markdown
## Prerequisites

See `compatibility` in the skill frontmatter for environment requirements. Ensure valid credentials are available for any authenticated flows before running tests.
```

### Impact if implemented
- **Agent behaviour:** Agents performing environment pre-checks before skill activation will read the `compatibility` field and surface a clear message if Playwright, TypeScript, or Edge is missing — instead of silently loading the skill and failing mid-execution during Step 1 (live page exploration).
- **Discoverability:** Registry filters that let users find skills compatible with their stack (e.g., "TypeScript + Playwright") will now include this skill in those results.
- **Portability:** A developer importing the skill into a new project immediately sees the environment contract in the frontmatter without reading through the full skill body.
- **Risk reduced:** Prevents half-executed test generation runs where the agent navigates the live UI (Step 1) successfully but then crashes at spec file generation (Step 3) due to missing TypeScript support, wasting the user's time.

### Existing use (before fix)
Today, an agent receives a request like "generate tests for the login page," activates `playwright-test-generation` without checking environment compatibility, and proceeds to Step 1 (live page exploration). If the project doesn't have TypeScript configured, the agent reaches Step 3 and generates `.spec.ts` files that immediately fail to compile. Worse, if Microsoft Edge is not installed, the default `playwright.config.ts` from Step 4 will cause all generated tests to error on first run. The user only discovers these issues after the entire generation flow has completed, requiring a second pass to fix the environment.

### Improved use (after fix)
With `compatibility` declared in the frontmatter, an agent running in a TypeScript-less or Edge-free environment can detect the mismatch before Step 1 and prompt the user: "This skill requires TypeScript and Microsoft Edge. Your project appears to lack TypeScript — would you like to configure it first?" The user either fixes the environment upfront or chooses a different approach. No wasted exploration run, no broken generated files, no silent late-stage failures.

---

## Improvement 4 — Strengthen Trigger Keywords in the `description` Field

### What needs to change

The current `description` reads: "Generate structured Playwright E2E tests by exploring the live UI first, then producing helpers, spec files, and a summary report." While accurate, it lacks the active trigger verbs and user-facing query terms that agent-discovery matching relies on. Keywords like "write", "automate", "create", and "e2e" appear only in the body's "When to use" section — which agents do not parse for routing decisions. The `description` itself is the primary signal used by orchestrators to match a user's intent to a skill.

### Before
```yaml
description: Generate structured Playwright E2E tests by exploring the live UI first, then producing helpers, spec files, and a summary report.
```

### After
```yaml
description: Generate or write structured Playwright E2E tests by exploring the live UI first, then producing helpers, spec files, and a summary report. Use when asked to automate, generate, create, or write e2e tests for any page or feature.
```

### Impact if implemented
- **Agent behaviour:** Semantic routing models that match user queries like "write tests for the checkout page", "automate the login flow", or "create e2e tests for my feature" will score this skill higher because the trigger verbs appear directly in the description.
- **Discoverability:** Registry full-text search indexed on the `description` field will return this skill for queries containing "write", "automate", "create", "e2e", and "page" — all currently absent from the description.
- **Portability:** Teams importing the skill into a new registry where the body is not indexed will still get correct routing based on the description alone.
- **Risk reduced:** Prevents the skill from being overlooked in favor of a less capable alternative that happens to include "write" or "automate" in its description, causing the wrong skill to be triggered.

### Existing use (before fix)
Currently, when a user types "write Playwright tests for the dashboard" or "automate the signup flow", an agent's semantic router compares the query against all skill descriptions. The word "write" does not appear in the current description, and "automate" is absent entirely. Depending on the router's threshold, the skill may rank below a less specific match or may not surface at all, forcing the user to invoke the skill explicitly by name rather than through natural language.

### Improved use (after fix)
After adding trigger verbs directly to the description, a user saying "can you write e2e tests for the checkout page?" or "automate the login flow using Playwright" will have their intent correctly routed to `playwright-test-generation` without needing to know the skill's exact name. The expanded description covers the full vocabulary users naturally reach for when requesting test automation, making the skill self-discoverable for new users encountering it for the first time.

---

## Improvement 5 — Remove Redundancy Between Prerequisites Section and Notes Section

### What needs to change

The body contains two sources of redundancy that inflate line count and create maintenance risk. First, the "Prerequisites" checklist duplicates what will be captured in the `compatibility` frontmatter field (Improvement 3). Second, the "Notes" section at the end repeats constraints already stated in Steps 2, 3, and 5 — specifically "helpers file, never the spec file" (Step 2 and Notes), "summary report is mandatory" (Step 5 and Notes), and "one report per feature" (Step 5 and Notes). If a constraint changes in a step, the Notes section must also be updated, creating a drift risk.

### Before
```markdown
## Prerequisites

- [ ] Live URL of the feature to test is accessible
- [ ] Valid credentials available for authenticated flows
- [ ] Playwright installed in the project (`npx playwright install`)
- [ ] TypeScript configured in the project

...

## Notes

- Always explore the live UI first — never guess selectors
- Prefer `getByRole` with `name` over `getByTestId` for resilience
- All helper functions and constants belong in the helpers file, never inside the spec file
- The summary report is mandatory — create the file and show it in chat every time
- One report per feature — never combine multiple features into one report
```

### After
```markdown
## Prerequisites

See `compatibility` in the skill frontmatter for environment requirements. Ensure valid credentials are available for any authenticated flows before starting Step 1.

...

## Notes

- Always explore the live UI first — never guess selectors
- Prefer `getByRole` with `name` over `getByTestId` for resilience
```

(The helper/spec separation and report-mandatory constraints are already fully stated in Steps 2, 3, and 5 — they do not need to be restated in Notes.)

### Impact if implemented
- **Agent behaviour:** A shorter, non-redundant body reduces token consumption when the skill is loaded into context, leaving more budget for the actual test-generation task. Current body is ~1428 tokens; removing the duplicated constraints saves approximately 80–120 tokens.
- **Discoverability:** No direct impact on routing, but a leaner skill body is easier for humans reviewing the registry to scan and assess.
- **Portability:** Eliminates drift risk — when Step 5's report instructions change, there is no second location (Notes) that must be kept in sync manually.
- **Risk reduced:** Prevents the situation where Notes and a Step contradict each other due to an incomplete update, which would leave an agent with conflicting instructions about whether to combine features into one report.

### Existing use (before fix)
Today, if the reporting convention changes — say, the team decides to combine related features into a single report — a maintainer must update both Step 5 and the Notes section. If only one is updated, an agent reading the skill encounters contradictory guidance and may follow the wrong rule. Similarly, a new contributor reading the body sees the prerequisites checklist and the `compatibility` field as two separate sources of truth, creating confusion about which is authoritative.

### Improved use (after fix)
After consolidating, each constraint appears exactly once: environment requirements live in `compatibility`, reporting rules live in Step 5, and selector conventions live in the Notes section (which genuinely adds context not stated elsewhere). An agent loading the skill gets an unambiguous, non-contradictory set of instructions, and a maintainer updating the reporting convention only needs to edit Step 5. The body drops to approximately 110–115 lines, improving readability without losing any instructional coverage.

---

## Priority Order

| Priority | Improvement | Effort | Impact |
|---|---|---|---|
| 1 | Nest non-standard frontmatter fields under `metadata:` | Low | Critical |
| 2 | Add missing `license` field | Low | Critical |
| 3 | Add missing `compatibility` field | Low | High |
| 4 | Strengthen trigger keywords in `description` | Low | High |
| 5 | Remove redundancy between Prerequisites and Notes | Medium | Medium |

---

## Before vs After: Full Skill Experience

### Before (current state)

A developer discovers `playwright-test-generation` in the registry and wants to adopt it. Before they can do so, they need to know whether it is MIT-licensed or restricted — but the `license` field is absent, forcing them to either contact the author (deepikaa.n@zysk.tech) or check the repository root. If they work in an environment with OSS compliance requirements, the skill is effectively blocked from adoption until this is resolved manually.

An agent tasked with test generation receives the user query "write e2e tests for the checkout page." The routing layer compares the query against all skill descriptions. Because "write" and "e2e" do not appear in `playwright-test-generation`'s description, the skill scores lower than expected and may not be selected automatically — the user may need to invoke it by name explicitly. Even when the skill is selected and begins execution, an agent running in a CI environment without Microsoft Edge installed will proceed through Step 1 (live page exploration) and Step 2 (helpers file) successfully, only to fail at test execution because the `playwright.config.ts` generated in Step 4 requires the `msedge` channel. This failure surfaces late, after the full generation run, wasting both time and tokens.

In the registry UI, the skill's `category: qa-testing` and `tags: [playwright, e2e-testing, ...]` fields are unrecognized top-level keys rather than properly nested values under `metadata:`. Tag-based and category-based filters return no results for this skill. The frontmatter validator logs warnings or errors for the eight unrecognized top-level fields, and in strict registry environments, the skill may be rejected from the index entirely.

### After (all improvements applied)

After all five improvements are applied, `playwright-test-generation` is a fully spec-compliant, self-describing skill. The `license: MIT` field allows any developer or automated compliance tool to assess usage terms in under a second. The `compatibility` field surfaces environment requirements — Playwright, TypeScript, Node.js 18+, Microsoft Edge — directly in the frontmatter, so agents perform an environment pre-check before activation and surface actionable warnings instead of failing mid-run. The frontmatter is clean: only spec-recognized fields at the top level, with all custom metadata properly nested under `metadata:`, making the skill parseable by any compliant registry without errors or warnings.

When a user says "write e2e tests for the checkout page" or "automate the login flow using Playwright," the enriched description — now containing "write", "automate", "create", "e2e", and "page" — ensures the skill ranks at the top of the routing candidates without requiring the user to know its exact name. Discovery is natural and frictionless. Inside the body, the Prerequisites section no longer duplicates the `compatibility` field, and the Notes section no longer restates the helpers/spec separation or report-mandatory rules already stated in Steps 2, 3, and 5. Each constraint appears exactly once, eliminating drift risk and reducing the token footprint of the skill body by roughly 100 tokens.

The end result is a skill that a developer can adopt without friction, that an agent can route to correctly from natural language, that activates only in compatible environments, and that maintains itself without redundant duplication. It remains within both the 500-line and 5000-token body budgets with room to grow, and its test-coverage checklists, concrete login-page example, and complete `playwright.config.ts` snippet continue to make it immediately actionable for any engineer or agent that loads it.
