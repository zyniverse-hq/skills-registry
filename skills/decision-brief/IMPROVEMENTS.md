# IMPROVEMENTS — decision-brief

> Improvement plan derived from SKILL.md + ANALYSIS.md audit against the agentskills.openml.io spec.

---

## Quick Summary

| | Before | After |
|---|---|---|
| Spec compliance | Partially compliant | Fully compliant |
| Critical violations | 2 | 0 |
| Agent discoverability | Medium | High |
| Portability | Partial | Pass |

---

## Improvement 1 — Nest non-standard frontmatter fields under `metadata:`

### What needs to change

Nine top-level frontmatter fields (`version`, `author`, `email`, `category`, `tags`, `product`, `sprint`, `tested_with`, `user-invocable`) violate the spec requirement that all non-standard fields be nested under a single `metadata:` key. These must be moved inside `metadata:` to be spec-compliant.

### Before
```yaml
name: decision-brief
description: "Produces a lightweight decision record (lighter than an ADR) before implementing ambiguous work — scoping features, evaluating design options, or deciding an approach before writing code."
version: 1.0.0
author: Varun U
email: varun@zysk.tech
category: engineering-practice
tags:
  - decision-record
  - scoping
  - planning
  - adr
  - github-issues
product: tms
sprint: 4
tested_with: claude-opus-4-7
user-invocable: true
```

### After
```yaml
name: decision-brief
description: "Produces a lightweight decision record (lighter than an ADR) before implementing ambiguous work — scoping features, evaluating design options, or deciding an approach before writing code."
license: MIT
compatibility: "Requires GitHub CLI (gh) for label removal in Step 5. Step 5 can be skipped if gh is unavailable or /auto-ship is not in use."
metadata:
  version: 1.0.0
  author: Varun U
  email: varun@zysk.tech
  category: engineering-practice
  tags:
    - decision-record
    - scoping
    - planning
    - adr
    - github-issues
  product: tms
  sprint: 4
  tested_with: claude-opus-4-7
  user-invocable: true
```

### Impact if implemented
- **Agent behaviour:** Parsers and registries that expect `metadata:` nesting will correctly ingest all nine fields instead of encountering unexpected top-level keys or silently dropping them.
- **Discoverability:** Indexing tools that read `metadata.tags` will now correctly surface the skill when agents search for `decision-record`, `adr`, `scoping`, or `planning` — currently those tags are invisible to any parser that respects the spec structure.
- **Portability:** Other teams pulling this skill into their registry will not have their YAML validators reject the frontmatter or produce warning noise.
- **Risk reduced:** Prevents silent tag loss — without the nesting fix, a registry that strictly follows the spec ignores the entire `tags` block, meaning the skill is never returned in tag-based searches.

### Existing use (before fix)
Today, when a registry or agent framework ingests `decision-brief`, it encounters nine unexpected top-level YAML keys alongside `name` and `description`. Strict parsers reject or warn on these fields. Tag-based discovery tools looking for `metadata.tags` find nothing, so a search for skills tagged `adr` or `scoping` silently omits this skill. The nine fields are also invisible to any tooling that builds author/category indexes from `metadata.*`. A developer who added `decision-brief` to a shared registry would see it appear in `name`/`description` searches but never in tag, category, or author filters.

### Improved use (after fix)
After the fix, all nine custom fields land in their correct home under `metadata:`. A registry query for `tags: adr` returns `decision-brief` immediately. Author-index tooling correctly attributes the skill to `Varun U`. Category filters for `engineering-practice` include this skill. YAML validators pass without warnings. The frontmatter becomes a clean two-tier structure: required top-level fields (`name`, `description`, `license`, `compatibility`) plus a single `metadata` block for everything else.

---

## Improvement 2 — Add the required `license` field

### What needs to change

The spec lists `license` as a required frontmatter field. The skill has no `license` declaration at all. This is a hard spec violation that must be resolved before the skill can be considered fully compliant.

### Before
```yaml
name: decision-brief
description: "Produces a lightweight decision record (lighter than an ADR) before implementing ambiguous work — scoping features, evaluating design options, or deciding an approach before writing code."
version: 1.0.0
author: Varun U
# ... no license field present anywhere in frontmatter
```

### After
```yaml
name: decision-brief
description: "Produces a lightweight decision record (lighter than an ADR) before implementing ambiguous work — scoping features, evaluating design options, or deciding an approach before writing code."
license: MIT
```

### Impact if implemented
- **Agent behaviour:** Registry ingestion pipelines that enforce required-field validation will no longer reject or flag `decision-brief` as incomplete.
- **Discoverability:** Skills registries that filter by license (e.g., only surfacing MIT-licensed skills in open-source contexts) will now include this skill.
- **Portability:** Teams evaluating whether they can legally adopt this skill in their product have a clear, machine-readable answer instead of needing to chase down the author.
- **Risk reduced:** Prevents the skill from being silently excluded from curated registries that require a `license` value before publishing.

### Existing use (before fix)
Without a `license` field, any registry that enforces required-field checks marks `decision-brief` as invalid and either rejects it at ingest time or flags it with a compliance warning. Teams browsing a registry for reusable engineering-practice skills cannot see the skill's license terms, which creates a legal ambiguity that risk-averse organisations use as a reason to skip the skill entirely. The ANALYSIS.md already flagged this as a must-fix, yet it remains absent.

### Improved use (after fix)
With `license: MIT` in the frontmatter, the skill passes required-field validation in compliant registries. License filters work correctly. Teams can adopt the skill with confidence about its terms. The field is a single line addition with zero effect on the skill body or agent behaviour — purely structural, with meaningful compliance and discoverability payoff.

---

## Improvement 3 — Add the `compatibility` field documenting the `gh` CLI dependency

### What needs to change

Step 5 of the skill shells out to `gh` (GitHub CLI) to remove the `status: needs investigation` label. This is an external tool dependency that is entirely undocumented in the frontmatter. The spec lists `compatibility` as an optional but recommended field. Omitting it means agents and developers have no machine-readable signal that `gh` must be installed and authenticated before Step 5 will succeed.

### Before
```yaml
# No compatibility field in frontmatter.
# The gh dependency is only discoverable by reading Step 5 of the body:
err=$(gh issue edit <N> --repo zyni-ai/tms-app --remove-label "status: needs investigation" 2>&1) \
  || echo "$err" | grep -q "not found" \
  || { echo "Failed to remove label: $err"; exit 1; }
```

### After
```yaml
compatibility: "Requires GitHub CLI (gh) for label removal in Step 5. Step 5 can be skipped if gh is unavailable or /auto-ship is not in use."
```

### Impact if implemented
- **Agent behaviour:** Agents that check `compatibility` before executing a skill can surface a clear pre-flight warning — "this skill needs `gh` installed and authenticated" — instead of running Step 5 and getting a cryptic auth or command-not-found error at runtime.
- **Discoverability:** Teams in environments without `gh` (e.g., air-gapped, non-GitHub VCS) can filter out this skill at evaluation time rather than discovering the friction mid-workflow.
- **Portability:** The `Notes` section already calls out the `tms-app` coupling; the `compatibility` field makes the `gh` dependency equally explicit and machine-readable, not just prose-readable.
- **Risk reduced:** Prevents silent Step 5 failures in environments where `gh` is absent or unauthenticated. Without this field, the failure only surfaces when the bash command errors — after the rest of the workflow has already run.

### Existing use (before fix)
Today, a developer or agent running `decision-brief` in an environment without `gh` installed reaches Step 5 and encounters a `command not found` error (or an authentication failure if `gh` is installed but not logged in). There is no prior warning — nothing in the frontmatter, nothing at the skill-selection stage. The agent may have already written and approved the decision record before discovering that the label cleanup step cannot run, leaving the `status: needs investigation` label on the issue and defeating the brief's purpose of unblocking `/auto-ship`.

### Improved use (after fix)
With the `compatibility` field declared, a framework-aware agent checks prerequisites before executing. If `gh` is absent, the agent can warn the user upfront: "Step 5 requires GitHub CLI — either install it or skip Step 5 if /auto-ship is not in use." The decision record writing and approval flow proceeds cleanly, and the label cleanup either succeeds or the user has already been told it will be skipped. No silent partial runs.

---

## Improvement 4 — Extract the hardcoded repo reference from the Step 5 bash snippet into a parameterised script

### What needs to change

The bash snippet in Step 5 hardcodes `zyni-ai/tms-app` as the repo target. The `Notes` section acknowledges this and tells users to "swap the repo," but the fix is manual and prose-only. For a skill published to a shared registry, project-specific constants inside the skill body reduce portability and force every adopting team to remember to edit a raw bash string. Moving the snippet to `scripts/remove-investigation-label.sh` with a `REPO` parameter makes the dependency explicit, testable, and easy to override without touching the skill body.

### Before

In the body under Step 5:
```bash
err=$(gh issue edit <N> --repo zyni-ai/tms-app --remove-label "status: needs investigation" 2>&1) \
  || echo "$err" | grep -q "not found" \
  || { echo "Failed to remove label: $err"; exit 1; }
```

And in the Notes section:
```
This skill was developed in the `tms-app` context, so the example command targets `zyni-ai/tms-app`. Swap the repo in step 5 of **Steps** for your own project.
```

### After

New file `scripts/remove-investigation-label.sh`:
```bash
#!/usr/bin/env bash
# Usage: ./scripts/remove-investigation-label.sh <issue-number> <owner/repo>
# Removes "status: needs investigation" from a GitHub issue via gh CLI.
# Swallows the benign "label not found" exit-1 from gh; surfaces real failures.
set -euo pipefail

ISSUE="${1:?Usage: $0 <issue-number> <owner/repo>}"
REPO="${2:?Usage: $0 <issue-number> <owner/repo>}"

err=$(gh issue edit "$ISSUE" --repo "$REPO" --remove-label "status: needs investigation" 2>&1) \
  || echo "$err" | grep -q "not found" \
  || { echo "Failed to remove label: $err"; exit 1; }
```

Step 5 in the skill body becomes:
```markdown
5. **Close the ambiguity loop.** If the source issue carries `status: needs investigation`, remove it now:

   ```bash
   ./scripts/remove-investigation-label.sh <issue-number> <owner/repo>
   ```

   Replace `<owner/repo>` with your project's GitHub repo (e.g., `acme-org/my-app`). The script handles the benign "label not found" case and surfaces real failures as hard errors. See `scripts/remove-investigation-label.sh` for the implementation.
```

### Impact if implemented
- **Agent behaviour:** Agents referencing the skill body see a clean, one-line invocation instead of a multi-line bash expression. The parameterisation makes it unambiguous that `<owner/repo>` is a required argument, not something to find-and-replace inside inline code.
- **Discoverability:** No change to discoverability, but the skill body becomes significantly less noisy — easier to scan during agent reasoning.
- **Portability:** Any team pulling this skill can run the script against their own repo by passing a different `<owner/repo>` argument. No editing of the skill body required. The `tms-app` hardcode is fully eliminated from both the script and the body.
- **Risk reduced:** Eliminates the risk of a team adopting the skill, forgetting to swap the repo in the inline bash, and accidentally running `gh issue edit` against `zyni-ai/tms-app` — an org they likely have no write access to, producing an auth error that looks like a `gh` configuration problem rather than a missed substitution.

### Existing use (before fix)
Today, a developer at a different organisation copies `decision-brief` into their registry, reads the Notes section, finds the instruction to "swap the repo," locates the hardcoded `zyni-ai/tms-app` string buried inside a multi-line bash expression, edits it, and hopes they got it right. If they miss the substitution — perhaps because the skill was pulled in automatically by a registry sync — Step 5 runs against the wrong repo. The `gh` call fails with an auth or permissions error that looks unrelated to the repo mismatch, and the `status: needs investigation` label is never removed.

### Improved use (after fix)
After the fix, a new adopter runs `./scripts/remove-investigation-label.sh 2241 acme-org/my-app` and the label is removed cleanly. No editing of skill body required. The script is version-controlled alongside the skill, testable in isolation, and the parameter contract is documented in the usage comment. The Step 5 body text is now three lines instead of seven, making the overall skill body easier to scan.

---

## Priority Order

| Priority | Improvement | Effort | Impact |
|---|---|---|---|
| 1 | Nest non-standard frontmatter fields under `metadata:` | Low | Critical |
| 2 | Add the required `license` field | Low | Critical |
| 3 | Add the `compatibility` field documenting the `gh` CLI dependency | Low | High |
| 4 | Extract hardcoded repo reference into a parameterised script | Medium | Medium |

---

## Before vs After: Full Skill Experience

### Before (current state)

A developer browsing a spec-compliant skills registry searches for `tags: adr` or `category: engineering-practice` and gets zero results for `decision-brief` — because the nine non-standard frontmatter fields sit at the top level of the YAML instead of under `metadata:`, so the registry's tag and category indexes never see them. When the developer instead finds the skill by name and tries to ingest it, their YAML validator flags nine unexpected top-level keys and either rejects the skill or emits a warning that clutters CI output. Even if they manually install the skill, the missing `license` field means their organisation's compliance tooling marks it as unreviewed, adding friction before the skill can be approved for use.

Once a developer does get the skill running, they invoke it for a fresh decision brief on a non-GitHub-hosted project and reach Step 5 only to discover that the skill shells out to `gh` — a dependency mentioned nowhere in the frontmatter, only deep in the body prose. If `gh` is absent or unauthenticated, Step 5 throws a cryptic error after the rest of the workflow has completed, leaving the `status: needs investigation` label on the issue and breaking the `/auto-ship` integration silently. For teams that are GitHub-based but not on `zyni-ai/tms-app`, Step 5's hardcoded repo target is an additional manual substitution that the Notes section warns about in prose but that is easy to miss in an automated registry sync, causing Step 5 to fail against a repo they do not own.

### After (all improvements applied)

With the four improvements applied, `decision-brief` is fully spec-compliant and immediately discoverable. A tag search for `adr`, `scoping`, or `decision-record` returns the skill correctly because the `metadata.tags` block is now structured as the spec requires. The `license: MIT` field passes required-field validation in any compliant registry, and the `compatibility` field gives agents a machine-readable signal that `gh` must be present before Step 5 executes. Teams evaluating the skill see its terms and dependencies upfront — no surprises mid-workflow.

At runtime, an agent invoking `decision-brief` in an environment without `gh` receives an early warning from the `compatibility` field rather than a cryptic Step 5 failure. If the environment is ready, Step 5 now calls `./scripts/remove-investigation-label.sh <issue-number> <owner/repo>` — a clean, parameterised invocation that makes the required substitution explicit rather than buried in a multi-line bash expression. A team at `acme-org/my-app` passes their own repo argument and gets the label removed correctly with no edits to the skill body. The portability warning in the Notes section is no longer needed as a prose mitigation because the script's parameter contract enforces the substitution at call time.

The net result is a skill that works correctly on first install in any spec-compliant registry, is discoverable by all its relevant tags and categories, documents its external dependency before the workflow starts, and can be adopted by any GitHub-using team without manual find-and-replace in the skill body.
