---
name: resilience-patterns
description: "Circuit breakers, retries, timeouts, and bulkheads for fault-tolerant systems"
version: 1.0.0
allowed-tools: ["Read", "Grep", "Glob", "Edit", "Write", "Bash"]
load_when:
  - designing_external_service_calls
  - handling_distributed_system_failures
  - implementing_retry_logic
inputs:
  - name: failure_scenario
    type: string
    required: true
  - name: sla_requirements
    type: string
    required: false
outputs:
  - name: resilience_implementation
    type: string
    format: "TypeScript/NestJS with circuit breaker + retry + timeout"
  - name: failure_runbook
    type: checklist
    format: "Condition | Pattern to apply | Configuration values"
constraints:
  - every_external_call_needs_timeout
  - circuit_breaker_required_for_critical_dependencies
  - retry_with_exponential_backoff_not_fixed_interval
---

# Resilience Patterns — NestJS Monolith

Skill para implementar patrones de resiliencia en aplicaciones monolíticas NestJS, enfocado en integraciones externas (S3, email, APIs de terceros).

---

## When to Invoke

- Designing external service calls (S3, email, third-party APIs, payment gateways)
- Handling distributed system or cross-service failures
- Implementing retry logic for transient errors
- Adding fault tolerance to a monolith without microservices migration
- Defining health/liveness/readiness endpoints for orchestration

---

## Principios Fundamentales

**Objetivo**: mejorar la tolerancia a fallos sin migrar a microservicios.

**Patrones clave**:
1. Circuit Breaker — evitar cascadas de fallos
2. Retry con Exponential Backoff — reintentos inteligentes
3. Timeout — prevenir bloqueos
4. Health Checks — monitoreo proactivo
5. Graceful Degradation — funcionalidad reducida vs fallo total
6. Bulkhead — aislamiento de recursos

---

## Anti-Patterns

- **Llamada externa sin timeout** — un servicio caído cuelga toda la app indefinidamente.
- **Retry con delay fijo** — amplifica el problema en outages (retry storm). Usar exponential backoff.
- **Reintentar todos los errores** — reintentar errores 4xx/validación es inútil. Solo errores transitorios (network, 5xx, timeouts).
- **Circuit breaker sin estado HALF_OPEN** — sin probe de recuperación, queda OPEN para siempre.
- **Health check que toca todo** — si liveness verifica DB+S3+Redis, una falla de S3 reinicia el pod sin razón. Liveness = lo crítico, readiness = todo.
- **Graceful degradation silencioso** — degradar sin loggear ni alertar oculta problemas reales.
- **Sin pool isolation** — operaciones lentas (reportes) consumen workers de operaciones críticas (login).
- **Fallback que falla igual** — fallback a otro servicio del mismo proveedor con misma falla raíz.

---

## Need → Reference

| Need | Reference |
|------|-----------|
| Implementar circuit breaker (CLOSED/OPEN/HALF_OPEN) | `references/circuit-breaker.md` |
| Retry decorator con exponential/linear/fixed backoff | `references/retry-backoff.md` |
| Timeout decorator con `Promise.race` | `references/timeout.md` |
| Health checks (liveness, readiness, indicadores S3/Redis/DB) | `references/health-checks.md` |
| Degradación con fallbacks (filesystem local, cola, manual) | `references/graceful-degradation.md` |
| Bulkhead con `p-queue` y pools separados | `references/bulkhead.md` |

---

## Checklist de Implementación

- [ ] Circuit breakers en integraciones externas (S3, email, APIs)
- [ ] Retry con exponential backoff para fallos transitorios
- [ ] Timeouts agresivos (< 5s para APIs externas)
- [ ] Health checks (liveness + readiness)
- [ ] Graceful degradation para operaciones no críticas
- [ ] Bulkhead isolation para operaciones pesadas
- [ ] Logging de estados de circuit breakers
- [ ] Métricas de reintentos y fallos
- [ ] Fallbacks documentados

---

## Comandos de Uso

```bash
# Añadir circuit breaker a servicio
/resilience-patterns add-circuit-breaker:S3Service

# Implementar retry con backoff
/resilience-patterns add-retry:EmailService

# Configurar health checks
/resilience-patterns setup-health-checks

# Auditar resiliencia de integraciones
/resilience-patterns audit
```

---

## Referencias externas

- [NestJS Terminus Documentation](https://docs.nestjs.com/recipes/terminus)
- [Circuit Breaker Pattern - Microsoft](https://docs.microsoft.com/en-us/azure/architecture/patterns/circuit-breaker)
- [Retry Pattern - AWS](https://aws.amazon.com/builders-library/timeouts-retries-and-backoff-with-jitter/)
- [microservices.io patterns index](https://microservices.io/patterns/index.html)

## Sources

- https://microservices.io/patterns/index.html — microservice patterns
- https://docs.aws.amazon.com/whitepapers/latest/availability-and-beyond-improving-resilience/ — AWS resilience guidance
- https://docs.microsoft.com/en-us/azure/architecture/patterns/circuit-breaker — Circuit Breaker pattern reference
