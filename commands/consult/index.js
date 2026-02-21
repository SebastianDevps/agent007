/**
 * Consult Command v2.0 - Entry Point
 *
 * Orchestrates the full consultation flow:
 * 1. Scan project context
 * 2. Auto-select experts
 * 3. Inject domain skills
 * 4. Execute consultation
 * 5. Consolidate responses
 * 6. Offer post-consultation actions
 */

const { scanProjectContext, formatContextSummary } = require('./lib/scan-context');
const { selectExperts, needsFollowUp } = require('./lib/consult-router');
const { injectSkillsForAgents } = require('./lib/skills-injector');
const { consolidateResponses } = require('./lib/response-consolidator');

/**
 * Main consultation function
 *
 * @param {string} query - User's question
 * @param {Object} options - Options
 * @param {string} options.mode - 'quick', 'normal', or 'deep'
 * @param {string} options.projectPath - Path to project root
 * @param {boolean} options.skipContext - Skip project scanning
 * @param {string[]} options.forceExperts - Force specific experts
 * @returns {Object} Consultation result
 */
async function consult(query, options = {}) {
  const {
    mode = 'normal',
    projectPath = process.cwd(),
    skipContext = false,
    forceExperts = null
  } = options;

  // Step 1: Scan project context (unless skipped)
  const projectContext = skipContext ? null : scanProjectContext(projectPath);

  // Step 2: Select experts (auto or forced)
  const selection = forceExperts
    ? { experts: forceExperts, model: mode === 'deep' ? 'opus' : 'sonnet', context: null }
    : selectExperts(query, mode, projectContext);

  // Step 3: Check if follow-up needed
  const followUp = needsFollowUp(query, selection.context || {});

  if (followUp.needed) {
    return {
      needsFollowUp: true,
      questions: followUp.questions,
      selectedExperts: selection.experts,
      projectContext
    };
  }

  // Step 4: Inject skills into prompts (with lazy loading)
  const enhancedPrompts = injectSkillsForAgents(
    selection.experts,
    query,
    projectContext,
    projectPath,
    { mode }  // Pass mode for lazy vs full loading
  );

  // Step 5: Prepare consultation request
  const consultationRequest = {
    query,
    mode,
    experts: selection.experts,
    prompts: enhancedPrompts,
    projectContext,
    reasoning: selection.reasoning
  };

  return consultationRequest;
}

/**
 * Preview what the consult command will do (without executing)
 *
 * @param {string} query - User's question
 * @param {Object} options - Options
 * @returns {Object} Preview information
 */
function preview(query, options = {}) {
  const {
    mode = 'normal',
    projectPath = process.cwd()
  } = options;

  const projectContext = scanProjectContext(projectPath);
  const selection = selectExperts(query, mode, projectContext);

  return {
    query,
    mode,
    selectedExperts: selection.experts,
    reasoning: selection.reasoning,
    model: selection.model,
    projectSummary: projectContext ? formatContextSummary(projectContext) : 'No context available',
    scores: selection.scores
  };
}

/**
 * Get available experts and their specializations
 */
function getAvailableExperts() {
  return {
    'backend-expert': {
      model: 'opus',
      specialization: 'APIs, microservices, distributed architecture',
      skills: ['api-design-principles', 'architecture-patterns', 'resilience-patterns']
    },
    'database-expert': {
      model: 'opus',
      specialization: 'Schema design, query optimization, scaling',
      skills: ['architecture-patterns']
    },
    'security-expert': {
      model: 'opus',
      specialization: 'OWASP, compliance, threat modeling',
      skills: ['nestjs-code-reviewer']
    },
    'frontend-expert': {
      model: 'sonnet',
      specialization: 'React/Next.js, performance, UI/UX',
      skills: ['react-best-practices', 'frontend-design']
    },
    'devops-expert': {
      model: 'sonnet',
      specialization: 'CI/CD, containers, infrastructure',
      skills: []
    },
    'testing-expert': {
      model: 'sonnet',
      specialization: 'TDD, testing strategy, quality',
      skills: ['workflow/tdd', 'quality-gates/systematic-debugging']
    },
    'product-expert': {
      model: 'opus',
      specialization: 'Product discovery, feature prioritization, roadmap planning',
      skills: ['product/product-discovery', 'product/feature-prioritization']
    },
    'ux-expert': {
      model: 'sonnet',
      specialization: 'UX research, UI design, wireframes, design systems, accessibility',
      skills: ['product/ux-research', 'product/design-system']
    },
    'data-expert': {
      model: 'sonnet',
      specialization: 'Analytics, data pipelines, metrics, dashboards, A/B testing',
      skills: ['data/analytics-setup', 'data/data-pipeline-design']
    },
    'devrel-expert': {
      model: 'sonnet',
      specialization: 'API documentation, developer portals, SDK design, technical writing',
      skills: ['devrel/api-documentation', 'devrel/developer-portal']
    }
  };
}

/**
 * Post-consultation flow
 *
 * Offers implementation, planning, or additional consultation
 */
function getPostConsultationActions(consultationResult) {
  return {
    actions: [
      {
        key: 'implement',
        label: 'Implement this solution',
        description: 'Start brainstorming → planning → implementation workflow',
        workflow: 'brainstorming'
      },
      {
        key: 'plan',
        label: 'Create implementation plan',
        description: 'Break down into executable tasks (2-5 min each)',
        workflow: 'writing-plans'
      },
      {
        key: 'clarify',
        label: 'Ask follow-up question',
        description: 'Get more details or alternative approaches'
      },
      {
        key: 'done',
        label: 'Done - just consulting',
        description: 'No further action needed'
      }
    ]
  };
}

/**
 * Format consultation result for display
 */
function formatResult(consultationRequest) {
  const lines = [];

  lines.push('# Consultation Request Prepared');
  lines.push('');
  lines.push(`**Query**: ${consultationRequest.query}`);
  lines.push(`**Mode**: ${consultationRequest.mode}`);
  lines.push(`**Experts**: ${consultationRequest.experts.join(', ')}`);
  lines.push('');

  if (consultationRequest.projectContext) {
    lines.push('**Project Context**:');
    lines.push(`- Framework: ${consultationRequest.projectContext.framework}`);
    lines.push(`- Language: ${consultationRequest.projectContext.language}`);
    if (consultationRequest.projectContext.database[0] !== 'unknown') {
      lines.push(`- Database: ${consultationRequest.projectContext.database.join(', ')}`);
    }
    lines.push('');
  }

  lines.push('**Skills Injected**:');
  consultationRequest.experts.forEach(expert => {
    const prompt = consultationRequest.prompts[expert];
    if (prompt.skillsLoaded.length > 0) {
      lines.push(`- ${expert}: ${prompt.skillsLoaded.join(', ')}`);
    } else {
      lines.push(`- ${expert}: No specific skills`);
    }
  });
  lines.push('');

  lines.push('**Reasoning**: ' + consultationRequest.reasoning);
  lines.push('');

  return lines.join('\n');
}

module.exports = {
  consult,
  preview,
  getAvailableExperts,
  getPostConsultationActions,
  formatResult,
  // Re-export utilities
  scanProjectContext,
  selectExperts,
  consolidateResponses
};
