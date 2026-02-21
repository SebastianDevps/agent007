/**
 * Ralph Loop Wrapper - Implementation
 *
 * Transforms any skill into a self-correcting iterative loop.
 * Inspired by the Ralph Wiggum technique from Claude Code.
 *
 * @see https://github.com/anthropics/claude-code/tree/main/plugins/ralph-wiggum
 */

import { execSync } from 'child_process';
import { readFileSync, appendFileSync, existsSync } from 'fs';
import { randomUUID } from 'crypto';

// ============================================================================
// TYPES
// ============================================================================

export interface RalphConfig {
  /** Which skill to wrap in the loop */
  skill: string;

  /** Maximum iterations before aborting (REQUIRED, no default) */
  maxIterations: number;

  /** Maximum cost in USD before aborting (REQUIRED, no default) */
  maxCostUSD: number;

  /** String to detect in output that signals completion */
  completionPromise: string;

  /** Optional command to run for verification (e.g., 'npm test') */
  verificationCommand?: string;

  /** Number of stalled iterations before aborting (default: 5) */
  stallDetectionThreshold?: number;

  /** If stalled, escalate to systematic-debugging? (default: false) */
  escalateToDeepDebug?: boolean;

  /** Original user prompt */
  initialPrompt: string;

  /** Inject context (git diff, test output) into prompt? (default: true) */
  contextInjection?: boolean;
}

export type RalphResultStatus = 'COMPLETED' | 'ABORTED' | 'ERROR';

export type RalphAbortReason =
  | 'MAX_ITERATIONS'
  | 'COST_LIMIT'
  | 'STALL_DETECTED'
  | 'SAME_ERROR_5X'
  | 'PROHIBITED_PATH_MODIFIED'
  | 'DAILY_BUDGET_EXCEEDED';

export interface RalphResult {
  status: RalphResultStatus;
  iterations: number;
  costUSD: number;
  durationSeconds: number;

  // For COMPLETED
  output?: string;
  verificationPassed?: boolean;

  // For ABORTED
  abortReason?: RalphAbortReason;
  lastOutput?: string;
  details?: any;

  // For ERROR
  error?: string;
}

export interface RalphMetrics {
  loopId: string;
  skill: string;
  taskType: string;

  startTime: Date;
  endTime: Date;

  status: RalphResultStatus;
  abortReason?: RalphAbortReason;

  iterations: number;
  costUSD: number;
  durationSeconds: number;

  filesModified: number;
  testsFixed: number;

  completionPromiseDetected: boolean;
  verificationPassed: boolean;
}

interface IterationState {
  number: number;
  filesChanged: number;
  testOutput: string | null;
  error: string | null;
  costIncrement: number;
}

// ============================================================================
// CONFIGURATION & CONSTANTS
// ============================================================================

const PROHIBITED_PATHS = [
  'src/auth/',
  'src/payments/',
  'migrations/',
  '.env',
  '.env.local',
  '.env.production',
  'secrets/',
];

const ABSOLUTE_MAX_ITERATIONS = 50;
const ABSOLUTE_MAX_COST_USD = 10.0;
const DAILY_BUDGET_USD = 50.0;

const METRICS_PATH = '.claude/metrics/ralph-loops.jsonl';

// ============================================================================
// RALPH LOOP WRAPPER CLASS
// ============================================================================

export class RalphLoopWrapper {
  private iteration = 0;
  private costAccumulator = 0;
  private fileChangesHistory: number[] = [];
  private lastError: string | null = null;
  private errorRepeatCount = 0;
  private iterationHistory: IterationState[] = [];
  private startTime: Date = new Date();
  private loopId: string = randomUUID();

  /**
   * Main entry point: run a skill in a Ralph loop
   */
  async run(config: RalphConfig): Promise<RalphResult> {
    console.log(`\n${'='.repeat(60)}`);
    console.log(`🔄 RALPH LOOP START`);
    console.log(`${'='.repeat(60)}`);
    console.log(`Loop ID: ${this.loopId}`);
    console.log(`Skill: ${config.skill}`);
    console.log(`Max Iterations: ${config.maxIterations}`);
    console.log(`Max Cost: $${config.maxCostUSD}`);
    console.log(`Completion Promise: "${config.completionPromise}"`);
    console.log(`${'='.repeat(60)}\n`);

    // Validate config
    this.validateConfig(config);

    // Check daily budget
    const dailyCost = this.getDailyCost();
    if (dailyCost >= DAILY_BUDGET_USD) {
      return this.abort(config, 'DAILY_BUDGET_EXCEEDED', {
        dailyCost,
        budget: DAILY_BUDGET_USD,
      });
    }

    // Main loop
    while (this.iteration < config.maxIterations) {
      this.iteration++;

      console.log(`\n${'─'.repeat(60)}`);
      console.log(`📍 Iteration ${this.iteration}/${config.maxIterations}`);
      console.log(`${'─'.repeat(60)}\n`);

      // 1. Build enriched prompt
      const prompt = this.buildPrompt(config);

      // 2. Execute skill
      const skillOutput = await this.executeSkill(config.skill, prompt);

      // 3. Accumulate cost
      this.costAccumulator += skillOutput.cost;
      console.log(`💰 Cost this iteration: $${skillOutput.cost.toFixed(4)}`);
      console.log(`💰 Total cost: $${this.costAccumulator.toFixed(4)} / $${config.maxCostUSD}`);

      // Check cost limit
      if (this.costAccumulator > config.maxCostUSD) {
        return this.abort(config, 'COST_LIMIT', {
          cost: this.costAccumulator,
          limit: config.maxCostUSD,
        });
      }

      // Warn at 80%
      if (this.costAccumulator > config.maxCostUSD * 0.8) {
        console.warn(`⚠️  Cost at 80% of limit!`);
      }

      // 4. Check for completion promise
      const hasCompletion = this.detectCompletion(
        skillOutput.content,
        config.completionPromise
      );

      if (hasCompletion) {
        console.log(`\n✅ Completion promise detected!`);
      }

      // 5. Run verification (if configured)
      let verificationResult = null;
      if (config.verificationCommand) {
        verificationResult = await this.runVerification(config.verificationCommand);

        if (verificationResult.passed) {
          console.log(`✅ Verification PASSED`);
        } else {
          console.log(`❌ Verification FAILED`);
          console.log(`Error: ${verificationResult.error?.substring(0, 200)}...`);
        }
      }

      // If BOTH completion promise AND verification passed, we're done!
      if (hasCompletion && (!verificationResult || verificationResult.passed)) {
        return this.complete(config, skillOutput.content, verificationResult?.passed ?? true);
      }

      // 6. Check for prohibited path modifications
      const prohibitedViolation = await this.checkProhibitedPaths();
      if (prohibitedViolation) {
        return this.abort(config, 'PROHIBITED_PATH_MODIFIED', {
          files: prohibitedViolation,
        });
      }

      // 7. Track file changes
      const filesChanged = await this.countFilesChanged();
      this.fileChangesHistory.push(filesChanged);
      console.log(`📝 Files modified: ${filesChanged}`);

      // 8. Check for stall
      const threshold = config.stallDetectionThreshold ?? 5;
      if (this.isStalled(threshold)) {
        console.warn(`⚠️  STALL DETECTED (${threshold} iterations with no progress)`);

        // Escalate to deep debug?
        if (config.escalateToDeepDebug && config.skill === 'tdd') {
          console.log(`🔍 Escalating to systematic-debugging...`);
          return await this.escalateToDeepDebug(config);
        }

        return this.abort(config, 'STALL_DETECTED', {
          iterations: threshold,
          reason: 'No file changes in last iterations',
        });
      }

      // 9. Check for repeated errors
      if (verificationResult && !verificationResult.passed) {
        const currentError = verificationResult.error;

        if (this.lastError === currentError) {
          this.errorRepeatCount++;
          console.warn(`⚠️  Same error repeated ${this.errorRepeatCount} times`);

          if (this.errorRepeatCount >= 5) {
            return this.abort(config, 'SAME_ERROR_5X', {
              error: this.lastError,
              iterations: this.iteration,
            });
          }
        } else {
          this.lastError = currentError;
          this.errorRepeatCount = 1;
        }
      }

      // 10. Record iteration state
      this.iterationHistory.push({
        number: this.iteration,
        filesChanged,
        testOutput: verificationResult?.output ?? null,
        error: verificationResult?.error ?? null,
        costIncrement: skillOutput.cost,
      });

      // 11. Small sleep to avoid rate limits
      await this.sleep(500);

      // Warn at 90% iterations
      if (this.iteration >= config.maxIterations * 0.9) {
        console.warn(`⚠️  Iteration at 90% of limit!`);
      }
    }

    // Max iterations reached
    return this.abort(config, 'MAX_ITERATIONS', {
      iterations: this.iteration,
      lastOutput: this.iterationHistory[this.iterationHistory.length - 1]?.testOutput,
    });
  }

  // ==========================================================================
  // VALIDATION
  // ==========================================================================

  private validateConfig(config: RalphConfig): void {
    if (!config.maxIterations) {
      throw new Error('Ralph: maxIterations is REQUIRED (no default allowed)');
    }

    if (!config.maxCostUSD) {
      throw new Error('Ralph: maxCostUSD is REQUIRED (no default allowed)');
    }

    if (config.maxIterations > ABSOLUTE_MAX_ITERATIONS) {
      throw new Error(
        `Ralph: maxIterations (${config.maxIterations}) exceeds absolute max (${ABSOLUTE_MAX_ITERATIONS})`
      );
    }

    if (config.maxCostUSD > ABSOLUTE_MAX_COST_USD) {
      throw new Error(
        `Ralph: maxCostUSD ($${config.maxCostUSD}) exceeds absolute max ($${ABSOLUTE_MAX_COST_USD})`
      );
    }

    if (!config.skill) {
      throw new Error('Ralph: skill is required');
    }

    if (!config.initialPrompt) {
      throw new Error('Ralph: initialPrompt is required');
    }

    if (!config.completionPromise) {
      throw new Error('Ralph: completionPromise is required');
    }
  }

  // ==========================================================================
  // PROMPT BUILDING
  // ==========================================================================

  private buildPrompt(config: RalphConfig): string {
    // First iteration: use original prompt
    if (this.iteration === 1) {
      return config.initialPrompt;
    }

    // Subsequent iterations: enrich with context
    if (config.contextInjection === false) {
      return config.initialPrompt;
    }

    const lastIteration = this.iterationHistory[this.iterationHistory.length - 1];

    let contextBlock = `\n\n---\n[Ralph Loop Context - Iteration ${this.iteration}]\n\n`;
    contextBlock += `You are in a Ralph loop. This is attempt #${this.iteration}.\n\n`;
    contextBlock += `Review your previous work:\n`;

    // Git diff
    try {
      const gitDiff = execSync('git diff HEAD~1 --name-only', {
        encoding: 'utf-8',
        stdio: ['pipe', 'pipe', 'ignore'],
      }).trim();

      if (gitDiff) {
        contextBlock += `\nModified files:\n${gitDiff}\n`;
      } else {
        contextBlock += `\nNo files modified in last iteration (potential stall).\n`;
      }
    } catch {
      contextBlock += `\n(Git diff unavailable)\n`;
    }

    // Test output
    if (lastIteration?.testOutput) {
      const truncated =
        lastIteration.testOutput.length > 500
          ? lastIteration.testOutput.substring(0, 500) + '\n... (truncated)'
          : lastIteration.testOutput;

      contextBlock += `\nLast verification output:\n\`\`\`\n${truncated}\n\`\`\`\n`;
    }

    // Error analysis
    if (lastIteration?.error) {
      contextBlock += `\nLast error: ${lastIteration.error.substring(0, 200)}\n`;
    }

    // Progress tracking
    const recentChanges = this.fileChangesHistory.slice(-3);
    contextBlock += `\nFile changes (last 3 iterations): ${recentChanges.join(', ')}\n`;

    if (recentChanges.every((c) => c === 0)) {
      contextBlock += `⚠️  WARNING: No file changes detected. You may be stalled.\n`;
      contextBlock += `Try a different approach or re-read the error messages carefully.\n`;
    }

    // Guidance
    contextBlock += `\n`;
    contextBlock += `If tests are failing, read the error messages carefully and fix the root cause.\n`;
    contextBlock += `If you're stuck on the same error, try a completely different approach.\n`;
    contextBlock += `\n`;
    contextBlock += `When ALL requirements are met, output ${config.completionPromise}\n`;

    return config.initialPrompt + contextBlock;
  }

  // ==========================================================================
  // SKILL EXECUTION
  // ==========================================================================

  private async executeSkill(
    skill: string,
    prompt: string
  ): Promise<{ content: string; cost: number }> {
    console.log(`🚀 Executing skill: ${skill}`);

    // In real implementation, this would use the Skill tool via Claude Code
    // For now, we simulate execution

    // TODO: Replace with actual Skill tool invocation
    // const result = await invokeSkill(skill, prompt);

    // Simulated response
    const simulatedCost = 0.05 + Math.random() * 0.1; // $0.05 - $0.15

    return {
      content: `[Simulated output from ${skill}]\n${prompt}`,
      cost: simulatedCost,
    };
  }

  // ==========================================================================
  // VERIFICATION
  // ==========================================================================

  private async runVerification(
    command: string
  ): Promise<{ passed: boolean; output: string; error: string | null }> {
    console.log(`🧪 Running verification: ${command}`);

    try {
      const output = execSync(command, {
        encoding: 'utf-8',
        stdio: ['pipe', 'pipe', 'pipe'],
      });

      return {
        passed: true,
        output,
        error: null,
      };
    } catch (error: any) {
      return {
        passed: false,
        output: error.stdout || '',
        error: error.stderr || error.message,
      };
    }
  }

  // ==========================================================================
  // DETECTION
  // ==========================================================================

  private detectCompletion(content: string, promise: string): boolean {
    return content.includes(promise);
  }

  private isStalled(threshold: number): boolean {
    if (this.fileChangesHistory.length < threshold) {
      return false;
    }

    const recent = this.fileChangesHistory.slice(-threshold);
    return recent.every((count) => count === 0);
  }

  private async checkProhibitedPaths(): Promise<string[] | null> {
    try {
      const modifiedFiles = execSync('git diff HEAD~1 --name-only', {
        encoding: 'utf-8',
        stdio: ['pipe', 'pipe', 'ignore'],
      })
        .trim()
        .split('\n')
        .filter(Boolean);

      const violations = modifiedFiles.filter((file) =>
        PROHIBITED_PATHS.some((prohibited) => file.startsWith(prohibited))
      );

      return violations.length > 0 ? violations : null;
    } catch {
      return null;
    }
  }

  private async countFilesChanged(): Promise<number> {
    try {
      const output = execSync('git diff HEAD~1 --name-only | wc -l', {
        encoding: 'utf-8',
        stdio: ['pipe', 'pipe', 'ignore'],
      });

      return parseInt(output.trim(), 10) || 0;
    } catch {
      return 0;
    }
  }

  // ==========================================================================
  // COMPLETION & ABORT
  // ==========================================================================

  private complete(
    config: RalphConfig,
    output: string,
    verificationPassed: boolean
  ): RalphResult {
    const duration = this.getDuration();

    console.log(`\n${'='.repeat(60)}`);
    console.log(`✅ RALPH LOOP COMPLETED`);
    console.log(`${'='.repeat(60)}`);
    console.log(`Iterations: ${this.iteration}`);
    console.log(`Cost: $${this.costAccumulator.toFixed(4)}`);
    console.log(`Duration: ${duration}s`);
    console.log(`Verification: ${verificationPassed ? 'PASSED' : 'N/A'}`);
    console.log(`${'='.repeat(60)}\n`);

    const result: RalphResult = {
      status: 'COMPLETED',
      iterations: this.iteration,
      costUSD: this.costAccumulator,
      durationSeconds: duration,
      output,
      verificationPassed,
    };

    this.recordMetrics(config, result);
    return result;
  }

  private abort(config: RalphConfig, reason: RalphAbortReason, details: any): RalphResult {
    const duration = this.getDuration();

    console.log(`\n${'='.repeat(60)}`);
    console.log(`❌ RALPH LOOP ABORTED`);
    console.log(`${'='.repeat(60)}`);
    console.log(`Reason: ${reason}`);
    console.log(`Iterations: ${this.iteration}`);
    console.log(`Cost: $${this.costAccumulator.toFixed(4)}`);
    console.log(`Duration: ${duration}s`);
    console.log(`Details:`, JSON.stringify(details, null, 2));
    console.log(`${'='.repeat(60)}\n`);

    const result: RalphResult = {
      status: 'ABORTED',
      iterations: this.iteration,
      costUSD: this.costAccumulator,
      durationSeconds: duration,
      abortReason: reason,
      lastOutput: this.iterationHistory[this.iterationHistory.length - 1]?.testOutput || '',
      details,
    };

    this.recordMetrics(config, result);
    return result;
  }

  private async escalateToDeepDebug(config: RalphConfig): Promise<RalphResult> {
    console.log(`\n🔍 Escalating to systematic-debugging...`);
    console.log(`This will inject the 4-phase debugging template.\n`);

    // Create new config for systematic-debugging
    const debugConfig: RalphConfig = {
      ...config,
      skill: 'systematic-debugging',
      maxIterations: 10, // Fewer iterations for deep debug
      completionPromise: '<promise>BUG_FIXED</promise>',
    };

    // Reset state
    this.iteration = 0;
    this.fileChangesHistory = [];
    this.lastError = null;
    this.errorRepeatCount = 0;

    // Run deep debug loop
    return await this.run(debugConfig);
  }

  // ==========================================================================
  // METRICS
  // ==========================================================================

  private recordMetrics(config: RalphConfig, result: RalphResult): void {
    const metrics: RalphMetrics = {
      loopId: this.loopId,
      skill: config.skill,
      taskType: 'unknown', // TODO: Extract from config

      startTime: this.startTime,
      endTime: new Date(),

      status: result.status,
      abortReason: result.abortReason,

      iterations: result.iterations,
      costUSD: result.costUSD,
      durationSeconds: result.durationSeconds,

      filesModified: this.fileChangesHistory.reduce((a, b) => a + b, 0),
      testsFixed: 0, // TODO: Calculate from test output

      completionPromiseDetected: result.status === 'COMPLETED',
      verificationPassed: result.verificationPassed ?? false,
    };

    try {
      appendFileSync(METRICS_PATH, JSON.stringify(metrics) + '\n', 'utf-8');
      console.log(`📊 Metrics recorded to ${METRICS_PATH}`);
    } catch (error) {
      console.warn(`⚠️  Failed to record metrics:`, error);
    }
  }

  private getDailyCost(): number {
    if (!existsSync(METRICS_PATH)) {
      return 0;
    }

    const today = new Date().toISOString().split('T')[0]; // YYYY-MM-DD

    try {
      const lines = readFileSync(METRICS_PATH, 'utf-8').trim().split('\n');
      let total = 0;

      for (const line of lines) {
        const metrics: RalphMetrics = JSON.parse(line);
        const metricsDate = new Date(metrics.startTime).toISOString().split('T')[0];

        if (metricsDate === today) {
          total += metrics.costUSD;
        }
      }

      return total;
    } catch {
      return 0;
    }
  }

  // ==========================================================================
  // HELPERS
  // ==========================================================================

  private getDuration(): number {
    return Math.floor((new Date().getTime() - this.startTime.getTime()) / 1000);
  }

  private sleep(ms: number): Promise<void> {
    return new Promise((resolve) => setTimeout(resolve, ms));
  }
}

// ============================================================================
// FACTORY FUNCTION
// ============================================================================

/**
 * Create and run a Ralph loop
 */
export async function runRalphLoop(config: RalphConfig): Promise<RalphResult> {
  const wrapper = new RalphLoopWrapper();
  return await wrapper.run(config);
}
