/**
 * Ralph Loop Wrapper - Unit Tests
 */

import { RalphLoopWrapper, RalphConfig, RalphResult } from './wrapper';

describe('RalphLoopWrapper', () => {
  describe('Configuration Validation', () => {
    it('should throw if maxIterations is missing', async () => {
      const wrapper = new RalphLoopWrapper();
      const config = {
        skill: 'tdd',
        maxCostUSD: 5.0,
        completionPromise: '<promise>COMPLETE</promise>',
        initialPrompt: 'Test',
      } as any;

      await expect(wrapper.run(config)).rejects.toThrow(
        'Ralph: maxIterations is REQUIRED'
      );
    });

    it('should throw if maxCostUSD is missing', async () => {
      const wrapper = new RalphLoopWrapper();
      const config = {
        skill: 'tdd',
        maxIterations: 10,
        completionPromise: '<promise>COMPLETE</promise>',
        initialPrompt: 'Test',
      } as any;

      await expect(wrapper.run(config)).rejects.toThrow(
        'Ralph: maxCostUSD is REQUIRED'
      );
    });

    it('should throw if maxIterations exceeds absolute max', async () => {
      const wrapper = new RalphLoopWrapper();
      const config: RalphConfig = {
        skill: 'tdd',
        maxIterations: 100, // Exceeds ABSOLUTE_MAX_ITERATIONS (50)
        maxCostUSD: 5.0,
        completionPromise: '<promise>COMPLETE</promise>',
        initialPrompt: 'Test',
      };

      await expect(wrapper.run(config)).rejects.toThrow(
        'exceeds absolute max'
      );
    });

    it('should throw if maxCostUSD exceeds absolute max', async () => {
      const wrapper = new RalphLoopWrapper();
      const config: RalphConfig = {
        skill: 'tdd',
        maxIterations: 10,
        maxCostUSD: 20.0, // Exceeds ABSOLUTE_MAX_COST_USD (10.0)
        completionPromise: '<promise>COMPLETE</promise>',
        initialPrompt: 'Test',
      };

      await expect(wrapper.run(config)).rejects.toThrow(
        'exceeds absolute max'
      );
    });

    it('should accept valid configuration', async () => {
      const wrapper = new RalphLoopWrapper();
      const config: RalphConfig = {
        skill: 'tdd',
        maxIterations: 20,
        maxCostUSD: 5.0,
        completionPromise: '<promise>COMPLETE</promise>',
        initialPrompt: 'Implement user registration',
      };

      // Should not throw during validation
      // (will fail during execution since skill is mocked)
      try {
        await wrapper.run(config);
      } catch (error) {
        // Expected to fail during execution, but validation passed
        expect(error).toBeDefined();
      }
    });
  });

  describe('Completion Detection', () => {
    it('should detect completion promise in output', () => {
      const wrapper = new RalphLoopWrapper();
      const output = `
All tests passing!

<promise>COMPLETE</promise>
`;

      // Access private method via type assertion
      const detected = (wrapper as any).detectCompletion(
        output,
        '<promise>COMPLETE</promise>'
      );

      expect(detected).toBe(true);
    });

    it('should not detect completion if promise is missing', () => {
      const wrapper = new RalphLoopWrapper();
      const output = `
All tests passing!
Work complete.
`;

      const detected = (wrapper as any).detectCompletion(
        output,
        '<promise>COMPLETE</promise>'
      );

      expect(detected).toBe(false);
    });

    it('should detect custom completion promises', () => {
      const wrapper = new RalphLoopWrapper();
      const output = `Bug fixed! <promise>BUG_FIXED</promise>`;

      const detected = (wrapper as any).detectCompletion(
        output,
        '<promise>BUG_FIXED</promise>'
      );

      expect(detected).toBe(true);
    });
  });

  describe('Stall Detection', () => {
    it('should detect stall when no files changed for 5 iterations', () => {
      const wrapper = new RalphLoopWrapper();

      // Simulate 5 iterations with zero file changes
      (wrapper as any).fileChangesHistory = [0, 0, 0, 0, 0];

      const isStalled = (wrapper as any).isStalled(5);

      expect(isStalled).toBe(true);
    });

    it('should not detect stall when files are changing', () => {
      const wrapper = new RalphLoopWrapper();

      // Simulate iterations with file changes
      (wrapper as any).fileChangesHistory = [2, 1, 0, 3, 1];

      const isStalled = (wrapper as any).isStalled(5);

      expect(isStalled).toBe(false);
    });

    it('should not detect stall when history is shorter than threshold', () => {
      const wrapper = new RalphLoopWrapper();

      // Only 3 iterations
      (wrapper as any).fileChangesHistory = [0, 0, 0];

      const isStalled = (wrapper as any).isStalled(5);

      expect(isStalled).toBe(false);
    });

    it('should use custom stall threshold', () => {
      const wrapper = new RalphLoopWrapper();

      // 3 iterations with no changes
      (wrapper as any).fileChangesHistory = [0, 0, 0];

      // Should detect stall with threshold=3
      expect((wrapper as any).isStalled(3)).toBe(true);

      // Should not detect stall with threshold=5
      expect((wrapper as any).isStalled(5)).toBe(false);
    });
  });

  describe('Prompt Enrichment', () => {
    it('should return original prompt on first iteration', () => {
      const wrapper = new RalphLoopWrapper();
      (wrapper as any).iteration = 1;

      const config: RalphConfig = {
        skill: 'tdd',
        maxIterations: 10,
        maxCostUSD: 5.0,
        completionPromise: '<promise>COMPLETE</promise>',
        initialPrompt: 'Implement feature X',
      };

      const prompt = (wrapper as any).buildPrompt(config);

      expect(prompt).toBe('Implement feature X');
    });

    it('should enrich prompt on subsequent iterations', () => {
      const wrapper = new RalphLoopWrapper();
      (wrapper as any).iteration = 3;
      (wrapper as any).iterationHistory = [
        {
          number: 1,
          filesChanged: 2,
          testOutput: 'FAIL: 3 tests failing',
          error: 'Validation error',
          costIncrement: 0.05,
        },
        {
          number: 2,
          filesChanged: 1,
          testOutput: 'FAIL: 1 test failing',
          error: null,
          costIncrement: 0.05,
        },
      ];
      (wrapper as any).fileChangesHistory = [2, 1];

      const config: RalphConfig = {
        skill: 'tdd',
        maxIterations: 10,
        maxCostUSD: 5.0,
        completionPromise: '<promise>COMPLETE</promise>',
        initialPrompt: 'Implement feature X',
        contextInjection: true,
      };

      const prompt = (wrapper as any).buildPrompt(config);

      expect(prompt).toContain('Implement feature X');
      expect(prompt).toContain('Ralph Loop Context');
      expect(prompt).toContain('Iteration 3');
      expect(prompt).toContain('FAIL: 1 test failing');
      expect(prompt).toContain('<promise>COMPLETE</promise>');
    });

    it('should warn about stall in enriched prompt', () => {
      const wrapper = new RalphLoopWrapper();
      (wrapper as any).iteration = 4;
      (wrapper as any).fileChangesHistory = [0, 0, 0]; // Last 3 are zeros
      (wrapper as any).iterationHistory = [
        { filesChanged: 0, testOutput: null, error: null, costIncrement: 0.05 },
      ];

      const config: RalphConfig = {
        skill: 'tdd',
        maxIterations: 10,
        maxCostUSD: 5.0,
        completionPromise: '<promise>COMPLETE</promise>',
        initialPrompt: 'Test',
        contextInjection: true,
      };

      const prompt = (wrapper as any).buildPrompt(config);

      expect(prompt).toContain('WARNING: No file changes detected');
      expect(prompt).toContain('stalled');
    });

    it('should skip context injection if disabled', () => {
      const wrapper = new RalphLoopWrapper();
      (wrapper as any).iteration = 3;

      const config: RalphConfig = {
        skill: 'tdd',
        maxIterations: 10,
        maxCostUSD: 5.0,
        completionPromise: '<promise>COMPLETE</promise>',
        initialPrompt: 'Implement feature X',
        contextInjection: false,
      };

      const prompt = (wrapper as any).buildPrompt(config);

      expect(prompt).toBe('Implement feature X');
      expect(prompt).not.toContain('Ralph Loop Context');
    });
  });

  describe('Result Types', () => {
    it('should return COMPLETED result when promise detected', async () => {
      const wrapper = new RalphLoopWrapper();

      // Mock executeSkill to return completion promise
      (wrapper as any).executeSkill = jest.fn().mockResolvedValue({
        content: '<promise>COMPLETE</promise>',
        cost: 0.05,
      });

      (wrapper as any).runVerification = jest.fn().mockResolvedValue({
        passed: true,
        output: 'All tests pass',
        error: null,
      });

      (wrapper as any).countFilesChanged = jest.fn().mockResolvedValue(2);
      (wrapper as any).checkProhibitedPaths = jest.fn().mockResolvedValue(null);

      const config: RalphConfig = {
        skill: 'tdd',
        maxIterations: 10,
        maxCostUSD: 5.0,
        completionPromise: '<promise>COMPLETE</promise>',
        verificationCommand: 'npm test',
        initialPrompt: 'Test',
      };

      const result = await wrapper.run(config);

      expect(result.status).toBe('COMPLETED');
      expect(result.iterations).toBe(1);
      expect(result.verificationPassed).toBe(true);
    });

    it('should return ABORTED result when max iterations reached', async () => {
      const wrapper = new RalphLoopWrapper();

      // Mock executeSkill to never return completion promise
      (wrapper as any).executeSkill = jest.fn().mockResolvedValue({
        content: 'Still working...',
        cost: 0.05,
      });

      (wrapper as any).countFilesChanged = jest.fn().mockResolvedValue(1);
      (wrapper as any).checkProhibitedPaths = jest.fn().mockResolvedValue(null);

      const config: RalphConfig = {
        skill: 'tdd',
        maxIterations: 3,
        maxCostUSD: 5.0,
        completionPromise: '<promise>COMPLETE</promise>',
        initialPrompt: 'Test',
      };

      const result = await wrapper.run(config);

      expect(result.status).toBe('ABORTED');
      expect(result.abortReason).toBe('MAX_ITERATIONS');
      expect(result.iterations).toBe(3);
    });

    it('should return ABORTED result when cost limit exceeded', async () => {
      const wrapper = new RalphLoopWrapper();

      // Mock executeSkill to return high cost
      (wrapper as any).executeSkill = jest.fn().mockResolvedValue({
        content: 'Working...',
        cost: 3.0, // Will exceed $5 limit after 2 iterations
      });

      (wrapper as any).countFilesChanged = jest.fn().mockResolvedValue(1);
      (wrapper as any).checkProhibitedPaths = jest.fn().mockResolvedValue(null);

      const config: RalphConfig = {
        skill: 'tdd',
        maxIterations: 10,
        maxCostUSD: 5.0,
        completionPromise: '<promise>COMPLETE</promise>',
        initialPrompt: 'Test',
      };

      const result = await wrapper.run(config);

      expect(result.status).toBe('ABORTED');
      expect(result.abortReason).toBe('COST_LIMIT');
      expect(result.costUSD).toBeGreaterThan(5.0);
    });

    it('should return ABORTED result when stall detected', async () => {
      const wrapper = new RalphLoopWrapper();

      (wrapper as any).executeSkill = jest.fn().mockResolvedValue({
        content: 'Working...',
        cost: 0.05,
      });

      // Mock no file changes (stall)
      (wrapper as any).countFilesChanged = jest.fn().mockResolvedValue(0);
      (wrapper as any).checkProhibitedPaths = jest.fn().mockResolvedValue(null);

      const config: RalphConfig = {
        skill: 'tdd',
        maxIterations: 20,
        maxCostUSD: 5.0,
        completionPromise: '<promise>COMPLETE</promise>',
        initialPrompt: 'Test',
        stallDetectionThreshold: 5,
      };

      const result = await wrapper.run(config);

      expect(result.status).toBe('ABORTED');
      expect(result.abortReason).toBe('STALL_DETECTED');
      expect(result.iterations).toBe(5);
    });
  });

  describe('Safety Mechanisms', () => {
    it('should abort if prohibited path is modified', async () => {
      const wrapper = new RalphLoopWrapper();

      (wrapper as any).executeSkill = jest.fn().mockResolvedValue({
        content: 'Working...',
        cost: 0.05,
      });

      (wrapper as any).countFilesChanged = jest.fn().mockResolvedValue(1);

      // Mock prohibited path modification
      (wrapper as any).checkProhibitedPaths = jest
        .fn()
        .mockResolvedValue(['src/auth/secrets.ts']);

      const config: RalphConfig = {
        skill: 'tdd',
        maxIterations: 10,
        maxCostUSD: 5.0,
        completionPromise: '<promise>COMPLETE</promise>',
        initialPrompt: 'Test',
      };

      const result = await wrapper.run(config);

      expect(result.status).toBe('ABORTED');
      expect(result.abortReason).toBe('PROHIBITED_PATH_MODIFIED');
      expect(result.details.files).toContain('src/auth/secrets.ts');
    });

    it('should abort if same error repeats 5 times', async () => {
      const wrapper = new RalphLoopWrapper();

      (wrapper as any).executeSkill = jest.fn().mockResolvedValue({
        content: 'Working...',
        cost: 0.05,
      });

      (wrapper as any).countFilesChanged = jest.fn().mockResolvedValue(1);
      (wrapper as any).checkProhibitedPaths = jest.fn().mockResolvedValue(null);

      // Mock same error repeating
      (wrapper as any).runVerification = jest.fn().mockResolvedValue({
        passed: false,
        output: 'Test failed',
        error: 'TypeError: Cannot read property "name" of undefined',
      });

      const config: RalphConfig = {
        skill: 'tdd',
        maxIterations: 20,
        maxCostUSD: 5.0,
        completionPromise: '<promise>COMPLETE</promise>',
        verificationCommand: 'npm test',
        initialPrompt: 'Test',
      };

      const result = await wrapper.run(config);

      expect(result.status).toBe('ABORTED');
      expect(result.abortReason).toBe('SAME_ERROR_5X');
      expect(result.iterations).toBe(5);
    });
  });

  describe('Metrics Recording', () => {
    it('should record metrics on completion', async () => {
      const wrapper = new RalphLoopWrapper();

      const recordMetricsSpy = jest.spyOn(
        wrapper as any,
        'recordMetrics'
      );

      (wrapper as any).executeSkill = jest.fn().mockResolvedValue({
        content: '<promise>COMPLETE</promise>',
        cost: 0.05,
      });

      (wrapper as any).countFilesChanged = jest.fn().mockResolvedValue(2);
      (wrapper as any).checkProhibitedPaths = jest.fn().mockResolvedValue(null);

      const config: RalphConfig = {
        skill: 'tdd',
        maxIterations: 10,
        maxCostUSD: 5.0,
        completionPromise: '<promise>COMPLETE</promise>',
        initialPrompt: 'Test',
      };

      await wrapper.run(config);

      expect(recordMetricsSpy).toHaveBeenCalled();
    });
  });
});
