# IMPROVEMENTS — hr-resume-screener

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

## Improvement 1 — Add Missing `license` Field

### What needs to change

The frontmatter is missing the required `license` field. The agentskills spec mandates this field on every skill. Without it, automated validation pipelines will flag the skill as non-compliant and registry tooling may reject the submission entirely.

### Before
```yaml
---
name: hr-resume-screener
description: Screen a candidate resume against a Job Description and return a FIT / PARTIAL FIT / NOT A FIT verdict with requirement match, strengths, gaps, salary check, and an Excel-ready summary row.
version: 1.0.0
author: Deepak Padmanabha
email: deepak@zysk.tech
category: business-sales
---
```

### After
```yaml
---
name: hr-resume-screener
description: Screen a candidate resume against a Job Description and return a FIT / PARTIAL FIT / NOT A FIT verdict with requirement match, strengths, gaps, salary check, and an Excel-ready summary row.
license: MIT
metadata:
  version: 1.0.0
  author: Deepak Padmanabha
  email: deepak@zysk.tech
  category: business-sales
---
```

### Impact if implemented
- **Agent behaviour:** No direct change to agent execution; this is a registry-level field. However, validators that gate skill execution on compliance will now pass.
- **Discoverability:** Registry search tools that filter by license (e.g., "show only open-source skills") will now surface this skill correctly.
- **Portability:** Other teams can now see the usage terms before adopting the skill. Without a license, downstream users cannot legally reuse or redistribute the skill.
- **Risk reduced:** Prevents automatic rejection by CI validators that enforce required-field presence in frontmatter.

### Existing use (before fix)
Today, any automated tooling that parses the frontmatter and checks for required fields will immediately flag `hr-resume-screener` as non-compliant due to the absent `license` field. Registry operators running a compliance check see a hard FAIL against this skill. Teams evaluating the skill for adoption cannot determine the usage rights — they either skip it to avoid legal ambiguity or have to contact the author manually. The skill works fine in execution, but it cannot safely be published or shared through any formal channel.

### Improved use (after fix)
Once `license: MIT` is added, the frontmatter passes required-field validation. Registry search surfaces the skill under open-source results. Teams evaluating the skill can immediately confirm they can use, modify, and redistribute it without contacting the author. The CI gate that previously blocked publishing now passes, and the skill can be formally released.

---

## Improvement 2 — Move Non-Standard Fields Under `metadata:`

### What needs to change

Eight non-standard fields — `version`, `author`, `email`, `category`, `tags`, `product`, `sprint`, `tested_with` — are currently placed at the top level of the frontmatter. The agentskills spec is explicit: non-standard fields MUST be nested under a single `metadata:` key. Top-level placement pollutes the standard frontmatter namespace and breaks parsers that only expect spec-defined top-level keys.

### Before
```yaml
---
name: hr-resume-screener
description: Screen a candidate resume against a Job Description and return a FIT / PARTIAL FIT / NOT A FIT verdict with requirement match, strengths, gaps, salary check, and an Excel-ready summary row.
version: 1.0.0
author: Deepak Padmanabha
email: deepak@zysk.tech
category: business-sales
tags:
  - hr
  - resume
  - screening
  - jd-matching
  - recruitment
product: zysk
sprint: 1
tested_with: claude-sonnet-4-6
---
```

### After
```yaml
---
name: hr-resume-screener
description: Screen a candidate resume against a Job Description and return a FIT / PARTIAL FIT / NOT A FIT verdict with requirement match, strengths, gaps, salary check, and an Excel-ready summary row.
license: MIT
metadata:
  version: 1.0.0
  author: Deepak Padmanabha
  email: deepak@zysk.tech
  category: business-sales
  tags:
    - hr
    - resume
    - screening
    - jd-matching
    - recruitment
  product: zysk
  sprint: 1
  tested_with: claude-sonnet-4-6
---
```

### Impact if implemented
- **Agent behaviour:** Parsers that strip non-standard top-level keys before passing frontmatter to the agent runtime will no longer silently drop `author`, `email`, `category`, `tags`, and the rest. All metadata is preserved inside the `metadata` envelope and survives the parse step.
- **Discoverability:** Tag-based search (e.g., "find skills tagged `jd-matching`") relies on `metadata.tags` being in the correct location. Correctly nested tags mean the skill now appears in tag-filtered results for `hr`, `resume`, `screening`, `jd-matching`, and `recruitment`.
- **Portability:** Other registries and tooling that consume the agentskills format will parse the frontmatter without errors. Strict-mode parsers that reject unknown top-level keys will no longer throw on `product`, `sprint`, or `tested_with`.
- **Risk reduced:** Eliminates silent data loss where a compliant parser discards all eight non-standard top-level keys, leaving the skill with no author attribution, no category, and no tags in the registry index.

### Existing use (before fix)
With all eight non-standard fields at the top level, any strict agentskills parser that only accepts `name`, `description`, `license`, `compatibility`, and `allowed-tools` as valid top-level keys will either throw a validation error or silently drop `version`, `author`, `email`, `category`, `tags`, `product`, `sprint`, and `tested_with`. In a registry UI, the skill shows no author, no category, and no tags — it looks like an anonymous, uncategorised stub. Tag searches for `jd-matching` or `recruitment` return no results because the tags were never stored under the correct key path.

### Improved use (after fix)
After nesting under `metadata:`, every parser — strict or lenient — correctly stores all eight fields without errors. The registry UI shows author attribution (`Deepak Padmanabha`), category (`business-sales`), version (`1.0.0`), and the full tag list. Tag-filtered search for `hr`, `resume`, or `jd-matching` returns this skill. The `tested_with: claude-sonnet-4-6` entry is preserved, giving operators and consumers confidence about which model has been validated against this skill.

---

## Improvement 3 — Add `compatibility` Field for File-Upload Dependencies

### What needs to change

The skill's Step 0 and Prerequisites sections explicitly require PDF and Word (.docx) file uploads. These are environment-level capabilities — not all LLM deployments support multimodal file reading. The spec requires a `compatibility` field whenever the skill has external tool or environment dependencies. Without it, an operator deploying this skill in a text-only environment will get a broken skill at runtime with no upfront warning.

### Before
```yaml
---
name: hr-resume-screener
description: Screen a candidate resume against a Job Description and return a FIT / PARTIAL FIT / NOT A FIT verdict with requirement match, strengths, gaps, salary check, and an Excel-ready summary row.
# no compatibility field present
version: 1.0.0
---
```

### After
```yaml
---
name: hr-resume-screener
description: Screen a candidate resume against a Job Description and return a FIT / PARTIAL FIT / NOT A FIT verdict with requirement match, strengths, gaps, salary check, and an Excel-ready summary row.
license: MIT
compatibility: Requires a multimodal LLM capable of reading uploaded PDF and Word (.docx) files, or text pasted directly in chat. No external API or tool integrations required. Tested with claude-sonnet-4-6.
metadata:
  version: 1.0.0
  ...
---
```

### Impact if implemented
- **Agent behaviour:** Deployment tooling that checks `compatibility` before installing a skill can now gate installation on whether the target environment supports file uploads. Operators get an actionable error ("this skill requires multimodal file reading") instead of a silent runtime failure when a user uploads a PDF.
- **Discoverability:** Operators filtering for skills that work in text-only environments know to exclude this one. Operators with multimodal environments know it is safe to install. Reduces mismatched deployments.
- **Portability:** Teams porting this skill to a different LLM provider can immediately see the capability requirement and evaluate whether their target model supports it — without reading through all five steps.
- **Risk reduced:** Prevents the silent failure mode where a user uploads a PDF resume in a text-only deployment, the model cannot read it, and the skill either errors out or fabricates a screening report from nothing.

### Existing use (before fix)
Without a `compatibility` field, there is no machine-readable signal that this skill requires multimodal file-reading capability. An operator deploying `hr-resume-screener` in a text-only LLM environment installs it without any warning. The first time an HR user uploads a PDF resume, the model either throws an error or — worse — proceeds as if the file is empty and produces a fabricated screening report that looks authoritative. There is no way to detect this misconfiguration without reading every line of the skill body. The agentskills registry shows no prerequisites, giving the false impression that the skill works in any environment.

### Improved use (after fix)
With `compatibility` documented, deployment tooling reads the field before installation and immediately flags any text-only environment as incompatible. Operators either upgrade their deployment to support file uploads or inform users to paste text. The registry UI shows the compatibility note, so evaluators never install the skill into an environment where it will silently fail. In environments that do support PDF/Word uploads, the note confirms expected behaviour and the skill proceeds exactly as designed.

---

## Improvement 4 — Strengthen `description` Trigger Keywords for Agent Discovery

### What needs to change

The `description` field accurately describes the output (FIT / PARTIAL FIT / NOT A FIT verdict, requirement match, strengths, gaps, salary check, Excel row) but uses noun phrases rather than action verbs and user-facing trigger phrases. Agent orchestrators that match user utterances to skills by scanning the `description` field will miss common triggers like "check if this candidate is suitable", "is this person right for the role", or "compare resume to JD". Adding action-verb phrasing and at least one explicit trigger phrase to the description significantly increases automatic skill selection accuracy.

### Before
```yaml
description: Screen a candidate resume against a Job Description and return a FIT / PARTIAL FIT / NOT A FIT verdict with requirement match, strengths, gaps, salary check, and an Excel-ready summary row.
```

### After
```yaml
description: Screen or match a candidate resume against a Job Description — upload or paste both to get an instant FIT / PARTIAL FIT / NOT A FIT verdict with requirement-by-requirement match, strengths, gaps, salary band check, and an Excel-ready summary row. Use when asked "is this candidate suitable?", "check this resume against the JD", or "screen this profile".
```

### Impact if implemented
- **Agent behaviour:** Orchestrators using semantic or keyword matching against the `description` field to select skills will now correctly route utterances like "is this candidate right for the role?", "screen this CV against the job spec", or "compare this resume to the JD" to `hr-resume-screener` instead of failing to match or routing to a generic assistant.
- **Discoverability:** The description now surfaces under searches for "match", "suitable", "screen", "CV", "JD", "job spec" — terms that real HR users type but were previously absent from the description.
- **Portability:** Teams customising this skill for their registry can see immediately from the description what utterances trigger it, making it easier to integrate into their own routing logic without reading the full skill body.
- **Risk reduced:** Reduces the failure mode where an HR user types "does this candidate fit the role?" and the orchestrator selects a generic Q&A skill instead of `hr-resume-screener`, producing an unstructured response with none of the verdict logic, salary band check, or Excel row.

### Existing use (before fix)
Today, the description leads with "Screen a candidate resume against a Job Description" — functional but passive. An orchestrator scanning descriptions for utterance matching scores this description low on queries phrased as questions ("is this candidate suitable?") or commands ("compare this resume"). The "When to use" section inside the skill body has excellent trigger phrases ("is this candidate fit for this role?", "check this resume against the JD", "screen this profile") but those are inside the body — many orchestrators only read the `description` field for routing. The result is that the skill is frequently not auto-selected even when it is exactly the right tool.

### Improved use (after fix)
After updating the description to include action verbs ("Screen or match"), a use-case preposition ("Use when asked"), and explicit trigger phrase examples, orchestrators that scan the `description` field now correctly route HR screening requests to this skill. The broader keyword surface ("CV", "job spec", "suitable", "compare") catches natural language variants that HR users actually type. Combined with the existing "When to use" section in the body, the skill is now discoverable both at the routing layer and at the in-context instruction layer.

---

## Improvement 5 — Extract Output Template to a Dedicated Section

### What needs to change

Step 5 currently embeds the full report scaffold — emoji headers, horizontal rules, all five tables, and every label — inline within the step instructions. This makes Step 5 roughly four times longer than Steps 1-4 combined, creating a visually unbalanced instructions section where logic and formatting are interleaved. Separating the template into a dedicated `## Output Template` section after the steps keeps each step focused on logic while making the template easier to update independently.

### Before
```markdown
### Step 5: Produce the Structured Report

Use this exact structure. Keep it verdict-first and readable in under 90 seconds.

---

## 📋 Resume Screening Report

**Candidate:** [Name]  
**Role Applied:** [Role from JD]  
**Screened by:** Zysk HR Screening Assistant  
**Date:** [today's date]

---

### [🟢 FIT / 🟡 PARTIAL FIT / 🔴 NOT A FIT]

> *[One sentence explaining the verdict...]*

---

### 📊 Profile Snapshot
...
### ✅ JD Requirements Match
...
### 💪 Strengths
...
### 🚩 Gaps
...
### 📞 Recommendation
...
### 📤 Excel Row Summary
...
```

### After
```markdown
### Step 5: Produce the Structured Report

Using the template in the **Output Template** section below, generate the full screening report. Place the verdict (🟢 FIT / 🟡 PARTIAL FIT / 🔴 NOT A FIT) first. Complete every table and every section — do not omit any field. The full report must be readable in under 90 seconds.

---

## Output Template

Use this exact structure for every screening report.

## 📋 Resume Screening Report

**Candidate:** [Name]  
**Role Applied:** [Role from JD]  
**Screened by:** Zysk HR Screening Assistant  
**Date:** [today's date]

---

### [🟢 FIT / 🟡 PARTIAL FIT / 🔴 NOT A FIT]

> *[One sentence explaining the verdict...]*

---

### 📊 Profile Snapshot
...
### ✅ JD Requirements Match
...
### 💪 Strengths
...
### 🚩 Gaps
...
### 📞 Recommendation
...
### 📤 Excel Row Summary
...
```

### Impact if implemented
- **Agent behaviour:** No change to verdict logic, matching rules, or salary band checks. The agent still follows Steps 0-4 for extraction and matching, then renders the template. Separation makes it easier to update the template (e.g., add a "Red Flags" section) without touching the step logic.
- **Discoverability:** No direct discoverability impact. Structural improvement only.
- **Portability:** Teams forking this skill and customising the report format can now edit only the `Output Template` section without risk of accidentally modifying extraction or verdict logic in Steps 1-4.
- **Risk reduced:** Reduces the chance of accidental edits to verdict logic when a maintainer only intends to reformat the output template, since the two concerns are now in separate sections.

### Existing use (before fix)
Today, Step 5 is a wall of nested markdown — the full report template is embedded inside the step instruction, making the step hard to scan quickly. A developer reading the skill to understand the verdict logic has to scroll past all five tables in Step 5 to find the edge-case table and Notes section. Updating the report format (e.g., adding a "Red Flags" row to the Excel summary) requires editing deep inside the step body, increasing the chance of accidentally breaking surrounding logic.

### Improved use (after fix)
With the template extracted to a named `## Output Template` section, the Steps section reads cleanly: Steps 0-4 cover input collection and matching logic, Step 5 is a short directive to apply the template. A developer auditing the verdict logic reads only Steps 1-4. A developer updating the report format edits only the Output Template section. The skill body remains well under the 500-line budget and is easier to navigate for both human maintainers and agents processing the skill text at inference time.

---

## Priority Order

| Priority | Improvement | Effort | Impact |
|---|---|---|---|
| 1 | Add missing `license` field | Low | Critical — required field; blocks registry publishing |
| 2 | Move non-standard fields under `metadata:` | Low | Critical — spec violation; breaks strict parsers and tag search |
| 3 | Add `compatibility` field for file-upload dependencies | Low | High — prevents silent runtime failures in text-only deployments |
| 4 | Strengthen `description` trigger keywords | Low | High — directly improves auto-selection accuracy by orchestrators |
| 5 | Extract output template to dedicated section | Medium | Medium — improves maintainability and reduces accidental edits |

---

## Before vs After: Full Skill Experience

### Before (current state)

A developer discovers `hr-resume-screener` in the registry and opens the skill card. The registry UI shows no author name, no category, and no tags — because `author`, `category`, and `tags` are at the top level of the frontmatter and were silently dropped by the strict-mode parser that only accepts spec-defined top-level keys. There is no `license` field, so the legal status is unknown; the developer cannot safely adopt or redistribute the skill without contacting the author directly. There is no `compatibility` field, so when the developer deploys the skill into their text-only LLM environment and an HR user uploads a PDF resume, the model fails to read the file and either errors out or silently generates a fabricated screening report. Because the `description` field uses only noun phrases ("Screen a candidate resume against a Job Description"), the orchestrator's routing layer does not confidently match "is this candidate suitable for the role?" to this skill — it routes to the generic assistant instead, and the user never gets the structured verdict, salary band check, or Excel row they needed.

Even when the skill does get invoked correctly — in the right environment, by the right trigger — a developer trying to update the report format has to navigate Step 5, which is a dense block mixing template markup with step-level instructions. Editing the Excel row summary requires scrolling through the full report scaffold embedded in the step, risking accidental changes to the surrounding verdict and salary logic. The tag list (`hr`, `jd-matching`, `recruitment`) exists in the frontmatter but is unreachable because it is not under `metadata:` — no tag-based search will surface this skill, even though it is one of the most precisely tagged skills in the registry.

### After (all improvements applied)

With all five improvements applied, `hr-resume-screener` is a fully spec-compliant, discoverable, and safely deployable skill. The `license: MIT` field is present — legal status is clear at a glance, and publishing gates pass without issues. All eight non-standard fields are correctly nested under `metadata:`, so tag searches for `hr`, `resume`, `jd-matching`, and `recruitment` all return this skill, and the registry UI shows full attribution to Deepak Padmanabha under the `business-sales` category. The `compatibility` field documents the file-upload requirement upfront — operators deploying into text-only environments see an immediate warning, and the silent PDF-failure mode is eliminated before it ever reaches an HR user.

The updated `description` field now includes action verbs and explicit trigger phrases, so orchestrators routing "is this candidate suitable?" or "check this resume against the JD" correctly select `hr-resume-screener` on the first match rather than falling back to a generic assistant. When the skill is invoked, the agent reads Steps 0-4 for clean extraction and matching logic, then renders the output against the dedicated `## Output Template` section — verdict first, profile snapshot, requirements match table, strengths and gaps, recommendation, and Excel row, exactly as designed. Developers updating the report format edit only the Output Template section without touching verdict logic. The skill is now portable, attributable, tag-searchable, deployment-safe, and fully compliant with the agentskills spec from frontmatter through to edge-case handling.
