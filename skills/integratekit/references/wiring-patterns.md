# Phase 3 Wiring Patterns

Read this when you reach **Phase 3 — Wire Up** (after the user confirms in Phase 2b and the
pre-flight conflict check has passed). Apply the edits in the exact order below.

## 1. mutations.js — append new mutation
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

## 2. queries.js — append new query (if lazy query or eager query)

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

## 3. masterdatav2.service.ts

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

## 4. Component — wire up the service call and Apollo hooks

Edit the component file to wire each action based on its type.

---

### For mutation and eager query actions — service method pattern

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

### For lazy query actions — useLazyQuery pattern

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

### For eager query actions — useQuery pattern

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
