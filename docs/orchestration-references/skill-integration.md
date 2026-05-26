---
name: ralph-loop-wrapper/skill-integration
description: How to make a skill Ralph-ready, current Ralph-ready skills, example usage, error handling, testing, future enhancements
---

# Integration with Skills

For a skill to be Ralph-ready, it must:

## 1. Support Completion Promise

```markdown
## Ralph Integration

When executed in Ralph mode, this skill outputs:

<promise>COMPLETE</promise>

when ALL acceptance criteria are met.
```

## 2. Define Success Criteria

```markdown
## Completion Criteria

- [ ] All tests pass (npm test exit code 0)
- [ ] Coverage >= 80%
- [ ] No TypeScript errors
- [ ] No `any` types in new code
```

## 3. Self-Correction Pattern

```markdown
## Self-Correction

In Ralph mode, this skill:
1. Reads test output from previous iteration
2. Identifies what's failing
3. Implements minimal fix
4. Runs verification
5. If success → outputs completion promise
6. If failure → analyzes and tries different approach
```

---

# Ralph-Ready Skills

| Skill | Completion Promise | Verification | Status |
|-------|-------------------|--------------|--------|
| `workflow/tdd` | `<promise>COMPLETE</promise>` | `npm test` | ✅ Ready |
| `quality-gates/systematic-debugging` | `<promise>BUG_FIXED</promise>` | `npm test` | ✅ Ready |
| `code-cleanup` | `<promise>LINT_CLEAN</promise>` | `npm run lint` | 🚧 TODO |

---

# Example Usage (Internal)

```typescript
// In session orchestrator:

const context = detectContext(userInput);

if (shouldActivateRalph(context)) {
  const wrapper = new RalphLoopWrapper();

  const result = await wrapper.run({
    skill: 'tdd',
    maxIterations: 20,
    maxCostUSD: 5.00,
    completionPromise: '<promise>COMPLETE</promise>',
    verificationCommand: 'npm test',
    stallDetectionThreshold: 5,
    initialPrompt: userInput
  });

  handleRalphResult(result);
}
```

---

# Error Handling

```typescript
// Graceful degradation:
try {
  return await wrapper.run(config);
} catch (error) {
  console.error('[Ralph] Wrapper failed:', error);

  // Fallback to normal (non-loop) execution
  console.log('[Ralph] Falling back to normal execution...');
  return await executeSkillNormally(config.skill, config.initialPrompt);
}
```

**Philosophy**: Ralph should never break the system. If it fails, gracefully fall back to traditional single-pass execution.

---

# Testing Ralph

```bash
# Unit tests
npm test -- ralph-loop-wrapper.spec.ts

# Integration tests with fixtures
npm test -- test-fixtures/ralph/

# Test with real TDD skill
cd test-fixtures/ralph/fixable-bug
npm test  # Should fail
# Run Ralph loop manually
# npm test  # Should now pass
```

---

# Implementation Details

See: `.claude/skills/_orchestration/ralph-loop-wrapper/wrapper.ts`

**Dependencies**: None (pure TypeScript, runs in Claude Code context)

**File Size**: ~500 lines

**Performance**: Negligible overhead (<100ms per iteration)

---

# Future Enhancements

- [ ] Parallel loops (multiple features simultaneously)
- [ ] Cost optimization (use cheaper models for iterations)
- [ ] Learning from history (analyze past loops to improve prompts)
- [ ] Multi-agent Ralph (different agents per iteration)
- [ ] Real-time dashboard (web UI showing loop progress)

---

# References

- Original Ralph technique: https://ghuntley.com/ralph/
- Claude Code plugin: https://github.com/anthropics/claude-code/tree/main/plugins/ralph-wiggum
- Session orchestrator integration: `.claude/skills/_orchestration/session-orchestrator/SKILL.md`
