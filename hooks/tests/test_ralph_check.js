#!/usr/bin/env node
/**
 * Tests for ralph-check.js — Ralph Loop Completion Hook
 *
 * Run: node .claude/hooks/tests/test_ralph_check.js
 * Exit: 0 = all pass | 1 = one or more fail
 */

'use strict';

const fs = require('fs');
const path = require('path');
const os = require('os');
const { execSync, spawnSync } = require('child_process');

// ANSI
const G = '\x1b[32m';
const R = '\x1b[31m';
const X = '\x1b[0m';
const B = '\x1b[1m';

const RALPH_HOOK = path.resolve(__dirname, '..', 'ralph-check.js');

let passed = 0;
let failed = 0;

function test(name, fn) {
  try {
    fn();
    console.log(`  ${G}PASS ✅${X} ${name}`);
    passed++;
  } catch (err) {
    console.log(`  ${R}FAIL ❌${X} ${name}`);
    console.log(`       ${err.message}`);
    failed++;
  }
}

function assert(condition, msg) {
  if (!condition) throw new Error(msg || 'Assertion failed');
}

function assertEqual(a, b, msg) {
  if (a !== b) throw new Error(msg || `Expected ${JSON.stringify(b)}, got ${JSON.stringify(a)}`);
}

/**
 * Run ralph-check.js with a given state and return {output, exitCode}.
 * Sets up a .claude/ directory structure in a tmp dir and runs the hook
 * from that directory (using cwd) so process.cwd()-based paths resolve correctly.
 */
function runRalph(stateJson, opts = {}) {
  const tmpDir = fs.mkdtempSync(path.join(os.tmpdir(), 'ralph-test-'));
  const claudeDir = path.join(tmpDir, '.claude');
  const metricsDir = path.join(claudeDir, 'metrics');

  fs.mkdirSync(claudeDir, { recursive: true });
  fs.mkdirSync(metricsDir, { recursive: true });

  if (stateJson) {
    fs.writeFileSync(path.join(claudeDir, 'ralph-state.json'), JSON.stringify(stateJson));
  }
  if (opts.withCompleteFile) {
    fs.writeFileSync(path.join(claudeDir, 'ralph-complete.txt'), 'done');
  }

  const result = spawnSync('node', [RALPH_HOOK], {
    input: '',
    encoding: 'utf8',
    cwd: tmpDir,  // hook uses process.cwd() to build paths
  });

  // Cleanup
  try { fs.rmSync(tmpDir, { recursive: true }); } catch {}

  return {
    stdout: result.stdout,
    exitCode: result.status,
  };
}

// ── Tests ──────────────────────────────────────────────────────────────────

console.log();
console.log(`${B}Ralph Loop Hook Tests${X}`);
console.log();

test('returns ok:true when no ralph state exists', () => {
  const { stdout, exitCode } = runRalph(null);
  const json = JSON.parse(stdout.trim());
  assert(json.ok === true, `Expected ok:true, got: ${JSON.stringify(json)}`);
  assertEqual(exitCode, 0, 'Expected exit code 0');
});

test('returns continue:true when state exists and not complete', () => {
  const { stdout, exitCode } = runRalph({
    active: true,
    currentIteration: 1,
    maxIterations: 10,
    task: 'Fix the bug',
    startTime: new Date().toISOString(),
  });
  const json = JSON.parse(stdout.trim());
  // Hook should block stop (ok: false) with a continue message
  assert('continue' in json || json.ok === false, `Expected continue or ok:false, got: ${JSON.stringify(json)}`);
});

test('returns ok:true when complete file exists', () => {
  const { stdout, exitCode } = runRalph(
    { active: true, currentIteration: 5, maxIterations: 10, task: 'Fix the bug', startTime: new Date().toISOString() },
    { withCompleteFile: true }
  );
  const json = JSON.parse(stdout.trim());
  assert(json.ok === true, `Expected ok:true on completion signal, got: ${JSON.stringify(json)}`);
});

test('returns ok:false when max iterations reached (hard cap)', () => {
  const { stdout, exitCode } = runRalph({
    active: true,
    currentIteration: 50,  // hook will increment to 51, > hard cap of 50
    maxIterations: 50,
    task: 'Fix the bug',
    startTime: new Date().toISOString(),
  });
  const json = JSON.parse(stdout.trim());
  // Hard cap reached — must block with reason (abort)
  assert(json.ok === false, `Expected ok:false at hard cap, got: ${JSON.stringify(json)}`);
  assert(json.reason && json.reason.includes('ABORTED'), `Expected ABORTED reason, got: ${json.reason}`);
});

test('output is valid JSON', () => {
  const { stdout } = runRalph(null);
  assert(stdout.trim().startsWith('{'), 'Output must start with {');
  JSON.parse(stdout.trim()); // Throws if invalid JSON
});

test('ralph-check.js has valid JS syntax', () => {
  execSync(`node --check "${RALPH_HOOK}"`, { stdio: 'pipe' });
});

// ── Summary ────────────────────────────────────────────────────────────────

console.log();
const total = passed + failed;
const allPass = failed === 0;
const color = allPass ? G : R;
console.log(`${B}${color}  ${allPass ? '🎯' : '⚠️ '} ${passed}/${total} tests passing${X}`);
console.log();

process.exit(allPass ? 0 : 1);
