# Skill Authoring Guide

How to write a skill that triggers reliably, stays maintainable, and earns its place
in a curated registry. For the mechanical standard (required fields, valid categories,
the template), see [CONTRIBUTING.md](../CONTRIBUTING.md); this guide is about writing a
*good* skill. The underlying format is the open [agentskills.io](https://agentskills.io)
spec.

## How a skill loads: progressive disclosure

A skill is loaded in three levels, cheapest first. Design for this — it's the single
most important idea in skill authoring.

1. **Metadata (`name` + `description`)** — always in context. ~A sentence. This is all
   Claude sees when deciding *whether* to use the skill.
2. **`SKILL.md` body** — loaded only once the skill triggers. Keep it focused (aim for
   under ~500 lines). This is the *how*.
3. **Bundled resources (`scripts/`, `references/`, `assets/`)** — pulled in only when
   needed. Unlimited size; scripts can even run without their source entering context.

The win: keep the body lean and push depth into references the model reads on demand, so
a skill can be rich without bloating every invocation.

## The description is the trigger

`description` is how Claude decides to activate the skill, so it carries the most weight.
Write what the skill does **and** when to use it, and lean slightly pushy — models tend to
*under*-trigger.

```
# weak — vague, under-triggers
description: Helps with deployments.

# strong — concrete + explicit triggers
description: Audits a branch or diff for production risks before a release. Use whenever
  the user asks if code is safe to deploy, wants a pre-release risk check, blast-radius
  or rollback assessment — even if they don't say "deployment".
```

Name the situations and the synonyms a user might actually say. Keep it one focused idea;
if you're listing two unrelated jobs, that's two skills.

## The body: structure and voice

Required sections (the validator enforces these): `## When to use`, `## Steps`, `## Output`.
Beyond that:

- **Write in the imperative**, addressed to Claude: "Scan the diff", not "The skill scans".
- **Explain *why*, not just what.** Today's models follow reasoning better than rigid rules.
  A short "because…" beats an ALL-CAPS MUST. If you're reaching for NEVER/ALWAYS everywhere,
  reframe and explain the stakes instead.
- **Be specific about output** — format, location, and a short example — so results are
  predictable.
- **Cover the edges** in a short Notes section: when *not* to act, known limitations.

## Bundled resources — when to use which

| Directory | Use for | Example |
|-----------|---------|---------|
| `scripts/` | Deterministic, repetitive, or fiddly work better done by code than by re-deriving it each run | a `gh` GraphQL fetch, a file transform |
| `references/` | Detail the body shouldn't carry — API tables, per-framework docs, taxonomies | `references/aws.md`, a category map |
| `assets/` | Files used *in the output* | a `.docx` template, an icon, a font |

Guidance:
- **Reach for `scripts/` when you notice the model would otherwise write the same helper
  every time.** Write it once, bundle it, and have the body call it. Bundled scripts must be
  **cross-platform and UTF-8-safe** (this registry runs on Windows too — pin encodings on
  subprocess calls and stdout; see existing scripts for the pattern).
- **Reach for `references/` to keep the body short.** Point to them explicitly from the body
  ("for the Azure path, read `references/azure.md`") so the model knows when to load them. For
  files over ~300 lines, add a short table of contents.
- Both layouts are valid: reference docs at the **skill root** (e.g. `reference.md`,
  `forms.md`) or under a **`references/` subdir**. Pick one and be consistent.

## A multi-file skill

High-quality skills are often more than one file:

```
pdf-forms/
├── SKILL.md            # workflow + when to use; points to the references below
├── reference.md        # the full field/API detail, loaded on demand
├── forms.md            # a focused sub-topic
└── scripts/
    └── fill_form.py    # the deterministic step
```

`SKILL.md` stays short and routes to the right resource; the heavy detail lives where it's
only paid for when used. (Anthropic's own `pdf` skill is built exactly this way.)

## Security and the principle of least surprise

Skills run with the agent's permissions, and bundled scripts execute in the user's
environment — so authoring is a position of trust.

- A skill must do only what its description implies. No hidden side effects, data
  exfiltration, or destructive actions a reader wouldn't expect.
- Be explicit about anything sensitive a script does (network calls, shell, `gh`/git writes)
  so reviewers and users can see it.
- No malware, credential harvesting, or obfuscated behavior — such PRs are rejected.

## What CI enforces

`scripts/validate_skill.py` runs on every changed skill and checks:

- `name` is a valid slug and **matches the folder name**;
- `description` is present and within length limits;
- `category` is one of the canonical slugs (in `scripts/categories.json`);
- the required `## When to use` / `## Steps` / `## Output` sections exist;
- extended fields are well-formed (nested under `metadata:`).

Run it locally before opening a PR (`PYTHONUTF8=1` on Windows). Bundled scripts are also
compile-checked on Linux and Windows.

## Versioning

Bump the skill's `metadata.version` with each meaningful change: patch for fixes/wording,
minor for new sections or capabilities, major for a rewrite.

## Before you open a PR

- `validate_skill.py` passes with no errors.
- The description names real trigger phrases.
- The body is lean; depth is in references; repeated work is in a script.
- You've sanity-tested the skill on a couple of realistic prompts.
