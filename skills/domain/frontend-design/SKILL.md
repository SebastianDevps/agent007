---
name: frontend-design
description: "Diseña y construye interfaces frontend distintivas de alta calidad con pensamiento de diseño profesional. Use when user asks to 'design component', 'create interface', 'build landing page', or 'design dashboard'."
canonical-sources:
  - url: https://www.w3.org/WAI/WCAG22/quickref/
    when: "for WCAG 2.2 accessibility guidelines"
  - url: https://material.io/design
    when: "for Material Design references"
  - url: https://developer.apple.com/design/human-interface-guidelines
    when: "for Apple Human Interface Guidelines"
version: 1.0.0
invokable: true
accepts_args: true
allowed-tools: ["Read", "Write", "Edit", "Bash"]
references:
  - references/process.md
  - references/color.md
  - references/typography.md
  - references/spacing.md
  - references/layout.md
  - references/motion.md
  - references/components.md
  - references/examples.md
  - references/resources.md
  - references/checklist.md
  - references/common-errors.md
---

# Frontend Design Skill

Crea interfaces frontend **distintivas y de alta calidad** con pensamiento de diseño profesional. Construye componentes, páginas y aplicaciones web que destaquen visualmente sin caer en patrones genéricos de IA, manteniendo excelente usabilidad.

## When to invoke

- "diseña un componente / design component"
- "crea una landing page / build landing page"
- "diseña un dashboard / design dashboard"
- "interfaz para X / interface for X"
- "rediseña / redesign"
- Cualquier petición de UI/UX en React, Next.js, Vue, Tailwind, shadcn/ui

NO invocar para: lógica de negocio pura, backend, infra, DB schemas. Esos van a sus respectivos expertos.

## Anti-patterns explícitos (NUNCA)

Diseños genéricos y reconocibles como IA. Si caés en alguno, REDISEÑÁ:

- **NUNCA** usar gradiente `from-purple-500 to-blue-500` (o purple-to-pink) — el gradiente AI por default. Buscá una paleta acorde a la marca.
- **NUNCA** anidar cards dentro de cards (cards-en-cards). Una card es un contenedor de contenido, no de otras cards.
- **NUNCA** usar Inter como fuente por default sin justificación. Considerá Geist, Manrope, IBM Plex, o un serif si la marca lo pide.
- **NUNCA** poner Space Grotesk en cada generación nueva — es el "Inter del 2024", igual de genérico.
- **NUNCA** colores primarios vibrantes sin contexto (`bg-red-500 text-blue-500 border-green-500`).
- **NUNCA** mezclar más de 2 familias de fuentes — caos tipográfico.
- **NUNCA** layouts no responsive (`grid-cols-4` fijo se rompe en mobile).
- **NUNCA** `transition-all` — anima todas las propiedades, es pesado y visualmente ruidoso.
- **NUNCA** anchos fijos (`w-[1200px]`) en lugar de `max-w-*`.
- **NUNCA** all caps en párrafos largos.
- **NUNCA** ignorar `prefers-reduced-motion`.
- **NUNCA** `animate-bounce` / `animate-spin` / `animate-pulse` infinitos en elementos no-loading.
- **NUNCA** entregar sin verificar contraste WCAG AA mínimo (4.5:1 texto normal).
- **NUNCA** generar código sin antes preguntar contexto (audiencia, marca, stack, referencias).

## Need → Reference

| Necesito... | Referencia |
|---|---|
| Proceso de design thinking, preguntas de discovery | `references/process.md` |
| Sistema de colores, dark mode, contraste, paletas | `references/color.md` |
| Escala tipográfica, font pairing, responsive type | `references/typography.md` |
| Sistema de espaciado 8px, white space, agrupación | `references/spacing.md` |
| Grids, containers, flexbox, sticky/fixed positioning | `references/layout.md` |
| Animaciones, micro-interacciones, page transitions, parallax | `references/motion.md` |
| Hero, feature cards, dashboard, forms (snippets completos) | `references/components.md` |
| Casos de uso completos (landing, dashboard, multi-step form, modal) | `references/examples.md` |
| Herramientas, design systems, fuentes de inspiración, a11y | `references/resources.md` |
| Checklist pre-entrega, mensajes al usuario | `references/checklist.md` |
| Patrones de diseño AI-genéricos a evitar, mindset final | `references/common-errors.md` |

## Workflow

1. **Discovery** — Antes de codear, preguntá contexto: tipo de producto, audiencia target, marca/colores, stack técnico, referencias visuales. Cargá `references/process.md` para el guion completo de preguntas.
2. **Search references** — Identificá qué pilares aplican (color, typography, spacing, layout, motion) y qué componente del catálogo (hero, cards, dashboard, form). Leé las referencias relevantes ANTES de generar código.
3. **Verify anti-patterns** — Releé la lista de NUNCAs de arriba. Si tu primera idea cae en alguno, descartala y rediseñá.
4. **Implement** — Aplicá los 5 pilares con el sistema (escalas consistentes, no valores mágicos). Componé desde los snippets de `references/components.md`, no copies-pegues sin adaptar.
5. **Quality gate** — Antes de entregar, corré el checklist de `references/checklist.md` (Visual / Responsive / Performance / A11y / UX / Code).
6. **Iterate** — Mostrá, recibí feedback, refiná. La primera versión casi nunca es la final.

## Filosofía

Calidad sobre velocidad · Creatividad distintiva sobre patrones AI · Contexto antes que código · Sistema antes que improvisación · Usuario al centro siempre.
