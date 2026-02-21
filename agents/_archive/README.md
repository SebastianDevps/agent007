# Archived Agent Definitions

**Date**: 2026-02-20
**Reason**: Agents consolidated to reduce cognitive overhead

---

## Consolidation Strategy

The original 10 agents have been consolidated into 5 core agents to reduce complexity while maintaining full capability coverage.

### Archived Agents (8)

| Original Agent | Archived | Merged Into |
|---------------|----------|-------------|
| `backend-expert` | ✅ | `backend-db-expert` |
| `database-expert` | ✅ | `backend-db-expert` |
| `frontend-expert` | ✅ | `frontend-ux-expert` |
| `ux-expert` | ✅ | `frontend-ux-expert` |
| `devops-expert` | ✅ | `platform-expert` |
| `testing-expert` | ✅ | `platform-expert` |
| `data-expert` | ✅ | Archived (low usage <5%) |
| `devrel-expert` | ✅ | Archived (low usage <5%) |

### Current Active Agents (5)

| Agent | Model | Expertise | Skills |
|-------|-------|-----------|--------|
| `backend-db-expert` | opus | Backend + Database | api-design-principles, architecture-patterns, resilience-patterns |
| `frontend-ux-expert` | sonnet | Frontend + UX Design | react-best-practices, frontend-design, ux-research, design-system |
| `platform-expert` | sonnet | DevOps + Testing | tdd, systematic-debugging |
| `product-expert` | opus | Product Discovery | product-discovery, feature-prioritization |
| `security-expert` | opus | Security & Compliance | nestjs-code-reviewer |

---

## Rationale for Consolidation

### Problem Identified
From the critical analysis consultation:
- **10 agents** for a solo-developer tool created excessive cognitive overhead
- **Routing complexity**: More agents = more routing decisions = more potential misroutes
- **Maintenance burden**: Each agent definition needs to stay current with best practices
- **Usage analysis**: Some agents (data-expert, devrel-expert) had <5% usage

### Solution
**Consolidate related domains**:
1. **Backend + Database**: These are tightly coupled (services use DBs, schema design affects APIs)
2. **Frontend + UX**: UI implementation and UX design should inform each other
3. **DevOps + Testing**: Infrastructure and quality are both platform concerns

**Keep specialized**:
- **Product**: Unique methodology (RICE, discovery, prioritization)
- **Security**: Critical domain that needs dedicated focus

### Benefits Achieved
- ✅ **Reduced cognitive load**: 5 agents vs 10 easier to understand
- ✅ **Better routing**: Fewer options = clearer decisions
- ✅ **Holistic expertise**: Consolidated agents give end-to-end perspective
  - Example: backend-db-expert can design API AND optimize the queries it generates
  - Example: frontend-ux-expert can design UX AND implement it performantly
- ✅ **Easier maintenance**: 5 agent definitions to keep updated vs 10

---

## Impact on /consult Command

The `/consult` command now has simpler expert selection:

**Before** (10 options):
```
Keywords: "api", "database", "schema"
Possible matches: backend-expert, database-expert → confusion, needs disambiguation
```

**After** (5 options):
```
Keywords: "api", "database", "schema"
Clear match: backend-db-expert → handles both concerns holistically
```

---

## Data Expert & DevRel Expert Archival

**Why archived (not merged)**:
- **Usage**: <5% (estimated from analysis)
- **Overlap**: Expertise covered by other agents
  - Data analytics → backend-db-expert (database queries, pipelines)
  - API documentation → backend-db-expert (API design includes docs)

**When to restore**:
If you're working on a project that's primarily data-focused (analytics platform) or developer-facing (API product), you can restore these agents:

```bash
cd /Users/sebasing/Projects/Agent007/.claude/agents
cp _archive/data-expert.md .
cp _archive/devrel-expert.md .
```

Then update `.claude/README.md` to include them in the agent table.

---

## Version History

| Version | Agents | Date | Change |
|---------|--------|------|--------|
| v2.0.0 | 10 | 2025-01 | Initial full team |
| v3.0.0 | 5 | 2026-02-20 | Consolidated based on usage analysis |

---

**Status**: Consolidation complete
**Next**: Update README.md agent table to reflect 5 active agents
