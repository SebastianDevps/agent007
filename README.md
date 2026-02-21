# Agent007 - Intelligent Development Orchestration System

> **v2.0** - Optimized for 85-92% token reduction with OpenCode-inspired patterns

An autonomous AI development team ecosystem with 5 consolidated expert agents, 17 active skills, and intelligent orchestration that automatically detects tasks, assesses risk, and routes work to the right experts.

---

## 🎯 What's New in v2.0

### Token Optimization (85-92% Reduction)
- **Lazy Skill Loading**: Only loads relevant skills based on query keywords
- **Skill Summaries**: 100-line summaries vs 650+ line full skills
- **Prompt Caching**: Anthropic caching for 67% additional savings
- **Context Contracts**: Minimal, structured context reduces redundancy

**Impact**: 60K → 5-10K tokens per consultation

### OpenCode-Inspired Features
- **Dual Agent System**: Plan (read-only) vs Build (full access) modes
- **Multi-Model Support**: Runtime selection (Opus, Sonnet, Haiku)
- **CI/CD Validation**: Auto-validate skills and agents on PRs
- **Modern Tooling**: Turborepo for task orchestration

---

## 🚀 Quick Start

### Installation (One Command)

```bash
/plugin install agent007@sebasing/agent007 --scope user
```

**That's it!** Agent007 is now available in **all your projects**. ✅

---

### Alternative: Local Testing

```bash
# Test locally without installing
cd ~/Projects/YourProject
claude --plugin-dir /path/to/agent007
```

### Basic Usage

Once installed, Agent007 skills are available globally:

```bash
# Simple consultation (normal mode - lazy loading + summaries)
/agent007:consult "How to implement circuit breaker for S3?"
# → Loads only: resilience-patterns summary (~100 lines)

# Deep consultation (all skills, full content)
/agent007:consult "Complete API architecture review" --deep
# → Loads all relevant skills in full detail

# Other skills (namespaced with plugin name)
/agent007:review
/agent007:plan
/agent007:architecture-review
/agent007:api-design-principles
/agent007:resilience-patterns
/agent007:frontend-design
```

**Note**: Skills are namespaced as `/agent007:skill-name` when installed as a plugin. This prevents conflicts with other plugins.

---

## 📊 Performance Metrics

| Metric | Before | After | Improvement |
|--------|--------|-------|-------------|
| **Tokens/query** | 60,000 | 10,000 | **83% ↓** |
| **Cost/query (Opus)** | $0.90 | $0.15 | **83% ↓** |
| **Cost/month** (10/day) | $270 | $45 | **$225 saved** |
| **With caching** | - | 5,000 tokens | **92% ↓** |

---

## 🛠️ Available Expert Agents (5)

| Agent | Model | Specialization |
|-------|-------|----------------|
| **backend-db-expert** | Opus | APIs, distributed systems, schema design, query optimization |
| **frontend-ux-expert** | Sonnet | React/Next.js, performance, UX design, accessibility |
| **platform-expert** | Sonnet | CI/CD, Docker, testing (TDD/BDD), quality gates |
| **product-expert** | Opus | Product discovery, roadmap, prioritization (RICE/ICE) |
| **security-expert** | Opus | OWASP, threat modeling, compliance (GDPR, SOC2) |

---

## 🎯 Available Commands

### Core Commands
- `/consult "question"` - Auto-selects experts and provides consolidated advice
- `/brainstorm` - Socratic requirements exploration before implementation
- `/plan` - Decomposes features into 2-5 minute tasks
- `/review` - Code review for NestJS + TypeORM

### Advanced
- `/architecture-review` - Deep architecture review (DRY, testing gaps, edge cases)
- `/api-design-principles` - API design audit
- `/architecture-patterns` - Architecture patterns review
- `/resilience-patterns` - Resilience patterns implementation
- `/frontend-design` - High-quality frontend interface creation

---

## 📈 Token Optimization Features

### 1. Lazy Skill Loading

**Before**: Loaded all 3 skills for backend-expert (~40K tokens)
**After**: Loads 1-2 relevant skills (~10K tokens)

```javascript
// Automatic keyword matching
Query: "circuit breaker for S3"
→ Loads ONLY: resilience-patterns

Query: "API design best practices"
→ Loads ONLY: api-design-principles
```

### 2. Skill Summaries

**Before**: Full SKILL.md (650+ lines)
**After**: SUMMARY.md (100 lines)

- Normal mode: Uses SUMMARY.md
- Deep mode (`--deep`): Uses full SKILL.md

### 3. Dual Agent System (Plan/Build)

**High-risk tasks** → Plan mode first (read-only analysis)

```
User: "Migrate database to PostgreSQL" (high risk)
  ↓
PLAN mode: Analysis, risks, steps
  ↓
User approves
  ↓
BUILD mode: Implementation
```

### 4. Prompt Caching

**First query**: 15K tokens
**Cached queries** (5min TTL): 5K tokens (67% reduction)

Automatically caches:
- Expert methodology
- Skill summaries
- Static project context

---

## 🔧 Monitoring & Analytics

### Token Usage Dashboard

```bash
# Analyze last 7 days
node analyze-tokens.js

# Comparison report (before/after optimization)
node analyze-tokens.js --comparison
```

**Output**:
```
📊 Token Usage Statistics (Last 7 days)

Token Usage:
  Total: 150,000
  Average: 10,000
  Range: 5,000 - 18,000

Caching:
  Hit Rate: 62.3%
  Avg Cached Tokens: 8,500

Optimization Usage:
  Lazy Loading: 95.0%
  Summaries: 98.0%
  Avg Skills Loaded: 1.2
```

---

## 🏗️ Architecture

### Plugin Structure

```
Agent007/                           # Root plugin directory
├── .claude-plugin/
│   └── plugin.json                 # Plugin manifest
│
├── agents/                         # 5 expert agents
│   ├── backend-db-expert.md
│   ├── frontend-ux-expert.md
│   ├── platform-expert.md
│   ├── product-expert.md
│   └── security-expert.md
│
├── skills/                         # 17 active skills
│   ├── architecture-patterns/
│   │   ├── SKILL.md               # Full details (650+ lines)
│   │   └── SUMMARY.md             # Quick reference (100 lines)
│   ├── resilience-patterns/
│   ├── api-design-principles/
│   ├── nestjs-code-reviewer/
│   ├── frontend-design/
│   ├── react-best-practices/
│   └── ...
│
├── commands/                       # Custom commands (optional)
│   └── consult/
│       ├── consult.md
│       └── lib/
│           ├── skill-selector.js      # Lazy loading
│           ├── skills-injector.js     # Summary vs full
│           ├── execution-mode.js      # Plan/Build modes
│           ├── prompt-builder.js      # Cache optimization
│           └── context-contracts.js   # Minimal context
│
├── settings.json                   # Default plugin configuration
├── README.md                       # This file
├── LICENSE                         # MIT
└── VERSION                         # Semantic versioning
```

### Legacy Structure (Deprecated)

The old `.claude/` directory structure is maintained for backward compatibility:

```
.claude/
├── agents/                  # Symlink to /agents/
├── skills/                  # Symlink to /skills/
├── commands/                # Symlink to /commands/
├── shared/                  # Shared utilities (deprecated)
└── metrics/                 # Token tracking (deprecated)
```

**Migration Note**: New installations should use the plugin structure. The `.claude/` directory is only needed for project-specific overrides.

---

## 🧪 Quality Enforcement (Always Active)

- **Verification**: No completion claims without actual test/build output
- **Anti-Rationalization**: No "should work" - only verified facts
- **Context-Awareness**: Read files before changing
- **CI/CD Validation**: Automatic validation on PRs

---

## 📚 Documentation

- **IMPLEMENTATION_PLAN.md** - Complete 13-task roadmap
- **OPTIMIZATION_COMPLETED.md** - Implementation status & next steps
- **OPENCODE_ADOPTION.md** - What we adopted from OpenCode and why

---

## 🎯 Workflow Example

```bash
# 1. User asks question
/consult "How to implement retry logic with exponential backoff?"

# 2. Orchestrator detects:
#    - Keywords: "retry", "exponential backoff"
#    - Risk: medium
#    - Expert: backend-db-expert

# 3. Lazy loading:
#    - Loads ONLY: resilience-patterns/SUMMARY.md
#    - Skips: api-design-principles, architecture-patterns

# 4. Response:
#    - Uses cached expert methodology (if available)
#    - Provides implementation steps
#    - Total tokens: ~10K (vs 60K before)
```

---

## 🚀 Next Steps

1. **Test optimizations**:
   ```bash
   /consult "circuit breaker for S3"
   # Verify lazy loading works
   ```

2. **Monitor token usage**:
   ```bash
   node analyze-tokens.js
   # Track actual savings
   ```

3. **Enable prompt caching** (optional):
   - Requires Anthropic API with caching support
   - See `.claude/shared/providers/cached-anthropic-client.js`

---

## 📄 License

MIT

---

**For detailed implementation guide, see IMPLEMENTATION_PLAN.md**
