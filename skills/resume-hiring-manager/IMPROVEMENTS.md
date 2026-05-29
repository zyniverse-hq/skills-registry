# IMPROVEMENTS — resume-hiring-manager

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

## Improvement 1 — Nest Non-Standard Frontmatter Fields Under `metadata:`

### What needs to change
Nine non-standard fields (`version`, `author`, `email`, `category`, `tags`, `product`, `sprint`, `tested_with`, `disable-model-invocation`) are declared at the top level of the YAML frontmatter. The agentskills.openml.io spec mandates that all custom fields be nested under a single `metadata:` key. These fields must be moved there.

### Before
```yaml
---
name: resume-hiring-manager
description: Runs a realistic mock interview as the hiring manager for the user's target role, asking hard technical and behavioural questions, scoring answers, and giving a hireability score.
version: 1.0.0
author: Arijit Saha
email: arijit.saha@zysk.tech
category: business-sales
tags:
  - resume
  - interview
  - mock-interview
  - career
  - hiring
product: zysk
sprint: 1
tested_with: claude-sonnet-4-6
disable-model-invocation: false
allowed-tools: "*"
---
```

### After
```yaml
---
name: resume-hiring-manager
description: Runs a realistic mock interview as the hiring manager for the user's target role, asking hard technical and behavioural questions, scoring answers, and giving a hireability score.
license: MIT
allowed-tools: "*"
metadata:
  version: 1.0.0
  author: Arijit Saha
  email: arijit.saha@zysk.tech
  category: business-sales
  tags:
    - resume
    - interview
    - mock-interview
    - career
    - hiring
  product: zysk
  sprint: 1
  tested_with: claude-sonnet-4-6
  disable-model-invocation: false
---
```

### Impact if implemented
- **Agent behaviour:** Agents and registries that parse the frontmatter according to the spec will now correctly recognize only `name`, `description`, `license`, and `allowed-tools` as top-level fields, and treat the rest as structured metadata. Parsers that strictly validate top-level keys will no longer reject or warn on this skill.
- **Discoverability:** Registries that index skills by `metadata.category` and `metadata.tags` will now be able to correctly surface this skill under `business-sales` and tags like `mock-interview`, `career`, and `hiring`. Before the fix, these fields are invisible to tag-based search.
- **Portability:** Any consuming project that imports skills from the registry and validates frontmatter structure will parse this skill without errors after the fix.
- **Risk reduced:** Prevents silent mis-classification — today a registry could fail to index the skill under its intended category/tags without any visible error to the author.

### Existing use (before fix)
Today, when a registry or agent harness parses `resume-hiring-manager/SKILL.md`, it encounters `version`, `author`, `email`, `category`, `tags`, `product`, `sprint`, `tested_with`, and `disable-model-invocation` as unknown top-level keys. Strict parsers will either reject the file with a validation error or silently drop these fields. Tag-based lookups for `mock-interview` or `career` will return zero results for this skill because the `tags` array is not nested where the spec expects it. The skill cannot be discovered by category filter either.

### Improved use (after fix)
After the fix, the frontmatter is spec-compliant. A registry indexing by `metadata.tags` will find this skill when a user searches for `mock-interview`, `interview`, or `career`. A harness checking `metadata.tested_with` can confirm the skill is validated against `claude-sonnet-4-6`. The `metadata.disable-model-invocation: false` flag is readable and actionable by orchestrators. No frontmatter parse errors occur.

---

## Improvement 2 — Add the Missing `license` Field

### What needs to change
The `license` field is absent from the frontmatter entirely. Without it, downstream consumers — agents, aggregators, enterprise registries — cannot determine the usage rights of this skill. This blocks adoption in any environment with compliance requirements.

### Before
```yaml
---
name: resume-hiring-manager
description: Runs a realistic mock interview as the hiring manager for the user's target role, asking hard technical and behavioural questions, scoring answers, and giving a hireability score.
version: 1.0.0
author: Arijit Saha
...
---
```
(no `license` field anywhere in the frontmatter)

### After
```yaml
---
name: resume-hiring-manager
description: Runs a realistic mock interview as the hiring manager for the user's target role, asking hard technical and behavioural questions, scoring answers, and giving a hireability score.
license: MIT
allowed-tools: "*"
metadata:
  ...
---
```

### Impact if implemented
- **Agent behaviour:** Orchestration platforms that gate skill loading on a declared license will now be able to load and execute `resume-hiring-manager` without manual override.
- **Discoverability:** Registries that filter by license (e.g., "show only MIT skills") will surface this skill once the field is present.
- **Portability:** Teams that operate under open-source or compliance policies can safely adopt the skill once its license is declared. Without it, legal review is required before any production use.
- **Risk reduced:** Eliminates the ambiguity that leads teams to avoid using an unlicensed skill in shared or commercial environments.

### Existing use (before fix)
Currently, any user or team looking at `resume-hiring-manager` in the registry cannot determine whether they are permitted to fork it, embed it in a product, or redistribute it. Enterprise consumers with legal review workflows will flag the skill as unusable. Automated registry tools that enforce a `license` field will emit a warning or fail validation on this skill.

### Improved use (after fix)
With `license: MIT` declared, the skill is immediately adoptable by any team operating under permissive open-source policies. Registry tools pass validation. Enterprise compliance checks resolve automatically. The skill author's intent is unambiguous.

---

## Improvement 3 — Add an `## Edge Cases` Subsection to the Body

### What needs to change
The body handles missing inputs (ask one at a time) but does not address three real-world failure modes: (1) the user refusing to provide a resume, (2) highly niche or non-standard roles where the model may lack domain depth, and (3) non-English input. These gaps mean the skill silently degrades — the interview either stalls or produces generic questions — without the user understanding why.

### Before
```markdown
Required inputs (ask one at a time if missing):
- Target role: [TARGET ROLE]
- Company type: [COMPANY TYPE]
- Seniority: [JUNIOR / MID / SENIOR / LEAD]
- Resume: [PASTE RESUME]

Start with question 1.
```
(no edge case guidance anywhere in the body)

### After
```markdown
Required inputs (ask one at a time if missing):
- Target role: [TARGET ROLE]
- Company type: [COMPANY TYPE]
- Seniority: [JUNIOR / MID / SENIOR / LEAD]
- Resume: [PASTE RESUME]

Start with question 1.

## Edge Cases

- **No resume provided:** If the user declines to paste a resume, proceed with the interview using generic role-appropriate questions. Inform the user: "Without your resume I'll ask standard questions for this role — answers will be less tailored to your background." Do not block the interview.
- **Highly niche or non-standard roles:** If the target role is uncommon (e.g., "Quantum Hardware Calibration Engineer", "Chief Metaverse Officer"), state upfront: "My questions will reflect general senior-level expectations for this domain — some specifics may not match your exact stack." Then proceed.
- **Non-English input:** If the user writes in a language other than English, conduct the entire interview in that language. Scoring rubrics and feedback apply identically.
```

### Impact if implemented
- **Agent behaviour:** The skill no longer stalls or loops on the resume prompt if the user explicitly says "I don't have one". The agent has a clear instruction to continue with generic questions, maintaining interview flow.
- **Discoverability:** No direct discoverability impact, but the skill becomes more robustly self-contained — a property that well-designed registries score positively.
- **Portability:** International users and users in highly specialized fields can now use the skill without hitting an undocumented dead-end.
- **Risk reduced:** Eliminates the silent quality degradation where the skill proceeds without a resume but never informs the user that their feedback will be less tailored.

### Existing use (before fix)
Today, if a user says "I don't want to share my resume", the skill has no guidance on how to proceed. The agent may loop on the resume prompt, make up resume content, or proceed silently with generic questions while still framing them as tailored — misleading the user. Similarly, a user practicing for a role like "Principal MLOps Engineer at a GPU cloud startup" may receive questions that feel mismatched because the skill has no fallback for depth-limited domains.

### Improved use (after fix)
After the fix, the skill explicitly unblocks the no-resume path, sets correct expectations for niche roles, and handles non-English users without friction. A user who declines to share their resume immediately sees a clear explanation and the interview continues. A user writing in French receives French-language questions and feedback scored by the same rubric.

---

## Improvement 4 — Strengthen the `description` Field with Activation-Triggering Keywords

### What needs to change
The current `description` is accurate but written from the skill's perspective ("Runs a realistic mock interview..."). Agent routing models use the description to match user intent phrasing. Adding explicit trigger phrases that mirror how users actually ask — "prep for my interview", "practice interview questions", "get ready for a job interview" — increases the probability of correct skill selection over competing skills like `hr-resume-screener`.

### Before
```yaml
description: Runs a realistic mock interview as the hiring manager for the user's target role, asking hard technical and behavioural questions, scoring answers, and giving a hireability score.
```

### After
```yaml
description: Runs a realistic mock interview as the hiring manager for the user's target role. Use when the user wants to prep for a job interview, practice interview questions, rehearse answers, get a hireability score, or simulate a real hiring conversation with tough technical and behavioural questions.
```

### Impact if implemented
- **Agent behaviour:** Routing agents comparing skill descriptions against user utterances like "help me prep for my Google interview" or "I want to practice behavioural questions" will score this skill higher due to lexical and semantic overlap with "prep", "practice", "rehearse", and "simulate".
- **Discoverability:** The expanded keyword surface — "prep for a job interview", "practice interview questions", "rehearse answers", "simulate a real hiring conversation" — covers more of the natural language space users actually type.
- **Portability:** No change to portability, but the stronger description reduces misrouting to `hr-resume-screener` (which screens candidates rather than coaching them).
- **Risk reduced:** Reduces the probability that a user asking to "practice interview questions" gets routed to the wrong skill.

### Existing use (before fix)
With the current description, an agent matching "I want to practice for my interview next week" against available skills may score `hr-resume-screener` equally or higher because "resume" is a salient word in both contexts. The user ends up in the wrong skill, receives keyword analysis instead of a mock interview, and must re-invoke manually.

### Improved use (after fix)
The expanded description raises the semantic similarity score for interview-prep intent phrasing. A user saying "I have a big interview on Friday and want to rehearse" is correctly routed to `resume-hiring-manager` rather than `hr-resume-screener`. The negative activation guard already present in the `When to use` section reinforces the correct boundary from the body side.

---

## Priority Order

| Priority | Improvement | Effort | Impact |
|---|---|---|---|
| 1 | Nest non-standard frontmatter fields under `metadata:` | Low | Critical |
| 2 | Add the missing `license` field | Low | Critical |
| 3 | Strengthen `description` with activation-triggering keywords | Low | High |
| 4 | Add `## Edge Cases` subsection to the body | Medium | Medium |

---

## Before vs After: Full Skill Experience

### Before (current state)
A developer browsing the skills registry and searching for `category: business-sales` or `tags: mock-interview` will not find `resume-hiring-manager` — the `category` and `tags` fields are at the top level of the frontmatter, outside the `metadata:` block where the spec and registry indexer expect them. The skill exists in the registry but is effectively invisible to tag and category filters. When the developer does locate the file manually and inspects the frontmatter, they see no `license` field — meaning they cannot determine whether they can embed this skill in their product, fork it, or redistribute it. Any compliance review flags it as unusable until licensing is clarified.

At runtime, an orchestration agent comparing user intent "I want to rehearse for my product manager interview next week" against available skill descriptions finds the current `description` — "Runs a realistic mock interview..." — and scores it against `hr-resume-screener`. Because "resume" is a dominant keyword in the user's implied context and the current description lacks phrases like "practice", "rehearse", or "prep", the agent may route the user to the wrong skill. If routing is correct, the interview begins — but if the user declines to provide a resume or writes in French, the skill has no documented fallback and the agent behavior becomes undefined: it may loop on the resume prompt, silently proceed with generic questions, or produce feedback in English regardless of input language.

### After (all improvements applied)
With all four improvements applied, `resume-hiring-manager` becomes fully spec-compliant and operationally robust. The frontmatter is restructured so that `name`, `description`, `license: MIT`, and `allowed-tools: "*"` are top-level spec fields, and all nine custom fields are cleanly nested under `metadata:`. A registry indexing by `metadata.tags` now surfaces this skill for searches on `mock-interview`, `career`, and `hiring`. A registry filtering by license returns it for `MIT`. Enterprise teams can adopt it immediately without a legal review cycle.

The enhanced `description` — now including "prep for a job interview", "practice interview questions", "rehearse answers", and "simulate a real hiring conversation" — gives routing agents a richer lexical and semantic surface to match against user intent. Misrouting to `hr-resume-screener` is substantially reduced. At runtime, the new `## Edge Cases` section ensures the interview never stalls: a user who declines to share a resume sees a clear explanation and the session continues with generic role-appropriate questions; a user practicing for a niche role receives an upfront caveat about domain depth; a non-English user conducts the entire interview in their language with the same scoring rubric applied. The skill is now portable, discoverable, licensable, and resilient to the real-world edge cases its users will encounter.
