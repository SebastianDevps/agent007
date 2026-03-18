#!/usr/bin/env node
/**
 * Ralph Loop Stop Hook
 *
 * Intercepts Claude's stop signal when a ralph loop is active.
 * Blocks stop + re-injects continuation context until:
 *   - Completion file found (.claude/ralph-complete.txt), OR
 *   - Max iterations reached (abort with reason), OR
 *   - Ralph is not active (pass through to next hook)
 *
 * State file:   .claude/ralph-state.json   (written by /ralph-loop command)
 * Complete file: .claude/ralph-complete.txt (written by Claude when task is done)
 *
 * Output format: JSON {"ok": true} or {"ok": false, "reason": "..."}
 * Claude Code reads this to allow or block the stop event.
 */

'use strict';

const fs = require('fs');
const path = require('path');

const projectDir = process.cwd();
const STATE_FILE  = path.join(projectDir, '.claude', 'ralph-state.json');
const COMPLETE_FILE = path.join(projectDir, '.claude', 'ralph-complete.txt');
const METRICS_FILE = path.join(projectDir, '.claude', 'metrics', 'ralph-loops.jsonl');

function allow(message) {
  const out = message ? { ok: true, message } : { ok: true };
  process.stdout.write(JSON.stringify(out));
}

function block(reason) {
  process.stdout.write(JSON.stringify({ ok: false, reason }));
}

function writeMetric(state, status, abortReason) {
  try {
    const metric = {
      loopId: state.loopId || 'unknown',
      task: state.task,
      status,
      abortReason: abortReason || undefined,
      iterations: state.currentIteration,
      durationSeconds: Math.round((Date.now() - new Date(state.startTime).getTime()) / 1000),
      completedAt: new Date().toISOString(),
    };
    fs.appendFileSync(METRICS_FILE, JSON.stringify(metric) + '\n');
  } catch {
    // metrics are non-critical, ignore write failures
  }
}

function cleanup(stateFile, updateFields) {
  try {
    const current = JSON.parse(fs.readFileSync(stateFile, 'utf8'));
    const updated = { ...current, ...updateFields, active: false };
    fs.writeFileSync(stateFile, JSON.stringify(updated, null, 2));
  } catch {}
  try { fs.unlinkSync(COMPLETE_FILE); } catch {}
}

function main() {
  // ── Not in ralph mode: pass through ────────────────────────────────────────
  if (!fs.existsSync(STATE_FILE)) {
    allow();
    return;
  }

  let state;
  try {
    state = JSON.parse(fs.readFileSync(STATE_FILE, 'utf8'));
  } catch {
    allow();
    return;
  }

  if (!state.active) {
    allow();
    return;
  }

  // ── Check completion via file signal ────────────────────────────────────────
  if (fs.existsSync(COMPLETE_FILE)) {
    const duration = Math.round((Date.now() - new Date(state.startTime).getTime()) / 1000);
    cleanup(STATE_FILE, {
      completedAt: new Date().toISOString(),
      totalIterations: state.currentIteration,
      durationSeconds: duration,
    });
    writeMetric(state, 'COMPLETED');
    allow(`✅ Ralph Loop COMPLETE — ${state.currentIteration} iteration(s), ${duration}s`);
    return;
  }

  // ── Increment iteration ─────────────────────────────────────────────────────
  const newIteration = (state.currentIteration || 0) + 1;
  state.currentIteration = newIteration;

  // ── Check max iterations ────────────────────────────────────────────────────
  const maxIterations = Math.min(state.maxIterations || 20, 50); // hard cap at 50
  if (newIteration > maxIterations) {
    cleanup(STATE_FILE, {
      abortReason: 'MAX_ITERATIONS',
      abortedAt: new Date().toISOString(),
    });
    writeMetric(state, 'ABORTED', 'MAX_ITERATIONS');
    block(
      `🔄 RALPH LOOP ABORTED\n` +
      `Max iterations (${maxIterations}) reached.\n` +
      `Task: "${state.task}"\n\n` +
      `The task was not completed. Options:\n` +
      `- Run /ralph-loop again with a different approach\n` +
      `- Increase --max-iterations (max 50)\n` +
      `- Break the task into smaller sub-tasks`
    );
    return;
  }

  // ── Save updated state ──────────────────────────────────────────────────────
  try {
    fs.writeFileSync(STATE_FILE, JSON.stringify(state, null, 2));
  } catch {}

  // ── Build continuation context ──────────────────────────────────────────────
  const pct = Math.round((newIteration / maxIterations) * 100);
  const warning = pct >= 80
    ? `\n⚠️  ${pct}% of iteration budget used (${newIteration}/${maxIterations}).`
    : '';

  const reqSection = (state.requirements || []).length > 0
    ? `\nRequirements:\n${state.requirements.map(r => `- ${r}`).join('\n')}`
    : '';

  const criteriaSection = (state.successCriteria || []).length > 0
    ? `\nSuccess Criteria:\n${state.successCriteria.map(c => `- ${c}`).join('\n')}`
    : '';

  const verifySection = state.verificationCommand
    ? `\nVerification: run \`${state.verificationCommand}\` — all checks must pass.`
    : '';

  const reason = [
    `🔄 RALPH LOOP — Iteration ${newIteration}/${maxIterations}${warning}`,
    `Task: ${state.task}`,
    ``,
    `The task is NOT complete — <promise>${state.completionPromise}</promise> was not found.`,
    reqSection,
    criteriaSection,
    verifySection,
    ``,
    `When ALL criteria are met:`,
    `1. Output <promise>${state.completionPromise}</promise> in your response`,
    `2. Run: echo "${state.completionPromise}" > .claude/ralph-complete.txt`,
    ``,
    `Continue working. Analyze what's missing and fix it.`,
  ].filter(l => l !== undefined).join('\n').trim();

  block(reason);
}

main();
