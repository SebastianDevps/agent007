/**
 * Execution Mode System - Dual Agent (Plan/Build)
 *
 * Inspired by OpenCode's dual agent pattern:
 * - PLAN mode: Read-only analysis, no implementation
 * - BUILD mode: Full access, implementation
 *
 * Benefits:
 * - Safety: High-risk tasks analyzed before execution
 * - Token efficiency: Plan mode uses minimal context
 * - User control: Explicit approval before risky changes
 */

const EXECUTION_MODES = {
  PLAN: 'plan',
  BUILD: 'build'
};

const RISK_LEVELS = {
  LOW: 'low',
  MEDIUM: 'medium',
  HIGH: 'high',
  CRITICAL: 'critical'
};

/**
 * Determine execution mode based on risk level
 *
 * @param {string} riskLevel - Risk level (low, medium, high, critical)
 * @param {Object} options - Options
 * @param {boolean} options.forceMode - Force specific mode
 * @returns {string} Execution mode ('plan' or 'build')
 */
function determineMode(riskLevel, options = {}) {
  const { forceMode } = options;

  // Forced mode (for testing or user override)
  if (forceMode) {
    return forceMode;
  }

  // High/Critical risk → PLAN mode first
  if (riskLevel === RISK_LEVELS.HIGH || riskLevel === RISK_LEVELS.CRITICAL) {
    return EXECUTION_MODES.PLAN;
  }

  // Low/Medium risk → BUILD mode directly
  return EXECUTION_MODES.BUILD;
}

/**
 * Get mode-specific configuration
 *
 * @param {string} mode - Execution mode
 * @returns {Object} Mode configuration
 */
function getModeConfig(mode) {
  const configs = {
    [EXECUTION_MODES.PLAN]: {
      mode: 'plan',
      description: 'Analysis mode (read-only)',
      allowedTools: ['Read', 'Grep', 'Glob', 'Bash'],  // Read-only
      loadSkills: false,        // Don't load skills, save tokens
      maxResponseLines: 30,     // Concise analysis
      promptSuffix: `

**PLAN MODE ACTIVE**: You are in read-only analysis mode.
- DO NOT implement changes
- DO NOT edit files
- Analyze and explain what you would do
- Identify risks and dependencies
- Provide clear implementation steps for BUILD mode
      `.trim()
    },
    [EXECUTION_MODES.BUILD]: {
      mode: 'build',
      description: 'Implementation mode (full access)',
      allowedTools: ['*'],      // All tools
      loadSkills: true,         // Load full context
      maxResponseLines: 100,    // Detailed implementation
      promptSuffix: `

**BUILD MODE ACTIVE**: You have full access to implement changes.
- Follow the plan if one exists
- Implement changes carefully
- Test your changes
- Report completion status
      `.trim()
    }
  };

  return configs[mode] || configs[EXECUTION_MODES.BUILD];
}

/**
 * Should transition from PLAN to BUILD?
 *
 * @param {Object} planResult - Result from PLAN mode execution
 * @param {boolean} userApproved - User approved the plan
 * @returns {boolean} True if should transition to BUILD
 */
function shouldTransitionToBuild(planResult, userApproved) {
  return userApproved === true;
}

module.exports = {
  EXECUTION_MODES,
  RISK_LEVELS,
  determineMode,
  getModeConfig,
  shouldTransitionToBuild
};
