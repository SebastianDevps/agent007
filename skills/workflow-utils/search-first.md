---
name: search-first
description: "Buscar antes de escribir: ejecuta búsqueda estructurada antes de crear cualquier utility, helper, o abstracción. Matriz de decisión: adopt→extend→compose→build."
invokable: true
accepts_args: true
version: 1.0.0
when:
  keywords: ["search first", "before creating", "before writing", "find existing", "don't reinvent", "utility", "helper", "abstraction"]
---

# Search-First — Buscar Antes de Escribir

**Propósito**: Evitar reinventar la rueda — el time-waster más común en desarrollo asistido por IA. Antes de escribir cualquier utility, helper, abstracción, o integración, ejecutar búsqueda estructurada.

**Regla**: Solo se pasa a `build` cuando los pasos 0–3 no producen nada utilizable.

---

## Búsqueda Estructurada (4 fuentes en orden)

### 0. ¿Ya existe en el repo?

```bash
# Buscar por nombre/concepto
grep -r "functionName\|ConceptKeyword" src/ --include="*.ts" -l

# Buscar utilidades similares
find src/ -name "*.utils.ts" -o -name "*.helper.ts" | head -20
```

**Si existe**: usar directamente o extender. Parar aquí.

### 1. npm / PyPI / pkg manager

```bash
# Para Node.js
npm search <keyword> --prefer-online

# Evaluar criterios: MIT/Apache license, >1k weekly downloads, <2 years sin actualizar
```

### 2. MCP servers disponibles

Revisar `~/.claude/settings.json` → `mcpServers`:
¿Hay algún MCP que ya provee esta capacidad?

Ejemplo: antes de escribir código para interactuar con GitHub API, verificar si `github-mcp` está activo.

### 3. Skills del registro

```
grep -r "<keyword>" .claude/skills/ --include="*.md" -l
```

¿Hay un skill que ya cubre este patrón?

### 4. GitHub code search (último recurso)

Solo si los pasos 0–3 no produjeron nada.

---

## Matriz de Decisión

| Resultado de búsqueda | Acción |
|----------------------|--------|
| Match exacto + MIT/Apache | **Adopt**: instalar y usar directamente |
| Match parcial (80% de lo necesario) | **Extend**: fork/subclass/wrap |
| 3+ opciones débiles pero complementarias | **Compose**: combinar dos paquetes pequeños |
| Nada relevante | **Build**: ahora sí, escribir desde cero |

---

## Criterios de evaluación de librerías

Antes de adoptar una dependencia externa:

- [ ] Licencia: MIT, Apache 2.0, BSD — nunca GPL en código cerrado
- [ ] Mantenimiento: commit en últimos 12 meses
- [ ] Popularidad: >1,000 npm downloads/semana o >100 GitHub stars
- [ ] Tamaño: bundle size razonable para el contexto (web vs backend)
- [ ] Dependencias transitivas: no traer 50 dependencias para una función simple

---

## Cuándo Activar este Skill

Este skill debe ejecutarse **automáticamente** durante `Skill('plan')` cuando el plan incluye crear cualquier:
- Utility function / helper
- HTTP client / API wrapper
- Cache layer
- Parser / formatter
- Validation logic

El planner debería incluir una fase "Search-First" antes de diseñar la implementación.
