# IMPROVEMENTS — edd

> Improvement plan derived from SKILL.md + ANALYSIS.md audit against the agentskills.openml.io spec.

---

## Quick Summary

| | Before | After |
|---|---|---|
| Spec compliance | Partially compliant | Fully compliant |
| Critical violations | 2 | 0 |
| Agent discoverability | High | High |
| Portability | Fails | Pass |

---

## Improvement 1 — Move Custom Frontmatter Fields Under `metadata:`

### What needs to change

Eight non-standard fields (`version`, `author`, `email`, `category`, `tags`, `product`, `sprint`, `tested_with`) sit at the top level of the frontmatter. The spec defines exactly six allowed top-level keys: `name`, `description`, `license`, `compatibility`, `metadata`, and `allowed-tools`. All custom fields must be nested under `metadata:` as string key-value pairs. The `tags` list and the integer `sprint: 1` must also be converted to strings.

### Before
```yaml
version: 1.0.0
author: Sharath S Rao
email: sharath.rao@zysk.tech
category: engineering-practice
tags:
  - eval
  - tdd
  - llm-evaluation
  - development-practice
product: tms
sprint: 1
tested_with: claude-sonnet-4-6
```

### After
```yaml
metadata:
  version: "1.0.0"
  author: Sharath S Rao
  email: sharath.rao@zysk.tech
  category: engineering-practice
  tags: "eval, tdd, llm-evaluation, development-practice"
  product: tms
  sprint: "1"
  tested_with: claude-sonnet-4-6
```

### Impact if implemented
- **Agent behaviour:** YAML parsers used by agent clients will no longer silently drop or reject the skill due to unrecognised top-level keys; the skill loads reliably in all registry consumers.
- **Discoverability:** No change to discoverability — the fix is structural, not semantic.
- **Portability:** Any team importing this skill from the registry gets a valid, parseable frontmatter block; the custom metadata is preserved and accessible under `metadata.*`.
- **Risk reduced:** Prevents silent skill-load failures in strict-spec agent runtimes that reject non-standard top-level frontmatter keys.

### Existing use (before fix)
Today, an agent client that validates frontmatter against the spec schema will encounter eight unexpected top-level keys. Strict parsers raise a validation error and refuse to load the skill entirely — the agent never activates EDD even when the user says "starting work on a new node". Lenient parsers silently discard the unrecognised fields, meaning `version`, `author`, and `tested_with` are lost from any registry index that reads metadata. The `tags` field is a YAML list and `sprint` is an integer, both of which violate the spec's requirement that `metadata` values be strings — causing type-mismatch errors in any registry tooling that enforces value types.

### Improved use (after fix)
After the fix, the frontmatter is fully spec-compliant. Every registry consumer can parse and load the skill without errors. The `tags` string (`"eval, tdd, llm-evaluation, development-practice"`) remains searchable in registry indices that tokenise the metadata values. The `tested_with: claude-sonnet-4-6` field is preserved and accessible, giving operators confidence the skill was validated against a known model. The skill activates reliably in all compliant agent runtimes.

---

## Improvement 2 — Add Missing `license` Field

### What needs to change

The `license` field is a required frontmatter key under the spec. It is entirely absent from the current skill. Any team picking this skill up from the registry has no signal about usage rights — they cannot safely import it into a commercial product or a client-facing deployment.

### Before
```yaml
---
name: edd
description: "INVOKE THIS SKILL whenever the user is about to start a new feature..."
version: 1.0.0
author: Sharath S Rao
# (no license field)
```

### After
```yaml
---
name: edd
description: "INVOKE THIS SKILL whenever the user is about to start a new feature..."
license: "Proprietary — internal use only (zysk.tech)"
metadata:
  version: "1.0.0"
  author: Sharath S Rao
  ...
```

### Impact if implemented
- **Agent behaviour:** No runtime change — `license` is metadata, not behavioural. However, registry tooling that enforces required fields will stop flagging this skill as non-compliant, allowing it to pass automated publishing gates.
- **Discoverability:** Registry filters that exclude skills with no declared license (a common safety gate in enterprise deployments) will now include this skill in results.
- **Portability:** Other teams can instantly see the usage terms. `Proprietary — internal use only (zysk.tech)` clearly signals that redistribution requires coordination with the author.
- **Risk reduced:** Prevents inadvertent redistribution or use in contexts that require open-source licensing; removes the compliance ambiguity for registry operators.

### Existing use (before fix)
Today, any developer browsing the registry sees no license information for `edd`. Enterprise registry gates that block skills without a `license` field will refuse to serve this skill to downstream agents — meaning the EDD methodology is invisible in regulated environments. Developers who do find the skill must guess at usage rights before embedding it in client-facing tooling.

### Improved use (after fix)
After adding `license: "Proprietary — internal use only (zysk.tech)"`, the skill passes automated publishing checks and is visible in filtered registry queries. Developers immediately know they need to check with zysk.tech before redistributing. The skill's compliance score moves from "Partially compliant" to "Fully compliant" on the two must-fix violations.

---

## Improvement 3 — Trim Description to Create Headroom Under the 1024-Char Limit

### What needs to change

The current description is approximately 740 characters — 72% of the 1024-character hard limit. The sentence "The skill starts with a triage step to decide whether EDD actually applies (deterministic glue code often doesn't), then guides the user through plan → dataset → evaluators → baseline → implement → iterate." adds ~170 characters of content already covered in detail by Step 1 of the body. Removing it creates ~170 chars of headroom for future trigger phrases or context without risking a hard truncation that silently breaks agent discovery.

### Before
```yaml
description: "INVOKE THIS SKILL whenever the user is about to start a new feature,
  refactor existing code, change a prompt, modify an agent/node, or otherwise alter
  behavior whose quality is hard to assert with a binary unit test. EDD
  (Evaluation-Driven Development) is the eval-first counterpart to TDD: define
  success criteria and evaluators BEFORE writing code, baseline the current
  behavior, then iterate against measurable scores. Triggers on phrases like
  'building X', 'refactoring Y', 'improving the prompt for Z', 'new node', 'new
  feature', 'how should I approach this', 'starting work on…', 'change the LLM
  behavior'. Use even when the user doesn't say 'eval' — their LLM-shaped work
  almost certainly needs this. The skill starts with a triage step to decide
  whether EDD actually applies (deterministic glue code often doesn't), then
  guides the user through plan → dataset → evaluators → baseline → implement →
  iterate."
```

### After
```yaml
description: >
  INVOKE THIS SKILL whenever the user is about to start a new feature, refactor
  existing code, change a prompt, or modify an agent/node — any work whose quality
  is hard to assert with a binary unit test. EDD (Evaluation-Driven Development)
  is the eval-first counterpart to TDD: define success criteria and evaluators
  BEFORE writing code, baseline current behavior, then iterate against measurable
  scores. Triggers on: 'building X', 'refactoring Y', 'improving the prompt for Z',
  'new node', 'new feature', 'how should I approach this', 'starting work on…',
  'change the LLM behavior'. Use even when the user doesn't say 'eval'.
```

### Impact if implemented
- **Agent behaviour:** No change to trigger coverage — all key phrases are retained. The triage logic remains in Step 1 where it belongs.
- **Discoverability:** Identical discoverability — all trigger phrases survive the trim. Freed headroom (~170 chars) allows future phrases like "rewriting the retrieval", "tuning the ranker", or "changing the scoring model" to be added without hitting the limit.
- **Portability:** Smaller description is faster to embed and less likely to be truncated by token-limited registry preview tools.
- **Risk reduced:** Prevents a future edit that adds one trigger phrase from silently truncating the description mid-sentence, which would break the last trigger in the list.

### Existing use (before fix)
At 740 characters the description is safe today, but the skill is actively developed (v1.0.0 implies iteration). Any contributor who adds a new trigger phrase without checking the character count risks pushing the description over 1024 chars. At that point, the spec parser truncates the description or rejects the skill entirely — and the truncated description may cut off the last trigger phrase, silently reducing discovery coverage with no error surfaced to the author.

### Improved use (after fix)
After the trim the description sits at approximately 570 characters — 56% of the limit — giving a comfortable buffer of ~450 chars for future additions. The removed sentence ("The skill starts with a triage step…") is already covered more completely in Step 1 of the body, so zero information is lost for the agent reading the full skill. Contributors can safely add two or three new trigger phrases before needing to worry about the character budget again.

---

## Improvement 4 — Extract Reference Sections to `references/` Directory (Contingency Improvement)

### What needs to change

The three reference sections at the end of the body — "How EDD differs from TDD" (table, ~15 lines), "Anti-patterns to call out" (~20 lines), and "Cooperating skills" (~8 lines) — add approximately 60 lines of supporting content to a body that currently sits at ~213 lines. The body is well within the 500-line limit now, but these sections are natural candidates for `references/` files if the body grows toward 400+ lines in future iterations. The contingency plan should be defined now so any contributor knows the extraction path without debate.

### Before
```markdown
## Reference: How EDD differs from TDD

| | TDD | EDD |
|---|---|---|
| Unit of confidence | One assertion per behavior | A dataset of N examples scored by evaluators |
...

## Reference: Anti-patterns to call out

If the user does any of these, gently course-correct:
- **Writing the eval after shipping** — defeats the entire point...
...

## Reference: Cooperating skills

You are the methodology layer. Execution is delegated:
- For *writing evaluator code* against LangSmith → invoke or refer to `langsmith-evaluator`
...
```

### After
If the body reaches 400+ lines, extract to:

```
skills/edd/
  skill.md                        (body trimmed by ~60 lines)
  references/
    edd-vs-tdd.md                 (the TDD comparison table)
    anti-patterns.md              (the anti-pattern checklist)
    cooperating-skills.md         (the cooperating-skills section)
```

And replace each section in `skill.md` with a compact reference link:

```markdown
## Reference: How EDD differs from TDD
See [references/edd-vs-tdd.md](references/edd-vs-tdd.md).

## Reference: Anti-patterns
See [references/anti-patterns.md](references/anti-patterns.md).

## Reference: Cooperating skills
See [references/cooperating-skills.md](references/cooperating-skills.md).
```

### Impact if implemented
- **Agent behaviour:** Agents reading the full skill still have access to all reference content via the linked files; the core step-by-step instructions remain in the main body and load faster because the body is smaller.
- **Discoverability:** No change — discoverability is driven by the description, not the body reference sections.
- **Portability:** The `references/` directory is an explicit spec-supported pattern; other teams importing the skill get the full reference material as separate, individually linkable documents.
- **Risk reduced:** Prevents the body silently exceeding the 500-line budget as the skill matures, which would trigger line-budget warnings in CI spec-checkers.

### Existing use (before fix)
Today the body is at ~213 lines and the reference sections are appropriate inline. However, every new anti-pattern added to the "Anti-patterns to call out" section or every new cooperating skill listed adds lines to the body budget. Without a defined extraction path, a future contributor will either hit the 500-line limit unexpectedly or start abbreviating the reference sections (losing quality) rather than extracting them properly.

### Improved use (after fix)
Once the body approaches 400 lines, the extraction is straightforward and non-breaking: three new files under `references/`, three one-line stub replacements in the body. The anti-patterns checklist and EDD-vs-TDD table become individually linkable documents that other skills (e.g., `langsmith-evaluator`, `run-eval`) can reference directly, reducing duplication across the registry.

---

## Priority Order

| Priority | Improvement | Effort | Impact |
|---|---|---|---|
| 1 | Move custom frontmatter fields under `metadata:` | Low | Critical — prevents silent skill-load failures in spec-strict runtimes |
| 2 | Add missing `license` field | Low | High — required spec field; blocks enterprise registry publishing gates |
| 3 | Trim description to create headroom under 1024-char limit | Low | Medium — prevents future contributor from silently breaking discovery |
| 4 | Extract reference sections to `references/` directory | Medium | Low (contingency) — only needed when body approaches 400+ lines |

---

## Before vs After: Full Skill Experience

### Before (current state)

A developer at zysk.tech publishes the `edd` skill to the skills registry. The automated publishing pipeline runs a spec-compliance check and immediately flags two critical violations: eight non-standard top-level frontmatter keys (`version`, `author`, `email`, `category`, `tags`, `product`, `sprint`, `tested_with`) that the schema rejects, and a missing `license` field. In a strict-mode registry deployment, the skill is refused at the gate entirely. In a lenient deployment, it publishes but with all eight custom metadata fields silently dropped — the registry index shows no `version`, no `author`, no `tested_with` model, and no `category`. A colleague searching the registry for `category: engineering-practice` gets zero results. An enterprise client whose registry enforces license declarations cannot serve the skill to their agents at all.

When an agent client does manage to load the skill (lenient parser, no license gate), the behavioral content is excellent — the triage gate fires correctly, the EDD Plan template is produced, and the evaluator scaffold guidance is actionable. But the description is already at 740 characters (72% of the 1024-char limit), and the next contributor who adds "rewriting the retrieval layer" as a trigger phrase without checking the character count pushes it over the limit, silently truncating the last trigger keyword in the list. The agent stops recognizing "change the LLM behavior" as an EDD trigger. No error is surfaced; discovery quietly degrades.

### After (all improvements applied)

With all four improvements applied, the `edd` skill publishes cleanly through the spec-compliance gate. The frontmatter contains exactly the six allowed top-level keys (`name`, `description`, `license`, `compatibility` omitted as acceptable, `metadata`, `allowed-tools` omitted as optional), with all nine custom fields correctly nested under `metadata:` as strings. The `license: "Proprietary — internal use only (zysk.tech)"` field satisfies enterprise registry gates, making the skill visible in filtered searches and safe to serve in regulated deployments. Registry indices can now surface `version: "1.0.0"`, `author: Sharath S Rao`, `tested_with: claude-sonnet-4-6`, and `category: engineering-practice` in search results.

The trimmed description sits at approximately 570 characters — well under the 1024-char limit — with a comfortable buffer for future trigger phrases. Contributors can add "rewriting the retrieval layer", "tuning the ranker", or "changing the scoring model" without risk. The three reference sections remain inline in the body (which is at ~213 lines, well under the 500-line budget), and the `references/` extraction path is documented as a contingency for future iterations. An agent loading this skill gets the full EDD methodology — triage gate, EDD Plan template, dataset guidance, four evaluator types, anti-pattern detection, and CI lock-in — from a fully compliant, reliably parseable, legally unambiguous skill definition.
