---
name: pull-request
description: "Create well-structured GitHub PRs with summary, test plan, and rollback plan. Invokes /pull-request command logic."
invokable: true
accepts_args: true
version: 1.0.0
when:
  keywords: ["pull request", "pr", "open pr", "create pr", "github pr"]
---

# Pull Request — Structured PR Creation

Delegates to the `/pull-request` command. See `.claude/commands/pull-request.md` for the full protocol.

## PR Template (secciones obligatorias)

```markdown
## Summary
- Qué se implementó y por qué (1–3 bullets)

## Motivation
- Por qué se necesitaba este cambio (link a ticket si aplica)

## Test Plan
- [ ] Pasos concretos de verificación

## Breaking Changes
- Ninguno / descripción si los hay

## Rollback Plan
- Cómo revertir si esto rompe producción
```

## Título del PR

```
tipo — Descripción imperativa en inglés (max 70 chars)
```

Ejemplos:
```
feat — Add user authentication with JWT refresh rotation
fix — Resolve null pointer in UserService.findById
refactor — Extract payment service to shared module
```

Sin footer de herramientas. Sin Co-Authored-By. Solo contenido de la empresa.

## Invocation

```
Skill('pull-request')
```

Corre: `git log` desde divergencia con main → draft PR title + body → `gh pr create` con template completo.
