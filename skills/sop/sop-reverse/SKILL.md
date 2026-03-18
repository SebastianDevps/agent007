---
name: sop-reverse
description: "Reverse engineer an existing codebase to create scenarios and SOPs. Enables SDD on codebases built without it."
invokable: true
version: 1.0.0
---

# sop-reverse

> Reverse engineer an existing codebase to create scenarios and SOPs. Enables SDD on codebases that were built without it. Ported from ai-framework (Dario-Arcos).

---

## When to invoke

- Working on a codebase with no existing scenarios
- Refactoring existing code (understand current behavior before changing it)
- User asks to "understand this system", "document how X works"
- Before `sop-planning` on an existing feature

---

## Mode Selection

### Mode A: Referent Discovery (for new features on existing codebase)
Find how world-class implementations do what you're about to build, then map to local patterns.

### Mode B: System Reverse Engineering (for understanding existing code)
Build a behavioral specification from the code itself.

---

## Mode A: Referent Discovery

### Step 1 — Identify the feature to build
```
FEATURE: [name]
TECH STACK: [framework, db, etc.]
LOCAL CONSTRAINTS: [existing patterns to follow]
```

### Step 2 — Find 3-5 reference implementations
```
WebSearch("[feature] [framework] implementation github")
WebSearch("[feature] best practices [framework] 2026")
```

### Step 3 — Extract transferable patterns
For each reference:
- Data model decisions
- Service layer design
- Error handling patterns
- Testing approaches

### Step 4 — Map to local codebase
- Which patterns fit our existing conventions?
- Which patterns conflict? (need adaptation)
- Which patterns can be adopted as-is?

Output → feed into `sop-planning` as discovery context.

---

## Mode B: System Reverse Engineering

### Step 1 — Entry point mapping

```bash
# Find all route handlers / controllers
Grep("@Get\|@Post\|@Put\|@Delete\|@Patch", "src/", glob="*.ts")
Grep("router\.\(get\|post\|put\|delete\)", "src/", glob="*.js")
Grep("def.*route\|@app\.", "src/", glob="*.py")
```

### Step 2 — Data flow tracing

Pick the most important endpoint. Trace:
```
Request → Middleware → Controller → DTO validation → Service → Repository → DB
Response → Transformer → Serializer → Controller → Response
```

Read each file in the chain.

### Step 3 — Behavioral documentation

For each endpoint/feature found, write a scenario that describes current behavior:

```markdown
## Existing Behavior: POST /auth/login

### Scenario 1: Successful login
Given: email "user@example.com" exists with password "correct"
When: POST /auth/login {email, password}
Then: 200 OK with {accessToken, refreshToken, user: {id, email}}

### Scenario 2: Invalid credentials
Given: email "user@example.com" exists with wrong password
When: POST /auth/login {email, wrongPassword}
Then: 401 Unauthorized with {message: "Invalid credentials"}
```

### Step 4 — Gap analysis

Compare documented behavior against existing tests:
- What behavior has no tests? → write tests
- What tests have no scenario? → write scenarios
- What behavior is undocumented? → verify and document

### Step 5 — Risk identification

Flag:
- Any behavior that would break if changed (high traffic, core user flow)
- Any code that is not tested (risky to refactor)
- Any security concerns found during reading

---

## Output

```markdown
# Reverse Engineering Report: [System/Feature]

## Entry Points
[List of routes/endpoints found]

## Data Flow
[Trace of main entity through system]

## Behavioral Scenarios
[Scenarios for each significant behavior]

## Gap Analysis
- Missing tests: [list]
- Missing scenarios: [list]
- Undocumented behavior: [list]

## Risk Areas
[High-risk areas identified]

## Recommended Next Steps
1. [Most important action]
2. [Second action]
```

---

## Integration

```
[sop-reverse] → sop-planning → sop-code-assist
```

For refactors: reverse-engineer first to capture current behavior as scenarios,
then refactor using those scenarios as the holdout set.
