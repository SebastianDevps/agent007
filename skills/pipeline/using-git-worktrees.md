---
name: using-git-worktrees
description: "Creates an isolated git worktree for feature development. Ensures clean baseline before starting. Use before writing-plans for any medium/complex feature."
invokable: true
accepts_args: true
version: 1.0
source: superpowers (obra/superpowers) — adapted for Agent007
---

# Using Git Worktrees

**Propósito**: Crear un workspace aislado para desarrollar sin tocar `main`. Cada feature tiene su propia rama + directorio limpio.

**Cuándo activar**: Automáticamente antes de `writing-plans` en tareas medium/complex.

---

## Proceso

### 1. Verificar directorio de worktrees

Buscar en este orden:
1. `.worktrees/` en el proyecto
2. `worktrees/` en el proyecto
3. Preguntar al usuario si ninguno existe

Verificar que el directorio está en `.gitignore`:
```bash
git check-ignore -v .worktrees/
```
Si NO está ignorado → añadir a `.gitignore` y hacer commit inmediatamente.

### 2. Crear la rama y el worktree

```bash
# Nombre de rama: feat/<kebab-case-del-task>
git worktree add .worktrees/<branch-name> -b feat/<branch-name>
cd .worktrees/<branch-name>
```

### 3. Setup del proyecto

Detectar tipo de proyecto y correr setup:
```bash
# Node.js
[ -f package.json ] && npm install

# Python
[ -f requirements.txt ] && pip install -r requirements.txt

# Rust
[ -f Cargo.toml ] && cargo build
```

### 4. Baseline validation

Correr los tests del proyecto para verificar que el worktree arranca limpio:
```bash
npm test
# ó la suite del proyecto
```

Si los tests fallan → reportar al usuario ANTES de empezar. No proceder con baseline roto.

### 5. Confirmar workspace listo

```
✅ Worktree listo
Branch: feat/<branch-name>
Directorio: .worktrees/<branch-name>
Baseline: X tests passing
→ Listo para /writing-plans
```

---

## Reglas

- ❌ Nunca trabajar directamente en `main`/`master` sin permiso explícito
- ❌ Nunca saltarse la baseline validation sin permiso explícito del usuario
- ✅ Si algo falla en setup: reportar inmediatamente
- ✅ El worktree se limpia en `finishing-a-development-branch` (opciones 1 y 4)

---

## Integración

- **Antes**: `/brainstorming` (entender el feature)
- **Después**: `/writing-plans` (crear el plan en el worktree)
- **Al final**: `/finishing-a-development-branch` (merge/PR/cleanup)
