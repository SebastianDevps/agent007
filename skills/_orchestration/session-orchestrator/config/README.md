# Orchestrator Configuration

**Current Status**: This directory contains configuration files for the session orchestrator.

---

## Files

### `adaptive-gates.yml` ✅ ACTIVE (Declarative)
**Purpose**: Defines quality gates based on risk level

**Status**: DECLARATIVE - describes intended behavior but not yet enforced by code

**Content**:
- Basic verification (all risk levels)
- Unit tests (medium+)
- Code review (high+)
- Security audit (critical)
- Integration tests (high+)

**Usage**: Referenced in documentation, used as specification for quality enforcement principles. Not programmatically loaded.

---

## Archived Files

See `../config_archive/README.md` for:
- `orchestrator.config.json` (unused - detector.js uses hardcoded patterns)
- `risk-profiles.json` (unused - risk detection uses function-based approach)

---

## Configuration Philosophy

The orchestrator uses a **hybrid approach**:

✅ **Declarative** (YAML): High-level specifications and intentions
- `adaptive-gates.yml` - describes quality philosophy

✅ **Code-based** (JavaScript): Actual implementation
- `lib/detector.js` - confidence and risk detection
- `lib/router.js` - skill routing logic

This balances **flexibility** (easy to understand and modify declarations) with **power** (complex logic in code).
