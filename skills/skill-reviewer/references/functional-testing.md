# Deeper Testing (Claude Code only)

Two optional, higher-cost steps that go beyond static review. Both run only in
Claude Code, because they need the `claude` CLI and/or subagents. They cost model
calls, so reserve them for skills that matter. Never invent numbers: if a step
can't run, say so and rely on the static review plus qualitative reasoning.

## Contents

- [A. Measured trigger rate (delegated to skill-creator)](#a-measured-trigger-rate)
- [B. Functional test harness (subagents)](#b-functional-test-harness)

## A. Measured trigger rate

skill-reviewer does not re-implement the trigger-rate runner. The detection of
whether a skill fired depends on the current `claude` CLI stream-event schema, and
skill-creator already maintains that logic. Delegate to it.

1. Build and validate the eval set (see the main SKILL.md triggering step), saving
   it to a JSON file, e.g. `/tmp/trigger-evals.json`.

2. Locate a skill-creator install:

   ```bash
   python3 scripts/find_skill_creator.py
   ```

   If it prints a path, use it as `$SC`. If it prints `NOT FOUND`, stop here:
   tell the user skill-creator is not installed, point them to it (it ships as an
   Anthropic example skill / plugin), and report the trigger rate as "not
   measured". Do not approximate a rate.

3. Run skill-creator's evaluator from its own directory (it imports its local
   `scripts` package, so the working directory must be `$SC`):

   ```bash
   cd "$SC" && python3 -m scripts.run_eval \
     --eval-set /tmp/trigger-evals.json \
     --skill-path <path/to/skill/under/review> \
     --runs-per-query 3 \
     --model <model-id-of-this-session>
   ```

   It prints JSON with per-query trigger rates and a passed/total summary. Use the
   session's own model id so the result matches what the user experiences.

4. For an optimization loop that proposes better descriptions, skill-creator also
   has `python3 -m scripts.run_loop` (same eval-set / skill-path arguments). Offer
   it only if the user wants the description rewritten, since it runs many
   iterations and costs more.

5. Fold the measured rate into the report's triggering section: overall pass rate,
   plus any should-trigger query under the threshold (a miss) or should-not query
   over it (a false fire). Those are the concrete description fixes.

## B. Functional test harness

This checks the skill actually produces good output, not just that it triggers. It
uses subagents, which a script cannot spawn - this is a workflow you run.

1. Draft 2-3 realistic task prompts the skill is meant to handle, plus, for each, a
   few objectively checkable assertions (e.g. "output is valid JSON", "file
   contains a totals row"). Subjective qualities (tone, design) are judged by
   reading, not asserted.

2. For each prompt, spawn a subagent that has the skill available and runs the
   task, saving its outputs to a known directory. Optionally spawn a baseline
   subagent without the skill, to show the skill's marginal value. Launch them in
   the same turn so they finish together.

3. Grade each output against its assertions. For anything checkable by code, write
   and run a small script rather than eyeballing. If skill-creator is installed,
   its `agents/grader.md` describes a consistent grading rubric you can follow.

4. Capture each run's token count and duration (they arrive in the subagent
   completion notification) so the report can note cost, which matters for skills
   run at scale.

5. Fold results into the report: per-prompt pass/fail on assertions, notable output
   problems, and the cost delta vs baseline. This is qualitative-heavy; let the
   user review the actual outputs before you finalize a verdict.
