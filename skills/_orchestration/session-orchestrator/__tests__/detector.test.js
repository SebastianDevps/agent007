/**
 * Tests for detector.js
 * Validates context detection logic
 */

const {
  detectContext,
  detectTaskType,
  detectRiskLevel,
  detectStack,
  detectScope,
  calculateConfidence
} = require('../lib/detector');

describe('Context Detector', () => {
  describe('detectTaskType', () => {
    test('should detect consult requests', () => {
      expect(detectTaskType('should i use redis or memcached?')).toBe('consult');
      expect(detectTaskType('what is better for authentication?')).toBe('consult');
      expect(detectTaskType('recommend a caching strategy')).toBe('consult');
    });

    test('should detect feature requests', () => {
      expect(detectTaskType('add jwt authentication')).toBe('feature');
      expect(detectTaskType('implement password reset')).toBe('feature');
      expect(detectTaskType('create a new api endpoint')).toBe('feature');
    });

    test('should detect bugs', () => {
      expect(detectTaskType('fix the login bug')).toBe('bug');
      expect(detectTaskType('users endpoint is broken')).toBe('bug');
      expect(detectTaskType('getting 500 error on payment')).toBe('bug');
    });

    test('should detect refactors', () => {
      expect(detectTaskType('refactor the auth module')).toBe('refactor');
      expect(detectTaskType('clean up the user service')).toBe('refactor');
      expect(detectTaskType('optimize database queries')).toBe('refactor');
    });

    test('should return unknown for ambiguous input', () => {
      expect(detectTaskType('hello')).toBe('unknown');
      expect(detectTaskType('help me')).toBe('unknown');
    });
  });

  describe('detectRiskLevel', () => {
    test('should detect high risk for auth/payment implementations', () => {
      // v3.0: Conservative risk detection - JWT auth is high (not critical) unless combined with other factors
      expect(detectRiskLevel('add jwt authentication')).toBe('high');
      expect(detectRiskLevel('implement payment processing')).toBe('high');
      expect(detectRiskLevel('update password encryption')).toBe('high');
    });

    test('should detect medium risk for database migrations', () => {
      // v3.0: Database migrations without other risk factors are medium
      expect(detectRiskLevel('database migration for users')).toBe('medium');
    });

    test('should detect low risk for simple features', () => {
      // v3.0: Simple features without complexity triggers remain low risk
      expect(detectRiskLevel('create new api endpoint')).toBe('low');
      expect(detectRiskLevel('add validation middleware')).toBe('low');
      expect(detectRiskLevel('optimize database query')).toBe('low');
      expect(detectRiskLevel('create new dto')).toBe('low');
      expect(detectRiskLevel('update user service')).toBe('low');
      expect(detectRiskLevel('add unit tests')).toBe('low');
      expect(detectRiskLevel('update readme')).toBe('low');
    });

    test('should detect medium risk for bugs', () => {
      // v3.0: Bugs have base risk of medium
      expect(detectRiskLevel('fix typo')).toBe('medium');
    });

    test('should detect critical risk for auth/payment + scope factors', () => {
      // v3.0: Critical = critical complexity (+2) + scope factor (+1) = +3 levels
      expect(detectRiskLevel('add jwt authentication affecting multiple modules')).toBe('critical');
      expect(detectRiskLevel('add payment processing with multiple services affected')).toBe('critical');
      expect(detectRiskLevel('implement oauth for core architecture')).toBe('critical');
    });
  });

  describe('detectStack', () => {
    test('should detect NestJS stack', () => {
      const result = detectStack('implement nestjs controller');
      expect(result).toContain('nestjs');
    });

    test('should detect multiple technologies', () => {
      const result = detectStack('add typeorm entity with postgresql');
      expect(result).toContain('typeorm');
      expect(result).toContain('postgresql');
    });

    test('should detect React', () => {
      const result = detectStack('create react component');
      expect(result).toContain('react');
    });

    test('should return general for unknown stack', () => {
      const result = detectStack('do something');
      expect(result).toEqual(['general']);
    });
  });

  describe('detectScope', () => {
    test('should detect small scope', () => {
      expect(detectScope('quick fix for typo')).toBe('small');
      expect(detectScope('simple change to readme')).toBe('small');
    });

    test('should detect large scope', () => {
      expect(detectScope('refactor entire auth module')).toBe('large');
      expect(detectScope('complex migration to microservices')).toBe('large');
    });

    test('should default to medium scope', () => {
      expect(detectScope('add new feature')).toBe('medium');
    });
  });

  describe('calculateConfidence', () => {
    test('short input with strong keywords gets high score', () => {
      // 'fix bug': 2 keywords = +0.3, imperative verb = +0.15, minimal clarity = +0.05
      // Total: 0.4 + 0.3 + 0.15 + 0.05 = 0.90
      const result = calculateConfidence('fix bug');
      expect(result).toBeGreaterThanOrEqual(0.7);
    });

    test('moderate input with specificity gets high confidence', () => {
      // Same keywords as above, still high score
      const result = calculateConfidence('fix the login bug');
      expect(result).toBeGreaterThan(0.5);
    });

    test('detailed input with multiple keywords gets very high confidence', () => {
      const input = 'implement jwt authentication with refresh tokens for the api';
      // Multiple strong keywords + imperative + specificity
      const result = calculateConfidence(input);
      expect(result).toBeGreaterThanOrEqual(0.8);
    });

    test('ambiguous short input gets lower confidence', () => {
      // 'hello': 0 keywords, no structure, no clarity
      const result = calculateConfidence('hello');
      expect(result).toBeLessThan(0.6);
    });
  });

  describe('detectContext (integration)', () => {
    test('should detect complete context for feature request', () => {
      const result = detectContext('Add JWT authentication to NestJS API');

      expect(result.taskType).toBe('feature');
      expect(result.riskLevel).toBe('high'); // v3.0: JWT auth without additional factors is high
      expect(result.stack).toContain('jwt');
      expect(result.stack).toContain('nestjs');
      expect(result.confidence).toBeGreaterThan(0.5);
    });

    test('should detect complete context for bug', () => {
      const result = detectContext('Fix 500 error in users endpoint');

      expect(result.taskType).toBe('bug');
      expect(result.riskLevel).toBe('medium'); // v3.0: Bugs have base medium risk
      expect(result.confidence).toBeGreaterThan(0.5);
    });

    test('should detect complete context for consult', () => {
      const result = detectContext('Should I use Redis or in-memory cache?');

      expect(result.taskType).toBe('consult');
      expect(result.stack).toContain('redis');
    });
  });
});
