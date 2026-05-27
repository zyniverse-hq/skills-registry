---
name: edd
description: "INVOKE THIS SKILL whenever the user is about to start a new feature, refactor existing code, change a prompt, modify an agent/node, or otherwise alter behavior whose quality is hard to assert with a binary unit test. EDD (Evaluation-Driven Development) is the eval-first counterpart to TDD: define success criteria and evaluators BEFORE writing code, baseline the current behavior, then iterate against measurable scores. Triggers on phrases like 'building X', 'refactoring Y', 'improving the prompt for Z', 'new node', 'new feature', 'how should I approach this', 'starting work on…', 'change the LLM behavior'. Use even when the user doesn't say 'eval' — their LLM-shaped work almost certainly needs this. The skill starts with a triage step to decide whether EDD actually applies (deterministic glue code often doesn't), then guides the user through plan → dataset → evaluators → baseline → implement → iterate."
version: 1.0.0
author: Sharath S Rao
email: sharath.rao@zysk.tech
category: engineering-practice
tags:
  - eval
  - tdd
  - llm-evaluation
  - development-practice
product: tms
sprint: 1
tested_with: claude-sonnet-4-6
---

# Evaluation-Driven Development (EDD)

> Eval-first development methodology for LLM-shaped features — define success criteria and evaluators before writing code, then iterate against measurable scores.

## When to use

- Activate when: the user is building or changing a feature that involves an LLM call, agent decision, retrieval, ranking, classification, or generation
- Activate when: the user says "building X", "refactoring Y", "improving the prompt for Z", "new node", "new feature", "starting work on…", or "change the LLM behavior"
- Activate when: the quality of the output is subjective, multi-valued, or graded rather than binary
- Activate when: an existing prompt or model behavior is being changed and could silently regress quality
- Do NOT activate when: the task is pure deterministic code (helpers, glue, schema changes, type fixes, dependency bumps) — EDD is overhead here; use TDD instead

## Prerequisites

- [ ] User has a concrete feature, prompt, or agent node in mind to evaluate
- [ ] Access to a dataset source (production logs, support tickets, or ability to create synthetic examples)
- [ ] Optionally: access to LangSmith, Phoenix, or custom tracing for pulling real production examples

## Steps

### Step 1: Triage — does EDD apply?

Before doing anything else, decide. Ask yourself (or the user) these questions in order. If you reach a "yes" you have your answer.

1. **Does this feature involve an LLM call, agent decision, retrieval, ranking, classification, or generation?** → Yes ⇒ EDD applies.
2. **Is the "right answer" subjective, multi-valued, or graded rather than binary?** → Yes ⇒ EDD applies.
3. **Will the same input plausibly produce different outputs across runs?** → Yes ⇒ EDD applies.
4. **Is there an existing prompt or model behavior whose change could silently regress quality?** → Yes ⇒ EDD applies — even for "small" prompt edits.
5. **Is this pure deterministic code (helpers, glue, schema changes, type fixes, dependency bumps)?** → Likely no ⇒ stick with TDD or just ship it.

When the answer is "no," say so plainly: *"This looks like deterministic code — EDD is overhead. Use a unit test or just ship it."*

For mixed cases (deterministic pre/post-processing wrapping an LLM call): apply EDD to the LLM part, TDD to the deterministic part.

### Step 2: Define success (EDD Plan)

This is the most important stage. Interview the user:

- **What is the feature/change in one sentence?**
- **What does a *good* output look like for this?** Get a concrete example.
- **What does a *bad* output look like?** Bad examples reveal what to evaluate.
- **What failure modes worry you most?** (E.g., hallucination, off-topic, too long, missing structure.)
- **How will you know after shipping that it's working in production?**
- **What is the input distribution?** Synthetic? Real production logs? A handful of demo cases?

Produce an **EDD Plan** — a short markdown doc (10–30 lines):

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

If the user asks, produce the plan as an actual file (e.g., `docs/edd-plans/<feature>.md`).

### Step 3: Build the dataset

The dataset defines the feature. Spend time here.

**Principles:**
- **Small and curated beats large and noisy.** 10–30 hand-picked examples will tell you more than 1000 synthetic ones.
- **Include three buckets**: happy path, edge cases (long inputs, empty fields, weird Unicode, multilingual), and known failures.
- **Real data beats invented data** wherever possible — pull from production logs, support tickets, actual user inputs.
- **Version the dataset.** Once in use, treat it like code.

**Format:** JSON or JSONL. Each entry has `id`, `input`, optional `expected`, optional `metadata`.

```json
{"id": "001", "input": {...}, "expected": "...", "metadata": {"bucket": "happy_path", "priority": "high"}}
```

When the user asks, produce a starter `dataset.json` with placeholder entries and 1–2 filled-in examples. Then nudge them to add real examples. If they have production traces (LangSmith, Phoenix), suggest pulling from there.

### Step 4: Write evaluators

An evaluator takes a run output (and optionally expected output) and returns a score. Build several narrow evaluators, each tied to a failure mode from the EDD Plan.

**Four evaluator types — use a mix:**

1. **Structural / programmatic** — Cheap, deterministic, fast. Examples: "output is valid JSON", "all required fields present", "length within bounds". Use heavily — they catch boring failures before LLM judges waste tokens.
2. **LLM-as-judge** — Score subjective qualities a regex can't catch: relevance, factuality, tone, completeness. Pin the judge model and prompt in the eval config.
3. **Reference-based / similarity** — When you have an "expected" output: exact match, embedding cosine similarity, ROUGE/BLEU, set-overlap.
4. **Human spot-check** — For the most important examples, the team eyeballs the output. Build simple tooling (an HTML diff is enough).

**Per-failure-mode mapping:**
- "Summary hallucinates facts" → LLM judge prompted to fact-check against source
- "JSON malformed" → structural validator
- "Response too long" → structural length check
- "Ranking puts wrong item first" → top-1 accuracy against labeled ranking

Don't write evaluators that always pass — they tell you nothing. Test each on a known-bad output and verify it fires. Scaffold an evaluator file at `evals/<feature>/evaluators.py` with descriptive names (`evaluator_no_hallucinated_facts`, not `evaluator_2`).

### Step 5: Baseline the current system

Run the *current* system against the dataset with the evaluators you wrote and **record the score.**

This number is the floor. Anything shipped later is measured against it.

The baseline run also surfaces problems early:
- "The evaluator scored 1.0 on every example" → the evaluator is too lenient or broken
- "The evaluator scored 0.0 on every example" → mis-calibrated or the dataset is malformed
- "The current system is way better than I thought" → maybe the feature isn't needed

Save the baseline somewhere durable (a file in the repo, an entry in LangSmith, a row in a doc).

### Step 6: Implement and iterate

Now write the code. The eval loop becomes the inner loop:

1. Make a change.
2. Run the eval against the dataset.
3. Read the score and the per-example breakdown.
4. Decide: was the score change real, or noise? (For LLM-judge evals, repeat 2–3 times to estimate variance.)
5. If score went up, keep going. If down or flat, look at *which examples changed*.
6. **If the new output looks better but the score dropped — the evaluator may be wrong.** Fix the evaluator and add the case to your evaluator validation set.

Track per-example deltas, not just the aggregate score. Aggregate scores hide regressions: +3pp overall might still mean two critical examples regressed. Commit the dataset, evaluator, and baseline runs alongside the feature code.

### Step 7: Lock in (CI)

Make the eval a standing check:

- **Pin** the dataset version, evaluator prompts, and judge model.
- **Run** the eval in CI or on a schedule. A PR that drops the score should require explicit acknowledgment.
- **Expand** the dataset over time as new failure modes appear in production. Each production bug = one new dataset example.
- **Revisit** evaluators periodically — LLM judges drift as underlying models evolve. Recalibrate on the known-good / known-bad set.

## Output

- **Format:** EDD Plan (markdown), dataset (JSON/JSONL), evaluator code (Python), baseline score (recorded value)
- **Location:** `docs/edd-plans/<feature>.md`, `evals/<feature>/dataset.jsonl`, `evals/<feature>/evaluators.py`
- **Example:** A 15-line EDD Plan, 10–30 curated examples in JSONL, and 3–5 narrow evaluators each tied to a specific failure mode

## Example

**User says:** "I'm adding a summarization node to our pipeline — how do I approach this?"
**Claude does:** Triages (LLM-shaped → EDD applies), interviews user on success criteria and failure modes, produces an EDD Plan, guides through building a golden dataset and writing per-failure-mode evaluators, records a baseline score, then tracks score deltas during implementation.
**Result:** Measurable evidence of improvement committed alongside the feature code, and the eval locked into CI to catch future regressions.

## Notes

- EDD is overhead for deterministic code — say so plainly and step back; credibility comes from knowing when not to apply it
- Always check per-example deltas — aggregate scores can hide regressions in critical cases
- Test each evaluator on a known-bad output before trusting it; an evaluator that has never failed has never been validated
- For mixed tasks (deterministic wrapper around an LLM core), apply EDD to the LLM part and TDD to the wrapper — don't try to evaluate the whole thing as one black box
- LLM judges drift as underlying models evolve; pin the judge model and recalibrate periodically against known-good/bad examples
- EDD Plans that grow into 5-page RFCs die — keep the plan short (10–30 lines)

---

## Reference: How EDD differs from TDD

| | TDD | EDD |
|---|---|---|
| Unit of confidence | One assertion per behavior | A dataset of N examples scored by evaluators |
| Pass criterion | Binary (green/red) | Graded (score, often per-dimension) |
| Output type | Deterministic | Often non-deterministic / subjective |
| Failure mode | "This case is wrong" | "We regressed from 0.82 → 0.74" |
| Refactor signal | Tests still green | Score stable or better, no per-example regressions |
| What you write first | A failing test | A dataset + an evaluator that *can score* the current system |

The honest answer for most LLM features is **both**: TDD for the deterministic glue, EDD for the LLM-shaped core.

## Reference: Anti-patterns to call out

If the user does any of these, gently course-correct:

- **Writing the eval after shipping** — defeats the entire point; EDD is *eval-first*
- **Single-score "quality" evaluator** — can't diagnose what regressed; break into per-failure-mode evaluators
- **Synthetic dataset that doesn't match production** — gives false confidence; pull real examples or label as exploratory
- **No baseline** — "the new version scores 0.78" is meaningless without knowing the old score
- **LLM-judge for things a regex can check** — wasteful and flakier than a structural check
- **Evaluator that always passes** — you have no evidence it works; test it against a known-bad output
- **Treating eval scores as ground truth** — they're a signal, not a verdict; spot-check critical examples
- **Letting the dataset rot** — production fails in new ways; the dataset has to grow

## Reference: Cooperating skills

You are the methodology layer. Execution is delegated:

- For *writing evaluator code* against LangSmith → invoke or refer to `langsmith-evaluator`
- For *running an eval dataset* against the current branch → invoke or refer to `run-eval`
- For *generating LLM-judge prompts* → the user's prompt-engineering skill of choice

Don't reimplement those. Your job is to make sure the user has thought through *why* they're evaluating, *what* counts as good, *which* examples matter, and *how* they'll know they improved.

## Reference: How to behave when this skill triggers

1. **Greet briefly and triage.** One short paragraph: "Sounds like a good candidate for EDD. Quick triage first — is this LLM-shaped or pure deterministic code?" Don't lecture. If the user is clearly mid-flow, skip triage.
2. **Find the user's current stage.** Ask one question if needed: "Have you defined what 'good' looks like? Built a dataset? Have a baseline?" Their answer tells you where to enter.
3. **Run that stage's interview.** Produce the artifact (plan, dataset starter, evaluator scaffold) if it adds value. Don't produce artifacts the user didn't ask for and won't use.
4. **Stop when the user has what they need.** EDD is a workflow, not a ceremony. If they say "I just wanted to know what EDD was, thanks," that's a successful invocation.
5. **Be honest when EDD doesn't fit.** A bug fix, a typo, a dependency bump — these don't need EDD. Saying so makes the skill trustworthy for the cases that do.
