---
name: ux-research
description: "User flows, wireframes, personas, usability analysis. Para diseño de experiencia de usuario."
invokable: true
accepts_args: true
auto-activate: false
version: 1.0.0
when:
  - task_type: design
    risk_level: [medium, high, critical]
  - user_mentions: ["wireframe", "user flow", "prototype", "ux", "user experience", "design"]
---

# UX Research - User-Centered Design Process

**Propósito**: Diseñar experiencias de usuario basadas en investigación, no en suposiciones. Crear flujos, wireframes y especificaciones antes de codear.

---

## Proceso de UX Research

### Fase 1: User Understanding

```markdown
**Q1: ¿Quién es el usuario?**
Definir persona:
  - Nombre ficticio y rol
  - Nivel técnico (novato, intermedio, experto)
  - Goals principales al usar el producto
  - Frustraciones actuales
  - Contexto de uso (dispositivo, ubicación, momento)

[Wait for answer]

**Q2: ¿Cuál es el job-to-be-done?**
"Cuando [situación], quiero [motivación], para poder [resultado esperado]"

Ejemplo: "Cuando recibo un pedido nuevo, quiero ver todos los detalles rápidamente,
para poder confirmar el envío en menos de 30 segundos"

[Wait for answer]
```

---

### Fase 2: Flow Mapping

```markdown
## User Flow: [Nombre del flujo]

### Entry Points
¿Cómo llega el usuario a este flujo?
  - [ ] Navegación directa (sidebar, menu)
  - [ ] Deep link (notificación, email)
  - [ ] Search result
  - [ ] Redirect from another flow

### Happy Path
```
[Start] → [Step 1] → [Step 2] → [Step 3] → [Success]
```

### Decision Points
```
[Step 2] →  Yes → [Step 3a]
            No  → [Step 3b] → [Alternative path]
```

### Error Paths
```
[Step 2] → Error: [tipo] → [Error screen] → [Recovery action]
```

### Exit Points
¿Cómo sale el usuario?
  - [ ] Completó el flujo (success)
  - [ ] Canceló (¿guardar borrador?)
  - [ ] Navegó a otro lugar (¿perder progreso?)
  - [ ] Timeout/session expiry
```

---

### Fase 3: Screen Specifications

Para cada pantalla del flujo:

```markdown
## Screen: [Nombre de pantalla]

### Purpose
[Qué logra el usuario en esta pantalla]

### Layout (ASCII Wireframe)
```
┌─────────────────────────────────┐
│ [Logo]        [Search]  [Avatar]│ ← Header
├─────────┬───────────────────────┤
│         │                       │
│ Nav     │  Page Title           │
│ ├ Item1 │  ┌──────────────────┐ │
│ ├ Item2 │  │  Card Content    │ │
│ ├ Item3 │  │  [Data Table]    │ │
│ └ Item4 │  │                  │ │
│         │  └──────────────────┘ │
│         │                       │
│         │  [Primary Action]     │
│         │  [Secondary Action]   │
├─────────┴───────────────────────┤
│ Footer                          │
└─────────────────────────────────┘
```

### Elements
| Element | Type | Behavior | Notes |
|---------|------|----------|-------|
| Search | Input | Autosuggest, debounce 300ms | Show recent searches |
| Data Table | Table | Sortable, paginated | 10 rows default |
| Primary Action | Button | Submit form | Disabled until valid |

### States
- **Loading**: Skeleton screens for card + table
- **Empty**: Illustration + "No items yet" + CTA
- **Error**: Inline error message + retry button
- **Success**: Toast notification (auto-dismiss 5s)

### Responsive Behavior
- **Desktop (>1024px)**: Sidebar visible, table layout
- **Tablet (768-1024px)**: Sidebar collapsible, table scrollable
- **Mobile (<768px)**: Bottom nav, card layout instead of table
```

---

### Fase 4: Interaction Specifications

```markdown
## Interactions: [Nombre del flujo]

### Micro-interactions
| Trigger | Animation | Duration | Easing |
|---------|-----------|----------|--------|
| Button click | Scale down 0.95 | 100ms | ease-out |
| Page transition | Slide left | 200ms | ease-in-out |
| Toast appear | Slide up + fade | 300ms | ease-out |
| Modal open | Scale up + overlay | 200ms | ease-out |
| Delete item | Fade out + collapse | 300ms | ease-in |

### Feedback Patterns
| Action | Feedback | When |
|--------|----------|------|
| Save | "Saved" toast (green) | Immediate after save |
| Delete | Confirmation modal | Before delete |
| Error | Inline red message | On field blur or submit |
| Loading | Skeleton → content | On data fetch |
| Empty | Illustration + help | When no data |

### Keyboard Shortcuts (if applicable)
| Shortcut | Action |
|----------|--------|
| Ctrl+S | Save |
| Ctrl+K | Open search |
| Escape | Close modal |
| Tab | Next field |
```

---

### Fase 5: Accessibility Specifications

```markdown
## Accessibility: [Nombre del flujo]

### ARIA Roles
| Element | Role | aria-label | Notes |
|---------|------|-----------|-------|
| Sidebar | navigation | "Main navigation" | |
| Search | search | "Search items" | |
| Data table | table | "Items list" | Include caption |
| Modal | dialog | "Confirm deletion" | Focus trap |

### Focus Management
1. Page load → Focus on main heading (h1)
2. Modal open → Focus on first interactive element
3. Modal close → Focus returns to trigger button
4. Tab order: Header → Sidebar → Main content → Footer

### Screen Reader Announcements
| Event | Announcement |
|-------|-------------|
| Item saved | "Item saved successfully" (aria-live: polite) |
| Error | "Error: [message]" (aria-live: assertive) |
| Loading | "Loading items..." (aria-live: polite) |
| Items loaded | "[N] items loaded" (aria-live: polite) |

### Color Contrast
- Text on background: minimum 4.5:1
- Large text (>18px): minimum 3:1
- UI components: minimum 3:1
- Focus indicators: minimum 3:1
```

---

## Output: UX Spec Document

```markdown
# UX Specification: [Feature Name]

**Date**: [fecha]
**Status**: UX Spec Complete → Ready for Implementation

## User Persona
[Descripción del usuario target]

## User Flow
[Diagrama del flujo completo]

## Screen Specifications
[Para cada pantalla: layout, elements, states]

## Interaction Design
[Animaciones, feedback, keyboard shortcuts]

## Accessibility Requirements
[ARIA, focus, screen readers, contrast]

## Design Tokens
[Colores, tipografía, spacing usados]

## Edge Cases
| Case | Handling |
|------|---------|
| [Case 1] | [Cómo se maneja] |

## Open Questions
- [ ] [Pregunta de diseño pendiente]

---
**Next Step**: → frontend-design (visual implementation) o → brainstorming (technical approach)
```

---

## Checklist: UX Spec Completa

- [ ] **User persona** definida con contexto
- [ ] **User flow** completo (happy + error + edge paths)
- [ ] **Wireframes** para cada pantalla clave
- [ ] **States** definidos (loading, empty, error, success)
- [ ] **Responsive** behavior especificado
- [ ] **Interactions** documentadas (animations, feedback)
- [ ] **Accessibility** requirements definidos
- [ ] **Edge cases** cubiertos
