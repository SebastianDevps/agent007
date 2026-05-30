---
name: spec
version: 1.0
description: "Standalone CRUD para specs estables en openspec/specs/. Sub-actions: new, edit, verify, list. NO confundir con sdd-spec (phase del pipeline SDD)."
when:
  keywords: [spec, "/spec", create spec, verify spec, list specs, edit spec]
allowed-tools:
  - Read
  - Edit
  - Write
  - Bash(python3 -m scripts.spec*)
  - Glob
  - Grep
---

# spec — Standalone Spec CRUD

## Purpose

Gestiona specs estables bajo `openspec/specs/`. Provee cuatro sub-acciones:
`new` (scaffold), `edit` (LLM-driven con race guard), `verify` (schema check),
`list` (tabla/JSON). Las piezas determinísticas delegan a scripts Python en
`scripts/spec/`. La sub-acción `edit` es LLM-driven y vive en este skill.
Toda invocación produce exactamente una línea en `.sdlc/state/spec-command-audit.jsonl`.
Este skill NUNCA toca `openspec/changes/` ni `_index.json`.

## Dispatcher

Parsear el primer argumento como `action` y el segundo (si existe) como `name`.

```
action = first token of $ARGUMENTS
name   = second token of $ARGUMENTS (optional for list/verify-batch)
```

Si `action` no está en `{new, edit, verify, list}`:

```
ERROR: acción desconocida "<action>".
Uso:
  /spec new <name>        — crear spec nuevo con scaffold
  /spec edit <name>       — editar spec existente (LLM-driven)
  /spec verify [<name>]   — validar schema (sin arg = batch sobre openspec/specs/)
  /spec list [--json]     — listar todos los specs
```

Rutear según action:

| action   | Handler                    |
|----------|----------------------------|
| `new`    | Dispatch determinístico    |
| `verify` | Dispatch determinístico    |
| `list`   | Dispatch determinístico    |
| `edit`   | Dispatch LLM-driven        |

Si `name` está vacío para `new` o `edit`, devolver error antes de invocar script:
`ERROR: <action> requiere un nombre. Uso: /spec <action> <name>`

## Dispatch determinístico

### new

```bash
python3 -m scripts.spec.spec_new <name>
```

Capturar stdout, stderr y exit code. Si exit 0: reportar `Spec creado: openspec/specs/<name>.md`.
Si exit 2: reportar el error de validación de nombre tal cual. Si exit 17: reportar el error EEXIST.
Si exit 1 (otro): mostrar stderr completo.

Tras cualquier resultado (ok o error), ejecutar el **Audit step**.
Tras exit 0, ejecutar el **Verification step**.

### verify

```bash
python3 -m scripts.spec.spec_verify <name>
# o sin nombre (batch):
python3 -m scripts.spec.spec_verify
```

Mostrar stdout completo. Ejecutar el **Audit step** con `result = "ok"` si exit 0,
`result = "error:SCHEMA"` si exit 1.

### list

```bash
python3 -m scripts.spec.spec_list
# o con flag:
python3 -m scripts.spec.spec_list --json
```

Mostrar stdout completo. Ejecutar el **Audit step** con `spec_name = null`.

## Dispatch LLM-driven (edit)

**Paso 1 — Race check.**

```bash
python3 -m scripts.spec.spec_race_check <name>
```

Si exit no-cero: mostrar stderr del script al usuario y abortar. NO continuar.
Ejecutar **Audit step** con `result = "error:RACE"` y retornar.

**Paso 2 — Leer spec actual.**

`Read openspec/specs/<name>.md`

Si el archivo no existe: devolver error `ERROR: spec '<name>' no encontrado.
Usá /spec new <name> para crearlo.` Ejecutar **Audit step** con `result = "error:NOT_FOUND"`.

**Paso 3 — Pedir al usuario que describa el cambio.**

Mostrar el contenido actual del spec y preguntar (UNA sola pregunta, luego STOP):
`¿Qué cambio querés aplicar a este spec?`

Esperar la respuesta del usuario antes de continuar.

**Paso 4 — Aplicar el cambio.**

Aplicar `Edit` ÚNICAMENTE sobre `openspec/specs/<name>.md`.
SCOPE_IS_CONTRACT: este skill NUNCA toca otro archivo en este flujo.

**Paso 5 — Post-edit verification.**

Ejecutar el **Verification step** sobre `<name>`.

Si verify falla: reportar el error con el output del script y ofrecer:
`El spec fue guardado pero no pasa el schema. ¿Querés corregirlo ahora?`
NO revertir automáticamente (v1 — el usuario decide).

Ejecutar el **Audit step** con `result = "ok"` si verify pasa, `result = "error:SCHEMA"` si falla.

## Audit step

Al finalizar cada invocación (éxito o error), construir el objeto de audit y
delegarlo al script. El skill NO appendea directamente — delega al script.

```bash
echo '{"action":"<action>","spec_name":"<name_or_null>","result":"<result>","caller":"<caller>"}' \
  | python3 -m scripts.spec.append_audit
```

Donde `<caller>` se obtiene del env `CLAUDE_SUBAGENT_NAME` si existe, sino `"main-session"`.
Falla del audit → warning a stderr del skill, NO abortar la operación.

## Verification step

Tras `new` o `edit` exitoso, correr el schema check y mostrar el output como feedback:

```bash
python3 -m scripts.spec.spec_verify <name>
```

Mostrar la salida completa. Esto da feedback inmediato del estado del schema.

## Error handling

| Condición                          | Respuesta                                                                  |
|------------------------------------|----------------------------------------------------------------------------|
| `action` no reconocida             | Mostrar help text con las 4 acciones válidas                               |
| `name` faltante en `new` / `edit`  | `ERROR: <action> requiere un nombre. Uso: /spec <action> <name>`           |
| Script Python no encontrado        | `ERROR: scripts/spec/<script>.py no encontrado. ¿Wave 1 fue aplicada?`    |
| Race detectada en `edit`           | Relay del stderr de `spec_race_check` + abort                              |
| Spec no encontrado en `edit`       | `ERROR: spec '<name>' no encontrado. Usá /spec new <name> para crearlo.`  |

## Limites

- Este skill NUNCA modifica archivos bajo `openspec/changes/<name>/` — eso es scope del pipeline SDD.
- Este skill NUNCA modifica `openspec/changes/_index.json`.
- Este skill NO guarda en engram.
- La sub-acción `edit` solo aplica `Edit` sobre `openspec/specs/<name>.md` — un archivo, scope mínimo.
- El path-guard (`path-existence-guard.py`) debe tener `spec` en su allowlist para que `Write` bajo
  `openspec/specs/` no sea bloqueado (Wave 4 del sub-change `spec-command-unification`).
