---
name: frontend-design/typography
---

# Typography (Jerarquía y Legibilidad)

## Best Practices

### Sistema de Tipografía Escalable
```typescript
// Escala tipográfica consistente (1.25 ratio)
const typography = {
  h1: 'text-5xl font-bold leading-tight',      // 48px
  h2: 'text-4xl font-bold leading-tight',      // 36px
  h3: 'text-3xl font-semibold leading-snug',   // 30px
  h4: 'text-2xl font-semibold leading-snug',   // 24px
  h5: 'text-xl font-medium leading-normal',    // 20px
  body: 'text-base leading-relaxed',           // 16px
  small: 'text-sm leading-normal',             // 14px
  tiny: 'text-xs leading-normal',              // 12px
}

// Jerarquía visual clara
<article>
  <h1 className="text-5xl font-bold text-neutral-900 mb-4">
    Título Principal de la Página
  </h1>
  <p className="text-xl text-neutral-600 mb-8 leading-relaxed">
    Subtítulo o lead paragraph con información clave
  </p>
  <h2 className="text-3xl font-semibold text-neutral-800 mb-3 mt-12">
    Sección Principal
  </h2>
  <p className="text-base text-neutral-700 leading-relaxed">
    Contenido del cuerpo con espaciado cómodo
  </p>
</article>
```

### Font Pairing Profesional
```typescript
// Combinar serif + sans-serif
import { Inter, Playfair_Display } from 'next/font/google'

const inter = Inter({ subsets: ['latin'], variable: '--font-inter' })
const playfair = Playfair_Display({ subsets: ['latin'], variable: '--font-playfair' })

// En layout
<body className={`${inter.variable} ${playfair.variable}`}>
  <h1 className="font-playfair text-5xl">  {/* Elegante */}
    Diseño Premium
  </h1>
  <p className="font-inter text-base">     {/* Legible */}
    Contenido fácil de leer
  </p>
</body>

// O usar una sola font con variaciones
<div className="font-inter">
  <h1 className="text-4xl font-black">      {/* 900 weight */}
    Super Bold
  </h1>
  <h2 className="text-2xl font-bold">       {/* 700 weight */}
    Bold
  </h2>
  <p className="text-base font-normal">     {/* 400 weight */}
    Normal text
  </p>
</div>
```

### Responsive Typography
```typescript
// Escalado inteligente con Tailwind
<h1 className="
  text-3xl sm:text-4xl md:text-5xl lg:text-6xl
  font-bold
  leading-tight
  max-w-4xl
">
  Título que escala bien en todos los tamaños
</h1>

// Limitar ancho para legibilidad
<p className="
  text-base md:text-lg
  leading-relaxed
  max-w-prose  {/* ~65 caracteres por línea */}
">
  El texto largo es más fácil de leer cuando está limitado a 65-75 caracteres por línea
</p>
```

## Anti-Patterns

```typescript
// NUNCA: Demasiados tamaños de fuente
<div>
  <h1 className="text-6xl">Title</h1>
  <h2 className="text-4.5xl">Subtitle</h2>  // Tamaño arbitrario
  <p className="text-17px">Text</p>         // Valor custom sin escala
</div>

// NUNCA: Mala legibilidad
<p className="text-xs leading-tight max-w-full">
  Texto pequeño, apretado y ancho completo = ilegible
</p>

// NUNCA: Mixing demasiadas fonts
<div className="font-roboto">
  <h1 className="font-montserrat">Title</h1>
  <h2 className="font-raleway">Subtitle</h2>
  <p className="font-lato">Body</p>
  // Caos tipográfico
</div>

// NUNCA: All caps para párrafos largos
<p className="uppercase">
  LEER TEXTOS LARGOS EN MAYÚSCULAS ES EXTREMADAMENTE DIFÍCIL Y CANSADO PARA LOS OJOS...
</p>
```
