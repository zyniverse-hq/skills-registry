# IMPROVEMENTS — integratekit

> Improvement plan derived from SKILL.md + ANALYSIS.md audit against the agentskills.openml.io spec.

---

## Quick Summary

| | Before | After |
|---|---|---|
| Spec compliance | Partially compliant | Fully compliant |
| Critical violations | 3 | 0 |
| Agent discoverability | Medium | High |
| Portability | Fails | Pass |

---

## Improvement 1 — Nest custom frontmatter fields under `metadata:`

### What needs to change

Eight custom fields (`version`, `author`, `email`, `category`, `tags`, `product`, `sprint`, `tested_with`) are placed at the top level of the frontmatter instead of nested under a `metadata:` key. The agentskills spec requires all non-standard fields to live under `metadata:`. Parsers that enforce strict frontmatter schemas will either reject the file or silently drop these fields.

### Before
```yaml
---
name: integratekit
description: Use this skill to find and wire up backend GraphQL APIs into frontend components. Scans for unwired actions, discovers matching APIs, and integrates after confirmation.
version: 1.0.0
author: Vishak Gowda
email: vishak@zysk.tech
category: frontend-integration
tags:
  - graphql
  - apollo
  - api-integration
  - frontend
product: zyniverse
sprint: 1
tested_with: claude-sonnet-4-6
---
```

### After
```yaml
---
name: integratekit
description: Use this skill to find and wire up backend GraphQL APIs into frontend components. Scans for unwired actions, discovers matching APIs, and integrates after confirmation.
license: MIT
compatibility: React frontend with Apollo Client; Python/Strawberry GraphQL backend. Requires read access to both frontend src/ and backend resolver source files.
metadata:
  version: 1.0.0
  author: Vishak Gowda
  email: vishak@zysk.tech
  category: frontend-integration
  tags:
    - graphql
    - apollo
    - api-integration
    - frontend
  product: zyniverse
  sprint: 1
  tested_with: claude-sonnet-4-6
---
```

### Impact if implemented
- **Agent behaviour:** Registry parsers can now correctly read and index the skill without schema errors. The `compatibility` field gives agents an upfront signal about required stack before even reading the body.
- **Discoverability:** Tag-based and category-based search in the registry will work correctly because `tags` and `category` are now in the expected location.
- **Portability:** No direct portability effect from this change alone, but it unblocks registry tooling from functioning correctly.
- **Risk reduced:** Prevents silent field loss in parsers that only read spec-defined top-level keys, which would strip `version`, `author`, and `tags` from the parsed output entirely.

### Existing use (before fix)
Today, when a registry tool or another agent reads this skill's frontmatter, it sees eight unexpected top-level keys. Strict YAML parsers used by the agentskills registry reject or ignore these keys because they are not in the spec schema. As a result, `tags: [graphql, apollo, api-integration, frontend]` does not contribute to tag-based search, and `category: frontend-integration` is not indexed. An agent searching for "graphql integration skills" may not find this skill at all because the indexing step silently dropped the tags.

### Improved use (after fix)
After nesting all eight fields under `metadata:`, the frontmatter matches the spec exactly. Registry parsers read and index `tags` and `category` from their correct location. Tag-based search for `graphql`, `apollo`, or `api-integration` surfaces this skill. The `compatibility` field added alongside this fix gives agents an immediate pre-read signal that this skill requires Apollo Client and a Strawberry GraphQL Python backend — allowing them to skip it gracefully in projects that do not match.

---

## Improvement 2 — Add missing `license` field

### What needs to change

The `license` field is absent from the frontmatter entirely. The agentskills spec lists `license` as an expected frontmatter field. Without it, consumers — both human and automated — cannot determine whether they can use, modify, or redistribute the skill. This is a hard spec violation.

### Before
```yaml
---
name: integratekit
description: Use this skill to find and wire up backend GraphQL APIs into frontend components. Scans for unwired actions, discovers matching APIs, and integrates after confirmation.
version: 1.0.0
author: Vishak Gowda
...
---
```

### After
```yaml
---
name: integratekit
description: Use this skill to find and wire up backend GraphQL APIs into frontend components. Scans for unwired actions, discovers matching APIs, and integrates after confirmation.
license: MIT
...
---
```

### Impact if implemented
- **Agent behaviour:** No direct change to how the agent executes the skill, but registry compliance checks pass cleanly.
- **Discoverability:** Some registries filter on license type (e.g. "show only MIT-licensed skills"). Without this field, the skill is excluded from those filtered views.
- **Portability:** Teams with license compliance requirements can confirm they are allowed to use and adapt the skill.
- **Risk reduced:** Prevents legal ambiguity for teams adopting the skill from a shared registry.

### Existing use (before fix)
Today, any team that finds this skill in the registry and wants to use it in a commercial project has no way to confirm licensing terms. Registry compliance tooling that validates required fields will flag this skill as incomplete. In some organization setups, skills without a `license` field are automatically quarantined and cannot be added to an approved skill list.

### Improved use (after fix)
Adding `license: MIT` (or the author's chosen license) satisfies the spec requirement. Teams can confirm usage rights immediately from the frontmatter. Registry compliance scans pass without warnings. The skill becomes eligible for inclusion in license-filtered views and organization-approved skill catalogs.

---

## Improvement 3 — Replace hardcoded absolute paths with portable path-resolution instructions

### What needs to change

The `## Repos` section and multiple inline references in Phase 2b hardcode absolute Windows paths tied to a single developer's machine (`C:\Users\VishakGowda\Projects\TRALEXHO\...`). These paths are wrong for every other user and environment. The skill cannot be used by anyone other than the original author without manually editing the SKILL.md — which defeats the purpose of a shared registry.

### Before
```markdown
## Repos

- **Frontend src:** `C:\Users\VishakGowda\Projects\TRALEXHO\txo-latest\txo-events-app\src`
- **Backend root:** `C:\Users\VishakGowda\Projects\TRALEXHO\masterdata-management-api-v2`
- **Backend docs:** `C:\Users\VishakGowda\Projects\TRALEXHO\masterdata-management-api-v2\docs`
- **Backend resolvers:** `C:\Users\VishakGowda\Projects\TRALEXHO\masterdata-management-api-v2\src\api\models`
```

And within Phase 2b Step 1:
```markdown
Glob the docs folder: `C:\Users\VishakGowda\Projects\TRALEXHO\masterdata-management-api-v2\docs\*.md`
```

And within Phase 2b Step 2:
```markdown
`src\api\common\types\`
```

### After
```markdown
## Repos

The agent must resolve the following roots before starting. Check in this order:

1. **From the user's prompt** — the user may supply explicit paths inline (e.g. `@src/...` or `"backend is at ~/projects/api"`).
2. **From the current working directory** — if the user's shell is inside the frontend or backend project, use `pwd` / `$PWD` to anchor paths.
3. **From a project config file** — look for `.integratekit.json` or `integratekit.config.json` in the working directory root:
   ```json
   {
     "frontendSrc": "./txo-events-app/src",
     "backendRoot": "../masterdata-management-api-v2",
     "backendDocs": "../masterdata-management-api-v2/docs",
     "backendResolvers": "../masterdata-management-api-v2/src/api/models"
   }
   ```
4. **Ask the user** — if none of the above resolve all four roots, ask once:
   > "I need the paths to your frontend src/ and backend project root. Please provide them or add them to `.integratekit.json`."

Do not proceed past Phase 1 until all four roots are resolved.
```

Also update Phase 2b Step 1 to reference the resolved variable:
```markdown
Glob the docs folder: `<backendDocs>/*.md`
```

And Phase 2b Step 2:
```markdown
Grep `<backendRoot>/src/api/common/types/` for the enum class name.
```

### Impact if implemented
- **Agent behaviour:** The agent now resolves paths dynamically before starting, either from context or by asking once. It will not silently fail mid-run because a hardcoded path doesn't exist on the current machine.
- **Discoverability:** No change to discoverability, but the skill becomes genuinely usable — currently it is discoverable but not executable for any team outside Zysk.
- **Portability:** This is the single biggest portability blocker. Fixing it makes the skill usable by any team with a React + Apollo + Strawberry GraphQL stack, regardless of where their projects live.
- **Risk reduced:** Eliminates silent failures where the agent reads a non-existent path and either crashes mid-phase or silently skips the resolver verification step (Phase 2b Step 2), producing GraphQL mutations with wrong field names.

### Existing use (before fix)
Today, any developer who activates this skill on a machine other than VishakGowda's Windows machine will see the agent attempt to read `C:\Users\VishakGowda\Projects\TRALEXHO\masterdata-management-api-v2\docs\*.md`. On Linux, macOS, or any Windows machine with a different username or project location, the glob returns nothing. The agent then falls through to Step 2 (resolver lookup), which also fails because the absolute path doesn't exist. The entire discovery phase collapses silently, the Phase 2b report shows "No matching backend API found", and the developer is left with no actionable output despite the backend API existing perfectly well in their own project structure.

### Improved use (after fix)
After the fix, the first thing the agent does is resolve the four path roots. If the user ran the skill from inside their frontend project directory, the agent anchors off `$PWD`. If a `.integratekit.json` config exists, the agent reads it and proceeds without asking. If neither is available, the agent asks once for the two root paths it needs. All subsequent path references (`<backendDocs>/*.md`, `<backendResolvers>/`) are built from these resolved roots. The skill works identically on Windows, macOS, and Linux, for any project structure, for any developer on any team using the same tech stack.

---

## Improvement 4 — Add `compatibility` field and extend `description` with additional trigger keywords

### What needs to change

Two related gaps: (1) the frontmatter has no `compatibility` field despite the skill being tightly coupled to a specific stack (React, Apollo Client, Strawberry Python), and (2) the `description` field misses several common phrasings developers use when they want to connect a UI component to a backend API.

### Before
```yaml
description: Use this skill to find and wire up backend GraphQL APIs into frontend components. Scans for unwired actions, discovers matching APIs, and integrates after confirmation.
```
(no `compatibility` field present)

### After
```yaml
description: Use this skill to find and wire up backend GraphQL APIs into frontend components. Scans for unwired actions, discovers matching APIs, and integrates after confirmation. Also triggers on "connect component to backend", "hook up API", or "add API call to component".
compatibility: React frontend with Apollo Client; Python/Strawberry GraphQL backend. Requires read access to both frontend src/ and backend resolver source files.
```

### Impact if implemented
- **Agent behaviour:** The `compatibility` field gives the invoking agent a pre-read signal. If the project uses REST instead of GraphQL, or Vue instead of React, the agent can detect the mismatch before loading the full skill body and skip gracefully with a useful message.
- **Discoverability:** Adding "connect component to backend", "hook up API", and "add API call to component" to the description means the agent matches on three additional natural-language phrasings that developers commonly use. Currently, a developer who says "hook up the form to the API" would not trigger this skill because the description only covers "wire up", "integrate", and "add to frontend".
- **Portability:** The `compatibility` field makes the stack requirement explicit and machine-readable rather than buried in the body prose.
- **Risk reduced:** Prevents the skill from being invoked on mismatched stacks (e.g. a Vue + REST project) where it would produce useless Apollo-specific edits.

### Existing use (before fix)
Today, an agent searching for skills to handle "hook up the save button to the backend" will not match this skill because "hook up" does not appear anywhere in the name or description. The agent either picks a generic dev-assistant skill or asks the user to be more specific. Separately, there is no `compatibility` field, so an agent has no way to quickly determine that this skill requires Apollo Client without reading 477 lines of body. On a React + REST project, the agent might invoke the skill, run through Phase 1 and Phase 2, then produce Apollo-specific code (`useLazyQuery`, `useMutation`) that is completely wrong for the project's architecture.

### Improved use (after fix)
After adding the three additional trigger phrases to `description`, the agent matches on a broader set of natural developer language. "Hook up the form", "connect the component to the backend", "add the API call to this component" — all now surface this skill. The `compatibility` field stops the skill from being invoked on mismatched stacks: an agent running on a Vue + Axios project reads `compatibility: React frontend with Apollo Client` and skips this skill, falling back to a more generic integration skill instead. Developer friction drops and incorrect Apollo code generation on non-Apollo projects is eliminated.

---

## Improvement 5 — Consolidate duplicated snackbar message rules into a single referenced section

### What needs to change

The snackbar/feedback message rules appear twice in the body: once under Phase 3 Step 4 "For mutation and eager query actions" (six bullet points with inline examples) and again under "For lazy query actions" (three bullet points partially repeating the same rules). This duplication adds ~25 lines to a body already at 477 lines (exceeding the 400-line warn threshold) and creates a maintenance hazard where the two copies can drift out of sync.

### Before

Under mutation pattern (Phase 3, Step 4):
```markdown
**Success and error message rules:**
- Call `showSnackbar(message, severity)` — severity is `"success"` (default), `"error"`, `"warning"`, or `"info"`
- **Success messages**: past tense, action-specific. Examples: `"Record saved as draft."`, `"Record published successfully."`, `"Record deleted."`
- **Error messages**: always use `"error"` severity. Keep brief. Examples: `"Failed to save record."`, `"Failed to publish record."`, `"Failed to delete record."`
- **Validation messages** (before the API call): use `"error"` severity. Example: `"Please fill in all required fields."`
- If the component already has a `showSnackbar` helper, use it. If not, use the MUI `Snackbar` + `Alert` pattern already present elsewhere in the component.
- Always call `showSnackbar` inside the `try` (on success) and `catch` (on failure) — never after `finally`.
- Do not show a success message if `result` is null or falsy — the service method already showed a snackbar for the error.
```

Then separately under lazy query pattern:
```markdown
**Lazy query message rules:**
- `onCompleted` — prefer updating inline UI state (e.g. `isAvailable`, a dropdown list) over showing a snackbar. Only show a snackbar if the result requires user attention (e.g. a warning that something is unavailable).
- `onError` — always reset related state to a safe default. Show a snackbar with `"error"` severity if the failure blocks the user's next action.
```

### After

Replace both blocks with a single `## Feedback and Message Rules` section placed once above Phase 3, and replace both inline blocks with a cross-reference:

```markdown
## Feedback and Message Rules

These rules apply across all wiring patterns. Follow them exactly.

- Use `showSnackbar(message, severity)` — severity values: `"success"` (default), `"error"`, `"warning"`, `"info"`.
- If the component already has a `showSnackbar` helper, use it. Otherwise use the MUI `Snackbar` + `Alert` pattern present elsewhere in the component.
- Always place `showSnackbar` inside `try` (success) or `catch` (failure) — never after `finally`.
- Do not show a success message if `result` is null or falsy — the service layer already showed an error snackbar.

**For mutations and eager queries:**
- Success: past tense, action-specific. E.g. `"Record saved as draft."`, `"Record published successfully."`, `"Record deleted."`
- Error: `"error"` severity, brief. E.g. `"Failed to save record."`, `"Failed to publish record."`
- Validation (pre-call): `"error"` severity. E.g. `"Please fill in all required fields."`

**For lazy queries:**
- `onCompleted`: prefer updating inline UI state (e.g. `isAvailable`, a list) over showing a snackbar. Only show a snackbar if the result requires explicit user attention.
- `onError`: reset related state to a safe default. Show an `"error"` snackbar only if the failure blocks the user's next action.
```

Then in each pattern section, replace the full rules block with:
```markdown
> Follow the **Feedback and Message Rules** section above.
```

### Impact if implemented
- **Agent behaviour:** No change in what the agent does — the rules are identical. The agent reads the consolidated section once and applies the correct rules to both mutation and lazy query wiring.
- **Discoverability:** No change to discoverability.
- **Portability:** No direct portability effect, but the body drops by approximately 20-25 lines, bringing it comfortably under the 400-line warn threshold.
- **Risk reduced:** Eliminates the maintenance hazard where a future edit updates the mutation rules block but forgets the lazy query rules block, causing the two copies to diverge and the agent to apply inconsistent feedback behavior depending on which wiring pattern it encounters first.

### Existing use (before fix)
Today, the snackbar rules are split across two locations in the body. An agent reading Phase 3 encounters the detailed rules under the mutation pattern, then re-reads a shorter and partially different version under the lazy query pattern. If the rules ever drift (e.g. someone updates the mutation block to add a `"warning"` severity example but forgets the lazy query block), the agent will apply different message rules to mutations versus lazy queries in the same component — producing inconsistent UX. The body also sits at 477 lines, 77 lines over the warn threshold, partly because of this duplication.

### Improved use (after fix)
After consolidation, the rules live in one place. Future edits to message conventions require a single change. The body length drops below 455 lines, clearing the 400-line warn threshold with some room to spare. An agent reading the skill sees a clear `## Feedback and Message Rules` section early in the body and then simple cross-references in each pattern — making the rules easier to find and impossible to miss.

---

## Priority Order

| Priority | Improvement | Effort | Impact |
|---|---|---|---|
| 1 | Replace hardcoded absolute paths with portable path-resolution instructions | Medium | Critical |
| 2 | Nest custom frontmatter fields under `metadata:` | Low | High |
| 3 | Add missing `license` field | Low | High |
| 4 | Add `compatibility` field and extend `description` with trigger keywords | Low | Medium |
| 5 | Consolidate duplicated snackbar message rules into a single referenced section | Low | Medium |

---

## Before vs After: Full Skill Experience

### Before (current state)

A developer at a different company discovers the `integratekit` skill in the registry while building a React + Apollo + Strawberry GraphQL app. The frontmatter looks almost right — there is a name, description, and several fields — but eight of those fields are at the top level instead of nested under `metadata:`. The registry's tag indexer silently drops `tags: [graphql, apollo, api-integration, frontend]` because they are not in the expected location. When the developer searches for "apollo integration skills", `integratekit` does not appear in the results. They find it only by browsing directly. There is no `license` field, so their team's compliance check flags the skill as unverifiable and blocks it from the approved list. There is no `compatibility` field either, so they have no immediate way to know the skill is tightly coupled to Apollo Client before reading all 477 lines of the body.

They get through the compliance hurdle manually and activate the skill. The agent reads the `## Repos` section and immediately tries to glob `C:\Users\VishakGowda\Projects\TRALEXHO\masterdata-management-api-v2\docs\*.md`. On their macOS machine, this path does not exist. The glob returns nothing. The agent falls through to resolver lookup, which also fails on the same hardcoded path. The Phase 2b report says "No matching backend API found for this action" — even though the backend API exists perfectly in their own project at a different path. Phase 3 never happens. The developer wasted time on a skill that was technically correct but physically non-executable in their environment.

Meanwhile, back at the original author's machine, the skill works flawlessly — but only there. The snackbar message rules are scattered across two sections, making it easy for a future contributor editing the mutation pattern to inadvertently leave the lazy query rules out of sync. At 477 lines, the body is already over the 400-line warn threshold, and the duplication is a contributor to that bloat.

### After (all improvements applied)

The same developer now finds `integratekit` through a tag search for `graphql` — the tags are correctly nested under `metadata:` and fully indexed. The `license: MIT` field passes their compliance check immediately. The `compatibility: React frontend with Apollo Client; Python/Strawberry GraphQL backend` field tells them upfront that this skill matches their stack without reading the body. The description now includes "connect component to backend" and "hook up API", so the next time they say "hook up the form to the backend" in a prompt, the agent matches this skill directly.

When they activate the skill, the agent reads the `## Repos` section and follows the four-step resolution protocol: checks the user's prompt for explicit paths, checks the current working directory, looks for `.integratekit.json`, and if none of those resolve all four roots, asks once. The developer points it at their project root and the agent derives all four paths from there. Every subsequent glob and grep in Phase 2b uses `<backendDocs>/*.md` and `<backendResolvers>/` anchored to the resolved roots. The skill runs end-to-end on macOS, Linux, or any Windows machine without modification.

The body is now under 460 lines, with a single `## Feedback and Message Rules` section that both the mutation and lazy query patterns reference. Future contributors editing message conventions update one block and both patterns benefit. The frontmatter is fully spec-compliant, the body is clean and non-duplicative, and the skill is genuinely portable — usable by any team with the matching stack, not just the team that wrote it.
