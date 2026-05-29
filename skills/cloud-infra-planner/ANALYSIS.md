# ANALYSIS — cloud-infra-planner

> Generated against the [agentskills.io](https://agentskills.openml.io) standard.

---

## Overall Verdict

**Partially compliant.** The skill has an excellent body — clear step-by-step instructions, a concrete example, well-defined outputs, and thorough notes covering edge cases. The description is outstanding for agent discovery. However, the frontmatter contains eight non-standard top-level fields (`version`, `author`, `email`, `category`, `tags`, `product`, `sprint`, `tested_with`) that must be nested under a `metadata:` key per spec, and the required `license` and `compatibility` fields are absent.

---

## Spec Compliance Checklist

| Check | Status | Detail |
|---|---|---|
| `name` field format | PASS | `cloud-infra-planner` — lowercase, hyphens only, no leading/trailing hyphens, 19 chars, matches folder name exactly |
| `description` present & non-empty | PASS | Present and 590 chars (within 1–1024 limit) |
| `description` describes what it does | PASS | Clearly states: plan infra, size servers, recommend hosting, estimate costs, produce Terraform + Ansible + diagram + client report |
| `description` describes when to use it | PASS | Excellent trigger keywords: "plan infra for", "what servers do we need", "estimate cloud costs", "terraform for", "provision servers", "DigitalOcean / AWS sizing", "infra for Laravel / Next.js / Node / NestJS" |
| `license` field | FAIL | Missing — not present in frontmatter |
| `compatibility` field | FAIL | Missing — not present in frontmatter |
| `metadata` field structure | FAIL | Eight non-standard fields (`version`, `author`, `email`, `category`, `tags`, `product`, `sprint`, `tested_with`) are at top level instead of nested under `metadata:` |
| `allowed-tools` field | — | Not present (optional) |
| Token budget (body) | PASS | ~2,725 tokens estimated (well under 5,000 limit) |
| Line budget (body) | PASS | 173 lines (well under 500 limit) |
| `scripts/` directory | — | Not present; not required for this skill type |
| `references/` directory | PASS | Present with 8 reference files (intake-form.md, digitalocean.md, aws.md, providers.md, architecture.md, terraform.md, ansible.md, drawio.md) |
| `assets/` directory | — | Not present; not required for this skill type |
| Body — step-by-step instructions | PASS | Six numbered steps with clear headings, substeps, and rules |
| Body — examples | PASS | Concrete end-to-end example with user input and expected Claude behaviour |
| Body — edge cases | PASS | Covers negative triggers, Laravel/Forge vs Docker distinction, UAT on-demand billing, secrets handling, approval gate |

---

## What the Skill Gets Right

- **Description is a model of best practice** — packs specific trigger phrases ("plan infra for", "estimate cloud costs", "terraform for", etc.) into the 590-char description, maximising agent discovery without hitting the 1,024-char ceiling.
- **Step-by-step instructions are explicit and ordered** — the six-step flow (intake form → pricing → architecture → approval gate → IaC → deliverables) leaves no ambiguity about sequencing.
- **Hard approval gate (step 4)** — explicitly blocking all file generation until user approval is a strong UX safety measure and is clearly documented.
- **Negative trigger guidance** — "Do NOT activate when" section prevents false activations on CI/CD or SaaS-licensing questions.
- **Reference table is well-structured** — maps each reference file to the exact scenario that warrants reading it, supporting progressive disclosure.
- **Output section is concrete** — specifies file formats, naming patterns, and delivery locations rather than vague "produce a report".
- **Notes section is actionable** — covers secrets handling, DNS sub-domain requirement, backup strategy, Forge IaC boundary, and managed-services preference.
- **Token and line budgets are well within limits** — 173 lines and ~2,725 tokens leave ample headroom.
- **Body uses relative file paths** throughout (`references/intake-form.md`, etc.) — fully portable.

---

## Violations (Must Fix)

### 1. Non-standard frontmatter fields must be nested under `metadata:`

Eight fields are at the top level of the frontmatter but are not part of the spec's defined set (`name`, `description`, `license`, `compatibility`, `metadata`, `allowed-tools`):

**Current:**
```yaml
version: 1.0.0
author: Nagendra K V
email: nagendra.kv@zysk.tech
category: infra-security
tags:
  - infrastructure
  - terraform
  - ansible
  - cost-estimation
  - deployment
product: zysk
sprint: 1
tested_with: claude-opus-4-7
```

**Fix — nest all of these under `metadata:`:**
```yaml
metadata:
  version: 1.0.0
  author: Nagendra K V
  email: nagendra.kv@zysk.tech
  category: infra-security
  tags:
    - infrastructure
    - terraform
    - ansible
    - cost-estimation
    - deployment
  product: zysk
  sprint: 1
  tested_with: claude-opus-4-7
```

### 2. `license` field is missing

The spec lists `license` as an optional but defined field for specifying licensing terms. Its absence means consumers cannot determine usage rights.

**Fix — add after `description:`:**
```yaml
license: MIT
```
(Or whichever licence applies — MIT, proprietary, Apache-2.0, etc.)

### 3. `compatibility` field is missing

The skill has a real Python dependency (`python-docx`, `reportlab`) called out in the Prerequisites section. That prerequisite belongs in `compatibility` so tooling and agents can check it before activation.

**Fix — add after `license:`:**
```yaml
compatibility: >
  Requires Python 3.8+ with python-docx and reportlab installed
  (pip install python-docx reportlab). No Terraform, Ansible, or
  pandoc CLI required. Works on any OS. Claude model: any.
```

---

## What's More Than Needed (Consider Restructuring)

- **"Notes" section partially duplicates earlier steps.** Several notes (e.g., never write files before approval, always include a pricing disclaimer, never put secrets in IaC) already appear in the numbered steps. The Notes section is still useful as a quick-reference checklist, but authors should audit each bullet to ensure it adds information rather than restating a step.
- **"Output" section after "Steps"** largely recaps what is already in step 6 (Deliverables). Consider merging Output into step 6 or trimming Output to just the location/format line and the example filename pattern.

---

## What's Missing (Must Add)

1. **`license` field** — add a top-level `license:` key with the applicable licence identifier.
2. **`compatibility` field** — document the Python runtime dependency so agents and operators know the environment requirement before activating the skill.
3. **`metadata:` wrapper** — all eight custom frontmatter fields need to be indented under a single `metadata:` key to comply with the spec's rule that non-standard fields must not appear at the top level.

---

## Summary Table

| Area | Status | Detail |
|---|---|---|
| `name` field | Pass | Valid format, correct length, matches folder name |
| `description` field | Pass | 590 chars, strong trigger keywords, clear what/when |
| `license` field | Missing | Not present in frontmatter |
| `compatibility` field | Missing | Not present; Python dependency should be declared here |
| `metadata` structure | Wrong | 8 non-standard fields at top level; must be nested under `metadata:` |
| Token budget | Pass | ~2,725 tokens (limit: 5,000) |
| Line budget | Pass | 173 lines (limit: 500) |
| Body structure | Excellent | 6 numbered steps, approval gate, concrete example, edge-case notes |
| Self-containment / portability | Pass | All paths are relative; references/ directory present and mapped |
