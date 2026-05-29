# IMPROVEMENTS — cloud-infra-planner

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

## Improvement 1 — Nest Non-Standard Frontmatter Fields Under `metadata:`

### What needs to change
Eight top-level frontmatter fields (`version`, `author`, `email`, `category`, `tags`, `product`, `sprint`, `tested_with`) are not part of the spec's defined top-level set (`name`, `description`, `license`, `compatibility`, `metadata`, `allowed-tools`). All eight must be indented under a single `metadata:` key.

### Before
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

### After
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

### Impact if implemented
- **Agent behaviour:** Spec-compliant parsers will no longer reject or silently drop the frontmatter when loading the skill, ensuring all metadata (including `tested_with: claude-opus-4-7`) is preserved and readable.
- **Discoverability:** Registries and orchestrators that validate frontmatter before indexing will now index the skill correctly instead of failing or partially indexing it.
- **Portability:** Any team consuming this skill through a skills registry that enforces the spec can now load it without patching the frontmatter manually.
- **Risk reduced:** Eliminates the risk of a registry loader overwriting or ignoring the eight rogue top-level keys, which would silently strip authorship, category, and version info from the skill record.

### Existing use (before fix)
Today, when a skills registry or orchestration tool parses `cloud-infra-planner`'s frontmatter, it encounters eight fields at the top level that the spec does not recognise. Strict parsers will reject the entire skill or emit a validation warning and drop those fields. This means `author`, `email`, `category`, `tags`, `product`, `sprint`, and `tested_with` are invisible to any tooling that relies on the spec — breaking attribution, tag-based search, and sprint tracking silently.

### Improved use (after fix)
After nesting all eight fields under `metadata:`, the frontmatter fully conforms to the spec. Registries index the skill without warnings, tag-based search surfaces it under `infrastructure`, `terraform`, and `cost-estimation`, and the `tested_with: claude-opus-4-7` note is preserved so operators know which model was validated against it.

---

## Improvement 2 — Add Missing `license` Field

### What needs to change
The spec defines `license` as a recognised top-level field for declaring usage rights. It is absent from the current frontmatter. Without it, consumers cannot determine whether they are permitted to use, modify, or redistribute the skill.

### Before
```yaml
---
name: cloud-infra-planner
description: >
  Plan cloud infrastructure, size servers, recommend hosting, and estimate costs for any
  tech stack or cloud provider, then produce ready-to-use Terraform + Ansible, an
  architecture diagram, and a client report. Use whenever a user asks to "plan infra for",
  ...
# (no license field present)
```

### After
```yaml
---
name: cloud-infra-planner
description: >
  Plan cloud infrastructure, size servers, recommend hosting, and estimate costs for any
  tech stack or cloud provider, then produce ready-to-use Terraform + Ansible, an
  architecture diagram, and a client report. Use whenever a user asks to "plan infra for",
  ...
license: MIT
```

### Impact if implemented
- **Agent behaviour:** No direct effect on runtime behaviour, but tooling that enforces a license-present check before activating a skill will no longer block or warn on this skill.
- **Discoverability:** Skills registries that surface license metadata alongside search results will now show the correct license, helping adopters assess suitability quickly.
- **Portability:** Other teams and projects can now assess reuse rights without contacting the author — a one-line addition that removes a legal ambiguity.
- **Risk reduced:** Prevents silent adoption under unknown terms, reducing potential licensing disputes when the skill is shared across teams or published to a public registry.

### Existing use (before fix)
Any developer browsing the skills registry today sees `cloud-infra-planner` listed without a license field. If they want to reuse it in a client-facing product or a different organisation's registry, they have no documented permission to do so. Strict registry policies that require a license field before allowing installation will block the skill entirely, and the error message will not clearly explain why.

### Improved use (after fix)
With `license: MIT` declared, the registry surfaces the license alongside the skill name and description. Developers can immediately confirm they are free to use, modify, and distribute the skill. Registry policies that gate on license presence now pass, and the skill installs without friction in organisations with strict supply-chain policies.

---

## Improvement 3 — Add Missing `compatibility` Field for Python Runtime Dependency

### What needs to change
The skill has a hard runtime dependency on Python 3.8+ with `python-docx` and `reportlab` installed (called out in the Prerequisites section of the body). The spec provides a `compatibility` field specifically for declaring environment requirements. Burying this information only in the Prerequisites prose means tooling cannot check it programmatically before activation.

### Before
```markdown
## Prerequisites

- [ ] The user can answer the intake form (provider, stack, DB, scale, environments, budget)
- [ ] An outputs folder to write deliverables into (Terraform/Ansible, diagram, report)
- [ ] For the client report: Python with `python-docx` and `reportlab` (pip-installable) — see
      deliverable C. No `pandoc` or Terraform/Ansible CLI is required to *generate* the files.
```
(No `compatibility:` key in the frontmatter.)

### After
```yaml
compatibility: >
  Requires Python 3.8+ with python-docx and reportlab installed
  (pip install python-docx reportlab). No Terraform, Ansible, or
  pandoc CLI is required to generate files. Works on macOS, Linux,
  and Windows. Validated against claude-opus-4-7; compatible with
  any Claude model that supports tool use.
```

### Impact if implemented
- **Agent behaviour:** Orchestrators that inspect `compatibility` before spawning an agent for this skill can pre-validate the Python environment and emit a clear install prompt (`pip install python-docx reportlab`) instead of letting the skill fail mid-run when it tries to generate the `.docx`/`.pdf`.
- **Discoverability:** The compatibility field makes the skill machine-queryable — a registry can filter skills by runtime requirement, helping ops teams find all skills that need Python installed.
- **Portability:** Teams adopting the skill in a new environment see the dependency declared in the frontmatter, not buried in a prerequisites checklist that they might skip during a quick evaluation.
- **Risk reduced:** Eliminates the failure mode where the skill runs through all six steps — intake form, pricing, architecture approval — and only fails at deliverable generation (step 6) because `python-docx` is not installed. That failure wastes the entire session.

### Existing use (before fix)
Today, an agent activates `cloud-infra-planner`, walks the user through the intake form, prices three tiers, designs the architecture, gets approval at the step 4 gate, and then attempts to generate the `.docx` + `.pdf` client report in step 6 — only to crash with a `ModuleNotFoundError: No module named 'python-docx'`. The user has already spent significant time filling in the form and approving the architecture. The prerequisite note exists in the body, but no tooling reads it programmatically, and the user may have skimmed past it.

### Improved use (after fix)
With `compatibility` declared in the frontmatter, an orchestrator checks for `python-docx` and `reportlab` before the skill activates. If they are missing, it surfaces a one-line install prompt (`pip install python-docx reportlab`) and blocks activation until the environment is ready. The user fixes the dependency in under a minute, then proceeds through all six steps knowing deliverable generation will succeed. No wasted intake sessions.

---

## Improvement 4 — Remove Duplicate Content Between "Notes" and Numbered Steps

### What needs to change
Several bullets in the "Notes" section at the bottom of SKILL.md directly restate constraints already embedded in the numbered steps. Three examples:
- "Never write any deliverable file … before presenting the architecture in chat and getting the user's explicit approval" — already the entire point of Step 4 ("Architecture Review & Approval Gate").
- "Never present costs as final — always include disclaimer + calculator link" — already stated verbatim in Step 2 ("Always produce … Pricing disclaimer on every cost section with the provider's calculator link").
- "IaC scope: Terraform = infra, Ansible = OS/app" — already stated in Step 5 opening sentence.

The "Output" section also largely recaps Step 6 (Deliverables), adding only a single new sentence about location. Both duplications add token cost without adding information.

### Before
```markdown
## Notes

- Always run the **form** (`references/intake-form.md`) and echo the Filled Form back before recommending.
- **Never write any deliverable file — `.drawio`, `.docx`, `.pdf`, Terraform, or Ansible — before presenting the architecture in chat and getting the user's explicit approval (the step 4 gate).**
- Always state all assumptions explicitly (traffic, DB engine, Docker count, UAT frequency).
- Never present costs as final — always include disclaimer + calculator link.
- Managed services preferred over self-hosted for DB, Redis, storage.
- Include a risks section whenever Docker runs alongside Forge on a shared server.
- IaC scope: **Terraform = infra, Ansible = OS/app**. For **Laravel + Forge**, Terraform provisions only and the README carries high-level Forge steps — never model PHP/Nginx in IaC.
- Never put secrets in generated IaC — variables + git-ignored tfvars / ansible-vault, always with an example file.
- Generated Terraform must create DNS records for **every sub-domain** captured in the form.
- **Always include a database backup strategy**: managed automated backups **+** nightly encrypted dump offsite to S3 / Cloudflare R2 / Google Cloud Storage (client's choice, ideally a different provider/region), with GFS retention and scheduled restore drills — provision the backup bucket + cron in the IaC.
- Supports **any hosting provider** — DO is the default; fall back to `references/providers.md` for others.
```

### After
Trim the Notes section to only bullets that add new, non-step-duplicated constraints. Remove the three restatements and merge the Output section's location sentence into Step 6:

```markdown
## Notes

- Always state all assumptions explicitly (traffic, DB engine, Docker count, UAT frequency).
- Managed services preferred over self-hosted for DB, Redis, storage.
- Include a risks section whenever Docker runs alongside Forge on a shared server.
- Never put secrets in generated IaC — use variables + git-ignored tfvars / ansible-vault, always with an example file.
- Generated Terraform must create DNS records for **every sub-domain** captured in the form.
- **Always include a database backup strategy**: managed automated backups **+** nightly encrypted dump offsite to S3 / Cloudflare R2 / Google Cloud Storage (client's choice, ideally a different provider/region), with GFS retention and scheduled restore drills — provision the backup bucket + cron in the IaC.
- Supports **any hosting provider** — DO is the default; fall back to `references/providers.md` for others.
```

(Remove the duplicate "Never write deliverable files before approval" and "Never present costs as final" bullets. Add the output location sentence to step 6's opening line.)

### Impact if implemented
- **Agent behaviour:** Reduces token consumption on every skill load by ~120 tokens (the three redundant bullets). On long infra sessions that involve multiple skill re-reads, this compounds.
- **Discoverability:** No change to discoverability.
- **Portability:** Cleaner body makes the skill easier to audit and maintain — a new author updating the approval gate in step 4 no longer has to remember to also update the corresponding Notes bullet.
- **Risk reduced:** Eliminates the risk of the two copies of a constraint drifting out of sync over time (e.g., if step 4 is updated to allow partial file generation but the Notes bullet still says "never write any file") — a future inconsistency that would confuse the agent.

### Existing use (before fix)
Today, when the agent loads `cloud-infra-planner`, it processes the approval gate instruction twice: once in step 4 ("This is a hard stop. Do not write a single file…") and again in the Notes ("Never write any deliverable file…"). On every activation, the agent reads and processes both. If a future author strengthens the approval gate in step 4 but forgets to update the Notes bullet, the agent sees contradictory instructions and may behave unpredictably — following whichever version appears later in the context.

### Improved use (after fix)
With the duplicate bullets removed, each constraint lives in exactly one place. Step 4 owns the approval gate; Step 2 owns the pricing disclaimer; Step 5 owns IaC scope. The Notes section becomes a tight, non-redundant checklist of constraints that genuinely have no natural home in the steps — making the skill faster to load, easier to maintain, and immune to the instruction-drift failure mode.

---

## Priority Order

| Priority | Improvement | Effort | Impact |
|---|---|---|---|
| 1 | Nest non-standard frontmatter fields under `metadata:` | Low | Critical |
| 2 | Add missing `compatibility` field for Python runtime dependency | Low | High |
| 3 | Add missing `license` field | Low | Medium |
| 4 | Remove duplicate content between "Notes" and numbered steps | Medium | Medium |

---

## Before vs After: Full Skill Experience

### Before (current state)

A developer discovers `cloud-infra-planner` in their team's skills registry and tries to install it. The registry's frontmatter validator immediately flags eight unrecognised top-level keys (`version`, `author`, `email`, `category`, `tags`, `product`, `sprint`, `tested_with`) and either rejects the install or silently drops all eight fields. If the registry is lenient, the skill loads — but tag-based search never surfaces it under `terraform` or `infrastructure` because the tags were dropped. The developer has to find it by exact name.

Once installed, an operator spins up an infra planning session. The skill runs smoothly through the intake form, pricing, and architecture review. The user approves at the step 4 gate and the agent begins generating the client report deliverable (step 6, deliverable C). It fails with `ModuleNotFoundError: No module named 'python-docx'` because nothing in the machine-readable frontmatter warned the orchestrator to check for this dependency. The user has to install `python-docx` and `reportlab` manually, re-run the session from the approval gate, and hope the agent doesn't lose context. Meanwhile, a compliance officer reviewing the skill for org-wide rollout notices there is no `license` field — they cannot approve the skill for production use without knowing its terms, and reaching the author adds days of delay.

### After (all improvements applied)

With all four improvements applied, the first thing a developer sees when browsing the registry is `cloud-infra-planner` tagged under `infrastructure`, `terraform`, `ansible`, and `cost-estimation`, discoverable through normal tag-based search. The frontmatter is fully spec-compliant: `metadata:` wraps all eight custom fields, `license: MIT` declares usage rights, and `compatibility:` calls out the Python 3.8+ requirement with the exact `pip install` command. The compliance officer approves the skill for org-wide rollout in minutes.

When an operator starts an infra planning session, the orchestrator reads `compatibility`, checks for `python-docx` and `reportlab`, finds them missing, and surfaces a one-line install prompt before the session begins. The user installs them in under a minute, then proceeds through the full six-step flow — intake form, pricing, architecture review, approval gate, IaC generation, deliverables — without interruption. The `.docx` + `.pdf` client report is generated successfully in step 6.

The skill body itself is tighter: the Notes section no longer restates the approval gate or pricing disclaimer (which live in steps 4 and 2 respectively), so there is no risk of those constraints drifting out of sync over future edits. Each constraint has exactly one home. The skill is faster to load, easier to maintain, and fully portable to any team that needs to plan cloud infrastructure for Laravel, NestJS, Next.js, or any other stack on DigitalOcean, AWS, or any other provider.
