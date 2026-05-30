# Agent007 v7 — Plugin de Orquestación

> **13 agentes · 57 skills · 43 hooks · 390/390 tests verde · 0 findings abiertos.** Sistema de orquestación con contratos de comportamiento always-on, pipeline SDD con 4 auto-gates, auto-loop V7.3 endurecido (fire → feedback → retry → converge/escalate), fan-out paralelo con worktree isolation, estado file-based, first-run onboarding, tool-allowlist fail-CLOSED, safety-guard con clasificación por ejecutor y detección de data-flow por pipes.

---

## Quickstart

```bash
.claude/scripts/lifecycle/verify.sh                # 5 checks (+ --with-tests para regression)
.claude/scripts/lifecycle/install.sh /path/to/proj # deploy a otro proyecto
.claude/scripts/lifecycle/sync-to-public.sh        # sync a Agent007/ flat (público)
.claude/scripts/lifecycle/waste-report.py          # audit de gasto (cuando tengas datos)
```

CI gate (`.github/workflows/plugin-validate.yml`) corre los 5 checks en cada PR.

---

## 3 comandos de entrada

| Comando | Uso |
|---|---|
| `/dev "task"` | Maestro. **Trivial** → `Skill('generate')` + `Skill('verify')`. **Substancial** → SDD pipeline (proposal → spec → design → tasks → apply → verify → archive). |
| `/consult "question"` | Routing por keywords al agente especializado |
| `/ralph-loop "task"` | Iteración autónoma hasta `<promise>COMPLETE</promise>` |

Routing siempre anuncia: `🎯 [target] | Risk: [low/med/high/critical]`. Risk auto-escala a **high** en auth/payments/encryption/migrations/breaking. **High/critical requiere "yes" explícito**.

---

## 13 Agentes (8 principales abajo; ver `agents/INDEX.md` para los 5 cross-cutting)

| Agente | Modelo | Dominio |
|---|---|---|
| `backend-db-expert` | opus | NestJS · TypeORM · PostgreSQL · Redis · microservices |
| `frontend-ux-expert` ⚡ | sonnet | **BUILDER mode default** — escribe código. React · Next · Tailwind · GSAP · shadcn · iOS HIG. Anti-convergencia gate enforced. |
| `security-expert` | opus | OWASP · JWT · threat modeling · GDPR/SOC2 |
| `platform-expert` | sonnet | CI/CD · Docker · Jest · Playwright · Kubernetes |
| `product-expert` | opus | RICE/ICE · user stories · roadmap · MVP scoping |
| `code-reviewer` | sonnet | Quality review (CRITICAL/HIGH/MED/LOW) |
| `loop-operator` | sonnet | Ralph control · stall detection · cost drift |
| `refactor-cleaner` | sonnet | Dead code (knip/depcheck/ts-prune) |

> Removidos en v6: `architect` → `Skill('domain-architecture-patterns')`. `performance-optimizer` → `Skill('quality-gates-performance-profiling')`.

---

## Frontend ejecutor

Antes el agente **validaba**. Ahora **construye**. Tools: `Read · Write · Edit · Bash · WebFetch · WebSearch`.

**Flujo blindado por hook**:
1. `Skill('domain-discovery-before-code')` — referent fetch + 1 de 11 estilos extremos + states + tokens
2. Escribe `.claude/state/discovery-output.json` (TTL 30 min)
3. `frontend-discovery-gate.py` (PreToolUse) bloquea cualquier `.tsx/.jsx/.css/.html/.svelte/.vue/.astro` sin discovery output reciente

**8 skills accionables**: `domain-discovery-before-code` · `domain-shadcn-component-install` · `domain-a11y-contrast-check` (script Node.js zero-deps WCAG) · `domain-design-tokens-extract` · `domain-design-system-doc` (9-section schema) · `domain-page-transitions-barba` · `domain-ios-hig-mobile` · `domain-spline-3d-embed`.

---

## 43 Hooks (deterministas — sample abajo, lista completa en `harness/`)

| Hook | Trigger | Qué enforza |
|---|---|---|
| `safety-guard` | PreToolUse/Bash | Bloquea destructivos (rm -rf, force push, DROP TABLE) |
| `sdd-guard` | Pre+Post/Edit\|Write | Anti-reward-hacking (edits que reducen assertions) |
| `path-existence-guard` ⭐ | Pre/Edit\|Write\|Read | Bloquea paths alucinados |
| `tool-allowlist-guard` ⭐ | Pre/Bash | Skill-level bash whitelist (shadcn pattern) |
| `frontend-discovery-gate` ⭐ | Pre/Edit\|Write | Anti-convergencia frontend inevitable |
| `mutation-guard` | Pre/Edit\|Write | Dedup writes; defensive contra retries |
| `web-distill` | Pre/WebFetch | Distill HTML + 24h URL cache |
| `context-engine` | Pre/Agent + Stop | Token budget gate ≥80% |
| `context-window-guard` | PostToolUse | Warning 30%, crítico 15% |
| `tool-loop-detection` | PostToolUse | Circuit breaker 30× tool repetido |
| `block-no-verify` | Pre/Bash | Prohíbe `git commit --no-verify` |
| `pre-commit-guard` | Pre/Bash | Valida staging antes de commit |
| `context-tick` | Session+Post+Stop | Telemetry → `.sdlc/state/context-budget.jsonl` |
| `session-recover` | SessionStart | Preamble con resumen de sesión previa + first-run onboarding |
| `rtk-bootstrap` · `rtk-rewrite` · `state-sync` · `tool-policy-guard` · `subagent-context` · `transcript-policy` · `config-guard` · `format-on-save` · `notify` · `constraint-reinforcement` | varios | …infraestructura |

> `memory-check` y `memory-decay` removidos en pivot 2026-05-23 (engram-removal).


---

## Telemetría + recovery

`context-tick.py` (hook) registra todo a `.sdlc/state/context-budget.jsonl`. Cuando tengas datos:

```bash
.claude/scripts/lifecycle/waste-report.py [--days 30] [--json]
```

Reporta: top 5 archivos cargados · references hit rate · references **never-loaded** (delete candidates) · p50/p95/p99 tokens-at-stop · sessions/día · avg tool calls/sesión.

`session-recover.py` (SessionStart) emite preamble si la última actividad fue <4h: files touched, tools used, active task de `session.md`. Override: `SESSION_RECOVER_HOURS=0`.

`statusLine` muestra en tiempo real:
```
◆ sonnet · 38% (76k/200k) · 24m · plugin~5%
◆ opus · 84% (168k/200k) ⚠ COMPACT · 1h12m · plugin~7%
```

---

## Persistencia (file-based)

Todo el estado del plugin vive en filesystem. **No hay memory backend externo** (engram removido — ver `.sdlc/adrs/ADR-002-remove-engram-from-plugin.md`).

| Tipo | Ubicación |
|---|---|
| Artefactos SDD por sub-change | `openspec/changes/<change>/{proposal,spec,design,tasks,apply-progress,verify-report,archive-report}.md` |
| Specs estables post-archive | `openspec/specs/<spec-name>.md` |
| Session continuity | `.sdlc/RESUME-*.md`, `.sdlc/state/session-summary-<date>.md` |
| Project context | `.sdlc/context/*.md` |
| ADRs / PRDs / Retros | `.sdlc/{adrs,prds,retrospectives}/` |
| State runtime | `.sdlc/state/*.json[l]` |

Cross-session recovery = `Read` literal de los archivos. Keyword search = `rg` / `fd` / `grep` sobre `.sdlc/` y `openspec/`. Sin tools custom.

> Requisito: `ripgrep` y `fd` instalados (`brew install ripgrep fd` en macOS).

---

## Frontmatter convention

```yaml
---
name: my-skill
description: "What it does, in one line"
invokable: true
when:
  keywords: [...]
canonical-sources:                # WebFetch obligatorio antes de afirmar best practice
  - url: https://owasp.org/Top10
    when: "para referencias OWASP"
allowed-tools:                    # whitelist shadcn-style
  - Read
  - Bash(npm test*)
references:                       # lazy-load
  - references/section-a.md
---
```

**Single source of truth en `/skills`.** Cero duplicados entre `/commands` y `/skills`.

---

## Estructura

```
.claude/
├── CLAUDE.md            # 99 líneas — identidad + core rules + routing + memory
├── CONTEXT.md           # 92 líneas — navegación de proyecto (Pocock pattern)
├── settings.json        # hooks registry + statusLine + permissions
├── agents/              # 8 specialists
├── commands/            # 8 orchestrators (dev, orchestrate, ralph-loop, …)
├── skills/              # 57 skills, flat depth-1
├── harness/             # 43 Python hooks (guides · sensors · sentinels · statusline)
├── scripts/lifecycle/   # verify, install, uninstall, sync-to-public, test-hooks, waste-report, statusline
├── instincts/           # active learning system (instinct-engine + /evolve + /instinct-status)
├── rules/               # typescript, security, git, patterns, hooks-authoring, coding-style
└── worktrees/           # placeholder for git worktrees
```

> **v6 cleanup** removió `metrics/` y 6 scripts huérfanos legacy (~916 líneas). Cero archivos eager > 200 líneas.

---

## Métricas (histórico v5.1 → v6, referencial — v7 actualiza counts a 13/57/43)

| | v5.1 | v6 | Δ |
|---|---|---|---|
| CLAUDE.md líneas | ~250 | 99 | -60% |
| Eager-loaded total | ~7300 | 1195 | -84% |
| Auto-inject overhead | 1239 | 237 | -81% |
| Skills invokables | 28 | 44 | +16 |
| Hooks | 21 | 26 | +5 |
| References lazy-load | 0 | 72 | nuevo |
| Archivos eager > 200 | 18 silenciosas | **0** | ✓ |
| Hook regression tests | 0 | 14 fixtures | ✓ |
| Anti-convergencia | no | hook + skill (inevitable) | ✓ |
| Frontend agent | validator-only | builder default | ✓ |
| Telemetría persistente | no | sí (JSONL + waste-report) | ✓ |
| Cross-session recovery | no | sí (session-recover) | ✓ |
| StatusLine | no | sí (tokens% + plugin~%) | ✓ |
| CI propia | no | 6 jobs | ✓ |
| Lifecycle scripts | no | 7 scripts | ✓ |
| Debt register | implícito | explícito Y vacío | ✓ |
| verify.sh status | n/a | **6/6 pass · 0 warnings** | ✓ |

---

## Filosofía

| Principio | Implementación |
|---|---|
| Hooks > rules | Lo no-negociable es determinista (hooks). Lo contextual es probabilístico (rules en CLAUDE.md). |
| Single source | `/skills` es la unidad invocable. `/commands` solo orquestadores. |
| Anti-convergencia | Hook bloquea visual writes sin discovery → no más "purple gradient + Inter" default. |
| Debt visible | `.line-cap-exemptions` debe estar vacío. Si crece, falla CI. |
| Medir antes de optimizar | Telemetría JSONL. waste-report decide qué cachear. No intuición. |
| Anti-redundancia | Antes de feature nueva, audit: ¿ya existe? ¿hay solapamiento? Si sí, skip. |
| Compaction-resistant | Hook persiste rastro continuo (no PreCompact native). SessionStart recupera. |

---

## Backlog (todo nice-to-have)

Con justificación de SKIP donde aplica:

- **F9** Multi-platform dist (otras plataformas) — solo si salir del nicho Claude Code
- **F10** Marketplace metadata + manifest.json — cuando se publique
- **D2** Web viewer citations — visualización de history, no bloquea
- ❌ **B2** verbatim capture — skip hasta dolor real
- ❌ **B4** instincts↔engram — redundante con `/evolve → skill`
- ❌ **C1** reference cache — sin datos en waste-report aún
- ❌ **C2** lazy auto-inject — peligroso (banned-phrases es seguridad)
- ❌ **C4** compaction-aware priority — fuera de control de hooks
- ⛔ **D1** worker HTTP / **D3** universal disclosure / **D4** superseded_by — out of scope (Engram engine)

---

## Patrones competitivos integrados

allowed-tools whitelisting · frontend anti-patterns (11 estilos) · 3-layer disclosure (cache TTL · session continuity) · temporal validity · CONTEXT.md separado · lifecycle scripts + CI · banned-phrases · medir antes de optimizar

---

## Documentación

- `CLAUDE.md` — identidad y core rules (auto-cargado)
- `CONTEXT.md` — navegación del proyecto
- `skills/INDEX.md` · `agents/INDEX.md` · `commands/INDEX.md`
- `rules/*.md` — convenciones (typescript · security · git · patterns · hooks-authoring · coding-style)

**Versión**: 7.0.0 · License: MIT · Author: Sebastian Guerra
