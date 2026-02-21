/**
 * Agent Context Contracts
 *
 * Defines structured input/output contracts for agents
 * to minimize context redundancy and improve clarity.
 *
 * Savings: ~15K tokens by removing duplicate/irrelevant context
 */

/**
 * Build minimal agent context (contract-based)
 *
 * @param {Object} params - Context parameters
 * @returns {Object} Minimal agent context
 */
function buildMinimalContext(params) {
  const {
    agentName,
    userQuestion,
    projectContext,
    skills = [],
    mode = 'normal'
  } = params;

  // Extract only core principles (not full methodology)
  const corePrinciples = extractCorePrinciples(agentName);

  // Filter project context to only relevant fields
  const minimalProjectContext = filterProjectContext(projectContext, userQuestion);

  // Get only relevant file paths (if mentioned in query)
  const relevantFiles = extractRelevantFiles(userQuestion, projectContext);

  return {
    role: agentName,
    corePrinciples,             // 5-10 key principles only
    relevantSkills: skills.map(s => ({
      name: s.name,
      keyPatterns: extractKeyPatterns(s.content)  // Extract only key patterns
    })),
    projectContext: minimalProjectContext,
    relevantFiles,
    question: userQuestion,
    constraints: {
      maxResponseLines: mode === 'deep' ? 100 : 50,
      focusArea: detectFocusArea(userQuestion)
    }
  };
}

/**
 * Extract core principles for agent (5-10 lines max)
 */
function extractCorePrinciples(agentName) {
  const principles = {
    'backend-db-expert': [
      'Design for failure - everything fails eventually',
      'Prefer async communication for loose coupling',
      'Index based on query patterns, not structure',
      'Denormalize for reads when JOINs hurt',
      'Security by design, not afterthought'
    ],
    'frontend-ux-expert': [
      'Mobile-first, progressive enhancement',
      'Accessibility is not optional (WCAG 2.1 AA)',
      'Performance budget: < 3s interactive',
      'Component reusability over duplication',
      'User testing validates assumptions'
    ],
    'platform-expert': [
      'Automate everything - manual does not scale',
      'Immutable infrastructure - no manual changes',
      'Infrastructure as code - declarative, versioned',
      'Testing pyramid: 70% unit, 20% integration, 10% E2E',
      'Monitor everything - you cannot fix what you cannot see'
    ],
    'security-expert': [
      'Never trust user input - validate everything',
      'Principle of least privilege',
      'Defense in depth - multiple security layers',
      'Fail secure - errors should not expose data',
      'Audit everything - logging is critical'
    ],
    'product-expert': [
      'Validate problem before building solution',
      'Start with MVP - iterate based on feedback',
      'User needs > Feature requests',
      'Measure outcomes, not outputs',
      'Prioritize ruthlessly - say no often'
    ]
  };

  return principles[agentName] || [];
}

/**
 * Filter project context to only relevant fields
 */
function filterProjectContext(projectContext, userQuestion) {
  if (!projectContext) return null;

  const query = userQuestion.toLowerCase();

  // Base context (always include)
  const minimal = {
    framework: projectContext.framework,
    language: projectContext.language
  };

  // Include database if query mentions it
  if (query.includes('database') || query.includes('query') || query.includes('schema')) {
    minimal.database = projectContext.database;
    minimal.orm = projectContext.orm;
  }

  // Include modules only if relevant
  if (query.includes('module') || query.includes('structure')) {
    minimal.modules = projectContext.modules?.slice(0, 3);  // Max 3
  }

  return minimal;
}

/**
 * Extract relevant file paths from query
 */
function extractRelevantFiles(userQuestion, projectContext) {
  const files = [];

  // Simple pattern matching for file references
  const filePattern = /[\w\/\-\.]+\.(ts|js|tsx|jsx|md|json)/g;
  const matches = userQuestion.match(filePattern);

  if (matches) {
    files.push(...matches);
  }

  // If no files mentioned, return empty (agent will discover them)
  return files;
}

/**
 * Extract key patterns from skill content (summary)
 */
function extractKeyPatterns(skillContent) {
  const patterns = [];

  // Extract checklist items
  const checklistPattern = /- \[ \] (.+)/g;
  let match;
  while ((match = checklistPattern.exec(skillContent)) !== null) {
    patterns.push(match[1]);
    if (patterns.length >= 5) break;  // Max 5 patterns
  }

  return patterns;
}

/**
 * Detect focus area from question
 */
function detectFocusArea(userQuestion) {
  const query = userQuestion.toLowerCase();

  if (query.includes('security') || query.includes('auth') || query.includes('vulnerability')) {
    return 'security';
  }
  if (query.includes('performance') || query.includes('optimize') || query.includes('slow')) {
    return 'performance';
  }
  if (query.includes('test') || query.includes('coverage')) {
    return 'testing';
  }
  if (query.includes('design') || query.includes('architecture') || query.includes('structure')) {
    return 'architecture';
  }
  if (query.includes('ui') || query.includes('ux') || query.includes('interface')) {
    return 'ui/ux';
  }

  return 'general';
}

/**
 * Validate context contract (for debugging)
 */
function validateContract(context) {
  const errors = [];

  if (!context.role) {
    errors.push('Missing role');
  }
  if (!context.question) {
    errors.push('Missing question');
  }
  if (context.corePrinciples.length === 0) {
    errors.push('No core principles defined');
  }

  return {
    valid: errors.length === 0,
    errors
  };
}

module.exports = {
  buildMinimalContext,
  extractCorePrinciples,
  filterProjectContext,
  extractRelevantFiles,
  detectFocusArea,
  validateContract
};
