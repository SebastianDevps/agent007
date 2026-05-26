---
name: frontend-design/color
---

# Color (Psicología y Armonía)

## Best Practices

### Paleta de Colores Profesional
```typescript
// Sistema de colores consistente
const colors = {
  // Marca principal - 60% del diseño
  primary: {
    50: '#f0f9ff',
    100: '#e0f2fe',
    500: '#0ea5e9',
    600: '#0284c7',
    700: '#0369a1',
    900: '#0c4a6e',
  },
  // Acento - 30% del diseño
  accent: {
    500: '#f59e0b',
    600: '#d97706',
  },
  // Neutros - Fondo y texto
  neutral: {
    50: '#fafafa',
    100: '#f5f5f5',
    500: '#737373',
    800: '#262626',
    900: '#171717',
  },
  // Estados
  success: '#10b981',
  warning: '#f59e0b',
  error: '#ef4444',
  info: '#3b82f6',
}

// Usar con propósito
<button className="bg-primary-600 hover:bg-primary-700 text-white">
  Acción Principal
</button>

<button className="bg-accent-500 hover:bg-accent-600 text-white">
  Acción Secundaria
</button>
```

### Contraste y Accesibilidad
```typescript
// WCAG AAA compliance
const textColors = {
  onLight: 'text-neutral-900',     // Contraste 21:1
  onDark: 'text-neutral-50',       // Contraste 21:1
  muted: 'text-neutral-600',       // Contraste 7:1
  disabled: 'text-neutral-400',    // Contraste 4.5:1
}

// Estados interactivos claros
<button className="
  bg-primary-600
  hover:bg-primary-700
  active:bg-primary-800
  focus:ring-4 focus:ring-primary-200
  disabled:bg-neutral-300 disabled:text-neutral-500
">
  Submit
</button>
```

### Dark Mode Thoughtful
```typescript
// Colores específicos para dark mode
<div className="
  bg-white dark:bg-neutral-900
  text-neutral-900 dark:text-neutral-50
  border-neutral-200 dark:border-neutral-800
  shadow-lg dark:shadow-neutral-900/50
">
  {/* Contenido */}
</div>

// Reducir intensidad en dark mode
<h1 className="
  text-primary-600 dark:text-primary-400
  font-bold text-4xl
">
  Título Principal
</h1>
```

## Anti-Patterns

```typescript
// NUNCA: Colores primarios vibrantes sin contexto
<div className="bg-red-500 text-blue-500 border-green-500">
  // Carnaval de colores sin significado
</div>

// NUNCA: Bajo contraste
<p className="text-gray-400 bg-gray-300">
  // Ilegible
</p>

// NUNCA: Demasiados colores de marca
<div>
  <button className="bg-purple-500">Click</button>
  <button className="bg-orange-500">Submit</button>
  <button className="bg-teal-500">Cancel</button>
  // Confuso y poco profesional
</div>

// NUNCA: Mismo color para dark mode
<div className="bg-white text-black dark:bg-black dark:text-white">
  // Demasiado contraste en dark mode
</div>
```
