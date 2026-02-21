/**
 * Session Orchestrator - Entry Point
 *
 * Connects detector → router → skill selection
 * Auto-invokes skills based on context detection
 */

const fs = require('fs');
const path = require('path');
const { detectContext, wantsWorkflow } = require('./lib/detector');
const { route, generateConfirmationMessage, shouldSkipConfirmation, execute } = require('./lib/router');

/**
 * Load settings from .claude/settings.json
 */
function loadSettings() {
  try {
    const settingsPath = path.join(__dirname, '../../../settings.json');
    const content = fs.readFileSync(settingsPath, 'utf-8');
    return JSON.parse(content);
  } catch (error) {
    console.warn('Warning: Could not load settings.json, using defaults');
    return {
      orchestration: {
        enabled: true,
        auto_detect: true,
        confirmations: {
          critical_risk: true,
          high_risk: false
        }
      }
    };
  }
}

/**
 * Main orchestration function
 *
 * @param {string} userInput - User's message
 * @param {Object} options - Additional options
 * @param {string} options.projectPath - Path to project root
 * @param {Object} options.sessionState - Current session state
 * @returns {Object} Orchestration result
 */
async function orchestrate(userInput, options = {}) {
  const settings = loadSettings();

  // Check if orchestration is enabled
  if (!settings.orchestration?.enabled) {
    return {
      action: 'proceed',
      reason: 'Orchestration disabled in settings',
      skill: null,
      command: null
    };
  }

  // Detect context from user input
  const context = detectContext(userInput);

  // Route based on context
  const routingDecision = route(context, userInput);

  // Check if confirmation is needed
  const skipConfirmation = shouldSkipConfirmation(routingDecision, settings);

  // Build result
  const result = {
    detection: context,
    routing: routingDecision,
    action: routingDecision.action,
    skill: routingDecision.skill,
    command: routingDecision.command,
    requiresConfirmation: routingDecision.requiresConfirmation && !skipConfirmation,
    confirmationMessage: routingDecision.requiresConfirmation
      ? generateConfirmationMessage(routingDecision)
      : null,
    reason: routingDecision.reason,
    execution: execute(routingDecision)
  };

  return result;
}

/**
 * Get skill recommendation without executing
 * Useful for preview/debugging
 *
 * @param {string} userInput - User's message
 * @returns {Object} Recommendation
 */
function recommend(userInput) {
  const context = detectContext(userInput);
  const routingDecision = route(context, userInput);

  return {
    taskType: context.taskType,
    riskLevel: context.riskLevel,
    stack: context.stack,
    confidence: context.confidence,
    recommendedSkill: routingDecision.skill,
    recommendedCommand: routingDecision.command,
    reason: routingDecision.reason
  };
}

/**
 * Check if a specific skill should be auto-invoked for input
 *
 * @param {string} userInput - User's message
 * @param {string} skillName - Skill to check
 * @returns {boolean} Should auto-invoke
 */
function shouldInvokeSkill(userInput, skillName) {
  const result = orchestrate(userInput);
  return result.skill === skillName && !result.requiresConfirmation;
}

module.exports = {
  orchestrate,
  recommend,
  shouldInvokeSkill,
  // Re-export for direct access
  detectContext,
  route
};
