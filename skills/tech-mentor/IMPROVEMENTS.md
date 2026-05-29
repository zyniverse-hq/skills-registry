# IMPROVEMENTS — tech-mentor

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

## Improvement 1 — Nest custom frontmatter fields under `metadata:`

### What needs to change
Nine custom fields (`version`, `author`, `email`, `category`, `tags`, `product`, `sprint`, `tested_with`) are declared at the top level of the frontmatter. The spec requires all non-standard fields to be nested under a single `metadata:` block. As-is, any spec-compliant parser that rejects unknown top-level keys will fail to load the skill or silently discard these fields.

### Before
```yaml
---
name: tech-mentor
description: Researches industry patterns for engineering decisions. Use when evaluating architecture choices, comparing approaches, or understanding what companies do before building something.
version: 1.0.0
author: Vishnu BV
email: vishnu@testmyskills.ai
category: engineering-practice
tags:
  - architecture
  - research
  - decision-support
  - industry-patterns
product: zyniverse
sprint: 1
tested_with: claude-sonnet-4-6
---
```

### After
```yaml
---
name: tech-mentor
description: Researches industry patterns for engineering decisions. Use when evaluating architecture choices, comparing approaches, or understanding what companies do before building something.
license: MIT
compatibility: Requires web search capability. Compatible with any LLM that supports tool use and markdown output. No specific language runtime required.
metadata:
  version: 1.0.0
  author: Vishnu BV
  email: vishnu@testmyskills.ai
  category: engineering-practice
  tags:
    - architecture
    - research
    - decision-support
    - industry-patterns
  product: zyniverse
  sprint: 1
  tested_with: claude-sonnet-4-6
---
```

### Impact if implemented
- **Agent behaviour:** Skill loads cleanly in spec-compliant registries; parsers no longer reject or silently drop the custom metadata fields.
- **Discoverability:** Registry indexers can correctly separate standard fields from custom metadata, improving search and filter accuracy.
- **Portability:** Other teams importing the skill via registry tooling get a predictable structure they can introspect programmatically.
- **Risk reduced:** Prevents silent load failures in strict parsers that reject unknown top-level YAML keys.

### Existing use (before fix)
Today, when a spec-compliant registry tool loads tech-mentor, it encounters nine unrecognised top-level YAML keys. Depending on the parser's strictness setting, it either raises a validation error (skill does not load at all) or silently ignores the fields (metadata like `author`, `category`, and `tested_with` is lost). Either way, the skill behaves differently than intended. A developer browsing the registry for skills by `category: engineering-practice` will not find this skill if the field was dropped.

### Improved use (after fix)
After nesting under `metadata:`, any spec-compliant parser processes the frontmatter without error. The `category`, `tags`, and `tested_with` values are preserved and indexable. A developer searching the registry for engineering-practice skills or filtering by `tested_with: claude-sonnet-4-6` will correctly surface tech-mentor. The skill loads reliably in all environments.

---

## Improvement 2 — Add missing `license` field

### What needs to change
The `license` field is absent from the frontmatter. Without it, any developer or team who wants to adapt, extend, or redistribute the skill has no legal clarity. Registry consumers cannot determine whether the skill is freely usable, proprietary, or somewhere in between.

### Before
```yaml
---
name: tech-mentor
description: Researches industry patterns for engineering decisions. Use when evaluating architecture choices, comparing approaches, or understanding what companies do before building something.
version: 1.0.0
author: Vishnu BV
# license field is absent
---
```

### After
```yaml
---
name: tech-mentor
description: Researches industry patterns for engineering decisions. Use when evaluating architecture choices, comparing approaches, or understanding what companies do before building something.
license: MIT
metadata:
  version: 1.0.0
  author: Vishnu BV
  ...
---
```

### Impact if implemented
- **Agent behaviour:** No direct change to runtime agent behaviour, but registry tooling that enforces license presence will no longer flag or reject the skill.
- **Discoverability:** Registry filters for "open" or "MIT" skills will include tech-mentor in results.
- **Portability:** Teams at other organisations can immediately determine whether they can adopt the skill without legal review.
- **Risk reduced:** Prevents ambiguity that leads teams to skip using the skill entirely out of caution.

### Existing use (before fix)
Today, a developer at a company with an open-source policy encounters tech-mentor in the registry. They cannot tell whether it is MIT, Apache 2.0, or proprietary. Their legal team requires a declared license before approval. The skill gets skipped in favour of a lower-quality alternative that has a declared license. The author's intent (likely open use) is never communicated.

### Improved use (after fix)
With `license: MIT` present, the skill passes automated license checks in corporate registry tooling. Developers and teams can adopt it immediately without manual review. The registry can surface it in filtered views for "MIT-licensed skills", increasing reach and adoption.

---

## Improvement 3 — Add missing `compatibility` field documenting the web search dependency

### What needs to change
Step 3 of the skill mandates "3-5 targeted web searches minimum" — this is a hard runtime dependency on web search capability. The `compatibility` field is absent, so agents running in search-restricted environments (air-gapped, sandboxed, or tool-restricted deployments) have no upfront warning. They activate the skill, reach Step 3, and fail silently or produce a degraded output with no sourced evidence.

### Before
```yaml
---
name: tech-mentor
description: Researches industry patterns for engineering decisions. Use when evaluating architecture choices, comparing approaches, or understanding what companies do before building something.
# compatibility field is absent
---
```

### After
```yaml
---
name: tech-mentor
description: Researches industry patterns for engineering decisions. Use when evaluating architecture choices, comparing approaches, or understanding what companies do before building something.
license: MIT
compatibility: Requires web search capability. Compatible with any LLM that supports tool use and markdown output. No specific language runtime required.
---
```

### Impact if implemented
- **Agent behaviour:** Agents in restricted environments see the compatibility declaration before activation and can surface a clear error or skip activation rather than failing mid-execution at Step 3.
- **Discoverability:** Operators who provision skill libraries for specific deployment environments can filter out skills whose compatibility requirements exceed what their environment supports.
- **Portability:** The skill now documents its own prerequisites, making it genuinely self-contained — a consumer knows what is needed before they try to run it.
- **Risk reduced:** Prevents silent degradation where the skill produces a report with zero sourced evidence because searches were blocked, giving the developer false confidence in unsourced output.

### Existing use (before fix)
A developer deploys tech-mentor in a corporate environment where outbound web requests from the agent are blocked by a proxy. They ask: "How do companies handle distributed tracing at the 10-engineer scale?" The skill activates, reaches Step 3, attempts web searches, and either errors out or skips the search step silently. The output is produced from the model's training data alone — no cited sources, no year stamps, no company examples with URLs. The developer reads it as a researched report. It is not. There is no warning that anything went wrong.

### Improved use (after fix)
With `compatibility` declared, the agent runtime checks prerequisites before activating the skill. In a search-restricted environment, it surfaces: "tech-mentor requires web search capability, which is not available in this environment." The developer is informed immediately and can either enable search, switch environments, or choose a different approach. No silent degradation, no false confidence in unreferenced output.

---

## Improvement 4 — Collapse redundant Notes section into the relevant Steps

### What needs to change
The **Notes** section at the end of the skill body contains four bullets that restate principles already embedded earlier in the Steps:

- "This skill produces industry landscape research, not implementation advice" — already stated in the "Do NOT activate when" guard and the voice rules in Step 5.
- "Output is deliberately non-prescriptive" — covered by the voice rules in Step 5 ("teams converge on X" not "you should use X").
- "Stage-first research ordering is intentional" — already explained in Step 3 with the explicit rationale.
- "Every company example requires a source and year" — already a voice rule in Step 5.

Duplication increases token count without adding information, and risks the Steps and Notes diverging over time if one is updated without the other.

### Before
```markdown
## Notes

- This skill produces industry landscape research, not implementation advice — it describes what companies do; the developer decides what to build
- Output is deliberately non-prescriptive: "teams converge on X" not "you should use X"
- Stage-first research ordering is intentional: startup patterns surface before enterprise patterns to prevent anchoring on solutions that do not fit the team scale
- Every company example requires a source and year — unsourced claims are not included in the output
```

### After
Remove the Notes section entirely. The four points are already covered:
- "Do NOT activate when: the user wants implementation help or code" (When to use section)
- Voice rules in Step 5: "no code snippets", "1500-3000 words of prose", source-and-year requirement
- Step 3 rationale: "This fights anchoring bias — the Netflix answer is not the right answer for most developers asking this question"

If a brief reminder is desired, collapse into a single sentence at the end of Step 5:

```markdown
> Voice reminder: no code, no prescriptive advice, source and year on every company example, startup examples before enterprise.
```

### Impact if implemented
- **Agent behaviour:** No functional change — the instructions remain in Steps 3 and 5 where the agent reads them in execution order. Removing the restatement reduces noise.
- **Discoverability:** Slightly reduces token count (~80 tokens), keeping the skill well under the 4000-token warning threshold.
- **Portability:** Reduces maintenance surface — one place to update sourcing and voice rules instead of two.
- **Risk reduced:** Prevents future divergence where Steps and Notes contradict each other after a partial edit.

### Existing use (before fix)
Today the skill works correctly, but a developer reading it to understand its design sees the same rule stated twice — once in the steps (authoritative, in-context) and once in the Notes (restatement, out of context). An agent executing the skill reads the voice rules in Step 5 and then re-encounters them in Notes, which adds no new constraint but increases the chance of conflicting interpretations if the two ever diverge. A future editor updating the voice rules in Step 5 may not notice the parallel statement in Notes and leave it inconsistent.

### Improved use (after fix)
After removing the Notes section, each rule appears exactly once, in the step where it is actionable. The skill is shorter, easier to scan, and has a single source of truth for each constraint. Future edits to sourcing rules or voice guidelines only require one change, not two.

---

## Improvement 5 — Make the ADR output path in Step 6 explicit and configurable

### What needs to change
Step 6 instructs the agent to write the ADR to `docs/adr/` but adds "(or ask where they prefer)" as a parenthetical. The assumed default path `docs/adr/` is a convention — not universal. Projects using `architecture/decisions/`, `adr/`, or no docs folder at all will have the agent write to a path that does not exist or does not match their project layout. The current phrasing buries the ask ("or ask where they prefer") after an assumed default, which means the agent may write to the wrong location before asking.

### Before
```markdown
### Step 6: Offer an ADR (optional follow-up)

After delivering the output, offer:

"Want me to write a quick ADR for this decision? It captures what you chose, what you considered, and why — so you do not have to relitigate it in three months."

If yes, write to docs/adr/ (or ask where they prefer) using the standard ADR template: Context, Decision, Options considered, Consequences.
```

### After
```markdown
### Step 6: Offer an ADR (optional follow-up)

After delivering the output, offer:

"Want me to write a quick ADR for this decision? It captures what you chose, what you considered, and why — so you do not have to relitigate it in three months."

If yes, **ask where to save it before writing** — common locations include `docs/adr/`, `architecture/decisions/`, and `adr/`. If the project is in scope, check for an existing ADR directory first. Write using the standard ADR template: Context, Decision, Options considered, Consequences.
```

### Impact if implemented
- **Agent behaviour:** The agent asks for the target path before writing, rather than assuming `docs/adr/` and potentially creating a directory in the wrong place.
- **Discoverability:** No change to discoverability.
- **Portability:** The skill now works correctly across all project layouts without requiring the developer to clean up a misplaced file.
- **Risk reduced:** Prevents the agent from creating `docs/adr/` in projects that use a different convention or have no docs folder at all.

### Existing use (before fix)
A developer working on a monorepo where ADRs live under `services/core/architecture/decisions/` accepts the ADR offer. The agent writes to `docs/adr/` — a directory that does not exist in this project — creating it in the process. The developer now has an ADR in the wrong location, an unwanted `docs/` directory, and has to manually move the file. The friction of cleaning up makes the ADR feature feel unreliable.

### Improved use (after fix)
The agent asks: "Where would you like me to save it? Common locations are `docs/adr/`, `architecture/decisions/`, or `adr/`." The developer specifies the correct path. The ADR lands exactly where it belongs, with no cleanup required. The feature becomes reliably useful across diverse project structures.

---

## Priority Order

| Priority | Improvement | Effort | Impact |
|---|---|---|---|
| 1 | Nest custom fields under `metadata:` | Low | Critical |
| 2 | Add missing `compatibility` field (web search dependency) | Low | Critical |
| 3 | Add missing `license` field | Low | High |
| 4 | Make ADR output path explicit and configurable | Low | Medium |
| 5 | Collapse redundant Notes section | Low | Low |

---

## Before vs After: Full Skill Experience

### Before (current state)

A developer discovers tech-mentor in the skills registry and wants to add it to their corporate AI deployment. The first problem surfaces immediately: their registry tooling validates frontmatter against the spec and rejects the skill with a parse error because `version`, `author`, `email`, `category`, `tags`, `product`, `sprint`, and `tested_with` are all declared at the top level instead of under `metadata:`. If the tooling is lenient and loads the skill anyway, these nine fields are silently dropped — the developer cannot filter the registry by `category: engineering-practice` or `tested_with: claude-sonnet-4-6` to find related skills. There is also no `license` field, so the company's open-source review process flags it as legally ambiguous and it gets parked in a review queue indefinitely.

When the skill is eventually activated in a restricted deployment environment, a developer asks about distributed tracing patterns. The skill reaches Step 3 and attempts web searches — but outbound requests are blocked. Because there is no `compatibility` declaration, nothing warned the operator or the developer that web search was required. The skill silently falls back to training-data recall, producing a report that looks sourced but contains no cited URLs or verified years. The developer acts on what they believe is a researched report. It is not. This is the most dangerous failure mode: confident output without the research that was supposed to back it.

In a working environment with search enabled, the skill functions well end-to-end — the step structure is solid, the failure-modes section is non-optional, and the stage-first research ordering consistently surfaces startup-scale answers before enterprise ones. But after delivering the report, when the developer accepts the ADR offer, the agent writes to `docs/adr/` without asking — creating a new directory in a project where ADRs live under `architecture/decisions/`. The developer cleans it up and loses confidence in the ADR feature for future sessions.

### After (all improvements applied)

With all five improvements applied, tech-mentor loads cleanly in every spec-compliant registry. The `metadata:` block correctly wraps all nine custom fields, so parsers process the frontmatter without error and the skill is fully indexable by `category`, `tags`, and `tested_with`. The `license: MIT` field resolves legal ambiguity instantly — corporate review queues clear, adoption decisions become self-service. Developers browsing for MIT-licensed architecture research skills find tech-mentor in filtered results.

Before a developer in a restricted environment even activates the skill, the `compatibility` declaration surfaces: "tech-mentor requires web search capability." Operators configuring tool libraries for air-gapped environments exclude the skill upfront rather than discovering the gap at runtime. In environments where search is available, the skill activates, executes its 3-5 targeted searches, and produces a fully sourced report with company examples, year stamps, and cited URLs — exactly as designed. There is no silent fallback to unsourced training-data output.

The body of the skill is tighter after collapsing the Notes section: each rule appears once, in the step where it is actionable. When the ADR offer is accepted, the agent asks where to save the file before writing — the ADR lands in the right directory on the first attempt, making the optional follow-up feature reliable across diverse project layouts. End-to-end, tech-mentor is now a self-describing, portable, spec-compliant skill that fails loudly when its prerequisites are missing and works correctly when they are met.
