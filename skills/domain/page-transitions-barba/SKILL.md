---
name: page-transitions-barba
description: "Add barba.js page transitions integrated with GSAP. Workflow: install → entry init → default transition → named per-route → hooks."
invokable: true
version: 1.0.0
when:
  keywords: [barba, page transition, smooth transition, route transition, animated navigation]
canonical-sources:
  - url: https://barba.js.org/docs/getting-started/intro/
allowed-tools:
  - Bash(npm install *)
  - Bash(pnpm add *)
  - Bash(bun add *)
  - Read
  - Write
  - Edit
references:
  - "../gsap/SKILL.md"
---

# page-transitions-barba

Wires `@barba/core` + GSAP into a non–App-Router project to deliver smooth page transitions. Barba intercepts navigation, swaps the `data-barba="container"` block, and runs `leave` / `enter` hooks where GSAP timelines live.

## Hard Rules

- ALWAYS verify the target framework FIRST. Barba is for: plain HTML/JS, Vite SPAs, Next.js Pages Router, Astro (with `view-transitions` opt-out), Remix Pages mode.
- NEVER use barba in Next.js **App Router**. Use the native View Transitions API + `unstable_ViewTransition` (or CSS `view-transition-name`) instead — barba's DOM-swap fights React's reconciler.
- ALWAYS wrap the page in `data-barba="wrapper"` and the swappable block in `data-barba="container"`. Barba does nothing without those.
- ALWAYS delegate the actual animation to GSAP timelines — see Skill('gsap'). Barba is the router; GSAP is the choreographer.
- NEVER animate `display: none` → `display: block`. Use `opacity` + `transform` and toggle visibility via `onComplete`.
- ALWAYS handle scroll restoration in `afterEnter` — barba does not restore scroll automatically.
- ALWAYS move focus to `<main>` (or the new page heading) in `afterEnter` for a11y; intercepted SPA navigation skips browser focus reset.

## Anti-Patterns

- Initializing barba **inside** a React/Vue component — must run once at the entry point, before mount.
- Using `prevent: 'all'` then forgetting to handle external links — links to other origins need `target="_blank"` or an explicit rule.
- Animating layout properties (`width`, `height`, `top`) — kills FPS. Stick to `transform` + `opacity`.
- Forgetting `gsap.killTweensOf(...)` on `beforeLeave` — orphaned tweens leak across routes.
- Mixing barba transitions with framework router transitions (Vue Router transition, React Router) — they fight.

## Workflow

1. **Verify framework** (read `package.json` + project files). If Next.js App Router → STOP and switch to View Transitions API.
2. **Install**: `npm i @barba/core gsap` (auto-detect `pnpm-lock.yaml` / `bun.lockb` and adjust).
3. **Mark up the layout**: add `data-barba="wrapper"` to the persistent shell and `data-barba="container" data-barba-namespace="<route>"` to the per-page block.
4. **Init at entry**: in `main.ts` / `_app.tsx` / `entry.client.tsx`, call `initBarba()` ONCE.
5. **Add default transition** (fade) → ship it → verify in browser.
6. **Add named per-route transitions** using `from.namespace` / `to.namespace`.
7. **Wire scroll + focus** in `afterEnter`.

## Snippet — `src/lib/barba.ts`

```ts
import barba from '@barba/core';
import gsap from 'gsap';

export function initBarba(): void {
  barba.init({
    debug: import.meta.env.DEV,
    preventRunning: true,
    transitions: [
      // Default — applies when no named transition matches
      {
        name: 'fade',
        async leave({ current }) {
          gsap.killTweensOf(current.container);
          await gsap.to(current.container, { opacity: 0, duration: 0.25, ease: 'power2.in' });
        },
        async enter({ next }) {
          gsap.set(next.container, { opacity: 0 });
          await gsap.to(next.container, { opacity: 1, duration: 0.35, ease: 'power2.out' });
        },
      },
      // Named — only home → product
      {
        name: 'home-to-product',
        from: { namespace: ['home'] },
        to: { namespace: ['product'] },
        async leave({ current }) {
          await gsap.to(current.container, { y: -40, opacity: 0, duration: 0.3, ease: 'power3.in' });
        },
        async enter({ next }) {
          gsap.set(next.container, { y: 40, opacity: 0 });
          await gsap.to(next.container, { y: 0, opacity: 1, duration: 0.45, ease: 'power3.out' });
        },
      },
    ],
  });

  // Scroll restoration + focus management
  barba.hooks.afterEnter(({ next }) => {
    window.scrollTo({ top: 0, behavior: 'instant' });
    const main = next.container.querySelector<HTMLElement>('main, h1');
    main?.focus({ preventScroll: true });
  });

  // Defensive: kill stray tweens before each leave
  barba.hooks.beforeLeave(({ current }) => {
    gsap.killTweensOf(current.container);
  });
}
```

## Entry-Point Wiring

| Stack | File | Call |
|---|---|---|
| Vite (vanilla) | `src/main.ts` | `initBarba()` after DOM ready |
| Next.js Pages Router | `pages/_app.tsx` | inside `useEffect(() => { initBarba(); }, [])` |
| Astro | `src/layouts/Base.astro` `<script>` | `initBarba()` (set `viewTransitions: false`) |
| Plain HTML | `<script type="module">` at end of body | `initBarba()` |

## Markup Contract

```html
<body data-barba="wrapper">
  <header><!-- persistent --></header>
  <main data-barba="container" data-barba-namespace="home" tabindex="-1">
    <!-- page content -->
  </main>
  <footer><!-- persistent --></footer>
</body>
```

`tabindex="-1"` on the container is required for the focus-management hook above.

## Verification

- `npm ls @barba/core gsap` returns versions.
- DOM has `[data-barba="wrapper"]` and `[data-barba="container"]`.
- Navigating between two pages plays the transition (visible fade or slide).
- DevTools → Performance: no layout thrash; transforms stay on the compositor thread.
- Scroll resets to top on every navigation; keyboard focus lands on `<main>`.
- No console warnings from barba (`debug: true` flushes them).

## Anti-Pattern Reminder (App Router)

If `app/` directory exists at the project root → DO NOT install barba. Use:

```tsx
// app/layout.tsx — App Router native transitions
import { unstable_ViewTransition as ViewTransition } from 'react';
export default function Layout({ children }) {
  return <ViewTransition>{children}</ViewTransition>;
}
```

Barba and the App Router router will both try to own navigation — symptoms: hydration mismatch, stuck transitions, leaked event listeners. There is no fix; pick one.
