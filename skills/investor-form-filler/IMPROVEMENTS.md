# IMPROVEMENTS — investor-form-filler

> Improvement plan derived from SKILL.md + ANALYSIS.md audit against the agentskills.openml.io spec.

---

## Quick Summary

| | Before | After |
|---|---|---|
| Spec compliance | Partially compliant | Fully compliant |
| Critical violations | 3 | 0 |
| Agent discoverability | Medium | High |
| Portability | Partial | Pass |

---

## Improvement 1 — Nest Non-Standard Frontmatter Fields Under `metadata:`

### What needs to change

Eight non-standard fields (`version`, `author`, `email`, `category`, `tags`, `product`, `sprint`, `tested_with`) are placed at the top level of the frontmatter. The agentskills.io spec requires all non-standard fields to be nested under a `metadata:` block. This is a structural violation that will cause parsers and registry tooling to reject or misread the skill manifest.

### Before
```yaml
---
name: investor-form-filler
description: Fill investor application forms (VC, accelerator, grant) from a single facts file, tuned per investor type, with sensitive financials kept behind an explicit gate.
version: 1.0.0
author: Sarang T S
email: sarang@testmyskills.ai
category: business-sales
tags:
  - investor-forms
  - fundraising
  - applications
  - sales-automation
  - pre-seed
product: zyniverse
sprint: 1
tested_with: claude-opus-4-7
---
```

### After
```yaml
---
name: investor-form-filler
description: Fill investor application forms (VC, accelerator, grant) from a single facts file, tuned per investor type, with sensitive financials kept behind an explicit gate.
license: MIT
compatibility: Requires WebSearch and WebFetch tool access. Expects company-facts.md at the project root. Optional scripts/match_question.py and scripts/check_consistency.py require Python 3.8+ (stdlib only).
metadata:
  version: 1.0.0
  author: Sarang T S
  email: sarang@testmyskills.ai
  category: business-sales
  tags:
    - investor-forms
    - fundraising
    - applications
    - sales-automation
    - pre-seed
  product: zyniverse
  sprint: 1
  tested_with: claude-opus-4-7
---
```

### Impact if implemented
- **Agent behaviour:** Registry parsers can now correctly distinguish spec-defined fields from skill-specific metadata. Tooling that reads `version`, `author`, or `tags` will find them in the expected location.
- **Discoverability:** Tag-based search (`investor-forms`, `fundraising`, `applications`) only works if tags are under `metadata:` — the registry indexes them from that path. Moving them unlocks tag-based routing.
- **Portability:** Other teams importing this skill into their own registries will not get parse errors or schema validation failures.
- **Risk reduced:** Prevents silent misreads where `sprint: 1` or `tested_with: claude-opus-4-7` are treated as reserved spec fields rather than custom metadata.

### Existing use (before fix)
Today, any registry tooling or CI validation that enforces the agentskills.io spec will flag this skill as non-compliant on the first pass. An agent that looks up skills by tag (`investor-forms`, `fundraising`) may get no results because the tag path is wrong. A developer cloning this skill into a different project may encounter YAML schema validation errors when the top-level fields collide with parser expectations for reserved keys. The sprint number and product name are silently treated as unknown top-level keys, which some parsers will discard entirely.

### Improved use (after fix)
After the restructure, the frontmatter validates cleanly against the spec. Registry tag search returns this skill when a user asks about investor forms or fundraising applications. A developer importing the skill sees `metadata.author`, `metadata.version`, and `metadata.tags` exactly where they expect them. CI passes on the first run. The skill can be published to the public agentskills.io registry without a rejection on structure alone.

---

## Improvement 2 — Add Missing `license` Field

### What needs to change

The `license` field is absent from the frontmatter entirely. Without it, consumers of this skill have no machine-readable signal about whether they can use, modify, or redistribute it. This is a gap for any published skill regardless of whether the spec marks it as optional.

### Before
```yaml
---
name: investor-form-filler
description: Fill investor application forms (VC, accelerator, grant) from a single facts file, tuned per investor type, with sensitive financials kept behind an explicit gate.
version: 1.0.0
author: Sarang T S
# ... no license field present
---
```

### After
```yaml
---
name: investor-form-filler
description: Fill investor application forms (VC, accelerator, grant) from a single facts file, tuned per investor type, with sensitive financials kept behind an explicit gate.
license: MIT
compatibility: Requires WebSearch and WebFetch tool access. Expects company-facts.md at the project root. Optional scripts/match_question.py and scripts/check_consistency.py require Python 3.8+ (stdlib only).
metadata:
  version: 1.0.0
  author: Sarang T S
  email: sarang@testmyskills.ai
  # ...
---
```

### Impact if implemented
- **Agent behaviour:** No direct change to runtime behaviour, but automated dependency checkers and legal-compliance tooling in enterprise environments can now confirm this skill is safe to use.
- **Discoverability:** The agentskills.io registry can surface this skill in "MIT-licensed only" filtered searches, which some organisations require before approving third-party skills.
- **Portability:** Another team can import the skill without asking the author whether it is safe to use. The answer is already in the manifest.
- **Risk reduced:** Prevents a legal ambiguity situation where a company uses the skill at scale, discovers there is no declared license, and must retroactively seek permission or stop using it.

### Existing use (before fix)
Today, any developer or organisation that browses the registry and finds `investor-form-filler` has no machine-readable license signal. Enterprise adoption pipelines that check for an approved SPDX identifier (`MIT`, `Apache-2.0`, etc.) will block this skill. A developer who wants to fork and extend the skill for their own accelerator workflow cannot know whether that is permitted. The gap is invisible until a compliance review catches it — usually at the worst possible time.

### Improved use (after fix)
After adding `license: MIT`, the skill passes enterprise adoption pipelines automatically. The registry surfaces it in license-filtered searches. Any developer who forks it knows the terms upfront. The author's intent is declared once, in the canonical place, and never needs to be communicated separately again.

---

## Improvement 3 — Add Missing `compatibility` Field

### What needs to change

The skill depends on WebSearch and WebFetch tool access at runtime, and on the presence of `company-facts.md` at the project root. These dependencies are documented in the body's "Prerequisites" section as human guidance, but they are not declared in the machine-readable `compatibility` frontmatter field. An agent instantiating this skill in an environment without WebSearch will fail at Step 2 with no upfront warning.

### Before
```yaml
---
name: investor-form-filler
description: Fill investor application forms (VC, accelerator, grant) from a single facts file, tuned per investor type, with sensitive financials kept behind an explicit gate.
version: 1.0.0
# ... no compatibility field
---
```

The only dependency declaration is buried in the body:

```markdown
## Prerequisites

- [ ] A `company-facts.md` at the project root ...
- [ ] A `references/tone-by-audience.md` ...
```

### After
```yaml
---
name: investor-form-filler
description: Fill investor application forms (VC, accelerator, grant) from a single facts file, tuned per investor type, with sensitive financials kept behind an explicit gate.
license: MIT
compatibility: Requires WebSearch and WebFetch tool access. Expects company-facts.md at the project root. Optional scripts/match_question.py and scripts/check_consistency.py require Python 3.8+ (stdlib only).
metadata:
  version: 1.0.0
  # ...
---
```

### Impact if implemented
- **Agent behaviour:** An orchestrator can pre-flight check tool availability before activating the skill. If WebSearch is unavailable, the orchestrator can warn the user or fall back gracefully rather than letting Step 2 fail silently mid-session.
- **Discoverability:** The `compatibility` field is the contract for environment-aware routing — a skills router that filters by available tools will now correctly include or exclude this skill based on the current session's tool access.
- **Portability:** Teams running Claude in restricted environments (no web access, air-gapped, no file system) know immediately from the frontmatter that this skill requires external tool access and a project-level file.
- **Risk reduced:** Prevents the common failure mode where a user triggers the skill in a no-WebSearch session and gets a confusing error at Step 2 ("Research the investor") with no explanation of why.

### Existing use (before fix)
Today, when a user activates `investor-form-filler` in a Claude session where WebSearch is disabled or unavailable, the skill proceeds through Step 1 (confirm investor name) and then fails at Step 2 when it attempts to run WebSearch. The user sees a tool-access error with no context about why it failed or what to do. The prerequisite checklist in the body mentions `company-facts.md` but an agent cannot read that checklist before deciding whether to activate the skill. The mismatch between runtime reality and skill expectations is invisible until execution.

### Improved use (after fix)
After adding the `compatibility` field, an orchestrator reads the machine-readable contract before activating the skill. If WebSearch is unavailable, it surfaces a clear pre-flight warning: "This skill requires WebSearch and WebFetch. These tools are not available in the current session." The user can switch sessions, enable the tools, or choose a different workflow before the skill even starts. The `company-facts.md` requirement is also declared upfront, so a scaffolding tool can check for its existence and prompt the user to create it if missing — rather than letting the skill run and produce generic outputs because the facts file was absent.

---

## Improvement 4 — Bundle `scripts/check_consistency.py` or Remove the Reference

### What needs to change

The "Notes" section at the bottom of the skill body recommends pairing the skill with `scripts/check_consistency.py` and describes what it should do in detail ("fail if a banned/stale value reappears... if `company-facts.md` is missing a canonical anchor... if any artifact references a fact that has changed"). This implies the script is part of the skill bundle. However, the script does not exist in `scripts/`. Only `scripts/match_question.py` is present. The reference creates a false expectation that will confuse users who look for the script.

### Before
```markdown
## Notes

- This skill pairs with **investor-deck-builder**. Both should read the same `company-facts.md` ...
- Pair with a `scripts/check_consistency.py` drift guard in your project. It should fail if a banned/stale
  value reappears (an old valuation, an old team size), if `company-facts.md` is missing a canonical
  anchor, or if any artifact references a fact that has changed. Prose can't be fully DRY; the guard is
  the safety net.
- For a stable Q&A bank with topic tags, `scripts/match_question.py` (included) gives deterministic
  matching — useful for batch mode across many questions.
```

### After (Option A — bundle the script)

Add `scripts/check_consistency.py` to the skill with an implementation that:
- Accepts a `--facts company-facts.md` flag and one or more artifact paths
- Scans each artifact for numeric values and compares them against the canonical values in `company-facts.md`
- Fails with a non-zero exit code and a diff-style report if any value has drifted

Update the Notes section to:
```markdown
## Notes

- This skill pairs with **investor-deck-builder**. Both should read the same `company-facts.md` — that is
  how the deck and form never drift on numbers.
- `scripts/check_consistency.py` (included) is a drift guard. Run it after filling any form to confirm
  that all numeric facts in the output match `company-facts.md`. It exits non-zero and prints a diff if
  any value has drifted, a canonical anchor is missing, or a banned stale value has reappeared.
  Usage: `python scripts/check_consistency.py --facts company-facts.md output/<slug>-application-FILLED.md`
- `scripts/match_question.py` (included) gives deterministic question-to-answer matching via weighted
  token overlap + tag bonuses — useful for batch mode across many questions. Stdlib only, no installs.
```

### After (Option B — remove the reference if bundling is not planned)

```markdown
## Notes

- This skill pairs with **investor-deck-builder**. Both should read the same `company-facts.md` — that is
  how the deck and form never drift on numbers.
- For a stable Q&A bank with topic tags, `scripts/match_question.py` (included) gives deterministic
  matching — useful for batch mode across many questions. Stdlib only, no installs.
- Filled forms can be turned into PDFs for emailing via a small markdown-to-PDF helper (the
  investor-deck-builder skill includes one).
```

### Impact if implemented
- **Agent behaviour:** With Option A, the agent can invoke `check_consistency.py` as part of Step 7 or Step 8 to automatically validate the filled output before handing it to the user. With Option B, the agent no longer misleads users into looking for a file that does not exist.
- **Discoverability:** Option A adds a concrete quality-gate capability that distinguishes this skill from generic form-filling tools. Option B reduces noise.
- **Portability:** Option A makes the skill fully self-contained — every referenced script is present. Option B removes a dead reference that would otherwise confuse every team that adopts the skill.
- **Risk reduced:** Prevents the failure mode where a user runs `python scripts/check_consistency.py` after following the Notes instructions and gets a `FileNotFoundError`. This erodes trust in the entire skill bundle.

### Existing use (before fix)
Today, a developer who reads the Notes section sees a clear recommendation to "pair with `scripts/check_consistency.py`" with a detailed description of what it does. They look in the `scripts/` folder and find only `match_question.py`. They must either write the consistency checker themselves (from a description in a skill file, not a spec) or skip the drift-guard step entirely. The most likely outcome is that the drift guard is skipped, which means filled forms can silently contain stale valuations or outdated team sizes that contradict the live deck — exactly the failure mode the script was designed to prevent.

### Improved use (after fix)
With Option A, the developer finds `check_consistency.py` in `scripts/`, runs it after the form is filled, and gets immediate feedback if any number in `output/<slug>-application-FILLED.md` has drifted from `company-facts.md`. The filled form and the deck stay in sync automatically. With Option B, the Notes section is accurate and honest — it only references tools that are actually present, and developers do not waste time searching for a script that does not exist.

---

## Improvement 5 — Soften the `investor-deck-builder` Cross-Skill Dependency in Step 8

### What needs to change

Step 8 ("Offer next steps") tells the agent to offer to "run the companion `investor-deck-builder` skill." This implies the skill is always present and runnable. If `investor-deck-builder` is not installed, the agent either fails or offers a next step it cannot fulfill. The language should be conditional.

### Before
```markdown
### Step 8: Offer next steps

1. **Matching deck?** — run the companion `investor-deck-builder` skill so the deck and form use the same
   numbers and framing.
2. **Diligence pack?** — only if the investor asks for financials.
3. **Save an investor-tuning block** — so the next application to the same investor is consistent.
```

### After
```markdown
### Step 8: Offer next steps

1. **Matching deck?** — if the `investor-deck-builder` skill is available in this session, offer to run
   it so the deck and form use the same numbers and framing. If not, note that the user should keep the
   filled form and any existing deck in sync against `company-facts.md` manually.
2. **Diligence pack?** — only if the investor explicitly asks for financials.
3. **Save an investor-tuning block** — offer to append a new investor-specific block to
   `investor-tuning.md` so the next application to this investor is consistent without re-running
   the web research steps.
```

### Impact if implemented
- **Agent behaviour:** The agent no longer attempts to invoke `investor-deck-builder` unconditionally. It checks availability first, which prevents a runtime error in sessions where the companion skill is absent.
- **Discoverability:** No change to discoverability, but the skill's reliability signal improves — agents that audit skill quality will not flag an unconditional cross-skill call as a potential failure point.
- **Portability:** Teams that adopt `investor-form-filler` without `investor-deck-builder` get a graceful degradation path rather than a broken next-steps offer.
- **Risk reduced:** Prevents the agent from offering a step it cannot execute, which damages user trust and creates a confusing interaction at the point where the user is most likely to act on the output.

### Existing use (before fix)
Today, when a user reaches the end of a form-filling session and the agent reaches Step 8, it unconditionally offers to "run the companion `investor-deck-builder` skill." If that skill is not installed, the agent either fails with an unknown-skill error or generates a hollow offer that leads nowhere. In either case, the user ends the session with a broken next step — precisely when they are ready to act on the filled form.

### Improved use (after fix)
After the fix, the agent checks whether `investor-deck-builder` is available before offering it. If it is available, the offer is made and can be fulfilled. If it is not available, the agent instead reminds the user to keep their existing deck aligned with `company-facts.md` — a useful fallback that turns a potential failure into actionable guidance. The investor-tuning block save step is also clarified with a concrete target file (`investor-tuning.md`), making it actionable rather than vague.

---

## Priority Order

| Priority | Improvement | Effort | Impact |
|---|---|---|---|
| 1 | Nest non-standard frontmatter fields under `metadata:` | Low | Critical |
| 2 | Add missing `license` field | Low | High |
| 3 | Add missing `compatibility` field | Low | High |
| 4 | Bundle `scripts/check_consistency.py` or remove the reference | Medium | High |
| 5 | Soften the `investor-deck-builder` cross-skill dependency in Step 8 | Low | Medium |

---

## Before vs After: Full Skill Experience

### Before (current state)

A developer discovers `investor-form-filler` in the skills registry and tries to add it to their fundraising workflow. Before they can use it, CI validation rejects the skill manifest because eight non-standard fields (`version`, `author`, `email`, `category`, `tags`, `product`, `sprint`, `tested_with`) are at the top level of the frontmatter instead of under `metadata:`. There is also no `license` field, so the developer's enterprise compliance tooling blocks the skill from being approved for use. The `compatibility` field is absent, meaning there is no machine-readable signal that the skill requires WebSearch and WebFetch — the developer only discovers this at Step 2 when the skill fails mid-session in their restricted-access environment.

Once the developer manually fixes the frontmatter and runs the skill in a full-access environment, the body performs well through Steps 1 to 7. But at Step 7, the Notes section tells them to "pair with `scripts/check_consistency.py`" for drift detection. They look in the `scripts/` folder and find only `match_question.py` — the consistency checker does not exist. They either write it from scratch or skip the drift guard, accepting the risk that stale valuations could silently appear in filled forms. Finally, at Step 8, the agent offers to run `investor-deck-builder` unconditionally, which fails if that skill is not installed, leaving the user with a broken next-steps experience at the moment they are most ready to act.

The skill's body content is genuinely strong — the diligence gate, the honesty constraints, the investor-type tuning table, and the failure-modes list are all well-designed. But the structural violations and missing declarations mean that the skill cannot be adopted without manual remediation, and two specific rough edges (the missing script and the unconditional companion-skill call) create trust-damaging failures that undercut an otherwise production-quality workflow.

### After (all improvements applied)

With all five improvements applied, a developer picks up `investor-form-filler` from the registry and it passes CI validation on the first run. The `metadata:` block is correctly structured, `license: MIT` is declared, and the `compatibility` field tells the orchestrator upfront that WebSearch, WebFetch, and `company-facts.md` are required. A skills router in a restricted environment surfaces a pre-flight warning before the skill is even activated, rather than letting it fail at Step 2. Tag-based search (`investor-forms`, `fundraising`, `applications`) now works because the tags are in the correct location under `metadata:`.

At runtime, the skill flows cleanly from investor identification through form filling to output generation. The `scripts/` folder now contains both `match_question.py` (for deterministic question matching) and `check_consistency.py` (for drift detection). After the form is filled, the developer runs the consistency checker and immediately confirms that every number in `output/<slug>-application-FILLED.md` matches `company-facts.md` — no stale valuations, no outdated team sizes, no silent divergence from the live deck. The companion-skill offer at Step 8 is conditional: if `investor-deck-builder` is available it is offered; if not, the agent gives a concrete fallback instruction instead of a broken next step.

The end result is a skill that is structurally compliant, environment-aware, fully self-contained, and gracefully degradable. Every referenced file exists. Every cross-skill dependency is conditional. Every runtime requirement is declared before execution begins. The body's original strengths — the diligence gate, the honesty constraints, the investor-type tuning table, the failure-modes list — are fully preserved. The skill can be adopted by any team, in any environment, without manual remediation.
