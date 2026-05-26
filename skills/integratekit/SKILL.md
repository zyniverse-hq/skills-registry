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

- **Frontend src:** `C:\Users\VishakGowda\Projects\TRALEXHO\txo-latest\txo-events-app\src`
- **Backend root:** `C:\Users\VishakGowda\Projects\TRALEXHO\masterdata-management-api-v2`
- **Backend docs:** `C:\Users\VishakGowda\Projects\TRALEXHO\masterdata-management-api-v2\docs`
- **Backend resolvers:** `C:\Users\VishakGowda\Projects\TRALEXHO\masterdata-management-api-v2\src\api\models`

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

Glob the docs folder: `C:\Users\VishakGowda\Projects\TRALEXHO\masterdata-management-api-v2\docs\*.md`

Find the file whose name normalizes to the same value (case-insensitive, hyphens and underscores treated as equivalent):
- `My-Feature.md` → `my_feature` ✓
- `my_feature.md` → `my_feature` ✓

If a match is found, read it to get operation names, purpose, and input/output shape.

### Step 2 — Resolvers (always, to verify exact field names)

Docs can be outdated. Always verify against the Python source.

Derive the module folder from the docs filename (same normalization):
`My-Feature.md` → `my_feature` → `src\api\models\my_feature\`

List files in that folder and read the relevant `*_mutation.py` or `*_query.py` file.
Get **exact** field names from the Python `@strawberry.input` class — Strawberry auto-converts `snake_case` → `camelCase` in GraphQL.

**Enum resolution — always look up actual string values:**
When a field's type is a `@strawberry.enum` class (e.g. `RecordStatus`, `RecordAccess`), do NOT use the Python member names as values. Instead:
1. Grep `src\api\common\types\` for the enum class name to find its definition.
2. Read the actual string values from the `member = "value"` pattern inside the class.
3. Use those exact string values everywhere — in the Phase 2b report and in the Phase 3 component code.

Example: Python `RecordStatus` has `draft = "draft"` and `published = "published"` → report as `"draft" | "published"`, wire as `status: "draft"` or `status: "published"`.

Never assume enum values are uppercase. The member name (`DRAFT`, `PUBLISHED`) is not the wire value — the assigned string (`"draft"`, `"published"`) is.

### If docs not found

Skip Step 1. Go directly to Step 2 — normalize the feature name, glob `src\api\models\` for a matching folder, read the resolver files directly.

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

After confirmation, make edits in this exact order:

### 1. mutations.js — append new mutation
```js
export const OperationName = gql`
mutation OperationName($input: InputType!) {
  operationName(input: $input) {
    success
    error
  }
}
`
```

### 2. queries.js — append new query (if lazy query or eager query)

Select only the fields the component actually uses (check the component's state/useEffect/onCompleted logic). Do not select all fields from the Python type — only what is needed.

```js
export const OperationName = gql`
query OperationName($param: Type!) {
  operationName(param: $param) {
    field1
    field2
  }
}
`
```

### 3. masterdatav2.service.ts

Only for **mutations** and **eager queries** (not lazy queries — those are wired directly in the component in Step 4).

**Step A** — Add the new name to the existing import line at the top of the file.

**Step B** — Append the service method at the end of the class before the closing `}`:

For a mutation:
```ts
async operationName(variables: { input: { field: string; field2: string } }) {
    try {
        const { data } = await this.__apolloClient.mutate({
            mutation: OperationName,
            variables,
            fetchPolicy: "network-only",
        });
        return data?.operationName;
    } catch (error) {
        this.showSnackbar("Error <description>");
        return null;
    }
}
```

For an eager query (service-layer fetch):
```ts
async operationName(variables: { param: string }) {
    try {
        const { data } = await this.__apolloClient.query({
            query: OperationName,
            variables,
            fetchPolicy: "network-only",
        });
        return data?.operationName ?? null;
    } catch (error) {
        this.showSnackbar("Error fetching <description>");
        return null;
    }
}
```

### 4. Component — wire up the service call and Apollo hooks

Edit the component file to wire each action based on its type.

---

#### For mutation and eager query actions — service method pattern

**Step A** — Add `useMasterDataV2Service` to the imports (if not already present):
```tsx
import useMasterDataV2Service from "../../../hooks/useMasterDataV2";
```

**Step B** — Add the hook call inside the component function:
```tsx
const masterDataV2Service = useMasterDataV2Service();
```

**Step C** — Update each unwired mutation handler with an async service call. Keep the existing validation block unchanged. Match the input shape exactly to what was shown in Phase 2b.

```tsx
const handleSave = async () => {
    // keep existing validation block unchanged
    setSaveLoading(true);
    try {
        const result = await masterDataV2Service.operationName({
            input: {
                field1: value1,
                field2: value2,
            },
        });
        if (result) {
            showSnackbar("Record saved as draft.");
            handleReset();
        }
    } catch {
        showSnackbar("Failed to save record.", "error");
    } finally {
        setSaveLoading(false);
    }
};
```

If loading state vars were stubbed as read-only (`const [x] = useState`), restore them to full `useState` with setter.

**Success and error message rules:**
- Call `showSnackbar(message, severity)` — severity is `"success"` (default), `"error"`, `"warning"`, or `"info"`
- **Success messages**: past tense, action-specific. Examples: `"Record saved as draft."`, `"Record published successfully."`, `"Record deleted."`
- **Error messages**: always use `"error"` severity. Keep brief. Examples: `"Failed to save record."`, `"Failed to publish record."`, `"Failed to delete record."`
- **Validation messages** (before the API call): use `"error"` severity. Example: `"Please fill in all required fields."`
- If the component already has a `showSnackbar` helper, use it. If not, use the MUI `Snackbar` + `Alert` pattern already present elsewhere in the component.
- Always call `showSnackbar` inside the `try` (on success) and `catch` (on failure) — never after `finally`.
- Do not show a success message if `result` is null or falsy — the service method already showed a snackbar for the error.

---

#### For lazy query actions — useLazyQuery pattern

**Step A** — Add `useLazyQuery` to the Apollo import (add alongside any existing Apollo imports, or add new import if not present):
```tsx
import { useLazyQuery } from "@apollo/client";
```

**Step B** — Add the query const import from queries.js:
```tsx
import { OperationName } from "../../../graphql/queries";
```

**Step C** — Add the `useLazyQuery` hook in the component body (near other hook declarations):
```tsx
const [runOperationName, { loading: nameCheckLoading }] = useLazyQuery(OperationName, {
    fetchPolicy: "network-only",
    onCompleted: (data) => {
        // update relevant state from data?.operationName
        // only show a message if the result warrants user feedback
        // e.g. for availability checks: no snackbar — update inline state (isAvailable)
        // e.g. for a background load: no snackbar — silently populate state
    },
    onError: () => {
        // reset relevant state to null/false
        // show a snackbar only if the failure is something the user needs to act on
        // e.g. showSnackbar("Could not check availability. Try again.", "error")
    },
});
```

**Lazy query message rules:**
- `onCompleted` — prefer updating inline UI state (e.g. `isAvailable`, a dropdown list) over showing a snackbar. Only show a snackbar if the result requires user attention (e.g. a warning that something is unavailable).
- `onError` — always reset related state to a safe default. Show a snackbar with `"error"` severity if the failure blocks the user's next action.

**Step D** — Update the stub handler to call the lazy query:
```tsx
const handleNameBlur = () => {
    const trimmed = fieldValue.trim();
    if (!trimmed || !orgId) return;
    runOperationName({ variables: { param: trimmed, orgId } });
};
```

---

#### For eager query actions — useQuery pattern

**Step A** — Add `useQuery` to the Apollo import:
```tsx
import { useQuery } from "@apollo/client";
```

**Step B** — Add the query const import from queries.js:
```tsx
import { OperationName } from "../../../graphql/queries";
```

**Step C** — Add the `useQuery` hook in the component body. Use `skip` to prevent fetching until the required variables are available:
```tsx
const { data: operationData } = useQuery(OperationName, {
    variables: { id: Number(selectedId), orgId },
    skip: !selectedId || !orgId,
    fetchPolicy: "network-only",
});
```

**Step D** — Add a `useEffect` to consume the query result and update component state:
```tsx
useEffect(() => {
    if (operationData?.operationName) {
        const result = operationData.operationName;
        // populate state from result
    }
}, [operationData]);
```

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
