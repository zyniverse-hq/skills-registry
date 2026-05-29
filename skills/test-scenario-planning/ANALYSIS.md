# ANALYSIS -- test-scenario-planning

> Generated against the [agentskills.io](https://agentskills.openml.io) standard.

---

## Overall Verdict

**Partially compliant.** The skill is well-structured with clear step-by-step instructions, a concrete example, and sensible output conventions. However, it has two significant violations: multiple non-standard frontmatter fields (version, author, email, category, tags, product, sprint, tested_with) are placed at top-level instead of under metadata:, and the license field is absent. The description is functional but could carry stronger trigger keywords to improve agent discovery.

---

## Spec Compliance Checklist

| Check | Status | Detail |
|---|---|---|
| name field format | PASS | test-scenario-planning -- lowercase, hyphens only, no leading/trailing hyphens, 22 chars, matches folder name exactly |
| description present and non-empty | PASS | 103 characters, well within 1-1024 range |
| description describes what it does | PASS | Clearly states planning high-level test scenarios covering user behaviors and business rules |
| description describes when to use it | WARN | Implies pre-code use but lacks trigger phrases like "write scenarios for", "plan test scenarios", "QA planning", "test strategy" that would help agents match user intent |
| license field | FAIL | Field is absent entirely |
| compatibility field | -- | Not present; not required, but the skill depends on Playwright browser tools which is a meaningful environment prerequisite |
| metadata field structure | FAIL | Eight non-standard fields (version, author, email, category, tags, product, sprint, tested_with) appear at top-level frontmatter instead of nested under metadata: |
| allowed-tools field | -- | Not present; optional, but worth considering given the Playwright browser tool dependency in Step 1 |
| Token budget (body) | PASS | Body is ~97 lines / ~3,300 characters / ~825 tokens -- well within the 5,000-token budget |
| Line budget (body) | PASS | 97 body lines (lines 17-113) -- well within the 500-line limit and under the 400-line warning threshold |
| scripts/ directory | -- | Not present; not required for this skill |
| references/ directory | -- | Not present; not required for this skill |
| assets/ directory | -- | Not present; not required for this skill |
| Body -- step-by-step instructions | PASS | Four clearly numbered steps covering feature exploration, scenario identification, document writing, and report generation |
| Body -- examples | PASS | Concrete example showing user prompt, agent action, and expected result |
| Body -- edge cases | WARN | Scenario types (positive/negative/edge) are well-defined, but the skill does not address what to do if the live URL is inaccessible -- the only stated prerequisite |

---

## What the Skill Gets Right

- The name field is perfectly formatted and exactly matches the folder name.
- Step-by-step instructions are numbered, clearly scoped, and easy to follow without ambiguity.
- The scenario table format (ID, Scenario, Type, Priority, Risk) is well-defined with concrete inline examples and explicit priority/risk rules.
- The "When to use" and "Do NOT activate when" sections provide useful disambiguation against adjacent skills (e.g. playwright-test-generation), reducing false activations.
- The mandatory report requirement (Step 4) is stated emphatically and includes a detailed required structure -- good for consistent agent output.
- The "Notes" section reinforces key behavioral rules (scenario count cap, specificity of names, live-first exploration) without repeating the full steps.
- Body is concise -- only 97 lines and ~825 tokens, leaving ample room for future expansion.
- The example is realistic and follows the input / action / result pattern well.

---

## Violations (Must Fix)

### 1. Non-standard frontmatter fields must be nested under metadata:

Current (violating):

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

Fix -- move all non-standard fields under metadata::

    ---
    name: test-scenario-planning
    description: Plan high-level test scenarios that describe user behaviors and business rules before writing test code.
    license: MIT
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

The spec is explicit: "Non-standard frontmatter fields must be nested under metadata:, not at top-level." The only recognized top-level fields are name, description, license, compatibility, metadata, and allowed-tools.

### 2. license field is missing

The spec lists license as an optional field but its absence is a gap for any skill intended for shared or registry use. A license must be added at the top level (not under metadata:).

Fix: Add `license: MIT` (or the appropriate license) as a top-level frontmatter field.

---

## What is More Than Needed (Consider Restructuring)

- The blockquote in Step 2 listing guiding questions works well as a mental model prompt but could be folded into a brief inline list to keep formatting uniform with the rest of the document.
- The "Output" section (after Step 4) largely repeats information already stated in Step 3 and Step 4. It could be removed or reduced to a single line, since the steps themselves already specify file locations and formats.

---

## What is Missing (Must Add)

1. **license field** -- Add a top-level `license:` field. Without it the skill is ambiguously licensed for registry consumers. Example: `license: MIT`.

2. **metadata: wrapper for all custom fields** -- All eight non-standard fields (version, author, email, category, tags, product, sprint, tested_with) must move under `metadata:`. See the corrected frontmatter in Violations above.

3. **Fallback behavior when live URL is inaccessible** -- The skill lists "Live URL of the feature to explore is accessible" as a prerequisite but provides no guidance for what to do if it is not. Add a brief fallback instruction such as: "If no live URL is available, request a feature description, wireframes, or requirements document from the user before proceeding to Step 2."

4. **compatibility field (recommended)** -- The skill relies on Playwright browser tools in Step 1. This is a meaningful environment dependency. Adding a `compatibility` field makes the skill more portable and self-documenting. Example: `Requires Playwright MCP browser tools to be available. Tested with claude-sonnet-4-6. Outputs written to specs/ and reports/ directories relative to project root.`

5. **Stronger trigger keywords in description** -- The description is clear but agents matching "write scenarios for X" or "plan test scenarios for X" may not reliably score this skill without those phrases. Consider: "Plan and document high-level QA test scenarios covering user behaviors, business rules, and edge cases before writing test code. Use when asked to write scenarios for a feature, plan test coverage, create a test strategy, or define what to test."

---

## Summary Table

| Area | Status | Detail |
|---|---|---|
| name field | Pass | Correct format, matches folder name, 22 chars |
| description field | Warn | Present and accurate; trigger keyword coverage is thin for agent discovery |
| license field | Missing | Absent entirely -- must be added |
| compatibility field | -- | Absent; recommended given Playwright dependency |
| metadata structure | Wrong | Eight non-standard fields at top level instead of under metadata: |
| Token budget | Pass | ~825 tokens -- well within 5,000-token limit |
| Line budget | Pass | 97 body lines -- well within 500-line limit |
| Body structure | Excellent | Clear numbered steps, explicit output format, good notes section |
| Self-containment / portability | Warn | Depends on Playwright browser tools with no fallback; not documented in compatibility |