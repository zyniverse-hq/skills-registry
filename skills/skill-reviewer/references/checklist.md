# Skill Review Checklist

The full criteria behind the four review dimensions. The static checker
(`scripts/review_skill.py`) automates the mechanical checks; this file is the
reference for the judgement calls and for explaining findings in the report.

## Contents

- [1. Structure and spec compliance](#1-structure-and-spec-compliance)
- [2. Quality](#2-quality)
- [3. Triggering accuracy](#3-triggering-accuracy)
- [4. Security and safety](#4-security-and-safety)

## 1. Structure and spec compliance

These are hard requirements. A failure here means the skill will not upload to the
Skills API or claude.ai, so they are Blockers.

- Exactly one `SKILL.md`, at the folder root. Nested SKILL.md files are rejected on
  upload (only Claude Code's filesystem loads nested ones). Supporting docs must use
  non-SKILL.md names, e.g. `references/<topic>.md`.
- Frontmatter starts with `---`, closes with `---`, and parses as a YAML mapping.
- Only these frontmatter keys are allowed: `name`, `description`, `license`,
  `allowed-tools`, `metadata`, `compatibility`. Anything else fails validation.
- `name` is required, kebab-case (`^[a-z0-9-]+$`), no leading/trailing hyphen, no
  `--`, max 64 characters. It should match the folder name.
- `description` is required, max 1024 characters, and must not contain `<` or `>`.
- `compatibility`, if present, is a string of at most 500 characters.

## 2. Quality

The core of this dimension is the **instruction review**: judging the skill's prompts
and instructions as an LLM-as-judge. That pass is **mandatory** and its findings are
required fixes (Major/Minor by impact), not advisory - see
`references/instruction-review.md` for the lenses and how to write each finding. The
structural and stylistic heuristics below complement it; they are softer judgement
calls, also rated Major/Minor.

- **Progressive disclosure.** SKILL.md body should be lean (~500 lines is the soft
  ceiling). Detail belongs in `references/` files that are loaded only when needed.
  Reference files over ~300 lines should open with a table of contents.
- **Resource organisation.** Executable helpers in `scripts/`, docs in
  `references/`, output templates/fonts/icons in `assets/`. Bundling a script the
  skill always needs beats making the model rewrite it each run.
  > The size flags above are signals, not verdicts: confirm detail is genuinely
  > movable via the *Structure / progressive disclosure* lens in
  > `references/instruction-review.md` before raising a split finding.
- **Writing style.** Prefer imperative instructions that explain *why* a step
  matters. Heavy reliance on all-caps ALWAYS/NEVER/MUST is a yellow flag: it tends
  to overfit and constrain the model instead of giving it a good mental model.
- **Leanness.** Cut instructions that don't pull their weight or send the model
  down unproductive paths. If reviewing test transcripts, watch for wasted steps.
- **Output formats.** Where the skill produces structured output, it should define
  the format clearly, ideally with a short input/output example.

## 3. Triggering accuracy

The `description` is the primary mechanism Claude uses to decide whether to invoke
a skill. Most skills *under*-trigger (don't fire when they'd help), so descriptions
should be a little pushy.

- Does the description state both **what** the skill does and **when** to use it,
  including casual or implicit phrasings ("is this good?", "vet this")?
- Build a small trigger eval set to reason about: roughly 8-10 queries that should
  trigger (varied phrasings, formal and casual) and 8-10 that should not. The
  valuable negatives are tricky near-misses that share keywords but need a
  different tool, not obviously-unrelated prompts.
- Remember simple one-step tasks may not trigger any skill even with a perfect
  description, because Claude handles them directly. Judge against substantive
  tasks.
- The quantitative triggering optimizer (running each query several times to get a
  trigger rate) requires Claude Code's `claude` CLI. If it isn't available, reason
  qualitatively and say so rather than implying a measured rate.

## 4. Security and safety

A skill must not contain malware, exploit code, or anything enabling unauthorized
access or data exfiltration. The guiding test is the **principle of lack of
surprise**: the skill's contents must do only what its description leads a user to
expect.

The scanner flags these pattern categories in code files for human review (they
are not automatic failures - many are legitimate):

- **network** - outbound calls (requests, urllib, sockets, curl, fetch, axios).
- **process_exec** - subprocess, os.system, eval/exec, shell=True, pickle.loads.
- **destructive_fs** - rm -rf, rmtree, file/dir removal.
- **secrets** - environment/credential access, .aws/.ssh/.env, password/token.
- **obfuscation** - base64 decode feeding exec, other indirection that hides intent.

Code files are not the only surface. A skill is *followed* as natural-language
instructions, so the scanner also reads the **prose** (SKILL.md + references) and
flags, as REVIEW: pipe-to-shell (`curl ... | bash`), exfiltration phrasing
("upload/send ... to <url>"), hardcoded IPs, and long encoded blobs. It likewise
flags **undeclared binaries** (`.exe`/`.dll`/`.so`/`.pyc`, etc.), **shebang
scripts** that have no code extension, and **notebook code cells** - all places
real code or directions can hide from a code-only scan.

For each flag, ask: is this consistent with the stated purpose? A "fetch GitHub
releases" skill making an HTTPS call is expected. The same call in a skill that
claims to only format local text is a surprise and a Blocker. Treat encoded
payloads, credential reads paired with network calls, and undisclosed destructive
commands as Blockers.
