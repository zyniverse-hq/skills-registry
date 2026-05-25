# Example: Third-Party Package Conflicts (SDK 53 → 54 hop)

## Scenario

Health check before the SDK 53→54 upgrade surfaces three third-party packages
that will silently break or crash on SDK 54's New Architecture default and
Reanimated v4 requirement. All three install cleanly — `expo-doctor` does not
flag them.

## Input — package.json (excerpt)

```json
{
  "dependencies": {
    "expo": "~54.0.0",
    "nativewind": "^4.0.36",
    "tailwindcss": "^3.4.17",
    "@shopify/flash-list": "^1.7.3",
    "@gorhom/bottom-sheet": "^5.0.5",
    "react-native-reanimated": "~4.1.0",
    "react-native-gesture-handler": "~2.28.0"
  }
}
```

`app.json` excerpt:

```json
{
  "expo": {
    "plugins": [["expo-build-properties", { "ios": { "newArchEnabled": true } }]]
  }
}
```

## Analysis (via checks/third-party-packages.md)

`detect-risky-dependencies.js` output:

```
[CRITICAL] nativewind@4.0.36 — must be >=4.2.1 for SDK 54
  Reanimated v4 conflicts with nativewind < 4.2.0 at the Babel plugin level.
  All className styling will silently produce no styles. No error, no warning.

[CRITICAL] @shopify/flash-list@1.7.3 — must be v2.x for SDK 54 (New Arch only)
  v2 is New Arch-only; v1 on New Arch crashes: "FlashList v2.x has been
  designed to be new architecture only and will not run on old architecture"

[HIGH] @gorhom/bottom-sheet@5.0.5 — must be >=5.1.8 for Reanimated v4
  v5.0.5 was built against Reanimated v3 APIs removed in v4.
  App crashes on any gesture interaction with the bottom sheet.
```

## TSX scan scope (Phase A)

```bash
THIRD_PARTY_FILES=$(grep -rln \
  "@shopify/flash-list\|@gorhom/bottom-sheet\|nativewind" \
  --include="*.tsx" --include="*.ts" --include="*.jsx" \
  src/ app/ components/ 2>/dev/null)

echo "$THIRD_PARTY_FILES"
# → 12 files use className (nativewind)
# → 3 files use FlashList
# → 2 files use BottomSheet
```

v1→v2 flash-list API changes present in the 3 matched files:

```
src/components/ActivityFeed.tsx:14  estimatedItemSize={80}       ← remove
src/components/LeaderboardList.tsx:8 MasonryFlashList             ← → <FlashList masonry>
src/components/LeaderboardList.tsx:9 estimatedListSize={{ height }} ← remove
```

## Fix applied

```bash
# 1. nativewind — patch version to 4.2.1+
npm install nativewind@^4.2.1 tailwindcss@3.4.17
# tailwindcss@4.x is NOT compatible with nativewind v4

# 2. flash-list — upgrade to v2 via expo install
npx expo install @shopify/flash-list

# 3. bottom-sheet — patch to 5.1.8+
npm install @gorhom/bottom-sheet@^5.1.8
```

Code changes in `ActivityFeed.tsx` and `LeaderboardList.tsx`:

```tsx
// ActivityFeed.tsx — remove estimatedItemSize
<FlashList
  data={items}
  renderItem={renderItem}
  // estimatedItemSize={80}   ← removed; v2 auto-sizes
/>

// LeaderboardList.tsx — MasonryFlashList → FlashList masonry
// Before
import { MasonryFlashList } from '@shopify/flash-list';
<MasonryFlashList data={items} estimatedListSize={{ height: 600, width: 400 }} />

// After
import { FlashList } from '@shopify/flash-list';
<FlashList masonry data={items} />
```

```bash
npx expo-doctor         # expect clean
npx expo install --check  # expect no mismatches
node scripts/detect-risky-dependencies.js .   # expect no CRITICAL/HIGH
```

## Lessons

1. `expo-doctor` and `expo install --check` are blind to third-party package
   incompatibilities — they only validate Expo-managed packages. Always run
   `detect-risky-dependencies.js` and check `third-party-packages.md` manually
   during any SDK upgrade.
2. nativewind + Reanimated v4 is the most dangerous silent regression: the UI
   just appears completely unstyled with no console output.
3. @shopify/flash-list v2 has a one-way migration (v2 is New Arch only) —
   check the API diff before bumping.
4. @gorhom/bottom-sheet requires a minimum patch version for Reanimated v4, not
   just a major version — `5.0.x` is not enough.
