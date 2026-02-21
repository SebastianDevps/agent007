# Consult Command v2.0

Intelligent expert consultation system that leverages the entire Agent007 ecosystem.

## Quick Start

```javascript
const { consult, preview } = require('./index');

// Consult with auto-selection
const result = await consult("How to implement JWT auth in NestJS?");

// Preview what will happen
const info = preview("How to implement JWT auth in NestJS?");
```

## Architecture

```
User Query
    ↓
scan-context.js (Project scanning)
    → Detects framework, database, ORM, modules
    ↓
consult-router.js (Expert selection)
    → Uses detector to analyze query
    → Selects relevant experts (1-3)
    ↓
skills-injector.js (Skills loading)
    → Loads domain skills for each expert
    → Enhances prompts with established patterns
    ↓
[Execute consultation with Task tool]
    → Launches selected experts
    → Experts receive enhanced prompts
    ↓
response-consolidator.js (Post-processing)
    → Eliminates redundancy
    → Highlights consensus
    → Creates unified response
    ↓
Post-consultation actions
    → [I]mplement, [P]lan, [C]larify, [D]one
```

## Components

### scan-context.js
Scans project to detect:
- Framework (NestJS, Express, Next.js)
- Database (PostgreSQL, MongoDB, Redis)
- ORM (TypeORM, Prisma, Mongoose)
- Testing (Jest, Vitest)
- Structure (modular, feature-based)
- Existing modules

### consult-router.js
Auto-selects experts based on:
- Keyword matching
- Stack detection
- Risk assessment
- Query complexity

### skills-injector.js
Injects domain skills into expert prompts:
- backend-expert → api-design-principles, architecture-patterns
- security-expert → nestjs-code-reviewer
- testing-expert → tdd workflow, systematic-debugging

### response-consolidator.js
Post-processes multi-expert responses:
- Extracts consensus
- Identifies differences
- Consolidates recommendations
- Removes redundancy

## Expert Selection Rules

### backend-expert
**Keywords**: api, endpoint, service, architecture, microservice, nestjs
**Model**: opus
**Skills**: api-design-principles, architecture-patterns, resilience-patterns

### database-expert
**Keywords**: database, query, sql, schema, orm, typeorm, optimization
**Model**: opus
**Skills**: architecture-patterns

### security-expert
**Keywords**: security, auth, jwt, oauth, encryption, vulnerability
**Model**: opus
**Skills**: nestjs-code-reviewer

### frontend-expert
**Keywords**: react, next, component, ui, performance, rendering
**Model**: sonnet
**Skills**: react-best-practices, frontend-design

### devops-expert
**Keywords**: deployment, docker, ci/cd, kubernetes, cloud
**Model**: sonnet
**Skills**: none

### testing-expert
**Keywords**: test, tdd, coverage, jest, quality
**Model**: sonnet
**Skills**: workflow/tdd, systematic-debugging

## Usage Examples

### Basic Consultation

```javascript
const { consult } = require('./.claude/commands/consult');

const result = await consult("How to implement rate limiting?", {
  mode: 'normal'  // quick, normal, or deep
});

console.log(result.experts);
// ['backend-expert', 'security-expert']

console.log(result.projectContext);
// { framework: 'NestJS', database: ['PostgreSQL'], ... }
```

### Preview Mode

```javascript
const { preview } = require('./.claude/commands/consult');

const info = preview("Optimize database queries", { mode: 'deep' });

console.log(info.selectedExperts);
// ['database-expert', 'backend-expert', 'testing-expert']

console.log(info.reasoning);
// "Selected 3 experts for deep mode: database-expert (score: 40), ..."
```

### Force Specific Experts

```javascript
const result = await consult("my question", {
  forceExperts: ['backend-expert', 'database-expert'],
  mode: 'deep'
});
```

### Skip Context Scanning

```javascript
const result = await consult("generic question", {
  skipContext: true
});
```

## Integration with Ecosystem

### With Session Orchestrator

```javascript
// Consult uses detector from session-orchestrator
const { detectContext } = require('../skills/_orchestration/session-orchestrator/lib/detector');

const context = detectContext(query);
// Used for expert selection
```

### With Domain Skills

```javascript
// Skills automatically injected into expert prompts
const skills = loadSkillsForAgent('backend-expert');
// Returns: [api-design-principles, architecture-patterns, resilience-patterns]

const prompt = buildEnhancedPrompt(agentName, query, projectContext, skills);
// Prompt includes full skill content
```

### Post-Consultation Workflow

```javascript
const actions = getPostConsultationActions(result);

// User selects [I]mplement
// → Auto-invokes brainstorming skill
// → Then writing-plans
// → Then TDD implementation
```

## Testing

```bash
# Test project scanner
node -e "
const { scanProjectContext } = require('./.claude/commands/consult');
console.log(scanProjectContext('.'));
"

# Test expert selection
node -e "
const { selectExperts } = require('./.claude/commands/consult/lib/consult-router');
console.log(selectExperts('implement JWT auth', 'deep'));
"

# Test skills injection
node -e "
const { loadSkillsForAgent } = require('./.claude/commands/consult/lib/skills-injector');
console.log(loadSkillsForAgent('backend-expert'));
"
```

## File Structure

```
consult/
├── index.js                    # Main entry point
├── consult.md                  # Command definition (v1.0 compat)
├── CONSULT.md                  # Full documentation
├── README.md                   # This file
└── lib/
    ├── scan-context.js         # Project scanner
    ├── consult-router.js       # Expert selection
    ├── skills-injector.js      # Skills loading
    └── response-consolidator.js # Response processing
```

## Version History

### v2.0.0 (2026-02-08)
- ✅ Auto-selection of experts
- ✅ Project context scanning
- ✅ Skills injection
- ✅ Multi-expert consolidation
- ✅ Post-consultation workflow

### v1.0.0
- Manual expert selection
- Basic consultation
- No context awareness

---

**Status**: ✅ Fully integrated with Agent007 ecosystem
**Version**: 2.0.0
