---
name: commit
description: "Genera commits con el formato estándar de la empresa: Tipo|IdTarea|YYYYMMDD|Descripción. Sin footers externos."
invokable: true
accepts_args: true
version: 1.0.0
when:
  keywords: ["commit", "save changes", "checkpoint", "git commit"]
---

# Commit — Formato Estándar de la Empresa

## Formato

```
Tipo|IdTarea|YYYYMMDD|Descripción imperativa en inglés
```

| Componente | Descripción |
|------------|-------------|
| `Tipo` | Naturaleza del cambio (ver tabla abajo) |
| `IdTarea` | ID del ticket / tarea (omitir entre pipes si no hay) |
| `YYYYMMDD` | Fecha del commit — siempre correr `date +%Y%m%d` |
| `Descripción` | Acción en inglés, modo imperativo, máx 60 caracteres |

## Tipos válidos

| Tipo | Cuándo usarlo |
|------|---------------|
| `feat` | Nueva funcionalidad |
| `fix` | Corrección de bug |
| `refactor` | Reestructuración sin cambio de comportamiento |
| `test` | Tests nuevos o ajustados |
| `docs` | Solo documentación |
| `chore` | Mantenimiento, configuración menor |
| `review` | Ajustes post code-review |
| `perf` | Mejora de rendimiento |
| `ci` | Cambios en pipeline CI/CD |

## Ejemplos canónicos

```
feat|PROJ-042|20260402|Add JWT refresh token rotation
fix|PROJ-101|20260402|Resolve null deref in UserService.findById
refactor|PROJ-015|20260402|Extract payment logic to PaymentService
test|PROJ-042|20260402|Add unit tests for JWT refresh flow
docs|PROJ-007|20260402|Update API reference for auth endpoints
chore|20260402|Upgrade TypeScript to 5.4
```

## Protocolo de ejecución

### 1. Revisar estado

```bash
git status
git diff --staged
git log --oneline -5
date +%Y%m%d
```

### 2. Stagear archivos específicos

```bash
# Siempre por nombre — nunca git add -A sin revisar
git add src/auth/auth.service.ts src/auth/auth.controller.ts
```

No stagear: `.env`, archivos de credenciales, binarios grandes.

### 3. Commit

```bash
git commit -m "$(cat <<'EOF'
feat|PROJ-042|20260402|Add JWT refresh token rotation
EOF
)"
```

### 4. Verificar

```bash
git log --oneline -1
git show --stat HEAD
```

## Reglas de la empresa

- Descripción en inglés, modo imperativo ("Add" no "Added")
- Máximo 60 caracteres en la descripción
- NUNCA escribir el mensaje sin el formato pipe
- NUNCA agregar footers, Co-Authored-By, ni atribuciones de herramientas
- SIEMPRE un cambio lógico por commit
