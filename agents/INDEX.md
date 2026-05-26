# Agents INDEX — Agent007

| Agent | Model | Trigger Keywords | Associated Skills |
|-------|-------|-----------------|-------------------|
| `backend-db-expert` | opus | api, endpoint, architecture, nestjs, database, query, sql, schema, typeorm, microservice, performance, cache, redis, migration, retry, resilience, circuit-breaker, rate-limit | domain-api-design-principles, domain-architecture-patterns, domain-resilience-patterns |
| `code-reviewer` | sonnet | code review, review, check quality, review pr, quality check, audit code, review changes, review diff | domain-nestjs-code-reviewer, quality-enforcement |
| `frontend-ux-expert` | sonnet | react, next, component, ui, ux, design, wireframe, accessibility, performance, tailwind, state, form | domain-react-best-practices, domain-frontend-design |
| `loop-operator` | sonnet | loop, ralph, autonomous, until, iterate, run until, loop until, retry until, keep running | ralph-loop-wrapper (docs/orchestration/), state-sync, context-awareness |
| `platform-expert` | sonnet | deploy, docker, ci/cd, test, tdd, coverage, pipeline, kubernetes, monitoring, infra, devops | subagent-driven-development, quality-gates-systematic-debugging |
| `product-expert` | opus | product, roadmap, user story, mvp, backlog, prioritize, rice, acceptance criteria, feature, discovery | product-product-discovery |
| `refactor-cleaner` | sonnet | dead code, unused, clean up, remove unused, depcheck, knip, ts-prune, prune dependencies, cleanup imports | sop-reverse |
| `security-expert` | opus | security, auth, jwt, oauth, owasp, vulnerability, permission, encryption, cors, xss, injection | domain-security-review |

## Removed in v6 refactor (2026-05-06)

| Agent | Reason | Replacement |
|---|---|---|
| `architect` | Orphan — duplicated `architecture-patterns` skill, no handoff routes in/out | Use `Skill('domain-architecture-patterns')` directly |
| `performance-optimizer` | Orphan — expertise extracted into dedicated skill | Use `Skill('quality-gates-performance-profiling')` (`skills/quality-gates-performance-profiling/`) |
