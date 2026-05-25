---
name: cloud-infra-planner
description: >
  Plan cloud infrastructure, size servers, recommend hosting, and estimate costs for any
  tech stack or cloud provider, then produce ready-to-use Terraform + Ansible, an
  architecture diagram, and a client report. Use whenever a user asks to "plan infra for",
  "what servers do we need", "estimate cloud costs", "plan deployment for", "DigitalOcean /
  AWS sizing", "infra for Laravel / Next.js / Node / NestJS", "terraform for", "provision
  servers", or any variation — even if they never say "infrastructure" or "cloud" but are
  asking how to host, provision, or run a project in production.
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
---

# Cloud Infra Planner

> Plan cloud infrastructure, estimate hosting costs, and produce ready-to-use Terraform +
> Ansible, an architecture diagram, and a client report for project deliveries.

Primary stacks: **Laravel PHP, Next.js, Node.js, NestJS** (Python rarely).
Default provider: **DigitalOcean**, but the skill supports **any hosting provider** the
client picks (AWS, GCP, Azure, Hetzner, Linode, Vultr, …). Laravel is always managed via
**Laravel Forge**.

## When to use

- Activate when: the user asks to plan infra, size servers, or pick hosting for a project
  ("plan infra for", "what servers / droplets / instances do we need", "production setup").
- Activate when: the user asks to estimate or budget hosting / cloud costs for a stack.
- Activate when: the user asks for deployment architecture, Terraform, Ansible, infra-as-code,
  or provisioning scripts for Laravel / Next.js / Node / NestJS / Python on any provider.
- Activate when: the user asks how to host, provision, or run a project in production — even
  if they never say the words "infrastructure" or "cloud".
- Do NOT activate when: the user wants application code, CI/CD pipeline authoring unrelated to
  provisioning, or a non-infra cost estimate (e.g. SaaS licensing) — those are different tasks.

## Prerequisites

- [ ] The user can answer the intake form (provider, stack, DB, scale, environments, budget)
- [ ] An outputs folder to write deliverables into (Terraform/Ansible, diagram, report)
- [ ] For the client report: Python with `python-docx` and `reportlab` (pip-installable) — see
      deliverable C. No `pandoc` or Terraform/Ansible CLI is required to *generate* the files.

> Before designing architecture, read the relevant reference files below.

## Reference Files

| File | Read when |
|---|---|
| `references/intake-form.md` | Gathering requirements — the structured form-style questionnaire (always read first) |
| `references/digitalocean.md` | Provider is DigitalOcean (default) |
| `references/aws.md` | Provider is AWS |
| `references/providers.md` | Provider is anything other than DO/AWS ("any hosting") |
| `references/architecture.md` | Designing stack layout, Docker strategy, environments, scaling, risks, or report structure |
| `references/terraform.md` | Generating Terraform to provision the infra |
| `references/ansible.md` | Generating Ansible to configure servers / deploy (non-Laravel-Forge stacks) |
| `references/drawio.md` | Generating architecture diagrams as `.drawio` files |

## Steps

### 1. Gather Project Info — run the form

**Read `references/intake-form.md` and walk the user through it like a form.** Present the
grouped sections (Provider → Backend → Frontend → Database → Cache/Queues → Storage →
Domains/Sub-domains → Scale → Environments → Budget/Deploy → **Backup & DR**). Where an
interactive question UI is available, ask section by section with multiple-choice options —
that is the form-filling experience the user wants.

Rules:
- Only the fields marked **(required)** truly block progress. For everything else, apply
  the section's default, mark it `(assumed)`, and keep moving.
- **Echo the completed "Filled Form" summary back** and get a confirm/correct before pricing.

### 2. Suggest Pricing

Immediately after the form is confirmed, read the relevant provider reference
(`digitalocean.md`, `aws.md`, or `providers.md` for any other host) and produce the cost
estimate. Pricing comes right after the form so the user sees the budget impact of their
choices before deeper design. Always produce:
- Per-service breakdown table for each environment (columns: Service, Product, Spec, Qty, $/mo)
- **Three tiers**: Low-cost / Recommended / High-Availability
- **Combined total** across all environments and projects
- **Forge Circles plan ($29/mo)** as a line item for multi-server Laravel/Forge setups
- **Pricing disclaimer** on every cost section with the provider's calculator link

### 3. Design Architecture

Read `references/architecture.md` for: stack configs, Docker + Forge coexistence rules, environment model (Prod/UAT/Dev/QA), UAT on-demand pattern, risks table, and scaling roadmap.

Key constraints to always apply:
- **Never containerise Laravel/PHP-FPM** — Forge owns that layer
- **MySQL is the default DB** for Laravel (not PostgreSQL)
- **Named Docker volumes only** — no bind mounts into `/home/forge`
- **UAT is hourly billed** — cost it as on-demand, not always-on

### 4. Architecture Review & Approval Gate (STOP — before writing ANY files)

**This is a hard stop. Do not write a single file — no `.drawio`, no `.docx`, no `.pdf`,
no Terraform/Ansible — until the user has explicitly approved the architecture.**

Present the **proposed architecture in chat** so the user can review and correct it before
anything is generated. Include:
- **Topology** — an ASCII/text diagram of the layout per environment (this previews what the
  `.drawio` will contain)
- **Components & rationale** — each service and why it's there
- **Environment model** — Prod / UAT (on-demand) / Dev-QA
- **Cost summary** — recap the three tiers + combined total from step 2
- **Backup & DR** and **key risks** — the short version

Then ask for an explicit go-ahead. Where an interactive question UI is available, ask:
**"Approve this architecture and generate the deliverables, or change something first?"**
with options like *Approve & generate* / *Change something* / *Adjust scope of outputs*.

Only after the user approves do you proceed to steps 5 and 6. If they request changes,
revise and re-present this preview — do not skip ahead to file generation.

### 5. Generate Deployment Scripts (Terraform + Ansible)

Turn the confirmed form into **ready-to-use Infrastructure as Code** for the chosen
provider, written to the outputs folder as a `terraform/` + `ansible/` project with a README.

- Read `references/terraform.md` — provision compute, managed DB, Redis, object storage,
  load balancer, firewall, and **DNS records for every sub-domain from the form**. Use the
  provider-mapping table to target whichever host was chosen ("any hosting").
- Read `references/ansible.md` — configure servers + deploy for **Node / NestJS / Python /
  Docker** stacks.
- **Laravel + Forge:** do NOT generate app-level Ansible. Terraform provisions infra only;
  emit the **high-level Forge steps** (connect server, create sites per sub-domain, paste
  DB/Redis creds, enable SSL, deploy script, Horizon, scheduler) in the README.
- Confirm the deploy method with the user (Forge vs Terraform+Ansible) before generating —
  it's set in form Section J.

### 6. Deliverables (only after the step 4 approval gate)

**Always produce all four:**

**A) Architecture diagram** — `.drawio` file. Read `references/drawio.md` before generating. Produce one diagram covering all environments (swimlane per environment) or one per environment if detail requires it. Present the file and tell the user to open it at app.diagrams.net.

**B) Internal breakdown** — in chat or markdown. Include: assumptions, topology, cost tables (all tiers/environments), risks, scaling triggers, ops checklist, effort estimate.

**C) Client-facing report** — `.docx` + `.pdf`. Generate both with Python libraries that work
on any machine: build the `.docx` with **`python-docx`** and the `.pdf` with **`reportlab`**
(install via `pip install python-docx reportlab` if missing — do not rely on `pandoc`, a
Terraform/Ansible CLI, or `/mnt/skills` paths being present). Follow the 11-section report
structure in `references/architecture.md`.

**D) Deployment scripts** — a `terraform/` + `ansible/` folder (per step 5) with a README covering apply steps, what to fill in, the Forge path for Laravel, and the pricing/calculator disclaimer. Present the files to the user.

## Output

- **Format:** four deliverables — a `.drawio` architecture diagram, an internal breakdown
  (chat/markdown), a client report as `.docx` + `.pdf`, and a `terraform/` + `ansible/` IaC
  project with a README. Pricing and architecture are also presented inline in chat.
- **Location:** files are written to the project's outputs folder (e.g. `outputs/<project>/`);
  the diagram opens at app.diagrams.net, the IaC is applied from its own folder.
- **Example:** for a NestJS + Next.js on AWS plan, the user receives
  `…-architecture.drawio`, `internal-breakdown.md`, `…-Infra-Plan.docx` / `.pdf`, and a
  `terraform/` + `ansible/` project with a README — preceded by a three-tier cost table and
  an approved topology in chat.

## Example

**User says:** "Plan the infra for a NestJS API + Next.js frontend on AWS, with staging and prod."

**Claude does:** Reads `references/intake-form.md` and runs the form section by section, echoes
the filled form for confirmation, prices three tiers from `references/aws.md`, designs the
architecture, then **stops at the step 4 approval gate** to present topology + cost + risks in
chat. After the user approves, it generates the `.drawio` diagram, the internal breakdown, the
`.docx`/`.pdf` client report (via `python-docx` + `reportlab`), and the `terraform/` + `ansible/`
project with a README.

**Result:** a complete, ready-to-deliver infra plan: cost estimate, architecture diagram,
client report, and apply-ready IaC for the chosen provider.

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
