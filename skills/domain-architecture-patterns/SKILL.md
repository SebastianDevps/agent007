---
name: architecture-patterns
description: "Hexagonal, Clean, and Screaming architecture patterns for maintainable systems"
canonical-sources:
  - url: https://martinfowler.com/architecture/
    when: "for Martin Fowler architecture references"
  - url: https://www.cosmicpython.com/
    when: "for DDD/Hexagonal architecture patterns"
  - url: https://blog.cleancoder.com/uncle-bob/2012/08/13/the-clean-architecture.html
    when: "for Clean Architecture (Uncle Bob)"
  - url: https://www.domainlanguage.com/ddd/
    when: "for Domain-Driven Design (Eric Evans)"
version: 1.0.0
invokable: true
accepts_args: true
allowed-tools: ["Read", "Grep", "Glob", "Edit", "Write"]
load_when:
  - designing_system_architecture
  - reviewing_architectural_decisions
  - refactoring_for_scalability
inputs:
  - name: system_description
    type: string
    required: true
  - name: constraints
    type: string
    required: false
outputs:
  - name: architecture_decision
    type: structured_report
    format: "Pattern | Rationale | Trade-offs | Implementation steps"
constraints:
  - prefer_hexagonal_over_layered_for_complex_domains
  - domain_layer_must_not_depend_on_infrastructure
  - ports_and_adapters_for_all_external_dependencies
references:
  - references/clean-architecture-layers.md
  - references/bounded-contexts.md
  - references/module-structure.md
  - references/ddd-tactical.md
  - references/repository-pattern.md
  - references/dto-types-interfaces.md
  - references/refactor-workflow.md
---

# Architecture Patterns — NestJS Clean Architecture & DDD

Skill para implementar, auditar y refactorizar módulos siguiendo Clean Architecture y Domain-Driven Design en NestJS.

---

## When to Invoke

- Designing a new module or system architecture
- Reviewing architectural decisions on existing code
- Refactoring for scalability or maintainability
- Splitting a monolith into bounded contexts
- Identifying cross-context coupling that should be event-driven

---

## Principios Fundamentales

1. **Clean Architecture** — dependencias apuntan hacia el dominio (ver `references/clean-architecture-layers.md`)
2. **Bounded Contexts** — agrupación modular por dominio de negocio
3. **DDD táctico** — Aggregates, Value Objects, Domain Events
4. **Repository Pattern** — abstrae el acceso a datos
5. **DTOs vs Types vs Interfaces** — cada uno en su carpeta y propósito
6. **Límite duro**: 450 líneas por archivo (señal de múltiples responsabilidades)

---

## Anti-Patterns

- **Domain depende de framework u ORM** — viola la regla de dependencias; el dominio debe ser puro.
- **Cross-context import directo** — acopla bounded contexts; debe ser vía eventos o interfaces.
- **Lógica de negocio en controllers o services anémicos** — entidades sin comportamiento ("Anemic Domain Model"). Las reglas viven en el dominio.
- **Servicios instanciando dependencias con `new`** — rompe DI y testabilidad.
- **Archivo > 450 líneas** — múltiples responsabilidades; partir.
- **DTOs reutilizados como types de respuesta** — confunde validación de entrada con contrato de salida.
- **Shared global con lógica de dominio** — `shared/` solo debe tener infraestructura (DB, email, cache), no reglas de negocio.
- **Repository expuesto como TypeORM Repository directo en service** — el service queda atado al ORM.
- **Eventos sincrónicos para cross-context crítico** — un fallo del listener tumba al emisor; usar eventos asincrónicos o un bus.

---

## Need → Reference

| Need | Reference |
|------|-----------|
| Capas Clean Architecture y regla de dependencias | `references/clean-architecture-layers.md` |
| Estructura `src/modules/<context>/<module>/` y reglas de comunicación | `references/bounded-contexts.md` |
| Plantilla completa de un módulo (module/controller/service) | `references/module-structure.md` |
| Aggregates, Value Objects y Domain Events (DDD) | `references/ddd-tactical.md` |
| Repository Pattern con interfaz | `references/repository-pattern.md` |
| Cuándo usar DTO vs Type vs Interface y dónde van | `references/dto-types-interfaces.md` |
| Workflow paso a paso para refactor de un módulo | `references/refactor-workflow.md` |

---

## Checklist rápido por módulo

- [ ] Cada archivo < 450 líneas
- [ ] Carpetas `dto/`, `types/`, `interfaces/`, `entities/` separadas
- [ ] DI por constructor (sin `new` en services)
- [ ] Lógica de dominio en entidades (no anémicas)
- [ ] Repository pattern implementado
- [ ] Cross-context vía eventos (no imports directos)
- [ ] Value objects para conceptos invariantes (Money, Period, Email)

---

## Referencias externas

- [Clean Architecture - Robert C. Martin](https://blog.cleancoder.com/uncle-bob/2012/08/13/the-clean-architecture.html)
- [Domain-Driven Design - Eric Evans](https://www.domainlanguage.com/ddd/)
- [NestJS Modules Documentation](https://docs.nestjs.com/modules)
- [Martin Fowler — Architecture](https://martinfowler.com/architecture/)
