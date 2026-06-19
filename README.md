# Zyniverse Skills Registry

> Production-grade [agent skills](https://agentskills.io) by Zyni Innovations — curated, versioned, and installable as a Claude Code plugin.

[![Browse the registry](https://img.shields.io/badge/browse-registry-2D1B69?style=flat)](https://zyniverse-hq.github.io/skills-registry/website/)
[![License: Apache 2.0](https://img.shields.io/badge/license-Apache--2.0-blue.svg)](LICENSE)

Each skill is a self-contained folder under [`skills/`](skills/) with a `SKILL.md`
(instructions + metadata) and any scripts, references, or assets it needs. Skills
are reviewed before they're merged, so the registry stays small, sharp, and
non-overlapping rather than a dumping ground.

## Install

The registry is a **Claude Code plugin marketplace**. Add it once, then install
skills individually:

```
/plugin marketplace add zyniverse-hq/skills-registry
/plugin install <skill-name>@zyniverse-skills
```

For example, `/plugin install daily-status@zyniverse-skills`. Browse every
available skill with `/plugin`, or on the site below. Installed skills are
available to Claude immediately — no extra setup.

> Already added the marketplace? Pull new and updated skills with
> `/plugin marketplace update zyniverse-skills`.

## Browse

**→ [zyniverse-hq.github.io/skills-registry/website](https://zyniverse-hq.github.io/skills-registry/website/)**

Search and filter the full, always-current catalog. The site is driven by
[`index.json`](index.json), which is generated from the skills — never edited by hand.

## What's inside

Skills span these categories:

- 🧪 QA & Testing Automation
- 🛡️ Pre-Deployment & Release Safety
- 💼 Business & Sales Automation
- 🤝 HR & Recruiting
- 🛠️ Engineering Practice & Decision Support
- 🔌 Frontend & Backend Integration
- 🔐 Infrastructure, Ops & Security
- 📊 Data, Analysis & Reporting
- 🤖 AI Agents & Prompts
- 💬 Communications & Content

See the [website](https://zyniverse-hq.github.io/skills-registry/website/) for the
complete, current list.

## Contributing

Contributions are welcome and curated — every skill goes through a GitHub Pull
Request and review. Quick start:

```bash
git clone https://github.com/zyniverse-hq/skills-registry.git
cd skills-registry
git checkout -b add-my-skill
cp -r skills/_template skills/my-skill          # folder name == the skill's name
$EDITOR skills/my-skill/SKILL.md                # write it
pip install pyyaml
python scripts/validate_skill.py skills/my-skill/SKILL.md   # must pass
# commit (Conventional Commits), push, open a PR
```

There's no one-skill-per-PR or branch-name rule — cohesive multi-skill PRs are
fine. See **[CONTRIBUTING.md](CONTRIBUTING.md)** for the full standard, the
frontmatter reference, and authoring guidance.

## Repository structure

```
skills-registry/
├── skills/                     # the skills (one folder each)
│   ├── _template/SKILL.md      # copy this to start a new skill
│   └── <skill-name>/
│       ├── SKILL.md            # required: frontmatter + instructions
│       └── scripts|references|assets/   # optional bundled resources
├── scripts/
│   ├── validate_skill.py       # SKILL.md quality gate (CI-enforced)
│   ├── generate_index.py       # builds index.json + marketplace.json
│   └── categories.json         # single source of truth for categories
├── index.json                  # GENERATED catalog (do not hand-edit)
├── .claude-plugin/             # GENERATED plugin marketplace
├── website/                    # static browse UI (reads index.json)
├── CONTRIBUTING.md · AGENTS.md · LICENSE · SECURITY.md · CODE_OF_CONDUCT.md
└── .github/workflows/          # validation + index regeneration
```

## Quality gates

Every PR is checked automatically:

- **`validate_skill.py`** on each changed skill — frontmatter schema, valid
  category, and the required `## When to use` / `## Steps` / `## Output` sections.
- **Cross-platform compile** of every bundled script (Linux + Windows).
- **`index.json` / `marketplace.json`** are regenerated from the skills on merge,
  so the catalog never drifts.

## License

[Apache License 2.0](LICENSE). By contributing a skill you agree your contribution
is licensed under the same terms.

---

Built by [Zyni Innovations Pvt. Ltd.](https://zyniverse.in) · Bengaluru
