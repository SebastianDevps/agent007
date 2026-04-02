# Changelog

All notable changes to Agent007 will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [4.2.0] — 2026-04-02

### Added

- **8 GSAP animation skills** for `frontend-ux-expert` (contributed by @JuanesEspinosa, issue #2):
  - `gsap-core` — tweens, easing, stagger, matchMedia, reduced-motion
  - `gsap-timeline` — sequencing, position parameter, labels, nesting
  - `gsap-scrolltrigger` — scroll-linked animations, pinning, scrub
  - `gsap-plugins` — Flip, Draggable, SplitText, MorphSVG, MotionPath, CustomEase
  - `gsap-react` — useGSAP hook, gsap.context(), cleanup on unmount
  - `gsap-utils` — clamp, mapRange, normalize, snap, toArray, pipe, distribute
  - `gsap-performance` — transforms, will-change, batching, quickTo
  - `gsap-frameworks` — Vue, Svelte, Nuxt, SvelteKit lifecycle & cleanup
- Animation keywords added to `/consult` routing: `gsap`, `animation`, `scroll`, `tween`, `timeline`, `stagger`, `parallax`, `motion`

### Changed

- `frontend-ux-expert` agent now includes 8 GSAP domain skills
- `ARCHITECTURE.md`: skill count updated 17 → 25, GSAP section added
- `plugin.json`: version bump 4.1.0 → 4.2.0, description updated (42 → 50 skills), keywords `gsap` and `animation` added

## [3.0.0] — 2026-03-01

### Added

- **`/dev` — Comando maestro**: clasifica automáticamente cada tarea (simple/medium/complex) y ejecuta el workflow correcto. Flags: `--simple`, `--full`, `--ralph`, `--max-iterations N`, `--verify "cmd"`.
- **`/ralph-loop` — Loop autónomo**: itera hasta detectar `<promise>COMPLETE</promise>`. Modo DIRECT (< 3 requisitos) y ORCHESTRATED (≥ 3 o multi-tech). Escribe `.claude/ralph-state.json` y `.claude/ralph-complete.txt`.
- **`ralph-check.js` — Stop hook**: bloquea paradas prematuras cuando ralph está activo. Incrementa iteración e inyecta contexto de continuación. También corre task verifier LLM antes de permitir stop.
- **4 Superpowers workflow skills**: `subagent-driven-development` (despacha experto por tarea con spec + quality review), `using-git-worktrees` (branch aislado en `.worktrees/`), `requesting-code-review` (2 etapas: spec compliance → calidad), `finishing-a-development-branch` (4 opciones: merge/PR/keep/discard).
- **STATE.md — Persistencia cross-session**: auto-cargado vía `context.include`. Banner de retomada si hay tarea activa. Actualización silenciosa al completar tareas. Resumen de sesión al salir.
- **`security-review` skill**: auditoría OWASP Top 10, auth/autorización, datos sensibles.
- **`session-state` core skill**: documenta formato y reglas de actualización de STATE.md.
- **`.claude/README.md`**: manual de uso interno detallado — todos los comandos, agentes, skills, hooks y patrones de extensión.

### Changed

- `plugin.json` actualizado a v3.0.0 con manifiesto completo de commands, skills, agents y hooks.
- `commands/`: ahora contiene los 9 commands (antes solo `consult.md`).
- `skills/workflow/`: añadidos 5 skills (executing-plans + 4 Superpowers).
- `skills/_core/`: añadido `session-state`.
- `skills/`: añadido `security-review`.
- Descripción del plugin reescrita: foco en orquestación autónoma, no en reducción de tokens.
- CLAUDE.md refactorizado con orquestador activo, tabla de clasificación, tabla de routing y reglas de enforcement.

### Fixed

- `using-git-worktrees` ya no bloquea cuando no existe test suite (validación baseline es condicional).
- `subagent-driven-development`: pasa el texto de la tarea directamente al subagente, no la ruta del plan.
- Ralph loop ya no permite parar a Claude a mitad de tarea aunque no haya `--ralph` explícito.

---

## [Unreleased]

### Added
- **Infrastructure (Phase 1)**:
  - Memory directory structure (`.claude/memory/` with patterns, lessons, decisions) + README.md
  - Knowledge directory structure (`.claude/knowledge/` with patterns, lessons) + README.md
  - Metrics directory (`.claude/metrics/` for Ralph Loop and routing tracking) + README.md
  - LICENSE (MIT)
  - CONTRIBUTING.md with development guidelines and frontmatter standard
  - CHANGELOG.md for tracking releases
  - Frontmatter validation script (`.claude/scripts/validate-frontmatter.js`)

- **Skills (Phase 1 & 2)**:
  - `executing-plans` skill to complete workflow chain
  - `security-review` skill with OWASP Top 10 audit (Phase 2)
  - OWASP checklist reference in `security-review/references/`
  - Trigger phrases to 18/27 skills (82% active skills coverage)
  - Tool permissions (`allowed-tools`) to 15/27 skills (Phase 3)

- **Documentation (Phase 2 & 3)**:
  - Manual test suite (`.claude/skills/TEST_SUITE.md`) with 24 comprehensive tests
  - ADR-001: Deprecate analytics workflow decision
  - MODEL_CONFIGURATION.md - Model mapping and selection guide (Phase 3)
  - FRONTMATTER_STANDARD.md - Official frontmatter specification v1.0 (Phase 3)
  - Phase 1, 2, and 3 implementation reports

### Changed
- **Frontmatter standardization (Phase 1)**: Improved consistency from 54% to 70%
  - Replaced deprecated `user-invocable` with `invokable` (6 skills)
  - Removed `model` field from skills (defined in agents only)
  - Standardized `allowed-tools` format to JSON arrays
  - Added missing `version` and `invokable` fields
- **Trigger phrase coverage (Phase 2)**: 47% → 82% for active skills (+35pp)
  - api-documentation, product-discovery, architecture-review updated
- **Security hardening (Phase 3)**: Added tool permissions to 7 additional skills
  - brainstorming, writing-plans, tdd, systematic-debugging, architecture-review, product-discovery, api-documentation
  - Implemented least privilege principle (read-only for review skills, full access for implementation)
- **Security expert agent**: Added `security-review` skill reference
- Fixed `react-best-practices` frontmatter position (moved to line 1)
- Updated validation script to handle both Unix and Windows line endings

### Fixed
- Directory structure for knowledge capture systems
- Broken reference to `executing-plans` skill from `writing-plans`
- Missing trigger phrases in 15 skills
- Deprecated frontmatter fields causing validation warnings
- Warnings reduced from 20 → 13 (-7)

### Deprecated
- Analytics workflow task type (documented in ADR-001)

## [2.0.0] - 2026-02-21

### Added
- Consolidated expert agents: 5 agents (backend-db, frontend-ux, platform, product, security)
- 17 active skills across domains
- Session orchestrator v3.0 with intelligent routing
- Ralph Loop v4.0 auto-correction system
- `/consult` command for multi-agent consultation
- Quality enforcement core skills
- Post-task knowledge capture [P][L][D][N]

### Changed
- Consolidated from multiple agents to 5 focused experts
- Unified skill structure and organization

## [1.0.0] - 2026-01-15

### Added
- Initial release of Agent007 ecosystem
- Basic skills and agents structure
- Custom commands framework

---

## Version History

- **3.0.0** (2026-03-01): Autonomous orchestration — /dev, ralph-loop, 4 Superpowers, STATE.md
- **2.0.0** (2026-02-21): Opensource ready, consolidated architecture
- **1.0.0** (2026-01-15): Initial release

[3.0.0]: https://github.com/SebastianDevps/agent007/compare/v2.0.0...v3.0.0
[2.0.0]: https://github.com/SebastianDevps/agent007/compare/v1.0.0...v2.0.0
[1.0.0]: https://github.com/SebastianDevps/agent007/releases/tag/v1.0.0
