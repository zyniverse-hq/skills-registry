#!/usr/bin/env node
/**
 * detect-risky-dependencies.js
 *
 * Read-only. Flags dependency patterns that are risky or incompatible with the
 * Expo Managed Workflow: known bare-only/native packages, missing Reanimated
 * Babel plugin, Expo Router triad gaps, patch-package on Expo core, duplicate
 * React/React Native, and deprecated packages.
 *
 * Usage:  node detect-risky-dependencies.js <projectRoot>
 *
 * Scope: Managed workflow only.
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
function readText(p) {
  try { return fs.readFileSync(p, 'utf8'); } catch (e) { return null; }
}

// Packages that typically require native linking / are not managed-friendly
// without a config plugin. Presence is a flag to investigate, not auto-fail.
const NATIVE_RISK = {
  'react-native-firebase': 'Use @react-native-firebase with its Expo config plugins, or expo-firebase alternatives.',
  '@react-native-firebase/app': 'Requires config plugin; verify managed-workflow setup.',
  'react-native-vision-camera': 'Needs a config plugin; confirm Expo-managed support for your SDK.',
  'react-native-track-player': 'Background audio needs config plugin + entitlements.',
  'react-native-ble-plx': 'BLE requires config plugin + iOS permission strings.',
  'react-native-maps': 'OK in managed but must be installed via expo install and configured with API keys via plugin.',
  'react-native-mmkv': 'Verify version supports Expo managed (no-native build) for your SDK.',
  'jsc-android': 'JSC override — Hermes is the managed default; remove unless intentional.',
};

// Deprecated / superseded in the Expo ecosystem
const DEPRECATED = {
  'expo-permissions': 'Removed — use per-module permission APIs / config plugins.',
  '@react-native-community/async-storage': 'Renamed to @react-native-async-storage/async-storage.',
  'expo-app-loading': 'Deprecated — use expo-splash-screen.',
  'react-native-unimodules': 'Removed in modern Expo — delete it.',
  '@expo/vector-icons-legacy': 'Use @expo/vector-icons.',
};

const ROUTER_TRIAD = [
  'expo-router', 'react-native-screens', 'react-native-safe-area-context',
];

const pkg = readJson(path.join(projectRoot, 'package.json'));
if (!pkg) {
  add('CRITICAL', 'NO_PACKAGE_JSON',
    `Cannot read package.json at ${projectRoot}`,
    'Pass the project root containing package.json.');
  return emit();
}
const deps = Object.assign({}, pkg.dependencies, pkg.devDependencies);

// 1. Native-risk packages
Object.entries(NATIVE_RISK).forEach(([name, note]) => {
  if (deps[name]) {
    add('HIGH', 'NATIVE_RISK_PKG',
      `"${name}" may need native config — verify managed-workflow compatibility. ${note}`,
      'Confirm an Expo config plugin exists for your SDK, or choose an Expo-supported alternative. Do NOT hand-edit native projects.');
  }
});

// 2. Deprecated packages
Object.entries(DEPRECATED).forEach(([name, note]) => {
  if (deps[name]) {
    add('MEDIUM', 'DEPRECATED_PKG',
      `"${name}" is deprecated/superseded. ${note}`,
      `Remove or replace "${name}".`);
  }
});

// 3. Reanimated Babel plugin
if (deps['react-native-reanimated']) {
  const babel = readText(path.join(projectRoot, 'babel.config.js')) ||
                readText(path.join(projectRoot, 'babel.config.cjs')) || '';
  if (!babel) {
    add('HIGH', 'NO_BABEL_CONFIG',
      'react-native-reanimated installed but babel.config.js not found/readable.',
      "Create babel.config.js with 'react-native-reanimated/plugin' last in plugins[].");
  } else if (!/react-native-reanimated\/plugin/.test(babel) &&
             !/react-native-worklets\/plugin/.test(babel)) {
    add('CRITICAL', 'REANIMATED_NO_PLUGIN',
      'react-native-reanimated installed but its Babel plugin is not referenced — app will crash on launch.',
      "Add 'react-native-reanimated/plugin' as the LAST entry of plugins[] in babel.config.js.");
  } else {
    // crude "is it last" heuristic
    const idx = babel.search(/react-native-(reanimated|worklets)\/plugin/);
    const after = babel.slice(idx);
    if (/['"]\s*,\s*['"][^'"]+['"]\s*\]/.test(after) &&
        !/react-native-(reanimated|worklets)\/plugin['"]\s*,?\s*\]/.test(after)) {
      add('MEDIUM', 'REANIMATED_PLUGIN_ORDER',
        'Reanimated Babel plugin may not be last — it must be the final plugin.',
        'Move the reanimated/worklets plugin to the end of plugins[].');
    }
  }
}

// 4. Expo Router triad completeness
if (deps['expo-router']) {
  const missing = ROUTER_TRIAD.filter((d) => !deps[d]);
  if (missing.length) {
    add('CRITICAL', 'ROUTER_TRIAD_INCOMPLETE',
      `expo-router present but missing: ${missing.join(', ')} — navigation will not work.`,
      `npx expo install ${missing.join(' ')}`);
  }
}

// 5. patch-package on Expo core
if (fs.existsSync(path.join(projectRoot, 'patches'))) {
  let patched = [];
  try {
    patched = fs.readdirSync(path.join(projectRoot, 'patches'));
  } catch (e) { /* ignore */ }
  const corePatched = patched.filter((f) =>
    /^(expo|react-native|expo-router|react)[+@]/.test(f));
  if (corePatched.length) {
    add('HIGH', 'PATCHED_CORE',
      `patch-package patches on Expo/RN core: ${corePatched.join(', ')} — will silently break on SDK upgrade.`,
      'Remove core patches; pursue an upstream-supported fix or alternative.');
  }
}

// 6. Duplicate React / React Native in nested node_modules (monorepo hoist)
['react', 'react-native'].forEach((mod) => {
  const nested = path.join(projectRoot, 'node_modules', mod, 'package.json');
  const rootUp = path.join(projectRoot, '..', 'node_modules', mod, 'package.json');
  const a = readJson(nested);
  const b = readJson(rootUp);
  if (a && b && a.version && b.version && a.version !== b.version) {
    add('CRITICAL', 'DUPLICATE_CORE',
      `Two copies of "${mod}" resolved (${a.version} vs ${b.version}) — invariant violation / red screen.`,
      'Dedupe: align versions and use package-manager resolutions/nohoist so one copy exists.');
  }
});

// 7. Expo packages installed with non-SDK ranges (advisory; pairs with analyze-package-json)
Object.keys(deps).forEach((name) => {
  if (/^expo-/.test(name) && /^[\^]/.test(deps[name])) {
    add('LOW', 'EXPO_PKG_CARET',
      `${name} uses a caret range ("${deps[name]}") — prefer expo install pinning.`,
      `npx expo install ${name}`);
  }
});

emit();

function emit() {
  const order = { CRITICAL: 0, HIGH: 1, MEDIUM: 2, LOW: 3 };
  findings.sort((a, b) => order[a.severity] - order[b.severity]);
  const counts = findings.reduce((m, f) => {
    m[f.severity] = (m[f.severity] || 0) + 1; return m;
  }, {});
  process.stderr.write(`\n[detect-risky-dependencies] ${projectRoot}\n`);
  findings.forEach((f) => {
    process.stderr.write(`  [${f.severity}] ${f.code}: ${f.message}\n`);
    if (f.fix) process.stderr.write(`      fix: ${f.fix}\n`);
  });
  process.stderr.write(`  summary: ${JSON.stringify(counts)}\n`);
  process.stdout.write(JSON.stringify(
    { script: 'detect-risky-dependencies', projectRoot, counts, findings },
    null, 2));
}
