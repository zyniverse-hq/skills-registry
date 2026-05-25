# Check: Expo SDK Upgrade Procedure & Checklist

The safe, ordered procedure for moving a managed project across an Expo SDK
version. Upgrade sequencing matters — doing steps out of order is the most
common cause of post-upgrade build failure.

## Golden rules

- Upgrade **one SDK major at a time** (e.g. 52 → 53 → 54 → 55). Skipping
  majors multiplies breakage. CRITICAL anti-pattern: jumping 52 → 55 in one
  commit.
- Always change `expo` first, then let `expo install --fix` move everything
  else. Never hand-bump `react-native`/`react`.
- Read the per-SDK breaking-change file for the **target** SDK before starting
  each hop (see Phase 0 below).
- Do each hop on its own branch with a green build as the baseline.

---

## Phase 0 — Multi-hop planning (do this BEFORE touching any code)

Determine the hop sequence by reading the current SDK from `package.json`:

| Current SDK | Target SDK | Hops required |
|---|---|---|
| 51 | 55 | 51→52, 52→53, 53→54, 54→55 |
| 52 | 55 | 52→53, 53→54, 54→55 |
| 53 | 55 | 53→54, 54→55 |
| 54 | 55 | 54→55 |

**Do not compress multiple hops into one branch.** Each hop = one branch, one
set of package changes, one green EAS preview build. Only then start the next
hop branch off the merged previous one.

For each hop, load the corresponding breaking-change file before running the
upgrade steps:

| Hop | Breaking-change file |
|---|---|
| SDK 51 → 52 | `checks/breaking-changes-sdk-52.md` |
| SDK 52 → 53 | `checks/breaking-changes-sdk-53.md` |
| SDK 53 → 54 | `checks/breaking-changes-sdk-54.md` |
| SDK 54 → 55 | `checks/breaking-changes-sdk-55.md` |

State the full hop plan in the report before beginning any upgrade steps.

---

## Ordered upgrade sequence (per hop)

### 1. Pre-flight (baseline must be green)

- Clean working tree; create `chore/expo-sdk-<target>` branch.
- Run `npx expo-doctor` — must be clean. If not, stop and fix before upgrading.
- Run `npx expo install --check` — must be clean.
- Record current SDK, RN, React, Router, Reanimated versions.

### 2. TSX scan — two-phase approach (before touching packages)

Scanning every file for every pattern is slow. Use the two-phase approach:

**Phase A — Fast import audit (seconds)**

Run a single combined grep for all package names affected this hop. This finds
only the files that import those packages — typically a small subset of the
codebase.

```bash
# Each breaking-change file has a "Fast import audit" section with this command.
# Example for 52→53 hop:
grep -rln "expo-av\|expo-camera\|expo-router\|useRootNavigation\|setImmediate" \
  --include="*.tsx" --include="*.ts" --include="*.js" --include="*.jsx" \
  src/ app/ components/ hooks/ 2>/dev/null
```

If Phase A returns zero files for a particular package, skip Phase B for that
package entirely. Only investigate what's actually imported.

**Phase B — Targeted API pattern scan (only matched files)**

For each file returned by Phase A, run the detailed pattern grep from the
breaking-change file against **that file only** — not the whole tree.

```bash
# Example: file returned by Phase A is src/screens/VideoPlayer.tsx
grep -n "from 'expo-av'\|Audio\.\|Video " src/screens/VideoPlayer.tsx
```

This produces a precise file:line list of code changes needed. Report this
list BEFORE running `expo install` — the developer needs to know the code
scope before committing to the hop.

**Which source dirs to scan:** `src/`, `app/`, `components/`, `hooks/`,
`screens/`, `lib/`, `utils/`. Skip `node_modules/`, `.expo/`, `dist/`.
If no `src/` exists, the Phase A commands fall back to scanning from the root
with `--exclude-dir=node_modules`.

Each Phase B pattern in the breaking-change files includes a **Failure mode**
annotation — the exact TypeScript error code or runtime error message. Use it
to confirm a match is genuinely breaking, not a false positive.

### 3. Bump the SDK

```bash
npx expo install expo@^<targetMajor>
```

### 4. Re-align managed dependencies

```bash
npx expo install --fix
```

`--fix` realigns each package **in its existing section** — dev tooling stays
in `devDependencies`. After it runs:

- Verify no dev-only package leaked into `dependencies`.
- For any new SDK-aligned dev dep, use the pass-through form:
  ```bash
  npx expo install -- --save-dev <pkg>
  ```
- For SDK 54 and 55 hops: confirm `react-native-worklets` is installed:
  ```bash
  npx expo install react-native-worklets
  ```

### 5. Apply breaking changes from the scan (step 2)

Work through each file flagged in the TSX scan. Apply the code fixes documented
in the breaking-change file for this hop. Common fixes by hop:

**52→53:** Run `npx codemod@latest react/19/migration-recipe`, then fix
remaining `useRef()` no-arg calls and any removed APIs manually.

**53→54:** Fix hard-removed reanimated APIs (`executeOnUIRuntimeSync`,
`makeShareableCloneRecursive`, `useWorkletCallback`, etc.).

**54→55:** Migrate all `expo-av` usages to `expo-video` / `expo-audio`.

### 6. Config changes

Apply any `app.json` / `app.config.js` field changes from the breaking-change
file (removed fields, renamed fields, new required fields).

### 7. Babel / Metro sanity

- Confirm `react-native-reanimated/plugin` (SDK 51–53) or
  `react-native-worklets/plugin` (SDK 54–55) is last in `babel.config.js`,
  **unless** you use `babel-preset-expo` which handles this automatically.
- Confirm `metro.config.js` extends `expo/metro-config`.

### 8. Clean install & cache

```bash
rm -rf node_modules
rm -f package-lock.json   # keep only one lockfile
npm install
npx expo start -c
```

### 9. Static health pass

Run all four skill scripts; resolve every CRITICAL/HIGH:

```bash
node <skill>/scripts/analyze-package-json.js .
node <skill>/scripts/check-sdk-alignment.js .
node <skill>/scripts/validate-expo-config.js .
node <skill>/scripts/detect-risky-dependencies.js .
```

### 10. Doctor pass

```bash
npx expo-doctor   # must be clean (17/18+ checks passed, 0 failed)
npx expo install --check   # must show no mismatches
```

### 11. Runtime smoke test

In Expo Go or dev client: cold start, all navigation routes (Router), any
permission-gated screens, deep links, camera/media features if used.

### 12. EAS preview build

```bash
eas build --profile preview --platform ios --non-interactive
```

Do not proceed to the next hop until this build succeeds and is smoke-tested on
a real device.

### 13. Update runtime version / channel (if needed)

If any native-affecting dependencies changed (reanimated major, new native
modules), increment `runtimeVersion` in `app.json` to prevent OTA updates
landing on incompatible native builds. See `eas-validation.md`.

### 14. Merge and start next hop

Merge the branch. Create the next hop branch off the merged result. Repeat
from step 1.

---

## Severity mapping for upgrade findings

| Situation | Severity |
|---|---|
| Skipping ≥1 SDK major | CRITICAL |
| `expo-doctor` not clean before upgrade | HIGH |
| Hard-removed API still in codebase (grep finds matches) | CRITICAL |
| `react-native`/`react` hand-edited during upgrade | HIGH |
| Dev tooling moved into `dependencies` during realign | MEDIUM |
| Deprecated API still in codebase (warns, not hard break) | MEDIUM |
| Missing `react-native-worklets` for SDK 54+ | HIGH |
| `expo-av` still imported in SDK 55 | CRITICAL |
| New Architecture not migrated before SDK 55 | CRITICAL |
| Deprecated app-config field still present | MEDIUM |
| No preview EAS build before production | HIGH |
| Lockfile not regenerated after upgrade | MEDIUM |

---

## Common upgrade failures

- `expo install --fix` skipped → half-upgraded tree, doctor red.
- React 19 `useRef()` no-arg calls → TypeScript errors throughout.
- Reanimated 3→4: `useWorkletCallback` removed → runtime crash.
- `expo-av` not migrated before SDK 55 → runtime crash in Expo Go.
- Legacy Architecture left in place → SDK 55 build fails.
- Old lockfile reused on EAS → stale transitive versions.
- Multi-hop attempted in one branch → tangled conflicts, hard to debug.

---

## Output

For each hop, fill `templates/sdk-upgrade-checklist.md` with the from/to
versions, the pre-scan TSX findings, and tick each step. Attach the scripts'
findings and `npx expo-doctor` output. Block the production build until every
CRITICAL/HIGH is resolved.
