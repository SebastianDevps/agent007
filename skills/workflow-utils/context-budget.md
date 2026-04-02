---
name: context-budget
description: "Inventario estático de tokens por componente cargado. Identifica qué consume más contexto y recomienda optimizaciones. Complementa el monitoreo runtime de context-window-guard.py."
invokable: true
accepts_args: false
version: 1.0.0
when:
  keywords: ["context budget", "token cost", "context overhead", "what's loaded", "mcp tokens", "optimize context"]
---

# Context Budget — Inventario Estático de Tokens

**Propósito**: Hacer visible el consumo de context window por componente, antes de que sea un problema. Complementa `context-window-guard.py` (monitoreo runtime) con una auditoría estática.

---

## Por qué Importa

La ventana de contexto no es solo "cuánto has escrito hoy". El sistema carga automáticamente:
- CLAUDE.md + todos sus @imports
- Tool schemas de cada MCP server activo
- Agents INDEX.md, Skills INDEX.md, Commands INDEX.md

Un MCP server con 30+ tools puede consumir ~15,000 tokens **antes de que digas una sola palabra**.

---

## Inventario (Qué Auditar)

### Componentes siempre-activos

| Componente | Estimado | Notas |
|------------|----------|-------|
| CLAUDE.md | ~1,500 tokens | Base + routing table |
| @imports de CLAUDE.md | ~3,000 tokens | rules/, context/, guides |
| skills/INDEX.md | ~1,200 tokens | Compressed registry |
| commands/INDEX.md | ~300 tokens | Command list |
| agents/INDEX.md | ~500 tokens | Agent descriptions |
| MCP server tools | ~500 tokens/tool | Cada tool schema |

### Regla de estimación

```
Prosa:  palabras × 1.3 = tokens aproximados
Código: caracteres ÷ 4 = tokens aproximados
```

### Red flags a identificar

- MCP servers con 20+ tools → cada herramienta ~500 tokens
- CLAUDE.md > 300 líneas → revisar qué se puede mover a skills/
- Agents con descriptions > 30 palabras → compactar
- Cualquier MCP que wrappea CLI tools ya disponibles (git, gh, npm) → redundante

---

## Protocol

### Step 1 — Listar componentes activos

Leer `.claude/settings.json` → sección `mcpServers` y `hooks`.
Leer `CLAUDE.md` → contar @imports y líneas.

### Step 2 — Estimar tokens por componente

Para cada archivo importado, calcular:
```python
tokens = len(content.split()) * 1.3  # prosa
# o
tokens = len(content) / 4  # código
```

### Step 3 — Clasificar por necesidad

| Categoría | Descripción |
|-----------|-------------|
| Always Needed | Nunca eliminar (CLAUDE.md, rules activas) |
| Sometimes Needed | Útil pero no en cada sesión (domain skills) |
| Rarely Needed | Casi nunca usado en este proyecto |

### Step 4 — Recomendaciones

Para cada componente "Rarely Needed":
- Si es MCP: considerar desactivar en `settings.json`
- Si es skill auto-injected: mover a invokable-only
- Si es rule: verificar si ya está cubierta en otro lugar

---

## Output Esperado

Tabla ordenada por tokens descendente:

| Componente | Tokens Est. | Categoría | Recomendación |
|------------|-------------|-----------|---------------|
| MCP: playwright | ~12,000 | Rarely Needed | Desactivar salvo E2E |
| CLAUDE.md | ~1,500 | Always | OK |
| skills/INDEX.md | ~1,200 | Always | OK |
| ... | ... | ... | ... |

**Total estimado en contexto base**: X tokens de Y disponibles (Z%)
