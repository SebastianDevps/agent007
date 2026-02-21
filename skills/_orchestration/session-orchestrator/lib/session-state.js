/**
 * Session State Management
 *
 * Tracks state across user interactions in a session:
 * - Previous skill activated
 * - Task history
 * - Active context (stack, framework, etc.)
 *
 * This enables:
 * - `previous_skill` condition in routing (router.js)
 * - Context-aware suggestions
 * - Workflow chaining (brainstorm → plan → implement)
 */

class SessionState {
  constructor() {
    this.previousSkill = null;
    this.taskHistory = [];
    this.activeContext = {
      stack: null,       // 'nestjs', 'react', 'nextjs', etc.
      framework: null,   // 'express', 'fastapi', etc.
      database: null,    // 'postgresql', 'mongodb', etc.
      orm: null          // 'typeorm', 'prisma', etc.
    };
    this.sessionStartTime = Date.now();
  }

  /**
   * Record skill activation
   * @param {string} skillName - Name of the skill activated
   * @param {object} context - Additional context (optional)
   */
  recordSkillActivation(skillName, context = {}) {
    this.previousSkill = skillName;
    this.taskHistory.push({
      skill: skillName,
      timestamp: Date.now(),
      context
    });

    // Keep history limited to last 20 tasks
    if (this.taskHistory.length > 20) {
      this.taskHistory.shift();
    }
  }

  /**
   * Update active context (stack, framework, etc.)
   * @param {object} updates - Context updates
   */
  updateContext(updates) {
    this.activeContext = {
      ...this.activeContext,
      ...updates
    };
  }

  /**
   * Get previous skill
   * @returns {string|null} Previous skill name or null
   */
  getPreviousSkill() {
    return this.previousSkill;
  }

  /**
   * Get task history
   * @param {number} limit - Number of recent tasks to return (default: 10)
   * @returns {Array} Recent task history
   */
  getTaskHistory(limit = 10) {
    return this.taskHistory.slice(-limit);
  }

  /**
   * Get active context
   * @returns {object} Active context (stack, framework, etc.)
   */
  getContext() {
    return { ...this.activeContext };
  }

  /**
   * Check if a specific skill was recently used
   * @param {string} skillName - Skill to check
   * @param {number} withinLast - Check within last N tasks (default: 5)
   * @returns {boolean} True if skill was used recently
   */
  wasSkillRecentlyUsed(skillName, withinLast = 5) {
    const recentTasks = this.getTaskHistory(withinLast);
    return recentTasks.some(task => task.skill === skillName);
  }

  /**
   * Get session duration in seconds
   * @returns {number} Session duration in seconds
   */
  getSessionDuration() {
    return Math.floor((Date.now() - this.sessionStartTime) / 1000);
  }

  /**
   * Reset session state (useful for testing)
   */
  reset() {
    this.previousSkill = null;
    this.taskHistory = [];
    this.activeContext = {
      stack: null,
      framework: null,
      database: null,
      orm: null
    };
    this.sessionStartTime = Date.now();
  }

  /**
   * Serialize state to JSON (for persistence if needed)
   * @returns {string} JSON representation
   */
  toJSON() {
    return JSON.stringify({
      previousSkill: this.previousSkill,
      taskHistory: this.taskHistory,
      activeContext: this.activeContext,
      sessionStartTime: this.sessionStartTime
    });
  }

  /**
   * Load state from JSON (for restoration)
   * @param {string} json - JSON string to load
   */
  fromJSON(json) {
    try {
      const data = JSON.parse(json);
      this.previousSkill = data.previousSkill || null;
      this.taskHistory = data.taskHistory || [];
      this.activeContext = data.activeContext || {
        stack: null,
        framework: null,
        database: null,
        orm: null
      };
      this.sessionStartTime = data.sessionStartTime || Date.now();
    } catch (error) {
      console.error('Failed to load session state from JSON:', error);
    }
  }
}

// Singleton instance for the session
let sessionInstance = null;

/**
 * Get the current session state instance
 * @returns {SessionState} Session state singleton
 */
function getSessionState() {
  if (!sessionInstance) {
    sessionInstance = new SessionState();
  }
  return sessionInstance;
}

/**
 * Reset the session state
 */
function resetSession() {
  if (sessionInstance) {
    sessionInstance.reset();
  }
}

module.exports = {
  SessionState,
  getSessionState,
  resetSession
};
