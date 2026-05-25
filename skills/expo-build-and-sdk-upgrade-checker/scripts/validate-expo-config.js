#!/usr/bin/env node
/**
 * validate-expo-config.js
 *
 * Read-only. Validates app config (app.json / app.config.js / app.config.ts)
 * and eas.json for managed-workflow build safety.
 *
 * Usage:  node validate-expo-config.js <projectRoot>
 *
 * Note: app.config.js/ts may be dynamic. This script statically reads app.json
 * when present; for dynamic configs it reports what it could not resolve so
 * the caller can reason about the file manually.
 *
 * Scope: Managed workflow only — no native project files inspected.
 */
'use strict';

const fs = require('fs');
const path = require('path');

const projectRoot = process.argv[2] || process.cwd();
const findings = [];
const add = (severity, code, message, fix) =>
  findings.push({ severity, code, message, fix: fix || null });

function readJson(p) {
  try { return JSON.parse(fs.readFileSync(p, 'utf8').replace(/^﻿/, '')); } catch (e) { return null; }
}
function exists(f) { return fs.existsSync(path.join(projectRoot, f)); }

// ---- App config ----
let appConfig = null;
let configSource = null;

if (exists('app.json')) {
  const raw = readJson(path.join(projectRoot, 'app.json'));
  appConfig = raw && raw.expo ? raw.expo : raw;
  configSource = 'app.json';
} else if (exists('app.config.ts') || exists('app.config.js')) {
  configSource = exists('app.config.ts') ? 'app.config.ts' : 'app.config.js';
  add('MEDIUM', 'DYNAMIC_CONFIG',
    `${configSource} is dynamic — static validation is partial. Read it and verify fields manually.`,
    'Manually confirm: name, slug, scheme, ios.bundleIdentifier, plugins, runtimeVersion.');
} else {
  add('CRITICAL', 'NO_APP_CONFIG',
    'No app.json / app.config.* found — not a valid Expo project root.',
    'Run from the app package directory.');
}

const pkg = readJson(path.join(projectRoot, 'package.json'));
const deps = pkg ? Object.assign({}, pkg.dependencies, pkg.devDependencies) : {};

if (appConfig) {
  // Core identity
  if (!appConfig.slug) add('HIGH', 'NO_SLUG',
    'expo.slug missing — required by EAS.', 'Add a "slug".');
  if (!appConfig.name) add('MEDIUM', 'NO_NAME',
    'expo.name missing.', 'Add a display "name".');

  // Expo Router needs a scheme for deep links
  if (deps['expo-router'] && !appConfig.scheme) {
    add('HIGH', 'NO_SCHEME',
      'expo-router present but expo.scheme is missing — deep links/auth redirects break.',
      'Add "scheme": "yourapp".');
  }

  // iOS managed essentials
  const ios = appConfig.ios || {};
  if (!ios.bundleIdentifier) {
    add('CRITICAL', 'NO_BUNDLE_ID',
      'expo.ios.bundleIdentifier missing — EAS iOS build cannot provision.',
      'Add "ios": { "bundleIdentifier": "com.acme.app" }.');
  }

  // Permission strings for common modules
  const infoPlist = ios.infoPlist || {};
  const permMap = [
    ['expo-image-picker', ['NSPhotoLibraryUsageDescription', 'NSCameraUsageDescription']],
    ['expo-camera', ['NSCameraUsageDescription']],
    ['expo-location', ['NSLocationWhenInUseUsageDescription']],
    ['expo-av', ['NSMicrophoneUsageDescription']],
    ['expo-media-library', ['NSPhotoLibraryUsageDescription']],
    ['expo-tracking-transparency', ['NSUserTrackingUsageDescription']],
  ];
  const pluginNames = (appConfig.plugins || []).map((p) =>
    Array.isArray(p) ? p[0] : p);
  permMap.forEach(([mod, keys]) => {
    if (!deps[mod]) return;
    const declaredViaPlugin = pluginNames.includes(mod);
    const missing = keys.filter((k) => !(k in infoPlist));
    if (missing.length && !declaredViaPlugin) {
      add('HIGH', 'MISSING_PERMISSION_STRING',
        `${mod} is installed but iOS purpose string(s) ${missing.join(', ')} not declared (and no ${mod} config plugin).`,
        `Add the string(s) to ios.infoPlist or configure the ${mod} plugin.`);
    }
  });

  // Icon
  if (!appConfig.icon && !ios.icon) {
    add('MEDIUM', 'NO_ICON',
      'No app icon configured — App Store submission will be rejected.',
      'Add a square, non-transparent PNG as expo.icon.');
  }

  // updates / runtimeVersion coherence
  if (deps['expo-updates']) {
    if (!appConfig.runtimeVersion) {
      add('HIGH', 'NO_RUNTIME_VERSION',
        'expo-updates installed but runtimeVersion not set — OTA updates may target the wrong builds.',
        'Set runtimeVersion (policy "appVersion" is a safe default).');
    }
    if (!appConfig.updates || !appConfig.updates.url) {
      add('MEDIUM', 'NO_UPDATES_URL',
        'expo-updates installed but expo.updates.url not configured.',
        'Run: eas update:configure');
    }
  }

  // Plugin/dependency cross-check
  pluginNames.forEach((name) => {
    if (typeof name === 'string' && name.startsWith('expo-') && !deps[name]) {
      add('MEDIUM', 'PLUGIN_NOT_INSTALLED',
        `Config plugin "${name}" referenced but not in package.json.`,
        `npx expo install ${name}`);
    }
  });

  // newArch advisory
  if (appConfig.newArchEnabled === true) {
    add('LOW', 'NEW_ARCH_ON',
      'newArchEnabled:true — verify every native-backed dependency supports Fabric for this SDK.',
      'Cross-check with checks/ios-managed-risks.md.');
  }
}

// ---- eas.json ----
if (exists('eas.json')) {
  const eas = readJson(path.join(projectRoot, 'eas.json'));
  if (!eas) {
    add('HIGH', 'EAS_JSON_INVALID',
      'eas.json present but not valid JSON.', 'Fix JSON syntax / run eas build:configure.');
  } else {
    const profiles = eas.build || {};
    if (!eas.cli || !eas.cli.version) {
      add('MEDIUM', 'NO_CLI_PIN',
        'eas.json has no cli.version pin.',
        'Add "cli": { "version": ">= 13.0.0" }.');
    }
    Object.entries(profiles).forEach(([name, prof]) => {
      const p = prof || {};
      if (p.developmentClient && !deps['expo-dev-client']) {
        add('HIGH', 'DEV_CLIENT_PROFILE_NO_DEP',
          `eas profile "${name}" sets developmentClient:true but expo-dev-client is not installed.`,
          'npx expo install expo-dev-client');
      }
      const isProd = /prod/i.test(name);
      if (isProd && p.ios && p.ios.simulator === true) {
        add('HIGH', 'PROD_SIMULATOR',
          `eas profile "${name}" builds an iOS simulator binary — not submittable.`,
          'Remove ios.simulator:true from production.');
      }
      if (isProd && p.developmentClient === true) {
        add('CRITICAL', 'PROD_DEV_CLIENT',
          `Production-like profile "${name}" has developmentClient:true — dev client would ship to store.`,
          'Give production its own profile without developmentClient.');
      }
      if (isProd && p.distribution && p.distribution !== 'store') {
        add('MEDIUM', 'PROD_NOT_STORE',
          `Production profile "${name}" distribution="${p.distribution}" (expected "store").`,
          'Set distribution:"store" for release.');
      }
    });
  }
} else {
  add('MEDIUM', 'NO_EAS_JSON',
    'No eas.json — EAS Build will use defaults.',
    'Run: eas build:configure');
}

emit();

function emit() {
  const order = { CRITICAL: 0, HIGH: 1, MEDIUM: 2, LOW: 3 };
  findings.sort((a, b) => order[a.severity] - order[b.severity]);
  const counts = findings.reduce((m, f) => {
    m[f.severity] = (m[f.severity] || 0) + 1; return m;
  }, {});
  process.stderr.write(
    `\n[validate-expo-config] source=${configSource || 'none'} @ ${projectRoot}\n`);
  findings.forEach((f) => {
    process.stderr.write(`  [${f.severity}] ${f.code}: ${f.message}\n`);
    if (f.fix) process.stderr.write(`      fix: ${f.fix}\n`);
  });
  process.stderr.write(`  summary: ${JSON.stringify(counts)}\n`);
  process.stdout.write(JSON.stringify(
    { script: 'validate-expo-config', projectRoot, configSource, counts, findings },
    null, 2));
}
