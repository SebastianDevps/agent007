---
name: a11y-contrast-check
description: "Statically check WCAG 2.2 AA color contrast in TS/TSX/CSS files. Detects Tailwind text/bg pairs and CSS color/background rules, fails build if ratio < 4.5:1 (normal) or < 3:1 (large)."
invokable: true
version: 1.0.0
when:
  keywords: [contrast, wcag, accessibility, a11y, color contrast, contrast ratio, color blind, low vision, design audit]
canonical-sources:
  - url: https://www.w3.org/WAI/WCAG22/quickref/
    when: "for WCAG 2.2 success criteria"
  - url: https://www.w3.org/TR/WCAG22/#contrast-minimum
    when: "for the exact contrast ratio formula"
allowed-tools:
  - Bash(node .claude/skills/domain/a11y-contrast-check/scripts/check-contrast.js *)
  - Read
  - Grep
  - Glob
---

# a11y-contrast-check — WCAG AA Contrast Auditor

## Agent directive

When the user asks to "audit colors", "check contrast", "review a11y", or modifies a file with Tailwind color classes (`text-*` + `bg-*`) or CSS `color`/`background` rules, run the contrast checker BEFORE claiming the change is done. Contrast bugs are invisible during normal use and impossible to detect by reading code visually — automate the check.

The script is dependency-free Node.js (stdlib only). It runs in any project that has `node` available.

---

## Hard rules

- ALWAYS run the script on changed files before saying a UI change is "done".
- NEVER claim "WCAG AA compliant" without running the script — visual inspection is unreliable.
- A FAIL (ratio < 4.5:1) blocks the change. Either fix the colors or document an explicit exemption (e.g. disabled state, decorative element).
- A WARN ("large only") is acceptable only for text ≥ 18pt regular or ≥ 14pt bold. Confirm with the user.
- Do NOT modify the script's thresholds to make tests pass — fix the colors instead.

---

## Workflow

### Step 1 — Identify changed files

Run on the specific files you just modified:

```bash
node .claude/skills/domain/a11y-contrast-check/scripts/check-contrast.js \
  src/components/Button.tsx src/styles/theme.css
```

### Step 2 — Read the report

Each line shows:

```
- <file> [<source>] <fg> on <bg> → <ratio>:1 PASS|WARN|FAIL
    ↳ <context snippet>
```

`source` is `tailwind` (class strings), `css` (rule blocks), or `css-vars` (`:root --foreground` / `--background`).

Exit code 0 = all pass. Exit code 1 = at least one FAIL — change must be fixed.

### Step 3 — Resolve violations

For each FAIL:
1. Show the user the offending pair and ratio.
2. Propose darker/lighter alternatives that hit ≥ 4.5:1 (e.g. `text-gray-400` → `text-gray-600`).
3. Apply the change ONLY after the user confirms — color changes are visual decisions, not mechanical fixes.

### Step 4 — Re-run

After the fix, re-run the script. Do not stop until exit code 0 or all WARNs are documented.

---

## What it detects

| Source | Pattern | Example |
|---|---|---|
| Tailwind | `class`/`className`/`clsx`/`cn` blocks containing both `text-*` and `bg-*` | `<div className="text-gray-400 bg-gray-300">` |
| CSS rules | `{ ... }` blocks containing both `color:` and `background[-color]:` | `.btn { color: #777; background: #888; }` |
| CSS vars | `:root` containing both `--foreground` and `--background` | `:root { --foreground: #333; --background: #f0f0f0; }` |

Supports color formats: hex (`#rgb`, `#rrggbb`), `rgb()`/`rgba()`, and Tailwind palette names (`slate-50` … `rose-600`, `white`, `black`).

Pairs with unresolvable colors (e.g. CSS variable references like `var(--unknown)`) are reported as SKIP — investigate manually.

---

## What it does NOT detect (yet)

- Pairs split across separate elements (e.g. `<span>` foreground over a parent's background)
- Dynamic colors set via runtime style props
- Image-based backgrounds
- Hover/focus state contrasts (only the static class set is parsed)

For those cases, complement with browser DevTools or axe-core in E2E tests.

---

## Anti-patterns

| Anti-pattern | Why it breaks | Correct replacement |
|---|---|---|
| "Looks fine to me" without running the script | Eyes adapt — gray-on-gray often fails AA at 2:1 while looking readable | Run the script |
| Lowering threshold in the script to silence FAIL | Hides real a11y bugs from users | Change the colors |
| Adding `// a11y-ignore` comments | The script doesn't honor them by design | Fix or document the exemption in design tokens |
| Running only on theme files | Most violations live in component class strings | Run on changed `.tsx` files too |

---

## Quick reference: WCAG 2.2 thresholds

- **AA normal text** — 4.5:1 (body text < 18pt regular / < 14pt bold)
- **AA large text** — 3:1 (≥ 18pt regular OR ≥ 14pt bold)
- **AA non-text UI** — 3:1 (icons, focus rings, form borders) — same threshold as large text
- **AAA normal** — 7:1, **AAA large** — 4.5:1 (this script targets AA, not AAA)
