---
name: design-system-doc
description: "Generate canonical DESIGN.md (9-section schema) for the project. Drives consistency across components and onboarding."
version: 1.0.0
when:
  keywords: [design system, design.md, style guide, brand doc, design tokens doc]
allowed-tools:
  - Read
  - Write
  - Glob
  - Grep
---

# design-system-doc

Generates a canonical `DESIGN.md` at the project root using the 9-section schema from VoltAgent/awesome-design-md. The doc is the single source of truth for visual decisions — agents read it before building UI.

## Hard Rules

- ALWAYS write `DESIGN.md` at the project root. Never nest it inside `src/` or `docs/`.
- ALWAYS include all 9 sections, in the exact order below. Empty sections are forbidden — if data is missing, mark `TBD` with a concrete question for the user.
- NEVER invent hex values. Extract them from `tokens.ts` / `tailwind.config.js` / `theme.css`. If none exist, run Skill('domain-design-tokens-extract') first.
- NEVER write more than 2 font families. If the project has 3+, ask the user which 2 to keep.
- NEVER skip the Guardrails section — a DESIGN.md without explicit `NEVER` rules is a wishlist, not a contract.

## Anti-Patterns

- Generating prose without numbers — "warm tones" instead of `#F4A261`.
- Listing components without their props/variants API.
- Omitting breakpoints or using `sm/md/lg` without pixel values.
- Copy-pasting Material/Tailwind defaults without project-specific decisions.
- Writing Agent Prompts in vague terms — they must be runnable verbatim.

## Workflow

1. **Discover sources** (parallel Glob): `tokens.{ts,js,json}`, `tailwind.config.{ts,js,cjs}`, `theme.css`, `**/*.tokens.*`, plus existing `DESIGN.md` (read first to preserve curated content).
2. **Decision branch**:
   - Sources exist → Read them and extract palette / typography / spacing / shadows.
   - No sources → invoke Skill('domain-design-tokens-extract') and pause until tokens exist.
3. **Reference URL** (optional): if the user supplied an inspiration URL, cite it verbatim in section 1 — never paraphrase the brand.
4. **Render** the template below, replacing `{{...}}` placeholders with extracted values.
5. **Write** `DESIGN.md` at project root. If the file exists, diff and ask before overwriting curated prose in sections 1, 7, 9.

## Template (the file this skill produces)

```markdown
# DESIGN.md — {{ProjectName}}

> Canonical visual contract. Agents read this before generating UI.
> Schema: VoltAgent/awesome-design-md (9-section).

## 1. Atmosphere & Mood

{{1-3 paragraphs: temperature, energy, references. Cite inspiration URL verbatim if provided.}}

Reference: {{url-or-none}}

## 2. Color Palettes

| Token | Hex | Usage |
|---|---|---|
| `--color-bg` | `{{#0A0A0B}}` | Page background |
| `--color-surface` | `{{#141416}}` | Cards, modals |
| `--color-text-primary` | `{{#F5F5F7}}` | Body copy |
| `--color-text-muted` | `{{#8E8E93}}` | Captions, hints |
| `--color-accent` | `{{#5E5CE6}}` | Primary actions |
| `--color-danger` | `{{#FF453A}}` | Destructive |
| `--color-success` | `{{#30D158}}` | Confirmations |

State variants (`-hover`, `-active`, `-disabled`) MUST be derived, never re-picked by hand.

## 3. Typography

- **Display**: `{{Inter}}`, weights `{{600, 700}}`
- **Body**: `{{Inter}}`, weights `{{400, 500}}`

Scale (rem): `text-xs 0.75 / text-sm 0.875 / text-base 1.0 / text-lg 1.125 / text-xl 1.5 / text-2xl 2.0 / text-3xl 3.0`.

## 4. Components

For each component: name, props, variants, states.

### Button
- Props: `variant: 'primary' | 'secondary' | 'ghost'`, `size: 'sm' | 'md' | 'lg'`, `disabled`, `loading`
- States: default, hover, active, focus-visible, disabled, loading

### Input
- Props: `type`, `error?`, `hint?`, `prefix?`, `suffix?`
- States: default, focus, error, disabled

### Card
- Props: `elevation: 0 | 1 | 2`, `interactive?`
- States: default, hover (only if `interactive`)

{{Add project components — never list components that don't exist in code.}}

## 5. Layout

- Grid: 12 columns, gutter `24px`, max content width `1280px`
- Container padding: `16px` (mobile) → `32px` (≥768) → `48px` (≥1280)
- Spacing scale: `4, 8, 12, 16, 24, 32, 48, 64, 96` (px)

Breakpoints (mobile-first):
| Token | Min width | Target |
|---|---|---|
| `sm` | 640px | Large phones |
| `md` | 768px | Tablets |
| `lg` | 1024px | Laptops |
| `xl` | 1280px | Desktops |
| `2xl` | 1536px | Wide |

## 6. Depth & Elevation

| Level | Shadow | Use |
|---|---|---|
| 0 | none | Inline content |
| 1 | `0 1px 2px rgba(0,0,0,.08)` | Cards at rest |
| 2 | `0 4px 12px rgba(0,0,0,.12)` | Hover cards, dropdowns |
| 3 | `0 12px 32px rgba(0,0,0,.18)` | Modals, popovers |

Z-index scale: `dropdown 1000`, `sticky 1100`, `modal-backdrop 1200`, `modal 1300`, `toast 1400`, `tooltip 1500`.

## 7. Guardrails (NEVER rules)

- NEVER use raw hex values in components — only `--color-*` tokens.
- NEVER introduce a 3rd font family.
- NEVER nest more than 2 elevation levels in the same surface.
- NEVER ship a component without all 5 states (default, hover, active, focus-visible, disabled).
- NEVER use `localStorage` for theme — use `prefers-color-scheme` + cookie.
- {{Add project-specific NEVERs — these are the most valuable lines in this doc.}}

## 8. Responsive

Mobile-first. Every component MUST render correctly at 360px width before any `sm:` modifier is added.

Order of declaration in code: base (mobile) first, then ascending `@media (min-width: …)` queries.

Touch targets: minimum `44x44px` on `<lg`.

## 9. Agent Prompts

Copy-pasteable prompts to regenerate components consistent with this doc.

### Regenerate Button
> Build a `<Button>` component using tokens from DESIGN.md §2-3. Variants: `primary | secondary | ghost`. Sizes: `sm | md | lg`. All 5 states. Named export. No raw hex. Test with React Testing Library: render each variant, assert role + accessible name.

### Regenerate Card
> Build a `<Card>` component using elevation tokens from DESIGN.md §6. Props: `elevation`, `interactive`. If `interactive`, add hover state at elevation+1. No raw shadow values.

### Regenerate Page Layout
> Build a page using grid + breakpoints from DESIGN.md §5. Mobile-first. Container max-width 1280px. Test at 360, 768, 1280 widths.
```

## Verification

- File exists at project root: `DESIGN.md`
- All 9 section headers present (Grep `^## [1-9]\.`)
- No `{{...}}` placeholder remains
- At least 3 hex values in section 2
- At least 1 NEVER rule in section 7

## Sources

- https://github.com/VoltAgent/awesome-design-md — schema de 9 secciones
