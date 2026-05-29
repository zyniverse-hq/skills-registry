# IMPROVEMENTS — review-queue

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

## Improvement 1 — Nest all custom frontmatter fields under `metadata:`

### What needs to change
Nine non-standard frontmatter fields (`version`, `author`, `email`, `category`, `tags`, `product`, `sprint`, `tested_with`, `user-invocable`) are declared at the top level of the YAML frontmatter. The agentskills spec requires all custom fields to be nested under a single `metadata:` key. Any agent or tooling that validates frontmatter will either reject these fields or fail to parse them correctly because they collide with the spec's reserved top-level namespace.

### Before
```yaml
---
name: review-queue
description: "Read-only digest of open PRs where you're a requested reviewer. Classifies each by readiness (ready-to-approve / needs your attention / waiting / stale) with one-line factual summaries, and stops — never approves, never comments."
version: 1.0.0
author: Varun U
email: varun@zysk.tech
category: engineering-practice
tags:
  - github-pr
  - code-review
  - triage
  - workflow
  - digest
product: tms
sprint: 4
tested_with: claude-opus-4-7
user-invocable: true
---
```

### After
```yaml
---
name: review-queue
description: "Read-only digest of open PRs where you're a requested reviewer. Classifies each by readiness (ready-to-approve / needs your attention / waiting / stale) with one-line factual summaries, and stops — never approves, never comments."
license: MIT
compatibility: "Requires gh CLI (>=2.23) authenticated with a GitHub account that has read access to the target repository. The --review-requested flag requires gh >=2.23."
metadata:
  version: 1.0.0
  author: Varun U
  email: varun@zysk.tech
  category: engineering-practice
  tags:
    - github-pr
    - code-review
    - triage
    - workflow
    - digest
  product: tms
  sprint: 4
  tested_with: claude-opus-4-7
  user-invocable: true
---
```

### Impact if implemented
- **Agent behaviour:** Agents and skill-loader tooling can parse the frontmatter without hitting unexpected top-level keys; validation passes cleanly instead of emitting warnings or dropping the skill from the index.
- **Discoverability:** Skills registries that index by `metadata.tags` (e.g., `github-pr`, `triage`) can now surface this skill in tag-based searches. Before the fix, those tags are unreachable to indexers that follow the spec's field path.
- **Portability:** Any team adopting this skill can extend `metadata:` with their own fields without risk of collision with reserved top-level keys.
- **Risk reduced:** Prevents silent field-drop failures where a spec-compliant loader silently ignores `version`, `author`, `sprint`, etc. because they appear outside the expected namespace.

### Existing use (before fix)
Today, when a spec-compliant skill loader reads `review-queue/SKILL.md`, it encounters nine top-level fields it does not recognise (`version`, `author`, `email`, `category`, `tags`, `product`, `sprint`, `tested_with`, `user-invocable`). Depending on the loader's strictness setting, it either rejects the entire skill or silently ignores those fields. In either case, tag-based discovery (`github-pr`, `triage`, `code-review`) does not work. A developer searching the registry for "code-review skills" will not find `review-queue` even though it is exactly what they need. The sprint and author attribution fields are also invisible to any reporting tooling that reads `metadata.*`.

### Improved use (after fix)
After nesting all nine fields under `metadata:`, the frontmatter is fully spec-compliant. Skill loaders parse the file without warnings. Tag-based searches for `github-pr`, `triage`, or `workflow` return this skill. Sprint-tracking dashboards that read `metadata.sprint` pick up the value `4` correctly. Author contact information (`metadata.email`) is surfaced in the registry UI. The skill passes CI validation on first attempt rather than requiring a maintainer to manually override schema errors.

---

## Improvement 2 — Add the required `license` field

### What needs to change
The `license` field is entirely absent from the frontmatter. This is a required field per spec. Without it, skills registries cannot determine the redistribution terms for this skill, and automated compliance checks will flag the skill as non-compliant on every scan.

### Before
```yaml
---
name: review-queue
description: "Read-only digest of open PRs where you're a requested reviewer. Classifies each by readiness (ready-to-approve / needs your attention / waiting / stale) with one-line factual summaries, and stops — never approves, never comments."
version: 1.0.0
author: Varun U
...
---
```
(no `license` field anywhere in the frontmatter)

### After
```yaml
---
name: review-queue
description: "Read-only digest of open PRs where you're a requested reviewer. Classifies each by readiness (ready-to-approve / needs your attention / waiting / stale) with one-line factual summaries, and stops — never approves, never comments."
license: MIT
compatibility: "Requires gh CLI (>=2.23) authenticated with a GitHub account that has read access to the target repository."
metadata:
  ...
---
```

### Impact if implemented
- **Agent behaviour:** No direct change to runtime behaviour — `license` is a metadata field. However, automated compliance gates that gate on `license` presence will stop blocking this skill from being published or indexed.
- **Discoverability:** Public skill registries often filter by license to show only skills that can be freely forked. Without the field, `review-queue` is excluded from those filtered views even if the intent is MIT.
- **Portability:** Other teams considering adopting this skill have no signal about whether they are allowed to fork and adapt it. Adding `license: MIT` (or the appropriate identifier) removes that ambiguity instantly.
- **Risk reduced:** Eliminates the compliance-check failure that blocks publishing this skill to the agentskills.openml.io registry.

### Existing use (before fix)
Any automated pipeline that validates skills before indexing them will fail on `review-queue` specifically because `license` is absent — even though the skill body is otherwise excellent. A maintainer running `skills validate` against the registry will see `review-queue` flagged as non-compliant alongside genuinely broken skills, diluting the signal. Teams evaluating the skill for adoption have no license clarity and may default to "do not use" to avoid legal ambiguity.

### Improved use (after fix)
With `license: MIT` present, the skill clears all compliance gates cleanly. Registry indexers display the license badge next to the skill. Teams evaluating adoption see immediately that they can fork and adapt it for their own repo. The `skills validate` output shows `review-queue` as fully compliant, and maintainers can focus on skills that actually have issues.

---

## Improvement 3 — Add the required `compatibility` field documenting `gh` CLI prerequisites

### What needs to change
The `compatibility` field is absent. This skill has a hard runtime dependency on the `gh` CLI (authenticated, with read access to `zyni-ai/tms-app`) and specifically requires `gh >=2.23` for the `--review-requested` search flag. None of this is documented in the frontmatter. A developer who installs the skill in an environment without `gh` or with an outdated version will hit a cryptic error at Step 1 with no guidance about what went wrong.

### Before
```yaml
---
name: review-queue
description: "Read-only digest of open PRs where you're a requested reviewer. ..."
version: 1.0.0
author: Varun U
...
---
```
(no `compatibility` field)

### After
```yaml
---
name: review-queue
description: "Read-only digest of open PRs where you're a requested reviewer. Classifies each by readiness (ready-to-approve / needs your attention / waiting / stale) with one-line factual summaries, and stops — never approves, never comments."
license: MIT
compatibility: "Requires gh CLI (>=2.23) authenticated with a GitHub account that has read access to the target repository. The --review-requested search flag requires gh >=2.23. Run 'gh auth status' to verify authentication before invoking."
metadata:
  ...
---
```

### Impact if implemented
- **Agent behaviour:** Agents that check `compatibility` before invoking a skill can surface a clear prerequisite-not-met message ("gh CLI not found or version too old") instead of letting Step 1 fail silently with a confusing shell error.
- **Discoverability:** Skills registries that filter by environment requirements (e.g., "show me skills that work in a GitHub-native environment") can now include `review-queue` in those filtered results.
- **Portability:** Any team adopting the skill for a different repo knows upfront what they need installed. The `gh auth status` tip in the compatibility string directly echoes the recovery guidance already in the skill body's "Recovery from partial-step failures" table — keeping the two sources of truth consistent.
- **Risk reduced:** Prevents the silent failure described in the recovery table ("Step 1 search returns empty when you know there are PRs — Likely token/auth issue") from being a surprise. The developer has been warned at install time, not at runtime.

### Existing use (before fix)
A developer picks up `review-queue` and invokes it in a fresh environment. Step 1 runs `gh search prs --review-requested "@me"` and returns an empty list or a cryptic authentication error. The developer spends time debugging whether the skill logic is wrong, whether there really are no PRs, or whether `@me` resolution failed — before eventually landing on `gh auth status` as the culprit. The recovery table inside the skill body does mention this, but only someone who has already read the full skill body would know to look there. The frontmatter `compatibility` field surfaces the prerequisite before the skill is ever invoked.

### Improved use (after fix)
With `compatibility` present, an agent or developer evaluating the skill sees the `gh` CLI requirement at a glance before invoking it. If their environment doesn't have `gh` installed or authenticated, they fix that first. If a skills registry surfaces compatibility metadata in its UI, users see "Requires gh CLI >=2.23" next to the skill card. Runtime surprises at Step 1 are eliminated for anyone who reads the skill's metadata before use.

---

## Improvement 4 — Trim the redundant "Bucket assignment by verdict" reference table

### What needs to change
The verdict-to-bucket mapping appears twice in the skill body: first in Step 3's classification matrix (the 10-row decision table with Condition / Verdict / Rationale columns) and again in the standalone "Bucket assignment by verdict" section (lines 229–245). The second table adds the "Why" column, but every "Why" entry is a shortened restatement of the Rationale already in Step 3. This duplication consumes ~17 lines, brings the body to 273 lines, and risks drift if someone updates one table but not the other.

### Before
```markdown
## Bucket assignment by verdict

Every verdict has exactly one bucket. The classifier in Step 3 produces the verdict; this table maps it to the report section. If you find yourself debating placement, this table is authority.

| Verdict | Bucket | Why |
|---|---|---|
| `ready-to-approve` | READY TO APPROVE | Your spot-check is the only thing missing |
| `auto-review-flagged` | NEEDS YOUR ATTENTION | Bot found concerns — read before approving |
| `unresolved-threads` | NEEDS YOUR ATTENTION | Active discussion |
| `pending-auto-review` | WAITING | Bot hasn't weighed in (path filter or workflow lag) |
| `ci-running` | WAITING | Wait for CI |
| `ci-failing` | WAITING | Author's turn to fix |
| `awaiting-author` | WAITING | You already reviewed; ball in author's court |
| `stale` | STALE | Aged > 7 days; revisit |
| `draft` | (filtered, not surfaced) | Should have been dropped in Step 1 |
| `closed` | (filtered, not surfaced) | Race-loss; PR closed between fetch and view |
| `unknown` | NEEDS YOUR ATTENTION | Log raw state for the user to investigate |
```

### After
```markdown
## Bucket assignment by verdict

Quick-lookup reference — rationale is in Step 3.

| Verdict | Bucket |
|---|---|
| `ready-to-approve` | READY TO APPROVE |
| `auto-review-flagged` | NEEDS YOUR ATTENTION |
| `unresolved-threads` | NEEDS YOUR ATTENTION |
| `unknown` | NEEDS YOUR ATTENTION |
| `pending-auto-review` | WAITING |
| `ci-running` | WAITING |
| `ci-failing` | WAITING |
| `awaiting-author` | WAITING |
| `stale` | STALE |
| `draft` | (filtered, not surfaced) |
| `closed` | (filtered, not surfaced) |
```

### Impact if implemented
- **Agent behaviour:** No change to runtime classification logic — the decision table in Step 3 is unchanged. The reference table remains available as a tie-breaker lookup, just without the redundant prose.
- **Discoverability:** Reduces body line count from 273 to approximately 260, making the skill leaner and easier to scan. Stays well within the 400-line soft warning.
- **Portability:** Eliminates the drift risk where a team forks the skill, updates the Step 3 rationale, but forgets to update the "Why" column in the reference table — producing contradictory guidance.
- **Risk reduced:** Prevents future maintainers from consulting the wrong table when the two fall out of sync after an update. The canonical authority is unambiguously Step 3; the reference table is just a lookup shortcut.

### Existing use (before fix)
A developer updating the classification logic (e.g., adding a new verdict for `changes-requested`) edits Step 3's decision table but misses the identical row in the "Bucket assignment by verdict" section because it's 80+ lines further down the file. The two tables now contradict each other. An agent reading the skill body to resolve a classification edge case encounters conflicting guidance and either halts or picks the wrong bucket. The skill's stated principle — "this table is authority" — becomes meaningless when both tables claim authority.

### Improved use (after fix)
With the "Why" column removed from the reference table, Step 3 is unambiguously the source of truth for rationale. The reference table is a fast lookup only. A maintainer adding a new verdict updates Step 3 (one place) and adds a row to the reference table (no "Why" to duplicate). The two never fall out of sync on reasoning, only on the verdict-to-bucket mapping, which is easy to verify at a glance.

---

## Improvement 5 — Move suite-wide output anti-patterns out of per-skill Red Flags into a shared reference

### What needs to change
The "Red flags — Output presentation" sub-section contains four anti-patterns that are explicitly identified in the ANALYSIS as "suite-wide conventions that do not need to live in every skill": citing memory keys, compressing the digest into a single block, editorial summaries, and omitting PR URLs. If this skill is part of a suite with a shared conventions document, these 8 lines should be replaced by a single reference link. If no shared document exists yet, the items should stay — but this is the lowest-priority structural improvement and should only be acted on once the shared conventions doc is established.

### Before
```markdown
### Output presentation

These are the same Sonnet output failure modes documented across the suite — no skill is exempt:

- **Citing memory keys** in the digest (e.g., `feedback_*` filenames) → no. The user doesn't read those names. Embed the rule in your prose.
- **Compressing the digest into a single block** → no. Each PR is one row. The user reads it row-by-row to decide what to act on. Collapsing rows defeats the digest.
- **Editorial summaries** ("game-changing", "delights users") → no. Stick to factual: type, size, closes, author. The user does the value framing.
- **Omitting the PR URL on each row** → no. The whole point is the user clicks through to act. Surface the URL on every row.
```

### After
```markdown
### Output presentation

See [suite-wide output conventions](../CONVENTIONS.md#output-presentation) for shared anti-patterns (memory-key citations, block compression, editorial summaries, missing URLs). Skill-specific rule: every row in the digest must include the PR URL — the user clicks through to act, and a row without a URL defeats the purpose of the digest.
```

### Impact if implemented
- **Agent behaviour:** No change — the anti-patterns are preserved either in-skill or in the referenced conventions doc. The agent still has access to the same rules.
- **Discoverability:** Reduces per-skill body size, making individual skills faster to scan. The conventions doc becomes the authoritative cross-skill reference, easier to maintain than N copies.
- **Portability:** A team adopting only `review-queue` (without the full suite) should keep the full anti-pattern list in-skill. This improvement is only beneficial once the shared conventions doc exists — flag it as conditional.
- **Risk reduced:** Prevents the suite's shared anti-patterns from drifting across skills as the suite evolves. One update to `CONVENTIONS.md` propagates to all skills that reference it.

### Existing use (before fix)
The four output anti-patterns are copied verbatim (or near-verbatim) across multiple skills in the suite. When a new anti-pattern is discovered (e.g., "don't truncate long PR titles"), a maintainer must update every skill file individually. Skills that are not updated silently carry stale guidance. The per-skill Red Flags sections become the source of truth by default, even though they were never intended to diverge.

### Improved use (after fix)
Once `CONVENTIONS.md` exists, each skill in the suite references it for shared anti-patterns and declares only skill-specific rules inline. `review-queue`'s skill-specific rule ("every row must include the PR URL") is the one that stays in-skill because it is unique to the digest format. Suite-wide rules are maintained once and applied everywhere. The per-skill body shrinks by ~8 lines, and the suite's conventions are authoritative and non-redundant.

---

## Priority Order

| Priority | Improvement | Effort | Impact |
|---|---|---|---|
| 1 | Nest all custom frontmatter fields under `metadata:` | Low | Critical |
| 2 | Add the required `license` field | Low | Critical |
| 3 | Add the required `compatibility` field documenting `gh` CLI prerequisites | Low | High |
| 4 | Trim the redundant "Bucket assignment by verdict" reference table | Low | Medium |
| 5 | Move suite-wide output anti-patterns to shared reference (conditional on CONVENTIONS.md existing) | Medium | Low |

---

## Before vs After: Full Skill Experience

### Before (current state)

A developer discovers `review-queue` in the skills registry and opens the SKILL.md to evaluate it. The frontmatter immediately presents nine top-level custom fields (`version`, `author`, `email`, `category`, `tags`, `product`, `sprint`, `tested_with`, `user-invocable`) outside any `metadata:` wrapper — a direct violation of the spec. If the developer runs `skills validate`, the tool flags the skill as non-compliant before they even read the body. The `license` field is missing entirely, so any compliance gate that requires it will block publishing this skill to a shared registry. The `compatibility` field is also absent, meaning there is no upfront signal that `gh` CLI version >=2.23 and active authentication are prerequisites — a developer in a fresh environment will invoke the skill, watch Step 1 return an empty list, and spend time debugging before landing on `gh auth status`.

Once the developer gets past the frontmatter issues and actually invokes the skill, the body is excellent: the step structure is clear, the 10-verdict classification matrix is precise, the auto-review classifier handles prose-format bot comments correctly, and the factual summary guidelines prevent editorial drift. The "Bucket assignment by verdict" reference table duplicates the Step 3 rationale in its "Why" column, creating a latent drift risk — if a future maintainer updates Step 3 but misses the reference table, the two sources contradict each other. The four output anti-patterns in the Red Flags section are valuable but are suite-wide conventions that will require N-file updates whenever they change.

### After (all improvements applied)

With all five improvements applied, `review-queue` is fully spec-compliant from the first line of frontmatter. The nine custom fields are nested under `metadata:`, making them accessible to tag-based registry searches (`github-pr`, `triage`, `code-review`). The `license: MIT` field clears every compliance gate. The `compatibility` string documents the `gh >=2.23` prerequisite and points developers directly to `gh auth status` for verification — matching the recovery guidance already in the skill body and ensuring the two sources stay consistent.

The body is leaner and more maintainable: the "Bucket assignment by verdict" table drops the redundant "Why" column, reducing drift risk and making Step 3 the unambiguous authority for classification rationale. Once the suite's shared `CONVENTIONS.md` document exists, the four suite-wide output anti-patterns can be replaced with a single reference link, further reducing per-skill maintenance overhead. The skill's unique rule — "every row in the digest must include the PR URL" — stays in-skill because it is specific to this digest format.

End-to-end, a developer or agent encountering `review-queue` now gets a clean validation pass, clear prerequisites, spec-compliant metadata indexing, and a body that is as precise as it was before — just with the structural issues resolved and the duplication removed. The skill is ready to be published to the agentskills.openml.io registry without any manual overrides.
