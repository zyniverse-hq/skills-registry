---
name: integratekit
description: Use this skill to find and wire up backend GraphQL APIs into frontend components. Scans for unwired actions, discovers matching APIs, and integrates after confirmation.
metadata:
  version: 1.1.0
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

# IntegrateKit

You are helping a frontend developer find and integrate backend GraphQL APIs. The developer builds the UI first without knowing the backend API, then uses this skill to find the right API and wire it up.

## When to use

- Activate when the user says "integrate X API", "add X to frontend", "wire up X", or "check the API for this component"
- Activate when the user provides a component path and asks to connect it to the backend
- Do NOT activate for backend-only changes or when no component path is provided

## Steps

1. **Phase 1** — Scan the component for unwired actions
2. **Phase 2** — Discover matching backend APIs and present a confirmation report
3. **Phase 3** — Wire up after user confirms
4. **Phase 4** — Show a summary of all changes made

## Output

- **Format:** Code edits to `mutations.js`, `queries.js`, `masterdatav2.service.ts`, and the component file
- **Location:** Inline file edits across the frontend project
- **Example:** New GraphQL mutation + service method + wired handler in the component

---

## Repos

Resolve these once at the start. If the user hasn't provided the repo roots, ask for the
frontend root and the backend root, then derive the rest. Use forward slashes in all paths.

- **Frontend src:** `<frontend-root>/src`
- **Backend root:** `<backend-root>`
- **Backend docs:** `<backend-root>/docs`
- **Backend resolvers:** `<backend-root>/src/api/models`

## Frontend Conventions (always follow, never ask)

- Queries → `src/graphql/queries.js`
- Mutations → `src/graphql/mutations.js`
- All service methods → `src/services/masterdatav2.service.ts`
- Apollo query: `this.__apolloClient.query({ query, variables, fetchPolicy: "network-only" })`
- Apollo mutation: `this.__apolloClient.mutate({ mutation, variables, fetchPolicy: "network-only" })`
- Service method names: camelCase matching the GraphQL operation (e.g. `saveRecord`)
- GraphQL const names: PascalCase (e.g. `SaveRecord`)
- New service methods appended at the end of the class, just before the closing `}`

---

## Phase 1 — Scan the Component

The user provides a component path. Read that file and scan for:

1. **Action handlers** — `onClick`, `onSubmit`, form submit handlers, button press handlers, `onBlur`/`onChange` handlers that trigger data fetches.
2. **Existing service calls** — any `masterDataV2Service.xxx()` calls inside those handlers.
3. **Existing Apollo hooks** — any `useQuery(...)` or `useLazyQuery(...)` already in the component body.
4. **Data shape** — state variables, form fields, TypeScript interfaces that show what data the UI is collecting or expecting.

From this scan, classify each unwired action into one of three types:

- **Mutation action** — sends data to the backend (save, publish, delete, submit). Wired via service method.
- **Lazy query action** — user-triggered data fetch (onBlur availability check, onChange search). Wired via `useLazyQuery` directly in the component.
- **Eager query** — data loaded automatically on mount or when a dependency changes (load by ID, load list). Wired via `useQuery` with `skip` directly in the component.

Then determine:
- Which actions already call a service method or Apollo hook → **INTEGRATED**
- Which actions have no backend call yet → **NOT INTEGRATED** (note the type for each)

---

## Phase 2a — All Actions Already Wired

If every action in the component already calls a service method, present this and stop:

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  IntegrateKit — "<feature>"
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Component: <path>

APIs already in place:

[MUTATION] saveRecord
  Purpose:  Create or update a record (draft / publish)
  Used in:  handleSubmit(), handlePublish()
  Method:   masterDataV2Service.saveRecord()

[QUERY] getRecordById
  Purpose:  Load record data on edit
  Used in:  useEffect on mount
  Method:   masterDataV2Service.getRecordById()

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
All APIs are already wired. No integration needed.
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

---

## Phase 2b — API Not Wired

For every unwired action, find the matching API using auto-discovery. Search in this order:

### Step 1 — Docs (primary)

Extract the feature name from the **prompt** — it is the part that describes the feature, not the component. It appears before the component path or before a dash/separator.

Examples:
- `"Order management — order form UI is ready at @src/..."` → feature name is `"order management"`
- `"Check and integrate order management APIs for @src/..."` → feature name is `"order management"`

Do NOT derive the feature name from component variable names, file names, or code found during the Phase 1 scan — those will mislead the search (e.g. seeing `orderName` or `orderStatus` in the code does not mean the feature is called "order status" — use the feature name from the prompt).

Normalize the extracted feature name: lowercase, replace spaces and hyphens with underscores.
Example: `"order management"` → `order_management`

Glob the docs folder: `<backend-root>/docs/*.md`

Find the file whose name normalizes to the same value (case-insensitive, hyphens and underscores treated as equivalent):
- `My-Feature.md` → `my_feature` ✓
- `my_feature.md` → `my_feature` ✓

If a match is found, read it to get operation names, purpose, and input/output shape.

### Step 2 — Resolvers (always, to verify exact field names)

Docs can be outdated. Always verify against the Python source.

Derive the module folder from the docs filename (same normalization):
`My-Feature.md` → `my_feature` → `<backend-root>/src/api/models/my_feature/`

List files in that folder and read the relevant `*_mutation.py` or `*_query.py` file.
Get **exact** field names from the Python `@strawberry.input` class — Strawberry auto-converts `snake_case` → `camelCase` in GraphQL.

**Enum resolution — always look up actual string values:**
When a field's type is a `@strawberry.enum` class (e.g. `RecordStatus`, `RecordAccess`), do NOT use the Python member names as values. Instead:
1. Grep `<backend-root>/src/api/common/types/` for the enum class name to find its definition.
2. Read the actual string values from the `member = "value"` pattern inside the class.
3. Use those exact string values everywhere — in the Phase 2b report and in the Phase 3 component code.

Example: Python `RecordStatus` has `draft = "draft"` and `published = "published"` → report as `"draft" | "published"`, wire as `status: "draft"` or `status: "published"`.

Never assume enum values are uppercase. The member name (`DRAFT`, `PUBLISHED`) is not the wire value — the assigned string (`"draft"`, `"published"`) is.

### If docs not found

Skip Step 1. Go directly to Step 2 — normalize the feature name, glob `<backend-root>/src/api/models/` for a matching folder, read the resolver files directly.

If no match found in either place, tell the user: "No matching backend API found for this action. Point me to the specific resolver file if you know it."

Show **all** unwired actions and their APIs together in one report. For each, note the wiring type:
- `[MUTATION]` — will be added to mutations.js + service method + component handler
- `[LAZY QUERY]` — will be added to queries.js + `useLazyQuery` hook in component
- `[QUERY]` — will be added to queries.js + `useQuery` hook with `skip` in component

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  IntegrateKit — "<feature>"
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Component: <path>

UI scan: Found 2 unwired actions.

─────────────────────────────────────
[MUTATION] saveRecord
  Action:  handleSubmit(), handlePublish()
  Purpose: Create or update a record (draft / publish / archive)

  Input (RecordInput):
    orgId:       String!
    name:        String!
    groupId:     String     (optional)
    metadata:    JSON       (optional)
    status:      String     (draft | published)
    description: String     (optional)
    access:      String     (optional)
    id:          Int        (optional, required when updating)
    isArchived:  Boolean    (optional)
    timezone:    String!

  Returns: data: JSON

─────────────────────────────────────
[LAZY QUERY] checkNameAvailability
  Action:  handleNameBlur()
  Purpose: Check if name is already taken for this org

  Params:
    name:   String!
    orgId:  String

  Returns:
    isAvailable: Boolean
    message:     String

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Confirm integration? (yes / no)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

Wait for confirmation before Phase 3.
- `yes` — proceed
- `no` — abort

---

## Pre-flight — Conflict Check

Before writing anything, grep each target file for the operation names discovered in Phase 2b:

- `mutations.js` → search for the mutation const name (e.g. `SaveRecord`)
- `queries.js` → search for the query const name (e.g. `CheckNameAvailability`)
- `masterdatav2.service.ts` → search for the method name (e.g. `saveRecord(`)

For each match found, read the existing definition and compare field-by-field against the Python resolver source:

| Situation | Action |
|-----------|--------|
| Exists and **matches** the resolver | Log `[SKIP] <name> — already up to date` and skip that file edit |
| Exists but **differs** from the resolver (missing fields, wrong types, renamed fields) | Show a `[CONFLICT]` block with the diff and ask: "Update existing definition? (yes / no)" |
| Does not exist | Proceed to add it |

Conflict block format:
```
[CONFLICT] CheckNameAvailability already exists in queries.js but differs from backend:

  Existing:  ($name: String!, $orgId: String)
  Backend:   ($name: String!, $orgId: String!)   ← orgId is now required

Update? (yes / no)
```

Only proceed to Phase 3 for operations that passed (new or confirmed update). Skip the rest.

---

## Phase 3 — Wire Up

After confirmation, wire up each action. The full step-by-step edit patterns — `mutations.js`,
`queries.js`, `masterdatav2.service.ts`, and the component wiring for the three action types
(mutation, lazy query, eager query), plus the success/error message rules — live in
`references/wiring-patterns.md`. **Read that file when you reach this phase**, then apply the
edits in the exact order it specifies.

---

## Phase 4 — Summary

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  IntegrateKit — Done ✓
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Added to mutations.js:
  + SaveRecord

Added to queries.js:
  + CheckNameAvailability

Added to masterdatav2.service.ts:
  + saveRecord()

Wired in component:
  + useMasterDataV2Service hook
  + handleSubmit()   → saveRecord (draft)      [MUTATION]
  + handlePublish()  → saveRecord (published)  [MUTATION]
  + handleNameBlur() → checkNameAvailability   [LAZY QUERY]

Skipped (conflict check):
  [SKIP] listRecords — already up to date in queries.js
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

---

## Rules

- **Never skip Phase 2.** Always show the full report for all unwired actions and wait for confirmation before editing.
- **Always read the Python resolver source** to verify field names and types — docs can be outdated.
- **Always run the Pre-flight conflict check** before writing to any file.
- **Lazy queries are wired directly in the component** via `useLazyQuery` — never through the service layer.
- **Eager queries** can go through the service layer or directly as `useQuery` depending on whether other components also need the same fetch.
- **If no matching API is found** in docs or resolvers, tell the user: "No matching backend API found for this action. Point me to the specific resolver file if you know it."
