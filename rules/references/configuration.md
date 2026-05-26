---
name: context-awareness/configuration
description: Configuration schema, logging shape, validation rules, and user override semantics.
---

# Configuration & Logging

## Context Logging

Every context detection is logged for observability:

```json
{
  "timestamp": "2026-02-06T10:30:00Z",
  "userInput": "Add JWT refresh token rotation",
  "context": {
    "taskType": "feature",
    "risk": "critical",
    "stack": ["nestjs", "typeorm"],
    "scope": "multi-module",
    "riskFactors": {
      "touchesAuth": true,
      "pathContains": ["auth"]
    }
  },
  "workflowRouted": "feature-development-critical",
  "estimatedDuration": "2-4 hours"
}
```

---

## Validation Rules

### Rule 1: Always Detect Context

**NEVER proceed without context detection.**

```diff
- ❌ User: "Add validation"
     Agent: [Starts coding immediately]

+ ✅ User: "Add validation"
     Agent: [Detects context]
     Context: feature, low risk, nestjs
     Workflow: feature-development-fast-track
     [Proceeds with appropriate pipeline]
```

### Rule 2: Explicit Risk Confirmation for Critical

**ALWAYS confirm with user for critical risk tasks.**

```typescript
if (context.risk === 'critical') {
  await askUserConfirmation(
    `This task touches ${context.riskFactors.criticalAreas.join(', ')}. ` +
    `I'll use the critical pipeline with manual approval gates. Proceed?`
  );
}
```

### Rule 3: Allow User Override

**User can override detected context if needed.**

```bash
User: "Add field to User entity --risk=low"
# Manual override: treat as low risk even if entity modification usually = medium
```

---

## orchestrator.config.json

```json
{
  "contextDetection": {
    "enabled": true,
    "customKeywords": {
      "feature": ["agregar", "implementar"],
      "bug": ["corregir", "arreglar"]
    }
  },

  "riskDetection": {
    "criticalPaths": [
      "src/auth/**",
      "src/payment/**",
      "database/migrations/**"
    ]
  },

  "autoActivation": {
    "requireConfirmation": {
      "critical": true,
      "high": false,
      "medium": false,
      "low": false
    }
  }
}
```

---

## Auto-injection Metadata

- **Auto-injected in**: ALL sessions, beginning of every task
- **Can be disabled**: NO (critical skill)
- **Override allowed**: YES (user can specify risk/workflow manually)
