---
name: edd
description: "INVOKE THIS SKILL whenever the user is about to start a new feature, refactor existing code, change a prompt, modify an agent/node, or otherwise alter behavior whose quality is hard to assert with a binary unit test. EDD (Evaluation-Driven Development) is the eval-first counterpart to TDD: define success criteria and evaluators BEFORE writing code, baseline the current behavior, then iterate against measurable scores. Triggers on phrases like 'building X', 'refactoring Y', 'improving the prompt for Z', 'new node', 'new feature', 'how should I approach this', 'starting work on…', 'change the LLM behavior'. Use even when the user doesn't say 'eval' — their LLM-shaped work almost certainly needs this. The skill starts with a triage step to decide whether EDD actually applies (deterministic glue code often doesn't), then guides the user through plan → dataset → evaluators → baseline → implement → iterate."
---

# Evaluation-Driven Development (EDD)

## What this skill is for

You are guiding the user through **Evaluation-Driven Development** — the practice of treating *evaluations* the way TDD treats *unit tests*: write them first, let them define "done," and use them to drive iteration.

EDD is the missing methodology for the LLM era. TDD assumes deterministic outputs where a single assertion is meaningful. Modern features — agent decisions, prompt outputs, retrieval rankings, classification calls — produce graded, often subjective results where one assertion is brittle and ten assertions across a curated dataset is the right unit of confidence.

Your job is to:
1. Decide *whether* EDD applies to the user's task (Stage 0 — triage).
2. If it does, walk them through the EDD lifecycle, producing concrete artifacts at each stage.
3. Stay flexible — if the user is already mid-flow, drop them into the right stage.

## How EDD differs from TDD

| | TDD | EDD |
|---|---|---|
| Unit of confidence | One assertion per behavior | A dataset of N examples scored by evaluators |
| Pass criterion | Binary (green/red) | Graded (score, often per-dimension) |
| Output type | Deterministic | Often non-deterministic / subjective |
| Failure mode | "This case is wrong" | "We regressed from 0.82 → 0.74" |
| Refactor signal | Tests still green | Score stable or better, no per-example regressions |
| What you write first | A failing test | A dataset + an evaluator that *can score* the current system |

Use the table when the user is unsure whether to "just write tests" or do EDD. The honest answer is usually **both**: TDD for the deterministic glue, EDD for the LLM-shaped core.

## Stage 0 — Triage: does EDD apply?

Before you do anything else, decide. Ask yourself (or the user) these questions in order. If you reach a "yes" you have your answer.

1. **Does this feature involve an LLM call, agent decision, retrieval, ranking, classification, or generation?** → Yes ⇒ EDD applies.
2. **Is the "right answer" subjective, multi-valued, or graded rather than binary?** (e.g., "is this summary good?", "is this rubric score fair?") → Yes ⇒ EDD applies.
3. **Will the same input plausibly produce different outputs across runs?** → Yes ⇒ EDD applies.
4. **Is there an existing prompt or model behavior whose change could silently regress quality?** → Yes ⇒ EDD applies — even for "small" prompt edits.
5. **Is this pure deterministic code (helpers, glue, schema changes, type fixes, dependency bumps)?** → Likely no ⇒ stick with TDD or just ship it. EDD is overhead here.

When the answer is "no," say so plainly: *"This looks like deterministic code — EDD is overhead. Use a unit test or just ship it."* Don't force the methodology onto features that don't need it. Credibility comes from knowing when to step back.

For mixed cases (deterministic pre/post-processing wrapping an LLM call): apply EDD to the LLM part, TDD to the deterministic part. Don't try to evaluate the whole thing as one black box if you can separate the seams.

## The EDD lifecycle

Once triage says EDD applies, walk through these stages. The user can be at any stage when they arrive — figure out where they are first.

```
Stage 1: Define success     → produces an EDD Plan doc
Stage 2: Build the dataset  → produces a golden set of N examples
Stage 3: Write evaluators   → produces evaluator code/spec
Stage 4: Baseline           → produces a recorded "before" score
Stage 5: Implement & iterate → produces working code + score deltas
Stage 6: Lock in            → adds eval to CI / standing regression check
```

You're not enforcing a linear march. If the user shows up at Stage 5 ("I built this, how do I know if it's better?") you skip back to Stages 2–4 and explain you can't measure improvement without a baseline.

---

### Stage 1 — Define success

This is the most important stage. The reason EDD beats "I'll test it later" is that you forced yourself to define "good" before you had a chance to motivated-reason yourself into shipping something mediocre.

Interview the user. Ask:

- **What is the feature/change in one sentence?** (Forces specificity.)
- **What does a *good* output look like for this?** Get a concrete example.
- **What does a *bad* output look like?** Get a concrete example. Bad examples reveal what to evaluate.
- **What failure modes worry you most?** (E.g., hallucination, off-topic, too long, missing structure, wrong rubric score, biased.)
- **How will you know after shipping that it's working in production?** This is sometimes a separate metric — keep it in mind but don't conflate with the offline eval.
- **What is the input distribution?** Synthetic? Real production logs? A handful of demo cases? The dataset has to match the production distribution or you're evaluating the wrong thing.

Produce an **EDD Plan** — a short markdown doc (10–30 lines) the user can paste into a PR description or RFC. Template:

```markdown
# EDD Plan: <feature name>

## What we're building
<one sentence>

## What "good" looks like
- <criterion 1>
- <criterion 2>

## Failure modes to evaluate
- <failure mode 1> → evaluator: <structural / LLM-judge / programmatic>
- <failure mode 2> → evaluator: <...>

## Dataset
- Source: <production logs / hand-curated / synthetic>
- Size: <N examples>
- Coverage: <happy path / edge cases / known failures>

## Baseline
- Current system score on this dataset: <to be measured>

## Success criterion for this change
- <e.g., overall score ≥ baseline + 5pp, no per-example regression on critical cases>
```

The plan is short on purpose. EDD plans that turn into 5-page RFCs die. The plan exists so a teammate (or future-you) can answer "did this change improve things?" without ambiguity.

If the user asks, produce the plan as an actual file (e.g., `docs/edd-plans/<feature>.md` or wherever the repo keeps decision docs). Otherwise, paste it into the conversation and let them decide where it lives.

---

### Stage 2 — Build the dataset

The dataset is the artifact that *defines* the feature. Spend time here.

**Principles:**

- **Small and curated beats large and noisy.** 10–30 hand-picked examples will tell you more than 1000 synthetic ones. You can grow later.
- **Include three buckets**: happy path (the obvious cases), edge cases (long inputs, empty fields, weird Unicode, multilingual), and known failures (cases where the current system is wrong — these are gold because they prove the eval can detect regressions).
- **Real data beats invented data** wherever possible. Pull from production logs, support tickets, actual user inputs. Synthetic data masks failure modes that only appear in the wild.
- **Each example has a label** — but the label format depends on the evaluator. For LLM-judge: maybe just an input. For structural: input + expected fields. For pairwise comparison: input + reference output. Don't over-label up front.
- **Version the dataset.** Once it's in use, treat it like code. A change to the dataset is a change to "what we mean by good" and should be a deliberate decision, not a drive-by edit.

**Format:** JSON or JSONL is usually right. Each entry has `id`, `input`, optional `expected`, optional `metadata` (tags like `bucket: edge_case`, `priority: critical`).

```json
{"id": "interview-001", "input": {...}, "expected": "...", "metadata": {"bucket": "happy_path", "priority": "high"}}
```

When the user asks, produce a starter `dataset.json` (or `.jsonl`) with placeholder entries shaped correctly, plus 1–2 filled-in examples to anchor the format. Then nudge them to add real examples — the model can sketch, but the user has the production knowledge that makes the dataset valuable.

If the user has access to production traces (LangSmith, Phoenix, custom logs), suggest pulling from there. Real distributions reveal the long tail.

---

### Stage 3 — Write evaluators

An evaluator is a function that takes a (run output, optionally expected output) and returns a score. The single biggest EDD mistake is making the evaluator too coarse: one global "is it good?" score is hard to interpret. Build several narrow evaluators instead, each tied to a failure mode from the EDD plan.

**Four evaluator types — use a mix:**

1. **Structural / programmatic** — Cheap, deterministic, fast. Examples: "output is valid JSON", "all required fields present", "length within bounds", "no `<PICKLED_OBJECT>` markers", "schema matches". Use these heavily. They catch the boring failures before LLM judges waste tokens.

2. **LLM-as-judge** — Score subjective qualities a regex can't catch: relevance, factuality, tone, completeness. Two warnings: (a) the judge is itself fallible; calibrate it on known-good and known-bad outputs before trusting it; (b) judges drift. Pin the judge model and prompt in the eval config.

3. **Reference-based / similarity** — When you have an "expected" output: exact match, embedding cosine similarity, ROUGE/BLEU for text, set-overlap for lists. Useful when there's a ground truth.

4. **Human spot-check** — Don't pretend you can fully automate. For the most important examples (e.g., the "critical priority" bucket), the team eyeballs the output. Build the tooling to make this easy — a simple HTML diff is enough.

**Per-failure-mode mapping:**

- Failure: "summary hallucinates facts" → LLM judge prompted to fact-check against source.
- Failure: "JSON malformed" → structural validator.
- Failure: "answer is off-topic" → LLM judge for relevance.
- Failure: "response too long" → structural length check.
- Failure: "ranking puts the wrong item first" → top-1 accuracy against labeled ranking.

Don't write evaluators that always pass — they tell you nothing. Test each evaluator on a known-bad output and verify it fires. An evaluator that has never failed has never been validated.

When the user asks, scaffold an evaluator file. Keep evaluators colocated with the dataset (e.g., `evals/<feature>/evaluators.py`). Each evaluator gets a descriptive name (`evaluator_no_hallucinated_facts`, not `evaluator_2`) — the name shows up in eval reports and matters more than you'd think.

---

### Stage 4 — Baseline

You cannot claim improvement without a baseline. Run the *current* system (or, if this is a greenfield feature, a trivial baseline like "return empty string" or "return a random choice") against the dataset, with the evaluators you wrote, and **record the score.**

This number is the floor. Anything you ship later is measured against it.

The baseline run also surfaces problems early:
- "The evaluator scored 1.0 on every example" → the evaluator is too lenient or broken.
- "The evaluator scored 0.0 on every example" → the evaluator is mis-calibrated or the dataset is malformed.
- "The current system is way better than I thought" → maybe the feature isn't needed.
- "The current system is way worse than I thought" → urgency just changed.

Save the baseline somewhere durable (a file in the repo, an entry in LangSmith, a row in a doc). Future-you needs to compare against it without ambiguity about which baseline was the baseline.

---

### Stage 5 — Implement and iterate

Now write the code. The eval loop becomes your inner loop:

1. Make a change.
2. Run the eval against the dataset.
3. Read the score and the per-example breakdown.
4. Decide: was the score change real, or noise? (For LLM-judge evals, repeat the run 2–3 times to estimate variance.)
5. If the score went up, keep going. If it went down or stayed flat, look at the *examples that changed*. Sometimes the new failures reveal a different problem.
6. **Crucially — sometimes the eval is wrong, not the code.** If the new output looks better to you than the old output but the score dropped, the evaluator may be measuring the wrong thing. Fix the evaluator (and add the case to your "evaluator validation" set so you don't break it again).

Track per-example deltas, not just the aggregate score. Aggregate scores hide regressions: an overall improvement of +3pp might still mean two critical examples regressed while five low-priority ones improved.

Encourage the user to commit the dataset, evaluator, and any baseline runs alongside the feature code. EDD evidence belongs in the PR.

---

### Stage 6 — Lock in

A change that improves the eval today can silently regress next month when someone tweaks the prompt for an unrelated reason. Make the eval a standing check:

- **Pin** the dataset version, evaluator prompts, and judge model.
- **Run** the eval in CI or on a schedule. A PR that drops the score should require an explicit acknowledgment ("yes, we're accepting this regression because…").
- **Expand** the dataset over time as new failure modes are found in production. Each production bug = one new dataset example + a note on which evaluator should catch it.
- **Revisit** the evaluators periodically. LLM judges drift as the underlying model evolves. Recalibrate on the known-good / known-bad set.

This stage is where EDD pays off long-term. Without it, the discipline you applied today erodes.

---

## Anti-patterns to call out

If you see the user doing any of these, gently course-correct.

- **Writing the eval after shipping** — defeats the entire point. EDD is *eval-first*.
- **Single-score "quality" evaluator** — can't diagnose what regressed. Break into per-failure-mode evaluators.
- **Synthetic dataset that doesn't match production** — gives false confidence. Pull real examples or label your dataset as exploratory.
- **No baseline** — "the new version scores 0.78" is meaningless without "the old version scored 0.71."
- **LLM-judge for things a regex can check** — wasteful and flakier than a structural check.
- **Evaluator that always passes** — never run a regression; you have no evidence it works.
- **Treating eval scores as ground truth** — they're a signal, not a verdict. Spot-check critical examples.
- **Letting the dataset rot** — production fails in new ways; the dataset has to grow.

---

## How this skill cooperates with related skills

You are the methodology layer. Execution is delegated:

- For *writing evaluator code* against LangSmith → invoke or refer to `langsmith-evaluator`.
- For *running an eval dataset* against the current branch → invoke or refer to `run-eval`.
- For *generating LLM-judge prompts* → the user's prompt-engineering skill of choice.

Don't reimplement those. Your job is to make sure the user has thought through *why* they're evaluating, *what* counts as good, *which* examples matter, and *how* they'll know they improved — then hand off to the execution skills.

---

## How to behave when this skill triggers

1. **Greet briefly and triage.** One short paragraph: "Sounds like a good candidate for EDD. Quick triage first — is this LLM-shaped or pure deterministic code?" Don't lecture. If the user is clearly mid-flow, skip triage.

2. **Find the user's current stage.** Ask one question if needed: "Have you defined what 'good' looks like for this? Built a dataset? Have a baseline?" Their answer tells you where to enter.

3. **Run that stage's interview.** Produce the artifact (plan, dataset starter, evaluator scaffold) if it adds value. Don't produce artifacts the user didn't ask for and won't use.

4. **Stop when the user has what they need.** EDD is a workflow, not a ceremony. If they say "I just wanted to know what EDD was, thanks," that's a successful invocation. Don't drag them through six stages they didn't ask for.

5. **Be honest when EDD doesn't fit.** A bug fix, a typo, a dependency bump — these don't need EDD. Saying so makes the skill trustworthy for the cases that do.
