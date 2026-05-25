# Example: Breaking Changes — SDK 54 → 55

## Scenario

App targeting SDK 55 has `expo-av` used in three screens for video and audio
playback. SDK 55 removes `expo-av` entirely — any import causes an immediate
Metro bundle failure. Additionally, `newArchEnabled: false` is still set in
`app.json`, which blocks the SDK 55 build entirely. Both issues are CRITICAL
and must be resolved before any build attempt.

## Input — package.json (excerpt, after `expo install --fix`)

```json
{
  "dependencies": {
    "expo": "~55.0.0",
    "expo-av": "~14.0.7",
    "expo-video": "~2.2.0",
    "react-native": "0.83.x"
  }
}
```

`app.json` excerpt:

```json
{
  "expo": {
    "plugins": [
      ["expo-build-properties", {
        "ios": { "newArchEnabled": false },
        "android": { "newArchEnabled": false }
      }]
    ]
  }
}
```

Pre-upgrade source patterns:

```tsx
// src/screens/VideoPlayer.tsx
import { Video, ResizeMode } from 'expo-av';
<Video source={{ uri }} resizeMode={ResizeMode.CONTAIN} useNativeControls />

// src/screens/AudioPlayer.tsx
import { Audio } from 'expo-av';
const { sound } = await Audio.Sound.createAsync(require('./track.mp3'));

// src/hooks/useAudioMode.ts
import { Audio } from 'expo-av';
await Audio.setAudioModeAsync({ allowsRecordingIOS: true });
```

## Analysis (via checks/breaking-changes-sdk-55.md)

Phase A fast import audit — `expo-av` must be zero before building:

```bash
AV_FILES=$(grep -rln "from 'expo-av'\|require.*expo-av" \
  --include="*.tsx" --include="*.ts" --include="*.js" \
  src/ app/ components/ hooks/ screens/ 2>/dev/null)
echo "$AV_FILES"
# → src/screens/VideoPlayer.tsx
# → src/screens/AudioPlayer.tsx
# → src/hooks/useAudioMode.ts
```

Phase B targeted scans:

```bash
# Video usage — CRITICAL
echo "$AV_FILES" | xargs grep -n "import.*\bVideo\b.*expo-av\|<Video\b\|ResizeMode\."
# → src/screens/VideoPlayer.tsx:1,2,8

# Audio usage — CRITICAL
echo "$AV_FILES" | xargs grep -n "import.*\bAudio\b.*expo-av\|Audio\.Sound\.\|Audio\.setAudioModeAsync"
# → src/screens/AudioPlayer.tsx:1,4
# → src/hooks/useAudioMode.ts:1,3

# New Arch check — CRITICAL
grep -n "newArchEnabled" app.json
# → "newArchEnabled": false  ← CRITICAL: SDK 55 build fails with Legacy Arch
```

## Findings report

```
VERDICT: NO-GO — 2 CRITICAL blockers, fix before any SDK 55 build attempt.

[CRITICAL] expo-av imported in 3 files — package removed from SDK 55
  src/screens/VideoPlayer.tsx  (Video, ResizeMode)
  src/screens/AudioPlayer.tsx  (Audio.Sound)
  src/hooks/useAudioMode.ts    (Audio.setAudioModeAsync)
  Metro: "Cannot find module 'expo-av'"
  Fix: migrate to expo-video (Video) and expo-audio (Audio)

[CRITICAL] newArchEnabled: false — SDK 55 removes Legacy Architecture entirely
  app.json: ios.newArchEnabled: false, android.newArchEnabled: false
  SDK 55 build-time error: Legacy Architecture is not supported.
  Fix: remove newArchEnabled: false from app.json; audit all native deps for
  New Arch compatibility before proceeding.
```

## Fix applied — New Arch first

Remove `newArchEnabled: false` from `app.json`, then audit native dependencies
using `detect-risky-dependencies.js` and `third-party-packages.md`.
If any package is not New Arch-compatible, stop and resolve it before proceeding
to the expo-av migration.

```json
// app.json — remove the newArchEnabled lines
{
  "expo": {
    "plugins": [["expo-build-properties", {}]]
  }
}
```

## Fix applied — expo-av migration

```tsx
// src/screens/VideoPlayer.tsx
// Before
import { Video, ResizeMode } from 'expo-av';
<Video source={{ uri }} resizeMode={ResizeMode.CONTAIN} useNativeControls />

// After
import { VideoView, useVideoPlayer } from 'expo-video';
const player = useVideoPlayer({ uri }, p => { p.loop = false; });
<VideoView player={player} contentFit="contain" nativeControls />

// src/screens/AudioPlayer.tsx
// Before
import { Audio } from 'expo-av';
const { sound } = await Audio.Sound.createAsync(require('./track.mp3'));

// After
import { useAudioPlayer } from 'expo-audio';
const player = useAudioPlayer(require('./track.mp3'));

// src/hooks/useAudioMode.ts
// Before
import { Audio } from 'expo-av';
await Audio.setAudioModeAsync({ allowsRecordingIOS: true });

// After
import { setAudioModeAsync } from 'expo-audio';
await setAudioModeAsync({ allowsRecordingIOS: true });
```

```bash
# Verify zero expo-av imports remain
grep -r "from 'expo-av'" --include="*.tsx" --include="*.ts" --include="*.js" \
  src/ app/ hooks/ screens/ 2>/dev/null
# → no output required before proceeding

npx expo install expo-video expo-audio   # ensure aligned versions
rm -rf node_modules && rm -f package-lock.json && npm install
npx expo start -c
npx expo-doctor   # expect clean
eas build --profile preview --platform ios --non-interactive
```

## Lesson

SDK 55 has two absolute build blockers that must be resolved before any other work:
(1) all `expo-av` imports must be migrated to `expo-video` / `expo-audio`, and
(2) `newArchEnabled: false` must be removed. The Phase A grep is the first action
for this hop — if `$AV_FILES` is non-empty, stop and migrate before bumping any
other package. Attempting a build with either blocker in place fails immediately
and wastes EAS build minutes.
