#!/usr/bin/env node
/**
 * session-observer.js — Stop Hook: Session Pattern Observer
 *
 * Analyzes the ending session to extract behavioral patterns and feed
 * the instinct learning engine. Runs AFTER context-engine.py and state-sync.py.
 *
 * INDEPENDENT from state-sync.py — reads/writes ONLY to:
 *   .claude/instincts/observations.jsonl
 *   .claude/instincts/personal/*.yaml
 *   .claude/instincts/evolved/*.yaml
 *
 * Never touches: .sdlc/state/, MASTER_GUIDE.md, .claude/STATE.md
 *
 * Performance budget: < 200ms
 * Exit: always 0 — never block session close
 *
 * Pattern detection signals:
 *   user_corrections     - correction/rewrite keywords in session
 *   error_resolutions    - recent git commits with fix/bugfix pattern
 *   repeated_workflows   - same tool sequence 3+ times in git log
 *   tool_preferences     - dominant tool category in recent activity
 *   rejected_suggestions - rejection keywords in session
 */

'use strict';

const fs            = require('fs');
const path          = require('path');
const { execSync }  = require('child_process');

const ROOT          = path.resolve(__dirname, '../..');
const ENGINE_PATH   = path.join(ROOT, '.claude', 'scripts', 'instinct-engine.js');

// ── Safe require of instinct-engine ──────────────────────────────────────────
let engine;
try {
  engine = require(ENGINE_PATH);
} catch {
  // Engine not available — exit silently
  process.stdout.write('{}');
  process.exit(0);
}

const { addObservation, compileInstincts, decayAll, cluster, VALID_DOMAINS } = engine;

// ── Helpers ───────────────────────────────────────────────────────────────────

const SESSION_ID = new Date().toISOString();

function safeExec(cmd, opts = {}) {
  try {
    return execSync(cmd, { encoding: 'utf8', timeout: 60, stdio: ['pipe','pipe','pipe'], ...opts }).trim();
  } catch {
    return '';
  }
}

function observe(type, domain, signal) {
  try {
    addObservation({ type, domain, signal, sessionId: SESSION_ID });
  } catch { /* never throw */ }
}

// ── Pattern detectors ─────────────────────────────────────────────────────────

/**
 * Analyze recent git log (last 4 hours) for error_resolution patterns.
 * Heuristic: commits with "fix", "bugfix", "revert", "hotfix" in message.
 */
function detectErrorResolutions() {
  const log = safeExec('git log --since="4 hours ago" --oneline 2>/dev/null');
  if (!log) return;

  const lines = log.split('\n').filter(Boolean);
  const fixLines = lines.filter(l => /\b(fix|bug|revert|hotfix|patch|repair)\b/i.test(l));

  if (fixLines.length >= 2) {
    // Detect which domain by looking at changed files
    const files = safeExec('git diff --name-only HEAD~' + Math.min(fixLines.length, 5) + ' HEAD 2>/dev/null');
    const domain = inferDomainFromFiles(files.split('\n'));
    observe('error_resolutions', domain, `${fixLines.length} fix commits: ${fixLines[0]?.slice(0, 60)}`);
  }
}

/**
 * Detect repeated workflow patterns from git log.
 * Heuristic: same file touched 3+ times in recent commits.
 */
function detectRepeatedWorkflows() {
  const log = safeExec('git log --since="4 hours ago" --name-only --format="" 2>/dev/null');
  if (!log) return;

  const fileCounts = new Map();
  for (const f of log.split('\n').filter(Boolean)) {
    fileCounts.set(f, (fileCounts.get(f) || 0) + 1);
  }

  for (const [file, count] of fileCounts) {
    if (count >= 3) {
      const domain = inferDomainFromFiles([file]);
      observe('repeated_workflows', domain, `File edited ${count}x in session: ${file}`);
    }
  }
}

/**
 * Detect tool preferences from recent git commit patterns.
 * Heuristic: frequency of test/build/lint commands in commit messages.
 */
function detectToolPreferences() {
  const log = safeExec('git log --since="8 hours ago" --oneline 2>/dev/null');
  if (!log) return;

  const lower = log.toLowerCase();
  const tools = {
    'npm test':   (lower.match(/\btest\b/g) || []).length,
    'pnpm':       (lower.match(/\bpnpm\b/g) || []).length,
    'vitest':     (lower.match(/\bvitest\b/g) || []).length,
    'cargo':      (lower.match(/\bcargo\b/g) || []).length,
    'docker':     (lower.match(/\bdocker\b/g) || []).length,
  };

  const [topTool, topCount] = Object.entries(tools).sort((a, b) => b[1] - a[1])[0] || [];
  if (topTool && topCount >= 2) {
    observe('tool_preferences', 'testing', `Frequently uses ${topTool} (${topCount}x in recent commits)`);
  }
}

/**
 * Detect patterns from stdin session data (if provided by Claude Code).
 * The Stop hook may receive session metadata via stdin.
 */
function detectFromStdin(raw) {
  if (!raw || raw.trim() === '{}' || raw.trim() === '') return;

  let data;
  try { data = JSON.parse(raw); } catch { return; }

  // Look for correction signals in any string fields
  const content = JSON.stringify(data).toLowerCase();

  if (/\b(actually|no,|wrong|incorrect|instead use|replace with|not that)\b/.test(content)) {
    const domain = inferDomainFromContent(content);
    observe('user_corrections', domain, 'Session contained correction signals');
  }

  if (/\b(reject|don't|avoid|stop doing|please don't|no thanks)\b/.test(content)) {
    const domain = inferDomainFromContent(content);
    observe('rejected_suggestions', domain, 'Session contained rejection signals');
  }
}

// ── Domain inference ──────────────────────────────────────────────────────────

function inferDomainFromFiles(files) {
  const allFiles = files.join(' ').toLowerCase();
  if (/\.(spec|test)\.|__tests__|test\//i.test(allFiles)) return 'testing';
  if (/\.git|gitignore|gitconfig/i.test(allFiles))        return 'git';
  if (/architecture|design|schema|model/i.test(allFiles)) return 'architecture';
  if (/debug|log|trace|error/i.test(allFiles))            return 'debugging';
  return 'code-style';
}

function inferDomainFromContent(content) {
  if (/test|spec|coverage|jest|vitest|pytest/.test(content)) return 'testing';
  if (/git|commit|branch|merge|rebase/.test(content))        return 'git';
  if (/architect|pattern|design|module|layer/.test(content)) return 'architecture';
  if (/debug|error|stack|trace|exception/.test(content))     return 'debugging';
  return 'code-style';
}

// ── Derive IDs of instincts reinforced this session (for decay skip-list) ────

function getReinforcedIds() {
  // Any instinct whose domain matches detected observation domains this session
  try {
    const obsFile = path.join(ROOT, '.claude', 'instincts', 'observations.jsonl');
    if (!fs.existsSync(obsFile)) return [];
    const recent = fs.readFileSync(obsFile, 'utf8')
      .split('\n').filter(Boolean)
      .map(l => { try { return JSON.parse(l); } catch { return null; } })
      .filter(Boolean)
      .filter(o => o.sessionId === SESSION_ID)
      .map(o => `${o.type.replace(/_/g, '-')}-${o.domain}`);
    return [...new Set(recent)];
  } catch { return []; }
}

// ── Main ──────────────────────────────────────────────────────────────────────

async function main() {
  // Consume stdin (required for hooks)
  let stdin = '';
  try {
    process.stdin.setEncoding('utf8');
    for await (const chunk of process.stdin) stdin += chunk;
  } catch { /* stdin may not be readable */ }

  const deadline = Date.now() + 180; // 180ms hard deadline

  try {
    // 1. Pattern detection from stdin
    detectFromStdin(stdin);

    if (Date.now() < deadline) detectErrorResolutions();
    if (Date.now() < deadline) detectRepeatedWorkflows();
    if (Date.now() < deadline) detectToolPreferences();

    // 2. Compile observations → instinct YAML files
    if (Date.now() < deadline) compileInstincts();

    // 3. Decay instincts not seen this session
    if (Date.now() < deadline) {
      const reinforced = getReinforcedIds();
      decayAll(reinforced);
    }

    // 4. Check for cluster promotions (only if well within budget)
    if (Date.now() < deadline - 40) cluster();

  } catch {
    // Never fail — Stop hook must exit cleanly
  }

  process.stdout.write('{}');
  process.exit(0);
}

main();
