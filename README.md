# Zyniverse Skills Registry

> Production-grade Claude skills built by the Zysk & Zyni teams. Public and installable by anyone.

[![Skills Registry](https://img.shields.io/badge/skills-zyniverse--hq-2D1B69?style=flat)](https://zyniverse-hq.github.io/skills-registry/website/)

## Install

Use the `skills` CLI to install from this registry into Claude Code, Cursor, Codex, or any compatible agent:

```bash
# Install all skills
npx skills add zyniverse-hq/skills-registry

# Install a specific skill
npx skills add zyniverse-hq/skills-registry --skill deployshield

# Install to Claude Code (global)
npx skills add zyniverse-hq/skills-registry -g -a claude-code -y

# Install to Claude Code (project-level)
npx skills add zyniverse-hq/skills-registry -a claude-code
```

Or reference individual skills in your `CLAUDE.md`:

```
> Use skill: github:zyniverse-hq/skills-registry/skills/deployshield
```

## Browse the registry

**→ [zyniverse-hq.github.io/skills-registry/website](https://zyniverse-hq.github.io/skills-registry/website/)**

Search, filter by category, and copy install snippets for any skill.

## Skills

> The registry is open for contributions. Skills appear here as they're merged via PR — see [CONTRIBUTING.md](CONTRIBUTING.md) to add yours.

| # | Skill | Author | Group | Category |
|---|-------|--------|-------|----------|
| _(awaiting first skill PR)_ | | | | |

## Contributing

All contributions go through **GitHub Pull Requests** — no manual submissions.

```bash
# Quick start
git clone https://github.com/zyniverse-hq/skills-registry.git
cd skills-registry
git checkout -b skill/your-skill-name
cp -r skills/_template skills/your-skill-name
# edit skills/your-skill-name/SKILL.md
git add skills/your-skill-name/
git commit -m "feat(skill): add your-skill-name"
git push origin skill/your-skill-name
# then open a PR on GitHub
```

See [CONTRIBUTING.md](CONTRIBUTING.md) for the full standard, field reference, and PR rules.

## Structure

```
skills-registry/
├── README.md
├── CONTRIBUTING.md          ← Contribution guide + SKILL.md standard
├── index.json               ← Machine-readable manifest
├── scripts/
│   └── validate_skill.py    ← Local validator
├── skills/
│   ├── _template/           ← Copy this to start a new skill
│   │   └── SKILL.md
│   └── <skill-name>/
│       └── SKILL.md
└── website/
    └── index.html           ← Registry UI
```

## CI

Every PR that touches `skills/**` is validated automatically:

- ✅ Branch name follows `skill/<name>` convention
- ✅ SKILL.md has required `name` and `description` fields
- ✅ Frontmatter passes schema validation
- ✅ Required content sections are present
- ✅ One skill per PR

---

Built by [Zyni Innovations Pvt. Ltd.](https://zyniverse.in) · Bengaluru
