const path = require('path');
const fs = require('fs');

const AGENTS_DIR = path.join(__dirname, '../../../../agents');
const SKILLS_BASE = path.join(__dirname, '../../../');

const ACTIVE_AGENTS = [
  'backend-db-expert.md',
  'frontend-ux-expert.md',
  'platform-expert.md',
  'product-expert.md',
  'security-expert.md'
];

const ARCHIVED_AGENTS = [
  'backend-expert.md',
  'database-expert.md',
  'frontend-expert.md',
  'devops-expert.md',
  'testing-expert.md',
  'ux-expert.md',
  'data-expert.md',
  'devrel-expert.md'
];

const ACTIVE_SKILLS = [
  '_core/verification-enforcement/SKILL.md',
  '_core/anti-rationalization/SKILL.md',
  '_core/context-awareness/SKILL.md',
  '_core/decision-memory/SKILL.md',
  '_orchestration/session-orchestrator/SKILL.md',
  'workflow/brainstorming/SKILL.md',
  'workflow/writing-plans/SKILL.md',
  'workflow/tdd/SKILL.md',
  'quality-gates/systematic-debugging/SKILL.md',
  'api-design-principles/SKILL.md',
  'architecture-patterns/SKILL.md',
  'resilience-patterns/SKILL.md',
  'nestjs-code-reviewer/SKILL.md',
  'frontend-design/SKILL.md',
  'react-best-practices/SKILL.md',
  'product/product-discovery/SKILL.md',
  'devrel/api-documentation/SKILL.md'
];

const ARCHIVED_SKILL_NAMES = [
  'feature-prioritization',
  'ux-research',
  'design-system',
  'analytics-setup',
  'data-pipeline-design',
  'developer-portal'
];

describe('Agent File Integrity', () => {
  test('all 5 active agents have .md files', () => {
    for (const agent of ACTIVE_AGENTS) {
      const agentPath = path.join(AGENTS_DIR, agent);
      expect(fs.existsSync(agentPath)).toBe(true);
    }
  });

  test('archived agents are in _archive directory', () => {
    for (const agent of ARCHIVED_AGENTS) {
      const activePath = path.join(AGENTS_DIR, agent);
      expect(fs.existsSync(activePath)).toBe(false);
    }
  });

  test('agents directory contains exactly 5 active agents', () => {
    const files = fs.readdirSync(AGENTS_DIR)
      .filter(f => f.endsWith('.md') && f !== 'README.md' && !f.startsWith('_'));
    expect(files).toHaveLength(5);
  });
});

describe('Skill File Integrity', () => {
  test('all 16 active skills have SKILL.md files', () => {
    for (const skillPath of ACTIVE_SKILLS) {
      const fullPath = path.join(SKILLS_BASE, skillPath);
      expect(fs.existsSync(fullPath)).toBe(true);
    }
  });

  test('skills/data directory does not exist (was empty, removed in Phase 1)', () => {
    const dataDir = path.join(SKILLS_BASE, 'data');
    expect(fs.existsSync(dataDir)).toBe(false);
  });
});

describe('Router Has No Broken References', () => {
  const ROUTER_PATH = path.join(__dirname, '../lib/router.js');
  let routerSource;

  beforeAll(() => {
    routerSource = fs.readFileSync(ROUTER_PATH, 'utf-8');
  });

  test('router.js does not reference any archived skill names', () => {
    for (const archivedSkill of ARCHIVED_SKILL_NAMES) {
      expect(routerSource).not.toContain(archivedSkill);
    }
  });
});
