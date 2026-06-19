# AGENTS.md

Guidance for AI coding agents working **on this repository** (the registry itself).
For authoring a *skill*, see [CONTRIBUTING.md](CONTRIBUTING.md).

> `CLAUDE.md` is a symlink to this file — one source of truth for every agent.

## What this repo is

A curated registry of agent skills. Each skill is a folder under `skills/` with a
`SKILL.md` (YAML frontmatter + Markdown instructions) and optional bundled
`scripts/`, `references/`, and `assets/`. `index.json` is a **generated** catalog
consumed by the website.

## Prerequisites

- Python 3.11+ with `pyyaml` (`pip install pyyaml`)
- [`gh`](https://cli.github.com/) authenticated (only needed for skills/scripts that call GitHub)

On Windows, prefix Python commands with `PYTHONUTF8=1` — several files contain
non-ASCII (emoji icons, em-dashes) and the default cp1252 codec will crash.

## Repository structure

```
skills/
  <skill-name>/
    SKILL.md            # required: frontmatter + instructions
    scripts/            # optional: executable helpers
    references/         # optional: docs loaded on demand
    assets/             # optional: templates/files used in output
  _template/SKILL.md    # starting point for new skills
scripts/
  validate_skill.py     # CI quality gate for SKILL.md
  generate_index.py     # rebuilds index.json + marketplace.json from skills/
  categories.json       # single source of truth for the category taxonomy
index.json              # GENERATED — do not hand-edit
.claude-plugin/         # GENERATED — plugin marketplace (one entry per skill)
website/                # static site that reads index.json
.github/workflows/      # validate-skill, scripts-check, regenerate-index, …
```

## Commands

```bash
# Validate one or more changed skills (the CI quality gate)
PYTHONUTF8=1 python scripts/validate_skill.py skills/<name>/SKILL.md

# Rebuild index.json from skills/
PYTHONUTF8=1 python scripts/generate_index.py

# Check the index is in sync without writing (used by CI / before committing)
PYTHONUTF8=1 python scripts/generate_index.py --check
```

## Conventions

- **Frontmatter shape:** only `name`, `description`, and spec fields
  (`license`, `compatibility`, `allowed-tools`) at the top level; all other
  fields (`version`, `author`, `email`, `category`, `tags`, …) nested under a
  `metadata:` map. Tooling reads either placement, but `metadata:` is the standard.
- **Categories:** defined once in `scripts/categories.json`. Add a new category
  there (slug + label + icon); never invent a slug inline.
- **Required SKILL.md sections:** `## When to use`, `## Steps`, `## Output`.
- **`index.json` and `.claude-plugin/marketplace.json` are generated** by
  `scripts/generate_index.py` — never edit them by hand. The `regenerate-index`
  workflow rebuilds and commits them on push to `main`.
- **PRs:** there is no one-skill-per-PR or branch-name rule — cohesive
  multi-skill and cross-cutting PRs are fine. Use [Conventional Commits](https://www.conventionalcommits.org/)
  (`feat:`, `fix:`, `chore:`, `ci:`, `docs:`, `refactor:`).

## Before completing any task

Run the quality gate on whatever you touched and confirm it's green:

```bash
PYTHONUTF8=1 python scripts/validate_skill.py skills/<changed>/SKILL.md
PYTHONUTF8=1 python scripts/generate_index.py --check
```

If you changed a bundled `*.py` script, also compile it
(`python -B -m py_compile <script>`). Don't claim a task is done until these pass.
