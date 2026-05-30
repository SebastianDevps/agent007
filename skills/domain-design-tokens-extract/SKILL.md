---
name: design-tokens-extract
description: "Fetch a reference URL, extract its design tokens (colors, fonts, spacing, radii, shadows), and emit a W3C-format tokens file. Replaces vibes-based copying with a structured, auditable extraction."
version: 1.0.0
when:
  keywords: [design tokens, extract tokens, palette extraction, copy design, inspiration site, reference style, design system bootstrap, tokens.css, tokens.ts, w3c tokens]
allowed-tools:
  - WebFetch
  - Write
  - Read
  - Bash(node *)
---

# design-tokens-extract — Reference URL → W3C Tokens

## Agent directive

When the user says "I want a site that looks like X", "extract tokens from this URL", "use this as inspiration", or pastes a reference link, do NOT eyeball colors and guess. Run this skill: fetch the page, extract a bounded set of tokens, write them to a file, and report what was kept vs discarded.

The output is a **starting point** — not a final design system. The user must review and iterate.

---

## Hard rules

- NEVER extract more than the documented limits (5 colors, 2 fonts, 6 spacing steps, 4 radii, 4 shadows). More tokens = noise, not signal.
- NEVER claim the tokens reproduce the reference site exactly. Browser-rendered CSS depends on JS, fonts loaded async, and computed cascades you cannot see from raw HTML.
- ALWAYS write a discard report alongside the tokens file — the user must see what was filtered out and why.
- ALWAYS ask the user where to write the output BEFORE calling Write — typical paths are `src/styles/tokens.css`, `src/design/tokens.ts`, or `tokens.json`.
- NEVER copy proprietary brand assets (logos, photographs, full stylesheets). This skill targets numerical tokens only — colors, sizes, shadows.

---

## Workflow

### Step 1 — Fetch the reference URL

```
WebFetch(url, prompt: "Return the raw HTML and all inlined or linked <style> contents. Include CSS custom properties from :root. Do not summarize.")
```

If the page is heavily JS-rendered (SPA shell only), warn the user — extraction will be poor and they should provide a stylesheet URL or screenshot-driven alternative.

### Step 2 — Extract candidates

Parse the returned HTML+CSS for:

| Token type | Pattern to scan | Limit |
|---|---|---|
| **color** | `#rrggbb`, `rgb()`, `hsl()`, `oklch()`, CSS vars `--color-*` / `--*-color`, `color:`, `background[-color]:` | top 5 by frequency |
| **fontFamily** | `font-family:` declarations, `@import url(...fonts.googleapis...)` | top 2 |
| **spacing** | `margin`, `padding`, `gap` numeric values (px/rem) | unique values, top 6 sorted ascending |
| **borderRadius** | `border-radius:` values | unique, top 4 |
| **shadow** | `box-shadow:` values (full string) | unique, top 4 |

Frequency = number of occurrences in the fetched stylesheet text. Discard `0`, `0px`, `none`, `inherit`, `initial`, `transparent`, `currentColor`.

### Step 3 — Normalize

- Colors → lowercase 6-digit hex (convert rgb/hsl when trivial; keep oklch as-is and flag).
- Spacing → convert px to rem (assuming 16px base) when value is divisible by 4. Otherwise keep px.
- Fonts → strip quotes and trailing fallbacks; keep the primary family.
- Shadows → keep as a single string token.

### Step 4 — Emit tokens file

Two output formats — pick based on the user's stack (ask if unclear):

**`tokens.css`** (CSS custom properties on `:root`):

```css
:root {
  /* extracted from <url> on <date> */
  --color-1: #0f172a;
  --color-2: #f8fafc;
  --color-3: #2563eb;
  --color-4: #94a3b8;
  --color-5: #ef4444;

  --font-sans: "Inter", system-ui, sans-serif;
  --font-display: "Fraunces", Georgia, serif;

  --space-1: 0.25rem;
  --space-2: 0.5rem;
  --space-3: 1rem;
  --space-4: 1.5rem;
  --space-5: 2rem;
  --space-6: 4rem;

  --radius-sm: 0.25rem;
  --radius-md: 0.5rem;
  --radius-lg: 1rem;
  --radius-full: 9999px;

  --shadow-sm: 0 1px 2px 0 rgb(0 0 0 / 0.05);
  --shadow-md: 0 4px 6px -1px rgb(0 0 0 / 0.1);
  --shadow-lg: 0 10px 15px -3px rgb(0 0 0 / 0.1);
  --shadow-xl: 0 20px 25px -5px rgb(0 0 0 / 0.1);
}
```

**`tokens.json`** (W3C Design Tokens Format):

```json
{
  "$description": "Extracted from <url> on <date>",
  "color": {
    "1": { "$type": "color", "$value": "#0f172a" },
    "2": { "$type": "color", "$value": "#f8fafc" }
  },
  "spacing": {
    "1": { "$type": "dimension", "$value": "0.25rem" }
  },
  "fontFamily": {
    "sans": { "$type": "fontFamily", "$value": ["Inter", "system-ui", "sans-serif"] }
  }
}
```

`$type` and `$value` keys are mandatory per the W3C spec — do not omit them.

### Step 5 — Write the discard report

Alongside the tokens file, append a comment block (CSS) or sibling `tokens.report.md` (JSON) listing:

- **Source URL** + fetch timestamp
- **Kept**: each token with its raw source value
- **Discarded**: tokens beyond the limit, with the reason (`exceeded limit`, `non-numeric`, `decorative-only`)
- **Warnings**: e.g. "page is JS-rendered, only shell CSS captured", "oklch() colors preserved as-is"

The user uses this report to decide what to bring back manually.

---

## Anti-patterns

| Anti-pattern | Why it breaks | Correct replacement |
|---|---|---|
| Extracting 30+ colors "to be safe" | Every extra token dilutes the system; tokens become a dump, not a contract | Hard cap at 5 — let the user add more deliberately |
| Copying the reference stylesheet wholesale | Pulls in vendor reset, framework classes, brand specifics | Extract numerical tokens only |
| Skipping the discard report | User has no way to know what was filtered | Always write the report |
| Not asking where to write | Overwrites existing tokens file or pollutes repo root | Confirm path before Write |
| Claiming "pixel-perfect copy" | Impossible from HTML+CSS alone (no JS, no fonts, no images) | Frame output as a starting palette |
| Extracting from a JS-only SPA without warning | Shell page has near-zero CSS — output is meaningless | Detect and warn before extracting |

---

## Output checklist

Before reporting "done":

- [ ] Tokens file written to user-confirmed path
- [ ] Discard report written (CSS comment or `.report.md`)
- [ ] All limits respected (5/2/6/4/4)
- [ ] Source URL + timestamp recorded in the file
- [ ] User informed this is a starting point, not a final system

## Sources

- https://design-tokens.github.io/community-group/format/ — W3C design tokens schema
- https://www.w3.org/TR/css-color-4/ — color format normalization
