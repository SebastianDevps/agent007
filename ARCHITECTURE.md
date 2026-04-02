# Agent007 - Architecture & Orchestration

Technical documentation explaining how Agent007 works internally.

---

## 🎯 Overview

Agent007 is an intelligent development orchestration system that automatically routes user queries to the most appropriate expert agents, loads relevant domain skills, and provides consolidated, token-optimized responses.

**Key Innovation**: 85-92% token reduction through lazy loading, skill summaries, and prompt caching.

---

## 🏗️ System Architecture

```
User Query
    ↓
[Orchestrator]
    ↓
┌───────────────────────────────────────┐
│ 1. Query Analysis                    │
│    - Keyword extraction               │
│    - Intent detection                 │
│    - Risk assessment                  │
└───────────────────────────────────────┘
    ↓
┌───────────────────────────────────────┐
│ 2. Expert Selection                  │
│    - Keyword matching algorithm       │
│    - Confidence scoring               │
│    - Multi-expert coordination        │
└───────────────────────────────────────┘
    ↓
┌───────────────────────────────────────┐
│ 3. Skill Loading (Lazy + Summaries)  │
│    - Load only relevant skills        │
│    - Use SUMMARY.md (100 lines)       │
│    - Skip irrelevant domains          │
└───────────────────────────────────────┘
    ↓
┌───────────────────────────────────────┐
│ 4. Context Building                   │
│    - Project detection (NestJS, etc.) │
│    - Minimal context contracts        │
│    - Cache optimization               │
└───────────────────────────────────────┘
    ↓
┌───────────────────────────────────────┐
│ 5. Agent Execution (Parallel)         │
│    - Launch 1-3 experts concurrently  │
│    - Model selection (Opus/Sonnet)    │
│    - Response generation              │
└───────────────────────────────────────┘
    ↓
┌───────────────────────────────────────┐
│ 6. Response Consolidation             │
│    - Extract consensus                │
│    - Merge perspectives               │
│    - Remove redundancy                │
└───────────────────────────────────────┘
    ↓
Unified Response (10K tokens vs 60K)
```

---

## 🧩 Core Components

### 1. Expert Agents (5)

| Agent | Model | Specialization | Skills |
|-------|-------|----------------|--------|
| **backend-db-expert** | Opus | APIs, NestJS, databases, distributed systems | api-design-principles, architecture-patterns, resilience-patterns |
| **frontend-ux-expert** | Sonnet | React, Next.js, UX, performance, animations | react-best-practices, frontend-design, gsap-core, gsap-timeline, gsap-scrolltrigger, gsap-plugins, gsap-react, gsap-utils, gsap-performance, gsap-frameworks |
| **platform-expert** | Sonnet | CI/CD, Docker, testing, quality gates | workflow/tdd, quality-gates/systematic-debugging |
| **product-expert** | Opus | Product discovery, roadmap, prioritization | product/product-discovery |
| **security-expert** | Opus | OWASP, threat modeling, compliance | nestjs-code-reviewer |

**Location**: `/agents/*.md`

Each agent has:
- Specialized methodology
- Domain expertise
- Associated skills
- Model preference (Opus/Sonnet)

### 2. Domain Skills (25)

Skills are grouped by category:

**Core Orchestration**:
- `_orchestration/session-orchestrator` - Query routing logic

**Quality Enforcement**:
- `_core/quality-enforcement` - Verification, anti-rationalization, context-awareness

**Workflows**:
- `workflow/brainstorm` - Socratic requirements exploration
- `workflow/writing-plans` - Feature decomposition
- `workflow/tdd` - Test-Driven Development

**Quality Gates**:
- `quality-gates/systematic-debugging` - Root cause analysis
- `quality-gates/architecture-review` - Deep architecture analysis

**Domain Expertise**:
- `api-design-principles` - REST API best practices
- `architecture-patterns` - Clean Architecture, DDD
- `resilience-patterns` - Circuit breakers, retry logic
- `nestjs-code-reviewer` - NestJS security & anti-patterns
- `frontend-design` - High-quality UI design
- `react-best-practices` - React optimization

**GSAP Animation** (frontend-ux-expert):
- `gsap-core` - Tweens, easing, stagger, matchMedia
- `gsap-timeline` - Sequencing, position parameter, nesting
- `gsap-scrolltrigger` - Scroll-linked animations, pinning, scrub
- `gsap-plugins` - Flip, Draggable, SplitText, MorphSVG, MotionPath
- `gsap-react` - useGSAP hook, context, SSR
- `gsap-utils` - clamp, mapRange, snap, toArray, pipe
- `gsap-performance` - transforms, will-change, quickTo
- `gsap-frameworks` - Vue, Svelte lifecycle, cleanup

**Location**: `/skills/{skill-name}/`

Each skill has:
- `SKILL.md` (full, 650+ lines)
- `SUMMARY.md` (condensed, 100 lines)

### 3. Commands

Custom slash commands that trigger orchestration:

- `/consult` - Main consultation entry point
- `/review` - Code review workflow
- `/plan` - Feature planning
- `/architecture-review` - Deep analysis

**Location**: `/commands/{command-name}/`

---

## 🔄 Orchestration Flow

### Query: "How to implement JWT authentication in NestJS?"

**Step 1: Keyword Analysis**
```javascript
Keywords extracted: ["jwt", "authentication", "nestjs"]

Matching scores:
- backend-db-expert: 25 (jwt=10, auth=10, nestjs=5)
- security-expert: 20 (jwt=10, auth=10)
- frontend-ux-expert: 0
- platform-expert: 5
- product-expert: 0

Selected: backend-db-expert, security-expert
```

**Step 2: Skill Loading**
```javascript
backend-db-expert → Load:
  - api-design-principles/SUMMARY.md (100 lines)
  - Skip: architecture-patterns, resilience-patterns

security-expert → Load:
  - nestjs-code-reviewer/SUMMARY.md (100 lines)

Total: ~200 lines vs 1,300+ lines (full skills)
```

**Step 3: Context Detection**
```javascript
Read package.json → Detect NestJS, TypeORM, PostgreSQL
Read tsconfig.json → Detect TypeScript strict mode

Context contract: {
  framework: "NestJS",
  database: "PostgreSQL",
  orm: "TypeORM",
  language: "TypeScript"
}
```

**Step 4: Agent Execution (Parallel)**
```javascript
Promise.all([
  Task(backend-db-expert, opus, prompt1),
  Task(security-expert, opus, prompt2)
])

Response 1: API design patterns for JWT
Response 2: Security best practices (OWASP)
```

**Step 5: Consolidation**
```javascript
Consensus:
- Use JWT with refresh tokens
- Store in httpOnly cookies
- Implement token rotation

Trade-offs:
- backend-db-expert: Focus on API structure
- security-expert: Focus on XSS/CSRF prevention

Merged response: 50 lines (both perspectives)
```

**Result**: 10K tokens (vs 60K without optimization)

---

## 🚀 Token Optimization Techniques

### 1. Lazy Skill Loading

**Before**:
```
Load ALL 3 skills for backend-expert:
- api-design-principles (650 lines)
- architecture-patterns (700 lines)
- resilience-patterns (650 lines)
Total: 2,000 lines → 40K tokens
```

**After**:
```
Load ONLY relevant skill:
- api-design-principles/SUMMARY.md (100 lines)
Total: 100 lines → 2K tokens

Savings: 95% (38K tokens)
```

**Implementation**: `/commands/consult/lib/skill-selector.js`

### 2. Skill Summaries

Each skill has two versions:

| File | Size | Use Case |
|------|------|----------|
| `SKILL.md` | 650+ lines | Deep mode, complex queries |
| `SUMMARY.md` | 100 lines | Normal mode, quick queries |

**SUMMARY.md contains**:
- Core principles (5-10)
- Quick checklist
- Key patterns
- Reference to full SKILL.md

**Implementation**: `/commands/consult/lib/skills-injector.js`

### 3. Prompt Caching (Anthropic)

Cache static content across queries:

**Cacheable** (5-minute TTL):
- Expert methodology
- Skill summaries
- Project context (if stable)

**Non-cacheable**:
- User question
- Dynamic context

**First query**: 15K tokens
**Cached queries**: 5K tokens (67% reduction)

**Implementation**: `.claude/shared/providers/cached-anthropic-client.js`

### 4. Context Contracts

Minimal, structured context instead of dumping entire project:

**Before**:
```
Context: [entire package.json, tsconfig.json, README, etc.]
Total: 10K tokens
```

**After**:
```
Context: {
  framework: "NestJS",
  database: "PostgreSQL",
  orm: "TypeORM",
  relevantFiles: ["src/auth/", "src/users/"]
}
Total: 500 tokens

Savings: 95% (9.5K tokens)
```

**Implementation**: `/commands/consult/lib/context-contracts.js`

---

## 📊 Performance Metrics

### Token Consumption

| Scenario | Before | After | Reduction |
|----------|--------|-------|-----------|
| Simple query (1 skill) | 60,000 | 8,000 | 87% |
| Normal query (2 skills) | 60,000 | 12,000 | 80% |
| Complex query (3 skills) | 60,000 | 18,000 | 70% |
| Cached query (repeat) | 15,000 | 5,000 | 67% |

### Cost Savings (Opus Model)

| Usage | Before | After | Savings |
|-------|--------|-------|---------|
| 10 queries/day | $9.00 | $1.50 | $7.50/day |
| 300 queries/month | $270 | $45 | **$225/month** |
| Annual | $3,240 | $540 | **$2,700/year** |

### Response Time

| Query Type | Time |
|------------|------|
| Simple (1 expert) | ~15s |
| Normal (2 experts) | ~20s |
| Deep (3 experts) | ~30s |
| Cached (hit) | ~10s |

---

## 🔧 Extension Points

### Adding a New Expert

1. Create `/agents/new-expert.md`:
```markdown
---
name: new-expert
description: Expert in X domain
model: sonnet
tools: Read, Grep, Glob, Bash
---

You are a senior expert in X...
```

2. Add to keyword mapping in orchestrator

3. Associate skills in `/skills/{domain}/`

### Adding a New Skill

1. Create directory: `/skills/{category}/{skill-name}/`

2. Create `SKILL.md` (full content, 500+ lines)

3. Create `SUMMARY.md` (100 lines):
```markdown
# Skill Name - Summary

## Core Principles
1. Principle 1
2. Principle 2

## Quick Checklist
- [ ] Item 1
- [ ] Item 2

## Key Patterns
- Pattern A
- Pattern B

See SKILL.md for full details.
```

4. Link to expert in `/agents/{expert}.md`

### Adding a New Command

1. Create `/commands/{command-name}/`

2. Create `{command-name}.md` with skill definition

3. Implement orchestration logic if needed

---

## 🧪 Testing

### Unit Tests (Planned)

- `skill-selector.test.js` - Keyword matching algorithm
- `skills-injector.test.js` - Summary vs full loading
- `context-contracts.test.js` - Minimal context extraction

### Integration Tests

- End-to-end consultation flow
- Multi-expert coordination
- Cache hit rate validation

---

## 🔐 Quality Enforcement

### Always Active

1. **Verification**: No completion claims without test/build output
2. **Anti-Rationalization**: No "should work", "probably", "usually"
3. **Context-Awareness**: Read files before changing

### Implementation

All agents receive quality enforcement skill automatically:
- Location: `/skills/_core/quality-enforcement/SKILL.md`
- Injected in every agent prompt
- Cannot be bypassed

---

## 🚦 Risk Assessment

Orchestrator automatically detects query risk:

| Risk Level | Triggers | Behavior |
|------------|----------|----------|
| **Low** | Simple queries, read-only | Standard execution |
| **Medium** | File modifications, refactoring | Confirmation prompt |
| **High** | Database migrations, auth changes | Plan mode first |
| **Critical** | Production deploys, data deletion | Manual approval required |

**Implementation**: `/commands/consult/lib/execution-mode.js`

---

## 📦 Distribution

Agent007 is distributed as a Claude Code plugin via custom marketplace:

**Installation**:
```bash
/plugin marketplace add SebastianDevps/agent007-marketplace
/plugin install agent007@agent007-marketplace
```

**Installed to**: `~/.claude/plugins/cache/agent007-*/`

**Skills available globally**: `/agent007:consult`, `/agent007:review`, etc.

---

## 🔄 Update Workflow

1. Make changes in `/Users/sebasing/Projects/Agent007`
2. Update `VERSION` file
3. Update `.claude-plugin/plugin.json` version
4. Commit & push to GitHub
5. Update marketplace version in `agent007-marketplace`
6. Users run: `/plugin update agent007`

---

## 🤝 Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for contribution guidelines.

**Note**: All PRs are reviewed before merge to ensure quality and architecture consistency.

---

## 📄 License

MIT License - See [LICENSE](LICENSE)

---

## 📞 Support

- **GitHub Issues**: https://github.com/SebastianDevps/agent007/issues
- **Discussions**: https://github.com/SebastianDevps/agent007/discussions
- **Documentation**: README.md, ARCHITECTURE.md, CONTRIBUTING.md

---

**Agent007 v2.0.0** - Intelligent Development Orchestration
