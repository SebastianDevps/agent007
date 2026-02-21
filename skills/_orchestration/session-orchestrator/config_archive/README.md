# Archived Configuration Files

**Date**: 2026-02-20
**Reason**: These config files are not used by the current implementation

---

## Files Archived

### `orchestrator.config.json`
**Original purpose**: Define task type patterns, risk detection rules, and routing workflows

**Why archived**:
- The detector.js implementation uses **hardcoded patterns** instead of reading this config
- All pattern matching logic is directly in `lib/detector.js` (lines 50-148)
- Risk detection rules are hardcoded in `detectRiskLevel()` (lines 154-214)
- Maintaining this file creates confusion between documentation and implementation

**If you want config-driven routing**:
You would need to modify `lib/detector.js` to actually read and use these patterns:
```javascript
// In detector.js
const config = require('../config/orchestrator.config.json');
const patterns = config.contextDetection.rules.consult.keywords;
// Then use 'patterns' instead of hardcoded arrays
```

---

### `risk-profiles.json`
**Original purpose**: Define risk profiles for different scenarios with file patterns and dependencies

**Why archived**:
- Never loaded or used by any code in the orchestrator
- Risk detection in detector.js uses pattern-based functions (lines 168-195)
- No code references this file

**If you want profile-based risk detection**:
You would need to:
1. Load this file in detector.js
2. Match against filePatterns, modifiesSchema, touchesMultipleContexts
3. Calculate risk based on matched profile

---

## Current Implementation (v3.0)

The detector now uses a **function-based approach** with contextual detection:

**Confidence calculation**: (lines 269-318)
- Base score (40%)
- Keyword bonus (0-30%)
- Structure bonus (0-15%)
- Clarity bonus (0-15%)

**Risk detection**: (lines 154-214)
- Critical complexity patterns (+2 levels): auth implementation, payments, encryption
- High complexity patterns (+1 level): JWT, real-time, migrations
- Scope factors (+1 level): production deployments, multi-module changes
- Order-independent matching using functions instead of regex

This approach is:
- ✅ More maintainable (code is self-documenting)
- ✅ More flexible (can use complex logic, not just regex)
- ✅ Faster (no JSON parsing on every request)
- ❌ Less configurable (changing patterns requires code changes)

---

## Decision Rationale

**Trade-off analysis**:
- Implementing config-driven routing: 8-12 hours effort
- Value added: ~5% (ability to change patterns without code changes)
- RICE score: Low

**Conclusion**:
Hardcoded patterns are the right choice for this use case. The patterns are stable and don't need frequent changes. Code-based patterns are easier to test and debug.

---

## Restoration

If you need these configs for reference or future implementation:
```bash
cd /Users/sebasing/Projects/Agent007/.claude/skills/_orchestration/session-orchestrator
cp config_archive/*.json config/
```

Then modify `lib/detector.js` to load and use them.
