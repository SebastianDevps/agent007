---
name: design-system
description: "Crear y mantener design system: tokens, componentes, guidelines. Para consistencia UI."
invokable: true
accepts_args: true
auto-activate: false
version: 1.0.0
when:
  - user_mentions: ["design system", "design tokens", "component library", "ui kit", "theme"]
---

# Design System - Consistent UI Architecture

**Propósito**: Crear y mantener un sistema de diseño que garantice consistencia visual y de interacción en todo el producto.

---

## Estructura del Design System

### 1. Design Tokens (Foundations)

```typescript
// tokens/colors.ts
export const colors = {
  // Brand
  primary: {
    50: '#EEF2FF',
    100: '#E0E7FF',
    200: '#C7D2FE',
    300: '#A5B4FC',
    400: '#818CF8',
    500: '#6366F1',  // Main
    600: '#4F46E5',
    700: '#4338CA',
    800: '#3730A3',
    900: '#312E81',
  },

  // Neutral
  gray: {
    50: '#F9FAFB',
    100: '#F3F4F6',
    200: '#E5E7EB',
    300: '#D1D5DB',
    400: '#9CA3AF',
    500: '#6B7280',
    600: '#4B5563',
    700: '#374151',
    800: '#1F2937',
    900: '#111827',
  },

  // Semantic
  success: { light: '#D1FAE5', main: '#10B981', dark: '#065F46' },
  error: { light: '#FEE2E2', main: '#EF4444', dark: '#991B1B' },
  warning: { light: '#FEF3C7', main: '#F59E0B', dark: '#92400E' },
  info: { light: '#DBEAFE', main: '#3B82F6', dark: '#1E40AF' },
};

// tokens/typography.ts
export const typography = {
  fontFamily: {
    sans: "'Inter', -apple-system, BlinkMacSystemFont, sans-serif",
    mono: "'JetBrains Mono', 'Fira Code', monospace",
  },
  fontSize: {
    xs: '0.75rem',     // 12px
    sm: '0.875rem',    // 14px
    base: '1rem',      // 16px
    lg: '1.125rem',    // 18px
    xl: '1.25rem',     // 20px
    '2xl': '1.5rem',   // 24px
    '3xl': '1.875rem', // 30px
    '4xl': '2.25rem',  // 36px
  },
  fontWeight: {
    normal: 400,
    medium: 500,
    semibold: 600,
    bold: 700,
  },
  lineHeight: {
    tight: 1.25,
    normal: 1.5,
    relaxed: 1.75,
  },
};

// tokens/spacing.ts (4px grid)
export const spacing = {
  0: '0',
  1: '0.25rem',  // 4px
  2: '0.5rem',   // 8px
  3: '0.75rem',  // 12px
  4: '1rem',     // 16px
  5: '1.25rem',  // 20px
  6: '1.5rem',   // 24px
  8: '2rem',     // 32px
  10: '2.5rem',  // 40px
  12: '3rem',    // 48px
  16: '4rem',    // 64px
};

// tokens/shadows.ts
export const shadows = {
  sm: '0 1px 2px 0 rgb(0 0 0 / 0.05)',
  md: '0 4px 6px -1px rgb(0 0 0 / 0.1)',
  lg: '0 10px 15px -3px rgb(0 0 0 / 0.1)',
  xl: '0 20px 25px -5px rgb(0 0 0 / 0.1)',
};

// tokens/borders.ts
export const borders = {
  radius: {
    sm: '0.25rem',   // 4px
    md: '0.5rem',    // 8px
    lg: '0.75rem',   // 12px
    xl: '1rem',      // 16px
    full: '9999px',  // pill
  },
};
```

---

### 2. Core Components

#### Component Specification Template

Para cada componente documentar:

```markdown
## Component: Button

### Variants
| Variant | Use case |
|---------|---------|
| Primary | Main actions (1 per screen) |
| Secondary | Secondary actions |
| Tertiary | Subtle actions, links |
| Danger | Destructive actions |
| Ghost | Minimal emphasis |

### Sizes
| Size | Height | Padding | Font Size |
|------|--------|---------|-----------|
| sm | 32px | 12px 16px | 14px |
| md | 40px | 16px 24px | 14px |
| lg | 48px | 20px 32px | 16px |

### States
| State | Visual change |
|-------|--------------|
| Default | Base styles |
| Hover | Slight darken (-10% lightness) |
| Active | More darken (-20% lightness) |
| Focus | Focus ring (2px offset, primary color) |
| Disabled | 50% opacity, no pointer events |
| Loading | Spinner replacing text, disabled |

### Accessibility
- Role: button
- Keyboard: Enter/Space to activate
- Focus: Visible focus ring
- aria-disabled when disabled
- aria-busy when loading

### Code Example
```tsx
<Button variant="primary" size="md" onClick={handleSave}>
  Save Changes
</Button>

<Button variant="danger" size="sm" loading={isDeleting}>
  Delete
</Button>
```
```

#### Essential Components Checklist

```
Layout:
  □ Container (max-width, padding)
  □ Stack (vertical/horizontal spacing)
  □ Grid (responsive columns)

Navigation:
  □ Navbar (top bar)
  □ Sidebar (collapsible)
  □ Breadcrumbs
  □ Tabs
  □ Pagination

Data Entry:
  □ Button (primary, secondary, danger, ghost)
  □ Input (text, number, password, search)
  □ Textarea
  □ Select / Dropdown
  □ Checkbox
  □ Radio
  □ Toggle / Switch
  □ Date Picker
  □ File Upload

Data Display:
  □ Table (sortable, paginated)
  □ Card
  □ Badge / Tag
  □ Avatar
  □ Stat / KPI Card
  □ Empty State
  □ Skeleton Loader

Feedback:
  □ Toast / Notification
  □ Alert / Banner
  □ Modal / Dialog
  □ Tooltip
  □ Progress Bar
  □ Spinner
```

---

### 3. Layout Patterns

```
Page Layout:
┌─────────────────────────────────────┐
│ Navbar (h: 64px, fixed)             │
├─────────┬───────────────────────────┤
│ Sidebar │ Main Content              │
│ (w:256) │ ┌─────────────────────┐   │
│         │ │ Page Header         │   │
│         │ │ [Title + Actions]   │   │
│         │ ├─────────────────────┤   │
│         │ │ Content Area        │   │
│         │ │ (max-w: 1200px)     │   │
│         │ │ (padding: 24px)     │   │
│         │ └─────────────────────┘   │
└─────────┴───────────────────────────┘

Page Header Pattern:
┌─────────────────────────────────────┐
│ ← Back   Breadcrumb > Path > Here  │
│                                     │
│ Page Title              [Action Btn]│
│ Description text                    │
├─────────────────────────────────────┤
│ [Tab 1] [Tab 2] [Tab 3]           │
└─────────────────────────────────────┘
```

---

### 4. Responsive Breakpoints

```typescript
export const breakpoints = {
  sm: '640px',   // Mobile landscape
  md: '768px',   // Tablet
  lg: '1024px',  // Desktop
  xl: '1280px',  // Large desktop
  '2xl': '1536px', // Extra large
};

// Usage patterns
// Mobile (<768px): Single column, bottom nav, cards
// Tablet (768-1024px): Two columns, collapsible sidebar
// Desktop (>1024px): Full layout, sidebar, tables
```

---

## Process: Creating/Updating Design System

### Step 1: Audit Existing UI
- [ ] Screenshot all existing screens
- [ ] List all colors, fonts, spacing used
- [ ] Identify inconsistencies
- [ ] List all component variants

### Step 2: Define Tokens
- [ ] Color palette (brand, neutral, semantic)
- [ ] Typography scale
- [ ] Spacing scale (4px grid)
- [ ] Shadow levels
- [ ] Border radii

### Step 3: Build Core Components
- [ ] Start with most-used (Button, Input, Card)
- [ ] Document all states
- [ ] Ensure accessibility
- [ ] Create Storybook/examples

### Step 4: Create Patterns
- [ ] Page layouts
- [ ] Form patterns
- [ ] Data display patterns
- [ ] Navigation patterns

### Step 5: Document & Govern
- [ ] Usage guidelines per component
- [ ] Do's and Don'ts
- [ ] Code examples
- [ ] Contribution process

---

## Checklist: Design System Completo

- [ ] **Tokens** definidos (colors, typography, spacing, shadows)
- [ ] **Core components** construidos (Button, Input, Card, Modal, Toast)
- [ ] **All states** cubiertos (default, hover, active, focus, disabled, error, loading)
- [ ] **Responsive** en todos los componentes
- [ ] **Accessibility** en todos los componentes
- [ ] **Documentation** con ejemplos de código
- [ ] **Consistent naming** en props y variants
