# IMPROVEMENTS — ui-consistency

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

## Improvement 1 — Nest All Custom Fields Under `metadata:`

### What needs to change

Eight custom frontmatter fields (`version`, `author`, `email`, `category`, `tags`, `product`, `sprint`, `tested_with`) are declared at the top level of the frontmatter. The agentskills spec only recognises six top-level fields: `name`, `description`, `license`, `compatibility`, `metadata`, and `allowed-tools`. All custom fields must be nested under a `metadata:` key.

### Before
```yaml
name: ui-consistency
description: Use when asked for any frontend UI change — modals, forms, buttons, tables, layouts, colors, or spacing. Runs pattern inspection before writing code; never skip for small changes.
version: 1.0.0
author: Ruthu Bahubali Jain
email: ruthu.jain@zysk.tech
category: "engineering-practice"
tags:
  - frontend
  - ui
  - css
  - components
  - consistency
product: zysk
sprint: 1
tested_with: claude-sonnet-4-6
```

### After
```yaml
name: ui-consistency
description: Use when asked for any frontend UI change — modals, forms, buttons, tables, layouts, colors, or spacing. Runs pattern inspection before writing code; never skip for small changes.
license: MIT
compatibility: "Requires access to a frontend source directory (resources/js/, src/, assets/, or equivalent). Depends on Glob tool and an Explore sub-agent. Tested with claude-sonnet-4-6. Compatible with Vue, React (JSX/TSX), Svelte, and Blade projects using Tailwind or Bootstrap."
metadata:
  version: 1.0.0
  author: Ruthu Bahubali Jain
  email: ruthu.jain@zysk.tech
  category: engineering-practice
  tags:
    - frontend
    - ui
    - css
    - components
    - consistency
  product: zysk
  sprint: 1
  tested_with: claude-sonnet-4-6
```

### Impact if implemented
- **Agent behaviour:** Spec-compliant parsers will correctly load the skill without ignoring or erroring on unrecognised top-level fields. Fields like `version` and `tags` become reliably queryable through the `metadata` namespace.
- **Discoverability:** Registries and tooling that index skills by spec-standard fields will now index this skill correctly — tag-based search for `frontend`, `ui`, or `css` will surface this skill.
- **Portability:** Any team importing this skill into a different registry will not encounter parse warnings or dropped fields due to non-standard structure.
- **Risk reduced:** Prevents silent field-drop where tools discard unrecognised top-level keys, causing metadata like author contact and version tracking to be lost without any error.

### Existing use (before fix)
Today, when a spec-compliant parser reads this skill's frontmatter, it encounters `version`, `author`, `email`, `category`, `tags`, `product`, `sprint`, and `tested_with` at the top level. A strict parser will raise a validation warning or silently discard these fields, meaning version history, author contact, and category tags are invisible to any tooling that relies on the spec. If the Zysk registry is later upgraded to enforce spec compliance, this skill will fail validation entirely and be excluded from the index until manually corrected.

### Improved use (after fix)
After nesting under `metadata:`, the skill passes frontmatter validation cleanly. Registry tooling can query `metadata.tags` to find all `frontend`-tagged skills, `metadata.author` to contact the maintainer, and `metadata.version` to track upgrades. The skill is portable to any agentskills-compliant registry without modification.

---

## Improvement 2 — Add Required `license` Field

### What needs to change

The `license` field is a required top-level frontmatter field per the agentskills spec. It is entirely absent from the current skill. Without it, the skill fails spec validation and cannot be published to a compliant registry.

### Before
```yaml
name: ui-consistency
description: Use when asked for any frontend UI change — modals, forms, buttons, tables, layouts, colors, or spacing. Runs pattern inspection before writing code; never skip for small changes.
version: 1.0.0
author: Ruthu Bahubali Jain
# (no license field present)
```

### After
```yaml
name: ui-consistency
description: Use when asked for any frontend UI change — modals, forms, buttons, tables, layouts, colors, or spacing. Runs pattern inspection before writing code; never skip for small changes.
license: MIT
```

### Impact if implemented
- **Agent behaviour:** No direct change to runtime agent behaviour, but registries that gate on spec compliance will now accept the skill for indexing and distribution.
- **Discoverability:** License-filtered queries (e.g., "show me only MIT-licensed skills") will now surface this skill. Skills without a `license` field are often excluded from public indexes entirely.
- **Portability:** Other teams can immediately assess whether they are legally permitted to use and adapt this skill without contacting the author — critical for open-source or cross-org sharing.
- **Risk reduced:** Prevents ambiguous intellectual property status where a consuming team cannot determine if the skill is freely usable, proprietary, or unlicensed.

### Existing use (before fix)
Currently, any developer or agent registry that checks for the `license` field will flag this skill as incomplete. A team outside Zysk who encounters this skill in a shared registry cannot determine if they are permitted to use it, fork it, or redistribute it. Automated compliance checks that are run as part of CI (e.g., a `validate-skills` script) will report this skill as failing and block it from being merged or published.

### Improved use (after fix)
With `license: MIT` present, the skill passes the required-fields check in CI, can be published to public registries, and is immediately usable by any team without legal ambiguity. The `license` field also signals intent: MIT communicates that this is a community-sharable, freely adaptable skill rather than an internal proprietary one.

---

## Improvement 3 — Add Required `compatibility` Field

### What needs to change

The `compatibility` field is required by the spec to document the skill's runtime prerequisites. This skill has real, non-trivial environment dependencies: it dispatches an `Explore` sub-agent (Step 2), uses the `Glob` tool (Step 1), and requires access to a frontend source directory. Without a `compatibility` field, agents and users cannot evaluate fitness before activation, and the skill will silently fail in environments where sub-agents or the frontend directory are unavailable.

### Before
```yaml
name: ui-consistency
description: Use when asked for any frontend UI change — modals, forms, buttons, tables, layouts, colors, or spacing. Runs pattern inspection before writing code; never skip for small changes.
# (no compatibility field present)
```

### After
```yaml
name: ui-consistency
description: Use when asked for any frontend UI change — modals, forms, buttons, tables, layouts, colors, or spacing. Runs pattern inspection before writing code; never skip for small changes.
license: MIT
compatibility: "Requires access to a frontend source directory (resources/js/, src/, assets/, or equivalent). Depends on Glob tool and an Explore sub-agent for Step 2 pattern scan. Tested with claude-sonnet-4-6. Compatible with Vue, React (JSX/TSX), Svelte, and Blade projects using Tailwind or Bootstrap. Not suitable for back-end-only projects with no frontend source directory."
```

### Impact if implemented
- **Agent behaviour:** Before invoking the skill, an orchestrating agent can read `compatibility` and check whether the current environment satisfies the prerequisites (sub-agent support, frontend directory presence). If not, the agent can surface a clear error rather than proceeding to Step 2 and failing mid-execution when the `Explore` agent call is not supported.
- **Discoverability:** Registry filters like "show me skills compatible with Vue" or "show me skills that work without sub-agents" will produce correct results only if `compatibility` is populated.
- **Portability:** A team using a non-Vue, non-React stack (e.g., plain HTML + vanilla JS) can immediately see that this skill is compatible with their project type. A back-end team can see it is not suitable for them without activating the skill and experiencing a confusing failure.
- **Risk reduced:** Prevents silent mid-execution failures in Step 2 where the `Explore` agent is dispatched but sub-agent support is unavailable in the environment, causing the entire skill to stall with no useful error message.

### Existing use (before fix)
Today, when the skill is activated on a back-end-only project or in an environment without sub-agent support, it proceeds through Steps 1 and 2 until the `Explore` agent dispatch in Step 2 fails or returns no results. The agent then either halts silently or tries to continue with an empty Pattern Inventory, which causes Step 3 to produce inconsistent or incorrect code. There is no pre-flight check, and the user receives no early warning that the skill is not appropriate for their context.

### Improved use (after fix)
With `compatibility` defined, an orchestrating agent performing pre-flight validation will read the field before Step 1 and immediately surface: "This skill requires a frontend source directory and sub-agent support — your current project appears to be back-end only." The user gets a fast, informative failure at the right moment rather than a confusing mid-execution stall. Teams evaluating the skill in a registry can filter by framework compatibility (`Vue`, `React`, `Svelte`, `Blade`) before even downloading it.

---

## Improvement 4 — Remove Redundancy in `## Notes` Section

### What needs to change

The `## Notes` section at the bottom of the skill body contains two points that duplicate guidance already present in Step 4 and the Pattern Inventory definition:

1. "Inline styles are legacy" — Step 4, Rule 1 already states: "Use utility classes from the Pattern Inventory. Only use `style=""` when no utility class equivalent exists."
2. "Pattern Inventory is the source of truth" — Step 2 already labels the output block as "This inventory is the source of truth for all remaining steps."

This duplication increases the skill's length without adding new information, and creates a maintenance risk: if the guidance in Step 4 changes, the `## Notes` section may go out of sync and contradict it.

### Before
```markdown
## Notes

- **Inline styles are legacy**: If you encounter ad-hoc inline styles in existing components, treat them as technical debt — do not replicate the inline style, use the framework utility equivalent. Only replicate if there is genuinely no utility class for it.
- **Pattern Inventory is the source of truth**: If the inventory contradicts something you think you know about the project's stack, trust the inventory. It was derived from what is actually in the codebase.
```

### After
Remove the `## Notes` section entirely, and strengthen the inline guidance in Step 4 Rule 1 to absorb the intent of the first note:

```markdown
1. **Framework classes over inline styles.** Use utility classes from the Pattern Inventory. Only use `style=""` when no utility class equivalent exists — existing inline styles in the codebase are technical debt; do not replicate them, find the utility class equivalent. If you must use an inline style, always add the comment: `<!-- intentional inline: no framework equivalent -->`.
```

The second note ("Pattern Inventory is the source of truth") is already stated explicitly at the end of Step 2 and does not need restating.

### Impact if implemented
- **Agent behaviour:** The agent now reads the inline-style guidance at the point of action (Step 4) rather than having to reconcile potentially diverging guidance from two locations. This reduces the chance of the agent following the `## Notes` guidance while ignoring or overriding Step 4.
- **Discoverability:** No change to discoverability.
- **Portability:** Trimming ~8 lines reduces the body from ~165 lines towards a leaner, lower-maintenance document. Future maintainers have a single location to update inline-style policy.
- **Risk reduced:** Prevents the `## Notes` section from drifting out of sync with Step 4 after future edits, eliminating a potential source of contradictory agent instructions.

### Existing use (before fix)
Today, the agent reads Step 4 Rule 1 ("Only use `style=""` when no utility class equivalent exists") and then, at the end of the skill, encounters the `## Notes` section repeating the same guidance. In most cases this is harmless, but if the notes and the step-level guidance ever diverge after a future edit, the agent will encounter a contradiction and may apply the notes guidance (as a "final override") instead of the more precise step-level rule. This is a latent maintenance risk.

### Improved use (after fix)
After consolidating the notes into Step 4, there is a single authoritative statement of the inline-style policy. The agent reads it at the point of decision (before writing code) and there is no redundant re-statement to drift out of sync. The skill body is slightly shorter and easier to maintain.

---

## Improvement 5 — Add `allowed-tools` Field to Declare Tool Dependencies

### What needs to change

Step 1 uses `Glob` explicitly, Step 2 dispatches an `Explore` agent, and Step 3 uses `Read`. These are named tool dependencies. The agentskills spec supports an optional `allowed-tools` field to declare which tools a skill requires. Declaring this field helps orchestrators pre-check tool availability and helps users understand what permissions to grant before activating the skill.

### Before
```yaml
# (no allowed-tools field present)
```

### After
```yaml
allowed-tools:
  - Glob
  - Read
  - Explore
```

### Impact if implemented
- **Agent behaviour:** Orchestrating agents that enforce tool allowlists can validate upfront that `Glob`, `Read`, and `Explore` are available before the skill starts executing, producing a clear pre-flight error rather than a mid-execution tool-not-found failure.
- **Discoverability:** Registry queries like "show me skills that only need Read and Glob" will now return accurate results for this skill. Skills without `allowed-tools` are often assumed to require no tools, which is incorrect here.
- **Portability:** A team with a restricted tool environment (e.g., `Explore` sub-agents not permitted) can immediately see from `allowed-tools` that the skill will not work in their environment without any trial-and-error.
- **Risk reduced:** Prevents the skill from being activated in environments where the `Explore` agent is unavailable, which currently causes a silent failure at Step 2 with no guidance to the user.

### Existing use (before fix)
Today, there is no declared tool manifest. An agent with a restricted toolset activates this skill, proceeds through Step 1 (`Glob` — succeeds), then hits Step 2 where it tries to dispatch an `Explore` agent. If `Explore` is not in the allowed-tools list for that environment, the call fails silently or raises a permissions error mid-execution. The user sees an incomplete Pattern Inventory and receives code that was written without the mandatory Step 2 scan.

### Improved use (after fix)
With `allowed-tools: [Glob, Read, Explore]` declared, an orchestrator performs a pre-flight check before Step 1. If `Explore` is not available, the user is informed immediately: "This skill requires the Explore tool, which is not available in your current environment." The user can then either enable sub-agent support or choose a different approach — rather than discovering the limitation after the skill has already started writing code.

---

## Priority Order

| Priority | Improvement | Effort | Impact |
|---|---|---|---|
| 1 | Add Required `license` Field | Low | Critical |
| 2 | Nest All Custom Fields Under `metadata:` | Low | Critical |
| 3 | Add Required `compatibility` Field | Low | High |
| 4 | Add `allowed-tools` Field to Declare Tool Dependencies | Low | High |
| 5 | Remove Redundancy in `## Notes` Section | Low | Medium |

---

## Before vs After: Full Skill Experience

### Before (current state)

A developer on another team discovers `ui-consistency` in a shared registry and wants to use it on their React + Tailwind project. Before they can evaluate fitness, they notice that the `license` field is absent — they cannot tell if this is an MIT-licensed community skill or a proprietary Zysk internal tool. They proceed anyway and activate the skill. The frontmatter parses with warnings: `version`, `author`, `email`, `category`, `tags`, `product`, `sprint`, and `tested_with` are all at the top level, and the registry's strict parser drops them silently — the skill appears in the index with no tags, no author contact, and no version information. The developer has no way to contact the maintainer if the skill breaks.

When the skill activates on a back-end-heavy project where the frontend directory is nested unusually and sub-agent support is disabled, the skill proceeds through Step 1 (Glob — succeeds), then stalls at Step 2 when it attempts to dispatch the `Explore` agent. There is no pre-flight check and no `compatibility` field to consult — the agent simply hits a tool-not-available error mid-execution, leaving the Pattern Inventory empty. The skill then continues to Step 3 with no inventory, produces code that ignores the existing codebase patterns entirely, and the developer receives a component that looks nothing like the rest of the UI. The failure is silent and the root cause is non-obvious.

Additionally, the `## Notes` section at the bottom of the skill body repeats guidance from Step 4 and Step 2. Six months after the initial release, a maintainer updates the inline-style rule in Step 4 but forgets to update `## Notes`. An agent reading the skill now encounters contradictory guidance: Step 4 says "only inline-style if no utility exists", while `## Notes` says "treat all inline styles as legacy debt — never replicate." The agent applies the notes rule (as the last instruction read) and strips a legitimate inline style that had no utility equivalent, introducing a visual regression.

### After (all improvements applied)

With all five improvements applied, the skill is fully spec-compliant and safe to distribute. The `license: MIT` field is present, so any team can immediately confirm they are permitted to use, adapt, and redistribute the skill. The `compatibility` field documents that the skill requires a frontend source directory, the `Glob` tool, and an `Explore` sub-agent, and lists the tested frameworks (Vue, React/JSX/TSX, Svelte, Blade). Before the skill activates, an orchestrating agent reads `compatibility` and performs a pre-flight check — if sub-agent support is unavailable or no frontend directory is found, the user receives an informative early failure rather than a mid-execution stall. Teams with incompatible environments know to skip this skill without trial-and-error.

The `allowed-tools: [Glob, Read, Explore]` declaration gives orchestrators a precise tool manifest. Restricted environments that do not permit the `Explore` tool will flag this skill as incompatible at selection time, not mid-execution. Registry queries for skills requiring only `Glob` and `Read` will correctly exclude this skill, while queries for skills that support `Explore`-based scanning will correctly surface it. All eight custom metadata fields (`version`, `author`, `email`, `category`, `tags`, `product`, `sprint`, `tested_with`) are now nested under `metadata:`, so registries index the skill with its full tag set (`frontend`, `ui`, `css`, `components`, `consistency`), the author is reachable, and version tracking works correctly.

The body is also tighter and more maintainable. The redundant `## Notes` section has been removed and its substantive guidance — the nuance about treating existing inline styles as technical debt rather than patterns to replicate — has been folded into Step 4 Rule 1 where the agent actually needs it. There is now a single, authoritative statement of the inline-style policy at the point of decision, with no risk of future drift between a step and a notes section. A developer reading the skill for the first time encounters a clean, linear 5-step flow with no conflicting guidance, and a developer maintaining the skill has one place to update the inline-style rule rather than two.
