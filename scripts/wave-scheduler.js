#!/usr/bin/env node
/**
 * wave-scheduler.js — Dependency-aware wave grouper for subagent execution
 *
 * Reads tasks.md, parses task blocks with depends_on fields, and groups
 * them into parallel execution waves using topological sort (Kahn's algorithm).
 *
 * Usage:
 *   node wave-scheduler.js --tasks docs/changes/<feature>/tasks.md
 *   node wave-scheduler.js --tasks <path> --json        → raw JSON output
 *   node wave-scheduler.js --tasks <path> --summary     → human-readable summary
 *
 * Output (default): JSON array of waves
 *   [
 *     { wave: 1, tasks: ["TASK-001", "TASK-002"] },
 *     { wave: 2, tasks: ["TASK-003"] },
 *     { wave: 3, tasks: ["TASK-004", "TASK-005"] }
 *   ]
 *
 * Exit codes:
 *   0 — success, waves written to stdout
 *   1 — error (file not found, circular dependency, parse error)
 */

'use strict';

const fs = require('fs');
const path = require('path');

// ── Parser ────────────────────────────────────────────────────────────────────

/**
 * Parse tasks.md into an array of task objects.
 * Handles the markdown format produced by Skill('plan'):
 *
 * ## TASK-001
 * title: Add user validation
 * domain: backend
 * depends_on: []
 * ...
 */
function parseTasks(content) {
  const tasks = [];
  // Split on ## TASK-NNN headers
  const blocks = content.split(/^## (TASK-\d+)\s*$/m);

  for (let i = 1; i < blocks.length; i += 2) {
    const taskId = blocks[i].trim();
    const body = blocks[i + 1] || '';

    const task = {
      id: taskId,
      title: extractField(body, 'title') || taskId,
      domain: extractField(body, 'domain') || 'mixed',
      depends_on: extractDependsList(body),
      verify_cmd: extractField(body, 'verify_cmd') || '',
      estimated_min: parseInt(extractField(body, 'estimated_min') || '3', 10),
    };

    tasks.push(task);
  }

  return tasks;
}

function extractField(body, field) {
  const regex = new RegExp(`^${field}:\\s*(.+)$`, 'm');
  const match = body.match(regex);
  return match ? match[1].trim() : null;
}

function extractDependsList(body) {
  const match = body.match(/^depends_on:\s*(.+)$/m);
  if (!match) return [];
  const raw = match[1].trim();
  // Handle: [], [TASK-001], [TASK-001, TASK-002]
  if (raw === '[]' || raw === '') return [];
  return raw
    .replace(/[\[\]]/g, '')
    .split(',')
    .map((s) => s.trim())
    .filter(Boolean);
}

// ── Topological Sort (Kahn's algorithm) ───────────────────────────────────────

/**
 * Groups tasks into parallel execution waves.
 * Tasks with no pending dependencies go in the same wave.
 * Returns array of waves, each wave is an array of task IDs.
 */
function computeWaves(tasks) {
  const taskMap = new Map(tasks.map((t) => [t.id, t]));
  const inDegree = new Map(tasks.map((t) => [t.id, 0]));
  const dependents = new Map(tasks.map((t) => [t.id, []]));

  // Build graph
  for (const task of tasks) {
    for (const dep of task.depends_on) {
      if (!taskMap.has(dep)) {
        throw new Error(
          `Task ${task.id} depends on unknown task: ${dep}`
        );
      }
      inDegree.set(task.id, (inDegree.get(task.id) || 0) + 1);
      dependents.get(dep).push(task.id);
    }
  }

  const waves = [];
  let remaining = new Set(tasks.map((t) => t.id));

  while (remaining.size > 0) {
    // Tasks with in-degree 0 can run in parallel this wave
    const wave = [];
    for (const id of remaining) {
      if (inDegree.get(id) === 0) wave.push(id);
    }

    if (wave.length === 0) {
      const cycle = [...remaining].join(', ');
      throw new Error(`Circular dependency detected among: ${cycle}`);
    }

    waves.push(wave);

    // Remove completed tasks, decrement dependents
    for (const id of wave) {
      remaining.delete(id);
      for (const dep of dependents.get(id)) {
        inDegree.set(dep, inDegree.get(dep) - 1);
      }
    }
  }

  return waves;
}

// ── Output formatters ─────────────────────────────────────────────────────────

function formatJson(waves, tasks) {
  const taskMap = new Map(tasks.map((t) => [t.id, t]));
  return JSON.stringify(
    waves.map((wave, i) => ({
      wave: i + 1,
      tasks: wave,
      parallel: wave.length > 1,
      estimated_min: Math.max(
        ...wave.map((id) => taskMap.get(id)?.estimated_min || 3)
      ),
    })),
    null,
    2
  );
}

function formatSummary(waves, tasks) {
  const taskMap = new Map(tasks.map((t) => [t.id, t]));
  const totalMin = waves.reduce(
    (sum, wave) =>
      sum + Math.max(...wave.map((id) => taskMap.get(id)?.estimated_min || 3)),
    0
  );

  const lines = [
    `📋 Wave Schedule`,
    `   Tasks: ${tasks.length}  |  Waves: ${waves.length}  |  Est. time: ~${totalMin} min`,
    '',
  ];

  for (let i = 0; i < waves.length; i++) {
    const wave = waves[i];
    const parallel = wave.length > 1 ? `(paralelo × ${wave.length})` : '(secuencial)';
    lines.push(`Wave ${i + 1} ${parallel}:`);
    for (const id of wave) {
      const t = taskMap.get(id);
      lines.push(`  ${id}: ${t?.title || id} [${t?.domain || 'mixed'}]`);
    }
    lines.push('');
  }

  return lines.join('\n');
}

// ── Main ──────────────────────────────────────────────────────────────────────

function main() {
  const args = process.argv.slice(2);
  const tasksIdx = args.indexOf('--tasks');
  const wantsJson = args.includes('--json');
  const wantsSummary = args.includes('--summary');

  if (tasksIdx === -1 || !args[tasksIdx + 1]) {
    process.stderr.write('Usage: node wave-scheduler.js --tasks <path>\n');
    process.exit(1);
  }

  const tasksPath = args[tasksIdx + 1];
  const fullPath = path.isAbsolute(tasksPath)
    ? tasksPath
    : path.join(process.cwd(), tasksPath);

  if (!fs.existsSync(fullPath)) {
    process.stderr.write(`Error: tasks file not found: ${fullPath}\n`);
    process.exit(1);
  }

  let content;
  try {
    content = fs.readFileSync(fullPath, 'utf8');
  } catch (err) {
    process.stderr.write(`Error reading file: ${err.message}\n`);
    process.exit(1);
  }

  let tasks;
  try {
    tasks = parseTasks(content);
  } catch (err) {
    process.stderr.write(`Parse error: ${err.message}\n`);
    process.exit(1);
  }

  if (tasks.length === 0) {
    process.stderr.write(`No tasks found in: ${fullPath}\n`);
    process.exit(1);
  }

  let waves;
  try {
    waves = computeWaves(tasks);
  } catch (err) {
    process.stderr.write(`Scheduling error: ${err.message}\n`);
    process.exit(1);
  }

  if (wantsSummary) {
    process.stdout.write(formatSummary(waves, tasks) + '\n');
  } else {
    // Default and --json both output JSON
    process.stdout.write(formatJson(waves, tasks) + '\n');
  }

  process.exit(0);
}

main();
