---
name: api-documentation
description: "Crear documentación de API: OpenAPI specs, guides, error catalogs. Use when user asks to 'document API', 'create API docs', 'generate OpenAPI spec', or 'write API guide'."
allowed-tools: ["Read", "Write", "Grep", "Glob"]
auto-activate: false
version: 1.0.0
when:
  - task_type: documentation
  - user_mentions: ["api docs", "documentation", "openapi", "swagger", "developer portal"]
---

# API Documentation — Developer-First Documentation

**Propósito**: Crear documentación de API que permita a developers obtener valor en menos de 10 minutos.

---

## Estructura de Documentación (Diátaxis)

La documentación se organiza en cuatro bloques. Los templates concretos viven en `references/`.

| # | Bloque | Goal | Template |
|---|--------|------|----------|
| 1 | Quick Start | Time-to-first-call < 5 min | `references/quickstart-auth.md` |
| 2 | Authentication | Cómo autenticar + best practices | `references/quickstart-auth.md` |
| 3 | API Reference | Endpoint-by-endpoint, request + response | `references/api-reference.md` |
| 4 | Error Catalog | Códigos, mensajes, fixes | `references/error-catalog.md` |

**Reglas de los templates:**
- Quick start incluye obtener API key + primer request + crear recurso
- Auth siempre cubre Bearer tokens, key types (live/test) y security DOs/DON'Ts
- Reference define base URL, formato de respuesta (success/error) y paginación antes de los endpoints
- Cada endpoint trae: query params, body, ejemplo curl, ejemplo response, tabla de status codes
- Error catalog agrupa por status code (401, 403, 400, 429) con fix sugerido para cada error code

---

## Process: Documentar un Módulo

**Input**: Nombre del módulo a documentar (ej: "users", "projects", "payments")

**Steps**:

1. **Read controller**: identificar endpoints, DTOs, responses
2. **Read service**: entender business logic, validaciones, errores
3. **Read DTOs**: extraer field definitions y validaciones
4. **Generate OpenAPI**: crear o actualizar spec
5. **Write examples**: curl + response por cada endpoint
6. **Document errors**: todos los error scenarios posibles
7. **Create guide**: how-to para casos comunes

---

## Quality Checklist

- [ ] **Quick start works** in < 10 minutes (tested)
- [ ] **Every endpoint** has working curl example
- [ ] **Every endpoint** has example response
- [ ] **All error codes** documented with fix suggestions
- [ ] **Authentication** clearly explained with security warnings
- [ ] **Rate limits** documented
- [ ] **Pagination** pattern documented
- [ ] **Examples use realistic data** (not foo/bar)
- [ ] **OpenAPI spec** matches actual implementation
- [ ] **Changelog** exists for breaking changes

---

## Anti-patterns (NEVER)

- ❌ Empezar por la API reference sin quick start — el dev se va antes de leer
- ❌ Ejemplos con `foo`/`bar`/`test123` — siempre datos realistas (`sk_live_…`, `proj_abc123`)
- ❌ Documentar response sólo en happy path — listar también 400/401/403/409
- ❌ Hardcodear API keys en ejemplos público (mostrar formato, no secret real)
- ❌ Mencionar autenticación pero no rotación / revocación / live vs test keys
- ❌ Usar lenguaje vago ("normalmente", "deberías") en lugar de status code exacto
- ❌ Omitir paginación — toda lista debe declarar `page` / `limit` / `total`
- ❌ Dejar la OpenAPI spec sin sincronizar con la implementación (drift)

## Required (ALWAYS)

- ✅ Quick start primero, reference después
- ✅ curl + response por endpoint
- ✅ Tabla de status codes por endpoint
- ✅ Error catalog separado y enlazable

---

**Next Step**: Generate OpenAPI spec from code → Create static site → Deploy developer portal
