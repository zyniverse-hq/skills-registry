---
name: skill-fixer
description: Fix the findings in a skill-reviewer report by editing the reviewed skill on a new git branch. Use this whenever someone wants to remediate, fix, address, or resolve the issues a skill review surfaced, or asks to "apply the fixes from the report" / "clean up this skill based on the review". Takes the JSON report from skill-reviewer's review_skill.py plus the skill folder. It applies safe deterministic fixes automatically, drafts fixes for judgement items, and flags anything unsafe to auto-fix (hardcoded secrets, confirmed-malicious code) for the user. Trigger after a skill has been reviewed and the findings need fixing.
metadata:
  version: 1.1.0
  author: Vikas M
  email: vikas.m@zysk.tech
  category: engineering-practice
  tags:
    - fix
    - remediation
    - skill-improvement
    - refactoring
    - automation
  product: zysk
  sprint: 1
  tested_with: claude-opus-4-8, claude-sonnet-4-6, glm-5.1
compatibility: "Python 3.8+ and git. No required third-party packages; PyYAML is used only if already installed. Operates on a git repository and creates a new branch."
---

# Skill Fixer

Take a skill-reviewer JSON report and remediate the findings on an isolated git
branch, so the user can review a clean diff before merging. The work is split:
the script does the deterministic, always-safe fixes; you do the judgement fixes;
neither you nor the script ever silently "fixes" something unsafe.

## Inputs

You need two things: the **JSON report** from skill-reviewer and the path to the
**skill folder** it reviewed. skill-reviewer writes its artifacts to
`.skill-review/<skill-name>/`, so the report is `.skill-review/<skill-name>/findings.json`
— read it from there by default. If you have only the skill, run skill-reviewer first
to produce the report. If either is missing, ask once and pause.

Write the artifacts this skill produces into that same folder, so review and fix output
stay together:

```
.skill-review/<skill-name>/
├── findings.json              # from skill-reviewer (input)
├── fix-manifest.json          # the auto/draft/human plan (step 1)
└── post-fix-findings.json     # re-judged still-open instruction findings (step 3)
```

Use the **unified** report - the one skill-reviewer produced with its
`--instruction-findings` folded in - so the mandatory LLM-judge instruction findings
(`check` = `instruction:*`, Major/Minor) are present and get fixed, not just the
mechanical ones. They route to the draft bucket like any other finding.

## Safety boundaries (non-negotiable)

- **Never auto-edit a hardcoded secret.** A text edit cannot rotate a leaked
  credential, so rewriting it would falsely imply the leak is resolved. Secrets go
  to the user with instructions to remove and rotate, regardless of any request to
  "fix everything".
- **Never auto-fix a security pattern you have not confirmed.** Any `REVIEW`
  finding - a `scan:` code pattern, a `prose:` instruction flag, or a flagged
  binary artifact - is a question, not a defect. If you confirm it is malicious,
  stop and tell the user; do not quietly rewrite it.
- **The reviewer's `ADVICE` rows are pointers, not fixes.** They are
  non-authoritative leads from the static checker, not findings — skip them. The
  substantive instruction-quality findings arrive as Major/Minor (often as draft
  items you read from the review report) and are fixed like any other finding.
- **Only branch from a clean tree.** The script refuses to create a branch if the
  working tree is dirty, and never commits to the existing branch, pushes, or
  deletes anything.

## Workflow

The commands below use `python3` for brevity. On Windows the interpreter is usually
`python` (not `python3`), so substitute your platform's interpreter name; paths use
forward slashes, which work on Windows too.

### 1. Prepare the branch and apply deterministic fixes

```bash
python3 scripts/prepare_fixes.py --skill <skill-folder> \
    --report .skill-review/<skill-name>/findings.json \
    --json .skill-review/<skill-name>/fix-manifest.json
```

This classifies every finding into **auto** (applied + committed now), **draft**
(for you to fix), or **human** (flagged, never auto-fixed). It creates branch
`skill-fix/<name>-<timestamp>` off the current branch, applies the auto-fixes
(insert a missing TOC, sync a name/folder mismatch), and commits them. Read the
printed plan and the manifest JSON before continuing.

If the git note says the tree is dirty or the folder is not a repo, relay that to
the user and stop. They commit/stash (or init git) and re-run; you do not work
around it by editing files outside a branch unless they ask. (The `.skill-review/`
artifact folder is exempt from the dirty check: the script `git stash push -u`es it
out of the way before branching - so it can't block the checkout or be swept into the
auto-fix commit by `git add -A` - then pops it straight back onto the new branch. The
git note says so when it happens; if a pop ever fails, the note tells you to recover
with `git stash pop`.)

### 2. Fix the draft items on the branch

Work through `draft_todo` in the manifest. Read the actual file before each edit;
see `references/fix-strategies.md` for how to handle each finding type. Common
ones: rewrite a weak description to state what + when (the biggest triggering
lever); fix a non-compiling script; split a bloated SKILL.md body into
`references/`; declare an undisclosed dependency in `compatibility` or a
requirements file; rename a skill that collides with a bundled name.

### 3. Re-review to confirm

Re-run skill-reviewer on the now-fixed folder and verify you did not regress it. The
script re-runs the mechanical checks itself, but **instruction findings are yours to
re-judge** - it cannot regenerate them. So re-read the fixed skill's instructions (as
in a review), write the ones that are *still open* to
`.skill-review/<skill-name>/post-fix-findings.json` (an empty array `[]` if you
resolved them all), and pass it:

```bash
python3 scripts/verify_fixes.py --before .skill-review/<skill-name>/findings.json \
    --skill <skill-folder> --reviewer <path/to/review_skill.py> \
    --after-instruction-findings .skill-review/<skill-name>/post-fix-findings.json
```

`review_skill.py` ships with the skill-reviewer skill (the same checker that produced
the report), usually installed alongside this one under `<skills-dir>/skill-reviewer`
in its `scripts/` folder. If you can't find it, ask the user for skill-reviewer's
path rather than guessing.

This folds your re-judged findings into a fresh review, then confirms the target
problems cleared, no new problem appeared, and the gate/score did not drop; it exits
non-zero on any regression. If the before report had instruction findings and you
omit `--after-instruction-findings`, it reports **INCOMPLETE** and exits non-zero
rather than falsely clearing them - it will not judge instructions for you. If it
reports a regression, fix or revert the offending change before reporting back; never
leave the branch worse than you found it. Anything still present that is not a
regression is a human-required item or needs another pass.

### 4. Report back

Tell the user, in plain prose: the branch name, what was auto-fixed, what you fixed
by hand, what they must handle themselves (each secret with a rotate-it
instruction), and the before/after gate and score. Do not merge the branch or
push - that is the user's call.

## Example

Input: `.skill-review/changelog-gen/findings.json` flags a short description (MAJOR),
a missing TOC (MINOR), and a hardcoded AWS key (BLOCKER).

1. `prepare_fixes.py` branches, inserts the TOC, commits. Manifest: 1 auto, 1
   draft (description), 1 human (secret).
2. You rewrite the description to add when-to-use cues.
3. Re-review: the description and TOC findings clear, but the gate stays FAILS SPEC
   because the secret is a Blocker the fixer must not touch - it drops to NEEDS
   REVIEW only once the user removes and rotates the key.
4. Report: branch `skill-fix/...`, TOC auto-added, description rewritten, and a
   clear note that the AWS key in `scripts/x.py:12` must be removed and rotated by
   them.
