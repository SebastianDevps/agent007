# Agents INDEX — Agent007

| Agent | Model | Trigger Keywords | Associated Skills |
|-------|-------|-----------------|-------------------|
| `architect-reviewer` | opus | architecture review, design review, boundary check, pattern consistency, module boundary, bounded context, coupling, cohesion, technical debt review, modernization | domain-architecture-patterns, domain-api-design-principles, verify, consult-critique |
| `backend-db-expert` | opus | api, endpoint, architecture, nestjs, database, query, sql, schema, typeorm, microservice, performance, cache, redis, migration, retry, resilience, circuit-breaker, rate-limit | domain-api-design-principles, domain-architecture-patterns, domain-resilience-patterns |
| `code-reviewer` | sonnet | code review, review, check quality, review pr, quality check, audit code, review changes, review diff | domain-nestjs-code-reviewer |
| `docs-architect` | haiku | docs, documentation, technical writing, readme, getting started, onboarding doc, system overview, architecture guide | writing-skills, devrel-api-documentation, domain-design-system-doc, deep-research |
| `error-coordinator` | opus | subagent failure, cascading failure, recovery, retry, BLOCKED status, multi-agent error, dispatch failure, fan-out failure | agent-self-diagnosis, quality-gates-systematic-debugging, verify |
| `frontend-ux-expert` | sonnet | react, next, component, ui, ux, design, wireframe, accessibility, performance, tailwind, state, form | domain-discovery-before-code, domain-frontend-design, domain-react-best-practices, domain-gsap, domain-shadcn-component-install, domain-a11y-contrast-check, domain-design-tokens-extract, domain-design-system-doc, domain-page-transitions-barba, domain-ios-hig-mobile, domain-spline-3d-embed |
| `incident-responder` | opus | incident, outage, sev1, sev2, p0, p1, postmortem, downtime, breach, on-call, pager, runbook, rollback, mttr | quality-gates-systematic-debugging, verify, domain-security-review, domain-resilience-patterns |
| `loop-operator` | sonnet | loop, ralph, autonomous, until, iterate, run until, loop until, retry until, keep running | ralph-loop-wrapper |
| `observability-engineer` | sonnet | observability, monitoring, metrics, logs, traces, prometheus, grafana, opentelemetry, datadog, sli, slo, error-budget, alert, dashboard, apm, telemetry, golden-signals | quality-gates-performance-profiling, verify, domain-resilience-patterns |
| `platform-expert` | sonnet | deploy, docker, ci/cd, test, tdd, coverage, pipeline, kubernetes, monitoring, infra, devops | quality-gates-systematic-debugging |
| `product-expert` | opus | product, roadmap, user story, mvp, backlog, prioritize, rice, acceptance criteria, feature, discovery | product-product-discovery |
| `refactor-cleaner` | sonnet | dead code, unused, clean up, remove unused, depcheck, knip, ts-prune, prune dependencies, cleanup imports | sop-reverse |
| `security-expert` | opus | security, auth, jwt, oauth, owasp, vulnerability, permission, encryption, cors, xss, injection | domain-security-review |

## Removed in v6 refactor (2026-05-06)

| Agent | Reason | Replacement |
|---|---|---|
| `architect` | Orphan — duplicated `domain-architecture-patterns` skill, no handoff routes in/out | Use `Skill('domain-architecture-patterns')` directly |
| `performance-optimizer` | Orphan — expertise extracted into dedicated skill | Use `Skill('quality-gates-performance-profiling')` (`skills/quality-gates-performance-profiling/`) |
