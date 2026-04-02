#!/usr/bin/env node
/**
 * agent007-init.js — Session Banner Generator
 *
 * Produces a single-line status banner for welcome.py:
 *   Agent007 v5 | 12 skills | 8 agents | branch: main | RTK: ✓ | Task: none
 *
 * Usage:
 *   node agent007-init.js --oneline   → single line to stdout
 *   node agent007-init.js             → JSON object to stdout
 *
 * Must complete in < 50ms (synchronous fs only, no async).
 */

const fs = require("fs");
const path = require("path");
const { execSync } = require("child_process");

const PROJECT_ROOT = findProjectRoot();
const CLAUDE_DIR = path.join(PROJECT_ROOT, ".claude");

function findProjectRoot() {
  let current = process.cwd();
  while (current !== path.dirname(current)) {
    if (fs.existsSync(path.join(current, ".claude"))) return current;
    current = path.dirname(current);
  }
  return process.cwd();
}

function countSkills() {
  const skillsDir = path.join(CLAUDE_DIR, "skills");
  if (!fs.existsSync(skillsDir)) return 0;
  try {
    const result = execSync(
      `find "${skillsDir}" -name "*.md" -not -path "*/_archive/*" 2>/dev/null | wc -l`,
      { encoding: "utf8", timeout: 500 }
    );
    return parseInt(result.trim(), 10) || 0;
  } catch {
    return 0;
  }
}

function countAgents() {
  const agentsDir = path.join(CLAUDE_DIR, "agents");
  if (!fs.existsSync(agentsDir)) return 0;
  try {
    const files = fs.readdirSync(agentsDir).filter((f) => f.endsWith(".md"));
    return files.length;
  } catch {
    return 0;
  }
}

function getCurrentBranch() {
  try {
    const branch = execSync("git rev-parse --abbrev-ref HEAD 2>/dev/null", {
      encoding: "utf8",
      timeout: 500,
      cwd: PROJECT_ROOT,
    });
    return branch.trim() || "HEAD";
  } catch {
    return "HEAD";
  }
}

function isRtkActive() {
  return fs.existsSync(path.join(CLAUDE_DIR, "hooks", "rtk-rewrite.py"));
}

function getActiveTask() {
  const sessionFile = path.join(PROJECT_ROOT, ".sdlc", "state", "session.md");
  if (!fs.existsSync(sessionFile)) return "none";
  try {
    const content = fs.readFileSync(sessionFile, "utf8");
    const match = content.match(/##\s*Tarea Activa\s*\n([^\n#]+)/);
    if (!match) return "none";
    const task = match[1].trim();
    return task === "ninguna" || task === "" ? "none" : task.slice(0, 40);
  } catch {
    return "none";
  }
}

function main() {
  const skills = countSkills();
  const agents = countAgents();
  const branch = getCurrentBranch();
  const rtk = isRtkActive() ? "✓" : "✗";
  const task = getActiveTask();

  const banner = `Agent007 v5 | ${skills} skills | ${agents} agents | branch: ${branch} | RTK: ${rtk} | Task: ${task}`;

  const args = process.argv.slice(2);
  if (args.includes("--oneline")) {
    process.stdout.write(banner + "\n");
  } else {
    process.stdout.write(
      JSON.stringify({ banner, skills, agents, branch, rtk, task }) + "\n"
    );
  }
  process.exit(0);
}

main();
