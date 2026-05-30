---
name: shadcn-component-install
description: "Install shadcn/ui components via CLI with mandatory dry-run preview before write. Workflow: info → search → docs → diff → install."
version: 1.0.0
when:
  keywords: [shadcn, ui component, button, dialog, accordion, card, install component, shadcn-ui, radix, registry]
allowed-tools:
  - Bash(npx shadcn@latest *)
  - Bash(pnpm dlx shadcn@latest *)
  - Bash(bunx shadcn@latest *)
  - Read
  - Grep
  - Glob
---

# shadcn-component-install — CLI-First Component Installation

## Agent directive

Whenever the user asks to "add a button", "install a dialog", "scaffold an accordion" or any shadcn/ui component — **DO NOT copy code from documentation into the project manually**. Always use the shadcn CLI. The CLI resolves dependencies, applies registry config (style, baseColor, aliases), wires `cn()` and Tailwind tokens, and keeps components upgradeable.

If `components.json` is missing, run `init` first.

---

## Hard rules

- NEVER paste component source from `ui.shadcn.com` directly into the project.
- NEVER skip the `--dry-run` step on a project that already has components installed (collisions silently overwrite files otherwise).
- NEVER pin to an old shadcn version unless the user explicitly asks — always use `shadcn@latest`.
- ALWAYS detect the package manager before invoking (`pnpm-lock.yaml` → `pnpm dlx`; `bun.lockb` → `bunx`; default → `npx`).
- ALWAYS read the existing `components.json` before installing, so style/baseColor/aliases match.

---

## Workflow (5 steps, all executable)

### Step 1 — `info`: confirm project is shadcn-ready

```bash
npx shadcn@latest info
```

Reads `components.json`, prints framework, style, baseColor, iconLibrary, and resolved aliases. If the command fails with "components.json not found", run:

```bash
npx shadcn@latest init
```

and stop to confirm style + baseColor with the user before proceeding.

### Step 2 — `search`: find the exact component slug

```bash
npx shadcn@latest search <query>
```

Example:

```bash
npx shadcn@latest search dialog
npx shadcn@latest search "data table"
```

Use the slug from the output (e.g. `dialog`, `data-table`) for the next steps. If the search returns multiple registries (e.g. `@shadcn/dialog`, `@magicui/dialog`), ask the user which one they want — do NOT guess.

### Step 3 — `view`: read component docs and dependencies

```bash
npx shadcn@latest view <slug>
```

Example:

```bash
npx shadcn@latest view dialog
```

This prints the component's files, registryDependencies (other shadcn components it pulls in), and npm dependencies. Surface this to the user before writing — especially the npm deps, since they affect lockfile and bundle size.

### Step 4 — `--dry-run`: preview the diff

```bash
npx shadcn@latest add <slug> --dry-run
```

Example:

```bash
npx shadcn@latest add dialog --dry-run
```

The CLI lists every file it would create or overwrite. If any line says `OVERWRITE`, STOP and ask the user — do not proceed unless they say "yes, overwrite".

For multiple components in one go:

```bash
npx shadcn@latest add dialog button label --dry-run
```

### Step 5 — Install

Only after the dry-run is reviewed:

```bash
npx shadcn@latest add <slug>
```

If overwrites were approved, append `--overwrite`. If the user wants a specific path override, append `--path src/components/ui`.

After install, run the project's typecheck (e.g. `pnpm tsc --noEmit`) to confirm imports resolve. Do NOT skip this — registry mismatches surface as TS errors first.

---

## Package manager detection

```bash
test -f pnpm-lock.yaml && echo "pnpm dlx shadcn@latest"
test -f bun.lockb && echo "bunx shadcn@latest"
test -f yarn.lock && echo "yarn dlx shadcn@latest"
# default
echo "npx shadcn@latest"
```

Use the detected runner consistently across all 5 steps. Mixing runners triggers cache misses and slower installs.

---

## Anti-patterns (refuse these)

| Anti-pattern | Why it breaks | Correct replacement |
|---|---|---|
| Copy `<Dialog>` source from ui.shadcn.com into `src/components/ui/dialog.tsx` | Skips registryDependencies, breaks future `diff` upgrades, hardcodes wrong cn alias | `npx shadcn@latest add dialog` |
| `npx shadcn add dialog` (no `--dry-run` first) | Silent overwrite of customized components | Run dry-run, review, then add |
| `npm install @radix-ui/react-dialog` then write your own wrapper | Misses Tailwind tokens, animation classes, a11y wiring | Use the registry component as base, customize after |
| Using `shadcn-ui@0.x` (deprecated) | Old CLI with broken registry resolution | `shadcn@latest` (no `-ui` suffix) |
| Pasting from a chat answer that includes the source | Same as #1, plus stale snapshots | Always `add` from CLI |

---

## Reference: common slugs

`button` · `dialog` · `dropdown-menu` · `form` · `input` · `label` · `select` · `sheet` · `table` · `tabs` · `toast` · `tooltip` · `accordion` · `alert` · `alert-dialog` · `avatar` · `badge` · `calendar` · `card` · `checkbox` · `command` · `data-table` · `date-picker` · `popover` · `progress` · `radio-group` · `scroll-area` · `separator` · `skeleton` · `slider` · `switch` · `textarea` · `toggle`

When unsure, run `search` (Step 2) — never guess slugs.

## Sources

- https://ui.shadcn.com/docs/components — component reference and props
- https://ui.shadcn.com/docs/cli — CLI flags and registry config
