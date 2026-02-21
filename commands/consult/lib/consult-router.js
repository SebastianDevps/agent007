/**
 * Consult Router
 *
 * Auto-selects appropriate experts based on query analysis
 * Uses session-orchestrator detector for intelligent routing
 */

const path = require('path');

// Import detector from session-orchestrator
const detectorPath = path.join(__dirname, '../../../skills/_orchestration/session-orchestrator/lib/detector.js');
let detector;

try {
  detector = require(detectorPath);
} catch (error) {
  // Fallback if detector not available
  detector = {
    detectContext: (input) => ({
      taskType: 'consult',
      riskLevel: 'medium',
      stack: [],
      confidence: 0.5
    })
  };
}

/**
 * Expert selection rules based on keywords and topics
 */
const EXPERT_SELECTION_RULES = {
  'backend-expert': {
    keywords: [
      'api', 'endpoint', 'rest', 'graphql', 'microservice',
      'service', 'architecture', 'backend', 'server',
      'nestjs', 'express', 'fastify', 'node',
      'scalability', 'performance', 'distributed'
    ],
    topics: ['api-design', 'architecture', 'backend', 'microservices', 'services']
  },

  'database-expert': {
    keywords: [
      'database', 'query', 'sql', 'postgresql', 'mysql', 'mongodb',
      'schema', 'migration', 'orm', 'typeorm', 'prisma',
      'index', 'optimization', 'n+1', 'transaction',
      'data model', 'normalization', 'denormalization'
    ],
    topics: ['database', 'data', 'schema', 'queries', 'orm']
  },

  'security-expert': {
    keywords: [
      'security', 'auth', 'authentication', 'authorization',
      'jwt', 'oauth', 'session', 'token', 'password',
      'encryption', 'hash', 'vulnerability', 'owasp',
      'xss', 'injection', 'csrf', 'cors', 'compliance'
    ],
    topics: ['security', 'auth', 'compliance', 'vulnerabilities']
  },

  'frontend-expert': {
    keywords: [
      'frontend', 'react', 'next', 'vue', 'angular',
      'component', 'ui', 'ux', 'interface', 'page',
      'state management', 'redux', 'hooks', 'rendering',
      'performance', 'optimization', 'bundle', 'ssr'
    ],
    topics: ['frontend', 'ui', 'react', 'performance']
  },

  'devops-expert': {
    keywords: [
      'devops', 'deployment', 'ci/cd', 'docker', 'kubernetes',
      'container', 'build', 'pipeline', 'github actions',
      'infrastructure', 'monitoring', 'logging', 'observability',
      'cloud', 'aws', 'azure', 'gcp', 'serverless'
    ],
    topics: ['devops', 'deployment', 'infrastructure', 'ci-cd']
  },

  'testing-expert': {
    keywords: [
      'test', 'testing', 'tdd', 'bdd', 'unit test',
      'integration test', 'e2e', 'jest', 'vitest',
      'coverage', 'mock', 'stub', 'fixture',
      'test strategy', 'quality assurance'
    ],
    topics: ['testing', 'quality', 'tdd', 'test-strategy']
  },

  'product-expert': {
    keywords: [
      'product', 'feature', 'roadmap', 'prioritize', 'prioritization',
      'user story', 'acceptance criteria', 'mvp', 'discovery',
      'user research', 'persona', 'backlog', 'sprint planning',
      'rice', 'stakeholder', 'requirement', 'specification'
    ],
    topics: ['product', 'pm', 'roadmap', 'prioritization', 'user-stories']
  },

  'ux-expert': {
    keywords: [
      'ux', 'user experience', 'wireframe', 'prototype',
      'user flow', 'usability', 'accessibility', 'wcag',
      'design system', 'design tokens', 'interaction design',
      'responsive', 'mobile first', 'navigation', 'layout'
    ],
    topics: ['ux', 'design', 'wireframes', 'accessibility', 'design-system']
  },

  'data-expert': {
    keywords: [
      'analytics', 'tracking', 'metrics', 'dashboard',
      'data pipeline', 'etl', 'data warehouse', 'dbt',
      'event tracking', 'funnel', 'cohort', 'retention',
      'a/b test', 'experiment', 'kpi', 'north star',
      'business intelligence', 'reporting'
    ],
    topics: ['analytics', 'data', 'metrics', 'dashboards', 'experiments']
  },

  'devrel-expert': {
    keywords: [
      'documentation', 'api docs', 'swagger', 'openapi',
      'developer portal', 'getting started', 'tutorial',
      'sdk', 'client library', 'developer experience',
      'changelog', 'migration guide', 'code examples'
    ],
    topics: ['documentation', 'devrel', 'api-docs', 'sdks', 'developer-portal']
  }
};

/**
 * Calculate relevance score for an expert given a query
 */
function calculateRelevance(expertName, query, context) {
  const rule = EXPERT_SELECTION_RULES[expertName];
  if (!rule) return 0;

  const queryLower = query.toLowerCase();
  let score = 0;

  // Keyword matching
  const matchedKeywords = rule.keywords.filter(keyword =>
    queryLower.includes(keyword.toLowerCase())
  );
  score += matchedKeywords.length * 10;

  // Stack matching from context
  if (context.stack) {
    const stackMatches = rule.keywords.filter(keyword =>
      context.stack.some(s => s.toLowerCase().includes(keyword.toLowerCase()))
    );
    score += stackMatches.length * 5;
  }

  // Risk level boost for security expert
  if (expertName === 'security-expert' && ['high', 'critical'].includes(context.riskLevel)) {
    score += 15;
  }

  // Database keywords boost database expert
  if (expertName === 'database-expert' && queryLower.match(/\b(query|schema|database|orm)\b/)) {
    score += 10;
  }

  // Product task type boost for product expert
  if (expertName === 'product-expert' && context.taskType === 'product') {
    score += 20;
  }

  // Design task type boost for UX expert
  if (expertName === 'ux-expert' && context.taskType === 'design') {
    score += 20;
  }

  // Analytics task type boost for data expert
  if (expertName === 'data-expert' && context.taskType === 'analytics') {
    score += 20;
  }

  // Documentation task type boost for devrel expert
  if (expertName === 'devrel-expert' && context.taskType === 'documentation') {
    score += 20;
  }

  // Product keywords boost product expert
  if (expertName === 'product-expert' && queryLower.match(/\b(user stor|roadmap|prioriti|mvp|backlog)\b/)) {
    score += 10;
  }

  // UX keywords boost ux expert
  if (expertName === 'ux-expert' && queryLower.match(/\b(wireframe|prototype|user flow|design system|accessibility)\b/)) {
    score += 10;
  }

  // Data keywords boost data expert
  if (expertName === 'data-expert' && queryLower.match(/\b(analytics|tracking|metrics|dashboard|pipeline)\b/)) {
    score += 10;
  }

  // DevRel keywords boost devrel expert
  if (expertName === 'devrel-expert' && queryLower.match(/\b(documentation|api docs|swagger|sdk|tutorial)\b/)) {
    score += 10;
  }

  return score;
}

/**
 * Select experts based on query and mode
 */
function selectExperts(query, mode = 'normal', context = null) {
  // Use detector if available
  const detectedContext = context || (detector ? detector.detectContext(query) : {
    taskType: 'consult',
    riskLevel: 'medium',
    stack: [],
    confidence: 0.5
  });

  // Calculate relevance for each expert
  const expertScores = Object.keys(EXPERT_SELECTION_RULES).map(expertName => ({
    name: expertName,
    score: calculateRelevance(expertName, query, detectedContext)
  }));

  // Sort by score
  expertScores.sort((a, b) => b.score - a.score);

  // Select based on mode
  let selectedCount;
  let model;

  switch (mode) {
    case 'quick':
      selectedCount = 1;
      model = 'haiku';
      break;
    case 'deep':
      selectedCount = 3;
      model = 'opus';
      break;
    default: // normal
      selectedCount = 2;
      model = 'sonnet';
  }

  // Filter experts with score > 0
  const relevantExperts = expertScores.filter(e => e.score > 0);

  // Take top N
  const selectedExperts = relevantExperts
    .slice(0, selectedCount)
    .map(e => e.name);

  // Fallback to backend-expert if no matches
  if (selectedExperts.length === 0) {
    selectedExperts.push('backend-expert');
  }

  return {
    experts: selectedExperts,
    scores: expertScores,
    model,
    context: detectedContext,
    reasoning: generateReasoning(selectedExperts, expertScores, mode)
  };
}

/**
 * Generate reasoning for expert selection
 */
function generateReasoning(selectedExperts, allScores, mode) {
  const reasons = selectedExperts.map(expertName => {
    const score = allScores.find(s => s.name === expertName);
    return `${expertName} (score: ${score.score})`;
  });

  return `Selected ${selectedExperts.length} expert(s) for ${mode} mode: ${reasons.join(', ')}`;
}

/**
 * Get model for expert based on agent definition
 */
function getModelForExpert(expertName) {
  // Map from agent definitions
  const modelMap = {
    'backend-expert': 'opus',
    'database-expert': 'opus',
    'security-expert': 'opus',
    'product-expert': 'opus',
    'frontend-expert': 'sonnet',
    'devops-expert': 'sonnet',
    'testing-expert': 'sonnet',
    'ux-expert': 'sonnet',
    'data-expert': 'sonnet',
    'devrel-expert': 'sonnet'
  };

  return modelMap[expertName] || 'sonnet';
}

/**
 * Determine if follow-up questions are needed
 */
function needsFollowUp(query, context) {
  // Check if query is too vague
  if (query.split(' ').length < 5) {
    return {
      needed: true,
      questions: [
        'What is your current tech stack?',
        'What scale are you targeting? (users, requests/sec)',
        'Are there specific constraints? (budget, timeline, team size)'
      ]
    };
  }

  // Check if critical topic without context
  const criticalKeywords = ['auth', 'payment', 'security', 'migration'];
  const hasCritical = criticalKeywords.some(k => query.toLowerCase().includes(k));

  if (hasCritical && !context.stack?.length) {
    return {
      needed: true,
      questions: [
        'What framework are you using?',
        'What is the expected scale?',
        'Are there compliance requirements?'
      ]
    };
  }

  return { needed: false };
}

module.exports = {
  selectExperts,
  calculateRelevance,
  getModelForExpert,
  needsFollowUp,
  EXPERT_SELECTION_RULES
};
