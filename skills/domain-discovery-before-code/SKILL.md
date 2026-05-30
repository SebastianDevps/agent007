---
name: discovery-before-code
description: "Anti-convergence gate for visual work. Forces a real referent fetch + extreme style choice + state design + token declaration BEFORE any code. Default to this skill before any frontend builder task."
version: 1.0.0
when:
  keywords:
    - new component
    - new page
    - landing
    - dashboard
    - hero
    - design
    - visual
    - ui
    - rebrand
    - redesign
    - frontend build
allowed-tools:
  - WebFetch
  - WebSearch
  - Read
  - Write
  - Glob
  - Grep
  - Bash(mkdir -p .claude/state)
---

# discovery-before-code

**Hard rule**: no `<div>` before this skill returns OK. No exceptions.

This skill exists because the LLM default — without discovery — is convergence to *purple-to-blue gradient + Inter + cards-in-cards + pulsing animations*. Discovery is the only known antidote.

---

## When to invoke

- BEFORE any visual implementation task
- BEFORE the BUILDER mode of `frontend-ux-expert`
- BEFORE building a new component, page, landing, dashboard, hero
- NOT for: pure refactors with no visual surface change, bug fixes that don't touch CSS

## When to skip (rare)

- User explicitly says "use the existing design system, don't invent" AND `tokens.ts` / `tailwind.config.js` exists with documented tokens
- Task is purely text/data formatting (no new visual element)

---

## The 4-step protocol (BLOCKING)

### Step 1 — Referent Fetch (MANDATORY)

Get a real URL. "Modern dashboard" is not a referent. "Linear app dashboard" is.

```
ASK USER (if not provided): "What's a real product/site whose look you want? Give me a URL."
```

Then:
```bash
WebFetch <url>  → distill via web-distill hook
```

If user can't or won't give a URL, STOP and ask. Do not invent.

Document in the design log:
```
REFERENT: <url>
WHAT WE TAKE FROM IT: <e.g. typography hierarchy, color discipline, spacing>
WHAT WE DON'T TAKE: <e.g. their over-saturated palette, their hero animation>
```

### Step 2 — Style Choice (anti-convergence)

Pick exactly ONE of these 11 extreme styles. Generic "modern clean" is BANNED.

| # | Style | Vibe |
|---|---|---|
| 1 | Brutalist | raw HTML feel, monospace, hard borders, no shadows |
| 2 | Retro-futuristic | 80s/90s sci-fi, neon, scan lines, cyber motifs |
| 3 | Art Deco | symmetric, gold accents, geometric patterns |
| 4 | Editorial | magazine layout, large serif, generous white space |
| 5 | Swiss / International | grid-based, sans-serif, mathematical alignment |
| 6 | Memphis | playful shapes, primary colors, asymmetry |
| 7 | Cyberpunk | dark, neon highlights, glitch, data-rich |
| 8 | Minimalist Japanese | restraint, asymmetric balance, intentional negative space |
| 9 | Y2K | chrome, gradients (allowed in this style only), bubble shapes |
| 10 | Bauhaus | primary colors, geometric forms, sans-serif |
| 11 | Hand-drawn / Sketchy | imperfect lines, marker textures, casual |

```
ASK USER if not specified. Show all 11. Pick ONE. Write it down.

CHOSEN STYLE: <number + name>
```

### Step 3 — State Design (every UX state, before code)

Every interactive surface has these states. Design ALL before implementing ANY.

| State | What to design |
|---|---|
| empty | First-visit, no data yet — what does the user see and do? |
| loading | Skeleton screens (NOT spinner-only) |
| error | Specific message + recovery action — never "Something went wrong" |
| success | The happy path |
| edge cases | Long names, missing fields, slow network, offline, no JS |

Output a table:

```
| Component  | empty           | loading      | error                  | success           |
|------------|-----------------|--------------|------------------------|-------------------|
| UserList   | "Add your first | skeleton 5×  | "Couldn't load users.  | grid of cards     |
|            | user" CTA       | rows         | Retry" + button        |                   |
```

### Step 4 — Token Declaration

Output a complete token sketch BEFORE writing the first component:

```
COLORS (max 5):
- primary:    #....  (used for: CTAs, active states)
- neutral-1:  #....  (used for: bg)
- neutral-2:  #....  (used for: borders, secondary text)
- accent:     #....  (used for: success, highlights)

TYPOGRAPHY (max 2 families):
- heading: <font> · weights: 600, 700
- body:    <font> · weights: 400, 500

SPACING SCALE: 4 · 8 · 12 · 16 · 24 · 32 · 48 · 64
RADIUS:        0 · 4 · 8 (avoid pills unless style 9 / 11)
SHADOW SCALE:  none · sm · md   (avoid more than 3 levels)
```

If `tokens.ts` already exists, READ IT and align. Don't redefine.
If it doesn't exist, invoke `Skill('domain-design-tokens-extract')` with the referent URL.

---

## Step 5 — Persist output (MANDATORY for hook gate)

Write `.claude/state/discovery-output.json` so the `frontend-discovery-gate` hook lets visual writes through. Without it, ALL `.tsx`/`.jsx`/`.css`/`.html`/`.svelte`/`.vue`/`.astro` writes are blocked. TTL: 30 min.

```bash
mkdir -p .claude/state
```

```json
{
  "timestamp": "<ISO 8601>",
  "referent": { "url": "...", "take": "...", "leave": "..." },
  "style": { "id": 7, "name": "Cyberpunk" },
  "states": [{ "component": "...", "empty": "...", "loading": "...", "error": "...", "success": "..." }],
  "tokens": {
    "colors": ["#hex1", "#hex2", "#hex3", "#hex4", "#hex5"],
    "typography": { "heading": "...", "body": "..." },
    "spacing": [4, 8, 12, 16, 24, 32, 48, 64]
  },
  "valid_for_minutes": 30
}
```

Then return the same content as a readable markdown block to the calling agent.

---

## Hard rules (non-negotiable)

- NEVER skip step 1 — no code without a fetched referent
- NEVER pick "modern clean" — that's the default convergence trap
- NEVER design only the happy path
- NEVER exceed 5 colors or 2 fonts
- NEVER let the user say "you decide the style" without offering the 11 — agency belongs to them
- NEVER cite a referent the agent didn't actually WebFetch in this session

## Anti-patterns

| Anti-pattern | Why it fails |
|---|---|
| "I'll just start coding and we'll style later" | LLM defaults converge — purple gradient + Inter every time |
| "Modern dashboard look" as referent | Not a referent — meaningless input |
| Skipping state design | UI ships broken — empty states forgotten, loading is just `<Spinner/>` |
| Picking 8+ colors "to be expressive" | Visual chaos. Restraint is the design |
| 3 font families | Hierarchy collapses. 2 is the cap |

## Why this exists

Without forced style choice, LLMs produce statistically identical "AI-looking" interfaces. The 11 extreme styles + referent fetch + token discipline is the only intervention that breaks convergence. The frontend builder agent invokes this BEFORE any visual code — non-negotiable.

## Sources

- https://github.com/anthropics/claude-code/blob/main/plugins/frontend-design/skills/frontend-design/SKILL.md — para los 11 estilos extremos y anti-convergencia
