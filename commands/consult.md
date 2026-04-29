---
name: consult
version: 1.0
description: "Route question to the correct expert agent based on keyword matching"
accepts_args: true
preconditions:
  - question_provided
outputs:
  - name: expert_recommendation
    type: structured_report
    format: "Recommendation | Key considerations | Implementation steps"
  - name: decisions_md
    type: string
    format: ".sdlc/context/DECISIONS.md — only for concrete technical decisions"
steps_count: 3
triggers:
  - "should I"
  - "recommend"
  - "best practice"
  - "compare"
  - "explain"
routing:
  backend-db-expert: [api, endpoint, architecture, nestjs, database, query, sql, typeorm, redis, migration]
  security-expert: [security, auth, jwt, oauth, owasp, vulnerability, encryption, cors, xss]
  frontend-ux-expert: [react, next, component, ui, ux, design, accessibility, tailwind, gsap]
  platform-expert: [deploy, docker, ci/cd, test, tdd, pipeline, kubernetes, monitoring]
  product-expert: [product, roadmap, user story, mvp, backlog, prioritize, rice, feature]
flags:
  --deep: "120 lines max, read all agent skills in full"
  --quick: "25 lines max, skip skills loading"
---

# /consult — Expert Consultation

Invocation: `/consult "question"` · `/consult "question" --deep` · `/consult "question" --experts backend,security`

---

## Step 1 — Select Expert (keyword match)

| Expert | Match keywords |
|--------|---------------|
| `backend-db-expert` | api, endpoint, architecture, nestjs, database, query, sql, schema, typeorm, microservice, performance, cache, redis, migration, retry, resilience, circuit-breaker, rate-limit |
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
¿Convertir estas recomendaciones en prompt ejecutable? /prompt-gen "[objetivo]" · [N]o
```

## Step 4 — Write DECISIONS.md (conditional)
Only write `.sdlc/context/DECISIONS.md` if the consultation resulted in:
- A concrete technical approach being recommended
- A choice between alternatives being made  
- Something that will be implemented with `/dev`

**Skip** if the consultation was:
- A factual/conceptual question ("what is X", "how does Y work")
- Pure exploration with no decision reached
- A quick lookup (`--quick` mode)

When writing, use this format:
\`\`\`markdown
# Decisions — [topic]
## Approach chosen: [one line]
[explanation]
## Rationale
[key reasons]
## Alternatives discarded
- [Option]: [why not]
## Next steps for /dev
[what to implement]
\`\`\`

Create `.sdlc/context/` if it doesn't exist. Overwrite if file exists.
