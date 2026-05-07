# GSAP — ScrollTrigger Reference

**Registration:** `gsap.registerPlugin(ScrollTrigger)` — once.

## Basic Usage

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

## Key Config

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

## Common Patterns

**Batch:** `ScrollTrigger.batch(".item", { onEnter: (els) => gsap.to(els, { ... }), interval: 0.1 })`

**Scrub:** `scrub: true` (direct) or `scrub: 1` (1s lag). Never use `scrub` + `toggleActions` together.

**Horizontal scroll:** Pin section → animate `x`/`xPercent` with `ease: "none"` → attach as `containerAnimation`. **`ease: "none"` is required.**

**Cleanup:** `ScrollTrigger.refresh()` after layout changes · `ScrollTrigger.getAll().forEach(t => t.kill())`

## Do Not

- `scrub` + `toggleActions` together
- Non-`"none"` ease on containerAnimation tween
- Create ScrollTriggers out of page order without `refreshPriority`
- Leave `markers: true` in production
