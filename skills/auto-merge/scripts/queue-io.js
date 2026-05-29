#!/usr/bin/env node
// Atomic read-merge-prune-write for auto-ship-queue.json.
// Usage: node queue-io.js update-and-prune <queue-path> '<json-array>'
const fs = require('fs');

const [,, command, queuePath, updatesJson] = process.argv;

if (command !== 'update-and-prune') {
  console.error(`Unknown command: ${command}`);
  process.exit(1);
}

if (!fs.existsSync(queuePath)) {
  console.log(`Queue file not found at ${queuePath}. Nothing to update.`);
  process.exit(0);
}

let queue;
try {
  queue = JSON.parse(fs.readFileSync(queuePath, 'utf8'));
} catch (e) {
  console.error(`Failed to parse queue file: ${e.message}`);
  process.exit(1);
}

const updates = JSON.parse(updatesJson);
const updateMap = new Map(updates.map(u => [u.prNumber, u.status]));
const PRUNE = new Set(['merged', 'abandoned']);

const updated = queue
  .map(entry => {
    const newStatus = updateMap.get(entry.prNumber);
    if (newStatus !== undefined) {
      if (!updateMap.has(entry.prNumber)) {
        console.warn(`Warning: prNumber ${entry.prNumber} not found in queue — skipped`);
      }
      return { ...entry, status: newStatus };
    }
    return entry;
  })
  .filter(entry => !PRUNE.has(entry.status));

const tmpPath = queuePath + '.tmp';
fs.writeFileSync(tmpPath, JSON.stringify(updated, null, 2));
fs.renameSync(tmpPath, queuePath);

const pruned = queue.length - updated.length;
console.log(`Queue updated. ${updates.length} status changes applied. ${pruned} entries pruned.`);
