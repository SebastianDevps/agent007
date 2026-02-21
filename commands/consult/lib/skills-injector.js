/**
 * Skills Injector v2.0 - With Lazy Loading
 *
 * Loads ONLY relevant domain skills based on query keywords
 * to minimize context window consumption (67% token reduction)
 *
 * Previous version: Loaded all skills for agent (~40K tokens)
 * New version: Loads 0-3 relevant skills (~5-15K tokens)
 */

const fs = require('fs');
const path = require('path');
const { selectRelevantSkills } = require('./skill-selector');

/**
 * Agent to skills mapping
 */
const AGENT_SKILLS_MAP = {
  'backend-expert': [
    'api-design-principles',
    'architecture-patterns',
    'resilience-patterns'
  ],
  'frontend-expert': [
    'react-best-practices',
    'frontend-design'
  ],
  'database-expert': [
    'architecture-patterns'
  ],
  'security-expert': [
    'nestjs-code-reviewer' // Has security checklist
  ],
  'testing-expert': [
    'workflow/tdd',
    'quality-gates/systematic-debugging'
  ],
  'devops-expert': [],
  'product-expert': [
    'product/product-discovery',
    'product/feature-prioritization'
  ],
  'ux-expert': [
    'product/ux-research',
    'product/design-system'
  ],
  'data-expert': [
    'data/analytics-setup',
    'data/data-pipeline-design'
  ],
  'devrel-expert': [
    'devrel/api-documentation',
    'devrel/developer-portal'
  ]
};

/**
 * Load skill content - SUMMARY.md (normal) or SKILL.md (deep mode)
 *
 * @param {string} skillPath - Skill path (e.g., 'architecture-patterns')
 * @param {string} basePath - Project root path
 * @param {boolean} useFull - Load full SKILL.md instead of SUMMARY.md (deep mode)
 * @returns {Object|null} Skill content or null if not found
 */
function loadSkillContent(skillPath, basePath, useFull = false) {
  try {
    const skillDir = path.join(basePath, '.claude', 'skills', skillPath);

    // Try SUMMARY.md first (unless deep mode)
    const summaryPath = path.join(skillDir, 'SUMMARY.md');
    const fullPath = path.join(skillDir, 'SKILL.md');

    let contentPath;
    if (!useFull && fs.existsSync(summaryPath)) {
      contentPath = summaryPath;  // Use summary for normal mode
    } else if (fs.existsSync(fullPath)) {
      contentPath = fullPath;     // Fallback to full skill
    } else {
      return null;
    }

    const content = fs.readFileSync(contentPath, 'utf-8');

    // Remove frontmatter if present
    const withoutFrontmatter = content.replace(/^---\n[\s\S]*?\n---\n/, '');

    return {
      name: skillPath,
      content: withoutFrontmatter.trim(),
      fullPath: contentPath,
      isSummary: contentPath.endsWith('SUMMARY.md')
    };
  } catch (error) {
    return null;
  }
}

/**
 * Load only relevant skills for an agent based on query
 *
 * @param {string} agentName - Name of the agent
 * @param {string} query - User's question (for lazy loading)
 * @param {string} projectPath - Project root path
 * @param {Object} options - Loading options
 * @param {boolean} options.lazyLoad - Enable lazy loading (default: true)
 * @param {boolean} options.forceAll - Force load all skills (--deep mode)
 * @param {boolean} options.useFull - Use full SKILL.md instead of SUMMARY.md
 * @returns {Array} Array of loaded skills
 */
function loadSkillsForAgent(agentName, query = '', projectPath = process.cwd(), options = {}) {
  const {
    lazyLoad = true,
    forceAll = false,
    useFull = false  // Deep mode loads full SKILL.md
  } = options;

  const availableSkills = AGENT_SKILLS_MAP[agentName] || [];

  // Determine which skills to load
  const skillsToLoad = lazyLoad && !forceAll
    ? selectRelevantSkills(query, availableSkills, { forceAll })
    : availableSkills;

  // Load selected skills (SUMMARY.md or SKILL.md)
  const skills = [];
  for (const skillPath of skillsToLoad) {
    const skill = loadSkillContent(skillPath, projectPath, useFull);
    if (skill) {
      skills.push(skill);
    }
  }

  return skills;
}

/**
 * Build enhanced prompt with skills injection
 */
function buildEnhancedPrompt(agentName, userQuestion, projectContext, skills) {
  const lines = [];

  // Agent role
  lines.push(`You are ${agentName}, a senior expert.`);
  lines.push('');

  // Project context
  if (projectContext) {
    lines.push('## Current Project Context');
    lines.push('');
    lines.push(`Framework: ${projectContext.framework}`);
    lines.push(`Language: ${projectContext.language}`);

    if (projectContext.database.length > 0 && projectContext.database[0] !== 'unknown') {
      lines.push(`Database: ${projectContext.database.join(', ')}`);
    }

    if (projectContext.orm !== 'none') {
      lines.push(`ORM: ${projectContext.orm}`);
    }

    if (projectContext.modules.length > 0) {
      lines.push(`Existing modules: ${projectContext.modules.slice(0, 5).join(', ')}`);
    }

    lines.push('');
  }

  // Skills reference
  if (skills.length > 0) {
    lines.push('## Reference Guidelines (From Domain Skills)');
    lines.push('');
    lines.push('You have access to the following established patterns and guidelines:');
    lines.push('');

    skills.forEach(skill => {
      lines.push(`### ${skill.name}`);
      lines.push('');
      lines.push(skill.content.trim());
      lines.push('');
      lines.push('---');
      lines.push('');
    });

    lines.push('**Use these guidelines** when applicable to your recommendation.');
    lines.push('');
  }

  // User question
  lines.push('## Question');
  lines.push('');
  lines.push(userQuestion);
  lines.push('');

  // Instructions
  lines.push('## Instructions');
  lines.push('');
  lines.push('Provide a response that:');
  lines.push('- Is specific to the project context above');
  lines.push('- Follows the reference guidelines when applicable');
  lines.push('- Includes concrete implementation steps');
  lines.push('- Considers trade-offs and alternatives');
  lines.push('- Is concise (max 50-100 lines depending on complexity)');
  lines.push('');

  return lines.join('\n');
}

/**
 * Inject skills into multiple agent prompts
 *
 * @param {string[]} agents - Agent names
 * @param {string} userQuestion - User's question
 * @param {Object} projectContext - Project context
 * @param {string} projectPath - Project root
 * @param {Object} options - Injection options
 * @param {string} options.mode - 'quick', 'normal', or 'deep'
 * @returns {Object} Enhanced prompts for each agent
 */
function injectSkillsForAgents(agents, userQuestion, projectContext, projectPath = process.cwd(), options = {}) {
  const { mode = 'normal' } = options;
  const enhancedPrompts = {};

  // Mode configuration
  const forceAll = mode === 'deep';   // Deep: load all skills
  const useFull = mode === 'deep';    // Deep: use full SKILL.md

  for (const agentName of agents) {
    const skills = loadSkillsForAgent(
      agentName,
      userQuestion,  // Pass query for lazy loading
      projectPath,
      { forceAll, useFull }
    );

    const prompt = buildEnhancedPrompt(agentName, userQuestion, projectContext, skills);

    enhancedPrompts[agentName] = {
      prompt,
      skillsLoaded: skills.map(s => s.name),
      hasContext: !!projectContext,
      lazyLoaded: !forceAll,
      usingSummaries: !useFull && skills.some(s => s.isSummary)
    };
  }

  return enhancedPrompts;
}

/**
 * Get skills summary for agent
 */
function getSkillsSummary(agentName) {
  const skillPaths = AGENT_SKILLS_MAP[agentName] || [];

  if (skillPaths.length === 0) {
    return 'No specific domain skills referenced.';
  }

  return `References: ${skillPaths.join(', ')}`;
}

module.exports = {
  loadSkillsForAgent,
  buildEnhancedPrompt,
  injectSkillsForAgents,
  getSkillsSummary,
  AGENT_SKILLS_MAP
};
