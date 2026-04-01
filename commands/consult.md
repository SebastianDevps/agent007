---
name: consult
version: 4.0
description: Consulta inteligente a agentes expertos con auto-selección y skills injection
---

# /consult — Expert Consultation

Invocation: `/consult "question"` · `/consult "question" --deep` · `/consult "question" --experts backend,security`

---

## Step 1 — Select Expert (keyword match)

| Expert | Match keywords |
|--------|---------------|
| `backend-db-expert` | api, endpoint, architecture, nestjs, database, query, sql, schema, typeorm, microservice, performance, cache, redis, migration |
| `security-expert` | security, auth, jwt, oauth, owasp, vulnerability, permission, encryption, cors, xss, injection |
| `frontend-ux-expert` | react, next, component, ui, ux, design, wireframe, accessibility, performance, tailwind, state, form, gsap, animation, scroll, tween, timeline, stagger, parallax, motion |
| `platform-expert` | deploy, docker, ci/cd, test, tdd, coverage, pipeline, kubernetes, monitoring, infra, devops |
| `product-expert` | product, roadmap, user story, mvp, backlog, prioritize, rice, acceptance criteria, feature, discovery |

Select the expert with the most keyword matches. If tie or `--experts X,Y` flag: consult both sequentially, label each section clearly.

## Step 2 — Read Expert + Skills

1. Read `.claude/agents/{expert}.md`
2. Read the agent's listed skills from `.claude/skills/`

## Step 3 — Respond

Adopt the expert's perspective fully. Structure response as:

```
## [Expert Name] — [query summary]

[Recommendation — direct, no preamble]

## Key Considerations
[Trade-offs, caveats, context-specific factors]

## Implementation
[Concrete next steps or code if applicable]
```

**Mode limits**:
- default: 60 lines max
- `--deep`: 120 lines max, read all agent skills in full
- `--quick`: 25 lines max, skip skills loading

After responding, offer:
```
¿Segunda opinión de otro experto? [backend/security/frontend/platform/product] · [N]o
```
