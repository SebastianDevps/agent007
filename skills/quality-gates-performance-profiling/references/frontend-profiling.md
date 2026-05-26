---
name: performance-profiling/frontend-profiling
description: "Browser / React frontend profiling — Core Web Vitals, render bottlenecks, bundle composition."
---

# Frontend Profiling — Browser / React / Next.js

## Tooling

| Tool | What it shows | When |
|---|---|---|
| Lighthouse (CLI or DevTools) | LCP, INP, CLS, TBT, bundle warnings | Page-level baseline |
| Chrome DevTools Performance tab | Frame timeline, layout shifts, scripting cost | Interaction bottleneck |
| React DevTools Profiler | Component render count + duration | "Why is this re-rendering?" |
| `webpack-bundle-analyzer` / `@next/bundle-analyzer` | Bundle composition | Bundle is too big |
| `source-map-explorer` | Source map → byte attribution | "What's in main.js?" |
| `web-vitals` library | Real-user CWV in production | Field data, not lab |

## Standard protocol

### 1. Baseline — Lighthouse CLI

```bash
npx lighthouse http://localhost:3000/page \
  --preset=desktop \
  --output=json --output-path=./lh-before.json \
  --chrome-flags="--headless"

# Or mobile preset (more demanding):
npx lighthouse http://localhost:3000/page \
  --preset=mobile \
  --throttling-method=simulate \
  --output=json --output-path=./lh-mobile-before.json
```

Record:
- LCP (target <2.5s) · INP (<200ms) · CLS (<0.1) · TBT (<200ms)
- Performance score
- Bundle warnings ("Avoid enormous network payloads")

### 2. Identify the dominant cost

Lighthouse audit categories show what dominates:
- **JavaScript execution time** → React Profiler + flame graph
- **Render-blocking resources** → defer/async, code-splitting
- **Largest Contentful Paint element** → preload, priority hint, server-side
- **Cumulative Layout Shift** → fixed dimensions, font swap strategy

### 3. Drill in

#### Render bottleneck — React DevTools Profiler

```
1. Open DevTools → React → Profiler tab
2. Click "Record" → perform the slow interaction → Stop
3. View flame chart:
   - Yellow = expensive renders
   - Look for components rendering 10x+ for one user action
4. "Ranked" view → top components by self-time
```

Common causes:
- New object/array literal in props every render → child re-renders unnecessarily
- Context value not memoized → all consumers re-render
- Inline function in `.map()` of a large list

#### Layout / paint — DevTools Performance tab

```
1. Performance tab → Record → user action → Stop
2. Look for:
   - Long tasks (>50ms) blocking the main thread
   - "Layout" rectangles (forced synchronous reflow)
   - "Recalculate Style" spikes
3. The "Web Vitals" track shows LCP/CLS markers in time
```

#### Bundle bloat — bundle-analyzer

```bash
# Next.js
ANALYZE=true pnpm build
# → opens bundle visualization in browser

# Or generic:
npx source-map-explorer build/static/js/*.js
```

Look for:
- Large libraries imported in full instead of cherry-picked (e.g., `lodash` instead of `lodash/debounce`)
- Polyfills duplicated across chunks
- Server-only code leaked to the client bundle (Node modules, secrets)

### 4. Verify with a second Lighthouse run

```bash
# Apply fix → re-run lighthouse with same flags → compare
```

### 5. Report format

```
## Frontend Profiling Report — /dashboard (mobile)

| Metric | Baseline | After fix | Target | Δ |
|---|---|---|---|---|
| LCP | 4.2s | 1.9s | <2.5s | -55% ✓ |
| INP | 380ms | 140ms | <200ms | -63% ✓ |
| CLS | 0.18 | 0.04 | <0.1 | -78% ✓ |
| Performance score | 47 | 89 | >85 | +42 ✓ |

Root cause (React Profiler): UserList re-rendered on every parent state
change due to inline filter function. Components: 3,200 renders for one
scroll event.

Fix: useMemo for the filter function + React.memo on UserListItem.
Renders: 3,200 → 18 per scroll.

Handoff: none — fix applied in components/UserList.tsx:45.
```

## Hard rules

- NEVER optimize without React Profiler evidence of a render problem
- NEVER add `useMemo`/`useCallback` "just in case" — profile first
- NEVER trust desktop-only Lighthouse for mobile-bound users
- NEVER compare numbers without same throttling preset
- ALWAYS measure both lab (Lighthouse) AND field (web-vitals on prod) when claim is "production users feel it"

## Anti-patterns

| Anti-pattern | Reality |
|---|---|
| "Memoize everything" | Wastes memory, hurts readability, often no measurable win |
| "Lazy-load every component" | Cold-start penalty per chunk. Load above-the-fold eagerly |
| "Compress images more" | Run Lighthouse first — you may already be image-optimal |
| "Add a CDN" | Fix code first. CDN masks issues, doesn't fix them |
| Single Lighthouse run as truth | Variance is real. Run 5x, take median |

## When to hand off

| Discovery | Hand off to |
|---|---|
| Server response time >500ms is the LCP bottleneck | `Skill('backend-profiling')` |
| Bundle includes server-only modules | `frontend-ux-expert` for code-split refactor |
| CSS is the blocker (paint long) | `frontend-ux-expert` for critical CSS extraction |
| 3rd-party script dominates | Discuss with stakeholder before removing |
