# GSAP — Performance & Utils Reference

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
