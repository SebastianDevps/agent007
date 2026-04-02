# /instinct-status — Instinct Learning System Status

Display all compiled instincts with confidence levels, domain breakdown, and cluster candidates.

---

## Usage

```
/instinct-status
/instinct-status --domain <code-style|testing|git|debugging|architecture>
/instinct-status --min <0.0-1.0>
/instinct-status --json
```

---

## Step 1 — Run the engine

```bash
node .claude/scripts/instinct-engine.js status
```

## Step 2 — Display results

Format the output as a structured report:

```
## Instinct System — Agent007
Status: [N] personal · [N] inherited · [N] evolved

### ⚡ Auto-Apply (confidence ≥ 0.7)
[list with confidence bar, trigger, domain]

### 🟡 Moderado (0.5 – 0.69)
[list]

### 🔵 Tentativo (< 0.5)
[list]

### 🌱 Skill Candidates (evolved/)
[list of cluster-promoted instincts]
```

## Step 3 — Show observation stats

```bash
# Count observations by type
grep -c "" .claude/instincts/observations.jsonl 2>/dev/null || echo 0
```

Report: total observations, sessions tracked, most active domain.

## Step 4 — Offer actions

```
¿Qué deseas hacer?
[C]ompilar observaciones recientes en instincts
[D]ecay — reducir confidence de instincts no reforzados
[K]luster — promover candidatos a skills
[E]xportar — exportar instincts compilados (sin observations)
[R]eset — borrar instincts tentativo (confidence < 0.3)
```

---

## Confidence Scale Reference

| Level | Range | Behavior |
|-------|-------|----------|
| Tentativo | 0.3 | Single observation, not applied automatically |
| Moderado | 0.5 | 2-3 observations, shown as suggestion |
| Auto-Apply | 0.7 | 4+ observations, applied without confirmation |
| Core | 0.9 | Deeply established, session-invariant |

**Decay rate**: -0.05 per session without reinforcement
**Cluster threshold**: 3 related instincts → skill candidate
