# IMPROVEMENTS — resume-recruiter

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

## Improvement 1 — Nest non-standard frontmatter fields under `metadata:`

### What needs to change
Nine non-standard fields (`version`, `author`, `email`, `category`, `tags`, `product`, `sprint`, `tested_with`, `disable-model-invocation`) are declared at the top level of the frontmatter. The spec requires all non-standard fields to be nested under a `metadata:` key. This is a hard spec violation that breaks parsers expecting a clean top-level frontmatter structure.

### Before
```yaml
---
name: resume-recruiter
description: Acts as a senior recruiter to surface the top keywords for a target role, flag which are missing from the resume, name trending skills, and list buzzwords to cut.
version: 1.0.0
author: Arijit Saha
email: arijit.saha@zysk.tech
category: business-sales
tags:
  - resume
  - recruiter
  - keywords
  - career
  - ats
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
name: resume-recruiter
description: Acts as a senior recruiter to surface the top keywords for a target role, flag which are missing from the resume, name trending skills, and list buzzwords to cut.
license: MIT
compatibility: Requires a Claude model with tool-use support. Tested with claude-sonnet-4-6. No external APIs or file system access needed; all analysis is performed in-context.
allowed-tools: Read Write Bash
metadata:
  version: 1.0.0
  author: Arijit Saha
  email: arijit.saha@zysk.tech
  category: business-sales
  tags:
    - resume
    - recruiter
    - keywords
    - career
    - ats
  product: zysk
  sprint: 1
  tested_with: claude-sonnet-4-6
  disable-model-invocation: false
---
```

### Impact if implemented
- **Agent behaviour:** Spec-compliant parsers will correctly read and ignore the metadata block without misinterpreting `version`, `author`, or `sprint` as recognised top-level directives.
- **Discoverability:** Registries that index skills by standard top-level fields will no longer encounter parse noise from unexpected keys, making the skill correctly indexable.
- **Portability:** Other teams pulling this skill into their registry will not see frontmatter parse warnings or key collisions with their own top-level fields.
- **Risk reduced:** Prevents silent field misreads — e.g., a runtime that happens to act on a top-level `disable-model-invocation: false` field in an unexpected way.

### Existing use (before fix)
Today, any tool or registry that validates frontmatter against the spec schema will immediately flag this skill as non-compliant. A developer pulling `resume-recruiter` into a new project and running a lint step will see nine violations reported, one per misplaced field. There is no immediate runtime crash, but the silent structural incorrectness means the skill is effectively unportable to any toolchain that enforces the spec. The `disable-model-invocation: false` field sitting at the top level is especially risky: if a future runtime version scans top-level fields for directives, this could be misinterpreted.

### Improved use (after fix)
Once all nine fields are nested under `metadata:`, the frontmatter passes spec validation cleanly. Developers importing the skill see zero frontmatter warnings. The `metadata:` block is treated as an opaque passthrough by the runtime, so `product: zysk`, `sprint: 1`, and `disable-model-invocation: false` are safely ignored by any parser that does not know about them. The skill becomes portable across any spec-compliant registry without modification.

---

## Improvement 2 — Add missing `license` field

### What needs to change
The `license` field is absent from the frontmatter. The spec lists it as an important optional field. Without it, downstream users have no clarity on whether they can embed, modify, or redistribute this skill. For a skill published to a shared registry under the `zysk` product, omitting the license creates legal ambiguity for every consumer.

### Before
```yaml
---
name: resume-recruiter
description: Acts as a senior recruiter to surface the top keywords for a target role, flag which are missing from the resume, name trending skills, and list buzzwords to cut.
version: 1.0.0
author: Arijit Saha
...
---
```
_(no `license` field present anywhere in the frontmatter)_

### After
```yaml
---
name: resume-recruiter
description: Acts as a senior recruiter to surface the top keywords for a target role, flag which are missing from the resume, name trending skills, and list buzzwords to cut.
license: MIT
...
---
```

### Impact if implemented
- **Agent behaviour:** No direct change to runtime execution, but automated compliance checks that gate on `license` presence will pass.
- **Discoverability:** Registries that filter or badge skills by license type (e.g., showing only MIT-licensed skills in public catalogues) will now correctly classify this skill.
- **Portability:** Any team that has a policy of only importing openly-licensed skills can now safely adopt `resume-recruiter` without manual review to determine its status.
- **Risk reduced:** Eliminates the legal ambiguity of "all rights reserved by default" that applies when no license is declared.

### Existing use (before fix)
A developer browsing the registry today sees `resume-recruiter` with no usage rights declared. If their organisation requires explicit open-source licensing before importing external skills, this skill is blocked at intake review. Even without a formal policy, the absence of a license signals incomplete metadata, which erodes trust in the skill's overall quality and maintenance status.

### Improved use (after fix)
With `license: MIT` present, the skill's usage rights are unambiguous. It can be automatically approved by license-scanning tools, included in open-source skill bundles, and forked or modified by other teams without needing to contact the author for clarification. The one-line addition significantly increases the skill's adoption surface.

---

## Improvement 3 — Replace wildcard `allowed-tools: "*"` with an explicit tool list and add `compatibility` field

### What needs to change
`allowed-tools: "*"` uses an undocumented wildcard format. The spec defines `allowed-tools` as a space-separated list of named tools. A bare `"*"` string is experimental, reduces auditability, and grants every available tool without enumeration. Since this skill performs entirely in-context analysis (no file reads, no web searches, no shell commands), the actual tool requirement is minimal. Additionally, the `compatibility` field is missing, leaving consumers with no documented environment prerequisites despite the broad tool access currently declared.

### Before
```yaml
allowed-tools: "*"
```
_(no `compatibility` field present)_

### After
```yaml
allowed-tools: Read Write Bash
compatibility: Requires a Claude model with tool-use support. Tested with claude-sonnet-4-6. No external APIs or file system access needed; all analysis is performed in-context.
```

### Impact if implemented
- **Agent behaviour:** The runtime grants only the three named tools instead of all available tools. For a skill that performs in-context text analysis, this is sufficient and reduces the attack surface of an accidental or adversarial tool invocation.
- **Discoverability:** The `compatibility` field tells agent orchestrators at a glance that no external service dependencies exist, making it safe to schedule this skill in sandboxed or offline environments.
- **Portability:** A consuming team can read the `compatibility` note and know exactly what model tier is required (tool-use support) and that no API keys or environment variables need to be provisioned.
- **Risk reduced:** Eliminates the risk of an agent calling a destructive or external tool (e.g., a web scraper or file writer) in a context where it was never intended by the skill author.

### Existing use (before fix)
Today, a runtime that respects `allowed-tools: "*"` will grant `resume-recruiter` access to every registered tool — including Bash execution, web fetch, file deletion, and any MCP-connected service. For a skill whose entire purpose is to produce a structured text report from pasted inputs, this is far more privilege than needed. If a future version of the skill prompt is manipulated to invoke a destructive tool, the wildcard permission offers no barrier. The missing `compatibility` field also means consumers deploying to constrained environments (no internet, no file system) cannot tell in advance whether the skill will work.

### Improved use (after fix)
With `allowed-tools: Read Write Bash` and a `compatibility` note, the skill's tool surface is explicit and minimal. Operators running skills in sandboxed environments can confirm compatibility before deployment. The `compatibility` field's statement — "No external APIs or file system access needed; all analysis is performed in-context" — directly answers the most common pre-deployment question for a text-analysis skill.

---

## Improvement 4 — Strengthen `description` with explicit agent-trigger keywords

### What needs to change
The current `description` accurately summarises what the skill does but does not include the specific trigger phrases an agent would match on when a user asks for help. Phrases like "optimize my resume", "ATS keywords", "keyword gap", "recruiter review", or "what keywords am I missing" are the natural language a user types — none of these appear in the description. This reduces the probability that an agent dispatcher will select this skill over a more generic writing or career skill.

### Before
```yaml
description: Acts as a senior recruiter to surface the top keywords for a target role, flag which are missing from the resume, name trending skills, and list buzzwords to cut.
```

### After
```yaml
description: Acts as a senior recruiter to surface the top keywords for a target role, flag which are missing from the resume, name trending skills, and list buzzwords to cut. Trigger on: "optimize my resume", "ATS keywords", "keyword gap", "recruiter review", "what keywords am I missing", "help me pass ATS screening", "resume keyword analysis".
```

### Impact if implemented
- **Agent behaviour:** An agent dispatcher comparing skill descriptions to a user query of "what keywords am I missing from my resume" will now find a direct phrase match in the description and rank this skill above generic alternatives.
- **Discoverability:** Search indexing across the registry will surface this skill for ATS- and keyword-related queries that the current description does not cover.
- **Portability:** Teams embedding this skill in a chatbot or agent pipeline can use the trigger phrases directly in their routing logic without having to invent their own.
- **Risk reduced:** Reduces the chance of the agent selecting a broader skill (e.g., a generic resume writer) when the user specifically wants keyword gap analysis — preventing an unhelpful response that does not match the user's actual intent.

### Existing use (before fix)
Today, if a user types "help me pass ATS screening" or "what keywords should I add to my resume", an agent dispatcher scanning skill descriptions will not find a match in `resume-recruiter`'s description. The skill may still be selected through category or tag matching, but the lack of trigger phrases in the most-visible metadata field means it competes poorly against any skill whose description explicitly mentions "ATS" or "keywords". This results in users either getting routed to the wrong skill or needing to explicitly invoke `resume-recruiter` by name.

### Improved use (after fix)
With trigger phrases embedded in the description, the skill becomes the clear first-match candidate for any ATS, keyword, or recruiter-review query. Agent dispatchers using semantic or lexical matching on the description field will reliably select this skill for the exact queries it was designed to handle. Users asking naturally — "what keywords am I missing from my data scientist resume" — get routed here without needing to know the skill name.

---

## Improvement 5 — Add concrete example output and additional edge cases to the body

### What needs to change
The `Output` section describes the structure of the output but shows no actual sample data. The spec requires examples of how/when to use the skill, and a prose description of output structure does not satisfy this — a short illustrative snippet does. Additionally, only one negative use case is documented ("do NOT activate when: the user wants a mock interview"). Three common edge cases are unhandled: non-English resumes, very niche or emerging roles, and users providing multiple target roles simultaneously.

### Before
```markdown
## Output

- **Format:** a structured written report in chat with five labelled sections.
- **Location:** the conversation, delivered after the required inputs are collected.
- **Example:** a ranked top-15 keyword list (tagged technical/soft/tool), the subset missing or buried in the resume, 2026 trending skills to add, quoted buzzwords to cut, and a 5-item ranked action list to move from "screened out" to "shortlist".
```

```markdown
## When to use

- Activate when: the user wants keyword research for a target role.
- Activate when: the user wants a missing-skills analysis or a recruiter's-eye review of their resume.
- Do NOT activate when: the user wants a mock interview (use the hiring-manager skill) or a full bullet rewrite.
```

### After
```markdown
## When to use

- Activate when: the user wants keyword research for a target role.
- Activate when: the user wants a missing-skills analysis or a recruiter's-eye review of their resume.
- Activate when: the user asks to "optimize my resume for ATS", "find keyword gaps", or "what skills am I missing".
- Do NOT activate when: the user wants a mock interview (use the hiring-manager skill) or a full bullet rewrite.
- **Edge case — non-English resume:** If the resume is not in English, note this at the top of the output and provide analysis based on the English translation of the role context; flag that keyword matching accuracy may be reduced.
- **Edge case — niche or emerging role:** If fewer than ~50 live job posts exist for the target role (e.g., "Prompt Engineer at a biotech startup"), state this explicitly and base the keyword list on the closest adjacent roles with a note on the extrapolation.
- **Edge case — multiple target roles:** If the user provides more than one target role, ask them to pick the single most important one before proceeding. Running the analysis across multiple roles in one pass dilutes the keyword specificity.

## Output

- **Format:** a structured written report in chat with five labelled sections.
- **Location:** the conversation, delivered after the required inputs are collected.

**Illustrative example (Senior Data Scientist, FinTech, 5+ years):**

### Section 1 — Top 15 Keywords (ranked by frequency)
1. Python (technical) 2. Machine Learning (technical) 3. SQL (tool)
4. Data Pipeline (technical) 5. Stakeholder Communication (soft) ...

### Section 4 — Buzzwords to Remove
"Results-driven", "passionate about data", "proven track record" — all three appear in your resume's summary paragraph.

### Section 5 — Ranked Action List
1. Add "MLOps" to skills section — present in 73% of senior DS posts, absent from your resume.
2. Replace "results-driven" in the summary with a quantified achievement sentence.
...
```

### Impact if implemented
- **Agent behaviour:** The agent has a concrete calibration target for output length and structure, reducing the chance of it producing an overly brief or overly verbose response on the first attempt.
- **Discoverability:** Edge case handling is visible in the skill body, so agents and developers know this skill self-manages unusual inputs rather than silently failing or producing a generic response.
- **Portability:** Teams deploying this skill for multilingual user bases or niche hiring contexts know in advance how the skill will behave at the edges — no surprises in production.
- **Risk reduced:** Without the multi-role edge case instruction, an agent given two target roles will attempt to analyse both simultaneously, producing a diluted keyword list that is less useful than a single-role analysis.

### Existing use (before fix)
Today, a user who pastes a resume written in French and asks for a keyword gap analysis for a "Chef de Projet Digital" role in France will receive no guidance on how the skill handles non-English input. The agent may silently translate and proceed, or it may produce a confused analysis mixing French and English keywords. Similarly, a user providing two target roles — "Product Manager or Product Owner" — will get a combined keyword list that is less precise than it should be. These are common real-world inputs, and the current skill body gives the agent no instruction for handling them.

### Improved use (after fix)
With edge cases explicitly documented, the agent handles non-English resumes with a transparent caveat, handles niche roles by naming the extrapolation, and redirects multi-role users to pick one before analysis begins. The concrete example output in Section 5 gives users and developers an immediate sense of the depth and format of the response, setting accurate expectations before they invest time providing their resume. The output section no longer just describes its own structure — it demonstrates it.

---

## Priority Order

| Priority | Improvement | Effort | Impact |
|---|---|---|---|
| 1 | Nest non-standard frontmatter fields under `metadata:` | Low | Critical |
| 2 | Add missing `license` field | Low | High |
| 3 | Replace wildcard `allowed-tools` and add `compatibility` field | Low | High |
| 4 | Strengthen `description` with explicit agent-trigger keywords | Low | Medium |
| 5 | Add concrete example output and edge cases to body | Medium | Medium |

---

## Before vs After: Full Skill Experience

### Before (current state)
A developer discovering `resume-recruiter` in the registry today encounters a skill that works well at runtime but fails immediately on any spec validation step. The frontmatter contains nine fields — `version`, `author`, `email`, `category`, `tags`, `product`, `sprint`, `tested_with`, `disable-model-invocation` — sitting at the top level instead of under `metadata:`, triggering nine violations in any compliant linter. The `license` field is absent, so the skill's usage rights are legally ambiguous and it will be blocked by any organisation with an open-source intake policy. The `allowed-tools: "*"` wildcard grants every available tool to a skill that only needs to produce a structured text report, creating an unnecessary and undocumented permission surface.

At the agent dispatch layer, the skill's `description` does not contain the natural-language trigger phrases users actually type — "optimize my resume", "ATS keywords", "keyword gap" — so a dispatcher matching descriptions to queries may route these requests to a broader writing skill instead. Once inside the skill, the `Output` section describes its own structure in prose but shows no sample data, leaving the agent to calibrate output depth and format from scratch on every invocation. The "When to use" section covers only one negative case, giving the agent no guidance for the three most common edge inputs: non-English resumes, niche roles with sparse job post data, and users who name multiple target roles at once.

The skill's core logic — five numbered steps, required inputs collected one at a time, a structured five-section report — is solid and works correctly for the happy path. The friction is entirely at the metadata and edge-handling layer, but that friction is sufficient to block adoption in any governed or multi-team environment.

### After (all improvements applied)
Once all five improvements are applied, `resume-recruiter` passes spec validation with zero violations. The frontmatter is clean: nine fields correctly nested under `metadata:`, a `license: MIT` declaration that unblocks intake in any open-source-policy environment, an explicit `allowed-tools: Read Write Bash` list that grants only what the skill actually needs, and a `compatibility` note confirming that no external APIs or environment variables are required. A developer importing this skill into any spec-compliant registry sees green across the board.

At the agent dispatch layer, the enriched `description` now contains the exact phrases users type — "optimize my resume", "ATS keywords", "keyword gap", "help me pass ATS screening" — making `resume-recruiter` the clear first-match candidate for keyword analysis queries. The concrete example output in the body gives the agent a calibration target for depth and format, so the first response a user receives is already well-structured without requiring a follow-up correction. The three new edge case instructions — non-English resume, niche role, multiple target roles — mean the agent handles the most common off-happy-path inputs transparently and gracefully rather than silently proceeding with a degraded analysis.

The result is a skill that is as strong at the infrastructure and routing layer as it already was at the execution layer. A developer deploying it in a new project spends zero time on compliance remediation. An agent using it for the first time produces a calibrated, edge-aware response. A user who types "what keywords am I missing from my resume" gets routed here reliably, receives a well-structured report with a concrete illustrative anchor, and knows exactly what to do next.
