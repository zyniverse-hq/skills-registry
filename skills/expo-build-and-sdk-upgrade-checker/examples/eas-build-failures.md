# Example: EAS iOS Build Failure (profile misconfiguration)

## Scenario

`eas build --profile production --platform ios` produces a build that TestFlight
rejects as a "simulator binary", and an earlier build shipped a dev client.

## Input — eas.json

```json
{
  "cli": { "version": ">= 13.0.0" },
  "build": {
    "development": {
      "developmentClient": true,
      "distribution": "internal",
      "ios": { "simulator": true }
    },
    "production": {
      "extends": "development",
      "distribution": "store"
    }
  }
}
```

## Analysis (via checks/eas-validation.md + validate-expo-config.js)

```
[CRITICAL] PROD_DEV_CLIENT
  production extends "development" → developmentClient:true inherited.
  A dev client would ship to the App Store.

[HIGH] PROD_SIMULATOR
  production inherits ios.simulator:true → non-submittable simulator binary.
```

## Fix — give production its own clean profile

```json
{
  "cli": { "version": ">= 13.0.0" },
  "build": {
    "development": {
      "developmentClient": true,
      "distribution": "internal",
      "ios": { "simulator": true }
    },
    "preview": {
      "distribution": "internal"
    },
    "production": {
      "distribution": "store",
      "autoIncrement": true
    }
  }
}
```

## Validation

```bash
node scripts/validate-expo-config.js .   # expect no CRITICAL/HIGH on eas.json
eas build --profile preview --platform ios --non-interactive   # smoke test
eas build --profile production --platform ios
```

## Lesson

Production must **not** `extends` a development profile. Never let
`developmentClient` or `ios.simulator:true` leak into a store build.
