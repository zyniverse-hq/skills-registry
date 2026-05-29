# IMPROVEMENTS — img-prompt-gen

> Improvement plan derived from SKILL.md + ANALYSIS.md audit against the agentskills.openml.io spec.

---

## Quick Summary

| | Before | After |
|---|---|---|
| Spec compliance | Partially compliant | Fully compliant |
| Critical violations | 3 | 0 |
| Agent discoverability | Low | High |
| Portability | Partial | Pass |

---

## Improvement 1 — Move Non-Standard Frontmatter Fields Under metadata

### What needs to change
Nine non-standard fields (`version`, `author`, `email`, `category`, `tags`, `product`, `sprint`, `tested_with`, `disable-model-invocation`) are placed at the top level of the frontmatter. The spec requires all custom/non-standard fields to be nested under a `metadata` key. These fields must be moved, and the two required standard fields (`license`, `compatibility`) must be added at the top level at the same time.

### Before
```yaml
---
name: img-prompt-gen
description: Structures a raw image idea into a clean, field-based prompt optimized for GPT Image 2, adding only safe recommendations without changing the user's intent.
version: 1.0.0
author: Arijit Saha
email: arijit.saha@zysk.tech
category: ai-agents
tags:
  - prompt-engineering
  - image-generation
  - gpt-image-2
  - creative
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
name: img-prompt-gen
description: Generate or structure an image prompt for GPT Image 2. Use when asked to create, improve, or structure a prompt for image generation - converts a raw idea into a clean field-based prompt without altering the user intent.
license: MIT
compatibility: Requires access to GPT Image 2 (OpenAI). No local dependencies. Outputs a structured prompt string for direct use in the GPT Image 2 interface or API.
allowed-tools: "*"
metadata:
  version: 1.0.0
  author: Arijit Saha
  email: arijit.saha@zysk.tech
  category: ai-agents
  tags:
    - prompt-engineering
    - image-generation
    - gpt-image-2
    - creative
  product: zysk
  sprint: 1
  tested_with: claude-sonnet-4-6
  disable-model-invocation: false
---
```

### Impact if implemented
- **Agent behaviour:** Parsers and orchestration layers that validate frontmatter against the spec schema will no longer reject or warn on this skill. Fields like `version` and `author` are preserved but in the correct location.
- **Discoverability:** No direct change to discoverability, but spec-compliant structure allows index tooling to correctly categorise the skill without errors.
- **Portability:** Any team importing this skill into a registry that enforces spec structure will no longer need to manually clean the frontmatter before use.
- **Risk reduced:** Prevents silent frontmatter parse failures where non-standard top-level keys are dropped or cause schema validation errors in strict-mode registries.

### Existing use (before fix)
Today, when a registry or agent loader reads `img-prompt-gen/SKILL.md`, it encounters nine unexpected top-level keys. Depending on the parser, these are either silently ignored (causing `version`, `author`, and `email` to be lost from the skill record) or they trigger a schema validation error that prevents the skill from loading at all. The author's contact information (`arijit.saha@zysk.tech`) and sprint tracking (`sprint: 1`) are effectively invisible to any tooling that only reads spec-defined fields.

### Improved use (after fix)
After the restructure, all nine custom fields are preserved under `metadata` where spec-compliant parsers expect them. The skill loads cleanly in any registry that enforces the agentskills.openml.io schema. Author attribution and version tracking remain accessible via `metadata.author` and `metadata.version` respectively, and no information is lost in the migration.

---

## Improvement 2 — Add Required license Field

### What needs to change
The `license` field is a required field per the agentskills.openml.io spec. It is entirely absent from the current frontmatter. It must be added at the top level with the appropriate SPDX identifier.

### Before
```yaml
---
name: img-prompt-gen
description: Structures a raw image idea into a clean, field-based prompt optimized for GPT Image 2, adding only safe recommendations without changing the user's intent.
version: 1.0.0
author: Arijit Saha
# ... no license field present
---
```

### After
```yaml
---
name: img-prompt-gen
description: Generate or structure an image prompt for GPT Image 2. Use when asked to create, improve, or structure a prompt for image generation - converts a raw idea into a clean field-based prompt without altering the user intent.
license: MIT
compatibility: Requires access to GPT Image 2 (OpenAI). No local dependencies. Outputs a structured prompt string for direct use in the GPT Image 2 interface or API.
allowed-tools: "*"
metadata:
  ...
---
```

### Impact if implemented
- **Agent behaviour:** No runtime behaviour change, but skill distribution pipelines that gate on `license` presence will now accept the skill.
- **Discoverability:** Skills without a license field are often excluded from public registries or flagged as incomplete. Adding `license: MIT` makes this skill eligible for open listing.
- **Portability:** Any developer or team considering importing or forking this skill now has explicit legal clarity on reuse rights.
- **Risk reduced:** Prevents the skill from being blocked by compliance checks in enterprise environments that require all skills to declare a license before use.

### Existing use (before fix)
Without a `license` field, consuming teams and automated pipelines have no way to determine the redistribution terms for `img-prompt-gen`. In regulated or enterprise environments, skills without a declared license are treated as unlicensed and blocked from deployment. Even in open-source registries, the skill appears incomplete and may be auto-excluded from listings that filter for spec-valid entries.

### Improved use (after fix)
With `license: MIT` present, the skill passes license-gate checks in all standard registries. Developers can immediately see they are free to fork, adapt, and redistribute the skill. The skill becomes eligible for public index listings that require spec completeness, increasing its reach and adoption.

---

## Improvement 3 — Add Required compatibility Field to Document GPT Image 2 Dependency

### What needs to change
The skill has a hard external dependency on GPT Image 2 (an OpenAI service), but the `compatibility` field is missing from the frontmatter entirely. Any agent or developer using this skill without GPT Image 2 access will produce structured prompts they cannot execute. The dependency must be made explicit.

### Before
```yaml
---
name: img-prompt-gen
description: Structures a raw image idea into a clean, field-based prompt optimized for GPT Image 2, adding only safe recommendations without changing the user's intent.
# ... no compatibility field
---
```

### After
```yaml
---
name: img-prompt-gen
description: Generate or structure an image prompt for GPT Image 2. Use when asked to create, improve, or structure a prompt for image generation - converts a raw idea into a clean field-based prompt without altering the user intent.
license: MIT
compatibility: Requires access to GPT Image 2 (OpenAI). No local dependencies. Outputs a structured prompt string for direct use in the GPT Image 2 interface or API.
allowed-tools: "*"
---
```

### Impact if implemented
- **Agent behaviour:** Orchestrators that read `compatibility` before routing to a skill can now skip `img-prompt-gen` when GPT Image 2 is unavailable, preventing useless skill execution and confusing partial outputs.
- **Discoverability:** Agents searching for GPT Image 2-compatible skills will now match this skill correctly via the compatibility field.
- **Portability:** Teams evaluating whether to adopt this skill in their stack can immediately see the external service requirement without reading the full body.
- **Risk reduced:** Prevents the silent failure where the skill runs, produces a structured prompt, but the user has no compatible image generation endpoint to use it with — a failure mode that is currently invisible until runtime.

### Existing use (before fix)
Today, an agent that does not have GPT Image 2 access can still invoke `img-prompt-gen` because nothing in the frontmatter signals the external dependency. The skill will execute successfully from the agent's perspective — it will produce a fully formatted prompt block — but that output is only useful inside GPT Image 2. Users without access receive a well-structured prompt they cannot run anywhere, with no explanation from the skill about what tool is required.

### Improved use (after fix)
With `compatibility: Requires access to GPT Image 2 (OpenAI)` declared, smart orchestrators can pre-check environment requirements before invoking the skill. Users and agents that lack GPT Image 2 access receive an upfront, clear signal about the prerequisite rather than discovering the mismatch after the skill has already run. The skill's scope is also clearer to developers browsing the registry.

---

## Improvement 4 — Strengthen description with Explicit Trigger Keywords

### What needs to change
The current `description` reads: "Structures a raw image idea into a clean, field-based prompt optimized for GPT Image 2, adding only safe recommendations without changing the user's intent." It describes what the skill does but does not contain the trigger phrases agents use for intent matching (e.g., "generate image prompt", "structure my prompt", "image generation"). Agent routers rely on keyword overlap between user input and skill descriptions to route correctly — the current description will miss many natural user phrasings.

### Before
```yaml
description: Structures a raw image idea into a clean, field-based prompt optimized for GPT Image 2, adding only safe recommendations without changing the user's intent.
```

### After
```yaml
description: Generate or structure an image prompt for GPT Image 2. Use when asked to create, improve, or structure a prompt for image generation - converts a raw idea into a clean field-based prompt without altering the user intent.
```

### Impact if implemented
- **Agent behaviour:** Agent routers performing keyword or semantic matching will now correctly match user inputs like "generate an image prompt", "help me structure this for image generation", "make this a GPT Image 2 prompt", and "improve my image prompt".
- **Discoverability:** The description now contains the key nouns and verbs users actually type, making auto-discovery substantially more reliable.
- **Portability:** Any registry that surfaces skills via description search will return this skill for image-generation-related queries.
- **Risk reduced:** Prevents the skill being bypassed silently when an agent routes to a less-specific skill because the description lacked the right trigger vocabulary.

### Existing use (before fix)
A user types "help me generate a good prompt for image generation" into an agent that uses description-based routing. The current description contains neither "generate" nor "image generation" as explicit phrases — it uses "structures" and "raw image idea" instead. The router either fails to match `img-prompt-gen` at all, or ranks it lower than a generic writing skill that happens to contain the word "generate". The user either receives no skill match or the wrong skill.

### Improved use (after fix)
With the updated description, the same user input "help me generate a good prompt for image generation" now matches directly on "generate", "image prompt", and "image generation" — all present in the new description. The router surfaces `img-prompt-gen` as the top match. The skill activates correctly without the user needing to know the skill's exact name or phrasing.

---

## Improvement 5 — Add Edge Case Guidance for Multi-Category Inputs

### What needs to change
The body defines four distinct recommendation blocks (regular photo, cinematic, infographic, ads) but provides no guidance for inputs that span multiple categories — for example, a cinematic product advertisement, or an infographic with a premium aesthetic. Without this guidance, the agent must guess which block to apply, risks applying both (producing contradictory recommendations), or silently picks one and drops the other.

### Before
```markdown
**For cinematic / high-quality photography:**
If the idea asks for premium quality, cinematic look, movie still, luxury, aesthetic visual, or best photo quality, add:
...

**For ads generation:**
If the idea is an ad, product promo, commercial banner, marketing creative, or social media advertisement, add:
...

(No guidance on what to do when both conditions apply)
```

### After
```markdown
**For cinematic / high-quality photography:**
If the idea asks for premium quality, cinematic look, movie still, luxury, aesthetic visual, or best photo quality, add:
...

**For ads generation:**
If the idea is an ad, product promo, commercial banner, marketing creative, or social media advertisement, add:
...

**Combining categories:**
If the user's idea spans multiple categories (e.g., a cinematic product ad, or a premium-quality infographic), apply both relevant recommendation blocks. Remove any lines that directly contradict each other — for example, if cinematic and ads blocks both reference composition, keep only the more specific line. Never add duplicate fields.
```

### Impact if implemented
- **Agent behaviour:** The agent now has explicit merge logic for overlapping categories. It will apply both recommendation blocks, de-duplicate conflicting lines, and produce a single coherent structured prompt rather than guessing or silently dropping one block.
- **Discoverability:** No impact on discoverability.
- **Portability:** Teams using this skill for varied creative briefs (common in agency workflows) will no longer need to manually resolve category overlaps.
- **Risk reduced:** Prevents silent quality degradation where a cinematic product ad gets only the ads block applied (losing cinematic quality cues) or both blocks applied verbatim (producing a duplicate composition field that confuses GPT Image 2).

### Existing use (before fix)
A user inputs "Create a cinematic product advertisement for a luxury watch brand". The current skill body has two candidate blocks — cinematic and ads — but no rule for which takes precedence or how to merge them. The agent likely applies whichever block appears first in the file (cinematic), and the ads-specific guidance ("no extra text, no watermarks, clean composition, strong color direction") is silently dropped. The resulting structured prompt is incomplete for the stated use case.

### Improved use (after fix)
With merge guidance in place, the agent applies both the cinematic block ("focused cinematic shot, natural light, movie-still composition, strong vignette") and the ads block ("no extra text, no watermarks, clean composition, strong color direction"). It identifies that both blocks reference "composition" and keeps only the more specific ads-block line. The final structured prompt is coherent, complete for both the cinematic aesthetic and advertising constraints, and contains no contradictory duplicate fields.

---

## Priority Order

| Priority | Improvement | Effort | Impact |
|---|---|---|---|
| 1 | Move Non-Standard Frontmatter Fields Under metadata | Low | Critical |
| 2 | Add Required license Field | Low | Critical |
| 3 | Add Required compatibility Field | Low | Critical |
| 4 | Strengthen description with Explicit Trigger Keywords | Low | High |
| 5 | Add Edge Case Guidance for Multi-Category Inputs | Low | Medium |

---

## Before vs After: Full Skill Experience

### Before (current state)
A developer browsing the agentskills registry encounters `img-prompt-gen` and attempts to load it into their pipeline. The frontmatter parser immediately flags nine unexpected top-level keys (`version`, `author`, `email`, `category`, `tags`, `product`, `sprint`, `tested_with`, `disable-model-invocation`) that are not part of the spec schema. Depending on the parser's strictness, the skill either fails to load entirely or loads with those nine fields silently discarded — meaning the author's contact (`arijit.saha@zysk.tech`) and version tracking (`1.0.0`) are invisible to the registry. On top of this, the required `license` and `compatibility` fields are completely absent, causing the skill to fail spec compliance checks and be excluded from public index listings.

For an agent trying to route user requests, the situation is equally problematic. When a user says "help me generate a prompt for image generation", the description "Structures a raw image idea into a clean, field-based prompt" does not match on the words the user actually used — "generate" and "image generation" are absent from the description. The router may pass over `img-prompt-gen` entirely and fall back to a generic skill. If the skill does get invoked, there is no `compatibility` field to warn the agent or user that GPT Image 2 access is required — so the skill happily produces a well-structured prompt block that cannot be executed in the current environment, and no error is surfaced.

At the body level, the skill works well for single-category inputs but breaks silently for multi-category requests. A user asking for a "cinematic luxury product ad" will receive a prompt with only one of the two applicable recommendation blocks applied, because the body provides no merge rule. The quality degradation is invisible — the output looks correct but is missing half its guidance.

### After (all improvements applied)
With all five improvements applied, `img-prompt-gen` is fully spec-compliant and loads cleanly in any agentskills-compatible registry. The frontmatter now has the correct structure: `name`, `description`, `license: MIT`, `compatibility`, and `allowed-tools` at the top level, with all nine custom fields correctly nested under `metadata`. Registry parsers accept the skill without warnings, and the author attribution and version information are preserved and accessible. License compliance checks pass, making the skill eligible for open public listings.

Agent routing is now reliable. The updated description — "Generate or structure an image prompt for GPT Image 2. Use when asked to create, improve, or structure a prompt for image generation" — contains the exact trigger vocabulary users type. Routers matching on "generate image prompt", "structure my prompt", or "image generation" surface `img-prompt-gen` as the top-ranked skill. The `compatibility` field ensures that before the skill is invoked, orchestrators can verify GPT Image 2 access is available, preventing the silent mismatch between a correctly structured output and an environment that cannot execute it.

Inside the body, the new multi-category merge guidance handles the full range of creative briefs without silent quality loss. A user requesting a cinematic product advertisement now gets both the cinematic and ads recommendation blocks applied, with contradicting lines cleanly resolved. The skill's output is accurate for the full spectrum of inputs it claims to support — everyday photos, cinematic shots, infographics, advertisements, and combinations of these — making it genuinely production-ready for agency and AI creative workflows.
