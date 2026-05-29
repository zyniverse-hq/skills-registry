# ANALYSIS — deploy-shield

> Generated against the [agentskills.io](https://agentskills.openml.io) standard.

---

## Overall Verdict

**Partially compliant.** The skill has a strong, well-structured body with clear step-by-step instructions, excellent trigger keywords in the description, and a thoughtful output format. However, it has multiple spec violations: eight non-standard frontmatter fields (Version, Author, Email, Category, Tags, Product, Sprint, Tested_with) are declared at the top level instead of under metadata:, and the license and compatibility fields are absent entirely.

---

## Spec Compliance Checklist

| Check | Status | Detail |
|---|---|---|
| name field format | PASS | deploy-shield — lowercase, hyphens only, no leading/trailing hyphen, 13 chars, exactly matches folder name |
| description present & non-empty | PASS | 342 chars — within 1-1024 char range |
| description describes what it does | PASS | Clearly states it audits a codebase branch or diff for production risks, deployment safety, and engineering hygiene |
| description describes when to use it | PASS | Lists specific trigger scenarios: safe to deploy, blast radius, rollback safety, pre-release risk report |
| license field | FAIL | Not present — field is missing |
| compatibility field | FAIL | Not present — skill depends on git CLI tools and file system access; prerequisites should be documented here |
| metadata field structure | FAIL | Eight non-standard fields (Version, Author, Email, Category, Tags, Product, Sprint, Tested_with) are at top-level frontmatter instead of nested under metadata: |
| allowed-tools field | N/A | Not present (optional) |
| Token budget (body) | PASS | ~1920 tokens — well under the 5000-token recommendation |
| Line budget (body) | PASS | 178 body lines — well under the 500-line limit |
| scripts/ directory | N/A | Not present; skill does not bundle scripts (acceptable) |
| references/ directory | N/A | Not present (optional) |
| assets/ directory | N/A | Not present (optional) |
| Body — step-by-step instructions | PASS | Five clearly numbered steps covering stack identification, scope clarification, five-dimension analysis, severity classification, and report writing |
| Body — examples | WARN | Output format example is present and detailed; however, there are no concrete input examples (e.g., a sample invocation or trigger phrase in context) |
| Body — edge cases | PASS | Covers Do NOT activate when cases, large multi-area diffs, staging vs. production threshold differences, and What NOT to flag guidance |

---

## What the Skill Gets Right

- The name field is perfectly formed: lowercase, hyphenated, matches the folder name exactly.
- The description is rich with trigger keywords (blast radius, rollback safety, pre-release, safe to deploy, audit dependencies) that make agent discovery highly effective.
- The five-dimension analysis framework (Production Readiness, Blast Radius, Dependency Health, Code Hygiene, Deployment and Rollback Safety) is comprehensive and well-explained.
- The severity classification (CRITICAL / HIGH / MEDIUM / LOW) gives clear, actionable output structure.
- The Do NOT activate when and What NOT to flag sections prevent false positives and misuse.
- The output report template is detailed and reproducible — an agent following it will produce consistent, structured results.
- Body is well within both the line (178/500) and token (~1920/5000) budgets, leaving room for future expansion.
- Step 2 explicitly tells the agent when to ask questions and when to skip — preventing unnecessary user interruptions.

---

## Violations (Must Fix)

### 1. Non-standard frontmatter fields at top level instead of under metadata:

The spec requires that any field that is not one of name, description, license, compatibility, metadata, or allowed-tools MUST be nested under metadata:. The following eight fields are currently at the top level and violate this rule: Version, Author, Email, Category, Tags, Product, Sprint, Tested_with.

**Current (wrong):**

    ---
    name: deploy-shield
    description: ...
    Version: 1.0.0
    Author: Akash R
    Email: akash.r@zysk.tech
    Category: deployment-safety
    Tags: deployment, code-review, production-safety, risk-audit
    Product: zysk
    Sprint: 1
    Tested_with: claude-sonnet-4-6
    ---

**Fix:**

    ---
    name: deploy-shield
    description: ...
    license: MIT
    compatibility: Requires git CLI available in PATH. Works with any language/framework — stack is auto-detected from the diff.
    metadata:
      version: 1.0.0
      author: Akash R
      email: akash.r@zysk.tech
      category: deployment-safety
      tags: deployment, code-review, production-safety, risk-audit
      product: zysk
      sprint: 1
      tested_with: claude-sonnet-4-6
    ---

### 2. license field is missing

Skills without a license cannot be safely reused or published on agentskills.openml.io. The license field must be added at the top level of the frontmatter.

**Fix:** Add license: MIT (or the appropriate license) to the frontmatter at the top level.

### 3. compatibility field is missing

The skill instructs the agent to run git diff --stat and git status, which requires a git CLI. This is an external tool dependency that must be documented in the compatibility field (max 500 chars).

**Fix:** Add to frontmatter:

    compatibility: Requires git CLI available in PATH. Target directory must be a git repository. No other runtime dependencies — language and framework are auto-detected from the diff.

---

## What's More Than Needed (Consider Restructuring)

The severity table in Step 4 uses a run-together format (SeverityMeaning, CRITICALProduction outage...) that has lost its table formatting and reads as unstructured text. This is not a spec violation but degrades readability. Converting it to a proper markdown table would improve clarity.

**Suggested fix:**

    | Severity | Meaning |
    |---|---|
    | CRITICAL | Production outage, data loss, security breach, or payment/financial failure |
    | HIGH | Major operational risk, deployment instability, or auth/security issue |
    | MEDIUM | Reliability, scalability, or maintainability concern |
    | LOW | Minor hygiene issue, non-blocking |

---

## What's Missing (Must Add)

### 1. license field

Without a license, this skill cannot be safely shared, published, or reused. Add a license: key at the top level of the frontmatter.

### 2. compatibility field

The skill runs git diff --stat and git status — it requires a git environment. Document this in compatibility so agents and users know the prerequisites before activation.

### 3. Concrete input examples in the body

The output section has a good example report template, but the body lacks concrete invocation examples. Adding 2-3 short examples would help agents and users understand the expected interaction pattern.

**Suggested addition (in body):**

    ## Example invocations

    - "I'm about to deploy the auth refactor branch — can you check it?"
    - "Here's my diff — anything that could break in production?"
    - "We're shipping the payments integration Friday. What's the blast radius?"

---

## Summary Table

| Area | Status | Detail |
|---|---|---|
| name field | Pass | Valid format, matches folder name exactly |
| description field | Pass | 342 chars, strong trigger keywords, explains what and when |
| license field | Missing | Not present in frontmatter |
| compatibility field | Missing | Not present; git CLI dependency undocumented |
| metadata structure | Wrong | 8 non-standard fields at top level; must be nested under metadata: |
| Token budget | Pass | ~1920 tokens — well under 5000-token limit |
| Line budget | Pass | 178 body lines — well under 500-line limit |
| Body structure | Excellent | 5 numbered steps, clear output template, edge cases covered, negative triggers included |
| Self-containment / portability | Warn | Mostly self-contained but git dependency is undocumented; no external script references |
