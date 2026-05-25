# Check: Expo SDK Compatibility

Validates that the Expo SDK, React Native, React, and the toolchain versions
form a supported combination for a **managed** project.

## Validation rules

1. **SDK pin must be explicit.** `expo` in `package.json` should resolve to a
   single major SDK (e.g. `~51.0.0`). A floating `*` or `latest` is CRITICAL.
2. **React Native must match the SDK.** Each Expo SDK ships with one
   supported React Native version. A mismatch is CRITICAL — EAS Build will
   either fail or produce an unstable binary.
3. **React must match React Native.** Wrong `react` / `react-dom` versions
   cause renderer crashes at runtime (HIGH).
4. **TypeScript & types** (`@types/react`, `typescript`) should match the
   SDK's recommended versions (MEDIUM if off, LOW if only patch-off).
5. **Single React/React Native instance.** Duplicate versions hoisted in a
   monorepo are CRITICAL (invariant violation / red screen).
6. **Node engine** should satisfy the SDK's minimum (recent SDKs require
   Node ≥ 18 LTS). Below minimum = HIGH.

## SDK → React Native → React reference map

Use this as the alignment source of truth. Always confirm against the live
`npx expo install --check` output when available, as point releases shift.

| Expo SDK | React Native | React | Min Node | Notes |
| --- | --- | --- | --- | --- |
| 55 | 0.83 | 19.2 | 20 | Current; New Architecture only (legacy arch removed) |
| 54 | 0.81 | 19.1 | 20 | New Architecture default on |
| 53 | 0.79 | 19.0 | 20 | New Architecture default on |
| 52 | 0.76 | 18.3 | 18 | New Architecture opt-in stabilizing |
| 51 | 0.74 | 18.2 | 18 | Hermes default; SDK 51 baseline |
| 50 | 0.73 | 18.2 | 18 | |
| 49 | 0.72 | 18.2 | 16 | |
| 48 | 0.71 | 18.2 | 16 | Older — recommend upgrade |

> The current GA SDK is **55** (React Native 0.83 / React 19.2). Treat
> anything ≥ 3 majors behind current (≤ SDK 52) as upgrade-recommended
> (MEDIUM) due to expiring EAS Build image support. SDK 55 removed the
> legacy architecture — every native-backed dependency must support the
> New Architecture (see `ios-managed-risks.md`).

## Common problems

- `expo@~51` but `react-native@0.73.x` (left behind from SDK 50 upgrade).
- `react@18.3.x` while SDK requires `18.2.x` → "Invariant Violation:
  Module AppRegistry is not a registered callable module".
- Monorepo hoists `react-native` at root **and** in the app → two copies.
- `expo` upgraded but `expo-router`, `expo-status-bar`, `expo-splash-screen`
  still on the old SDK's versions (see `dependency-alignment.md`).

## Warning patterns

- `Unable to resolve module` for a core RN/Expo module after upgrade.
- `requireNativeComponent` errors → JS/native version skew.
- Metro starts but app crashes on launch with a React invariant.
- `expo-doctor` "Expected package X@... but found Y".

## Recommended fixes

```bash
# Authoritative re-alignment to the pinned SDK
npx expo install --check      # report
npx expo install --fix        # apply — preserves each package's existing
                              # section (devDependencies stays devDependencies)

# If SDK itself is being changed, follow upgrade-checklist.md, not --fix alone
npx expo install expo@^55
npx expo install --fix
```

### Dev dependencies (typescript, @types/react, jest-expo, etc.)

`expo install --fix` keeps a package wherever it already lives, so dev tooling
already under `devDependencies` is realigned **in place** — do not move it to
`dependencies`.

When *adding* a new SDK-aligned dev dependency, forward `--save-dev` to the
package manager with `--` so it lands in `devDependencies`, not `dependencies`:

```bash
# npm / pnpm
npx expo install -- --save-dev typescript @types/react jest-expo
# yarn
npx expo install -- --dev typescript @types/react jest-expo
```

If a dev tool was mistakenly added to `dependencies`, move it back:

```bash
npm rm <pkg> && npx expo install -- --save-dev <pkg>
```

- Pin `expo` with `~` (tilde) to a single SDK major.
- Never hand-edit `react-native` / `react`; let `expo install` choose.
- In monorepos add `react`, `react-native` to `nohoist` or use the package
  manager's resolution pinning so only one copy exists.

## Example output

```
[CRITICAL] React Native version does not match Expo SDK
  expo: ~51.0.0  →  expects react-native@0.74.x
  found react-native@0.73.6
  Fix: npx expo install --fix   (will set react-native to 0.74.x)

[HIGH] React version mismatch
  Expected react@18.2.x for SDK 51, found 18.3.1
  Fix: npx expo install react@18.2.0 react-dom@18.2.0

[LOW] @types/react ahead of SDK recommendation (19.x vs 18.2.x)
  Fix: npx expo install --fix
```
