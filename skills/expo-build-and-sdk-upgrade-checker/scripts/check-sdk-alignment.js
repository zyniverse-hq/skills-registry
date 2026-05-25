#!/usr/bin/env node
/**
 * check-sdk-alignment.js
 *
 * Read-only. Resolves the project's Expo SDK major and verifies that
 * react-native / react fall within the expected family for that SDK.
 *
 * Usage:  node check-sdk-alignment.js <projectRoot>
 *
 * The embedded table is a best-effort reference; the authoritative source is
 * `npx expo install --check`. When unsure, defer to that command.
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

// SDK major -> expected react-native minor + react minor
const SDK_MAP = {
  55: { rn: '0.83', react: '19.2' },
  54: { rn: '0.81', react: '19.1' },
  53: { rn: '0.79', react: '19.0' },
  52: { rn: '0.76', react: '18.3' },
  51: { rn: '0.74', react: '18.2' },
  50: { rn: '0.73', react: '18.2' },
  49: { rn: '0.72', react: '18.2' },
  48: { rn: '0.71', react: '18.2' },
};

function readJson(p) {
  try { return JSON.parse(fs.readFileSync(p, 'utf8').replace(/^﻿/, '')); } catch (e) { return null; }
}
function cleanRange(v) {
  return String(v || '').replace(/^[\^~>=<\s]+/, '').trim();
}
function major(v) {
  const m = cleanRange(v).match(/^(\d+)/);
  return m ? parseInt(m[1], 10) : null;
}
function minorKey(v) {
  const m = cleanRange(v).match(/^(\d+)\.(\d+)/);
  return m ? `${m[1]}.${m[2]}` : null;
}

let sdkMajor = null;
const pkg = readJson(path.join(projectRoot, 'package.json'));
if (!pkg) {
  add('CRITICAL', 'NO_PACKAGE_JSON',
    `Cannot read package.json at ${projectRoot}`,
    'Pass the project root containing package.json.');
  return emit();
}

const deps = Object.assign({}, pkg.dependencies, pkg.devDependencies);
sdkMajor = major(deps.expo);

if (!deps.expo || sdkMajor == null) {
  add('CRITICAL', 'NO_SDK',
    'Could not resolve an Expo SDK major from the "expo" dependency.',
    'Pin "expo": "~<major>.0.0".');
  return emit();
}

const expected = SDK_MAP[sdkMajor];
if (!expected) {
  add('MEDIUM', 'UNKNOWN_SDK',
    `Expo SDK ${sdkMajor} is not in the reference table (newer/older than known).`,
    'Verify alignment with: npx expo install --check');
} else {
  // React Native
  const rnMinor = minorKey(deps['react-native']);
  if (!rnMinor) {
    add('CRITICAL', 'NO_RN', 'react-native not resolvable.',
      'npx expo install --fix');
  } else if (rnMinor !== expected.rn) {
    add('CRITICAL', 'RN_MISMATCH',
      `SDK ${sdkMajor} expects react-native ${expected.rn}.x, found ${rnMinor}.x.`,
      'npx expo install --fix  (do NOT hand-edit react-native)');
  } else {
    add('LOW', 'RN_OK', `react-native ${rnMinor}.x matches SDK ${sdkMajor}.`);
  }

  // React
  const reactMinor = minorKey(deps.react);
  if (!reactMinor) {
    add('HIGH', 'NO_REACT', 'react not resolvable.', 'npx expo install --fix');
  } else if (reactMinor !== expected.react) {
    add('HIGH', 'REACT_MISMATCH',
      `SDK ${sdkMajor} expects react ${expected.react}.x, found ${reactMinor}.x.`,
      `npx expo install react@${expected.react}.0 react-dom@${expected.react}.0`);
  } else {
    add('LOW', 'REACT_OK', `react ${reactMinor}.x matches SDK ${sdkMajor}.`);
  }
}

// Stale-SDK advisory
const NEWEST_KNOWN = Math.max(...Object.keys(SDK_MAP).map(Number));
if (sdkMajor <= NEWEST_KNOWN - 3) {
  add('MEDIUM', 'STALE_SDK',
    `Expo SDK ${sdkMajor} is several majors behind (newest known ${NEWEST_KNOWN}); EAS image support expires for old SDKs.`,
    'Plan a staged upgrade (one major at a time) — see checks/upgrade-checklist.md.');
}

emit();

function emit() {
  const order = { CRITICAL: 0, HIGH: 1, MEDIUM: 2, LOW: 3 };
  findings.sort((a, b) => order[a.severity] - order[b.severity]);
  const counts = findings.reduce((m, f) => {
    m[f.severity] = (m[f.severity] || 0) + 1; return m;
  }, {});
  process.stderr.write(`\n[check-sdk-alignment] SDK ${sdkMajor ?? '?'} @ ${projectRoot}\n`);
  findings.forEach((f) => {
    process.stderr.write(`  [${f.severity}] ${f.code}: ${f.message}\n`);
    if (f.fix) process.stderr.write(`      fix: ${f.fix}\n`);
  });
  process.stderr.write(`  summary: ${JSON.stringify(counts)}\n`);
  process.stdout.write(JSON.stringify(
    { script: 'check-sdk-alignment', projectRoot, sdkMajor, counts, findings },
    null, 2));
}
