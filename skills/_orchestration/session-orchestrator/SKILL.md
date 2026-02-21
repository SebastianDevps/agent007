# Session Orchestrator

**Auto-inject**: true
**Priority**: highest
**Invokable**: false

## Purpose

The session orchestrator is the central intelligence layer for Agent007. It automatically:
- Detects task type, risk level, and technology stack from user input
- Routes consultations to `/consult` command
- Auto-invokes workflow skills for features/bugs
- Reads `when` conditions from SKILL.md files for dynamic routing
- Ensures core quality enforcement rules are always active
- Confirms with user when tasks are ambiguous or critical
- **Shows routing decisions transparently** (v3.0+)

**Version**: 3.0 (Transparent Routing)
**Status**: ✅ Fully operational with visible decision-making

---

## 🔍 ROUTING TRANSPARENCY (v3.0)

**CRITICAL**: When orchestrating ANY user request, you MUST show your detection and routing decision BEFORE executing.

### Display Format

```
🎯 **Orchestrator Decision**

**Detected**:
- Task Type: {feature|bug|consult|product|design|analytics|documentation|refactor}
- Risk Level: {low|medium|high|critical}
- Confidence: {percentage}%
- Stack Detected: {technologies if any}

**Routing Decision**:
→ {description of what will be invoked and why}

**Skills to Activate**:
- {skill-name-1} (reason)
- {skill-name-2} (reason)

---
```

### Examples

**Example 1: Feature Request**
```
🎯 **Orchestrator Decision**

**Detected**:
- Task Type: feature
- Risk Level: medium
- Confidence: 85%
- Stack Detected: NestJS, TypeORM, PostgreSQL

**Routing Decision**:
→ Medium-risk feature detected. Will invoke brainstorming workflow to refine requirements before implementation.

**Skills to Activate**:
- brainstorming (feature with medium+ risk requires requirements exploration)
- architecture-patterns (NestJS project, ensure clean architecture principles)

---
```

**Example 2: Consultation**
```
🎯 **Orchestrator Decision**

**Detected**:
- Task Type: consult
- Risk Level: n/a
- Confidence: 92%
- Stack Detected: PostgreSQL

**Routing Decision**:
→ Question detected. Routing to /consult command with database-expert (keywords: "uuid", "primary key", "postgresql")

**Skills to Activate**:
- architecture-patterns (will be injected into database-expert prompt)

---
```

**Example 3: Bug Fix**
```
🎯 **Orchestrator Decision**:

**Detected**:
- Task Type: bug
- Risk Level: high
- Confidence: 95%
- Stack Detected: NestJS, authentication

**Routing Decision**:
→ Bug detected. Auto-invoking systematic-debugging (4-phase mandatory process: Reproduce → Root Cause → Hypothesis → Fix)

**Skills to Activate**:
- systematic-debugging (all bugs require systematic approach)

---
```

### When to Show

- **ALWAYS** show before invoking any skill, workflow, or command
- **ALWAYS** show before routing to an expert agent
- Show **even for simple tasks** (builds trust and understanding)
- Show **even when confidence is high** (transparency = learning)

### Debug Mode

When user says "debug mode" or "--debug", show ADDITIONAL information:

```
🐛 **Debug Info**

**Keywords Matched**: {list of matched keywords}
**Risk Factors**: {what triggered medium/high/critical}
**Alternative Routes Considered**: {what other paths were evaluated}
**Confidence Calculation**: {breakdown of confidence score}
```

---

## Detection Logic

On every user message, the orchestrator:

1. **Parse input** for keywords/patterns using `orchestrator.config.json`
2. **Assess risk** using `risk-profiles.json`
3. **Detect stack** from technology mentions
4. **Classify task type**: consult, feature, bug, refactor, product, design, analytics, documentation

### Task Type Classification

```
CONSULT:
- Questions: "should I", "what's better", "how does X compare to Y"
- Advice: "recommend", "suggest", "best practice"
- Architecture: "design", "architecture", "approach for"

FEATURE:
- Implementation: "add", "implement", "create", "build"
- New functionality: "new feature", "enable", "support"

BUG:
- Issues: "fix", "bug", "error", "broken", "not working"
- Problems: "fails", "crashes", "returns wrong"

REFACTOR:
- Code quality: "refactor", "clean up", "optimize"
- Restructure: "reorganize", "move", "rename"

PRODUCT:
- Discovery: "user story", "acceptance criteria", "definition of done"
- Planning: "roadmap", "prioritize", "backlog", "sprint plan"
- Strategy: "mvp", "product discovery", "feature spec", "rice score"

DESIGN:
- UX: "wireframe", "mockup", "prototype", "user flow"
- Systems: "design system", "design tokens", "ui/ux", "ux research"
- Accessibility: "usability", "accessibility audit", "wcag"

ANALYTICS:
- Tracking: "analytics", "tracking", "event tracking", "metrics"
- Analysis: "dashboard", "funnel", "cohort", "retention"
- Experiments: "a/b test", "experiment", "kpi", "north star"
- Pipelines: "data pipeline", "etl", "data warehouse"

DOCUMENTATION:
- API: "documentation", "api docs", "openapi", "swagger"
- Portal: "developer portal", "getting started", "tutorial"
- SDKs: "sdk", "client library", "changelog", "migration guide"
```

## 🧠 Advanced Detection (v3.0)

### Improved Confidence Calculation

**OLD (naive)**: Word count based
- < 3 words = 30% confidence
- < 6 words = 50% confidence
- < 10 words = 70% confidence
- else = 90% confidence

**NEW (contextual)**:

```python
confidence = base_score + keyword_bonus + structure_bonus + clarity_bonus

# Base score (40%)
base_score = 0.4

# Keyword matching (30%)
if strong_keywords_matched >= 2:
  keyword_bonus = 0.3
elif strong_keywords_matched == 1:
  keyword_bonus = 0.2
else:
  keyword_bonus = 0.0

# Structure (15%)
if has_question_mark or has_imperative_verb:
  structure_bonus = 0.15
elif has_multiple_sentences:
  structure_bonus = 0.10
else:
  structure_bonus = 0.05

# Clarity (15%)
if no_ambiguous_terms and specific_nouns:
  clarity_bonus = 0.15
elif some_specificity:
  clarity_bonus = 0.10
else:
  clarity_bonus = 0.0

# Total: 40% + 30% + 15% + 15% = 100% max
```

**Examples**:
- "fix bug" → 40% + 20% (1 keyword) + 5% (short) + 0% = 65%
- "Should I use JWT or sessions for auth?" → 40% + 30% (jwt, auth) + 15% (question) + 15% (specific) = 100%
- "I want to add a user registration endpoint with email verification" → 40% + 30% (endpoint, user, email) + 10% (multi-sentence) + 15% (specific) = 95%

### Improved Risk Detection

**OLD (over-triggers)**: Any mention of "api", "endpoint", "database" → HIGH risk

**NEW (specific triggers)**:

```javascript
risk = base_risk + complexity_factors + scope_factors

// Base risk by task type
base_risk = {
  feature: 'low',
  bug: 'medium',
  refactor: 'low',
  consult: 'n/a'
}

// Complexity factors (increase risk)
complexity_factors = [
  'authentication', 'authorization', 'payment', 'encryption',  // +2 levels
  'database migration', 'breaking change', 'multi-tenant',    // +2 levels
  'real-time', 'websocket', 'event-driven',                   // +1 level
  'third-party integration', 'external api'                   // +1 level
]

// Scope factors (increase risk)
scope_factors = [
  'affects multiple modules' → +1 level,
  'changes core architecture' → +2 levels,
  'no rollback plan' → +1 level,
  'production only' → +1 level
]

// Risk levels
low → medium → high → critical
```

**Examples**:
- "add a GET /users endpoint" → base: low, no complexity → **LOW**
- "add JWT authentication" → base: low, auth +2 → **HIGH**
- "migrate from sessions to JWT in production" → base: low, auth +2, production +1 → **CRITICAL**
- "fix N+1 query in users controller" → base: medium, no complexity → **MEDIUM**

### Language Detection

Detect if user is writing in español or english:

```javascript
spanish_indicators = [
  'implementar', 'crear', 'agregar', 'arreglar', 'corregir',
  'debería', 'cómo', 'qué', 'usuario', 'base de datos'
]

english_indicators = [
  'implement', 'create', 'add', 'fix', 'should',
  'how', 'what', 'user', 'database'
]

if (spanish_matches > english_matches * 1.5):
  language = 'es'
  use_spanish_responses = true
elif (english_matches > spanish_matches * 1.5):
  language = 'en'
  use_spanish_responses = false
else:
  language = 'mixed'
  use_user_language_preference = true
```

**Impact**: Respond in user's language, use localized examples

---

## Dynamic Routing (v2.0)

The orchestrator reads `when` conditions from SKILL.md frontmatter:

```yaml
# In brainstorming/SKILL.md
when:
  - task_type: feature
    risk_level: [medium, high, critical]
  - user_mentions: ["unclear requirements"]
```

These are converted to dynamic routing rules that take **precedence** over static rules.

## Routing Table (Static + Dynamic)

```javascript
// Consultation (questions/advice)
if (taskType === 'consult') {
  → Invoke: /consult command
  → No confirmation needed
}

// Ralph Loop Auto-Activation (NEW - v4.0)
if (shouldActivateRalph(context)) {
  → Auto-wrap skill in Ralph Loop
  → Iterative self-correction until completion
  → See: Ralph Loop Integration section below
}

// Features (medium/high risk)
if (taskType === 'feature' && risk >= 'medium') {
  → Confirm: "This is a [risk] complexity task. Use brainstorming workflow?"
  → If yes: Invoke brainstorming skill
  → After brainstorm: Ask "Ready to create implementation plan?"
  → If yes: Invoke writing-plans skill
}

// Features (low risk)
if (taskType === 'feature' && risk === 'low') {
  → Check: shouldActivateRalph()
  → If yes: Wrap in Ralph Loop
  → If no: Proceed directly (no workflow)
  → Core enforcement still active
}

// Bugs (all risk levels)
if (taskType === 'bug') {
  → Auto-invoke: systematic-debugging skill
  → No confirmation (bugs always need systematic approach)
}

// Product (discovery, planning, prioritization)
if (taskType === 'product') {
  → Route to: /consult (auto-selects product-expert by keywords)
  → Skills injected: product/product-discovery
  → After completion: Feed output into brainstorming → planning → TDD workflow
}

// Design (UX research, wireframes, design systems)
if (taskType === 'design') {
  → Route to: /consult (auto-selects frontend-ux-expert by keywords)
  → Note: ux-research and design-system skills archived (<5% usage); expertise embedded in agent
  → Output: Wireframes, user flows, interaction specs, design tokens
}

// Analytics (tracking, metrics, dashboards, pipelines)
if (taskType === 'analytics') {
  → Route to: /consult (auto-selects backend-db-expert for analytics schema/queries)
  → Note: analytics-setup and data-pipeline-design skills archived (<5% usage)
  → Output: Event taxonomy, metrics framework, dashboard specs
}

// Documentation (API docs, developer portal, SDKs)
if (taskType === 'documentation') {
  → Invoke skill: devrel/api-documentation
  → Note: developer-portal skill archived (<2% usage)
  → Output: API reference, quick start guide, error catalog
}

// Ambiguous input
if (taskType === 'unknown' || confidence < 0.7) {
  → Ask: "I can help with:
    [C] Consult - Get expert advice
    [F] Feature - Build something new
    [B] Bug - Fix an issue
    [R] Refactor - Improve code
    [P] Product - Define/prioritize features
    [D] Design - UX/wireframes/design system
    [A] Analytics - Tracking/metrics/dashboards
    [O] Docs - API docs/developer portal
    Which best describes what you need?"
  → Route based on response
}
```

## Core Skills Enforcement (Always Active)

### From verification-enforcement

**BLOCKING RULES** (prevent completion without evidence):

1. **Test Evidence Required**
   - Cannot claim "done" or "fixed" without test output
   - Must show: test run output, error reproduction, verification steps
   - Rationalization blocked: "tests should pass" → Show actual output

2. **Build Verification Required**
   - Cannot merge/deploy without clean build
   - Must show: `npm run build` output, compilation success
   - Rationalization blocked: "it compiles" → Show actual output

3. **Explicit Confirmation Required**
   - Cannot assume user approval
   - Must get explicit "yes" / "approved" / "proceed"
   - Rationalization blocked: "user probably wants" → Ask directly

### From anti-rationalization

**BANNED PHRASES** (trigger immediate self-correction):

```
❌ "should work" → ✅ "verified working (evidence: ...)"
❌ "probably" → ✅ "confirmed by testing"
❌ "typically" → ✅ "documented in [file/docs]"
❌ "usually" → ✅ "verified in this codebase"
❌ "might" → ✅ "tested and confirmed"
❌ "I assume" → ✅ "I verified by reading [file]"
❌ "likely" → ✅ "confirmed in [location]"
❌ "it seems" → ✅ "confirmed by [evidence]"
```

**EVIDENCE REQUIREMENTS**:
- Config values → Read actual config file
- Dependencies → Read package.json
- API behavior → Read code or test it
- Framework features → Read docs or code

### From context-awareness

**MANDATORY CHECKS** (before any implementation):

1. **Read Before Changing**
   - Must read file before editing
   - Must understand existing patterns
   - Must check for similar implementations

2. **Verify Assumptions**
   - Stack detection → Confirm by reading package.json
   - File locations → Use Glob/Grep to find
   - API contracts → Read actual interfaces/types

3. **Follow Existing Patterns**
   - Check how project handles similar cases
   - Match naming conventions
   - Use same libraries/approaches already in use

## Knowledge Integration

### Auto-Load on Task Start

When orchestrator detects a task:

1. **Load relevant patterns**:
   ```javascript
   const stack = detectStack(userInput); // e.g., "nestjs", "typeorm"
   const patterns = loadPatterns(stack, taskType);
   // Reads: .claude/knowledge/patterns/*-{stack}-*.json
   ```

2. **Load relevant lessons**:
   ```javascript
   const lessons = loadLessons(stack);
   // Reads: .claude/knowledge/lessons/*-{stack}-*.json
   ```

3. **Inject into context**:
   - Mention: "Based on past patterns in this codebase..."
   - Apply: Use established patterns automatically
   - Avoid: Don't repeat past mistakes

### Prompt Capture After Completion

After any task completion:

```
✅ Task completed!

¿Aprendiste algo reutilizable? (ayuda: .claude/memory/README.md)

[P] Pattern → Patrón técnico reutilizable
    Ejemplo: "Pagination con cursor-based para evitar offset N+1"

[L] Lesson → Lección aprendida (qué evitar)
    Ejemplo: "N+1 queries con eager loading - usar relations[]"

[D] Decision → Decisión de diseño con rationale
    Ejemplo: "JWT vs sessions: elegimos JWT por stateless scaling"

[N] No → Nada que capturar esta vez

→ If P/L/D selected, prompt for:
  - Title (corto, descriptivo)
  - Context (cuándo aplicar esto)
  - Solution/Lesson/Rationale (qué hiciste y por qué)
  - Tags (stack: nestjs, typeorm; task-type: feature, bug)

→ Save to: .claude/memory/ (persists across sessions)
```

**UX Improvements**:
- ✅ Inline examples for each option
- ✅ Clear Spanish labels (matches user's language)
- ✅ Help reference (.claude/memory/README.md)
- ✅ Explanation of value (reutilizable, persists across sessions)

## Orchestration Flow

```
User Input
    ↓
[1] DETECT
    - Parse input (detector.js)
    - Classify task type
    - Assess risk level
    - Detect stack
    ↓
[2] LOAD KNOWLEDGE
    - Read relevant patterns
    - Read relevant lessons
    - Inject into context
    ↓
[3] ROUTE
    - Consult? → /consult (auto-select experts)
    - Feature (medium/high)? → Confirm → brainstorming → planning → TDD
    - Feature (low)? → Proceed with enforcement
    - Bug? → systematic-debugging (4 phases)
    - Product? → product-expert (discovery/prioritization)
    - Design? → ux-expert (research/design-system)
    - Analytics? → data-expert (tracking/pipelines)
    - Documentation? → devrel-expert (api-docs/portal)
    - Refactor? → Proceed with enforcement
    ↓
[4] EXECUTE
    - Invoke skill via Skill tool
    - Or execute directly
    - Core enforcement always active
    ↓
[5] CAPTURE
    - Prompt for documentation
    - Save pattern/lesson/decision
    - Update knowledge base
```

## Implementation Notes

**This skill embeds the enforcement rules** from:
- `_core/verification-enforcement` → Blocking rules
- `_core/anti-rationalization` → Banned phrases
- `_core/context-awareness` → Mandatory checks

**Why embed?** These rules must be active on every task, not just when explicitly invoked. By embedding them in the auto-loaded orchestrator, they become transparent guardrails.

**Detection uses**: Hardcoded patterns in `lib/detector.js` (config files archived, see `config_archive/README.md`)

**Knowledge uses**: `.claude/knowledge/patterns/` and `.claude/knowledge/lessons/`

## Examples

### Example 1: Consultation
```
User: "Should I use Redis or in-memory cache for session storage?"

Orchestrator detects: taskType=consult
→ Routes to: /consult
→ /consult invokes: backend-expert + devops-expert
→ Returns: Architectural advice
```

### Example 2: Medium-Risk Feature
```
User: "Add JWT authentication with refresh tokens"

Orchestrator detects: taskType=feature, risk=critical, stack=nestjs
→ Confirms: "Critical complexity task. Use brainstorming workflow? (Y/n)"
→ User: "y"
→ Invokes: Skill('brainstorming', 'Add JWT auth with refresh tokens')
→ After brainstorm: "Ready to create implementation plan? (Y/n)"
→ Invokes: Skill('writing-plans', brainstormOutput)
→ Proceeds with implementation
→ After completion: "Document this? [P]attern [L]esson [D]ecision [N]o"
```

### Example 3: Bug Report
```
User: "Users endpoint returns 500 error randomly"

Orchestrator detects: taskType=bug, risk=medium, stack=nestjs
→ Auto-invokes: Skill('systematic-debugging', 'Users endpoint 500 error')
→ Phase 1: Reproduce
→ Phase 2: Root cause analysis
→ Phase 3: Hypothesis formation
→ Phase 4: Fix + verification
→ After fix: "Document this lesson? [L]esson [N]o"
```

### Example 4: Product Discovery
```
User: "Define user stories for the onboarding flow"

Orchestrator detects: taskType=product, risk=medium
→ Routes to: /consult (selects product-expert by keywords)
→ Skills injected: product/product-discovery
→ Executes: Problem Framing → User & Context → Solution → Scope
→ Output: User stories with acceptance criteria, RICE scores
→ After completion: "Document this? [P]attern [L]esson [D]ecision [N]o"
```

### Example 5: Design/UX
```
User: "Create wireframes for the dashboard"

Orchestrator detects: taskType=design, risk=low
→ Routes to: /consult (selects frontend-ux-expert by design keywords)
→ Note: ux-research and design-system skills archived; expertise embedded in agent
→ Executes: User Understanding → Flow Mapping → Screen Specs → Interaction Specs
→ Output: ASCII wireframes, responsive specs, design tokens
```

### Example 6: Analytics Setup
```
User: "Setup analytics for user behavior tracking"

Orchestrator detects: taskType=analytics, risk=medium
→ Routes to: /consult (selects backend-db-expert for analytics queries/schema)
→ Note: analytics-setup skill archived (<5% usage); analytics schema/query expertise in backend-db-expert
→ Executes: Event taxonomy → North Star metrics → Dashboard specs
→ Output: Event naming conventions, AARRR framework, dashboard per audience
```

### Example 7: API Documentation
```
User: "Create API docs for the users module"

Orchestrator detects: taskType=documentation, risk=low
→ Invokes skill: devrel/api-documentation
→ Note: developer-portal skill archived; api-documentation skill active in devrel/
→ Executes: Quick Start → Auth → Endpoint Reference → Error Catalog
→ Output: Complete API reference with curl examples
```

### Example 8: Ambiguous Input
```
User: "The database thing isn't working right"

Orchestrator detects: taskType=unknown, confidence=0.4
→ Asks: "I can help with:
  [C] Consult  [F] Feature  [B] Bug  [R] Refactor
  [P] Product  [D] Design   [A] Analytics  [O] Docs
  Which best describes what you need?"
→ User: "B"
→ Routes to: systematic-debugging
```

## Configuration

Controlled by `.claude/settings.json`:

```json
{
  "orchestration": {
    "enabled": true,
    "auto_detect": true,
    "confirmations": {
      "critical_risk": true,
      "high_risk": false
    }
  },
  "knowledge": {
    "enabled": true,
    "auto_load_patterns": true,
    "prompt_capture_after_completion": true
  }
}
```

---

## Ralph Loop Integration (v4.0)

### Auto-Activation Logic

The orchestrator automatically wraps skills in Ralph loops when ALL conditions are met:

```typescript
function shouldActivateRalph(context: TaskContext): RalphConfig | null {
  const { taskType, riskLevel, hasTestSuite, verificationCommand, intent } = context;
  const settings = loadSettings('.claude/settings.json');

  if (!settings.ralph.enabled || !settings.ralph.autoActivation.enabled) {
    return null;
  }

  // Rule 1: TDD Feature Implementation
  if (
    taskType === 'feature' &&
    hasTestSuite &&
    riskLevel in ['low', 'medium'] &&
    verificationCommand === 'npm test'
  ) {
    return {
      skill: 'tdd',
      maxIterations: settings.ralph.autoActivation.rules.tdd.maxIterations,
      maxCostUSD: settings.ralph.autoActivation.rules.tdd.maxCostUSD,
      completionPromise: '<promise>COMPLETE</promise>',
      verificationCommand: 'npm test',
      stallDetectionThreshold: 5,
      initialPrompt: userInput
    };
  }

  // Rule 2: Bug Fix with Systematic Debugging
  if (
    taskType === 'bug' &&
    hasTestSuite &&
    riskLevel in ['low', 'medium']
  ) {
    return {
      skill: 'systematic-debugging',
      maxIterations: settings.ralph.autoActivation.rules.debugging.maxIterations,
      maxCostUSD: settings.ralph.autoActivation.rules.debugging.maxCostUSD,
      completionPromise: '<promise>BUG_FIXED</promise>',
      verificationCommand: 'npm test',
      stallDetectionThreshold: 5,
      escalateToDeepDebug: true,
      initialPrompt: userInput
    };
  }

  // Rule 3: Lint/Format Cleanup
  if (
    taskType === 'refactor' &&
    intent === 'fix-linting'
  ) {
    return {
      skill: 'code-cleanup',
      maxIterations: settings.ralph.autoActivation.rules.linting.maxIterations,
      maxCostUSD: settings.ralph.autoActivation.rules.linting.maxCostUSD,
      completionPromise: '<promise>LINT_CLEAN</promise>',
      verificationCommand: 'npm run lint',
      stallDetectionThreshold: 3,
      initialPrompt: userInput
    };
  }

  // No Ralph for:
  // - Architecture/design decisions (subjective)
  // - High/critical risk (needs human oversight)
  // - Tasks without verification command
  // - Tasks without clear success criteria
  return null;
}
```

### Ralph Execution Flow

```
User Input → Detect Context → Check shouldActivateRalph()
                                        ↓
                                      YES ↓ NO → Normal Flow
                                        ↓
                            ┌───────────────────────┐
                            │ Ralph Loop Wrapper     │
                            │ ──────────────────────│
                            │ Iteration 1:          │
                            │  - Execute skill      │
                            │  - Run verification   │
                            │  - Check completion   │
                            │                       │
                            │ Iteration 2:          │
                            │  - Read test failures │
                            │  - Fix issues         │
                            │  - Run verification   │
                            │                       │
                            │ ...                   │
                            │                       │
                            │ Iteration N:          │
                            │  - All tests pass     │
                            │  - <promise>COMPLETE> │
                            │  → EXIT SUCCESS ✅    │
                            └───────────────────────┘
```

### Displaying Ralph Status to User

When Ralph is activated, show transparent status:

```
🔄 **Ralph Loop Activated**

**Configuration**:
- Skill: tdd
- Max Iterations: 20
- Max Cost: $5.00
- Verification: npm test
- Completion Signal: <promise>COMPLETE</promise>

**Safety**:
- Stall detection after 5 iterations with no progress
- Prohibited paths: src/auth/, src/payments/, migrations/
- Daily budget: $50.00 (remaining: $47.23)

---

Iteration 1/20 (Cost: $0.00 / $5.00)
🚀 Executing TDD skill...
✅ Tests: 0 passing, 3 failing
📝 Files modified: 2

Iteration 2/20 (Cost: $0.08 / $5.00)
🚀 Executing TDD skill...
✅ Tests: 2 passing, 1 failing
📝 Files modified: 1

Iteration 3/20 (Cost: $0.15 / $5.00)
🚀 Executing TDD skill...
✅ Tests: 3 passing, 0 failing
✅ Completion promise detected!
✅ Verification PASSED

---

✅ **Ralph Loop Completed**
- Iterations: 3/20
- Total Cost: $0.15
- Duration: 42 seconds
- Result: All tests passing ✅
```

### Handling Ralph Aborts

If Ralph aborts (stall, cost limit, etc.), display clear status:

```
❌ **Ralph Loop Aborted**

**Reason**: Stall detected (5 iterations with no progress)

**Progress Made**:
- Iterations completed: 8/20
- Cost spent: $0.67
- Tests fixed: 2 (was 5 failing, now 3 failing)
- Files modified: 12

**Last Error**:
```
FAIL src/auth/register.spec.ts
  ● should validate email format
    Expected valid email to pass, but validation failed
```

**Next Steps**:
Would you like to:
1. Continue manually (I'll apply fixes without the loop)
2. Escalate to systematic-debugging (4-phase deep analysis)
3. Review the code together and discuss approach
```

### Configuration Override

Users can override Ralph settings per-invocation:

```
User: "Implement user registration --ralph-iterations=10 --ralph-cost=2"

→ Orchestrator: Overrides default settings with user values
```

### Disabling Ralph

Users can disable Ralph for specific tasks:

```
User: "Implement user registration --no-ralph"

→ Orchestrator: Skips Ralph activation, uses normal flow
```

---

**Note**: This orchestrator is auto-loaded and runs transparently on every user interaction. It makes intelligent routing decisions while keeping the user in control through confirmations when appropriate.

**Ralph Integration**: Version 4.0 adds automatic iterative self-correction through the Ralph Loop Wrapper.
