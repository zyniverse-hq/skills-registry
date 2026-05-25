# Example: Breaking Changes — SDK 51 → 52

## Scenario

App uses expo-camera for document scanning (with the legacy API) and has
expo-barcode-scanner installed. After bumping to SDK 52, Metro fails to bundle
with two module-not-found errors. A third issue — `Href<T>` generics in
expo-router — causes TypeScript compilation to fail.

## Input — package.json (excerpt)

```json
{
  "dependencies": {
    "expo": "~52.0.0",
    "expo-camera": "~15.0.0",
    "expo-barcode-scanner": "~13.0.0",
    "expo-router": "~4.0.2"
  }
}
```

Source files (pre-upgrade):

```tsx
// src/screens/ScanDocument.tsx
import { Camera } from 'expo-camera/legacy';

// src/screens/QRScan.tsx
import { BarCodeScanner } from 'expo-barcode-scanner';

// src/navigation/types.ts
import type { Href } from 'expo-router';
const profileLink: Href<'/profile'> = '/profile';
```

## Analysis (via checks/breaking-changes-sdk-52.md)

Phase A fast import audit:

```bash
CAMERA_FILES=$(grep -rln "expo-camera\|expo-barcode-scanner" \
  --include="*.tsx" --include="*.ts" src/ app/ 2>/dev/null)
ROUTER_FILES=$(grep -rln "from 'expo-router'" \
  --include="*.tsx" --include="*.ts" src/ app/ 2>/dev/null)
```

Phase B targeted scans:

```bash
# expo-camera/legacy — CRITICAL
echo "$CAMERA_FILES" | xargs grep -n "from 'expo-camera/legacy'"
# → src/screens/ScanDocument.tsx:1  ← CRITICAL: module removed in SDK 52

# expo-barcode-scanner — CRITICAL
echo "$CAMERA_FILES" | xargs grep -n "from 'expo-barcode-scanner'"
# → src/screens/QRScan.tsx:1  ← CRITICAL: package removed in SDK 52

# Href<T> generics — HIGH
echo "$ROUTER_FILES" | xargs grep -n "Href<"
# → src/navigation/types.ts:2  ← HIGH: Href no longer generic (TS2315)
```

## Findings report

```
VERDICT: BLOCK — 2 CRITICAL, 1 HIGH

[CRITICAL] expo-camera/legacy imported — module does not exist in SDK 52
  src/screens/ScanDocument.tsx:1
  Metro: "Cannot resolve module 'expo-camera/legacy'"
  Fix: migrate to CameraView from 'expo-camera'

[CRITICAL] expo-barcode-scanner imported — package removed in SDK 52
  src/screens/QRScan.tsx:1
  Metro: "Cannot resolve module 'expo-barcode-scanner'"
  Fix: use CameraView with onBarcodeScanned prop

[HIGH] Href<'/profile'> generic — TS2315 in SDK 52 (expo-router 4)
  src/navigation/types.ts:2
  Fix: remove the type parameter → Href = '/profile'
```

## Fix applied

```tsx
// src/screens/ScanDocument.tsx
// Before
import { Camera } from 'expo-camera/legacy';
// After
import { CameraView, useCameraPermissions } from 'expo-camera';

// src/screens/QRScan.tsx
// Before
import { BarCodeScanner } from 'expo-barcode-scanner';
// After
import { CameraView } from 'expo-camera';
// Replace <BarCodeScanner> JSX with:
// <CameraView onBarcodeScanned={handleScan} barcodeScannerSettings={{ barcodeTypes: ['qr'] }} />

// src/navigation/types.ts
// Before
const profileLink: Href<'/profile'> = '/profile';
// After
const profileLink: Href = '/profile';
```

```bash
npx expo install --fix   # re-align all managed packages
npx expo-doctor          # expect clean
eas build --profile preview --platform ios --non-interactive
```

## Lesson

`expo-camera/legacy` and `expo-barcode-scanner` were soft-deprecated in SDK 51
but removed entirely in SDK 52 — any import causes a Metro bundle failure that
blocks the app from launching. The TSX scan in Phase B (before touching
packages) is essential: finding these before the build cycle saves hours.
Run Phase A + B from `breaking-changes-sdk-52.md` as the first step of the hop.
