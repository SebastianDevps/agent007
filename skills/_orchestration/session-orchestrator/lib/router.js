/**
 * Workflow Router
 *
 * Makes routing decisions based on detected context.
 * Determines whether to:
 * - Invoke /consult command
 * - Auto-invoke a workflow skill
 * - Proceed with direct implementation
 * - Ask user for clarification
 *
 * Phase 3 Optimization: Static routing table eliminates filesystem scan
 */

const fs = require('fs');
const path = require('path');

/**
 * Static skill routing table
 *
 * IMPORTANT: When adding new skills with `when` conditions, update this table manually.
 * Each entry maps skill name to { when, autoActivate, invokable }
 *
 * Source: Compiled from SKILL.md frontmatter (Phase 3 optimization - eliminates filesystem scan)
 * Last updated: 2026-02-20
 */
const STATIC_SKILL_ROUTING = new Map([
  ['brainstorming', {
    when: [
      { task_type: 'feature', risk_level: ['medium', 'high', 'critical'] },
      { task_type: 'refactor', risk_level: ['high', 'critical'] },
      { user_mentions: ['unclear requirements', 'explore options', 'not sure how'] }
    ],
    autoActivate: 'feature-development (medium+), refactor (high+)',
    invokable: true
  }],

  ['writing-plans', {
    when: [
      { previous_skill: 'brainstorming', status: 'completed' },
      { task_type: ['feature', 'bug', 'refactor'], risk_level: ['medium', 'high', 'critical'] },
      { user_mentions: ['create plan', 'break down', 'tasks'] }
    ],
    autoActivate: 'feature-development (all), bug-fixing (medium+), refactor (medium+)',
    invokable: true
  }],

  ['systematic-debugging', {
    when: [
      { task_type: 'bug', risk_level: ['low', 'medium', 'high', 'critical'] },
      { user_mentions: ['bug', 'error', 'fix', 'broken', 'not working', 'fails'] }
    ],
    autoActivate: 'bug-fixing (all levels)',
    invokable: true
  }],

  ['product-discovery', {
    when: [
      { task_type: 'product', risk_level: ['medium', 'high', 'critical'] },
      { user_mentions: ['validate idea', 'mvp', 'product discovery', 'user needs', 'problem validation'] }
    ],
    autoActivate: false,
    invokable: true
  }],

  ['api-documentation', {
    when: [
      { task_type: 'documentation' },
      { user_mentions: ['api docs', 'documentation', 'openapi', 'swagger', 'developer portal'] }
    ],
    autoActivate: false,
    invokable: true
  }]
]);

/**
 * Get static skill when conditions (replaces filesystem scan)
 * @returns {Map} Map of skill names to when conditions
 */
function loadSkillWhenConditions() {
  // Phase 3 optimization: Return static table instead of scanning filesystem
  return STATIC_SKILL_ROUTING;
}

/**
 * Create trigger function from when conditions
 */
function createTriggerFromWhen(whenConditions, userInput = '') {
  return (context) => {
    for (const condition of whenConditions) {
      // Handle task_type matching
      if (condition.task_type) {
        const taskTypes = Array.isArray(condition.task_type)
          ? condition.task_type
          : [condition.task_type];

        if (!taskTypes.includes(context.taskType)) {
          continue;
        }
      }

      // Handle risk_level matching
      if (condition.risk_level) {
        const riskLevels = Array.isArray(condition.risk_level)
          ? condition.risk_level
          : [condition.risk_level];

        if (!riskLevels.includes(context.riskLevel)) {
          continue;
        }
      }

      // Handle user_mentions matching
      if (condition.user_mentions) {
        const mentions = condition.user_mentions;
        const input = userInput.toLowerCase();

        if (!mentions.some(phrase => input.includes(phrase.toLowerCase()))) {
          continue;
        }
      }

      // Handle previous_skill matching
      if (condition.previous_skill) {
        const sessionState = require('./session-state').getSessionState();
        const previousSkill = sessionState.getPreviousSkill();
        const expectedSkills = Array.isArray(condition.previous_skill)
          ? condition.previous_skill
          : [condition.previous_skill];

        if (!previousSkill || !expectedSkills.includes(previousSkill)) {
          continue;
        }
      }

      // Handle stack matching
      if (condition.stack) {
        const stacks = Array.isArray(condition.stack) ? condition.stack : [condition.stack];
        const hasMatchingStack = stacks.some(s => context.stack?.includes(s));

        if (!hasMatchingStack) {
          continue;
        }
      }

      // If we made it here, all conditions matched
      return true;
    }

    return false;
  };
}

/**
 * Routing table definition
 */
const ROUTING_TABLE = {
  // Consultations - always route to /consult
  consult: {
    trigger: (context) => context.taskType === 'consult',
    action: 'invoke_command',
    command: '/consult',
    requiresConfirmation: false,
    reason: 'Question or architectural advice'
  },

  // Features - medium/high risk get brainstorming
  feature_critical: {
    trigger: (context) => context.taskType === 'feature' && context.riskLevel === 'critical',
    action: 'invoke_skill',
    skill: 'brainstorming',
    requiresConfirmation: true,
    reason: 'Critical complexity feature - brainstorming recommended'
  },

  feature_high: {
    trigger: (context) => context.taskType === 'feature' && context.riskLevel === 'high',
    action: 'invoke_skill',
    skill: 'brainstorming',
    requiresConfirmation: true,
    reason: 'High complexity feature - brainstorming recommended'
  },

  feature_medium: {
    trigger: (context) => context.taskType === 'feature' && context.riskLevel === 'medium',
    action: 'invoke_skill',
    skill: 'brainstorming',
    requiresConfirmation: true,
    reason: 'Medium complexity feature - brainstorming recommended'
  },

  feature_low: {
    trigger: (context) => context.taskType === 'feature' && context.riskLevel === 'low',
    action: 'proceed',
    requiresConfirmation: false,
    reason: 'Low complexity feature - direct implementation'
  },

  // Bugs - always use systematic debugging
  bug_all: {
    trigger: (context) => context.taskType === 'bug',
    action: 'invoke_skill',
    skill: 'systematic-debugging',
    requiresConfirmation: false,
    reason: 'Bug requires systematic debugging approach'
  },

  // Refactor - depends on scope
  refactor_large: {
    trigger: (context) => context.taskType === 'refactor' && context.scope === 'large',
    action: 'invoke_skill',
    skill: 'brainstorming',
    requiresConfirmation: true,
    reason: 'Large refactor - planning recommended'
  },

  refactor_small: {
    trigger: (context) => context.taskType === 'refactor' && context.scope !== 'large',
    action: 'proceed',
    requiresConfirmation: false,
    reason: 'Small refactor - direct implementation'
  },

  // Product - route to /consult (auto-selects product-expert)
  product: {
    trigger: (context) => context.taskType === 'product',
    action: 'invoke_command',
    command: '/consult',
    requiresConfirmation: false,
    reason: 'Product task - routing to /consult with product-expert auto-selection'
  },

  // Design/UX - route to /consult (auto-selects frontend-ux-expert)
  design: {
    trigger: (context) => context.taskType === 'design',
    action: 'invoke_command',
    command: '/consult',
    requiresConfirmation: false,
    reason: 'Design/UX task - routing to /consult with frontend-ux-expert auto-selection'
  },

  // Analytics - route to /consult (backend-db-expert covers analytics queries/schema)
  analytics: {
    trigger: (context) => context.taskType === 'analytics',
    action: 'invoke_command',
    command: '/consult',
    requiresConfirmation: false,
    reason: 'Analytics task - routing to /consult with backend-db-expert auto-selection'
  },

  // Documentation - route to devrel/api-documentation skill
  documentation: {
    trigger: (context) => context.taskType === 'documentation',
    action: 'invoke_skill',
    skill: 'devrel/api-documentation',
    requiresConfirmation: false,
    reason: 'Documentation task - invoking api-documentation skill'
  },

  // Ambiguous - ask user
  ambiguous: {
    trigger: (context) => context.taskType === 'unknown' || context.confidence < 0.6,
    action: 'ask_user',
    requiresConfirmation: true,
    reason: 'Ambiguous input - clarification needed'
  }
};

/**
 * Build dynamic routing table from skill when conditions
 */
function buildDynamicRoutingTable(userInput = '') {
  const skillConditions = loadSkillWhenConditions();
  const dynamicRules = {};

  for (const [skillName, config] of skillConditions.entries()) {
    if (!config.when || !config.invokable) continue;

    const whenArray = Array.isArray(config.when) ? config.when : [config.when];
    const trigger = createTriggerFromWhen(whenArray, userInput);

    // Determine if this is auto-activated
    const isAutoActivate = config.autoActivate !== undefined;

    dynamicRules[`skill_${skillName}`] = {
      trigger,
      action: 'invoke_skill',
      skill: skillName,
      requiresConfirmation: isAutoActivate ? true : false,
      reason: `Auto-activation condition matched for ${skillName}`
    };
  }

  return dynamicRules;
}

/**
 * Log routing decision to usage.jsonl for analytics
 * @param {string} userInput - Original user input
 * @param {Object} routingDecision - Decision object from route()
 */
function logRoutingDecision(userInput, routingDecision) {
  try {
    const logDir = path.join(__dirname, '../../../../');
    const logFile = path.join(logDir, 'usage.jsonl');

    // Check file size and rotate if needed (max 10MB)
    try {
      const stats = fs.statSync(logFile);
      if (stats.size > 10 * 1024 * 1024) {
        const backupFile = path.join(logDir, `usage.${Date.now()}.jsonl`);
        fs.renameSync(logFile, backupFile);
      }
    } catch (error) {
      // File doesn't exist yet, will be created
    }

    const logEntry = {
      timestamp: new Date().toISOString(),
      userInput: userInput.substring(0, 200), // Limit length
      taskType: routingDecision.context?.taskType,
      riskLevel: routingDecision.context?.riskLevel,
      confidence: routingDecision.context?.confidence,
      matchedRule: routingDecision.rule,
      action: routingDecision.action,
      skill: routingDecision.skill,
      command: routingDecision.command,
      requiresConfirmation: routingDecision.requiresConfirmation
    };

    fs.appendFileSync(logFile, JSON.stringify(logEntry) + '\n', 'utf-8');
  } catch (error) {
    // Silent fail - telemetry should not break routing
    // Could optionally log to console in development
  }
}

/**
 * Main routing function
 * @param {Object} context - Detection context from detector
 * @param {string} userInput - Original user input for when conditions
 * @returns {Object} Routing decision
 */
function route(context, userInput = '') {
  const sessionState = require('./session-state').getSessionState();

  // Build combined routing table: dynamic + static
  const dynamicRules = buildDynamicRoutingTable(userInput);
  const combinedTable = {
    ...ROUTING_TABLE,      // Static rules (fallback)
    ...dynamicRules        // Dynamic rules from when conditions (take precedence)
  };

  // Find first matching rule
  for (const [ruleName, rule] of Object.entries(combinedTable)) {
    if (rule.trigger(context)) {
      const decision = {
        rule: ruleName,
        action: rule.action,
        command: rule.command,
        skill: rule.skill,
        requiresConfirmation: rule.requiresConfirmation,
        reason: rule.reason,
        context
      };

      // Track skill activation in session state
      if (rule.skill) {
        sessionState.recordSkillActivation(rule.skill, {
          taskType: context.taskType,
          riskLevel: context.riskLevel,
          confidence: context.confidence
        });
      }

      // Log routing decision for analytics
      logRoutingDecision(userInput, decision);

      return decision;
    }
  }

  // Default: proceed with direct implementation
  const defaultDecision = {
    rule: 'default',
    action: 'proceed',
    requiresConfirmation: false,
    reason: 'Default - direct implementation with enforcement',
    context
  };

  // Log routing decision for analytics
  logRoutingDecision(userInput, defaultDecision);

  return defaultDecision;
}

/**
 * Generate confirmation message for user
 */
function generateConfirmationMessage(routingDecision) {
  const { context, reason, action, skill } = routingDecision;

  if (action === 'ask_user') {
    return `I can help with:\n` +
           `[C] Consult - Get architectural advice\n` +
           `[F] Feature - Implement new functionality\n` +
           `[B] Bug - Fix an issue systematically\n` +
           `[R] Refactor - Improve existing code\n\n` +
           `Which best describes what you need?`;
  }

  if (action === 'invoke_skill' && skill === 'brainstorming') {
    const riskEmoji = {
      critical: '🔴',
      high: '🟠',
      medium: '🟡',
      low: '🟢'
    }[context.riskLevel] || '⚪';

    return `${riskEmoji} **${context.riskLevel.toUpperCase()} complexity** task detected.\n\n` +
           `${reason}\n\n` +
           `Use brainstorming workflow? (Y/n)`;
  }

  return `${reason}\n\nProceed? (Y/n)`;
}

/**
 * Check if settings allow auto-invocation without confirmation
 */
function shouldSkipConfirmation(routingDecision, settings = {}) {
  const orchestration = settings.orchestration || {};
  const confirmations = orchestration.confirmations || {};

  // If orchestration disabled, always confirm
  if (!orchestration.enabled) {
    return false;
  }

  // If auto_detect disabled, always confirm
  if (!orchestration.auto_detect) {
    return false;
  }

  const { context, requiresConfirmation } = routingDecision;

  // Rule says no confirmation needed
  if (!requiresConfirmation) {
    return true;
  }

  // Check settings for this risk level
  if (context.riskLevel === 'critical' && confirmations.critical_risk === false) {
    return true;
  }

  if (context.riskLevel === 'high' && confirmations.high_risk === false) {
    return true;
  }

  // Default: require confirmation
  return false;
}

/**
 * Execute routing decision
 * Returns command/skill to invoke
 */
function execute(routingDecision) {
  const { action, command, skill } = routingDecision;

  switch (action) {
    case 'invoke_command':
      return { type: 'command', value: command };

    case 'invoke_skill':
      return { type: 'skill', value: skill };

    case 'proceed':
      return { type: 'proceed', value: null };

    case 'ask_user':
      return { type: 'ask', value: null };

    default:
      return { type: 'proceed', value: null };
  }
}

module.exports = {
  ROUTING_TABLE,
  route,
  generateConfirmationMessage,
  shouldSkipConfirmation,
  execute,
  logRoutingDecision  // Exposed for testing/debugging
};
