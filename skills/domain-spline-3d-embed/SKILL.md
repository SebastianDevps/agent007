---
name: spline-3d-embed
description: "Embed Spline 3D scenes safely: lazy-load, perf-gated, mobile-aware, a11y-conscious. Never ships without LCP measurement."
version: 1.0.0
when:
  keywords: [spline, 3d, three, hero animation, interactive 3d, splinetool]
allowed-tools:
  - Bash(npm install *)
  - Bash(pnpm add *)
  - Read
  - Write
  - Edit
  - WebFetch
---

# Spline 3D Embed — Safe Web Integration

## Agent directive

When the user wants to embed a Spline scene, you DO NOT just drop `<Spline url="..."/>`. You measure LCP first, lazy-load by default, gate on Save-Data and `prefers-reduced-motion`, and add a11y. A 5MB Spline scene on a hero kills mobile Core Web Vitals — refuse to ship without measurement.

If user wants Spline in SSR, push back: scenes must run client-only.

---

## Workflow (executable)

1. **Receive Spline URL** from the user (`https://prod.spline.design/.../scene.splinecode`).
2. **Inspect scene size**: ask user for the size, or fetch HEAD and check `Content-Length`. If > 3MB → mandatory lazy load + intersection observer. If > 8MB → push back, ask if they can simplify the scene.
3. **Install runtime**:
   - React/Next: `npm install @splinetool/react-spline @splinetool/runtime`
   - Vanilla JS: `npm install @splinetool/runtime`
4. **Generate component** with: dynamic import (no SSR), Suspense fallback, intersection observer, `prefers-reduced-motion` guard, `saveData` guard, a11y wrapper.
5. **Measure LCP before/after**: instruct user to run Lighthouse mobile on the page before adding Spline and again after. Block "done" claim until they share both numbers.

---

## Hard rules

- Never render Spline in SSR. Always `dynamic(() => ..., { ssr: false })` in Next.js.
- Always wrap in Suspense with a static fallback that matches the final scene's aspect ratio (avoid CLS).
- Always honor `prefers-reduced-motion: reduce` — show static fallback instead.
- Always honor `navigator.connection.saveData === true` — skip the scene.
- Always add `aria-label` to the wrapper and `tabindex={-1}` (3D scenes are not keyboard-tabbable).
- Always lazy-load when scene > 3MB or below the fold (intersection observer).
- Always ship a non-3D fallback image — Spline is enhancement, not a hard requirement.

---

## Anti-patterns

- `<Spline url={...} />` rendered eagerly above the fold on mobile → tanks LCP.
- Loading Spline in SSR → hydration mismatch, server crash on `window` access.
- No fallback while loading → 2s blank space + CLS when scene appears.
- Ignoring `prefers-reduced-motion` → accessibility violation, user discomfort.
- Same scene file used desktop and mobile without conditional → mobile users download 5MB+ for no reason.
- Scene as a tab focusable element with no instructions → screen-reader users get nothing useful.

---

## Complete reference (Next.js, App Router)

```tsx
"use client";

import dynamic from "next/dynamic";
import { Suspense, useEffect, useRef, useState } from "react";

const Spline = dynamic(() => import("@splinetool/react-spline"), {
  ssr: false,
  loading: () => <SceneFallback />,
});

const SCENE_URL = "https://prod.spline.design/your-id/scene.splinecode";
const ASPECT = "aspect-[16/9]"; // match scene to avoid CLS

export function SplineScene({ alt }: { alt: string }): JSX.Element {
  const [render, setRender] = useState(false);
  const [skip, setSkip] = useState<"motion" | "data" | null>(null);
  const ref = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (typeof window === "undefined") return;
    if (window.matchMedia("(prefers-reduced-motion: reduce)").matches) {
      setSkip("motion"); return;
    }
    const conn = (navigator as Navigator & { connection?: { saveData?: boolean } }).connection;
    if (conn?.saveData === true) { setSkip("data"); return; }

    if (!ref.current) return;
    const obs = new IntersectionObserver((entries) => {
      if (entries.some((e) => e.isIntersecting)) { setRender(true); obs.disconnect(); }
    }, { rootMargin: "200px" });
    obs.observe(ref.current);
    return () => obs.disconnect();
  }, []);

  if (skip !== null) return <SceneFallback />;

  return (
    <div ref={ref} role="img" aria-label={alt} tabIndex={-1}
         className={`relative w-full ${ASPECT}`}>
      {render ? (
        <Suspense fallback={<SceneFallback />}>
          <Spline scene={SCENE_URL} />
        </Suspense>
      ) : <SceneFallback />}
    </div>
  );
}

function SceneFallback(): JSX.Element {
  return <div aria-hidden className={`w-full ${ASPECT} bg-gradient-to-br
    from-slate-100 to-slate-200 animate-pulse rounded-lg`} />;
}
```

---

## Performance gates (mandatory)

Before shipping, the user must confirm:

1. **LCP measurement done**: Lighthouse mobile run before and after adding Spline. Share both numbers.
2. **Scene size verified**: known and under 8MB. If 3-8MB, lazy load is mandatory.
3. **Mobile tested**: opens on a throttled "Slow 4G" Lighthouse profile without freezing.
4. **Fallback path tested**: with `prefers-reduced-motion: reduce` enabled in DevTools, the static fallback renders instead of the scene.

If the user pushes back ("just embed it"), respond:
> A Spline scene without these gates breaks mobile users. The minimum is lazy load + reduced-motion fallback. I will not skip those.

---

## Vanilla JS fallback (when not using React)

```html
<div id="spline-canvas" role="img" aria-label="Hero scene" tabindex="-1"
     style="aspect-ratio: 16/9; width: 100%;"></div>

<script type="module">
  if (!window.matchMedia("(prefers-reduced-motion: reduce)").matches) {
    const { Application } = await import("@splinetool/runtime");
    const canvas = document.createElement("canvas");
    document.getElementById("spline-canvas").appendChild(canvas);
    const app = new Application(canvas);
    await app.load("https://prod.spline.design/your-id/scene.splinecode");
  }
</script>
```

---

## Validation checklist

Before returning generated code, confirm:

- [ ] `dynamic(..., { ssr: false })` used (Next.js)
- [ ] Suspense fallback matches final aspect ratio (no CLS)
- [ ] `prefers-reduced-motion` guarded
- [ ] `navigator.connection.saveData` guarded
- [ ] Intersection observer when scene > 3MB or below the fold
- [ ] `role="img"` + `aria-label` + `tabIndex={-1}` on wrapper
- [ ] LCP measurement requested from user
- [ ] Static fallback path tested

## Sources

- https://docs.spline.design/doc/exporting-spline-scenes-as-react-components/ — integración React/Next oficial
