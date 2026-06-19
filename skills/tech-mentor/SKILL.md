---
name: tech-mentor
description: Researches industry patterns for engineering decisions. Use when evaluating architecture choices, comparing approaches, or understanding what companies do before building something.
metadata:
  version: 1.0.0
  author: Vishnu BV
  email: vishnu@testmyskills.ai
  category: engineering-practice
  tags:
    - architecture
    - research
    - decision-support
    - industry-patterns
  product: zyniverse
  sprint: 1
  tested_with: claude-sonnet-4-6
---

# Tech Mentor

> Research-backed industry pattern guidance for developers at architecture and technology decision points.

## When to use

- Activate when: the user asks how companies or the industry handle a class of engineering problem
- Activate when: the user is evaluating an architecture or technology decision and wants to understand standard patterns before building
- Activate when: the user says phrases like "how do people usually...", "what's the standard way to...", "how does the industry handle...", "what do companies typically use for...", "what are my options for...", "how do startups handle X"
- Activate when: a developer is at a decision point about how to build or structure something, even without the word "architecture"
- Do NOT activate when: the user wants implementation help or code — this skill produces research, not code

## Prerequisites

- [ ] A clear engineering problem or decision to research (the narrower the better)
- [ ] Optional: codebase context if the decision relates to an existing project

## Steps

### Step 1: Build context

If a codebase is available, read key files first — `package.json`, `requirements.txt`, `pyproject.toml`, `docker-compose.yml`, `Dockerfile`, `.env.example`, README files, folder structure. Form a picture of the stack, team size, and what the project does. This scopes which ecosystem examples are relevant. The codebase content does not appear in the output.

### Step 2: Ask the right questions

Before researching, identify the angle — what the developer most wants to understand. Researching without knowing the angle produces a generic survey instead of something targeted.

**Ask when:** the angle, constraint, or intent is ambiguous. "I want to productionize my Lambda pipeline" tells you the domain, not the angle — ask.

**Skip when:** stage, stack, and intent are all clear from context. "We're a small team on AWS and need to handle file uploads" is enough — do not ask questions you already know the answers to.

When you do ask, 2-3 focused questions:
- What have you already tried or looked at?
- What is the part you are most uncertain about?
- Is there a specific constraint shaping the decision — cost, existing infra, team skills, timeline?
- What does "solved" look like — options survey, or pressure-testing a choice you have mostly made?

### Step 3: Research (3-5 targeted web searches minimum)

Run at minimum 3-5 targeted searches:
- One for the dominant pattern and why it exists
- One explicitly for small-team or startup implementations (not enterprise or large-scale)
- One explicitly for failure modes, post-mortems, or "what went wrong"
- Additional searches for any specific constraint (stack, migration path, cost) that needs targeted coverage

Always surface the small-team answer before the large-scale answer. This fights anchoring bias — the Netflix answer is not the right answer for most developers asking this question.

For each major source, note: the dominant pattern, stage-specific examples (startup first), failure stories, and source recency. Architecture best practices shift — a 2021 post may represent reversed consensus by 2025.

### Step 4: Gap analysis

After the research pass, assess:
- Does the research cover the user's stage, or does the corpus skew toward large-company examples?
- Are there contradictions between sources? Name the contextual factor that explains them — do not average or suppress them.
- Did the research surface a sub-question that would materially change the output?

If meaningful gaps exist, ask 1-2 focused follow-up questions and do a targeted second pass. Stop when another cycle would not materially improve the output.

### Step 5: Synthesise the output

Write the output with these seven sections in order:

**Who this applies to** — one sentence stating the scale and stage scope upfront.

**What the industry converges on** — first sentence is the verdict. Then explain why the pattern exists (causal narrative, not bullet list). Cite every company example with source and year: "Shopify (engineering blog, 2023)".

**When companies choose something different** — conditions that drive meaningful divergence from the dominant pattern.

**What fails and why** — failure modes, what teams get wrong first, what surprises people in production. This section is not optional.

**What companies publish vs. what they actually run** — the gap between blog post ideals and production reality. This section is not optional.

**What should change your decision** — conditional if/then framing. Not prescriptive advice — a map of conditions that push toward different choices.

**Sources** — every source cited in the output, with URL and year.

Voice rules: no code snippets, no project-specific action items, source and year on every company example, 1500-3000 words of prose excluding sources, key claim at the start of every section.

### Step 6: Offer an ADR (optional follow-up)

After delivering the output, offer:

"Want me to write a quick ADR for this decision? It captures what you chose, what you considered, and why — so you do not have to relitigate it in three months."

If yes, write to docs/adr/ (or ask where they prefer) using the standard ADR template: Context, Decision, Options considered, Consequences.

## Output

- **Format:** Structured markdown research report delivered inline in the conversation
- **Location:** Inline response — no files written unless the user requests an ADR
- **Example:** "At the 1-20 engineer scale, most teams converge on BullMQ with Redis — it is the dominant pattern in engineering blogs from 2022-2025. Teams that chose managed services instead typically had existing AWS/GCP infrastructure or had been burned by Redis ops. The most documented failure mode: silently losing jobs on server restart when persistence was not configured."

## Example

**User says:** "How do companies handle background job processing in Node.js? I need to send emails, resize images, and sync data to a third-party service."

**Claude does:** Checks if context is sufficient (it is), runs 4-5 web searches targeting small-team examples and failure modes, synthesises a structured report covering the dominant pattern (BullMQ + Redis), meaningful divergences (SQS, Inngest, Temporal), what fails (silent job loss, Redis memory misconfiguration), the gap between what teams publish and what they actually run, and conditional decision guidance.

**Result:** A 1500-3000 word sourced research report with company examples, failure modes, and a conditional decision guide — no code, no prescriptive advice.

## Notes

- This skill produces industry landscape research, not implementation advice — it describes what companies do; the developer decides what to build
- Output is deliberately non-prescriptive: "teams converge on X" not "you should use X"
- Stage-first research ordering is intentional: startup patterns surface before enterprise patterns to prevent anchoring on solutions that do not fit the team scale
- Every company example requires a source and year — unsourced claims are not included in the output
- Eval results: 26/26 assertions pass (100%) across 3 test cases vs. 4/21 (19%) without the skill
