---
name: decision-memory
description: "Registrar y consultar decisiones arquitectónicas pasadas. Para consistencia y aprendizaje organizacional."
invokable: false
auto-activate: true
version: 2.0.0
when:
  - after_task_completion: true
  - user_mentions: ["why did we", "past decision", "document decision", "adr"]
---

# Decision Memory - Organizational Learning

**Auto-inject**: true
**Priority**: low (runs after task completion)
**Version**: 2.0.0 (Runtime Implementation)

## Purpose

Capturar decisiones importantes para:
- Consistencia en futuras implementaciones
- Onboarding de nuevos miembros del equipo
- Evitar repetir debates ya resueltos
- Crear ADRs (Architecture Decision Records) automáticamente

**NEW in v2.0**: Persistent storage in `.claude/memory/` with searchable index.

---

## 💾 Storage Structure

All decisions, patterns, and lessons are stored in:
```
.claude/memory/
├── decisions/       # ADR-{number}-{slug}.md
├── patterns/        # PATTERN-{number}-{slug}.md
├── lessons/         # LESSON-{number}-{slug}.md
├── index.json       # Searchable metadata
└── README.md        # Documentation
```

---

## 📝 Post-Task Capture (EXECUTABLE)

After completing any significant task, you MUST offer:

```
✅ Task completed!

📚 Document this for future reference?
[P] Pattern - Reusable solution/approach discovered
[L] Lesson - Mistake avoided or learned from
[D] Decision - Architectural choice made (ADR)
[N] No documentation needed
```

### If User Selects [D] Decision:

1. **Read current index**:
   ```bash
   cat .claude/memory/index.json
   ```

2. **Get next ID**: Use `nextId.decision` from index

3. **Create ADR file** at `.claude/memory/decisions/ADR-{id}-{slug}.md` using template below

4. **Update index.json**:
   - Add entry to `decisions` array
   - Add tags to `tags` object
   - Increment `nextId.decision`

5. **Save both files**

### If User Selects [P] Pattern:

Same process, use `patterns/` directory and `nextId.pattern`

### If User Selects [L] Lesson:

Same process, use `lessons/` directory and `nextId.lesson`

---

## 🔍 Query Past Decisions (EXECUTABLE)

When user asks about past decisions:

**Examples**:
- "Did we decide on JWT vs sessions?"
- "What patterns do we use for database access?"
- "Have we seen N+1 query issues before?"

**Process**:

1. **Read index.json**:
   ```bash
   cat .claude/memory/index.json
   ```

2. **Search by keywords**:
   - Check `tags` object for matches
   - Check `title` fields for text matches
   - Filter by `status` (accepted, superseded, deprecated)

3. **Read matching files**:
   ```bash
   cat .claude/memory/decisions/ADR-{id}-{slug}.md
   ```

4. **Summarize findings**:
   ```
   📚 Past Decisions Found:

   **ADR-001: Use JWT with Refresh Tokens** (2026-02-20)
   - Status: Accepted
   - Decision: Use JWT access tokens (15 min) + refresh tokens (7 days)
   - Rationale: Stateless, mobile-friendly, industry standard
   - Tags: auth, security, jwt

   Applying this to your current question...
   ```

---

## 📋 Templates

### Decision Record Format (ADR)

```markdown
# ADR-[NUMBER]: [Title]

**Date**: [fecha]
**Status**: Accepted | Superseded | Deprecated
**Context**: [task/feature that prompted this decision]

## Problem
[What problem we were solving]

## Decision
[What we decided]

## Alternatives Considered
1. **[Alternative A]**: [Description]
   - Pros: [...]
   - Cons: [...]

2. **[Alternative B]**: [Description]
   - Pros: [...]
   - Cons: [...]

## Rationale
[Why we chose this option over alternatives]

## Consequences
- [Positive consequence 1]
- [Positive consequence 2]
- [Trade-off or negative consequence]

## Tags
- stack: [nestjs, typeorm, react, etc.]
- domain: [auth, payments, database, etc.]
- type: [pattern, lesson, architecture]
```

---

## Pattern Record Format

```markdown
# Pattern: [Name]

**Date**: [fecha]
**Applies to**: [stack/domain]

## Context
[When to use this pattern]

## Solution
[The pattern/approach]

## Code Example
[Working code example]

## When NOT to Use
[Anti-patterns or wrong contexts]

## Tags
- stack: [...]
- domain: [...]
```

---

## Lesson Record Format

```markdown
# Lesson: [Title]

**Date**: [fecha]
**Severity**: [High | Medium | Low]

## What Happened
[Description of the issue/mistake]

## Root Cause
[Why it happened]

## How We Fixed It
[Solution applied]

## How to Prevent
[What to do differently next time]

## Tags
- stack: [...]
- domain: [...]
```

---

## 💡 Example: Complete Workflow

### Scenario: User implements JWT authentication

1. **Task completes** - JWT auth implementation successful

2. **Claude offers**:
   ```
   ✅ Task completed!

   📚 Document this for future reference?
   [D] Decision - Architectural choice made (ADR)
   ```

3. **User selects [D]**

4. **Claude executes**:
   ```bash
   # Read current state
   cat .claude/memory/index.json  # nextId.decision = 1

   # Create ADR file
   # Write to .claude/memory/decisions/ADR-001-jwt-refresh-tokens.md

   # Update index with new entry
   # Increment nextId.decision to 2
   ```

5. **Result**: ADR-001 created and indexed

6. **Later**: User asks "How should I implement auth?"
   - Claude reads index.json → finds ADR-001
   - Reads ADR-001-jwt-refresh-tokens.md
   - Responds: "We already decided on JWT with refresh tokens in ADR-001. Here's the pattern..."

---

## 🔗 Integration Points

### With Brainstorming Skill

Before exploring new approaches, check:
```bash
# Search for relevant decisions
cat .claude/memory/index.json | grep -i "auth"
```

If found: "We already have ADR-001 on authentication. Let me review that first..."

### With Writing-Plans Skill

When creating implementation plan, reference patterns:
```
Step 3: Implement JWT auth
→ Reference: ADR-001-jwt-refresh-tokens.md
→ Pattern: PATTERN-003-nestjs-passport-jwt.md
```

### With Systematic-Debugging Skill

When debugging, check lessons:
```bash
# Have we seen this before?
cat .claude/memory/index.json | grep -i "n+1"
```

If found: "We encountered N+1 queries before (LESSON-002). The fix was..."

---

## 📊 Metrics (Future)

Track in index.json:
```json
{
  "stats": {
    "total_decisions": 5,
    "total_patterns": 8,
    "total_lessons": 3,
    "most_referenced": ["ADR-001", "PATTERN-002"],
    "last_updated": "2026-02-20"
  }
}
```
