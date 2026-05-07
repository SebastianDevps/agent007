# GSAP — Plugins Reference

**Registration:** `gsap.registerPlugin(ScrollToPlugin, Flip, Draggable, ...)` — once before first use.

**All formerly paid Club GSAP plugins are now free** (Flip, SplitText, MorphSVG, DrawSVG, Physics2D, etc.).

## Scroll

- `ScrollToPlugin`: `gsap.to(window, { scrollTo: { y: "#section", offsetY: 50 } })`
- `ScrollSmoother`: Smooth native scroll. Requires ScrollTrigger + `#smooth-wrapper > #smooth-content`.

## DOM/UI

- `Flip`: `Flip.getState(".item")` → DOM change → `Flip.from(state, { duration: 0.5 })`
- `Draggable`: `Draggable.create(".box", { type: "x,y", bounds: "#container", inertia: true })`
- `Observer`: `Observer.create({ target, onUp, onDown, onLeft, onRight, tolerance })`

## Text

- `SplitText`: `SplitText.create(".heading", { type: "words, chars" })` → animate `split.chars`. Options: `autoSplit`, `onSplit(self)`, `mask`, `aria`, `smartWrap`. Return animation from `onSplit()` for auto cleanup. Revert with `split.revert()`.
- `ScrambleText`: `scrambleText: { text: "New message", chars: "01", revealDelay: 0.5 }`

## SVG

- `DrawSVG`: Animate stroke reveal. `drawSVG: "0% 100%"` = full; `"20% 80%"` = middle segment. Requires `stroke` + `stroke-width`.
- `MorphSVG`: Morph path `d`. `morphSVG: "#target"` or `{ shape, type: "linear"|"rotational", shapeIndex, smooth }`. `MorphSVGPlugin.convertToPath("circle, rect")`.
- `MotionPath`: `motionPath: { path: "#path", align: "#path", alignOrigin: [0.5, 0.5], autoRotate: true }`

## Easing

CustomEase, EasePack (SlowMo, RoughEase), CustomWiggle, CustomBounce.

## Physics

Physics2D (`velocity`, `angle`, `gravity`), PhysicsProps (`x: { velocity, end }`).

## Dev

`GSDevTools.create({ animation: tl })` — remove from production.

## Do Not

- Use plugin without registering
- Ship GSDevTools to production
