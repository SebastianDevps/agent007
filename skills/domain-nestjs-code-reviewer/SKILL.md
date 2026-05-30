---
name: nestjs-code-reviewer
version: 1.0.0
description: "Revisa código NestJS + TypeORM siguiendo mejores prácticas, detecta vulnerabilidades OWASP y anti-patterns. Use when user asks to 'review code', 'audit module', or 'check security'."
allowed-tools: ["Read", "Grep", "Bash"]
---

# NestJS Code Reviewer

Skill especializado para revisar código de aplicaciones NestJS con TypeORM y PostgreSQL, enfocado en calidad, seguridad y arquitectura.

## When to Use

Activa este skill cuando el usuario:
- Pida "revisar código", "code review", "auditar"
- Mencione "mejores prácticas", "clean code", "refactorizar"
- Pregunte "¿está bien este código?", "¿hay bugs?"
- Solicite validación de seguridad o performance

---

## Review Checklist (6 layers)

Cada layer tiene su archivo de referencia con ejemplos antes/después.

| # | Layer | Foco | Reference |
|---|-------|------|-----------|
| 1 | Arquitectura NestJS | Controllers delegan, DTOs validan, DI por constructor | `references/architecture-patterns.md` |
| 2 | TypeORM | N+1, transacciones, índices, repositorios | `references/architecture-patterns.md` + `references/TYPEORM_ANTIPATTERNS.md` |
| 3 | Seguridad OWASP Top 10 | SQLi, AuthN/Z, sensitive data, mass assignment | `references/security-owasp.md` + `references/SECURITY_CHECKLIST.md` |
| 4 | Performance | Connection pooling, caching, paginación obligatoria | `references/performance-typescript.md` |
| 5 | TypeScript Quality | Sin `any`, errores tipados de NestJS, async/await correcto | `references/performance-typescript.md` |
| 6 | Testing | >80% coverage en servicios críticos, integration + E2E | `references/performance-typescript.md` |

**Regla**: leer las referencias relevantes antes de aplicar el checklist al módulo. No improvisar criterios — usar los snippets como ground truth.

---

## Cómo Usar Este Skill

### Paso 1: Identificar archivos a revisar
```bash
rg "class.*Controller" src/
rg "class.*Service" src/
rg "@Entity" src/
```

### Paso 2: Leer código y aplicar checklist
- Leer cada archivo con `Read tool`
- Comparar contra los patrones en las referencias
- Identificar violaciones (❌) y buenas prácticas (✅)

### Paso 3: Generar reporte
```markdown
## 🔴 CRÍTICO (fix inmediato)
- `src/users/users.controller.ts:42` - SQL Injection vulnerable
- `src/auth/auth.service.ts:15` - Password sin hash

## 🟡 MEJORAS (refactor recomendado)
- `src/products/products.service.ts:28` - Query N+1
- `src/orders/orders.controller.ts:12` - Lógica de negocio en controller

## ✅ BUENAS PRÁCTICAS DETECTADAS
- Uso correcto de DTOs con validación
- Transacciones en operaciones críticas
```

### Paso 4: Sugerir código mejorado
Para cada issue, snippet corregido en formato:
```typescript
// Archivo: src/path/to/file.ts:línea

// ❌ ANTES
[código problemático]

// ✅ DESPUÉS
[código corregido]

// 📝 RAZÓN
[explicación breve]
```

---

## Output Format

```markdown
# Code Review: [Módulo/Feature]

## Resumen
- Archivos revisados: X
- Issues críticos: Y
- Mejoras sugeridas: Z
- Score de calidad: A/B/C

## 🔴 Issues Críticos
[lista con file:line]

## 🟡 Mejoras Recomendadas
[lista con file:line]

## ✅ Aspectos Positivos
[buenas prácticas encontradas]

## Sugerencias de Refactor
[código antes/después]
```

---

## Anti-patterns (NEVER)

- ❌ Aprobar PR con `any` salvo justificación explícita y documentada
- ❌ Aprobar SQL crudo construido con template literals (`${}`) — siempre parámetros preparados
- ❌ Marcar como OK un endpoint sin guards en operaciones que mutan estado
- ❌ Aprobar `@Body() data: any` en POST/PATCH — siempre DTO con `class-validator`
- ❌ Marcar como OK lógica de negocio dentro del controller
- ❌ Aceptar código que retorna passwords / secrets / tokens en la respuesta (usar `@Exclude()`)
- ❌ Aprobar `find()` sin paginación en endpoints de listado
- ❌ Aceptar imports estáticos de servicios — siempre constructor injection
- ❌ Saltar criterios sin leer la reference correspondiente — improvisar pierde rigor

## Required (ALWAYS)

- ✅ Reportar `file:line` para cada hallazgo
- ✅ Explicar el "por qué" del issue, no solo el "qué"
- ✅ Sugerir snippet antes/después en cada refactor crítico
- ✅ Priorizar OWASP sobre estilo

---

## Limitaciones

Este skill NO cubre:
- Performance profiling (usa Clinic.js o 0x)
- Dependency vulnerabilities (usa `npm audit`)
- Infrastructure/DevOps (usa otro skill)

---

## Tips para el Agente

1. **Prioriza seguridad**: Issues OWASP son críticos
2. **Sé específico**: Siempre menciona `file:line`
3. **Da contexto**: Explica el "por qué", no solo el "qué"
4. **Sugiere, no impongas**: Usa "considera..." en lugar de "debes..."
5. **Limita scope**: Si hay >10 files, pide al usuario enfocarse en un módulo

## Sources

- https://docs.nestjs.com/ — NestJS official documentation
- https://typeorm.io/ — TypeORM documentation
- https://owasp.org/www-project-top-ten/ — OWASP Top 10 references
