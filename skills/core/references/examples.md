---
name: context-awareness/examples
description: Worked examples of context analysis and pipeline activation across all task types.
---

# Context Analysis Examples

Each example shows: user input → context analysis → routed workflow → activated pipeline.

---

## Example 1: Feature Request (critical risk)

**User Input**: "Add JWT refresh token rotation to the auth system"

**Context Analysis**:
```typescript
{
  taskType: 'feature',          // "Add" keyword
  risk: 'critical',             // Touches auth + complex feature
  stack: ['nestjs', 'typeorm'],
  scope: 'multi-module',        // Auth + tokens + middleware
  touchesCriticalPath: true,
  touchesAuth: true,

  riskFactors: {
    pathContains: ['auth'],     // ← Critical path
    touchesAuth: true,          // ← Critical indicator
    exposesNewEndpoint: true,   // /refresh endpoint
    crossContextChanges: false,
    modifiesSchema: false
  }
}
```

**Routed To**: `feature-development-critical`

**Pipeline Activated**:
1. Context Awareness (auto)
2. Brainstorming (obligatorio)
3. Security Pre-Assessment
4. Writing Detailed Plans (con rollback plan)
5. **Manual Approval Gate**
6. TDD Enforcement (muy estricto)
7. Executing Plans (step-by-step)
8. Two-Stage Review
9. Security Audit
10. Integration + E2E Tests
11. **Manual Final Approval**
12. Verification
13. Finish

---

## Example 2: Bug Fix (medium risk)

**User Input**: "Fix the N+1 query problem in /api/users endpoint"

**Context Analysis**:
```typescript
{
  taskType: 'bug',              // "Fix" keyword
  risk: 'medium',               // Performance issue, not security
  stack: ['nestjs', 'typeorm'],
  scope: 'single-module',
  touchesCriticalPath: false,   // Users endpoint, not auth
  issueType: 'performance',

  riskFactors: {
    pathContains: ['users'],
    performanceImpact: true,
    touchesEntity: true,
    fileCount: 2                // service + test
  }
}
```

**Routed To**: `bug-fixing-standard`

**Pipeline Activated**:
1. Context Awareness (auto)
2. Systematic Debugging - Phase 1: Reproduce
3. Systematic Debugging - Phase 2: Root Cause Analysis
4. Systematic Debugging - Phase 3: Hypothesis Testing
5. Writing Fix Plan
6. TDD (test → fix)
7. Verification + Regression Tests
8. Finish

---

## Example 3: Refactor (medium risk)

**User Input**: "Refactor the providers module to use Repository pattern"

**Context Analysis**:
```typescript
{
  taskType: 'refactor',         // "Refactor" keyword
  risk: 'medium',               // Module refactor, not architectural
  stack: ['nestjs', 'typeorm'],
  scope: 'module',
  touchesCriticalPath: false,
  refactorType: 'pattern-introduction',

  riskFactors: {
    fileCount: 5,
    modifiesEntity: false,
    introducesPattern: true,
    behaviorChange: false
  }
}
```

**Routed To**: `refactoring-standard`

**Pipeline Activated**:
1. Context Awareness (auto)
2. Architecture Patterns Review
3. Identify Code Smells
4. Writing Refactor Plan
5. Tests Pass Gate (before)
6. Incremental Refactoring
7. Tests Pass After Each Step
8. Code Review (NestJS patterns)
9. Coverage Verification
10. Finish

---

## Example 4: Consultation

**User Input**: "Should I use Redis or in-memory cache for session storage?"

**Context Analysis**:
```typescript
{
  taskType: 'consult',          // "Should I" pattern
  risk: 'n/a',
  stack: ['nestjs'],
  questionType: 'architecture-decision',
  requiresExpertise: ['backend', 'devops'],

  consultationContext: {
    decision: 'caching-strategy',
    options: ['redis', 'in-memory'],
    impactArea: 'session-storage'
  }
}
```

**Routed To**: `consultation-pipeline`

**Pipeline Activated**:
1. Context Awareness (auto)
2. Context Gathering (stack, scale, constraints)
3. Consult (select backend + devops experts)
4. [Optional] Transition to Implementation (if user decides)
5. Finish

---

## Example 5: Code Review

**User Input**: "Review the cutoffs module for OWASP vulnerabilities and NestJS best practices"

**Context Analysis**:
```typescript
{
  taskType: 'review',           // "Review" keyword
  risk: 'n/a',
  stack: ['nestjs', 'typeorm'],
  scope: 'module',
  reviewType: 'security + quality',

  reviewFocus: {
    security: true,
    quality: true,
    performance: false,
    architecture: false
  }
}
```

**Routed To**: `code-review-pipeline`

**Pipeline Activated**:
1. Context Awareness (auto)
2. Scope Detection (cutoffs module)
3. Two-Stage Review
   3.1 Spec Conformance (if spec available)
   3.2 Code Quality Review (NestJS patterns)
4. Security Audit (OWASP checklist)
5. Generate Report
6. [Optional] Auto-Fix Suggestions
7. Finish
