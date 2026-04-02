# Frontend Design - Quick Reference

> **Full details**: See SKILL.md for complete design process

## Design Principles

### Visual Hierarchy
1. **Size**: Larger = more important
2. **Color**: Contrast draws attention
3. **Spacing**: White space creates focus
4. **Typography**: Weight, size, font family

### Composition
- **Grid**: 12-column for responsive layouts
- **Alignment**: Everything aligns to something
- **Proximity**: Related items close together
- **Balance**: Visual weight distribution

### Color System
```
Primary: Brand color (CTAs, links)
Secondary: Supporting actions
Accent: Highlights, success states
Neutrals: Text, backgrounds (gray scale)
Semantic: Error (red), Warning (yellow), Success (green)
```

### Typography Scale
```
Display: 48-64px (hero, h1)
Heading: 32-40px (h2-h3)
Subheading: 24-28px (h4-h5)
Body: 16px (base)
Small: 14px (captions, labels)
```

## Component Patterns

### Spacing Scale (8px base)
```
4px  - Tight (icon padding)
8px  - Compact (button padding)
16px - Default (card padding)
24px - Comfortable (section spacing)
32px - Loose (major sections)
48px - Extra loose (page sections)
```

### Buttons
```
Primary: Solid, primary color (main action)
Secondary: Outlined (alternative action)
Tertiary: Text only (low priority)

Sizes: sm (32px), md (40px), lg (48px)
States: default, hover, active, disabled
```

### Cards
```
Structure:
- Header (title, actions)
- Content (body)
- Footer (metadata, links)

Variants: outlined, elevated, filled
```

### Forms
```
Labels: Above input (mobile-friendly)
Validation: Inline, on blur
States: default, focus, error, disabled
Help text: Below input
```

## Accessibility Quick Check

- [ ] Color contrast ≥ 4.5:1 (text)
- [ ] Focus visible (keyboard navigation)
- [ ] Alt text en images
- [ ] ARIA labels donde sea necesario
- [ ] Semantic HTML (`<button>`, `<nav>`, `<main>`)
- [ ] Form labels asociados con inputs

## Responsive Breakpoints

```
Mobile: < 640px
Tablet: 640px - 1024px
Desktop: > 1024px
Wide: > 1440px
```

## Component Anatomy Template

```tsx
// Visual structure
<Component>
  <Header />      // Title, actions, close
  <Content />     // Main content
  <Footer />      // Metadata, actions
</Component>

// States to design
- Default
- Hover
- Active
- Disabled
- Loading
- Error
```

## Design Tokens

```typescript
const tokens = {
  colors: { primary, secondary, ... },
  spacing: { xs, sm, md, lg, xl },
  typography: { fontSize, lineHeight, fontWeight },
  borderRadius: { sm: 4px, md: 8px, lg: 16px },
  shadows: { sm, md, lg },
};
```

## Quick Design Process

1. **Wireframe** (low-fidelity, structure)
2. **Mockup** (high-fidelity, visual design)
3. **Prototype** (interactive, user flows)
4. **Component specs** (spacing, colors, states)
5. **Handoff** (design tokens, assets)

---

Ver SKILL.md para proceso completo y ejemplos de diseño profesional.
