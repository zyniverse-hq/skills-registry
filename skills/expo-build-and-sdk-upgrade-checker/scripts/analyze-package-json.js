#!/usr/bin/env node
/**
 * analyze-package-json.js
 *
 * Read-only analyzer for an Expo Managed Workflow project's package.json.
 * Detects missing/loose Expo SDK pin, loose ranges on Expo-managed packages,
 * multiple lockfiles, package-manager ambiguity, and Expo Router entry wiring.
 *
 * Usage:  node analyze-package-json.js <projectRoot>
 * Output: human summary on stderr + JSON findings on stdout.
 *
 * Scope: Managed workflow only. No native project inspection.
 */
'use strict';

const fs = require('fs');
const path = require('path');

const projectRoot = process.argv[2] || process.cwd();
const findings = [];

function add(severity, code, message, fix) {
  findings.push({ severity, code, message, fix: fix || null });
}

function readJson(p) {
  try {
    return JSON.parse(fs.readFileSync(p, 'utf8').replace(/^﻿/, ''));
  } catch (e) {
    return null;
  }
}

const EXPO_MANAGED = [
  'expo-router', 'expo-status-bar', 'expo-splash-screen', 'expo-constants',
  'expo-linking', 'expo-font', 'expo-asset', 'expo-updates', 'expo-dev-client',
  'expo-build-properties', 'expo-image', 'react-native-screens',
  'react-native-safe-area-context', 'react-native-reanimated',
  'react-native-gesture-handler', 'react-native-svg', 'react-native-webview',
  '@react-native-async-storage/async-storage', 'react-native-maps',
  'react-native-pager-view',
];

const pkgPath = path.join(projectRoot, 'package.json');
const pkg = readJson(pkgPath);

if (!pkg) {
  add('CRITICAL', 'NO_PACKAGE_JSON',
    `Cannot read package.json at ${pkgPath}`,
    'Pass the directory containing package.json as the first argument.');
  emit();
  process.exit(0);
}

const prodDeps = pkg.dependencies || {};
const deps = Object.assign({}, pkg.dependencies, pkg.devDependencies);

// 0. Dev-only tooling wrongly placed in "dependencies"
// expo install puts packages in dependencies by default; dev tooling must be
// added with `npx expo install -- --save-dev <pkg>` (yarn: -- --dev) so it
// lands in devDependencies instead.
const DEV_ONLY = [
  'typescript', '@types/react', '@types/react-native', '@types/jest',
  'jest', 'jest-expo', 'react-test-renderer', '@testing-library/react-native',
  '@testing-library/jest-native', 'eslint', 'eslint-config-expo', 'prettier',
  'eslint-config-prettier', '@babel/core', 'babel-jest',
];
DEV_ONLY.forEach((name) => {
  if (prodDeps[name]) {
    add('MEDIUM', 'DEV_DEP_IN_PROD',
      `"${name}" is dev-only tooling but is listed in "dependencies".`,
      `Move it: npm rm ${name} && npx expo install -- --save-dev ${name}  (yarn: -- --dev)`);
  }
});

// 1. Expo SDK pin
if (!deps.expo) {
  add('CRITICAL', 'NO_EXPO_DEP',
    'package.json has no "expo" dependency — not an Expo project or broken setup.');
} else {
  const v = deps.expo;
  if (v === '*' || /latest/i.test(v) || v.startsWith('^')) {
    add('CRITICAL', 'LOOSE_EXPO_PIN',
      `expo is pinned loosely ("${v}") — SDK can float and break the build.`,
      'Pin with a tilde to a single SDK major, e.g. "expo": "~51.0.0".');
  } else {
    add('LOW', 'EXPO_PIN_OK', `expo pinned as "${v}".`);
  }
}

// 2. Core triad presence
['react', 'react-native'].forEach((c) => {
  if (!deps[c]) {
    add('CRITICAL', 'MISSING_CORE',
      `Missing core dependency "${c}".`,
      'Run: npx expo install --fix');
  }
});

// 3. Loose ranges on Expo-managed packages
EXPO_MANAGED.forEach((name) => {
  const v = deps[name];
  if (!v) return;
  if (v.startsWith('^') || v === '*' || /latest/i.test(v)) {
    add('MEDIUM', 'LOOSE_MANAGED_RANGE',
      `${name} uses a loose range ("${v}") that bypasses SDK alignment.`,
      `Re-add via: npx expo install ${name}`);
  }
});

// 4. Expo Router entry wiring
if (deps['expo-router']) {
  if (pkg.main && pkg.main !== 'expo-router/entry') {
    add('HIGH', 'ROUTER_ENTRY',
      `expo-router present but package.json "main" is "${pkg.main}".`,
      'Set "main": "expo-router/entry".');
  } else if (!pkg.main) {
    add('MEDIUM', 'ROUTER_ENTRY_MISSING',
      'expo-router present but package.json "main" is unset.',
      'Set "main": "expo-router/entry".');
  }
}

// 5. dev-client expectation (paired with eas.json checks)
if (!deps['expo-dev-client']) {
  add('LOW', 'NO_DEV_CLIENT',
    'expo-dev-client not installed — required only if an EAS profile sets developmentClient:true.');
}

// 6. Lockfile / package manager ambiguity
const locks = ['package-lock.json', 'yarn.lock', 'pnpm-lock.yaml']
  .filter((f) => fs.existsSync(path.join(projectRoot, f)));
if (locks.length > 1) {
  add('HIGH', 'MULTIPLE_LOCKFILES',
    `Multiple lockfiles found: ${locks.join(', ')} — non-deterministic installs on EAS.`,
    'Keep exactly one lockfile matching your package manager.');
} else if (locks.length === 0) {
  add('MEDIUM', 'NO_LOCKFILE',
    'No lockfile found — EAS builds will not be reproducible.',
    'Commit a lockfile (npm install / yarn / pnpm install).');
}

// 7. Node engine
if (pkg.engines && pkg.engines.node) {
  add('LOW', 'NODE_ENGINE', `engines.node = "${pkg.engines.node}".`);
} else {
  add('LOW', 'NO_NODE_ENGINE',
    'No engines.node set — EAS image Node may differ from local.',
    'Add "engines": { "node": ">=18" } and/or pin node in eas.json.');
}

emit();

function emit() {
  const order = { CRITICAL: 0, HIGH: 1, MEDIUM: 2, LOW: 3 };
  findings.sort((a, b) => order[a.severity] - order[b.severity]);
  const counts = findings.reduce((m, f) => {
    m[f.severity] = (m[f.severity] || 0) + 1; return m;
  }, {});
  process.stderr.write(`\n[analyze-package-json] ${projectRoot}\n`);
  findings.forEach((f) => {
    process.stderr.write(`  [${f.severity}] ${f.code}: ${f.message}\n`);
    if (f.fix) process.stderr.write(`      fix: ${f.fix}\n`);
  });
  process.stderr.write(
    `  summary: ${JSON.stringify(counts)}\n`);
  process.stdout.write(JSON.stringify(
    { script: 'analyze-package-json', projectRoot, counts, findings }, null, 2));
}
