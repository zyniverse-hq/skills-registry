# IMPROVEMENTS — test-scenario-planning

> Improvement plan derived from SKILL.md + ANALYSIS.md audit against the agentskills.openml.io spec.

---

## Quick Summary

| | Before | After |
|---|---|---|
| Spec compliance | Partially compliant | Fully compliant |
| Critical violations | 2 | 0 |
| Agent discoverability | Medium | High |
| Portability | Partial | Pass |

---

## Improvement 1 — Move non-standard frontmatter fields under `metadata:`

### What needs to change
Eight non-standard fields (`version`, `author`, `email`, `category`, `tags`, `product`, `sprint`, `tested_with`) are placed at the top level of the frontmatter. The agentskills.io spec only permits `name`, `description`, `license`, `compatibility`, `metadata`, and `allowed-tools` at top level. All custom fields must be nested under `metadata:`.

### Before
```yaml
---
name: test-scenario-planning
description: Plan high-level test scenarios that describe user behaviors and business rules before writing test code.
version: 1.0.1
author: Deepikaa Naganathan
email: deepikaa.n@zysk.tech
category: qa-testing
tags:
  - scenario-planning
  - test-strategy
  - qa
  - requirements
product: zysk | tms | zyni
sprint: 1
tested_with: claude-sonnet-4-6
---
```

### After
```yaml
---
name: test-scenario-planning
description: Plan and document high-level QA test scenarios covering user behaviors, business rules, and edge cases before writing test code. Use when asked to write scenarios for a feature, plan test coverage, create a test strategy, or define what to test.
license: MIT
compatibility: Requires Playwright MCP browser tools to be available. Tested with claude-sonnet-4-6. Outputs written to specs/ and reports/ directories relative to project root.
metadata:
  version: 1.0.1
  author: Deepikaa Naganathan
  email: deepikaa.n@zysk.tech
  category: qa-testing
  tags:
    - scenario-planning
    - test-strategy
    - qa
    - requirements
  product: zysk | tms | zyni
  sprint: 1
  tested_with: claude-sonnet-4-6
---
```

### Impact if implemented
- **Agent behaviour:** Parsers and registry tooling that validate against the spec will no longer reject this skill as malformed. Downstream consumers can safely ingest the frontmatter without encountering unexpected top-level keys.
- **Discoverability:** No direct effect on keyword matching, but a well-formed frontmatter signals registry readiness and allows indexing tools to correctly extract `metadata.tags` for faceted search.
- **Portability:** Any team consuming this skill from the registry can parse it with a compliant YAML reader without custom handling for unknown top-level fields.
- **Risk reduced:** Prevents silent parse failures in registry pipelines that validate against a strict frontmatter schema.

### Existing use (before fix)
Today, when a registry pipeline or agent harness parses `SKILL.md`, it encounters eight unexpected top-level keys (`version`, `author`, `email`, `category`, `tags`, `product`, `sprint`, `tested_with`). A strict validator rejects the skill entirely. A lenient parser silently ignores those fields, meaning metadata like `category: qa-testing` and the `tags` list are lost and never indexed. The skill author has no indication anything is wrong — the skill appears to load but is invisible to tag-based searches.

### Improved use (after fix)
After the fix, the frontmatter is fully spec-compliant. A registry validator passes the file without warnings. Tag-based searches for `scenario-planning`, `test-strategy`, or `qa` correctly surface this skill. The `metadata` block is preserved as a structured object that tooling can inspect for version tracking, author contact, and product scoping — all without polluting the top-level namespace.

---

## Improvement 2 — Add the missing `license` field

### What needs to change
The `license` field is entirely absent from the frontmatter. Without it, the skill is ambiguously licensed for any registry consumer. This is a required omission to address for shared or public registry use.

### Before
```yaml
---
name: test-scenario-planning
description: Plan high-level test scenarios that describe user behaviors and business rules before writing test code.
version: 1.0.1
author: Deepikaa Naganathan
...
---
```
*(no `license` key anywhere in the frontmatter)*

### After
```yaml
---
name: test-scenario-planning
description: ...
license: MIT
...
---
```

### Impact if implemented
- **Agent behaviour:** No direct change to how the agent executes steps, but registry consumers that gate on license presence will now accept the skill.
- **Discoverability:** Some registry indexes filter by license type; an MIT-licensed skill becomes discoverable in open-source skill searches.
- **Portability:** Other teams can safely fork, adapt, and redistribute the skill knowing the terms under which it is shared.
- **Risk reduced:** Eliminates legal ambiguity for any organisation adopting skills from the registry into their own tooling or products.

### Existing use (before fix)
Currently, any organisation scanning the registry for usable skills cannot determine the license terms for `test-scenario-planning`. A compliance-aware team would skip the skill entirely rather than risk adopting ambiguously licensed content. Registry tooling that requires a `license` field may flag the skill as incomplete or refuse to publish it.

### Improved use (after fix)
With `license: MIT` added, the skill is unambiguously open for use, modification, and redistribution. Registry validators pass it without a license-missing warning. Teams can adopt the skill with confidence, and the registry listing can surface it in license-filtered searches alongside other MIT-licensed QA skills.

---

## Improvement 3 — Add fallback behavior for inaccessible live URL

### What needs to change
Step 1 instructs the agent to use Playwright browser tools to explore the live page and lists "Live URL of the feature to explore is accessible" as a prerequisite. However, there is no guidance for what the agent should do if the URL is not accessible — the skill silently stalls. A fallback instruction must be added directly after the prerequisite check.

### Before
```markdown
## Prerequisites

- [ ] Live URL of the feature to explore is accessible
- [ ] Understanding of the feature's business purpose

## Steps

### Step 1: Understand the Feature

Use Playwright browser tools to explore the live page:
- Navigate through the full happy path
- Trigger error states, validation messages, modals
- Note distinct user goals and business rules
```

### After
```markdown
## Prerequisites

- [ ] Live URL of the feature to explore is accessible
- [ ] Understanding of the feature's business purpose

> **If no live URL is available:** Ask the user to provide a feature description, wireframes, requirements document, or user story before proceeding to Step 2. Do not attempt to plan scenarios from assumptions alone. Pause and wait for the user's input.

## Steps

### Step 1: Understand the Feature

Use Playwright browser tools to explore the live page:
- Navigate through the full happy path
- Trigger error states, validation messages, modals
- Note distinct user goals and business rules

If the live URL is inaccessible (timeout, auth wall, or not provided), stop and ask:
> "I need access to the live feature to plan accurate scenarios. Can you share a URL, wireframes, a requirements doc, or a written description of how the feature works?"
```

### Impact if implemented
- **Agent behaviour:** The agent no longer silently proceeds to invent scenarios based on the skill name alone. It halts, asks for input, and waits — producing zero scenarios rather than fabricated ones.
- **Discoverability:** No effect on discoverability.
- **Portability:** Makes the skill usable in environments where Playwright is unavailable or where only design specs exist (e.g. pre-development QA planning), by routing to the text-based fallback path.
- **Risk reduced:** Eliminates the failure mode where the agent generates 10–15 plausible-sounding but entirely fabricated scenarios for a feature it never actually observed.

### Existing use (before fix)
Today, if a user runs this skill and either forgets to provide a URL or provides one that requires authentication, the agent hits Step 1 with no live page to explore. Without a fallback instruction, the agent either errors out on the Playwright call with no recovery path, or — worse — silently falls back on its training data to invent scenarios for a generic version of the feature. The resulting scenario document looks plausible but is untethered from the actual UI, missing real validation rules, real error messages, and actual edge cases visible only in the live product.

### Improved use (after fix)
With the fallback instruction in place, the agent immediately recognises when it cannot fulfil the prerequisite and asks the user for an alternative input. The user can paste a requirements doc or describe the feature, and the agent proceeds to Step 2 using that input instead. The scenario document that results is grounded in real information rather than assumptions. The user is never left wondering why the agent stalled or why the output looks generic.

---

## Improvement 4 — Strengthen `description` with agent-discoverable trigger keywords

### What needs to change
The current `description` reads: "Plan high-level test scenarios that describe user behaviors and business rules before writing test code." This is accurate but thin on trigger phrases. Agents matching user requests like "write scenarios for X", "plan test scenarios for X", "what should I test for X", or "create a test strategy for X" may not reliably score this skill highly enough to select it over adjacent QA skills. The description should be expanded to embed the natural-language phrases users actually type.

### Before
```yaml
description: Plan high-level test scenarios that describe user behaviors and business rules before writing test code.
```

### After
```yaml
description: Plan and document high-level QA test scenarios covering user behaviors, business rules, and edge cases before writing test code. Use when asked to write scenarios for a feature, plan test coverage, create a test strategy, define what to test, or answer "what scenarios should I test for X".
```

### Impact if implemented
- **Agent behaviour:** When a user says "write scenarios for the checkout flow" or "what should I test for the login page", the agent's skill-matching layer now has explicit phrase overlap with the user's input, increasing the probability this skill is selected over a generic QA or test-generation skill.
- **Discoverability:** Direct improvement — the description is the primary field used in semantic skill matching. Adding phrases like "plan test coverage", "create a test strategy", and "define what to test" broadens the surface area for intent matching.
- **Portability:** No effect on portability.
- **Risk reduced:** Reduces false negatives (user intends this skill but a different skill is selected) and false positives (a test-code-generation skill fires when the user only wanted scenario planning).

### Existing use (before fix)
Today, a user who types "what scenarios should I test for the password reset feature?" may not trigger this skill at all. The current description does not contain the phrase "what scenarios should I test", so a semantic matcher may score it below a generic QA skill or a test-case-generator. The user gets the wrong skill, receives test code instead of a scenario plan, and has to manually course-correct.

### Improved use (after fix)
After the fix, the description explicitly contains "what scenarios should I test for X", "plan test coverage", and "define what to test" — all natural phrases users employ. The skill scores higher in intent matching and fires correctly. The user receives the structured scenario table and report they intended, not generated test code. The "Do NOT activate when" guard in the body continues to prevent accidental activation for test-code requests.

---

## Improvement 5 — Add `compatibility` field documenting the Playwright dependency

### What needs to change
The skill depends on Playwright MCP browser tools in Step 1 for live UI exploration, but there is no `compatibility` field declaring this environment dependency. Teams running this skill in environments without Playwright (e.g. a Claude Code session without the Playwright MCP server configured) will encounter a silent failure at Step 1 with no diagnostic information in the skill itself.

### Before
```yaml
---
name: test-scenario-planning
description: Plan high-level test scenarios that describe user behaviors and business rules before writing test code.
version: 1.0.1
...
---
```
*(no `compatibility` field)*

### After
```yaml
---
name: test-scenario-planning
description: Plan and document high-level QA test scenarios covering user behaviors, business rules, and edge cases before writing test code. Use when asked to write scenarios for a feature, plan test coverage, create a test strategy, define what to test, or answer "what scenarios should I test for X".
license: MIT
compatibility: Requires Playwright MCP browser tools to be available for Step 1 live UI exploration. Tested with claude-sonnet-4-6. Falls back to user-supplied descriptions or wireframes when Playwright is unavailable. Outputs written to specs/ and reports/ directories relative to project root.
metadata:
  ...
---
```

### Impact if implemented
- **Agent behaviour:** The harness or orchestration layer can check the `compatibility` field before activating the skill and warn the user if Playwright MCP is not configured, rather than letting Step 1 fail silently mid-execution.
- **Discoverability:** Registry consumers can filter skills by compatibility requirements, ensuring this skill appears in "Playwright-enabled" environments and is excluded from environments that cannot support it.
- **Portability:** Other teams adopting the skill know upfront what infrastructure they need. They can configure the Playwright MCP server before running the skill rather than discovering the dependency through a runtime failure.
- **Risk reduced:** Prevents the silent failure mode where the skill activates, Step 1 errors on a missing Playwright tool call, and the agent either halts with a confusing error or skips to Step 2 and fabricates observations.

### Existing use (before fix)
A team adds this skill to their skills registry and assigns it to a Claude Code session that does not have the Playwright MCP server configured. When a user triggers "plan test scenarios for the dashboard", the skill activates, reaches Step 1, and attempts a Playwright tool call that does not exist in the session. The error message references a missing tool with no explanation of why it is needed or how to fix it. The user is left debugging the harness rather than planning scenarios.

### Improved use (after fix)
With the `compatibility` field in place, the session harness can validate tool availability before the skill runs. If Playwright is missing, the harness surfaces a clear message: "This skill requires Playwright MCP browser tools. Please configure the Playwright MCP server and retry." The user knows exactly what to do. If the harness does not perform pre-checks, the compatibility field at least documents the dependency for any developer reading the skill file — reducing debugging time from minutes to seconds.

---

## Priority Order

| Priority | Improvement | Effort | Impact |
|---|---|---|---|
| 1 | Move non-standard frontmatter fields under `metadata:` | Low | Critical |
| 2 | Add the missing `license` field | Low | Critical |
| 3 | Strengthen `description` with agent-discoverable trigger keywords | Low | High |
| 4 | Add fallback behavior for inaccessible live URL | Low | High |
| 5 | Add `compatibility` field documenting the Playwright dependency | Low | Medium |

---

## Before vs After: Full Skill Experience

### Before (current state)

A developer discovers `test-scenario-planning` in the registry and attempts to parse its frontmatter. Eight non-standard keys sit at the top level — `version`, `author`, `email`, `category`, `tags`, `product`, `sprint`, `tested_with` — alongside the required `name` and `description`. A strict registry validator rejects the file as non-compliant. A lenient one silently drops those keys, making the tag list (`scenario-planning`, `test-strategy`, `qa`, `requirements`) invisible to search. There is no `license` field, so the organisation's legal review flags the skill as ambiguously licensed and places it on hold.

When a user in a compliant environment finally triggers the skill by typing "write scenarios for the checkout feature", the agent reaches Step 1 and immediately calls Playwright browser tools. If the session lacks the Playwright MCP server, the tool call fails with a cryptic error — there is no fallback instruction, no guidance to ask for alternative inputs, and no `compatibility` field that would have warned the harness in advance. In a luckier session where Playwright is available, the agent explores the live UI correctly. But if the URL requires authentication or is simply unreachable, the agent has no prescribed fallback and may silently invent observations before proceeding to write a scenario document based on fabricated UI behaviour.

On the discoverability front, a user who types "what should I test for the password reset page?" may not trigger this skill at all. The description — "Plan high-level test scenarios that describe user behaviors and business rules before writing test code" — does not contain the phrase "what should I test", "plan test coverage", or "define what to test", so semantic matching may rank a generic QA skill or a test-code-generation skill higher. The wrong skill fires, the user receives generated test code instead of a scenario plan, and they must manually retry with a more specific prompt.

### After (all improvements applied)

With all five improvements applied, the skill is fully spec-compliant and self-documenting. The frontmatter now has exactly six top-level keys (`name`, `description`, `license`, `compatibility`, `metadata`, and `allowed-tools` if added later), with all custom fields correctly nested under `metadata:`. The `license: MIT` field removes all legal ambiguity. Registry validators pass the file cleanly, and tag-based searches for `scenario-planning` or `qa-testing` surface it correctly.

The `description` now contains explicit trigger phrases — "write scenarios for a feature", "plan test coverage", "define what to test", "what scenarios should I test for X" — that directly mirror how users phrase these requests. Semantic matching reliably scores this skill above adjacent skills for QA planning intents. The `compatibility` field documents the Playwright MCP dependency upfront, allowing harnesses to validate the environment before the skill runs and surfacing a clear, actionable error if the tool is missing — rather than a silent mid-step failure.

Inside the skill body, the fallback instruction after the Prerequisites section ensures that when a live URL is inaccessible, the agent immediately asks the user for alternative inputs (wireframes, requirements doc, written description) rather than fabricating observations. The scenario documents and reports that result are always grounded in real information. The overall experience is one of a skill that fails loudly and helpfully when its prerequisites are unmet, matches user intent reliably, and integrates cleanly into any compliant registry pipeline.
