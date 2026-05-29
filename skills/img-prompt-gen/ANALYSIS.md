# ANALYSIS - img-prompt-gen

> Generated against the agentskills.io standard (https://agentskills.openml.io).

---

## Overall Verdict

**Partially compliant.** The skill has a clear purpose, well-structured body instructions, a good worked example, and a name that correctly matches its folder. However, it has two critical structural violations: the license field is absent, and nine non-standard frontmatter fields (version, author, email, category, tags, product, sprint, tested_with, disable-model-invocation) are placed at the top level instead of being nested under metadata. The compatibility field is also missing despite a hard dependency on GPT Image 2.

---

## Spec Compliance Checklist

| Check | Status | Detail |
|---|---|---|
| name field format | PASS | img-prompt-gen - lowercase, hyphens only, no leading/trailing hyphens, 13 chars, matches folder name exactly |
| description present and non-empty | PASS | 133 chars - well within 1-1024 char range |
| description describes what it does | PASS | Clearly states it structures a raw image idea into a field-based GPT Image 2 prompt |
| description describes when to use it | WARN | Implies use case but lacks explicit trigger keywords agents can match |
| license field | FAIL | Not present - required field is missing |
| compatibility field | FAIL | Not present; skill has external dependency on GPT Image 2 - prerequisites should be documented |
| metadata field structure | FAIL | Nine non-standard fields (version, author, email, category, tags, product, sprint, tested_with, disable-model-invocation) are at top level instead of nested under metadata |
| allowed-tools field | WARN | Present as wildcard - valid per spec but overly permissive |
| Token budget (body) | PASS | ~950 tokens - well under the 5000-token recommendation |
| Line budget (body) | PASS | 90 body lines - well under the 500-line recommendation |
| scripts/ directory | N/A | Not present (not required) |
| references/ directory | N/A | Not present (not required) |
| assets/ directory | N/A | Not present (not required) |
| Body - step-by-step instructions | PASS | Clear numbered rules, conditional recommendation blocks per photo type, explicit output requirements |
| Body - examples | PASS | One complete worked example with input prompt and full structured output |
| Body - edge cases | WARN | Some edge cases covered but no guidance for multi-category inputs |

---

## What the Skill Gets Right

- The name field is correctly formatted and exactly matches the folder name img-prompt-gen.
- The description is concise and communicates the core value proposition clearly.
- The body is well within both the line budget (90 lines) and token budget (~950 tokens), leaving ample room for growth.
- Conditional recommendation blocks (regular photo, cinematic, infographic, ads) give agents clear branching logic.
- The Do NOT activate when note in the body prevents misuse - a good practice.
- The worked example is complete and realistic, showing both input and full expected output.
- The Notes section reinforces the no-intent-change constraint, reducing ambiguity.

---

## Violations (Must Fix)

### 1. Non-standard frontmatter fields at top level instead of under metadata

The spec requires that all custom/non-standard fields be nested under metadata. Fields version, author, email, category, tags, product, sprint, tested_with, and disable-model-invocation are not part of the standard spec and must be moved.

Current (wrong):

    name: img-prompt-gen
    description: Structures a raw image idea...
    version: 1.0.0
    author: Arijit Saha
    email: arijit.saha@zysk.tech
    category: ai-agents
    tags:
      - prompt-engineering
      - image-generation
    product: zysk
    sprint: 1
    tested_with: claude-sonnet-4-6
    disable-model-invocation: false

Fix:

    name: img-prompt-gen
    description: Structures a raw image idea...
    license: MIT
    compatibility: Designed for use with GPT Image 2 (OpenAI). No local dependencies required.
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

### 2. license field is missing

The license field is a required field per the spec. It must be present in the frontmatter.

Fix: Add license: MIT (or whichever license applies to this skill).

---

### 3. compatibility field is missing with an external tool dependency

The skill has a hard dependency on GPT Image 2 (an external OpenAI service). The compatibility field must document this prerequisite.

Fix: Add compatibility: Requires access to GPT Image 2 (OpenAI). No local dependencies. Outputs a structured prompt string for direct use in the GPT Image 2 interface or API.

---

## What Is More Than Needed (Consider Restructuring)

The Optional paragraph (body line 76: try to make the characters prettier) and the informal vibe language introduce subjective style guidance that could conflict with the stated rule of not changing the user intent. Consider removing or demoting this to a clearly labeled optional enhancement note.

---

## What Is Missing (Must Add)

### 1. license field
Add an explicit license key in the frontmatter (e.g., license: MIT).

### 2. compatibility field
Document that the skill targets GPT Image 2. Agents need to know what environment or external service is required.

### 3. Edge case: overlapping categories
The body does not handle inputs that span multiple recommendation categories (e.g., a cinematic product ad, or an infographic with a cinematic style). Add a brief note on how to combine or prioritize recommendation blocks in such cases.

### 4. Trigger keywords in description
Add explicit trigger phrases like generate image prompt, structure my prompt, or image generation to the description so agent discovery/routing can match user intent more reliably.

Current description:
  Structures a raw image idea into a clean, field-based prompt optimized for GPT Image 2, adding only safe recommendations without changing the user intent.

Improved description:
  Generate or structure an image prompt for GPT Image 2. Use when asked to create, improve, or structure a prompt for image generation - converts a raw idea into a clean field-based prompt without altering the user intent.

---

## Summary Table

| Area | Status | Detail |
|---|---|---|
| name field | Pass | Correctly formatted, matches folder name |
| description field | Warn | Present and descriptive, but lacks explicit trigger keywords for agent discovery |
| license field | Missing | Required field not present |
| compatibility field | Missing | External dependency on GPT Image 2 is undocumented |
| metadata structure | Wrong | Nine non-standard fields at top level; all must be nested under metadata |
| Token budget | Pass | ~950 tokens - well under 5000-token limit |
| Line budget | Pass | 90 body lines - well under 500-line limit |
| Body structure | Excellent | Clear rules, conditional blocks, worked example, output spec, notes |
| Self-containment / portability | Warn | Skill logic is self-contained but has an undocumented hard dependency on GPT Image 2 |