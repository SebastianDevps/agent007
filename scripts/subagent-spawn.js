#!/usr/bin/env node
/**
 * subagent-spawn.js — Minimal prompt builder for subagent dispatch
 *
 * Builds a focused, token-efficient prompt for a single task subagent.
 * Implements the Fork Window pattern (LastNTurns: 3 equivalent):
 * each subagent gets only what it needs — no context rot from the orchestrator.
 *
 * Usage:
 *   node subagent-spawn.js --task <tasks.md> --task-id TASK-001
 *   node subagent-spawn.js --task <tasks.md> --task-id TASK-001 --context <extra-file>
 *   node subagent-spawn.js --task <tasks.md> --task-id TASK-001 --dry-run  (show token estimate)
 *
 * Output: prompt text to stdout, ready to pass to Agent tool
 *
 * Context budget per subagent: 16k tokens max
 *   - Task block:         ~500 tokens
 *   - Active plan:        ~800 tokens  (40 lines)
 *   - Tech stack:         ~400 tokens  (40 lines)
 *   - Conventions:        ~400 tokens  (40 lines)
 *   - Banned phrases:     ~300 tokens  (40 lines)
 *   - Extra context:      ~600 tokens  (40 lines each, up to 3 files)
 *   - Identity + rules:   ~500 tokens
 *   Total:              ~3,500 tokens  (well under 16k)
 */

'use strict';

const fs = require('fs');
const path = require('path');

const PROJECT_ROOT = findProjectRoot();
const CLAUDE_DIR = path.join(PROJECT_ROOT, '.claude');
const SDLC_DIR = path.join(PROJECT_ROOT, '.sdlc');

const MAX_SNIPPET_LINES = 40;
const MAX_EXTRA_CONTEXT_FILES = 3;

// ── Project root detection ────────────────────────────────────────────────────

function findProjectRoot() {
  let current = process.cwd();
  while (current !== path.dirname(current)) {
    if (fs.existsSync(path.join(current, '.claude'))) return current;
    current = path.dirname(current);
  }
  return process.cwd();
}

// ── File readers ──────────────────────────────────────────────────────────────

function readSnippet(filePath, maxLines = MAX_SNIPPET_LINES) {
  if (!fs.existsSync(filePath)) return null;
  try {
    const lines = fs.readFileSync(filePath, 'utf8').split('\n');
    const snippet = lines.slice(0, maxLines).join('\n');
    const truncated = lines.length > maxLines;
    return { content: snippet, truncated, totalLines: lines.length };
  } catch {
    return null;
  }
}

function readFull(filePath) {
  if (!fs.existsSync(filePath)) return null;
  try {
    return fs.readFileSync(filePath, 'utf8');
  } catch {
    return null;
  }
}

// ── Task parser ───────────────────────────────────────────────────────────────

function extractTaskBlock(tasksContent, taskId) {
  // Match ## TASK-NNN header and capture until next ## TASK- or end of file
  const regex = new RegExp(
    `## ${taskId}\\s*\\n([\\s\\S]*?)(?=\\n## TASK-|$)`,
    'm'
  );
  const match = tasksContent.match(regex);
  if (!match) return null;

  return `## ${taskId}\n${match[1].trimEnd()}`;
}

function extractTaskDomain(taskBlock) {
  const match = taskBlock.match(/^domain:\s*(.+)$/m);
  return match ? match[1].trim() : 'mixed';
}

function extractTaskTitle(taskBlock) {
  const match = taskBlock.match(/^title:\s*(.+)$/m);
  return match ? match[1].trim() : 'Unknown task';
}

function extractVerifyCmd(taskBlock) {
  const match = taskBlock.match(/^verify_cmd:\s*(.+)$/m);
  return match ? match[1].trim() : 'npm test';
}

// ── Domain → agent identity ───────────────────────────────────────────────────

const DOMAIN_IDENTITY = {
  backend: 'You are a senior backend engineer specializing in NestJS, TypeORM, and PostgreSQL. You write production-ready APIs with proper validation, error handling, and test coverage.',
  frontend: 'You are a senior frontend engineer specializing in Next.js 14, React 18, Tailwind CSS, and GSAP. You build accessible, performant, visually excellent UIs.',
  platform: 'You are a senior DevOps and platform engineer specializing in CI/CD, Docker, Jest, and infrastructure. You ensure reliability, test coverage, and deployment quality.',
  security: 'You are a senior security engineer specializing in OWASP Top 10, JWT, and threat modeling. You identify and fix vulnerabilities before they reach production.',
  mixed: 'You are a senior full-stack engineer. You write clean, tested, production-ready code across the full stack.',
};

function getAgentIdentity(domain) {
  return DOMAIN_IDENTITY[domain] || DOMAIN_IDENTITY.mixed;
}

// ── Prompt builder ────────────────────────────────────────────────────────────

function buildPrompt({ taskBlock, taskId, domain, verifyCmd, contextFiles }) {
  const identity = getAgentIdentity(domain);
  const sections = [];

  // 1. Identity
  sections.push(identity);
  sections.push('');

  // 2. Core rules (condensed from banned-phrases + core_rules)
  sections.push('<core_rules>');
  sections.push('- Only claim "done" when verify command passes with real output evidence.');
  sections.push('- NEVER use placeholders like "// rest of the code remains the same...". Always show complete file contents.');
  sections.push('- Read a file before editing it. Verify paths exist before assuming.');
  sections.push('- Write production code only after having a failing test (SDD Iron Law).');
  sections.push('- Think holistically: consider ALL relevant files before making changes.');
  sections.push('- The code you write will be reviewed by humans — optimize for clarity and readability.');
  sections.push('- When debugging: address the root cause, not the symptoms.');
  sections.push('</core_rules>');
  sections.push('');

  // 3. Active plan (global context — why this task exists)
  const activePlan = readSnippet(
    path.join(SDLC_DIR, 'tasks', 'active-plan.md')
  );
  if (activePlan) {
    sections.push('<global_plan>');
    sections.push(activePlan.content);
    if (activePlan.truncated) {
      sections.push(`... [truncated at ${MAX_SNIPPET_LINES} lines — see .sdlc/tasks/active-plan.md for full plan]`);
    }
    sections.push('</global_plan>');
    sections.push('');
  }

  // 4. Tech stack (language, framework, db)
  const techStack = readSnippet(
    path.join(SDLC_DIR, 'context', 'tech-stack.md')
  );
  if (techStack) {
    sections.push('<tech_stack>');
    sections.push(techStack.content);
    sections.push('</tech_stack>');
    sections.push('');
  }

  // 5. Conventions
  const conventions = readSnippet(
    path.join(SDLC_DIR, 'context', 'conventions.md')
  );
  if (conventions) {
    sections.push('<conventions>');
    sections.push(conventions.content);
    sections.push('</conventions>');
    sections.push('');
  }

  // 6. Extra context files (--context flags)
  for (const ctxFile of contextFiles.slice(0, MAX_EXTRA_CONTEXT_FILES)) {
    const snippet = readSnippet(ctxFile);
    if (snippet) {
      const label = path.basename(ctxFile);
      sections.push(`<context file="${label}">`);
      sections.push(snippet.content);
      if (snippet.truncated) {
        sections.push(`... [truncated — see ${ctxFile} for full content]`);
      }
      sections.push('</context>');
      sections.push('');
    }
  }

  // 7. The task itself (full block — this is the core instruction)
  sections.push('<task>');
  sections.push(taskBlock);
  sections.push('</task>');
  sections.push('');

  // 8. Execution instructions
  sections.push('<execution>');
  sections.push('Execute the task above following TDD: RED (failing test) → GREEN (minimal code) → REFACTOR.');
  sections.push('');
  sections.push(`Verification command: ${verifyCmd}`);
  sections.push('Run it and show the actual output — never claim done without evidence.');
  sections.push('');
  sections.push('When ALL acceptance criteria are met and verification passes, output:');
  sections.push('<promise>COMPLETE</promise>');
  sections.push('');
  sections.push('If you cannot complete after 3 attempts, output:');
  sections.push('<promise>FAIL</promise>');
  sections.push('with the last error output and your diagnosis.');
  sections.push('</execution>');

  return sections.join('\n');
}

// ── Token estimator (rough: 1 token ≈ 4 chars) ────────────────────────────────

function estimateTokens(text) {
  return Math.ceil(text.length / 4);
}

// ── Main ──────────────────────────────────────────────────────────────────────

function main() {
  const args = process.argv.slice(2);

  const taskFileIdx = args.indexOf('--task');
  const taskIdIdx = args.indexOf('--task-id');
  const dryRun = args.includes('--dry-run');

  // Collect --context flags (can be repeated)
  const contextFiles = [];
  for (let i = 0; i < args.length; i++) {
    if (args[i] === '--context' && args[i + 1]) {
      const p = args[i + 1];
      contextFiles.push(path.isAbsolute(p) ? p : path.join(process.cwd(), p));
    }
  }

  if (taskFileIdx === -1 || !args[taskFileIdx + 1]) {
    process.stderr.write('Usage: node subagent-spawn.js --task <tasks.md> --task-id TASK-NNN\n');
    process.exit(1);
  }
  if (taskIdIdx === -1 || !args[taskIdIdx + 1]) {
    process.stderr.write('Error: --task-id is required\n');
    process.exit(1);
  }

  const taskFilePath = path.isAbsolute(args[taskFileIdx + 1])
    ? args[taskFileIdx + 1]
    : path.join(process.cwd(), args[taskFileIdx + 1]);
  const taskId = args[taskIdIdx + 1].toUpperCase();

  if (!fs.existsSync(taskFilePath)) {
    process.stderr.write(`Error: tasks file not found: ${taskFilePath}\n`);
    process.exit(1);
  }

  const tasksContent = readFull(taskFilePath);
  if (!tasksContent) {
    process.stderr.write('Error: could not read tasks file\n');
    process.exit(1);
  }

  const taskBlock = extractTaskBlock(tasksContent, taskId);
  if (!taskBlock) {
    process.stderr.write(`Error: task ${taskId} not found in ${taskFilePath}\n`);
    process.exit(1);
  }

  const domain = extractTaskDomain(taskBlock);
  const verifyCmd = extractVerifyCmd(taskBlock);

  const prompt = buildPrompt({
    taskBlock,
    taskId,
    domain,
    verifyCmd,
    contextFiles,
  });

  if (dryRun) {
    const tokens = estimateTokens(prompt);
    process.stdout.write(`Dry run — ${taskId} (${domain})\n`);
    process.stdout.write(`Estimated tokens: ~${tokens}\n`);
    process.stdout.write(`Context files included: ${contextFiles.length}\n`);
    process.stdout.write(`Active plan: ${fs.existsSync(path.join(SDLC_DIR, 'tasks', 'active-plan.md')) ? '✓' : '✗ (missing)'}\n`);
    process.stdout.write(`Tech stack: ${fs.existsSync(path.join(SDLC_DIR, 'context', 'tech-stack.md')) ? '✓' : '✗ (missing)'}\n`);
  } else {
    process.stdout.write(prompt + '\n');
  }

  process.exit(0);
}

main();
