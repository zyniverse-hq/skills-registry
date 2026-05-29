# ANALYSIS - integratekit

> Generated against the [agentskills.io](https://agentskills.openml.io) standard.

---

## Overall Verdict

**Partially compliant.** The skill has excellent body structure - clear phases, concrete code examples, and well-defined edge-case handling - and its name and description both meet spec. However, eight non-standard frontmatter fields (`version`, `author`, `email`, `category`, `tags`, `product`, `sprint`, `tested_with`) are placed directly at the top level instead of nested under `metadata:`, which is a spec violation. Additionally, the body hardcodes absolute Windows paths to a specific developer's machine, making the skill non-portable and unusable by anyone else.

---

## Spec Compliance Checklist

| Check | Status | Detail |
|---|---|---|
| `name` field format | PASS | `integratekit` - lowercase letters only, no hyphens, 12 chars, matches folder name |
| `description` present & non-empty | PASS | 162 chars, well within 1-1024 range |
| `description` describes what it does | PASS | "find and wire up backend GraphQL APIs into frontend components" is clear |
| `description` describes when to use it | PASS | "Scans for unwired actions, discovers matching APIs, and integrates after confirmation" gives good context |
| `license` field | FAIL | Missing entirely |
| `compatibility` field | - | Not present; not required but strongly recommended for stack-specific skills |
| `metadata` field structure | FAIL | `version`, `author`, `email`, `category`, `tags`, `product`, `sprint`, `tested_with` are all top-level; spec requires custom fields nested under `metadata:` |
| `allowed-tools` field | - | Not present; optional, acceptable to omit |
| Token budget (body) | PASS | ~4,628 tokens estimated (18,513 chars / 4); under 5,000 token budget |
| Line budget (body) | WARN | 477 lines - under 500-line hard limit but exceeds 400-line warn threshold |
| `scripts/` directory | - | Not present; not required (no scripts referenced) |
| `references/` directory | - | Not present; not applicable |
| `assets/` directory | - | Not present; not applicable |
| Body - step-by-step instructions | PASS | Four clearly numbered phases with ordered sub-steps per phase |
| Body - examples | PASS | Concrete formatted output blocks for Phase 2a, Phase 2b report, conflict block, and Phase 4 summary |
| Body - edge cases | PASS | Covers: all actions already wired, docs not found, conflict detection, enum value resolution, docs-vs-resolver mismatch, lazy vs eager query distinction |

---

## What the Skill Gets Right

- The four-phase workflow (Scan, Discover, Confirm, Wire, Summarize) is logical and the confirmation gate before Phase 3 prevents unreviewed edits.
- The pre-flight conflict check is a strong safety mechanism that prevents overwriting existing definitions silently.
- The three action-type taxonomy (mutation, lazy query, eager query) maps directly to distinct wiring patterns, with clear step-by-step instructions for each.
- Code templates for each pattern (`mutations.js`, `queries.js`, `masterdatav2.service.ts`, component) are concrete and immediately usable.
- Enum resolution instructions explicitly warn against using Python member names and show how to retrieve the actual wire values - a subtle but important correctness detail.
- The "When to use" section has precise trigger phrases and a clear negative ("Do NOT activate for backend-only changes") that helps agents decide correctly.
- Snackbar message rules (tone, severity, placement in try/catch vs finally) are explicit and consistent.
- The Phase 2b discovery algorithm has a clear priority order (docs then resolvers fallback) with normalization logic explained step by step.

---

## Violations (Must Fix)

### 1. Non-standard frontmatter fields not nested under `metadata:`

The spec requires that all custom fields be placed under a `metadata:` key. Eight fields violate this:

**Current:**
```yaml
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
```

**Fix:**
```yaml
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
```

### 2. Absolute hardcoded machine-specific paths (portability failure)

The `## Repos` section and multiple references throughout Phase 2b embed absolute Windows paths tied to a single developer's machine. These paths will be wrong for every other user and environment.

**Current (examples):**
```
C:\Users\VishakGowda\Projects\TRALEXHO\txo-latest\txo-events-app\src
C:\Users\VishakGowda\Projects\TRALEXHO\masterdata-management-api-v2\docs\*.md
src\api\common\types\
```

**Fix - Option A (preferred):** Remove the `## Repos` section and instruct the agent to infer paths from the user's prompt or working directory:

```markdown
## Repos

The user must supply (or the agent must infer from the prompt or working directory):
- Frontend src/ root
- Backend project root (Python API)
- Backend docs/ subdirectory
- Backend src/api/models/ subdirectory for resolvers
```

**Fix - Option B:** Move concrete paths into `metadata:` as project-specific defaults and add a `compatibility:` field documenting the required environment.

### 3. `license` field is missing

The spec lists `license` as an expected field. Its absence means consumers cannot determine the terms under which the skill may be used or distributed.

**Fix:** Add to frontmatter:
```yaml
license: MIT
```

---

## What's More Than Needed (Consider Restructuring)

### Snackbar message rules are verbose and partially duplicated

The snackbar rules block under the mutation pattern lists six bullet points with multiple inline code examples. A shorter version then reappears under the lazy query pattern. Consider consolidating into a single `## Message and Feedback Rules` section referenced from both patterns to reduce repeated lines and body length.

### Phase 2b formatted output example is large

The confirmation report example block (44 lines of ASCII-art formatting and field listings) is helpful but could be trimmed by 30-40% without losing meaning. Doing so would bring the body comfortably under the 400-line warn threshold.

---

## What's Missing (Must Add)

1. **`license` field** - Add `license: MIT` (or the appropriate license) to frontmatter.

2. **`compatibility` field** - This skill is tightly coupled to a specific stack (React, Apollo Client, Strawberry GraphQL Python backend). Adding a `compatibility:` field helps agents and users know upfront what environment is required. Example:
   ```yaml
   compatibility: React frontend with Apollo Client; Python/Strawberry GraphQL backend. Requires read access to both frontend src/ and backend resolver source files.
   ```

3. **Portable path handling** - Replace all hardcoded absolute paths with instructions for the agent to resolve paths from context (working directory, user prompt, or a project config file). This is the single biggest portability blocker; without fixing it the skill cannot be used outside the original author's machine.

4. **Additional trigger keywords in description** - The description covers "wire up" and "GraphQL APIs" but misses common phrasings like "connect component to backend", "hook up API", or "add API call to component". Adding one or two within the 1024-char limit would improve agent discovery.

---

## Summary Table

| Area | Status | Detail |
|---|---|---|
| `name` field | Pass | Valid format, matches folder name, 12 chars |
| `description` field | Pass | Clear, informative, includes good trigger keywords |
| `license` field | Missing | Not present in frontmatter |
| `compatibility` field | - | Absent; strongly recommended given stack-specific requirements |
| `metadata` structure | Wrong | 8 custom fields at top level instead of nested under `metadata:` |
| Token budget | Pass | ~4,628 estimated tokens; within 5,000 budget |
| Line budget | Warn | 477 lines; exceeds 400-line warn threshold, within 500-line limit |
| Body structure | Excellent | Clear phases, ordered steps, concrete code templates, edge cases covered |
| Self-containment / portability | Fails | Hardcoded absolute paths to a single developer's machine make the skill unusable in any other environment |
