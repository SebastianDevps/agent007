#!/usr/bin/env node
/**
 * agent007-statusline.js — PreToolUse Hook (statusline fallback)
 *
 * Renders a compact Agent007 status line showing:
 *   - previousSkill (from .claude/.session-state.json)
 *   - Tarea Activa (from .claude/STATE.md)
 *   - Current directory (basename)
 *   - Context window bar + percentage
 *   - Ralph active indicator (from .claude/ralph-complete.txt recency)
 *
 * Registered as PreToolUse (no matcher) — fires once per tool invocation.
 * Output: hookSpecificOutput.additionalContext with the ANSI status string.
 *
 * No external dependencies — Node.js built-ins only (fs, path, process, os).
 */

'use strict';

const fs = require('fs');
const path = require('path');
const os = require('os');

// ---------------------------------------------------------------------------
// Path resolution
// ---------------------------------------------------------------------------

function findProjectRoot(startDir) {
  let current = startDir || __dirname;
  while (current !== path.dirname(current)) {
    if (fs.existsSync(path.join(current, '.claude'))) {
      return current;
    }
    current = path.dirname(current);
  }
  return process.cwd();
}

const PROJECT_ROOT = findProjectRoot(__dirname);
const SESSION_STATE_FILE = path.join(PROJECT_ROOT, '.claude', '.session-state.json');
const STATE_MD_FILE = path.join(PROJECT_ROOT, '.claude', 'STATE.md');
const RALPH_COMPLETE_FILE = path.join(PROJECT_ROOT, '.claude', 'ralph-complete.txt');

// ---------------------------------------------------------------------------
// ANSI helpers
// ---------------------------------------------------------------------------

const ANSI = {
  reset: '\x1b[0m',
  bold: '\x1b[1m',
  green: '\x1b[32m',
  yellow: '\x1b[33m',
  red: '\x1b[31m',
  blink: '\x1b[5m',
  orange: '\x1b[38;5;208m',
  cyan: '\x1b[36m',
  dim: '\x1b[2m'
};

/**
 * Build a 10-segment Unicode bar showing used / remaining.
 * █ = used, ░ = remaining
 * @param {number} remainingPct - 0..100
 * @returns {string} colored bar string
 */
function buildContextBar(remainingPct) {
  const segments = 10;
  const usedPct = 100 - remainingPct;
  const usedSegments = Math.round((usedPct / 100) * segments);
  const freeSegments = segments - usedSegments;

  const bar = '█'.repeat(usedSegments) + '░'.repeat(freeSegments);

  let color;
  if (remainingPct >= 70) {
    color = ANSI.green;
  } else if (remainingPct >= 50) {
    color = ANSI.yellow;
  } else if (remainingPct >= 30) {
    color = ANSI.orange;
  } else {
    color = ANSI.blink + ANSI.red;
  }

  return `${color}${bar}${ANSI.reset}`;
}

// ---------------------------------------------------------------------------
// Data readers (all silent-fail)
// ---------------------------------------------------------------------------

function readSessionState() {
  try {
    if (!fs.existsSync(SESSION_STATE_FILE)) return null;
    return JSON.parse(fs.readFileSync(SESSION_STATE_FILE, 'utf-8'));
  } catch (_) {
    return null;
  }
}

function readActiveTarea() {
  try {
    if (!fs.existsSync(STATE_MD_FILE)) return null;
    const content = fs.readFileSync(STATE_MD_FILE, 'utf-8');
    // Match: - **Tarea Activa**: <value>
    const match = content.match(/[-*]\s*\*\*Tarea Activa\*\*\s*:\s*(.+)/);
    if (!match) return null;
    const value = match[1].trim();
    return value === 'ninguna' ? null : value;
  } catch (_) {
    return null;
  }
}

function isRalphActive() {
  try {
    if (!fs.existsSync(RALPH_COMPLETE_FILE)) return false;
    // Consider ralph active if the file was modified within last 5 minutes
    const stat = fs.statSync(RALPH_COMPLETE_FILE);
    const ageMs = Date.now() - stat.mtimeMs;
    return ageMs < 5 * 60 * 1000;
  } catch (_) {
    return false;
  }
}

function extractRemainingPct(payload) {
  if (!payload) return null;

  // payload.context_window.remaining_percentage
  const ctx = payload.context_window;
  if (ctx && typeof ctx === 'object') {
    if (typeof ctx.remaining_percentage === 'number') return ctx.remaining_percentage;
    if (ctx.tokens_remaining != null && ctx.tokens_total > 0) {
      return (ctx.tokens_remaining / ctx.tokens_total) * 100;
    }
  }

  // payload.hook_event_data.context_window
  const eventCtx = (payload.hook_event_data || {}).context_window;
  if (eventCtx && typeof eventCtx === 'object') {
    if (typeof eventCtx.remaining_percentage === 'number') return eventCtx.remaining_percentage;
  }

  return null;
}

function extractWorkspaceDir(payload) {
  if (!payload) return path.basename(PROJECT_ROOT);
  const ws = payload.workspace || payload.hook_event_data?.workspace || {};
  const dir = ws.current_dir || ws.cwd || PROJECT_ROOT;
  return path.basename(dir);
}

// ---------------------------------------------------------------------------
// Status line builder
// ---------------------------------------------------------------------------

function truncate(str, maxLen) {
  if (!str) return '';
  if (str.length <= maxLen) return str;
  return str.slice(0, maxLen - 1) + '…';
}

function buildStatusLine(payload) {
  const state = readSessionState();
  const previousSkill = state ? state.previousSkill : null;
  const tarea = readActiveTarea();
  const ralphActive = isRalphActive();
  const remainingPct = extractRemainingPct(payload) || 100;
  const dirName = extractWorkspaceDir(payload);

  const contextBar = buildContextBar(remainingPct);
  const pctStr = `${Math.round(remainingPct)}%`;

  const prefix = `${ANSI.bold}${ANSI.cyan}agent007${ANSI.reset}`;
  const sep = `${ANSI.dim} │ ${ANSI.reset}`;

  let middle;

  if (ralphActive) {
    const tareaDisplay = tarea ? ` │ ${truncate(tarea, 30)}` : '';
    middle = `${ANSI.yellow}🔄 ralph${ANSI.reset}${tareaDisplay}`;
  } else if (previousSkill) {
    const tareaDisplay = tarea ? ` → ${truncate(tarea, 20)}` : '';
    middle = `${ANSI.cyan}⚡ ${truncate(previousSkill, 20)}${ANSI.reset}${tareaDisplay}`;
  } else if (tarea) {
    middle = truncate(tarea, 30);
  } else {
    middle = `${ANSI.dim}sin tarea activa${ANSI.reset}`;
  }

  const rightSide = `${ANSI.dim}${dirName}${ANSI.reset} ${contextBar} ${pctStr}`;

  return `${prefix}${sep}${middle}${sep}${rightSide}`;
}

// ---------------------------------------------------------------------------
// Main
// ---------------------------------------------------------------------------

function main() {
  let payload = null;

  try {
    const raw = fs.readFileSync('/dev/stdin', 'utf-8');
    if (raw.trim()) payload = JSON.parse(raw);
  } catch (_) {}

  try {
    const statusLine = buildStatusLine(payload);
    const output = {
      additionalContext: statusLine
    };
    process.stdout.write(JSON.stringify(output) + '\n');
  } catch (_) {
    // Never block the tool
    process.stdout.write('{}\n');
  }
}

main();
