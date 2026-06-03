---
name: decision-brief
description: "Produces a lightweight decision record (lighter than an ADR) before implementing ambiguous work — scoping features, evaluating design options, or deciding an approach before writing code."
license: "Proprietary — internal use only (zysk.tech)"
compatibility: >
  Requires GitHub CLI (gh) for the optional label-cleanup step (Step 5). No other
  external dependencies. Designed for Claude Code. The label-cleanup step targets
  zyni-ai/tms-app by default — update the repo flag before use in other projects.
metadata:
  version: "1.0.0"
  author: Varun U
  email: varun@zysk.tech
  category: engineering-practice
  tags: "decision-record, scoping, planning, adr, github-issues"
  product: tms
  sprint: "4"
  tested_with: claude-opus-4-7
  user-invocable: "true"
---

# Decision Brief

> Produce a lightweight decision record before implementing ambiguous work. Lighter than a full ADR — just enough to align on the "what and why" before writing code.

## When to use

- Ambiguous-track issues from `/backlog-burn-down`
- Work with multiple valid approaches and no obvious winner
- Cross-cutting changes that touch 3+ features
- Anything where you'd regret not writing down the reasoning

### When NOT to use

- Quick-fixes (obvious, 1–2 files)
- Clear-scope work where the plan fits in a PR description
- Pure refactors with mechanical scope (find → replace)

## Steps

1. Write the brief using the template below.
2. Present to the user at the 🛑 scope checkpoint.
3. On approval, save to `docs/decisions/YYYY-MM-DD-<slug>.md` and proceed to implementation.
4. Update **Status** to `Accepted` after approval, `Superseded` if approach changes mid-flight.
5. **Close the ambiguity loop.** If the source issue (the `**Issue:** #NNNN` field in the brief) carries `status: needs investigation` — `/auto-ship` adds this label when it classifies an issue ambiguous — remove it now:

   ```bash
   err=$(gh issue edit <N> --repo zyni-ai/tms-app --remove-label "status: needs investigation" 2>&1) \
     || echo "$err" | grep -q "not found" \
     || { echo "Failed to remove label: $err"; exit 1; }
   ```

   The narrow error swallow handles the "label wasn't on this issue" case (e.g., the brief was written for a fresh issue not previously triaged by `/auto-ship` — `gh` returns exit 1 with `'<label>' not found`). Real failures (auth, network, rate limit, repo not found) surface as a hard error rather than getting silently masked, so a partial run is visible. After removal, the next `/auto-ship` run treats the issue as no-longer-ambiguous and picks it up.

## Output

- **Format:** Markdown file matching the repo's existing ADR convention.
- **Location:** `docs/decisions/YYYY-MM-DD-<slug>.md`
- **Side effect:** Removes `status: needs investigation` label from the source GitHub issue (if present) so `/auto-ship` can pick it up on the next run.

### Template

```markdown
# <Title>

**Date:** YYYY-MM-DD
**Issue:** #NNNN
**Status:** Proposed | Accepted | Superseded

## Problem

What's broken or missing? 2–3 sentences max.

## Current State

What exists today. Cite the actual code (`src/foo.ts:42`), the existing
behavior, the constraint that frames the problem. If you haven't yet
investigated, say so explicitly and propose the audit rather than
guess — the Approach below should follow from this section, not float
free of it.

## Approach

What we'll do. Be specific enough that a reviewer can say "yes" or "no."

## Alternatives considered

| Option | Pros | Cons | Why not |
|--------|------|------|---------|
| A (chosen) | ... | ... | — |
| B | ... | ... | One sentence |
| C | ... | ... | One sentence |

## Risks

What could go wrong with the chosen approach. Be honest — the point
is to surface these before code review, not after. For 3+ risks, a
Risk / Likelihood / Impact / Mitigation table reads better than prose.

## Scope boundary

What's explicitly NOT in this work. Prevents scope creep mid-implementation.

## Decision

The recommended path forward in one paragraph. Name the owner
("@me will start the audit," "next person on auth-area rotation,"
"open to whoever picks it up"), the urgency, and the immediate next
action (open a PR, start an audit, file follow-up issues, close as
no-op). This is the brief's closer — readers should know what is
*going to happen* after this brief lands.

## References

Bullet list of files, issues, and docs cited above. Helps the next
reader trace claims to source. Compact format:

- `src/auth.ts` (NextAuth v5 config — see lines 60–80)
- Issue #2176 (auth refresh token, blocked on backend)
- `docs/decisions/2025-11-15-axios-to-fetch.md` (related migration)
```

## Example

**User says:** "Let's scope out issue #2241 — RSC migration phasing."

**Claude does:** Investigates the current data-fetching surface, drafts `docs/decisions/2026-05-25-rsc-migration-phasing.md` with Problem / Current State / Approach / Alternatives / Risks / Scope boundary / Decision / References, and presents at the scope checkpoint. On approval, saves the file and removes `status: needs investigation` from issue #2241.

**Result:** A 1-page decision record committed to the repo + a clear, unambiguous Todo `/auto-ship` can now pick up.

## Quality check

A good brief answers these in under 1 page:

- Could someone else implement this from the brief alone?
- Does **Current State** cite actual code, or is it speculation? If you didn't investigate, did you say so?
- Are the alternatives real options you considered, not strawmen?
- Does the scope boundary prevent the PR from growing 2x?
- Does **Decision** name a clear next action and an owner (or explicitly say "open to whoever picks it up")?

If the brief takes more than 15 minutes to write, the problem isn't well understood yet — investigate more before writing.

## Red flags

- **Writing the brief before investigating Current State.** The Approach section should follow from Current State, not float free of it. If you haven't read the relevant files yet, the brief is a fiction — say so explicitly and propose the audit, or stop and investigate first.
- **Strawman alternatives.** "Do nothing" is rarely a real option; "completely rewrite the system" is rarely realistic. Alternatives must be options you genuinely considered, with honest pros/cons. A reviewer who reads the table should be able to argue for option B if your reasoning for A is weak.
- **Scope boundary missing or vague.** "Don't touch unrelated code" is too soft to prevent scope creep. Name the specific files, modules, or concerns that are explicitly out of scope, and mention any related-but-deferred issue numbers.
- **Decision section without an owner or next action.** A brief that ends "this is what we should do" but doesn't say *who's doing it when* leaves the work in limbo. If no one's picking it up immediately, say "open to whoever picks it up" — that's still a clear next action (the user files it as a Todo and moves on).
- **Skipping the ambiguity-loop label removal (Steps step 5)** when the source issue carries `status: needs investigation`. Without removing the label, `/auto-ship` will keep skipping the issue forever, and the brief's whole purpose (unblocking the issue) is defeated.
- **Verifying the issue's premise without questioning it.** A brief is the right place to push back on the issue body if the proposed problem doesn't actually exist or has already been resolved. Use Current State as the evidence layer for that pushback — don't write a brief that solves a non-problem.

## Notes

- This skill was developed in the `tms-app` context, so the example command targets `zyni-ai/tms-app`. Swap the repo in step 5 of **Steps** for your own project.
- The `status: needs investigation` label coupling is specific to a workflow where `/auto-ship` (and the matching label) exists. If you don't use `/auto-ship`, skip step 5 entirely.
