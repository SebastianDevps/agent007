# GSAP — React / Vue / Svelte Integration

## React

**Install:** `npm install gsap @gsap/react`

**Prefer `useGSAP()` hook:**
```javascript
import { useGSAP } from "@gsap/react";
gsap.registerPlugin(useGSAP);

useGSAP(() => {
  gsap.to(".box", { x: 100 });
}, { scope: containerRef });
```

**Config (2nd arg):** `{ dependencies: [endX], scope: container, revertOnUpdate: true }`

**`contextSafe`:** Wrap post-`useGSAP` event handlers: `contextSafe(() => { ... })` — tracked + cleaned up automatically.

**`useEffect` fallback:**
```javascript
useEffect(() => {
  const ctx = gsap.context(() => { ... }, containerRef);
  return () => ctx.revert();
}, []);
```

**SSR (Next.js):** Never call GSAP during server render. All GSAP code inside `useGSAP` or `useEffect`.

**Do Not:** Unscoped selectors; skip cleanup; run GSAP during SSR; `useGSAP` without registering first.

---

## Vue / Svelte

**Principles (All Frameworks):** Create tweens/ScrollTriggers after DOM is available. Kill/revert in unmount. Scope selectors to component root.

### Vue 3 (Composition API)

```javascript
onMounted(() => { ctx = gsap.context(callback, container.value); });
onUnmounted(() => ctx?.revert());
```

### Svelte

```javascript
onMount(() => {
  const ctx = gsap.context(() => { ... }, container);
  return () => ctx.revert();
});
```

### Scoping Rules

Always pass container element as second arg to `gsap.context(callback, scope)`. Never use unscoped selector strings in components.

### ScrollTrigger Cleanup

Create inside same `gsap.context()`. Call `ScrollTrigger.refresh()` after layout changes (`nextTick` in Vue, `tick` in Svelte).
