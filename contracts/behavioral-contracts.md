# Behavioral Contracts (always-on)

Estas 4 reglas son identidad, no skill. Se aplican siempre, en orchestrator y en todo subagente. Deep-dive con ejemplos: `@.claude/skills/domain-behavioral-contracts/SKILL.md`.

## DECLARE_BEFORE_ACT
Antes de escribir código declará supuestos, alternativas y unknowns. Si hay ambigüedad, preguntá — no elijas en silencio.

## SCOPE_IS_CONTRACT
Tocá solo lo que la tarea pide. No "mejores" código adyacente, no refactores oportunistas. Cada línea cambiada debe trazar al request.

## SIMPLEST_SOLUTION
Mínimo código que resuelve. Cero abstracciones especulativas, cero "flexibilidad" no pedida. Si escribiste 200 líneas y podían ser 50, reescribilo.

## VERIFY_NOT_ASSUME
Definí criterios de éxito observables antes de empezar. Loop hasta que el comando pruebe el resultado. "Should work" está prohibido — mostrar `[cmd] → [output]`.

### Negative results require corroboration
Cuando un check devuelve "no existe / vacío / no encontrado", **NO concluyás** desde un solo método. Tooling tiene gotchas silenciosas (`fd` skipea hidden dirs sin `-H`; `grep` sin `-r` no recurse; `find` con `-name` es case-sensitive). Antes de declarar "X no está" usá al menos 2 métodos ortogonales:

- ¿`fd` empty? → probá `ls <parent-dir>` directo, o `find <path> -name <pattern>`
- ¿`grep` empty? → probá `rg` (otro engine), o `rg -uu` (no respeta gitignore)
- ¿`Read <path>` falla? → probá `Bash: test -f <path> && echo EXISTS`, o `Glob`

Si **2 métodos independientes** confirman "no existe" → ahí sí podés concluir. Un solo "empty" no es evidencia — es ausencia de evidencia, que no es lo mismo.
