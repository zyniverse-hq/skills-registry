# IMPROVEMENTS — git-workflow

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

## Improvement 1 — Move Non-Standard Frontmatter Fields Under `metadata:`

### What needs to change

Seven non-standard fields (`version`, `author`, `email`, `category`, `tags`, `product`, `sprint`, `tested_with`) are currently placed at the top level of the YAML frontmatter. The spec requires all custom/non-standard fields to be nested under a `metadata:` key. This must be restructured so only spec-defined top-level fields (`name`, `description`, `license`, `compatibility`, `allowed-tools`) appear at the root level.

### Before
```yaml
---
name: git-workflow
description: Applies this user's git conventions for branches, commits, merges, pull requests, force-pushes, and release tags whenever Claude runs any git command.
version: 1.0.0
author: Arijit Saha
email: arijit.saha@zysk.tech
category: engineering-practice
tags:
  - git
  - version-control
  - commits
  - branching
  - pull-requests
product: zysk
sprint: 1
tested_with: claude-sonnet-4-6
---
```

### After
```yaml
---
name: git-workflow
description: Enforces git conventions for branch naming, commit messages, merges, pull requests, force-push safety, and release tags. Use whenever running git commit, branch, merge, push, rebase, or tag commands, or when opening/updating a pull request.
license: MIT
metadata:
  version: 1.0.0
  author: Arijit Saha
  email: arijit.saha@zysk.tech
  category: engineering-practice
  tags:
    - git
    - version-control
    - commits
    - branching
    - pull-requests
  product: zysk
  sprint: 1
  tested_with: claude-sonnet-4-6
---
```

### Impact if implemented
- **Agent behaviour:** Parsers and registry tooling that validate frontmatter against the spec schema will no longer reject or warn on this skill. Fields like `version` and `category` will be read from the correct location.
- **Discoverability:** Registries that index skills by spec-compliant metadata will correctly surface tags like `git`, `commits`, and `branching` because they will be in the expected `metadata.tags` path.
- **Portability:** Any team importing this skill into their own registry via automated tooling will receive a valid, parseable document rather than one with spec violations.
- **Risk reduced:** Prevents silent metadata loss in registry tooling that ignores unrecognised top-level fields — `category`, `tags`, `tested_with`, and `sprint` would otherwise be silently dropped.

### Existing use (before fix)
Today, when an agent registry or CI validation step parses `skills/git-workflow/skill.md`, it encounters `version`, `author`, `email`, `category`, `tags`, `product`, `sprint`, and `tested_with` as unrecognised top-level YAML keys. Strict parsers raise a validation error and reject the skill entirely. Lenient parsers silently ignore these fields, meaning the tag index never includes `git`, `commits`, or `branching` — searches for those terms will not surface this skill. The skill may still work manually, but it fails automated quality gates and registry indexing.

### Improved use (after fix)
After restructuring, the frontmatter is fully spec-compliant. The registry correctly indexes `metadata.tags` for search, `metadata.version` for version tracking, and `metadata.tested_with` for compatibility filtering. CI validation passes. Other teams can import the skill via automated tooling without encountering schema errors. The `category: engineering-practice` field is accessible to dashboards that group skills by category, making the skill appear correctly in engineering-practice collections.

---

## Improvement 2 — Add the Required `license` Field

### What needs to change

The `license` field is a required top-level frontmatter field per the agentskills spec. It is entirely absent from the current `skill.md`. Without it, consumers of the skill — whether individuals or teams — have no indication of usage terms, and spec validators will flag this as a hard failure.

### Before
```yaml
---
name: git-workflow
description: Applies this user's git conventions for branches, commits, merges, pull requests, force-pushes, and release tags whenever Claude runs any git command.
version: 1.0.0
author: Arijit Saha
# ... no license field anywhere in the frontmatter
---
```

### After
```yaml
---
name: git-workflow
description: Enforces git conventions for branch naming, commit messages, merges, pull requests, force-push safety, and release tags. Use whenever running git commit, branch, merge, push, rebase, or tag commands, or when opening/updating a pull request.
license: MIT
metadata:
  version: 1.0.0
  author: Arijit Saha
  ...
---
```

### Impact if implemented
- **Agent behaviour:** No direct change to runtime agent behaviour, but spec validators and registry ingestion pipelines will move from FAIL to PASS on this check.
- **Discoverability:** Public skill registries filter or badge skills by license. Without a `license` field, this skill may be excluded from "open" or "freely reusable" collections, reducing how often it appears in search results.
- **Portability:** Teams evaluating whether they can legally adopt this skill in a commercial or open-source project have a clear answer. Without a license declaration, legal-cautious teams must skip the skill.
- **Risk reduced:** Eliminates ambiguity about redistribution and modification rights, preventing downstream legal friction when the skill is shared across organisations.

### Existing use (before fix)
Currently, anyone who discovers `git-workflow` in a public or shared registry sees no license declaration. Teams with legal or compliance requirements cannot determine whether they are permitted to use, modify, or redistribute the skill. Automated registry validators mark the skill as non-compliant and may suppress it from curated "safe to use" collections. The skill author (Arijit Saha, arijit.saha@zysk.tech) is identifiable via the `author` field, but there is no statement of intent about reuse.

### Improved use (after fix)
With `license: MIT` added, the skill is clearly and immediately reusable by any team or individual. Registry validators pass this check, and the skill can be included in curated open-source skill collections. Consumers can modify and redistribute the skill without ambiguity. The skill gains access to "open" and "MIT-licensed" filter categories in registries, directly increasing its discoverability and adoption rate.

---

## Improvement 3 — Strengthen `description` with Explicit Trigger Keywords

### What needs to change

The current `description` reads: `"Applies this user's git conventions for branches, commits, merges, pull requests, force-pushes, and release tags whenever Claude runs any git command."` While accurate for a human reader, the phrase "whenever Claude runs any git command" is vague for automated agent-discovery systems. These systems scan description text for concrete action verbs and noun phrases — specific terms like `git commit`, `git branch`, `git push`, `rebase`, `pull request`, and `release tag` must appear explicitly so keyword-based matching and semantic indexing fire correctly.

### Before
```
description: Applies this user's git conventions for branches, commits, merges, pull requests, force-pushes, and release tags whenever Claude runs any git command.
```

### After
```
description: Enforces git conventions for branch naming, commit messages, merges, pull requests, force-push safety, and release tags. Use whenever running git commit, branch, merge, push, rebase, or tag commands, or when opening/updating a pull request.
```

### Impact if implemented
- **Agent behaviour:** Agents performing skill-selection via keyword scan will match this skill on explicit triggers: `git commit`, `git push`, `git tag`, `rebase`, `pull request`, `branch`. Previously, the vague phrase "any git command" could be missed by exact-match keyword scanners.
- **Discoverability:** Semantic search and keyword-indexed registries will surface this skill for queries like "how do I commit", "open a PR", "create a release tag", or "push my branch" — searches that the current description does not reliably match.
- **Portability:** A clearer description reduces the need for teams to read the full body before deciding whether the skill applies to their workflow. This accelerates adoption.
- **Risk reduced:** Prevents the skill from being skipped by an agent that is scanning descriptions for activation triggers — a missed activation means git conventions are not applied, leading to non-compliant branches, commits, or PRs.

### Existing use (before fix)
When an agent is about to run `git commit -m "fix stuff"`, it scans available skill descriptions for relevant triggers. The current description's phrase "whenever Claude runs any git command" is generic enough that a keyword scanner might not score it highly against the specific query `git commit`. The skill body contains a good "When to use" section, but agents that rely on description-level matching never reach the body — the skill is not activated, and the commit is made without any convention enforcement.

### Improved use (after fix)
With the rewritten description, an agent scanning for `git commit`, `pull request`, or `release tag` will find an explicit match in the description itself, triggering the skill before any git action is taken. The "When to use" body section then reinforces the decision. The result is reliable, consistent activation of all six convention steps — branch naming, commit format, merge discipline, PR structure, force-push safety, and release tagging — every time they are relevant.

---

## Improvement 4 — Add a Note on `email` Field Exposure in `metadata`

### What needs to change

The frontmatter currently exposes `email: arijit.saha@zysk.tech` as a direct metadata field. While the spec permits this, it is an operational risk when the skill is published to a public or shared registry — the email address becomes machine-readable and crawlable. The improvement is to add a comment (or update the field to reference a GitHub handle or org URL instead) to make the exposure intentional and documented, or to replace it with a less sensitive contact reference.

### Before
```yaml
author: Arijit Saha
email: arijit.saha@zysk.tech
```
(top-level, unguarded, no acknowledgement of exposure risk)

### After
```yaml
metadata:
  author: Arijit Saha
  # email exposed intentionally for internal registry contact; remove before publishing publicly
  email: arijit.saha@zysk.tech
  # alternatively: contact: https://github.com/arijitsaha
```

### Impact if implemented
- **Agent behaviour:** No runtime change — agents do not act on the `email` field. This is a human/operational improvement.
- **Discoverability:** No effect on discoverability.
- **Portability:** Teams forking this skill for their own registries are reminded to strip or replace the email before publishing externally, preventing accidental PII exposure.
- **Risk reduced:** Reduces risk of the `zysk.tech` email address being harvested by crawlers scanning open skill registries. Makes the decision to include or exclude the email an explicit, documented choice rather than an oversight.

### Existing use (before fix)
The `email: arijit.saha@zysk.tech` field sits at the top level of the frontmatter with no indication of whether it is intended for internal or public consumption. When the skill is published to a public registry, the email address is trivially machine-readable. Crawlers scanning YAML frontmatter in public GitHub repositories or skill registries can harvest this address without any indication that the author intended it to be private.

### Improved use (after fix)
After adding an inline comment that flags the exposure, any developer who forks or publishes the skill is immediately reminded to evaluate whether the email should be retained. Teams publishing to public registries will strip it or replace it with a GitHub profile URL, keeping contact information appropriately scoped. The intent of the field is explicit rather than ambiguous, and the operational risk is reduced to near zero with a one-line comment cost.

---

## Improvement 5 — Add `compatibility` Field to Declare the `git` Tool Dependency

### What needs to change

Although the analysis notes that absence of `compatibility` is acceptable because `git` is universally available, adding a minimal `compatibility` block is a positive signal to agents and registry consumers: it makes the single external dependency (`git`) explicit, confirms no cloud service or paid API is required, and future-proofs the skill if a platform-specific variant is ever needed (e.g., a Windows-only or Linux-only variant). This is a low-effort improvement with meaningful discoverability and trust benefits.

### Before
```yaml
---
name: git-workflow
description: Applies this user's git conventions ...
# no compatibility field
---
```

### After
```yaml
---
name: git-workflow
description: Enforces git conventions for branch naming, commit messages, merges, pull requests, force-push safety, and release tags. Use whenever running git commit, branch, merge, push, rebase, or tag commands, or when opening/updating a pull request.
license: MIT
compatibility:
  tools:
    - git
metadata:
  ...
---
```

### Impact if implemented
- **Agent behaviour:** Agents that check `compatibility.tools` before activating a skill will confirm `git` is available in the environment before applying conventions — preventing activation in non-git contexts.
- **Discoverability:** Registries that filter by required tools will correctly include this skill in results for "git skills" and exclude it from "no-dependency" or "web-only" collections.
- **Portability:** A team browsing the registry can immediately see that this skill requires only `git` — no API keys, no cloud services, no npm install — making adoption frictionless.
- **Risk reduced:** Explicitly declaring `git` as the only tool dependency prevents confusion about whether the skill needs GitHub CLI, a CI service, or any other tooling.

### Existing use (before fix)
A developer browsing the skill registry sees `git-workflow` and must read the full body to determine what tooling it requires. An agent in a non-git environment (e.g., an SVN repo or a plain file editor context) has no frontmatter signal to prevent accidental activation. The skill silently applies git-specific conventions in an environment where git commands may not exist, potentially producing confusing output or errors.

### Improved use (after fix)
With `compatibility.tools: [git]` declared, an agent can short-circuit activation in non-git environments before reading a single line of the body. Registry browsing immediately communicates "this skill needs git only — no other setup". The skill's zero-dependency nature becomes a documented feature rather than an implicit assumption, making it one of the easiest skills in the registry to adopt and trust.

---

## Priority Order

| Priority | Improvement | Effort | Impact |
|---|---|---|---|
| 1 | Move non-standard frontmatter fields under `metadata:` | Low | Critical |
| 2 | Add the required `license` field | Low | Critical |
| 3 | Strengthen `description` with explicit trigger keywords | Low | High |
| 4 | Add `compatibility` field to declare `git` tool dependency | Low | Medium |
| 5 | Add note on `email` field exposure in `metadata` | Low | Medium |

---

## Before vs After: Full Skill Experience

### Before (current state)

A developer discovers `git-workflow` in the skills registry and tries to validate it before adopting it in their team's CI pipeline. The spec validator immediately returns two hard failures: the `license` field is absent, and seven fields (`version`, `author`, `email`, `category`, `tags`, `product`, `sprint`, `tested_with`) are sitting at the top level of the frontmatter instead of under `metadata:`. The skill is rejected by the automated ingestion pipeline. A developer who pushes past the validator notices the `tags` block was silently ignored — searches for `git` or `commits` in the registry return zero results for this skill, even though it is the most directly relevant one. The `email` field is also sitting unguarded at the top level, where any public crawler can harvest it.

Meanwhile, an agent about to run `git commit -m "fix stuff"` scans skill descriptions for activation triggers. The description reads "whenever Claude runs any git command" — a phrase that passes human comprehension but scores weakly against a keyword scanner looking for `git commit`, `push`, or `branch`. The skill is not activated. The commit is made with a vague past-tense message and no issue reference, violating the conventions the skill was written to enforce. The branch was also named `feature/loginretrylogicfix` — 28 characters, no type prefix abbreviation, violating the 20-char rule in Step 1. None of this is caught because the skill never fired.

### After (all improvements applied)

With all five improvements applied, the frontmatter is fully spec-compliant. The `license: MIT` field is present, the seven metadata fields are correctly nested under `metadata:`, and the `compatibility.tools: [git]` block explicitly declares the single dependency. The CI validation pipeline passes with zero errors or warnings. Registry tag indexing correctly picks up `git`, `version-control`, `commits`, `branching`, and `pull-requests` from `metadata.tags`, so the skill appears at the top of results for all relevant searches.

The rewritten description — "Enforces git conventions for branch naming, commit messages, merges, pull requests, force-push safety, and release tags. Use whenever running git commit, branch, merge, push, rebase, or tag commands, or when opening/updating a pull request." — now contains every concrete trigger keyword an agent needs. When the agent is about to run `git commit`, it finds an explicit match in the description and activates the skill before executing the command. The six-step convention flow fires: the branch is named `feat/login-retry` (18 chars, valid), the commit message is written in present tense with an issue reference (`Add login retry on 401 #42`), the PR is opened with a clear imperative title, linked issues, labels, and assigned reviewers. Force-push is blocked unless truly necessary, and any tag created follows semantic versioning with an annotated message.

The `email` field is now accompanied by an inline comment flagging the exposure decision, so any developer who forks the skill for a public registry is reminded to evaluate whether to retain it. The overall skill is clean, portable, and trustworthy — a team can adopt it in under two minutes, confident that the metadata is valid, the license is clear, the dependency is declared, and the agent will activate it reliably every time a git operation is in scope.
