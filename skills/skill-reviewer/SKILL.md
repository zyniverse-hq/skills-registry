---
name: skill-reviewer
description: Review, audit, or quality-check an Anthropic Agent Skill (a SKILL.md folder) and produce a detailed review report. Use this whenever someone asks to review, audit, evaluate, vet, grade, or QA a skill, check whether a SKILL.md is well-formed or upload-ready, assess a skill's triggering, description, or instruction quality (whether its prompts are clear, complete, and internally consistent), or security-review a skill before sharing or installing it. Use it even when the person just points at a skill folder and asks "is this good?" or "what's wrong with this skill?". Trigger when a path to a skill directory or a SKILL.md file is provided for review.
compatibility: "Python 3.8+. No required third-party packages. PyYAML is used for exact frontmatter parsing only if it is already installed; otherwise a built-in parser is used."
metadata:
  version: 1.1.0
  author: Vikas M
  email: vikas.m@zysk.tech
  category: engineering-practice
  tags:
    - review
    - quality-assurance
    - skill-audit
    - linting
    - validation
  product: zysk
  sprint: 1
  tested_with: claude-opus-4-8, claude-sonnet-4-6, glm-5.1
---

# Skill Reviewer

Review an Agent Skill and return a prioritized report. Two layers do the work: a
deterministic **static checker** (spec, structure, security, footprint), and - the
part that makes this more than a linter - a mandatory **instruction review**, where
you act as an expert LLM judge of the skill's prompts and instructions. A skill *is*
a prompt, so judging whether its instructions are clear, complete, consistent, and
actually steer the model right is the core of the review, not an afterthought. The
goal is a report a maintainer can act on, with each finding rated by severity and
paired with a concrete fix.

## When to use

- Activate when: someone asks to review, audit, evaluate, vet, grade, or QA a skill, or to check whether a SKILL.md is well-formed or upload-ready.
- Activate when: someone wants a skill's triggering, description, instruction quality, or security assessed before sharing or installing it.
- Activate when: a person points at a skill folder or SKILL.md and asks "is this good?" / "what's wrong with this skill?".
- Do NOT activate when: no skill path is provided — ask for the skill folder first.

## Inputs

You need a path to the skill folder (the directory containing `SKILL.md`). If the
person hasn't given one, ask once for it and pause. Don't guess a path.

## Steps

Run these steps in order. The script does the deterministic checks fast and
consistently; you do the judgement the script can't.

**Review against the spec and this checklist only — never against the host repo's
own conventions.** Grade the skill as the Agent Skill spec defines it: a local
project rule, registry convention, house style, or team norm does not excuse a
finding or lower its severity. If a project's convention conflicts with the spec,
the skill still fails the spec — report it at full severity with the spec-compliant
fix, and note the convention as one line of context for the maintainer to reconcile
separately. Your job is to report what the checklist says, not to pre-absolve
violations because "that's how this repo does it."

**Artifact folder.** Write every file this review produces into one folder so the
artifacts stay together and skill-fixer has a single predictable place to read from,
instead of scattering files at the working-directory root. The convention is:

```
.skill-review/<skill-name>/
├── report.md                  # the human-readable review report (step 4)
├── findings.json              # unified findings JSON — skill-fixer reads this (steps 1 & 4)
└── instruction-findings.json  # your authored instruction findings (--instruction-findings, step 4)
```

`<skill-name>` is the reviewed skill's folder name, so reviewing several skills never
collides. Create the folder once before step 1 (`mkdir -p .skill-review/<skill-name>`).
The folder holds throwaway analysis artifacts — add `.skill-review/` to `.gitignore`
if the repo doesn't already ignore it; keep `report.md` elsewhere if you want it tracked.

The commands below use `python3` for brevity. On Windows the interpreter is usually
`python` (not `python3`), so substitute your platform's interpreter name; paths use
forward slashes, which work on Windows too.

### 1. Run the static checker

```bash
python3 scripts/review_skill.py <path/to/skill-folder> \
    --json .skill-review/<skill-name>/findings.json
```

It prints a severity-sorted summary and writes JSON. It only reads files (no
network, no subprocess, no deletion - reviewing a skill never runs that skill's
code), and uses PyYAML if installed or a built-in parser otherwise, so it runs on
a stock Python 3 install. Read both the printed output and the JSON before
continuing. For CI gating, add `--fail-on {blocker,major,review}` to make the exit
code non-zero at or above that severity (default: blocker); the JSON also records
`reviewer_version` and `generated_at` for an audit trail.

The output includes:
- A **gate**: `FAILS SPEC` (a BLOCKER - would not upload), `NEEDS FIXES` (a MAJOR),
  `NEEDS REVIEW` (only REVIEW-level flags to confirm), or `CLEAN`.
- A **score** (0-100 + letter) per dimension. It is a heuristic for tracking, not
  the verdict - you assign the verdict. The overall score is capped by the gate, so
  a skill with a Blocker or Major can't show a passing grade.
- A **footprint**: estimated always-on tokens (name + description), on-trigger
  tokens (SKILL.md body), and bundle size. Useful for context-cost review.

Severity `REVIEW` means an unconfirmed flag a human must judge (e.g. a scanned
network/exec pattern), not a confirmed defect. Confirmed problems (real hardcoded
secrets, non-compiling scripts, spec violations) come back as BLOCKER or MAJOR.

### 2. Read the skill yourself for what the script can't judge

Open the target `SKILL.md`, plus every file under `scripts/`, `references/`, and
`assets/`. The script flags patterns; you decide what they mean. Use
`references/checklist.md` for the full criteria. The judgement calls that need a
human-level read:

- **Instruction quality (the core of the review - mandatory).** This is the value
  the static checker cannot provide. Read the SKILL.md and references as an expert
  who must execute them with no other context, and judge whether the instructions
  hold up as a prompt: clear, complete, internally consistent, and likely to steer
  the model to the right behavior. Hunt for gaps (missing steps, unstated
  preconditions, unhandled inputs), ambiguity, internal contradictions,
  description-vs-body mismatch, guidance that would misdirect the model, and
  under-specified output. Also judge the everyday quality signals: imperative
  instructions that explain *why* over rigid all-caps directives, a lean body, and
  output formats shown with examples. **Every issue you find is a finding (Major or
  Minor) with a required fix - not optional polish.** See
  `references/instruction-review.md` for the full rubric.
- **Triggering**: Does the description say both *what* it does and *when* to use
  it? Would it fire on realistic phrasings and stay quiet on near-misses? Draft a
  trigger eval set: 8-10 queries that should trigger (varied, casual and formal)
  and 8-10 tricky should-not near-misses that share keywords but need a different
  tool. Save it as a JSON array of `{"query": "...", "should_trigger": true|false}`
  and check it with:

  ```bash
  python3 scripts/validate_eval_set.py <eval-set.json>
  ```

  That confirms the set is well-formed and balanced before it is used to measure a
  trigger rate. Measuring the actual trigger rate requires running the queries
  through Claude Code's `claude` CLI (a separate runner); if that runner is not
  available, reason through the eval set qualitatively and say the rate was not
  measured rather than implying a number.
- **Security**: For each pattern the scanner flagged, judge it in context. A
  network call or `subprocess` may be legitimate for the skill's stated job, or it
  may be a surprise the description never mentions. The test is the principle of
  lack of surprise: does the code do only what the description claims? The scanner
  also reads the *prose* (SKILL.md + references) for instructions that would
  surprise a reader - pipe-to-shell, exfiltration, raw IPs, encoded blobs - plus
  shebang scripts, notebook code cells, and undeclared binaries. Apply the same
  test to those: a skill's instructions are followed, so they are part of its
  attack surface, not just its code.

The static checker also emits **instruction-review pointers** (ADVICE severity):
mechanical hits like vague wording, an overlong section, a vague heading, a repeated
sentence, a single-phrasing description, or a missing example. These are *leads, not
the deliverable*, and do not by themselves affect the grade - they are weak proxies
that point you at spots to inspect. Confirm and expand each one in the instruction
review: promote anything real to a Major/Minor finding with a fix, and discard the
rest. The mandatory instruction review above - guided by
`references/instruction-review.md` - is where the actual judgement lives and where
the production-grade bar is set.

### 3. Optional: deeper testing (Claude Code only)

For skills that warrant more than static review, two higher-cost steps are
described in `references/functional-testing.md`: a **measured trigger rate**
(delegated to skill-creator's runner; run `scripts/find_skill_creator.py` to locate
it, and fall back to qualitative reasoning if it is absent) and a **functional test
harness** that runs the skill on real prompts via subagents and grades the output.
Both need the `claude` CLI or subagents, so they run only in Claude Code and cost
model calls. Skip them for a quick review; never report a trigger rate you did not
actually measure.

### 4. Fold in your instruction findings, then write the report

Do this in order. **First record the instruction findings** from your read (step 2)
so they reach the score, gate, and skill-fixer - they live in your head, but the
report header and the fixer both read the JSON. Write them as a JSON array and re-run
the checker with `--instruction-findings`, which recomputes the gate, counts, and
score over the combined set:

```bash
# .skill-review/<skill-name>/instruction-findings.json - one object per finding:
# [{"dimension": "quality", "severity": "MAJOR",
#   "check": "instruction:step3-precondition",
#   "message": "Step 3 runs git but the skill never says a repo is required ... Fix: ..."}]
python3 scripts/review_skill.py <skill-folder> \
    --instruction-findings .skill-review/<skill-name>/instruction-findings.json \
    --json .skill-review/<skill-name>/findings.json   # 'python' on Windows
```

Each item needs `severity` (MAJOR or MINOR), a `message` (problem + where + why +
**Fix:**), an optional `dimension` (a scored dimension - quality / triggering /
structure / security; default quality), and a distinct `check` slug (auto-prefixed
`instruction:`).

**Then write the report from that unified JSON**, following
`references/report-template.md` exactly: assign each finding a severity (Blocker /
Major / Review / Minor) and a concrete fix, and give a per-dimension verdict.
Instruction-review findings are **mandatory fixes**: while any is open the overall
verdict is at best **Pass with fixes**, never a clean **Pass** - a skill is not
production-grade until they are resolved. End with one overall verdict: **Pass**,
**Pass with fixes**, or **Fail**. Save the report to
`.skill-review/<skill-name>/report.md`, tell the person where it is, and hand the
unified `findings.json` to skill-fixer.

## Output

The review writes everything under `.skill-review/<skill-name>/`:
- `report.md` — the human-readable review report, built from `references/report-template.md`: each finding with a severity (Blocker / Major / Review / Minor) and a concrete fix, a per-dimension verdict, and one overall verdict (**Pass**, **Pass with fixes**, or **Fail**).
- `findings.json` — the unified machine-readable findings (consumed by skill-fixer).
- `instruction-findings.json` — your authored instruction-review findings.

Tell the person where the report is. Instruction-review findings are mandatory fixes: while any is open, the overall verdict is at best **Pass with fixes**, never a clean **Pass**.

## Severity guidance

- **Blocker**: would fail upload or is a genuine security risk (spec violations,
  hardcoded secrets, unexplained data exfiltration, destructive commands).
- **Major**: materially hurts reliability or trust - a weak triggering description,
  a bloated body, a non-compiling script, a name collision with a bundled skill, or
  a serious instruction defect (a contradiction, a missing step, a misdirecting
  instruction, an unmet promise, an unspecified output format). Instruction defects
  are mandatory fixes, not advice.
- **Review**: an unconfirmed flag to judge in context (a scanned network/exec
  pattern). Resolve each as justified-by-purpose or escalate it.
- **Minor**: polish or a smaller instruction issue (missing TOC, name/folder
  mismatch, dangling reference, undisclosed dependency, a mildly ambiguous or
  redundant instruction). Still a required fix, just lower impact.
- **Advice**: a *script pointer* for the instruction review - a mechanical hit
  (vague term, long section) you confirm and promote to a finding or discard. It is
  a lead, not a defect, and not itself a verdict input.

## Example

Input: "Can you review the skill in ./changelog-gen?"

1. `mkdir -p .skill-review/changelog-gen`, then run `review_skill.py ./changelog-gen
   --json .skill-review/changelog-gen/findings.json`.
2. Read its `SKILL.md` and its `scripts/build.py`.
3. Produce `.skill-review/changelog-gen/report.md` using the template, e.g. verdict
   "Pass with fixes" with one Major instruction finding (step 3 runs git but the
   skill never states a repo is required - a gap that would misdirect the model),
   plus a Major weak-description finding and two Minor findings.
