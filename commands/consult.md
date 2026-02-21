---
name: consult
version: 3.0
description: Consulta inteligente a agentes expertos con auto-selección, context scanning, y skills injection
---

# /consult v3.0 - Intelligent Expert Consultation

**EXECUTION MODE**: This command now ACTUALLY executes agents and returns consolidated responses.

When the user invokes `/consult "question" [--mode]`, you MUST follow this execution flow:

---

## EXECUTION INSTRUCTIONS FOR CLAUDE

### Step 1: Parse Arguments

Extract from user input:
- **query**: The question (required)
- **mode**: --quick, --normal (default), or --deep
- **force-experts**: Optional list like `--experts backend,security`

### Step 2: Detect Project Context

Scan the current project to detect:
- **Framework**: Look for package.json (NestJS, Express, Next.js, React)
- **Database**: Look for docker-compose.yml, config files (PostgreSQL, MongoDB, Redis)
- **Language**: TypeScript, JavaScript, Python, Go
- **ORM**: TypeORM, Prisma, Mongoose
- **Testing**: Jest, Vitest, Playwright

Quick scan pattern:
```
Read package.json → Check dependencies
Read tsconfig.json → Check TS config
Grep "TypeORM|Prisma|Mongoose" in src/
```

### Step 3: Select Experts

Use keyword matching to select 1-3 experts based on mode:

**Available Experts (5)**:
| Expert | Keywords | Model | Skills |
|--------|----------|-------|--------|
| backend-db-expert | api, endpoint, microservice, architecture, nestjs, database, query, sql, schema, orm, typeorm | opus | api-design-principles, architecture-patterns, resilience-patterns |
| security-expert | security, auth, jwt, oauth, vulnerability, owasp | opus | nestjs-code-reviewer |
| frontend-ux-expert | react, next, component, ui, performance, ssr, ux, design, wireframe, prototype, accessibility | sonnet | react-best-practices, frontend-design |
| platform-expert | deploy, docker, ci/cd, kubernetes, infrastructure, test, tdd, coverage, quality | sonnet | workflow/tdd, quality-gates/systematic-debugging |
| product-expert | product, roadmap, user story, mvp, backlog, sprint, rice, acceptance criteria | opus | product/product-discovery |

**Selection Rules**:
- `--quick`: 1 expert (highest keyword match), use haiku
- `--normal`: 1-2 experts (top matches), use sonnet
- `--deep`: 2-3 experts (top matches + complementary), use opus for critical agents

**Keyword Matching**:
Count keyword occurrences in query. Select experts with highest scores.
If multiple experts have similar scores, prefer complementary perspectives (e.g., backend + security for auth questions).

### Step 4: Load Skills for Each Expert

For each selected expert, read their associated skills from `.claude/skills/`:

Example for backend-expert:
```
Read .claude/skills/api-design-principles/SKILL.md
Read .claude/skills/architecture-patterns/SKILL.md
Read .claude/skills/resilience-patterns/SKILL.md
```

Skills provide checklists, patterns, and best practices that enhance the expert's response.

### Step 5: Execute Consultation (CRITICAL)

**Launch agents in PARALLEL** using Task tool with one message containing multiple tool calls:

```
For each selected expert:
  - Build enhanced prompt with:
    * Expert role and methodology (from .claude/agents/{expert}.md)
    * Project context detected
    * Skills content loaded
    * User's question
    * Response length limit based on mode
  - Use Task tool with appropriate model (opus/sonnet/haiku)
```

**Example**:
```
Task(backend-db-expert, opus, "You are backend-db-expert. Context: NestJS + TypeORM + PostgreSQL.
Skills: [api-design-principles content]. Question: How to implement JWT auth? Max 50 lines.")

Task(security-expert, opus, "You are security-expert. Context: NestJS + TypeORM + PostgreSQL.
Skills: [nestjs-code-reviewer content]. Question: How to implement JWT auth securely? Max 50 lines.")
```

### Step 6: Consolidate Responses

After all agents respond:
1. **Extract consensus**: What do all experts agree on?
2. **Highlight differences**: Where do they disagree and why?
3. **Synthesize recommendation**: Unified advice incorporating all perspectives
4. **Remove redundancy**: Don't repeat the same point from multiple experts

### Step 7: Format Final Response

```markdown
# Consultation: {query}

**Experts Consulted**: {list of experts}
**Project Context**: {framework, database, language detected}

## Consolidated Recommendation

{Synthesized advice from all experts, 50-100 lines max}

## Consensus Points
- {Point all experts agree on}
- {Another consensus point}

## Trade-offs Discussed
- **Expert A**: {perspective}
- **Expert B**: {alternative perspective}

## Implementation Steps
1. {Step 1}
2. {Step 2}
...

## Resources
- {Relevant patterns/skills referenced}
```

---

## Mode-Specific Limits

- **--quick**: 1 expert, haiku, 30 lines max
- **--normal**: 1-2 experts, sonnet, 50 lines max
- **--deep**: 2-3 experts, opus, 100 lines max

---

## Anti-Patterns to Avoid

❌ **Do NOT** just return a JSON object or preparation message
❌ **Do NOT** launch agents sequentially (use parallel Task calls)
❌ **Do NOT** copy-paste full agent responses (consolidate them)
❌ **Do NOT** forget to load skills for each expert

✅ **DO** execute agents and return real answers
✅ **DO** detect project context automatically
✅ **DO** consolidate responses to remove redundancy
✅ **DO** respect length limits

---

## Debugging

If execution fails:
1. Check that agent files exist in `.claude/agents/`
2. Verify skills exist in `.claude/skills/`
3. Ensure Task tool is available
4. Log which experts were selected and why
