/**
 * Context Detector
 *
 * Analyzes user input to detect:
 * - Task type (consult, feature, bug, refactor, product, design, analytics, documentation)
 * - Risk level (low, medium, high, critical)
 * - Technology stack
 * - Scope/complexity
 */

const path = require('path');

/**
 * Main detection function
 * @param {string} userInput - The user's message
 * @returns {Object} Detection result
 */
function detectContext(userInput) {
  const input = userInput.toLowerCase();

  return {
    taskType: detectTaskType(input),
    riskLevel: detectRiskLevel(input),
    stack: detectStack(input),
    scope: detectScope(input),
    confidence: calculateConfidence(input)
  };
}

/**
 * Detect task type from input
 */
function detectTaskType(input) {
  // Pattern matching is hardcoded below (config-driven patterns archived in config_archive/)
  const rules = {};

  // Build patterns (hardcoded)
  const consultPatterns = [
    /should i|what'?s better|what is better|how does \w+ compare to|which is best/i,
    /recommend|suggest|advice|best practice/i,
    /design|architecture|approach for/i,
    /difference between|pros and cons|when to use/i,
    ...(rules.consult?.keywords?.map(k => new RegExp(k, 'i')) || [])
  ];

  const featurePatterns = [
    /add|implement|create|build/i,
    /new feature|enable|support/i,
    /integrate|connect|setup/i,
    /migrate|migration|upgrade/i,
    ...(rules.feature?.keywords?.map(k => new RegExp(k, 'i')) || [])
  ];

  const bugPatterns = [
    /fix|bug|error|broken|not working/i,
    /fails|crashes|returns wrong|issue with/i,
    /500 error|exception|throws/i,
    ...(rules.bug?.keywords?.map(k => new RegExp(k, 'i')) || [])
  ];

  const refactorPatterns = [
    /refactor|clean up|optimize|improve/i,
    /reorganize|move|rename|restructure/i,
    ...(rules.refactor?.keywords?.map(k => new RegExp(k, 'i')) || [])
  ];

  const productPatterns = [
    /user story|user stories|acceptance criteria|definition of done/i,
    /roadmap|prioritize|prioritization|backlog|sprint plan/i,
    /mvp|minimum viable|product discovery|feature spec/i,
    /rice score|ice score|stakeholder/i
  ];

  const designPatterns = [
    /wireframe|mockup|prototype|user flow/i,
    /design system|design tokens|ui\/ux|ux research/i,
    /usability|accessibility audit|wcag/i,
    /interaction design|responsive design/i
  ];

  const analyticsPatterns = [
    /analytics|tracking|event tracking|metrics/i,
    /dashboard|funnel|cohort|retention/i,
    /a\/b test|experiment|kpi|north star/i,
    /data pipeline|etl|data warehouse|reporting/i
  ];

  const documentationPatterns = [
    /documentation|api docs|openapi|swagger/i,
    /developer portal|getting started|tutorial/i,
    /sdk|client library|changelog|migration guide/i
  ];

  // Check patterns in order of priority
  if (consultPatterns.some(pattern => pattern.test(input))) {
    return 'consult';
  }

  if (bugPatterns.some(pattern => pattern.test(input))) {
    return 'bug';
  }

  if (productPatterns.some(pattern => pattern.test(input))) {
    return 'product';
  }

  if (designPatterns.some(pattern => pattern.test(input))) {
    return 'design';
  }

  if (analyticsPatterns.some(pattern => pattern.test(input))) {
    return 'analytics';
  }

  if (documentationPatterns.some(pattern => pattern.test(input))) {
    return 'documentation';
  }

  if (featurePatterns.some(pattern => pattern.test(input))) {
    return 'feature';
  }

  if (refactorPatterns.some(pattern => pattern.test(input))) {
    return 'refactor';
  }

  return 'unknown';
}

/**
 * Detect risk level based on keywords and patterns
 * NEW (v3.0): Specific triggers only, no over-triggering
 */
function detectRiskLevel(input) {
  const taskType = detectTaskType(input);

  // Base risk by task type
  const baseRisk = {
    'feature': 'low',
    'bug': 'medium',
    'refactor': 'low',
    'consult': 'low'
  };

  let risk = baseRisk[taskType] || 'low';

  // Complexity factors that increase risk (+2 levels)
  // Check for presence of both concepts, regardless of order
  const criticalComplexity = [
    // ANY auth/security implementation (JWT, OAuth, full auth system)
    // Includes "migrate to JWT" as implementing auth
    input => /\b(authentication|authorization|jwt|oauth|saml)\b/i.test(input) &&
             /\b(add|implement|create|build|migrat(e|ion))\b/i.test(input),
    // Payment processing
    input => /\b(payment|billing|stripe)\b/i.test(input) &&
             /\b(process|processing|handle|integrate|implement|create)\b/i.test(input),
    // Encryption of sensitive data
    input => /\b(encrypt|encryption)\b/i.test(input) &&
             /\b(password|sensitive|credential)/i.test(input),
    // Breaking changes (singular or plural)
    input => /\bbreaking\s+changes?\b/i.test(input)
  ];

  // Moderate complexity factors (+1 level)
  const highComplexity = [
    // Real-time features
    input => /\b(websocket|real.?time|event.?driven)\b/i.test(input),
    // Third-party integrations
    input => /\bthird.?party\b/i.test(input) &&
             /\b(api|integration|service)/i.test(input),
    // Multi-tenancy
    input => /\bmulti.?tenant/i.test(input),
    // Database/schema migrations (NOT auth migrations, those are critical)
    input => /\b(migrat(e|ion)|schema\s+change)\b/i.test(input) &&
             !/\b(jwt|oauth|saml|authentication|authorization)\b/i.test(input)
  ];

  // Scope factors that increase risk (+1 level each)
  const scopeFactors = [
    /\b(multiple|several|many)\s+(modules|services|files)/i,
    /\bcore\s+architecture\b/i,
    /\bproduction\s+only\b/i,
    /\bno\s+rollback\b/i,
    // Production deployments/migrations (bidirectional check)
    input => (/\b(production|prod)\b/i.test(input) &&
              /\b(deploy|migration|migrat(e|ion)|release)\b/i.test(input))
  ];

  let riskIncrease = 0;

  // Check critical complexity (functions or regex patterns)
  if (criticalComplexity.some(check =>
    typeof check === 'function' ? check(input) : check.test(input)
  )) {
    riskIncrease += 2;
  }

  // Check high complexity (functions or regex patterns)
  if (highComplexity.some(check =>
    typeof check === 'function' ? check(input) : check.test(input)
  )) {
    riskIncrease += 1;
  }

  // Check scope factors (functions or regex patterns)
  if (scopeFactors.some(check =>
    typeof check === 'function' ? check(input) : check.test(input)
  )) {
    riskIncrease += 1;
  }

  // Calculate final risk
  const riskLevels = ['low', 'medium', 'high', 'critical'];
  const baseIndex = riskLevels.indexOf(risk);
  const finalIndex = Math.min(baseIndex + riskIncrease, riskLevels.length - 1);

  return riskLevels[finalIndex];
}

/**
 * Detect technology stack from input
 */
function detectStack(input) {
  const stacks = [];

  const stackPatterns = {
    nestjs: /nest\.?js|nest/i,
    typeorm: /typeorm|orm/i,
    postgresql: /postgres|postgresql|pg/i,
    redis: /redis/i,
    typescript: /typescript|ts/i,
    react: /react|next\.?js/i,
    docker: /docker|container/i,
    jwt: /jwt|json web token/i
  };

  for (const [stack, pattern] of Object.entries(stackPatterns)) {
    if (pattern.test(input)) {
      stacks.push(stack);
    }
  }

  return stacks.length > 0 ? stacks : ['general'];
}

/**
 * Detect scope/complexity
 */
function detectScope(input) {
  // Simple indicators
  if (/simple|quick|small|minor|trivial/.test(input)) {
    return 'small';
  }

  // Large indicators
  if (/complex|large|major|entire|full|complete/.test(input)) {
    return 'large';
  }

  // Multi-file indicators
  if (/refactor|restructure|migrate|upgrade/.test(input)) {
    return 'large';
  }

  return 'medium';
}

/**
 * Calculate confidence in detection
 * NEW (v3.0): Contextual algorithm with keyword, structure, and clarity bonuses
 */
function calculateConfidence(input) {
  // Base score: 40%
  let confidence = 0.4;

  // Keyword bonus: up to 30%
  const strongKeywords = [
    'api', 'endpoint', 'database', 'authentication', 'auth',
    'payment', 'security', 'migration', 'deploy', 'production',
    'user', 'service', 'controller', 'repository', 'entity',
    'bug', 'error', 'fix', 'implement', 'create', 'add',
    'refactor', 'optimize', 'test', 'integration'
  ];

  const keywordMatches = strongKeywords.filter(keyword =>
    new RegExp(`\\b${keyword}\\b`, 'i').test(input)
  ).length;

  if (keywordMatches >= 2) {
    confidence += 0.3;
  } else if (keywordMatches === 1) {
    confidence += 0.2;
  }

  // Structure bonus: up to 15%
  const hasQuestionMark = /\?/.test(input);
  const hasImperativeVerb = /^(add|create|implement|fix|update|delete|build|refactor|optimize)\b/i.test(input.trim());
  const hasMultipleSentences = (input.match(/[.!?]+/g) || []).length > 1;

  if (hasQuestionMark || hasImperativeVerb) {
    confidence += 0.15;
  } else if (hasMultipleSentences) {
    confidence += 0.10;
  } else {
    confidence += 0.05;
  }

  // Clarity bonus: up to 15%
  const words = input.split(/\s+/).length;
  const hasSpecificNouns = /\b(user|endpoint|table|service|controller|component|feature)\b/i.test(input);
  const noAmbiguousTerms = !/\b(something|stuff|thing|whatever|some)\b/i.test(input);

  if (noAmbiguousTerms && hasSpecificNouns && words >= 5) {
    confidence += 0.15;
  } else if (hasSpecificNouns || words >= 8) {
    confidence += 0.10;
  }

  // Cap at 1.0
  return Math.min(confidence, 1.0);
}

/**
 * Check if user input requests planning/brainstorming explicitly
 */
function wantsWorkflow(input) {
  return /plan|brainstorm|think through|step.by.step|workflow/.test(input.toLowerCase());
}

module.exports = {
  detectContext,
  detectTaskType,
  detectRiskLevel,
  detectStack,
  detectScope,
  calculateConfidence,
  wantsWorkflow
};
