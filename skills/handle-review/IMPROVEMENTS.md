# IMPROVEMENTS — handle-review

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

## Improvement 1 — Move non-standard frontmatter fields under `metadata:`

### What needs to change

Nine custom fields (`version`, `author`, `email`, `category`, `tags`, `product`, `sprint`, `tested_with`, `user-invocable`) are declared at the top level of the frontmatter. The spec requires all non-standard fields to be nested under a `metadata:` key. As-is, any spec-compliant parser will either reject the document or silently discard these fields.

### Before
```yaml
---
name: handle-review
description: "Triages PR review comments (human or bot), classifies each as valid/invalid/needs-human, fixes what's valid in one batch, replies with evidence for the rest, and pushes once."
version: 1.0.0
author: Varun U
email: varun@zysk.tech
category: engineering-practice
tags:
  - pr-review
  - code-review
  - github
  - triage
  - workflow
product: tms
sprint: 4
tested_with: claude-opus-4-7
user-invocable: true
---
```

### After
```yaml
---
name: handle-review
description: "Triages PR review comments (human or bot), classifies each as valid/invalid/needs-human, fixes what's valid in one batch, replies with evidence for the rest, and pushes once."
license: MIT
compatibility: "Requires gh CLI (authenticated) and git. npm/npx used for type-check/test steps (npm run type-check, npx vitest). Companion skills (pr-review-toolkit:code-reviewer, pr-review-toolkit:silent-failure-hunter, simplify, next-best-practices, vercel-react-best-practices) are optional — substitute project equivalents if unavailable."
metadata:
  version: 1.0.0
  author: Varun U
  email: varun@zysk.tech
  category: engineering-practice
  tags:
    - pr-review
    - code-review
    - github
    - triage
    - workflow
  product: tms
  sprint: 4
  tested_with: claude-opus-4-7
  user-invocable: true
---
```

### Impact if implemented
- **Agent behaviour:** Spec-compliant parsers can now correctly read and index all custom metadata without schema errors or silent field drops.
- **Discoverability:** Tags (`pr-review`, `code-review`, `github`, `triage`, `workflow`) become accessible to tag-based skill search once properly nested under `metadata:`.
- **Portability:** Other teams ingesting this skill via the registry will see structured, predictable metadata rather than a flat blob of unknown top-level keys.
- **Risk reduced:** Prevents silent data loss when a registry tool validates frontmatter against the spec schema and strips unrecognised top-level keys.

### Existing use (before fix)
Today, any tool that validates the skill frontmatter against the agentskills.io spec will encounter nine unknown top-level keys. Depending on the parser, this either produces a validation error that prevents the skill from loading, or silently drops the fields. Either outcome means `category: engineering-practice`, the tag list, and `tested_with: claude-opus-4-7` are invisible to search and indexing pipelines. A developer browsing the registry by category or tag will not find this skill even though it is correctly tagged in the source.

### Improved use (after fix)
Once the nine fields are nested under `metadata:`, the frontmatter passes spec validation. The tag list (`pr-review`, `code-review`, `triage`) becomes indexable, the `category` field routes the skill into the correct engineering-practice grouping, and `tested_with` is surfaced in the skill detail view. No structural changes are needed elsewhere in the file.

---

## Improvement 2 — Add the required `license` field

### What needs to change

The spec lists `license` as a required top-level frontmatter field. It is entirely absent from the current frontmatter. Without it, the skill is technically undistributable — consumers cannot determine whether they are permitted to use, modify, or redistribute it.

### Before
```yaml
---
name: handle-review
description: "Triages PR review comments (human or bot), classifies each as valid/invalid/needs-human, fixes what's valid in one batch, replies with evidence for the rest, and pushes once."
version: 1.0.0
author: Varun U
# ... (no license field anywhere)
---
```

### After
```yaml
---
name: handle-review
description: "Triages PR review comments (human or bot), classifies each as valid/invalid/needs-human, fixes what's valid in one batch, replies with evidence for the rest, and pushes once."
license: MIT
compatibility: "..."
metadata:
  version: 1.0.0
  author: Varun U
  # ...
---
```

### Impact if implemented
- **Agent behaviour:** Registry tooling that enforces required fields will no longer block ingestion of this skill or emit a blocking validation warning.
- **Discoverability:** Skills missing required fields are often deprioritised or hidden in registries with strict compliance filtering — adding `license` restores full visibility.
- **Portability:** Other projects and teams can now confirm they are permitted to copy and adapt the skill without needing to contact the author.
- **Risk reduced:** Eliminates the legal ambiguity that arises when `author: Varun U` is present but no license grants downstream users any rights.

### Existing use (before fix)
Any registry pipeline that checks for required fields before indexing will flag `handle-review` as non-compliant and either skip it or surface it with a compliance warning badge. A developer scanning the registry for skills they can freely adapt for their project sees the skill as potentially restricted. The author's name is present (`author: Varun U`), which actually reinforces the ambiguity — it reads as proprietary without an explicit license grant.

### Improved use (after fix)
With `license: MIT` present, the skill passes the required-fields check and is indexed without warnings. Developers can immediately see they are free to use and adapt the skill. Registry compliance dashboards show the skill as fully compliant alongside its `author`, `version`, and `description`.

---

## Improvement 3 — Add the `compatibility` field documenting external dependencies

### What needs to change

The skill has real, non-trivial external dependencies: `gh` CLI (must be authenticated), `git`, `npm run type-check`, `npx vitest`, and five optional companion skills (`pr-review-toolkit:code-reviewer`, `pr-review-toolkit:silent-failure-hunter`, `simplify`, `next-best-practices`, `vercel-react-best-practices`). None of these prerequisites are declared in the frontmatter. A developer activating this skill on a fresh machine with no `gh` CLI configured will hit a silent runtime failure at Step 1's very first command.

### Before
```yaml
---
name: handle-review
description: "Triages PR review comments (human or bot), classifies each as valid/invalid/needs-human, fixes what's valid in one batch, replies with evidence for the rest, and pushes once."
version: 1.0.0
# ... no compatibility field
---
```

The only mention of dependencies is buried in the body's `## Notes` section:
```markdown
## Notes
- Companion skill to `/ship-issue`; references `/simplify`, `next-best-practices`,
  `vercel-react-best-practices`, `pr-review-toolkit:code-reviewer`, and
  `pr-review-toolkit:silent-failure-hunter` — swap in your project's equivalents
  if those aren't installed.
```

### After
```yaml
---
name: handle-review
description: "Triages PR review comments (human or bot), classifies each as valid/invalid/needs-human, fixes what's valid in one batch, replies with evidence for the rest, and pushes once."
license: MIT
compatibility: "Requires gh CLI (authenticated) and git. npm/npx used for type-check/test steps (npm run type-check, npx vitest). Companion skills (pr-review-toolkit:code-reviewer, pr-review-toolkit:silent-failure-hunter, simplify, next-best-practices, vercel-react-best-practices) are optional — substitute project equivalents if unavailable."
metadata:
  version: 1.0.0
  # ...
---
```

### Impact if implemented
- **Agent behaviour:** An orchestration agent evaluating whether to activate this skill can now pre-flight check tool availability (`gh`, `git`) before invoking — rather than discovering the gap mid-execution at Step 1.
- **Discoverability:** The `compatibility` field enables registry filtering by environment (e.g., "show only skills that work with gh CLI"), surfacing this skill to exactly the developers who can use it.
- **Portability:** Teams without `pr-review-toolkit` installed now know before activation that the companion skills are optional, not required — removing a false blocker.
- **Risk reduced:** Prevents the confusing failure mode where the skill executes Steps 1–3 successfully but silently skips the Step 6 self-review because `pr-review-toolkit:code-reviewer` is not installed, with no warning to the user.

### Existing use (before fix)
A developer on a project that does not use `pr-review-toolkit` reads the skill body and finds the dependency mention only at the very bottom in `## Notes`. They may not reach that section before invoking. When Step 6 runs and `pr-review-toolkit:code-reviewer` is not available, the step either errors silently or is skipped without explanation. On a fresh machine without `gh` authenticated, the skill fails immediately at Step 1's `gh pr view` call with an opaque auth error — no upfront signal that `gh` authentication is a prerequisite.

### Improved use (after fix)
The `compatibility` field is read at skill-selection time, before any code runs. An orchestration layer can emit "missing gh CLI — please run `gh auth login` before activating this skill" as a pre-flight warning. Developers browsing the registry see the prerequisites immediately in the skill card, not buried in a notes section. Teams without `pr-review-toolkit` know in advance they will need project-equivalent tools for Step 6, and can substitute before activating.

---

## Improvement 4 — Eliminate the duplicated round-3+ simplification guidance

### What needs to change

The round-3+ simplification rule is stated in full in both Step 6 and the Red Flags section. The two blocks are nearly identical (~15 lines each) and cover the same directive: at round 3+, run `/simplify` on the full PR diff, prefer a collapsed design over patching individual findings, and escalate if `/simplify` finds nothing. This duplication adds ~15 lines of redundancy without adding new information, inflates the body line count, and creates a maintenance hazard where the two copies can drift.

### Before

Step 6 contains:
```markdown
**At round 3+ on the same PR, simplify aggressively.** The "diff > 20 lines / > 1 file"
rule above is for individual fixes. If you're at the third review round or later, run
`/simplify` against the **full PR diff** (`git diff origin/dev`), not just the latest
fix. Each round's narrow fix can introduce complexity that seeds the next round of
findings — at round 3+ the cumulative changes are usually carrying the kind of
complexity that reviewers keep flagging. Often a 20-line replacement for 100 lines of
careful guards resolves multiple reviewer flags at once. That's a stronger move than
patching each finding in isolation. **Simplification target:** if the full PR diff is
200 lines but could be 50, rewrite — brevity is a sign of understanding; reviewers
keep finding issues because the design is too complex to hold, not because the fixes
are wrong.
```

Red Flags section also contains:
```markdown
- **More than 2 review rounds on one PR → stop fixing, start simplifying.** The
  pattern: each fix introduces complexity that becomes the seed for the next round of
  findings. Run `/simplify` on the full diff (`git diff origin/dev`), not just the
  latest fix. If `/simplify` surfaces a way to collapse the design, prefer that over
  patching individual reviewer findings — the simpler version usually resolves
  multiple flags at once. If `/simplify` finds nothing, escalate to the user: the
  design is wrong upstream of this PR, and continuing to fix at the surface won't
  break the loop.
```

### After

Keep the full explanation in Step 6 (it belongs to the execution flow). Condense the Red Flags entry to a single cross-reference line:

```markdown
- **More than 2 review rounds on one PR → stop fixing, start simplifying.**
  See Step 6's round-3+ rule: run `/simplify` on the full PR diff (`git diff
  origin/dev`); if it finds nothing, escalate — the design is wrong upstream.
```

### Impact if implemented
- **Agent behaviour:** No functional change — the rule is still present and unambiguous. An agent reading either section reaches the same instruction.
- **Discoverability:** No change.
- **Portability:** Reduces body line count by ~12 lines, making the skill easier to scan and maintain. Eliminates the drift risk where one copy is updated and the other is not.
- **Risk reduced:** Prevents a future maintainer from updating the Step 6 version with a new threshold (e.g., "round 2+") without noticing the Red Flags copy still says "round 3+", creating contradictory instructions within the same skill file.

### Existing use (before fix)
Today a developer reading both sections encounters the same directive twice in slightly different wording. The Red Flags version omits the "simplification target" sentence (200-line diff → 50 lines = rewrite). The Step 6 version omits the "escalate to user" path. Neither copy is complete. A careful reader notices the discrepancy and has to reconcile two partially overlapping statements to extract the full rule. A future maintainer who updates the round threshold in one place will almost certainly miss the other.

### Improved use (after fix)
The full rule lives once in Step 6. The Red Flags entry is a one-line pointer that tells the reader where to find it. A maintainer updating the threshold touches one location. A developer reading the skill sees the complete rule exactly once, in the execution step where it applies.

---

## Improvement 5 — Relocate "Output presentation" rules out of the Red Flags section

### What needs to change

The `### Output presentation` subsection currently lives inside `## Red flags`. Its three bullet points are formatting rules for Step 4 and Step 8 output — not anti-patterns or failure modes. Misplacing them under Red Flags means a developer scanning for formatting guidance will miss them, and a developer scanning Red Flags for failure modes will be confused by format rules appearing alongside anti-patterns like "pushing without reading cited code."

### Before

The skill body contains (at the end of the Red Flags section):
```markdown
### Output presentation (Step 4 triage table, Step 8 report)

- **Don't cite memory keys in user-facing output.** Names like
  `feedback_no_premature_toasts` are internal — the user shouldn't see them
  in the triage table or the report. Reference the *content* of the memory
  ("we agreed not to add toasts in utility functions"), not the file name.
- **Don't compress the triage table into a single block.** Each row is one
  comment. The user reads it row-by-row to approve, skip, or override.
  Collapsing rows or merging columns defeats the checkpoint — re-render the
  full table even if it's long.
- **Don't omit the evidence column to save space.** The "evidence" column is
  what makes Step 4 a real review gate vs. a rubber-stamp. Without it, the
  user can't tell `invalid-wrong` from a hallucination.
```

### After

Remove the subsection from `## Red flags` and merge it into the existing `## Output` section:

```markdown
## Output

- **Format:** triage table at Step 4 (file:line / verdict / evidence /
  proposed action), then a single squashable commit chain + follow-up issues
  + PR replies + Step 8 grouped counts.
- **Location:** GitHub PR + filed follow-up issues + local git commits.
- **Side effects:** code changes to the PR branch, new GitHub issues for
  out-of-scope findings, threaded replies on PR comments.

### Output presentation conventions

- **Don't cite memory keys in user-facing output.** Names like
  `feedback_no_premature_toasts` are internal — reference the *content*
  ("we agreed not to add toasts in utility functions"), not the key name.
- **Don't compress the triage table into a single block.** Each row is one
  comment; the user reads row-by-row to approve, skip, or override.
  Collapsing rows defeats the Step 4 checkpoint — re-render the full table
  even if it's long.
- **Don't omit the evidence column to save space.** Without it, the user
  cannot distinguish `invalid-wrong` from a hallucination.
```

### Impact if implemented
- **Agent behaviour:** Formatting rules are now co-located with the `## Output` section they govern. An agent looking for output format guidance finds them in the expected place without scanning Red Flags.
- **Discoverability:** Logical grouping improves scanability — Red Flags is now exclusively failure modes, Output is now exclusively format rules.
- **Portability:** No change to portability, but reduces cognitive load for developers adapting the skill to a new project.
- **Risk reduced:** Prevents an agent from treating formatting rules as optional "anti-pattern" warnings rather than mandatory output conventions.

### Existing use (before fix)
A developer customising the Step 4 triage table output scans `## Output` and finds only three high-level bullets (Format, Location, Side effects). The detailed presentation rules — no memory keys, no compressed rows, no omitting evidence — are buried under `## Red flags` with a different header. The developer misses them, produces a triage table that cites internal memory key names, and confuses the end user.

### Improved use (after fix)
The `## Output` section is now the single source of truth for all output-related guidance. A developer customising or adapting the skill reads `## Output`, sees both the structural bullets and the `### Output presentation conventions` subsection immediately below, and applies all three formatting rules correctly from the start.

---

## Priority Order

| Priority | Improvement | Effort | Impact |
|---|---|---|---|
| 1 | Move non-standard frontmatter fields under `metadata:` | Low | Critical |
| 2 | Add required `license` field | Low | Critical |
| 3 | Add `compatibility` field for external dependencies | Low | High |
| 4 | Eliminate duplicated round-3+ simplification guidance | Low | Medium |
| 5 | Relocate "Output presentation" rules to `## Output` section | Low | Medium |

---

## Before vs After: Full Skill Experience

### Before (current state)

A developer discovering `handle-review` in the registry today encounters a skill that is well-designed operationally but structurally non-compliant. The frontmatter has nine custom fields (`version`, `author`, `email`, `category`, `tags`, `product`, `sprint`, `tested_with`, `user-invocable`) sitting at the top level — any strict parser will reject the document or silently drop these fields, making the skill invisible to tag-based and category-based search. There is no `license` field, so a developer who wants to adapt the skill for their project has no way to confirm they are permitted to do so. There are no `compatibility` prerequisites listed in the frontmatter, meaning a developer on a fresh machine with no `gh` CLI configured will not discover this until Step 1 fails with an opaque authentication error mid-execution.

Within the body, the round-3+ simplification rule appears twice in nearly identical form — once in Step 6 and once in Red Flags — in slightly different wording that is incomplete in both copies. A developer reading carefully notices the inconsistency and has to mentally reconcile two partial statements. More problematically, formatting rules for the Step 4 triage table and Step 8 report are buried inside `## Red flags` rather than `## Output`, meaning a developer customising output rendering will miss the "no memory key citations, no compressed rows, no omitted evidence column" rules entirely unless they read every section.

The skill's operational logic — triage gate, verdict taxonomy, ALREADY_HANDLED deduplication, self-review conditions, bucket accounting — is genuinely strong. The problems are entirely structural and metadata-level. But structural violations are what prevent a well-designed skill from being found, used, and trusted by other teams.

### After (all improvements applied)

Once all five improvements are applied, `handle-review` passes full spec compliance. The frontmatter declares `license: MIT`, a `compatibility` field listing `gh` CLI, `git`, `npm/npx`, and the optional companion skills, and moves all nine custom fields under `metadata:` where spec-compliant parsers expect them. The skill is now indexable by tag (`pr-review`, `triage`, `workflow`), category (`engineering-practice`), and license, and surfaces correctly in registry searches. Pre-flight tooling can read `compatibility` before activation and warn the developer if `gh` is not authenticated — rather than failing silently at Step 1's first command.

Inside the body, the round-3+ simplification rule lives once in Step 6 (complete, with the simplification target and the "escalate if nothing found" path). The Red Flags entry points to it in a single line. The `## Output` section now contains all output-related guidance — both the structural bullets and the `### Output presentation conventions` subsection — so a developer adapting the triage table or the Step 8 report reads everything they need in one place. Red Flags is now exclusively failure modes and anti-patterns, as intended.

A developer activating this skill on a new project reads the frontmatter, confirms they have `gh` and `git` installed, notes the companion skills are optional, and proceeds with confidence. An orchestration agent matching user intent against skill descriptions finds `handle-review` via its tags and `category`, reads the `compatibility` prerequisites, and either activates the skill or emits a pre-flight warning. The operational logic — triage, classify, fix, reply, push once — is unchanged and remains the strongest part of the skill. The improvements remove the structural friction that was previously preventing that logic from being found and trusted.
