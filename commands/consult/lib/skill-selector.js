/**
 * Skill Selector - Lazy Loading Engine
 *
 * Selects only relevant skills based on query keywords
 * to minimize context window consumption (67% token reduction)
 */

/**
 * Keyword mapping for skills
 * Maps skill names to their relevant keywords
 */
const SKILL_KEYWORDS = {
  'api-design-principles': [
    'api', 'endpoint', 'rest', 'graphql', 'versioning', 'pagination',
    'rate limit', 'throttling', 'authentication', 'authorization',
    'dto', 'validation', 'swagger', 'openapi'
  ],
  'architecture-patterns': [
    'architecture', 'ddd', 'clean', 'bounded', 'context', 'module',
    'structure', 'layer', 'separation', 'organization', 'pattern',
    'design pattern', 'refactor', 'repository', 'service layer'
  ],
  'resilience-patterns': [
    'resilience', 'circuit', 'breaker', 'retry', 'timeout', 'health',
    'graceful', 'degradation', 'fallback', 'bulkhead', 'monitoring',
    'reliability', 'fault tolerance', 'recovery'
  ],
  'nestjs-code-reviewer': [
    'security', 'review', 'code quality', 'owasp', 'vulnerability',
    'injection', 'xss', 'csrf', 'audit', 'secure', 'validation',
    'sanitization', 'best practice'
  ],
  'react-best-practices': [
    'react', 'component', 'hook', 'state', 'props', 'performance',
    'memoization', 'optimization', 'rendering', 'lifecycle'
  ],
  'frontend-design': [
    'frontend', 'ui', 'ux', 'design', 'interface', 'layout', 'style',
    'css', 'responsive', 'accessibility', 'a11y', 'wireframe', 'mockup'
  ],
  'workflow/tdd': [
    'test', 'tdd', 'unit test', 'integration', 'testing', 'coverage',
    'jest', 'vitest', 'spec', 'test-driven'
  ],
  'quality-gates/systematic-debugging': [
    'debug', 'bug', 'error', 'issue', 'troubleshoot', 'diagnose',
    'root cause', 'fix', 'problem'
  ],
  'product/product-discovery': [
    'product', 'feature', 'requirement', 'user story', 'epic',
    'discovery', 'roadmap', 'backlog', 'prioritization'
  ],
  'product/feature-prioritization': [
    'priority', 'prioritize', 'rice', 'ice', 'moscow', 'roadmap',
    'backlog', 'sprint', 'planning'
  ],
  'product/ux-research': [
    'ux', 'research', 'user', 'interview', 'survey', 'persona',
    'journey', 'usability', 'testing'
  ],
  'product/design-system': [
    'design system', 'component library', 'token', 'theme',
    'style guide', 'pattern library', 'ui kit'
  ],
  'data/analytics-setup': [
    'analytics', 'tracking', 'metrics', 'dashboard', 'kpi',
    'measurement', 'data collection'
  ],
  'data/data-pipeline-design': [
    'pipeline', 'etl', 'data flow', 'ingestion', 'transformation',
    'aggregation', 'data processing'
  ],
  'devrel/api-documentation': [
    'documentation', 'docs', 'api docs', 'reference', 'guide',
    'tutorial', 'example', 'readme'
  ],
  'devrel/developer-portal': [
    'portal', 'developer experience', 'dx', 'onboarding', 'sdk',
    'getting started'
  ]
};

/**
 * Extract keywords from user query
 * Normalizes and tokenizes the query
 */
function extractKeywords(query) {
  // Normalize: lowercase, remove punctuation
  const normalized = query
    .toLowerCase()
    .replace(/[^\w\s-]/g, ' ')
    .trim();

  // Tokenize: split by whitespace
  const tokens = normalized.split(/\s+/);

  // Include bigrams for better matching
  const bigrams = [];
  for (let i = 0; i < tokens.length - 1; i++) {
    bigrams.push(`${tokens[i]} ${tokens[i + 1]}`);
  }

  return [...tokens, ...bigrams];
}

/**
 * Calculate relevance score for a skill based on query
 *
 * @param {string} skillName - Name of the skill
 * @param {string[]} queryKeywords - Keywords from user query
 * @returns {number} Relevance score (0-100)
 */
function calculateSkillRelevance(skillName, queryKeywords) {
  const skillKeywords = SKILL_KEYWORDS[skillName] || [];

  if (skillKeywords.length === 0) {
    return 0;
  }

  let matches = 0;
  let totalWeight = 0;

  for (const queryKw of queryKeywords) {
    for (const skillKw of skillKeywords) {
      // Exact match
      if (queryKw === skillKw) {
        matches += 10;
        totalWeight += 10;
      }
      // Partial match (contains)
      else if (queryKw.includes(skillKw) || skillKw.includes(queryKw)) {
        matches += 5;
        totalWeight += 5;
      }
    }
  }

  // Normalize to 0-100 scale
  if (totalWeight === 0) {
    return 0;
  }

  return Math.min(100, (matches / skillKeywords.length) * 100);
}

/**
 * Select relevant skills from available skills for an agent
 *
 * @param {string} query - User's question
 * @param {string[]} availableSkills - All skills available for this agent
 * @param {Object} options - Selection options
 * @param {number} options.threshold - Minimum relevance score (0-100)
 * @param {number} options.maxSkills - Maximum number of skills to return
 * @param {boolean} options.forceAll - Force loading all skills (bypass lazy loading)
 * @returns {string[]} Selected skill names
 */
function selectRelevantSkills(query, availableSkills, options = {}) {
  const {
    threshold = 10,        // Minimum 10% relevance
    maxSkills = 3,         // Max 3 skills per agent
    forceAll = false       // --deep mode bypasses lazy loading
  } = options;

  // Deep mode: load all skills
  if (forceAll) {
    return availableSkills;
  }

  // Empty query: load no skills (let agent use general knowledge)
  if (!query || query.trim().length === 0) {
    return [];
  }

  // Extract keywords
  const queryKeywords = extractKeywords(query);

  // Score each skill
  const scoredSkills = availableSkills.map(skillName => ({
    name: skillName,
    score: calculateSkillRelevance(skillName, queryKeywords)
  }));

  // Filter by threshold and sort by score
  const relevantSkills = scoredSkills
    .filter(s => s.score >= threshold)
    .sort((a, b) => b.score - a.score)
    .slice(0, maxSkills)
    .map(s => s.name);

  return relevantSkills;
}

/**
 * Get selection statistics (for debugging/monitoring)
 */
function getSelectionStats(query, availableSkills) {
  const queryKeywords = extractKeywords(query);

  const scores = availableSkills.map(skillName => ({
    skill: skillName,
    score: calculateSkillRelevance(skillName, queryKeywords),
    keywords: SKILL_KEYWORDS[skillName] || []
  }));

  return {
    query,
    queryKeywords,
    scores: scores.sort((a, b) => b.score - a.score)
  };
}

module.exports = {
  selectRelevantSkills,
  extractKeywords,
  calculateSkillRelevance,
  getSelectionStats,
  SKILL_KEYWORDS
};
