#!/usr/bin/env node
/**
 * Agent007 — Security Scanner
 * Local-only scan of the Agent007 ecosystem for policy violations and
 * potential prompt injection / configuration weaknesses.
 *
 * 5 categories:
 *   1. CLAUDE.md         — no safety-bypass phrases
 *   2. settings.json     — permissions.deny covers critical commands
 *   3. hooks/            — no unsafe eval/exec patterns, no external curl
 *   4. skills/           — no prompt-injection instructions
 *   5. instincts/        — no suspiciously high confidence instincts
 *
 * Scoring (A–F):
 *   A  0 issues
 *   B  1-2 warnings
 *   C  3-4 warnings or 1 critical
 *   D  5+ warnings or 2 criticals
 *   F  3+ criticals
 *
 * Usage:
 *   node .claude/scripts/security-scan.js
 *   node .claude/scripts/security-scan.js --json
 *   node .claude/scripts/security-scan.js --category <1-5>
 *
 * Note: All analysis is LOCAL. No data is sent externally.
 */

'use strict';

const fs   = require('fs');
const path = require('path');

const ROOT       = path.resolve(__dirname, '../..');
const CLAUDE_DIR = path.join(ROOT, '.claude');

// ── ANSI ──────────────────────────────────────────────────────────────────────
const c = {
  reset:  '\x1b[0m',
  bold:   '\x1b[1m',
  green:  '\x1b[32m',
  yellow: '\x1b[33m',
  red:    '\x1b[31m',
  cyan:   '\x1b[36m',
  gray:   '\x1b[90m',
};

// ── Issue severity ────────────────────────────────────────────────────────────
const SEV = { WARNING: 'warning', CRITICAL: 'critical', OK: 'ok' };

function issue(severity, category, message, file = null) {
  return { severity, category, message, file };
}

// ── File traversal ────────────────────────────────────────────────────────────

function readFileSafe(filePath) {
  try { return fs.readFileSync(filePath, 'utf8'); }
  catch { return ''; }
}

function walkDir(dir, exts = ['.md', '.js', '.py', '.sh', '.yaml', '.yml', '.json']) {
  const results = [];
  if (!fs.existsSync(dir)) return results;
  try {
    const entries = fs.readdirSync(dir, { withFileTypes: true });
    for (const e of entries) {
      const full = path.join(dir, e.name);
      if (e.isDirectory()) {
        results.push(...walkDir(full, exts));
      } else if (exts.includes(path.extname(e.name))) {
        results.push(full);
      }
    }
  } catch { /* skip inaccessible dirs */ }
  return results;
}

// ── Category 1: CLAUDE.md safety bypass phrases ───────────────────────────────

const BYPASS_PATTERNS = [
  { pattern: /ignore\s+safety/i,           label: 'ignore safety' },
  { pattern: /bypass\s+(guard|check|rule)/i, label: 'bypass guard/check/rule' },
  { pattern: /disable\s+guard/i,            label: 'disable guard' },
  { pattern: /override\s+constraint/i,      label: 'override constraint' },
  { pattern: /ignore\s+previous\s+instructions/i, label: 'ignore previous instructions' },
  { pattern: /disregard\s+(all|your|the)\s+(rules|instructions|guidelines)/i, label: 'disregard rules' },
];

function scanClaudeMd() {
  const issues = [];
  const filePath = path.join(CLAUDE_DIR, 'CLAUDE.md');
  const content = readFileSafe(filePath);
  if (!content) return [issue(SEV.WARNING, 1, 'CLAUDE.md not found or empty', filePath)];

  for (const { pattern, label } of BYPASS_PATTERNS) {
    if (pattern.test(content)) {
      issues.push(issue(SEV.CRITICAL, 1, `Safety bypass phrase detected: "${label}"`, 'CLAUDE.md'));
    }
  }

  return issues;
}

// ── Category 2: settings.json permissions.deny ───────────────────────────────

const REQUIRED_DENY = [
  { pattern: /rm\s+-rf\s+\//, label: 'rm -rf /' },
  { pattern: /sudo/, label: 'sudo' },
];

function scanSettingsJson() {
  const issues = [];
  const filePath = path.join(CLAUDE_DIR, 'settings.json');
  let settings;

  try {
    settings = JSON.parse(fs.readFileSync(filePath, 'utf8'));
  } catch {
    return [issue(SEV.WARNING, 2, 'settings.json not found or invalid JSON', filePath)];
  }

  const denyList = (settings.permissions?.deny || []).join('\n');

  for (const { pattern, label } of REQUIRED_DENY) {
    if (!pattern.test(denyList)) {
      issues.push(issue(SEV.WARNING, 2, `permissions.deny missing protection for: ${label}`, 'settings.json'));
    }
  }

  // Check that allow list doesn't grant dangerous broad permissions
  const allowList = settings.permissions?.allow || [];
  if (allowList.includes('Bash(*:*)') || allowList.includes('Bash(*)')) {
    issues.push(issue(SEV.CRITICAL, 2, 'permissions.allow grants unrestricted Bash(*) — over-permissive', 'settings.json'));
  }

  return issues;
}

// ── Category 3: hooks/ unsafe patterns ───────────────────────────────────────

// JS/Python eval patterns that could be unsafe
const UNSAFE_EVAL_JS = [
  /\beval\s*\(/,
  /new\s+Function\s*\(/,
];
const UNSAFE_EVAL_PY = [
  /\beval\s*\(/,
  /\bexec\s*\([^)]*(?:input|request|user|argv|stdin)/i,  // exec with user input
];
// External curl in hook files
const EXTERNAL_CURL = /\bcurl\s+https?:\/\/(?!rtk-ai\.app|localhost|127\.)/;

function scanHooks() {
  const issues = [];
  const hooksDir = path.join(CLAUDE_DIR, 'hooks');
  const files = walkDir(hooksDir, ['.js', '.py', '.sh']);

  for (const file of files) {
    if (file.includes('/tests/')) continue;  // skip test fixtures
    const content = readFileSafe(file);
    const rel = path.relative(ROOT, file);

    // Check eval patterns
    const patterns = file.endsWith('.py') ? UNSAFE_EVAL_PY : UNSAFE_EVAL_JS;
    for (const pat of patterns) {
      if (pat.test(content)) {
        issues.push(issue(SEV.WARNING, 3, `Potentially unsafe eval/exec pattern`, rel));
        break;  // one warning per file
      }
    }

    // Check external curl
    if (EXTERNAL_CURL.test(content)) {
      issues.push(issue(SEV.CRITICAL, 3, `Hook makes external HTTP request via curl`, rel));
    }

    // Check for shell=True with dynamic content in Python (risky pattern)
    if (file.endsWith('.py') && /subprocess\.(run|call|check_output|Popen)\([^)]*shell\s*=\s*True/s.test(content)) {
      if (/f['"](.*)\{.*\}/.test(content)) {
        issues.push(issue(SEV.WARNING, 3, `subprocess with shell=True + f-string interpolation (injection risk)`, rel));
      }
    }
  }

  return issues;
}

// ── Category 4: skills/ prompt injection patterns ─────────────────────────────

const INJECTION_PATTERNS = [
  { pattern: /ignore\s+previous\s+instructions/i,    label: 'ignore previous instructions' },
  { pattern: /forget\s+(all|your|everything)/i,       label: 'forget all/everything' },
  { pattern: /new\s+instructions\s*:/i,               label: 'new instructions:' },
  { pattern: /system\s+prompt\s+override/i,           label: 'system prompt override' },
  { pattern: /you\s+are\s+now\s+(?!an?\s+expert)/i,  label: 'you are now [role change]' },
  { pattern: /\[INST\]|\[\/INST\]/,                   label: 'Llama instruction tags' },
  { pattern: /<\|im_start\|>|<\|im_end\|>/,           label: 'ChatML tags' },
];

function scanSkills() {
  const issues = [];
  const skillsDir = path.join(CLAUDE_DIR, 'skills');
  const files = walkDir(skillsDir, ['.md']);

  for (const file of files) {
    const content = readFileSafe(file);
    const rel = path.relative(ROOT, file);

    for (const { pattern, label } of INJECTION_PATTERNS) {
      if (pattern.test(content)) {
        issues.push(issue(SEV.CRITICAL, 4, `Potential prompt injection: "${label}"`, rel));
        break;  // one critical per file max
      }
    }
  }

  return issues;
}

// ── Category 5: instincts confidence anomalies ───────────────────────────────

const SUSPICIOUS_CONFIDENCE = 0.9;

function scanInstincts() {
  const issues = [];
  const instinctsDir = path.join(CLAUDE_DIR, 'instincts');
  const files = walkDir(instinctsDir, ['.yaml', '.yml']);

  for (const file of files) {
    if (file.includes('.gitkeep')) continue;
    const content = readFileSafe(file);
    const rel = path.relative(ROOT, file);

    // Parse confidence value
    const match = content.match(/^confidence:\s*([\d.]+)/m);
    if (match) {
      const conf = parseFloat(match[1]);
      if (conf > SUSPICIOUS_CONFIDENCE) {
        issues.push(issue(SEV.WARNING, 5, `Instinct confidence unusually high (${conf}) — verify legitimacy`, rel));
      }
    }

    // Check for injection patterns in instinct action/trigger fields
    for (const { pattern, label } of INJECTION_PATTERNS) {
      if (pattern.test(content)) {
        issues.push(issue(SEV.CRITICAL, 5, `Instinct contains injection pattern: "${label}"`, rel));
      }
    }
  }

  return issues;
}

// ── Scoring ───────────────────────────────────────────────────────────────────

function computeGrade(issues) {
  const warnings  = issues.filter(i => i.severity === SEV.WARNING).length;
  const criticals = issues.filter(i => i.severity === SEV.CRITICAL).length;

  if (criticals >= 3)        return 'F';
  if (criticals >= 2)        return 'D';
  if (criticals >= 1 || warnings >= 5) return 'C';
  if (warnings >= 3)         return 'C';
  if (warnings >= 1)         return 'B';
  return 'A';
}

function gradeColor(grade) {
  return { A: c.green, B: c.green, C: c.yellow, D: c.yellow, F: c.red }[grade] || c.reset;
}

// ── Report formatter ──────────────────────────────────────────────────────────

function formatReport(allIssues, elapsed) {
  const grade = computeGrade(allIssues);
  const gc    = gradeColor(grade);
  const warnings  = allIssues.filter(i => i.severity === SEV.WARNING);
  const criticals = allIssues.filter(i => i.severity === SEV.CRITICAL);
  const lines = [];

  lines.push('');
  lines.push(`${c.bold}${c.cyan}══════════════════════════════════════════════${c.reset}`);
  lines.push(`${c.bold}${c.cyan}  Agent007 Security Scan${c.reset}${c.gray}  (local-only, ${elapsed}ms)${c.reset}`);
  lines.push(`${c.bold}${c.cyan}══════════════════════════════════════════════${c.reset}`);
  lines.push('');
  lines.push(`  Score: ${gc}${c.bold}${grade}${c.reset}  |  ${c.red}${criticals.length} critical${c.reset}  ${c.yellow}${warnings.length} warnings${c.reset}  ✅ ${5 - new Set(allIssues.map(i=>i.category)).size} clean categories`);
  lines.push('');

  const CATEGORIES = [
    [1, 'CLAUDE.md — safety bypass phrases'],
    [2, 'settings.json — permissions.deny coverage'],
    [3, 'hooks/ — unsafe eval/exec/curl patterns'],
    [4, 'skills/ — prompt injection patterns'],
    [5, 'instincts/ — confidence anomalies'],
  ];

  for (const [cat, label] of CATEGORIES) {
    const catIssues = allIssues.filter(i => i.category === cat);
    const icon = catIssues.length === 0 ? `${c.green}✅${c.reset}` :
      catIssues.some(i => i.severity === SEV.CRITICAL) ? `${c.red}🚨${c.reset}` : `${c.yellow}⚠️ ${c.reset}`;
    lines.push(`  ${icon} [${cat}] ${label}`);
    for (const iss of catIssues) {
      const sevColor = iss.severity === SEV.CRITICAL ? c.red : c.yellow;
      const sevLabel = iss.severity.toUpperCase().padEnd(8);
      lines.push(`       ${sevColor}${sevLabel}${c.reset} ${iss.message}`);
      if (iss.file) lines.push(`       ${c.gray}→ ${iss.file}${c.reset}`);
    }
  }

  lines.push('');

  if (grade === 'A') {
    lines.push(`  ${c.green}${c.bold}All checks passed. Ecosystem looks clean.${c.reset}`);
  } else {
    lines.push(`  ${c.bold}Recommendations:${c.reset}`);
    if (criticals.length > 0) {
      lines.push(`  ${c.red}• Fix all CRITICAL issues before running in production${c.reset}`);
    }
    if (warnings.length > 0) {
      lines.push(`  ${c.yellow}• Review WARNING items and confirm they are intentional${c.reset}`);
    }
  }

  lines.push('');
  lines.push(`${c.bold}${gc}══════════════════════════════════════════════${c.reset}`);
  lines.push('');

  return lines.join('\n');
}

// ── Main ──────────────────────────────────────────────────────────────────────

function runScan(categoryFilter = null) {
  const scanners = [
    [1, scanClaudeMd],
    [2, scanSettingsJson],
    [3, scanHooks],
    [4, scanSkills],
    [5, scanInstincts],
  ];

  const allIssues = [];
  for (const [cat, fn] of scanners) {
    if (categoryFilter && cat !== categoryFilter) continue;
    try {
      allIssues.push(...fn());
    } catch { /* never fail on scan error */ }
  }

  return allIssues;
}

if (require.main === module) {
  const args = process.argv.slice(2);
  const jsonMode = args.includes('--json');
  const catArg   = args.includes('--category') ? parseInt(args[args.indexOf('--category') + 1]) : null;

  const start = Date.now();
  const issues = runScan(catArg);
  const elapsed = Date.now() - start;

  if (jsonMode) {
    const grade = computeGrade(issues);
    console.log(JSON.stringify({ grade, issues, elapsed }, null, 2));
    process.exit(grade === 'A' || grade === 'B' ? 0 : 1);
  } else {
    process.stdout.write(formatReport(issues, elapsed));
    const grade = computeGrade(issues);
    process.exit(grade === 'A' || grade === 'B' ? 0 : 1);
  }
}

module.exports = { runScan, computeGrade };
