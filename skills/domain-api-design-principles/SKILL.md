---
name: api-design-principles
description: "RESTful API design principles for consistent, versioned, developer-friendly APIs"
version: 1.0.0
allowed-tools: ["Read", "Grep", "Glob", "Edit", "Write"]
load_when:
  - designing_api_endpoints
  - reviewing_api_contracts
  - creating_openapi_specs
inputs:
  - name: api_scope
    type: string
    required: true
  - name: existing_endpoints
    type: array
    required: false
outputs:
  - name: api_contract
    type: structured_report
    format: "Method | Path | Request | Response | Status codes"
  - name: openapi_snippet
    type: string
    format: "YAML OpenAPI 3.0"
constraints:
  - versioning_required_in_all_public_apis
  - no_breaking_changes_without_version_bump
  - consistent_error_response_format_enforced
---

# API Design Principles — NestJS & TypeORM

Skill para diseñar, implementar y auditar APIs REST siguiendo mejores prácticas en NestJS.

---

## When to Invoke

- Designing new API endpoints (new module or extending existing)
- Reviewing or auditing API contracts
- Creating or updating OpenAPI / Swagger specifications
- Adding pagination, filtering, sorting to list endpoints
- Establishing versioning strategy
- Standardizing error responses across the application

---

## Principios Fundamentales

1. **Resource-oriented URLs** — sustantivos plurales, sin verbos
2. **HTTP semantics correctos** — GET/POST/PATCH/DELETE + status codes apropiados
3. **Paginación obligatoria** en listados
4. **Filtrado y ordenamiento** explícitos vía DTO
5. **Versionado por URL** (`/api/v1/`)
6. **Errores consistentes** con `{ statusCode, message, errors?, timestamp, path, method }`
7. **Respuestas con patrón** `{ status, message, data }` (o `data + meta` paginado)
8. **Swagger completo** — `@ApiOperation`, `@ApiResponse`, `@ApiBody`, ejemplos

---

## Anti-Patterns

- **Verbos en URL** (`/getUser`, `/createCutoff`, `/cutoffs/delete/:id`) — usar el método HTTP.
- **Singular en colecciones** (`/user/123`) — siempre plural (`/users/123`).
- **Status code incorrecto** — devolver 200 en POST de creación (debe ser 201), o 200 en error.
- **Listados sin paginación** — caída de performance y memoria al crecer datos.
- **Sin límite máximo de page size** — un cliente pidiendo `limit=10000` tumba el servicio.
- **Errores con shape inconsistente** — cada endpoint devuelve un formato distinto, los clientes no pueden manejarlos.
- **Sin versionado** — un breaking change rompe a todos los clientes.
- **Breaking changes sin bump de versión** — viola contrato; siempre `v2`.
- **DTOs reusados como respuestas** — confunde validación de entrada con shape de salida.
- **Swagger ausente o incompleto** — clientes y QA dependen de leer el código.
- **Filtros como query params libres** — sin DTO con `class-validator` permite SQL injection / abuso.

---

## Need → Reference

| Need | Reference |
|------|-----------|
| Convenciones de URLs y recursos | `references/resource-oriented-urls.md` |
| Métodos HTTP, status codes, idempotencia | `references/http-semantics.md` |
| `PaginationDto` + `PaginatedResponse<T>` con meta | `references/pagination.md` |
| `FiltersDto` con `sortBy`, `sortOrder`, filtros validados | `references/filtering-sorting.md` |
| Estrategia de versionado por URL y deprecación | `references/versioning.md` |
| `ErrorResponse` + `AllExceptionsFilter` global | `references/error-handling.md` |
| Decoradores `@ApiOperation`, `@ApiResponse`, ejemplos | `references/swagger-docs.md` |
| Workflow de auditoría de un módulo existente | `references/audit-workflow.md` |

---

## Checklist rápido por endpoint

- [ ] URL en plural, sustantivo, sin verbos
- [ ] Método HTTP correcto + status code esperado
- [ ] DTO de entrada con `class-validator`
- [ ] Type de respuesta `{ status, message, data }`
- [ ] Paginación si es listado
- [ ] Documentación Swagger con ejemplo de éxito y error
- [ ] Errores siguen `ErrorResponse` global
- [ ] Prefix `/api/v{N}/` aplicado

---

## Referencias externas

- [REST API Design Best Practices](https://restfulapi.net/)
- [NestJS OpenAPI Documentation](https://docs.nestjs.com/openapi/introduction)
- [HTTP Status Codes Reference](https://developer.mozilla.org/en-US/docs/Web/HTTP/Status)
- [JSON:API specification](https://jsonapi.org/)

## Sources

- https://restfulapi.net/ — REST design principles
- https://docs.nestjs.com/openapi/introduction — OpenAPI/Swagger integration with NestJS
- https://jsonapi.org/ — JSON:API specification
- https://developer.mozilla.org/en-US/docs/Web/HTTP/Status — HTTP status codes reference
