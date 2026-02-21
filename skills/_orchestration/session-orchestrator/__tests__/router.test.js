/**
 * Tests for router.js
 * Validates routing logic and skill selection
 */

const {
  route,
  generateConfirmationMessage,
  shouldSkipConfirmation,
  execute
} = require('../lib/router');

describe('Workflow Router', () => {
  describe('route', () => {
    test('should route consult requests to /consult command', () => {
      const context = {
        taskType: 'consult',
        riskLevel: 'low',
        stack: ['general'],
        scope: 'medium',
        confidence: 0.8
      };

      const result = route(context, 'should I use Redis?');

      expect(result.action).toBe('invoke_command');
      expect(result.command).toBe('/consult');
      expect(result.requiresConfirmation).toBe(false);
    });

    test('should route critical features to brainstorming', () => {
      const context = {
        taskType: 'feature',
        riskLevel: 'critical',
        stack: ['jwt'],
        scope: 'medium',
        confidence: 0.9
      };

      const result = route(context, 'Add JWT authentication');

      expect(result.action).toBe('invoke_skill');
      expect(result.skill).toBe('brainstorming');
      expect(result.requiresConfirmation).toBe(true);
    });

    test('should route bugs to systematic-debugging', () => {
      const context = {
        taskType: 'bug',
        riskLevel: 'high',
        stack: ['nestjs'],
        scope: 'medium',
        confidence: 0.8
      };

      const result = route(context, 'Fix 500 error');

      expect(result.action).toBe('invoke_skill');
      expect(result.skill).toBe('systematic-debugging');
      expect(result.requiresConfirmation).toBe(false);
    });

    test('should allow low risk features to proceed', () => {
      const context = {
        taskType: 'feature',
        riskLevel: 'low',
        stack: ['general'],
        scope: 'small',
        confidence: 0.7
      };

      const result = route(context, 'Add createdAt field');

      expect(result.action).toBe('proceed');
      expect(result.requiresConfirmation).toBe(false);
    });

    test('should ask user for ambiguous input', () => {
      const context = {
        taskType: 'unknown',
        riskLevel: 'low',
        stack: ['general'],
        scope: 'medium',
        confidence: 0.3
      };

      const result = route(context, 'help');

      expect(result.action).toBe('ask_user');
      expect(result.requiresConfirmation).toBe(true);
    });

    // NEW: Product routing
    test('should route product requests to /consult', () => {
      const context = {
        taskType: 'product',
        riskLevel: 'medium',
        stack: ['general'],
        scope: 'medium',
        confidence: 0.8
      };
      const result = route(context, 'create user stories for MVP');
      expect(result.action).toBe('invoke_command');
      expect(result.command).toBe('/consult');
    });

    // NEW: Design routing
    test('should route design requests to /consult', () => {
      const context = {
        taskType: 'design',
        riskLevel: 'medium',
        stack: ['general'],
        scope: 'medium',
        confidence: 0.8
      };
      const result = route(context, 'create wireframes for onboarding');
      expect(result.action).toBe('invoke_command');
      expect(result.command).toBe('/consult');
    });

    // NEW: Analytics routing
    test('should route analytics requests to /consult', () => {
      const context = {
        taskType: 'analytics',
        riskLevel: 'low',
        stack: ['general'],
        scope: 'medium',
        confidence: 0.8
      };
      const result = route(context, 'setup analytics dashboard');
      expect(result.action).toBe('invoke_command');
      expect(result.command).toBe('/consult');
    });

    // NEW: Documentation routing
    test('should route documentation requests to api-documentation skill', () => {
      const context = {
        taskType: 'documentation',
        riskLevel: 'low',
        stack: ['general'],
        scope: 'medium',
        confidence: 0.8
      };
      const result = route(context, 'create api docs for users endpoint');
      expect(result.action).toBe('invoke_skill');
      expect(result.skill).toBe('devrel/api-documentation');
    });

    // NEW: Regression guard for all 8 task types
    test('all 8 task types produce non-ambiguous routing decisions', () => {
      const taskTypes = ['consult', 'feature', 'bug', 'refactor', 'product', 'design', 'analytics', 'documentation'];
      for (const taskType of taskTypes) {
        const context = {
          taskType,
          riskLevel: 'medium',
          stack: ['general'],
          scope: 'medium',
          confidence: 0.8
        };
        const result = route(context, `do ${taskType} task`);
        expect(result.action).not.toBe('ask_user');
      }
    });
  });

  describe('generateConfirmationMessage', () => {
    test('should generate message for brainstorming', () => {
      const routingDecision = {
        action: 'invoke_skill',
        skill: 'brainstorming',
        context: {
          taskType: 'feature',
          riskLevel: 'critical'
        },
        reason: 'Critical complexity feature'
      };

      const message = generateConfirmationMessage(routingDecision);

      expect(message).toContain('CRITICAL');
      expect(message).toContain('brainstorming');
    });

    test('should generate clarification message for ambiguous input', () => {
      const routingDecision = {
        action: 'ask_user',
        context: {
          taskType: 'unknown'
        }
      };

      const message = generateConfirmationMessage(routingDecision);

      expect(message).toContain('Consult');
      expect(message).toContain('Feature');
      expect(message).toContain('Bug');
      expect(message).toContain('Refactor');
    });
  });

  describe('shouldSkipConfirmation', () => {
    test('should skip confirmation if orchestration disabled', () => {
      const settings = {
        orchestration: {
          enabled: false
        }
      };

      const routingDecision = {
        requiresConfirmation: true,
        context: { riskLevel: 'low' }
      };

      expect(shouldSkipConfirmation(routingDecision, settings)).toBe(false);
    });

    test('should skip confirmation if rule says no confirmation needed', () => {
      const settings = {
        orchestration: {
          enabled: true,
          auto_detect: true
        }
      };

      const routingDecision = {
        requiresConfirmation: false,
        context: { riskLevel: 'low' }
      };

      expect(shouldSkipConfirmation(routingDecision, settings)).toBe(true);
    });

    test('should skip confirmation for critical risk if setting allows', () => {
      const settings = {
        orchestration: {
          enabled: true,
          auto_detect: true,
          confirmations: {
            critical_risk: false
          }
        }
      };

      const routingDecision = {
        requiresConfirmation: true,
        context: { riskLevel: 'critical' }
      };

      expect(shouldSkipConfirmation(routingDecision, settings)).toBe(true);
    });

    test('should require confirmation for critical risk by default', () => {
      const settings = {
        orchestration: {
          enabled: true,
          auto_detect: true,
          confirmations: {
            critical_risk: true
          }
        }
      };

      const routingDecision = {
        requiresConfirmation: true,
        context: { riskLevel: 'critical' }
      };

      expect(shouldSkipConfirmation(routingDecision, settings)).toBe(false);
    });
  });

  describe('execute', () => {
    test('should return command for invoke_command action', () => {
      const routingDecision = {
        action: 'invoke_command',
        command: '/consult'
      };

      const result = execute(routingDecision);

      expect(result.type).toBe('command');
      expect(result.value).toBe('/consult');
    });

    test('should return skill for invoke_skill action', () => {
      const routingDecision = {
        action: 'invoke_skill',
        skill: 'brainstorming'
      };

      const result = execute(routingDecision);

      expect(result.type).toBe('skill');
      expect(result.value).toBe('brainstorming');
    });

    test('should return proceed for direct implementation', () => {
      const routingDecision = {
        action: 'proceed'
      };

      const result = execute(routingDecision);

      expect(result.type).toBe('proceed');
      expect(result.value).toBe(null);
    });
  });
});
