---
name: ios-hig-mobile
description: "Mobile-first components following Apple HIG patterns adapted for web (React/Next/PWA). Tab bars, sheets, Dynamic Type, Safe Areas, haptics."
version: 1.0.0
when:
  keywords: [mobile, ios, hig, tab bar, sheet, modal, safe area, dynamic type, haptic, native feel]
allowed-tools:
  - Read
  - Write
  - Edit
  - Glob
---

# iOS HIG Mobile — Web Implementation

## Agent directive

When the user asks for mobile components, "native feel", or iOS-style UI on web — apply HIG patterns adapted to React/Next/PWA. Use Tailwind classes plus Lucide icons. Never ship fixed-pixel text. Always use `env(safe-area-inset-*)`.

If user wants pixel-perfect native UIKit, push back: web cannot fully replicate it. Offer the closest faithful adaptation.

---

## Workflow (executable)

For every component request:

1. **Identify HIG pattern** from user intent (tab bar, sheet, nav bar, list row, segmented control).
2. **Validate against hard rules** (below). Reject configurations that break them.
3. **Generate component** using Tailwind + Lucide, respecting the 5 domains.
4. **Verify**: max 5 tab items, safe-area inset present, no `text-[14px]`-style fixed pixels, `prefers-reduced-motion` honored where animation exists.

---

## Hard rules

- Tab bars: 3 to 5 items. Never 6+. Never 1-2 (use a single button instead).
- Nav bars: back button left, primary action right, title centered.
- Text sizing: `rem`/`em` only. Never `px` for typography.
- Safe areas: every fixed top/bottom UI uses `env(safe-area-inset-*)`.
- Haptics: `navigator.vibrate` is progressive enhancement — never required, never blocking.
- Sheets: use for secondary tasks. Full-screen modals only for self-contained flows (compose, onboarding).
- Touch targets: minimum `h-11 w-11` (44pt equivalent).
- Icons: import from `lucide-react`. Never inline custom SVG when a Lucide equivalent exists.

---

## Anti-patterns

- 6+ tab items "to fit one more feature" → split into More menu or redesign IA.
- `text-[14px]` or `font-size: 14px` → breaks Dynamic Type.
- `pb-4` on a bottom tab bar → ignores home indicator. Use `pb-[env(safe-area-inset-bottom)]`.
- Custom hand-drawn SVG for a chevron → use `lucide-react` `ChevronRight`.
- Requiring haptics for the action to succeed → excludes users on devices without Vibration API.
- Sheet with a back stack → use full-screen navigation instead.
- Tab bar that hides on scroll without user opt-in → confuses orientation.

---

## Domain 1: Navigation patterns

**Tab bar (3-5 items, fixed bottom):**

```tsx
import { Home, Search, Bell, User } from "lucide-react";

export function TabBar() {
  return (
    <nav className="fixed bottom-0 inset-x-0 bg-white/90 backdrop-blur border-t
                    pb-[env(safe-area-inset-bottom)] flex justify-around" role="tablist">
      {[Home, Search, Bell, User].map((Icon, i) => (
        <button key={i} role="tab"
          className="flex flex-col items-center gap-0.5 py-2 h-11 min-w-11">
          <Icon className="w-6 h-6" aria-hidden />
          <span className="text-[0.625rem]">Label</span>
        </button>
      ))}
    </nav>
  );
}
```

**Nav bar (back left, action right):**

```tsx
import { ChevronLeft, Plus } from "lucide-react";

<header className="sticky top-0 bg-white/90 backdrop-blur
                   pt-[env(safe-area-inset-top)] flex items-center h-11 px-2">
  <button className="h-11 w-11 grid place-items-center" aria-label="Back">
    <ChevronLeft className="w-6 h-6" />
  </button>
  <h1 className="flex-1 text-center text-base font-semibold">Title</h1>
  <button className="h-11 w-11 grid place-items-center" aria-label="Add">
    <Plus className="w-6 h-6" />
  </button>
</header>
```

- Sheet: secondary task, drag-down dismiss. Use Radix or vaul `<Drawer>`.
- Full-screen modal: self-contained flow. Explicit Cancel/Done buttons.

---

## Domain 2: SF Symbols to Lucide mapping

| SF Symbol | Lucide | SF Symbol | Lucide |
|-----------|--------|-----------|--------|
| chevron.right | `ChevronRight` | chevron.left | `ChevronLeft` |
| chevron.up | `ChevronUp` | chevron.down | `ChevronDown` |
| ellipsis | `MoreHorizontal` | plus | `Plus` |
| xmark | `X` | magnifyingglass | `Search` |
| person | `User` | person.crop.circle | `UserCircle` |
| gear / gearshape | `Settings` | bell | `Bell` |
| heart | `Heart` | star | `Star` |
| bookmark | `Bookmark` | square.and.arrow.up | `Share` |
| trash | `Trash2` | pencil | `Pencil` |
| arrow.up | `ArrowUp` | arrow.down | `ArrowDown` |
| checkmark | `Check` | info.circle | `Info` |
| exclamationmark.triangle | `AlertTriangle` | house | `Home` |
| paperplane | `Send` | camera | `Camera` |

Install: `npm install lucide-react`. Import named only.

---

## Domain 3: Dynamic Type

Use `rem` everywhere. iOS text styles → Tailwind:

| iOS style | Tailwind | iOS style | Tailwind |
|-----------|----------|-----------|----------|
| Large Title | `text-[2.125rem] font-bold` | Title 1 | `text-[1.75rem] font-bold` |
| Headline | `text-[1.0625rem] font-semibold` | Body | `text-base` |
| Subheadline | `text-[0.9375rem]` | Footnote | `text-[0.8125rem]` |
| Caption | `text-xs` | | |

```css
html { font-size: 100%; } /* respect OS root size */
@media (prefers-reduced-motion: reduce) {
  *, *::before, *::after { animation-duration: 0.01ms !important; }
}
```

Line length: cap at `max-w-[60ch]` for body copy.

---

## Domain 4: Safe Areas

Root layout once: `<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover" />`. Then on every fixed-position chrome:

```tsx
className="pt-[env(safe-area-inset-top)] pb-[env(safe-area-inset-bottom)] pl-[env(safe-area-inset-left)] pr-[env(safe-area-inset-right)]"
```

Scrollable content under fixed tab bar: `pb-[calc(env(safe-area-inset-bottom)+3.5rem)]`.

---

## Domain 5: Haptics (progressive enhancement)

```ts
type HapticPattern = "tap" | "success" | "warning" | "error";

const PATTERNS: Record<HapticPattern, number | number[]> = {
  tap: 10,
  success: [10, 40, 10],
  warning: [20, 60, 20],
  error: [40, 60, 40, 60, 40],
};

export function haptic(pattern: HapticPattern = "tap"): void {
  if (typeof navigator === "undefined") return;
  if (!("vibrate" in navigator)) return;
  navigator.vibrate(PATTERNS[pattern]);
}
```

Usage: `onClick={() => { haptic("tap"); doAction(); }}`. Action must succeed without haptic firing.

---

## Validation checklist

Before returning generated code, confirm:

- [ ] Tab bar (if present) has 3 to 5 items
- [ ] All fixed top/bottom containers use `env(safe-area-inset-*)`
- [ ] No fixed-pixel font sizes (`text-[14px]`, `font-size: 14px`)
- [ ] Touch targets `h-11 w-11` minimum
- [ ] Icons from `lucide-react`, not inline SVG
- [ ] Haptic calls are wrapped in feature detection
- [ ] `<meta viewport ... viewport-fit=cover>` documented if first install

## Sources

- https://developer.apple.com/design/human-interface-guidelines — Apple HIG canonical patterns
- https://lucide.dev/icons/ — SF Symbols → Lucide mapping
