# Contributing to the Zyniverse Skills Registry

The Zyniverse Skills Registry is a **public** collection of Claude skills built by Zysk Technologies and Zyni Innovations. Anyone can install these skills. Everyone contributes the same way — fork, branch, PR.

---

## Workflow

```
Fork the repo → Clone your fork → Create branch → Add skill → Push → Open PR
```

---

## Step-by-step

### 1. Fork the repository

Go to **[github.com/zyniverse-hq/skills-registry](https://github.com/zyniverse-hq/skills-registry)** and click **Fork** (top-right). This creates your own copy under your GitHub account.

You only do this once.

### 2. Clone your fork

```bash
git clone https://github.com/<your-username>/skills-registry.git
cd skills-registry
```

### 3. Add the upstream remote (one-time)

This keeps your fork in sync with the main registry:

```bash
git remote add upstream https://github.com/zyniverse-hq/skills-registry.git
```

### 4. Sync before starting work

Always pull the latest from upstream before creating a new branch:

```bash
git fetch upstream
git checkout main
git merge upstream/main
```

### 5. Create a branch

Branch names must follow `skill/<skill-name>`:

```bash
git checkout -b skill/your-skill-name
```

### 6. Add your skill

```bash
cp -r skills/_template skills/your-skill-name
# Now edit skills/your-skill-name/SKILL.md
```

### 7. Validate locally

```bash
python3 scripts/validate_skill.py skills/your-skill-name/SKILL.md
```

Fix any errors before pushing. Warnings are advisory.

### 8. Commit and push to your fork

```bash
git add skills/your-skill-name/
git commit -m "feat(skill): add your-skill-name"
git push origin skill/your-skill-name
```

### 9. Open a Pull Request

Go to **[github.com/zyniverse-hq/skills-registry/pulls](https://github.com/zyniverse-hq/skills-registry/pulls)** → **New pull request** → **compare across forks**.

Select:
- **base repository:** `zyniverse-hq/skills-registry` / `main`
- **head repository:** `<your-username>/skills-registry` / `skill/your-skill-name`

The PR template will appear. Fill it in and submit.

---

## SKILL.md Standard

Every skill is a single folder containing one file:

```
skills/
└── your-skill-name/
    └── SKILL.md
```

### Required frontmatter fields

| Field | Type | Description |
|-------|------|-------------|
| `name` | string | Unique slug — **must match the folder name exactly**. Lowercase, hyphens only. |
| `description` | string | One sentence, verb-first. This is how Claude decides when to activate the skill. |

### Extended Zyniverse fields (strongly recommended)

These live **under a top-level `metadata:` map** — per the agentskills.io spec, only `name`, `description`, and the spec fields (`license`, `compatibility`, `allowed-tools`) belong at the top level. The tooling reads these fields from either placement, but `metadata:` is the standard (see the template below).

| Field | Type | Values |
|-------|------|--------|
| `version` | semver | Start at `1.0.0` |
| `author` | string | Your full name |
| `email` | string | Your Zysk / Zyni email |
| `category` | string | See categories below |
| `tags` | list | 2–5 lowercase kebab-case tags |
| `product` | string | `zysk` \| `tms` \| `zyniverse` |
| `sprint` | integer | Sprint number this was built in |
| `tested_with` | string | Model used during development |

### Valid categories

| Slug | What belongs here |
|------|-------------------|
| `qa-testing` | Test case generation, review automation, coverage analysis |
| `pre-deploy-safety` | Pre-deployment checks, risk audits, release safety |
| `business-sales` | Proposals, investor forms, sales automation |
| `engineering-practice` | Code review, architecture, development practices |
| `frontend-integration` | UI components, design systems, frontend↔backend wiring |
| `infra-security` | Security audits, infrastructure, access controls |
| `documents` | Word, PDF, Excel, PowerPoint generation |
| `ai-agents` | LangGraph, MCP, multi-agent systems |
| `data` | Data analysis, extraction, reporting |
| `comms` | Internal comms, emails, announcements |
| `hr-recruiting` | Resume screening, candidate interviews, and recruiting workflows |

### Full SKILL.md template

```markdown
---
name: your-skill-name
description: Verb-first one sentence that tells Claude what this skill does and when to use it.
metadata:
  version: 1.0.0
  author: Your Full Name
  email: you@zysk.tech
  category: engineering-practice
  tags:
    - tag-one
    - tag-two
  product: zysk
  sprint: 1
  tested_with: claude-sonnet-4-6
---

# Skill Title

> One-line summary — mirrors the description above.

## When to use

- Activate when: [specific condition]
- Activate when: [specific condition]
- Do NOT activate when: [anti-pattern]

## Prerequisites

- [ ] Prerequisite 1
- [ ] Prerequisite 2

## Steps

### Step 1: [Action name]
[Instructions for Claude]

### Step 2: [Action name]
[Instructions for Claude]

## Output

- **Format:** file / message / artifact / code block
- **Location:** where it appears
- **Example:** brief example

## Example

**User says:** "..."
**Claude does:** [what happens]
**Result:** [what the user gets]

## Notes

- Edge cases, caveats, known limitations
```

---

## PR rules

- **One skill per PR.** Don't bundle multiple skills — open separate PRs.
- **Branch must be `skill/<skill-name>`.** CI rejects other patterns.
- **CI must pass** before requesting review.
- **Folder name, `name` frontmatter, and branch suffix must all match.**
- **Don't modify other people's skills** in your PR — open a separate PR for fixes to existing skills.

---

## Versioning

| Change | Bump | Example |
|--------|------|---------|
| Typo, wording fix | Patch | `1.0.0` → `1.0.1` |
| New section or example | Minor | `1.0.0` → `1.1.0` |
| Full rewrite | Major | `1.0.0` → `2.0.0` |

---

## Installing skills from this registry

```bash
# Install all skills
npx skills add zyniverse-hq/skills-registry

# Install a specific skill
npx skills add zyniverse-hq/skills-registry --skill your-skill-name

# Install to Claude Code globally
npx skills add zyniverse-hq/skills-registry -g -a claude-code -y
```

---

## Questions?

Open a [GitHub Issue](https://github.com/zyniverse-hq/skills-registry/issues) or reach out to `varun@zysk.tech`.
