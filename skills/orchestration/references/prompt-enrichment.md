---
name: ralph-loop-wrapper/prompt-enrichment
description: Prompt enrichment templates for Ralph iterations — first attempt vs subsequent attempts
---

# Prompt Enrichment

Ralph enriches prompts with context from previous iterations.

## Iteration 1 (First Attempt)

```
[Original user prompt - unchanged]
```

## Iteration 2+ (Subsequent Attempts)

```
[Original user prompt]

---
[Ralph Loop Context - Iteration N]

You are in a Ralph loop. This is attempt #N.

Review your previous work:
- Modified files: `git diff HEAD~1 --name-only`
- Test output:
  ```
  [Last npm test output]
  ```
- Git history: `git log --oneline -5`

Analysis:
- Files changed in iteration N-1: [count]
- Tests status: [X passing, Y failing]
- Last error: [error message if any]

If tests are failing, read the error messages carefully and fix the root cause.
If you're stuck on the same error, try a different approach.

When ALL requirements are met, output <promise>COMPLETE</promise>.
```
