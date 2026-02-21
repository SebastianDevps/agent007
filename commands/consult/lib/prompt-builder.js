/**
 * Prompt Builder with Caching Support
 *
 * Builds structured prompts optimized for Anthropic's Prompt Caching.
 * Separates static (cacheable) from dynamic (non-cacheable) content.
 */

/**
 * Build enhanced prompt with cache optimization
 *
 * @param {string} agentName - Agent name
 * @param {string} userQuestion - User's question
 * @param {Object} projectContext - Project context
 * @param {Array} skills - Loaded skills
 * @param {Object} options - Build options
 * @returns {Object} Structured prompt with cache markers
 */
function buildEnhancedPromptWithCache(agentName, userQuestion, projectContext, skills, options = {}) {
  const {
    mode = 'normal',
    executionMode = 'build'
  } = options;

  const sections = [];

  // SECTION 1: Agent Role & Core Methodology (CACHEABLE)
  // This is static per agent - perfect for caching
  sections.push({
    type: 'expert_methodology',
    cacheable: true,
    text: buildAgentMethodology(agentName, executionMode)
  });

  // SECTION 2: Skill Summaries (CACHEABLE if query-independent)
  // Skills are static - cache them
  if (skills.length > 0) {
    sections.push({
      type: 'skill_summaries',
      cacheable: true,
      text: buildSkillsSection(skills)
    });
  }

  // SECTION 3: Project Context (NOT CACHEABLE)
  // Changes per project, so don't cache
  if (projectContext) {
    sections.push({
      type: 'project_context',
      cacheable: false,
      text: buildProjectContextSection(projectContext)
    });
  }

  // SECTION 4: User Question (NOT CACHEABLE)
  // Always unique per query
  sections.push({
    type: 'user_question',
    cacheable: false,
    text: buildQuestionSection(userQuestion, executionMode)
  });

  return {
    sections,
    cacheableTokenEstimate: estimateCacheableTokens(sections),
    totalTokenEstimate: estimateTotalTokens(sections)
  };
}

/**
 * Build agent methodology section
 */
function buildAgentMethodology(agentName, executionMode) {
  const lines = [];

  lines.push(`You are ${agentName}, a senior expert.`);
  lines.push('');

  // Core principles (static, cacheable)
  lines.push('## Your Expertise');
  lines.push('');
  lines.push('You specialize in providing expert guidance based on established patterns and best practices.');
  lines.push('');

  // Execution mode instructions
  if (executionMode === 'plan') {
    lines.push('**EXECUTION MODE: PLAN (Read-Only Analysis)**');
    lines.push('');
    lines.push('- Analyze the request without implementing changes');
    lines.push('- Identify what needs to be done and any risks');
    lines.push('- Provide clear implementation steps');
    lines.push('- You can read files but NOT edit them');
    lines.push('');
  } else {
    lines.push('**EXECUTION MODE: BUILD (Full Implementation)**');
    lines.push('');
    lines.push('- Implement the requested changes');
    lines.push('- Follow best practices and patterns');
    lines.push('- Test your implementation');
    lines.push('- Report completion status');
    lines.push('');
  }

  return lines.join('\n');
}

/**
 * Build skills reference section
 */
function buildSkillsSection(skills) {
  const lines = [];

  lines.push('## Reference Guidelines (Domain Patterns)');
  lines.push('');
  lines.push('You have access to these established patterns:');
  lines.push('');

  skills.forEach(skill => {
    lines.push(`### ${skill.name}`);
    lines.push('');
    lines.push(skill.content.trim());
    lines.push('');
    lines.push('---');
    lines.push('');
  });

  lines.push('**Apply these patterns** when relevant to your response.');
  lines.push('');

  return lines.join('\n');
}

/**
 * Build project context section
 */
function buildProjectContextSection(projectContext) {
  const lines = [];

  lines.push('## Current Project Context');
  lines.push('');
  lines.push(`Framework: ${projectContext.framework || 'Unknown'}`);
  lines.push(`Language: ${projectContext.language || 'Unknown'}`);

  if (projectContext.database && projectContext.database.length > 0) {
    lines.push(`Database: ${projectContext.database.join(', ')}`);
  }

  if (projectContext.orm && projectContext.orm !== 'none') {
    lines.push(`ORM: ${projectContext.orm}`);
  }

  if (projectContext.modules && projectContext.modules.length > 0) {
    lines.push(`Modules: ${projectContext.modules.slice(0, 5).join(', ')}`);
  }

  lines.push('');

  return lines.join('\n');
}

/**
 * Build question section
 */
function buildQuestionSection(userQuestion, executionMode) {
  const lines = [];

  lines.push('## Question');
  lines.push('');
  lines.push(userQuestion);
  lines.push('');

  lines.push('## Instructions');
  lines.push('');

  if (executionMode === 'plan') {
    lines.push('Provide a concise analysis (max 30 lines):');
    lines.push('- What needs to be done');
    lines.push('- What files/areas are affected');
    lines.push('- Any risks or dependencies');
    lines.push('- Step-by-step implementation plan');
  } else {
    lines.push('Provide a complete response (max 100 lines):');
    lines.push('- Specific to the project context');
    lines.push('- Following reference guidelines');
    lines.push('- Include concrete implementation steps');
    lines.push('- Consider trade-offs');
  }

  lines.push('');

  return lines.join('\n');
}

/**
 * Estimate cacheable tokens
 */
function estimateCacheableTokens(sections) {
  const cacheableSections = sections.filter(s => s.cacheable);
  const totalChars = cacheableSections.reduce((sum, s) => sum + s.text.length, 0);

  // Rough estimate: 1 token ≈ 4 characters
  return Math.round(totalChars / 4);
}

/**
 * Estimate total tokens
 */
function estimateTotalTokens(sections) {
  const totalChars = sections.reduce((sum, s) => sum + s.text.length, 0);
  return Math.round(totalChars / 4);
}

/**
 * Convert structured sections to Anthropic format
 */
function sectionsToAnthropicFormat(sections) {
  return sections.map(section => {
    const message = {
      type: 'text',
      text: section.text
    };

    if (section.cacheable) {
      message.cache_control = { type: 'ephemeral' };
    }

    return message;
  });
}

module.exports = {
  buildEnhancedPromptWithCache,
  sectionsToAnthropicFormat,
  buildAgentMethodology,
  buildSkillsSection,
  buildProjectContextSection,
  buildQuestionSection
};
