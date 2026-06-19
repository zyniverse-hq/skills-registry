# Instruction Review (LLM-as-judge)

This is the core of a skill review and the part a static checker cannot do. A skill
is a prompt: its value depends on whether its instructions are clear, complete,
consistent, and actually steer the model to the right behavior. Read the SKILL.md
and every reference as if you had to execute them with no other context, and judge
the instructions as an expert.

Everything you surface here is a **finding**, not a suggestion. Rate each Major or
Minor by impact, pair it with a concrete fix, and treat it as mandatory - a skill is
not production-grade while any is open. The static checker's ADVICE rows are only
*pointers*: leads to inspect, then confirm and promote to a finding or discard.

## Contents

- [Lenses to apply](#lenses-to-apply)
- [Severity](#severity)
- [How to write each finding](#how-to-write-each-finding)
- [Recording findings for handoff](#recording-findings-for-handoff)

## Lenses to apply

Read with each of these in mind; each is a common source of real instruction defects.

- **Gaps / completeness.** Missing steps, unstated preconditions (e.g. "assumes a git
  repo", "assumes the CSV has a header row"), inputs the workflow implies but never
  handles, and "what happens when this fails?" left unanswered.
- **Ambiguity / under-specification.** Steps a reader could execute two different
  ways; undefined terms; success criteria that can't be checked; "handle it" with no
  definition of how.
- **Contradictions / inconsistency.** The description promises X but the body does Y;
  step 3 contradicts step 6; an example violates a stated rule; a threshold, name, or
  default given two different values in two places.
- **Misdirection / correctness.** Guidance that would lead the model to the wrong
  action, a default that defeats the stated goal, or a recommended step that does not
  actually achieve what the surrounding text claims.
- **Output contract.** If the skill produces output, is the format fully specified,
  with edge cases (empty input, partial data, errors) covered - or only the happy
  path?
- **Coherence with the promise.** Does the body deliver what the description claims -
  no more, no less? Scope creep and unmet promises are both findings.
- **Redundancy / dead instructions.** Steps that can never apply, guidance repeated in
  conflicting words, or instruction that adds nothing but context cost.
- **Structure / progressive disclosure.** Is the body genuinely lean, or is there
  reference-worthy detail - long tables, exhaustive option lists, worked examples,
  edge-case catalogues - that belongs in a `references/` file loaded only when needed?
  Is there a deterministic, repeated procedure the model is told to reconstruct each
  run that would be more reliable bundled as a `script`? The static checker flags body
  size by line/token count alone; that is a size signal, not a verdict. Your job is the
  judgement it can't make: confirm the detail is *actually* movable (vs. all-essential
  procedure that must stay inline to steer the model) before raising it, and name what
  goes where. Relocating is not cutting - if the detail is dead weight it is a
  Redundancy finding instead. File these as `dimension: structure`.
- **Triggering reasoning.** Beyond the cue regex: would the description actually fire
  on the real phrasings a user types, and stay quiet on near-misses? Reason through
  the eval set (see SKILL.md) and record concrete description fixes.

## Severity

- **Major** - would cause wrong or unreliable behavior: a contradiction, a missing
  step, a misdirecting instruction, an unmet promise, an unspecified output format.
- **Minor** - degrades clarity or consistency but the model would likely still
  succeed: a mildly ambiguous phrasing, a redundant step, a vague heading.

Both are mandatory fixes. The split is impact, not whether to fix.

## How to write each finding

State the problem, *where* it is (file + section/step), *why* it bites (what the
model would get wrong), and the concrete fix. Quote the offending instruction.

Example:

> **[instruction] Step 3 assumes a git repo** - `prepare.py` runs with no check that
> the folder is a repository, and the description never says one is required; on a
> non-repo it fails opaquely. **Fix:** state the precondition in the description and
> have step 3 verify it (or fall back gracefully) before running.

## Recording findings for handoff

These findings are authored by you, not the static script, so they must be written
back into the review JSON or skill-fixer (which reads that JSON) never sees them.
Write a JSON array - one object per finding - and fold it in by re-running the
checker with `--instruction-findings` (see SKILL.md step 4):

```json
[
  {"dimension": "quality", "severity": "MAJOR",
   "check": "instruction:step3-precondition",
   "message": "Step 3 runs git but the skill never states a repo is required; on a non-repo it fails opaquely. Fix: declare the precondition and verify it in step 3."},
  {"dimension": "triggering", "severity": "MINOR",
   "check": "instruction:desc-scope",
   "message": "Description implies it handles JSON too, but the body only covers CSV. Fix: narrow the description or add JSON handling."}
]
```

- `severity` is MAJOR or MINOR (never advisory) - required.
- `message` states the problem, where it is, why it bites, and the **Fix:** - required.
- `dimension` is a scored dimension (quality / triggering / structure / security),
  default `quality`, so the finding penalizes the right axis.
- `check` is a short distinct slug, auto-prefixed `instruction:`; give each finding
  its own so they aren't merged by the per-check score cap.

Once folded in, they count toward the gate, counts, and score, and route to
skill-fixer's draft bucket like any Major/Minor finding.
