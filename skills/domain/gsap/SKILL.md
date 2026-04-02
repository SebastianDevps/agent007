---
name: gsap
description: "Official GSAP skill — core API, timelines, ScrollTrigger, plugins (Flip/SplitText/MorphSVG), React/Vue/Svelte integration, performance, utils. Use for any GSAP animation, scroll, or DOM motion task."
version: 2.0.0
invokable: false
accepts_args: false
when:
  - task_type: [feature, consult]
    keywords: [animation, gsap, tween, gsap.to, gsap.from, easing, stagger, motion, timeline, sequence,
               scroll animation, scrolltrigger, parallax, pin, scrub, scroll-linked,
               flip animation, draggable, splittext, morphsvg, motionpath, gsap plugin,
               gsap react, usegsap, animation react, gsap next.js, gsap cleanup,
               gsap vue, gsap svelte, gsap nuxt, gsap sveltekit,
               animation performance, 60fps, jank, will-change, quickto,
               gsap utils, clamp, maprange, normalize, snap, interpolate]
---

# GSAP — Complete Reference

---

## Core API

**Tween methods:** `gsap.to`, `gsap.from`, `gsap.fromTo`, `gsap.set`. Always camelCase properties.

**Common vars:** `duration`, `delay`, `ease`, `stagger`, `overwrite`, `repeat`, `yoyo`, `onComplete/Start/Update`, `immediateRender`.

**Transform aliases** (prefer over raw `transform`): `x`, `y`, `z`, `xPercent`, `yPercent`, `scale`, `scaleX`, `scaleY`, `rotation`, `rotationX`, `rotationY`, `skewX`, `skewY`, `transformOrigin`.

**Special props:** `autoAlpha` (opacity + visibility:hidden at 0), CSS variables, `svgOrigin`, directional rotation suffixes (`_short`, `_cw`, `_ccw`), `clearProps`.

**Eases:** `"power1.out"` (default), `"power3.inOut"`, `"back.out(1.7)"`, `"elastic.out(1, 0.3)"`, `"none"`. Custom: `CustomEase.create("name", "...")`.

**Function-based values:** `x: (i, target, targets) => i * 50`

**Relative values:** `x: "+=20"`, `"-=30"`, `"*=2"`, `"/=2"`

**Defaults:** `gsap.defaults({ duration: 0.6, ease: "power2.out" })`

**matchMedia** (GSAP 3.11+): Responsive + `prefers-reduced-motion`. Reverts automatically. Use `context.conditions` for multi-condition form.

**Do Not:** Animate layout properties when transforms work; use `svgOrigin` + `transformOrigin` together; rely on `immediateRender: true` stacking same property.

---

## Timeline

**Create:**
```javascript
const tl = gsap.timeline({ defaults: { duration: 0.5, ease: "power2.out" } });
tl.to(".a", { x: 100 })
  .to(".b", { y: 50 })
  .to(".c", { opacity: 0 });
```

**Position parameter (3rd arg):**
- `0` — absolute 0s · `"+=0.5"` — after prev end · `"-=0.2"` — before prev end
- `"labelName"` / `"labelName+=0.3"` — at label
- `"<"` — same start as prev · `">"` — after prev · `"<0.2"` — 0.2s after prev start

**Labels:** `tl.addLabel("intro", 0)` → `tl.to(".a", {}, "intro")` · `tl.play("outro")` · `tl.tweenFromTo("intro", "outro")`

**Nesting:** `master.add(child, 0)`

**Playback:** `.play()`, `.pause()`, `.reverse()`, `.restart()`, `.time(2)`, `.progress(0.5)`, `.kill()`

**Do Not:** Chain with `delay` when timeline can sequence; forget `defaults`; put ScrollTrigger on child tweens inside a timeline.

---

## ScrollTrigger

**Registration:** `gsap.registerPlugin(ScrollTrigger)` — once.

**Basic:**
```javascript
gsap.to(".box", {
  x: 500,
  scrollTrigger: {
    trigger: ".box",
    start: "top center",
    end: "bottom center",
    toggleActions: "play reverse play reverse"
  }
});
```

**Key config:**

| Property | Description |
|----------|-------------|
| `trigger` | Element that defines start position |
| `start` / `end` | `"triggerPos viewportPos"`, number, fn, or `"clamp(...)"` |
| `scrub` | `true` or number (lag seconds) — links progress to scroll |
| `toggleActions` | 4 actions: onEnter, onLeave, onEnterBack, onLeaveBack |
| `pin` | `true` pins trigger; animate children, not pinned element |
| `horizontal` | `true` for horizontal scroll |
| `scroller` | Custom scroll container |
| `markers` | Dev only — remove in production |
| `once` | Kill after reached once |
| `snap` | Snap to progress values |
| `containerAnimation` | Nested triggers inside fake horizontal scroll |
| callbacks | `onEnter`, `onLeave`, `onEnterBack`, `onLeaveBack`, `onUpdate`, `onToggle` |

**Batch:** `ScrollTrigger.batch(".item", { onEnter: (els) => gsap.to(els, { ... }), interval: 0.1 })`

**Scrub:** `scrub: true` (direct) or `scrub: 1` (1s lag). Never use `scrub` + `toggleActions` together.

**Horizontal scroll:** Pin section → animate `x`/`xPercent` with `ease: "none"` → attach as `containerAnimation`. **`ease: "none"` is required.**

**Cleanup:** `ScrollTrigger.refresh()` after layout changes · `ScrollTrigger.getAll().forEach(t => t.kill())`

**Do Not:** `scrub` + `toggleActions` together; non-`"none"` ease on containerAnimation tween; create ScrollTriggers out of page order without `refreshPriority`; leave `markers: true` in production.

---

## Plugins

**Registration:** `gsap.registerPlugin(ScrollToPlugin, Flip, Draggable, ...)` — once before first use.

**All formerly paid Club GSAP plugins are now free** (Flip, SplitText, MorphSVG, DrawSVG, Physics2D, etc.).

**Scroll:**
- `ScrollToPlugin`: `gsap.to(window, { scrollTo: { y: "#section", offsetY: 50 } })`
- `ScrollSmoother`: Smooth native scroll. Requires ScrollTrigger + `#smooth-wrapper > #smooth-content`.

**DOM/UI:**
- `Flip`: `Flip.getState(".item")` → DOM change → `Flip.from(state, { duration: 0.5 })`
- `Draggable`: `Draggable.create(".box", { type: "x,y", bounds: "#container", inertia: true })`
- `Observer`: `Observer.create({ target, onUp, onDown, onLeft, onRight, tolerance })`

**Text:**
- `SplitText`: `SplitText.create(".heading", { type: "words, chars" })` → animate `split.chars`. Options: `autoSplit`, `onSplit(self)`, `mask`, `aria`, `smartWrap`. Return animation from `onSplit()` for auto cleanup. Revert with `split.revert()`.
- `ScrambleText`: `scrambleText: { text: "New message", chars: "01", revealDelay: 0.5 }`

**SVG:**
- `DrawSVG`: Animate stroke reveal. `drawSVG: "0% 100%"` = full; `"20% 80%"` = middle segment. Requires `stroke` + `stroke-width`.
- `MorphSVG`: Morph path `d`. `morphSVG: "#target"` or `{ shape, type: "linear"|"rotational", shapeIndex, smooth }`. `MorphSVGPlugin.convertToPath("circle, rect")`.
- `MotionPath`: `motionPath: { path: "#path", align: "#path", alignOrigin: [0.5, 0.5], autoRotate: true }`

**Easing:** CustomEase, EasePack (SlowMo, RoughEase), CustomWiggle, CustomBounce.

**Physics:** Physics2D (`velocity`, `angle`, `gravity`), PhysicsProps (`x: { velocity, end }`).

**Dev:** `GSDevTools.create({ animation: tl })` — remove from production.

**Do Not:** Use plugin without registering; ship GSDevTools to production.

---

## React Integration

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

## Vue / Svelte Integration

**Principles (All Frameworks):** Create tweens/ScrollTriggers after DOM is available. Kill/revert in unmount. Scope selectors to component root.

**Vue 3 (Composition API):**
```javascript
onMounted(() => { ctx = gsap.context(callback, container.value); });
onUnmounted(() => ctx?.revert());
```

**Svelte:**
```javascript
onMount(() => {
  const ctx = gsap.context(() => { ... }, container);
  return () => ctx.revert();
});
```

**Scoping:** Always pass container element as second arg to `gsap.context(callback, scope)`. Never use unscoped selector strings in components.

**ScrollTrigger cleanup:** Create inside same `gsap.context()`. Call `ScrollTrigger.refresh()` after layout changes (`nextTick` in Vue, `tick` in Svelte).

---

## Performance

**Prefer transforms + opacity:** `x`, `y`, `scale`, `rotation`, `opacity`. Avoid `width`, `height`, `top`, `left`, `margin`.

**`will-change`:** `will-change: transform` in CSS only on elements that animate.

**Many elements:** Use `stagger` over manual delays. Reuse timelines. Virtualize long lists.

**Mouse followers / frequent updates:** Use `gsap.quickTo()`:
```javascript
const xTo = gsap.quickTo("#id", "x", { duration: 0.4, ease: "power3" });
// call xTo(e.pageX) in mousemove handler
```

**ScrollTrigger:** `pin` only what's needed. Debounce `ScrollTrigger.refresh()`. Test `scrub` on low-end devices.

**Do Not:** Animate layout properties for movement; `will-change` on every element; hundreds of simultaneous tweens untested; stray tweens/ScrollTriggers not killed.

---

## Utils (`gsap.utils.*`)

No plugin registration needed.

**Function form:** Omit last value arg for reusable function — e.g. `gsap.utils.clamp(0, 100)` returns a function. Exception: `random()` — pass `true` as last arg.

| Utility | Signature | Purpose |
|---------|-----------|---------|
| `clamp` | `(min, max, value?)` | Constrain value |
| `mapRange` | `(inMin, inMax, outMin, outMax, value?)` | Map between ranges |
| `normalize` | `(min, max, value?)` | Normalize to 0–1 |
| `interpolate` | `(start, end, progress?)` | Numbers, colors, matching-key objects |
| `random` | `(min, max[, snap, returnFn])` | Random number/from array |
| `snap` | `(snapTo, value?)` | Snap to multiple or nearest array value |
| `wrap` | `(min, max, value?)` | Cyclic wrap (370° → 10° in 0–360) |
| `wrapYoyo` | `(min, max, value?)` | Wrap with bounce at ends |
| `distribute` | `(config)` | Spread values across targets (`base`, `amount`, `from`, `grid`, `ease`) |
| `pipe` | `(...fns)` | Compose: `pipe(normalize, snap)(value)` |
| `toArray` | `(value, scope?)` | NodeList/element/selector → array |
| `selector` | `(scope)` | Scoped selector fn (works with React refs) |
| `getUnit` | `("100px")` | → `"px"` |
| `unitize` | `(100, "px")` | → `"100px"` |
| `splitColor` | `("red")` | → `[255, 0, 0]`; pass `true` for HSL |
| `shuffle` | `(array)` | Random order in place |

**Do Not:** Assume mapRange/normalize handle CSS units (numbers only).
