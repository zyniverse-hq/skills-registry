# IMPROVEMENTS — deploy-shield

> Improvement plan derived from SKILL.md + ANALYSIS.md audit against the agentskills.openml.io spec.

---

## Quick Summary

| | Before | After |
|---|---|---|
| Spec compliance | Partially compliant | Fully compliant |
| Critical violations | 3 | 0 |
| Agent discoverability | High | High |
| Portability | Partial | Pass |

---

## Improvement 1 — Move non-standard frontmatter fields under `metadata:`

### What needs to change

Eight non-standard fields (Version, Author, Email, Category, Tags, Product, Sprint, Tested_with) are declared at the top level of the frontmatter. The agentskills.openml.io spec only permits name, description, license, compatibility, metadata, and allowed-tools at the top level. All other fields must be nested under metadata:.

### Before
```yaml
---
name: deploy-shield
description: Audits a codebase branch or diff for production risks, deployment safety, and engineering hygiene before a release. Use when a developer wants to know if code is safe to deploy, assess blast radius, check rollback safety, audit dependencies, or get a pre-release risk report — even if they don't use the word "deployment".
Version: 1.0.0
Author: Akash R
Email: akash.r@zysk.tech
Category: deployment-safety
Tags: deployment, code-review, production-safety, risk-audit
Product: zysk
Sprint: 1
Tested_with: claude-sonnet-4-6
---
```

### After
```yaml
---
name: deploy-shield
description: Audits a codebase branch or diff for production risks, deployment safety, and engineering hygiene before a release. Use when a developer wants to know if code is safe to deploy, assess blast radius, check rollback safety, audit dependencies, or get a pre-release risk report — even if they don't use the word "deployment".
license: MIT
compatibility: Requires git CLI available in PATH. Target directory must be a git repository. No other runtime dependencies — language and framework are auto-detected from the diff.
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
```

### Impact if implemented
- **Agent behaviour:** Agents that parse frontmatter strictly will correctly read Version, Author, and all metadata fields instead of silently ignoring or misinterpreting top-level unknown keys.
- **Discoverability:** No change to discoverability — the description field already carries strong trigger keywords. Metadata fields like tags and category become correctly scoped and parseable by the registry.
- **Portability:** Any team cloning this skill into a different registry will have their frontmatter parser accept the file without errors or warnings.
- **Risk reduced:** Prevents frontmatter parse failures and silent data loss of version/author/contact fields when this skill is published to agentskills.openml.io.

### Existing use (before fix)
Today, when the skill is loaded by a registry-aware agent or a CI validation step, the parser encounters Version, Author, Email, and five other fields at the top level of the YAML frontmatter. These are not in the allowed set of top-level keys. Depending on the parser, this either throws a validation error (blocking the skill from being indexed) or silently discards those fields entirely — meaning the version number, author contact, and category tags are lost without any warning. The skill technically still runs because agents read the body, but registry features that depend on metadata (filtering by category: deployment-safety, attributing to akash.r@zysk.tech, or showing version 1.0.0 in the UI) all break silently.

### Improved use (after fix)
After restructuring, every frontmatter field lands in its correct slot. A registry parser validates the file cleanly, indexes the skill under the deployment-safety category, and surfaces version 1.0.0 and the author's contact. The metadata block is a single, clearly scoped section that any team member can extend without risking top-level key collisions. The skill publishes to agentskills.openml.io without errors.

---

## Improvement 2 — Add missing `license` field

### What needs to change

The license field is entirely absent from the frontmatter. Without it, the skill cannot be safely shared, reused, or published. The spec requires this field at the top level of the frontmatter.

### Before
```yaml
---
name: deploy-shield
description: Audits a codebase branch or diff for production risks...
Version: 1.0.0
Author: Akash R
# no license field present
---
```

### After
```yaml
---
name: deploy-shield
description: Audits a codebase branch or diff for production risks...
license: MIT
compatibility: Requires git CLI available in PATH. Target directory must be a git repository. No other runtime dependencies — language and framework are auto-detected from the diff.
metadata:
  version: 1.0.0
  author: Akash R
  ...
---
```

### Impact if implemented
- **Agent behaviour:** No direct change to runtime agent behaviour, but registry tooling that checks for license before allowing publish/install will stop blocking this skill.
- **Discoverability:** Skills without a license field are excluded from the public index on agentskills.openml.io — adding it makes the skill publicly discoverable.
- **Portability:** Other teams and projects can now safely copy, fork, and use this skill knowing they are operating under MIT terms.
- **Risk reduced:** Prevents legal ambiguity about whether consumers are permitted to run, modify, or redistribute this skill.

### Existing use (before fix)
Any developer who finds deploy-shield in the registry today and wants to integrate it into their own team's workflow has no legal clarity. The agentskills.openml.io publish pipeline rejects the skill outright at the validation step because license is a required field — meaning deploy-shield never reaches the public index and can only be used by cloning the repo directly. Teams that do use it via direct clone are technically in an unlicensed grey zone.

### Improved use (after fix)
With license: MIT present, the skill passes frontmatter validation and is published to the public index. Any agent or developer can install it with confidence that MIT terms govern reuse. The registry displays the license badge alongside the skill, and automated dependency scanners in downstream projects correctly classify it as a permissively licensed component.

---

## Improvement 3 — Add missing `compatibility` field documenting git CLI dependency

### What needs to change

Step 1 of the skill body instructs the agent to "Run git diff --stat and git status first." This means the skill has a hard runtime dependency on the git CLI being available in PATH and the working directory being a git repository. Neither dependency is documented anywhere in the frontmatter. The spec requires that external tool and environment dependencies be declared in the compatibility field (max 500 chars).

### Before
```yaml
---
name: deploy-shield
description: ...
Version: 1.0.0
# no compatibility field
---
```

```markdown
## Step 1: Understand the stack
Run git diff --stat and git status first. Read changed files with context. Do not analyze blind.
```

### After
```yaml
---
name: deploy-shield
description: ...
license: MIT
compatibility: Requires git CLI available in PATH. Target directory must be a git repository. No other runtime dependencies — language and framework are auto-detected from the diff.
---
```

### Impact if implemented
- **Agent behaviour:** Agents that check compatibility before activating a skill will correctly pre-validate that git is available before attempting Step 1 — instead of running blind and hitting a git: command not found error mid-analysis.
- **Discoverability:** Registry users filtering by environment compatibility (e.g., "works in my Docker container") can see at a glance whether this skill fits their setup.
- **Portability:** Teams running deploy-shield in CI pipelines or containerised environments know exactly what to install before the skill can run.
- **Risk reduced:** Prevents confusing mid-execution failures where the agent starts Step 1, runs git diff, gets an error, and either halts with a cryptic message or continues with no diff data and produces a meaningless report.

### Existing use (before fix)
Today, a developer in a CI environment or a sandboxed agent container activates deploy-shield and the agent reaches Step 1: "Run git diff --stat". If git is not installed, the command fails silently or throws an error. The agent has no prior warning to check for git availability. In the worst case, the agent skips git and proceeds with no diff data, producing an empty or fabricated DeployShield report — giving the developer false confidence about their deployment safety. There is no way for a registry consumer to know this dependency exists without reading the full body.

### Improved use (after fix)
With compatibility: Requires git CLI available in PATH. Target directory must be a git repository declared in the frontmatter, the agent can check prerequisites before activating. A registry-aware agent surfaces a clear error: "deploy-shield requires git CLI. Please ensure git is installed." CI setups can add a git install step to their pipeline based on this documented requirement. The skill never runs without the tool it depends on, and the DeployShield report is always grounded in real diff data.

---

## Improvement 4 — Fix broken severity table formatting in Step 4

### What needs to change

The severity classification table in Step 4 has lost its markdown table formatting and renders as run-together unstructured text. The current content reads as "SeverityMeaning 🔴CRITICALProduction outage..." which is unreadable. This needs to be converted to a proper markdown table.

### Before
```markdown
## Step 4: Classify every finding by severity

- SeverityMeaning 
🔴CRITICALProduction outage, data loss, security breach, or payment/financial failure

🟠HIGHMajor operational risk, deployment instability, or auth/security issue

🟡MEDIUMReliability, scalability, or maintainability concern

🟢LOWMinor hygiene issue, non-blocking
```

### After
```markdown
## Step 4: Classify every finding by severity

| Severity | Meaning |
|---|---|
| 🔴 CRITICAL | Production outage, data loss, security breach, or payment/financial failure |
| 🟠 HIGH | Major operational risk, deployment instability, or auth/security issue |
| 🟡 MEDIUM | Reliability, scalability, or maintainability concern |
| 🟢 LOW | Minor hygiene issue, non-blocking |
```

### Impact if implemented
- **Agent behaviour:** The agent reading Step 4 now parses a clean, structured table and correctly maps each finding to its severity tier. With the broken formatting, an agent may misread CRITICAL and HIGH as a single concatenated string and produce incorrectly classified findings.
- **Discoverability:** No direct effect on discoverability.
- **Portability:** Any renderer (GitHub, VSCode, agentskills.io) now displays the severity guide correctly instead of showing raw unformatted text.
- **Risk reduced:** Prevents the agent from miscategorising a CRITICAL finding as MEDIUM or producing a DeployShield report where severity labels are garbled — which would give developers a false read on deployment safety.

### Existing use (before fix)
When an agent reads Step 4 today, it encounters "SeverityMeaning 🔴CRITICALProduction outage..." as a single unparseable block. A developer reviewing the raw SKILL.md also sees an unreadable wall of text where the severity guide should be. Any agent that parses this step literally may associate the wrong meanings with the wrong severity levels — for example tagging a missing database timeout as LOW instead of 🔴 CRITICAL, which is precisely the kind of misclassification that causes production incidents.

### Improved use (after fix)
With a properly formatted markdown table, both human reviewers and agents read the severity classifications cleanly. The agent executing Step 4 produces a report where every finding is correctly tagged 🔴/🟠/🟡/🟢 with the right risk framing. Developers can skim the DeployShield report header and immediately understand the severity distribution without ambiguity.

---

## Improvement 5 — Add concrete input examples to the body

### What needs to change

The body has a detailed output example (the report template) but no concrete input examples showing how a developer or agent should invoke deploy-shield. Adding 2-3 short trigger-phrase examples anchors agent understanding of the expected interaction pattern and improves activation accuracy.

### Before
```markdown
## When to use

- Activate when: the user asks "is this ready to deploy?", "check for issues before I push", "what could go wrong?", "safe to merge?", "pre-release audit", "what's the blast radius?", "what breaks if I deploy this?"
- Activate when: the user asks for a code review with emphasis on runtime safety, reliability, or operational impact — even without the word "deployment"
- Activate when: the user mentions deployment risk, production readiness, rollback safety, or dependency health in the context of shipping code
Do NOT activate when: the user wants a general style review, formatting feedback, or architecture discussion with no imminent release

# (no Example invocations section exists anywhere in the body)
```

### After
```markdown
## When to use

- Activate when: the user asks "is this ready to deploy?", "check for issues before I push", "what could go wrong?", "safe to merge?", "pre-release audit", "what's the blast radius?", "what breaks if I deploy this?"
- Activate when: the user asks for a code review with emphasis on runtime safety, reliability, or operational impact — even without the word "deployment"
- Activate when: the user mentions deployment risk, production readiness, rollback safety, or dependency health in the context of shipping code
- Do NOT activate when: the user wants a general style review, formatting feedback, or architecture discussion with no imminent release

## Example invocations

- "I'm about to deploy the auth refactor branch — can you check it?"
- "Here's my diff — anything that could break in production?"
- "We're shipping the payments integration Friday. What's the blast radius?"
- "Is the migration safe to run on prod tonight?"
```

### Impact if implemented
- **Agent behaviour:** Agents use few-shot examples to calibrate activation thresholds. Three concrete invocation examples help agents recognise real-world phrasings that do not use the exact trigger keywords in the description (e.g., "migration safe to run" is not in the description but is clearly in scope).
- **Discoverability:** Registry users browsing skills see example invocations and immediately understand what type of input to give — reducing friction and increasing correct usage.
- **Portability:** Teams onboarding to a new project can copy an example invocation directly and know it will activate the skill correctly.
- **Risk reduced:** Prevents under-activation (developer phrases their request in a way not matching trigger keywords, so the skill is skipped) and over-activation (agent triggers deploy-shield on a formatting review because the boundary was unclear).

### Existing use (before fix)
Today, a developer asking "is the migration safe to run on prod tonight?" may not activate deploy-shield because "migration safe" is not among the listed trigger phrases and the agent cannot match it to the activation criteria with high confidence. Conversely, a developer asking "review this code" in the context of a DB schema discussion might accidentally activate it when they wanted a style review. Without concrete examples, the boundary between activate and do not activate is fuzzy and agent-dependent.

### Improved use (after fix)
With four concrete example invocations added, agents have calibration anchors. "Migration safe to run" maps to the fourth example and activates the skill confidently. "Review my code for style" does not match any example and falls under the Do NOT activate when rule. Developers onboarding to deploy-shield can copy an example invocation directly, reducing time-to-first-use from minutes to seconds.

---

## Priority Order

| Priority | Improvement | Effort | Impact |
|---|---|---|---|
| 1 | Move non-standard frontmatter fields under `metadata:` | Low | Critical |
| 2 | Add missing `license` field | Low | Critical |
| 3 | Add missing `compatibility` field documenting git CLI dependency | Low | High |
| 4 | Fix broken severity table formatting in Step 4 | Low | High |
| 5 | Add concrete input examples to the body | Low | Medium |

---

## Before vs After: Full Skill Experience

### Before (current state)

A developer at a team that uses the agentskills.openml.io registry searches for "deploy" or "production safety" and does not find deploy-shield in the public index — because the missing license field causes the publish pipeline to reject the skill outright. They only discover it by browsing the GitHub repo directly. When they clone it and try to register it in their internal registry, their frontmatter parser throws warnings or errors on Version, Author, Email, Category, Tags, Product, Sprint, and Tested_with at the top level. Depending on strictness, the skill either fails to register or registers with all eight metadata fields silently discarded — meaning the category, version, and author contact are lost.

When the skill does activate, an agent running Step 1 in a fresh CI container hits git: command not found with no prior warning because the compatibility field does not exist. There is nothing in the frontmatter to tell the CI setup that git must be installed. The agent may fall back to analysing files without a diff, producing a DeployShield report with fabricated or empty findings. If the agent does have git available and produces a real report, the Step 4 severity guide renders as garbled unformatted text — "SeverityMeaning 🔴CRITICALProduction outage" — making it hard to trust that the CRITICAL / HIGH / MEDIUM / LOW labels in the report mean what they should. The developer gets a report they cannot fully trust, built on a skill they are not certain they are permitted to reuse.

A different developer, unfamiliar with deploy-shield, wants to check whether a database migration is safe to run tonight. They phrase their question as "is the migration safe to run on prod?" — a natural phrasing that does not match any of the listed trigger keywords. The agent skips deploy-shield entirely and does a generic code review instead, missing the migration sequencing checks, rollback viability analysis, and NOT NULL column detection that deploy-shield would have caught. The deployment proceeds with unreviewed migration risk.

### After (all improvements applied)

With all five improvements applied, deploy-shield passes frontmatter validation on the first attempt. The license: MIT field unlocks it for public indexing on agentskills.openml.io — developers searching for "deployment safety" or browsing the deployment-safety category find it immediately. The metadata: block correctly scopes version 1.0.0, author contact, and tags, so the registry displays a complete skill card with no missing fields.

Before an agent activates deploy-shield in a new environment, the compatibility field tells it — and the CI pipeline — that git CLI must be available in PATH and the directory must be a git repository. A container setup adds a git install step before running the skill. The agent never starts Step 1 without the tools it needs. When it does run, it reads a real git diff, identifies the actual stack, and produces a DeployShield report grounded in the real codebase changes.

The developer asking "is the migration safe to run on prod tonight?" now gets a match against the concrete invocation example "Is the migration safe to run on prod tonight?" added in Improvement 5 — deploy-shield activates, runs its five-dimension analysis, and surfaces the migration sequencing check, NOT NULL column risk, and rollback viability score. The severity table in Step 4 renders as a clean markdown table, so the agent correctly tags migration risks as 🔴 CRITICAL or 🟠 HIGH rather than producing garbled severity labels. The developer receives a structured, trustworthy DeployShield report before a single line reaches production.
