# Archived Skills (Low Usage <5%)

**Date**: 2026-02-20
**Reason**: Skills archived based on usage analysis from critical consultation

---

## Archived Skills (6)

| Skill | Original Location | Usage Estimate | Reason for Archival |
|-------|------------------|----------------|---------------------|
| `analytics-setup` | `data/` | <3% | Event taxonomy & metrics setup - niche use case |
| `data-pipeline-design` | `data/` | <3% | ETL & data warehousing - niche use case |
| `developer-portal` | `devrel/` | <2% | Portal structure & SDK templates - very niche |
| `design-system` | `product/` | <5% | Design tokens & components - covered by frontend-ux-expert |
| `ux-research` | `product/` | <5% | User flows & wireframes - covered by frontend-ux-expert |
| `feature-prioritization` | `product/` | <5% | RICE/ICE scoring - covered by product-expert |

---

## Active Skills Remaining (10)

### Core (Always Active)
- `_core/verification-enforcement`
- `_core/anti-rationalization`
- `_core/context-awareness`
- `_core/decision-memory`

### Orchestration
- `_orchestration/session-orchestrator`

### Workflows
- `workflow/brainstorming`
- `workflow/writing-plans`
- `workflow/tdd`

### Quality Gates
- `quality-gates/systematic-debugging`

### Domain-Specific
- `api-design-principles`
- `architecture-patterns`
- `resilience-patterns`
- `nestjs-code-reviewer`
- `frontend-design`
- `react-best-practices`

### Product (Retained)
- `product/product-discovery` (medium usage, valuable)

**Total active skills**: 16

---

## Rationale

### Why Archive These Skills?

**1. Low Utilization**
- Usage analysis showed <5% invocation rate
- For a solo-developer tool, this is dead weight
- 90%+ of value comes from core + workflow skills

**2. Capability Overlap**
- `design-system`, `ux-research` → Covered by `frontend-ux-expert` agent
- `feature-prioritization` → Covered by `product-expert` agent
- `developer-portal` → API documentation covered by `backend-db-expert`

**3. Niche Use Cases**
- `analytics-setup`, `data-pipeline-design` → Only useful for data-focused projects
- Most projects use Agent007 for backend/frontend development, not data engineering

### When to Restore

If you're working on specific project types:

**Data/Analytics project**:
```bash
cd /Users/sebasing/Projects/Agent007/.claude/skills
mkdir -p data
cp _archive/analytics-setup data/
cp _archive/data-pipeline-design data/
```

**API product project** (developer-facing):
```bash
cd /Users/sebasing/Projects/Agent007/.claude/skills
mkdir -p devrel
cp _archive/developer-portal devrel/
```

**Design-heavy project**:
```bash
cd /Users/sebasing/Projects/Agent007/.claude/skills/product
cp ../_archive/design-system .
cp ../_archive/ux-research .
```

Then update `.claude/README.md` to include them in the skills table.

---

## Benefits of Archival

✅ **Reduced cognitive load**: 16 active skills vs 22 is easier to navigate
✅ **Faster skill discovery**: Router has fewer options to scan
✅ **Clearer documentation**: README skill tables are more focused
✅ **Easier maintenance**: Fewer skills to keep updated with framework changes

---

## Skill Coverage After Consolidation

**Still covered** (by agents):
- Design systems → `frontend-ux-expert` has design-system skill built-in
- UX research → `frontend-ux-expert` has ux-research methodology
- Feature prioritization → `product-expert` uses RICE/ICE methodology
- API documentation → `backend-db-expert` includes API design principles
- Analytics → `backend-db-expert` can design analytics queries/schema

**Not covered** (niche, restore if needed):
- Advanced data pipelines (ETL, data warehousing, real-time streaming)
- Developer portal creation (onboarding flows, SDK generation)

---

**Status**: Skills archived successfully
**Impact**: Ecosystem reduced from 22 skills → 16 active skills (27% reduction)
