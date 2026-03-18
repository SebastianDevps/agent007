---
name: sop-discovery
description: "Discover world-class reference implementations before designing. Prevents designing from scratch."
invokable: true
version: 1.0.0
---

# sop-discovery

> Discover world-class reference implementations before designing. Referent discovery prevents designing from scratch. Ported from ai-framework (Dario-Arcos).

---

## When to invoke

- Starting a new feature or system design
- Before `sop-planning` to find proven patterns
- When the user asks "how should we structure X"

---

## Referent Discovery Mode (new features)

Find 3-5 world-class existing implementations of the same or similar feature.

### Step 1 — Search for references

```
WebSearch("best [feature] implementation [tech stack] 2026")
WebSearch("[feature] architecture design [framework] github")
WebSearch("[company] engineering blog [feature]")
```

Target sources:
- GitHub repositories with high stars implementing this feature
- Engineering blogs from: Stripe, Netflix, Uber, Airbnb, GitHub, Shopify
- Official framework examples / starter kits

### Step 2 — Extract patterns from each reference

For each reference found, document:

| Aspect | What reference does | Why |
|--------|--------------------|----|
| Architecture | [description] | [reasoning] |
| Data model | [description] | [reasoning] |
| Testing approach | [description] | [reasoning] |
| Error handling | [description] | [reasoning] |
| Security | [description] | [reasoning] |

### Step 3 — Synthesize common patterns

Identify:
- **Universally adopted patterns** (appear in 4+ references) → must-have
- **Commonly adopted patterns** (appear in 2-3 references) → consider
- **Divergent approaches** (varies by reference) → decide based on our constraints

---

## Reverse Engineering Mode (existing code)

When the codebase already exists and you need to understand it.

### Step 1 — Entry points

```bash
# Find entry points
Glob("src/main.*")
Glob("src/index.*")
Glob("src/app.*")
```

### Step 2 — Dependency map

```bash
# Find imports and dependencies
Grep("import.*from", "src/", glob="*.ts")
# Build mental model of module relationships
```

### Step 3 — Data flow

Trace the path of a key entity through the system:
1. Where does it enter? (controller/route)
2. Where is it validated? (DTO/schema)
3. Where is it processed? (service)
4. Where is it stored? (repository/db)
5. Where is it returned? (serializer/transformer)

### Step 4 — Identify gaps and issues

Document:
- Missing layers (e.g., no input validation)
- Anti-patterns found
- Security concerns
- Performance bottlenecks

---

## Output Format

```markdown
## Discovery Report: [Feature/System]

### Reference Implementations Found
1. [Name] (url) — [why relevant]
2. [Name] (url) — [why relevant]
3. [Name] (url) — [why relevant]

### Universal Patterns (must implement)
- [Pattern 1]: [description]
- [Pattern 2]: [description]

### Recommended Approach
[Synthesis of best practices for our specific context]

### Key Decisions Required
- [Decision 1]: Options are A or B. Recommendation: A because [evidence]
- [Decision 2]: ...
```

---

## Integration

```
sop-discovery → sop-planning → sop-code-assist
```

Always run discovery before planning. Planning without references leads to reinventing patterns that have already been solved.

---

## See Also — When to Use sop-discovery vs brainstorming

| | **sop-discovery** | **brainstorming** |
|---|---|---|
| **Style** | Autonomous referent research | Socratic, interactive with user |
| **Direction** | Agent finds 3-5 world-class implementations | User refines requirements through questions |
| **Output** | Discovery report: patterns + must-haves + decisions | Refined requirements document |
| **Use when** | You need to learn from existing solutions before planning | Requirements are unclear or user wants to explore options |
| **Leads to** | `sop-planning` | `writing-plans` |

**Rule**: Use **sop-discovery** to learn *how to build it well*. Use **brainstorming** to clarify *what to build*.
