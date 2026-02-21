---
name: frontend-design
description: Diseña y construye interfaces frontend distintivas de alta calidad con pensamiento de diseño profesional
version: 1.0.0
author: DevPartners Team
tags:
  - frontend
  - design
  - ui
  - ux
  - react
  - nextjs
  - tailwind
  - aesthetics
  - user-experience
trigger:
  auto: true
  keywords:
    - "diseña componente"
    - "crea interfaz"
    - "landing page"
    - "dashboard"
    - "formulario"
    - "card"
    - "modal"
    - "navbar"
    - "sidebar"
    - "tabla"
    - "página web"
    - "aplicación web"
    - "UI design"
    - "frontend design"
---

# Frontend Design Skill

## 🎯 Propósito

Crea interfaces frontend **distintivas y de alta calidad** con pensamiento de diseño profesional. Este skill te ayuda a construir componentes, páginas y aplicaciones web que destacan visualmente mientras mantienen excelente usabilidad.

## 🚀 Filosofía

**Tu trabajo es producir diseños frontend excepcionales** que los usuarios reconozcan como producto de alta calidad, no diseños genéricos generados por IA.

### Principios Core

1. **Calidad sobre Velocidad**: Tómate el tiempo para diseñar bien
2. **Creatividad Distintiva**: Evita patrones genéricos de IA
3. **Contexto Primero**: Entiende antes de diseñar
4. **Detalles Importan**: Pequeños toques marcan la diferencia
5. **Usuario al Centro**: Diseña para humanos reales

## 📋 Proceso de Design Thinking

### 1. COMPRENDER (Understand)

Antes de escribir código, **SIEMPRE** pregunta:

#### Contexto del Proyecto
```
¿Qué tipo de producto/página necesitas?
- Landing page
- Dashboard
- Aplicación SaaS
- Sitio corporativo
- E-commerce
- Portfolio
- Blog
- Otro: _______

¿Cuál es el objetivo principal?
- Conversión/ventas
- Información
- Herramienta de trabajo
- Engagement/comunidad
- Showcase/portfolio
```

#### Target Audience
```
¿Quién usará esto?
- Edad aproximada: _______
- Nivel técnico: Principiante / Intermedio / Experto
- Industria/sector: _______
- Dispositivos principales: Desktop / Mobile / Ambos
```

#### Brand & Estética
```
¿Tienes preferencias de estilo?
- Minimalista / Moderno / Clásico / Bold / Otro
- Colores de marca (si aplica): _______
- Referencias que te gusten: _______
- Lo que NO quieres: _______
```

#### Requisitos Técnicos
```
Stack actual:
- Framework: React / Next.js / Vue / Otro
- Styling: Tailwind / CSS Modules / Styled Components / Otro
- Componentes: shadcn/ui / Material UI / Chakra / Custom
- Estado: Redux / Zustand / Context / Otro

Features necesarias:
- [ ] Responsive design
- [ ] Dark mode
- [ ] Animaciones
- [ ] Internacionalización
- [ ] Accesibilidad (WCAG)
- [ ] SEO optimization
```

### 2. IDEAR (Ideate)

Una vez que entiendes el contexto, genera ideas creativas:

#### Layout Thinking
- ¿Grid o flexbox?
- ¿Una columna o múltiples?
- ¿Navegación fija o estática?
- ¿Hero section o entrada directa?
- ¿Sidebar o top navigation?

#### Visual Direction
- ¿Qué emoción debe transmitir?
- ¿Qué elementos visuales destacan la marca?
- ¿Qué diferencia este diseño de la competencia?
- ¿Qué micro-interacciones mejoran la experiencia?

#### Content Hierarchy
1. ¿Qué es lo más importante?
2. ¿Qué necesita ver primero el usuario?
3. ¿Cómo guiamos la atención?
4. ¿Dónde están los CTAs?

### 3. CREAR (Create)

Implementa con atención a los **5 pilares de Frontend Aesthetics**.

### 4. ITERAR (Iterate)

- Muestra el diseño
- Recibe feedback
- Refina y mejora
- Repite hasta perfección

## 🎨 Las 5 Áreas de Frontend Aesthetics

### 1. Color (Psicología y Armonía)

#### ✅ Best Practices

**Paleta de Colores Profesional**
```typescript
// ✅ Sistema de colores consistente
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

// ✅ Usar con propósito
<button className="bg-primary-600 hover:bg-primary-700 text-white">
  Acción Principal
</button>

<button className="bg-accent-500 hover:bg-accent-600 text-white">
  Acción Secundaria
</button>
```

**Contraste y Accesibilidad**
```typescript
// ✅ WCAG AAA compliance
const textColors = {
  onLight: 'text-neutral-900',     // Contraste 21:1
  onDark: 'text-neutral-50',       // Contraste 21:1
  muted: 'text-neutral-600',       // Contraste 7:1
  disabled: 'text-neutral-400',    // Contraste 4.5:1
}

// ✅ Estados interactivos claros
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

**Dark Mode Thoughtful**
```typescript
// ✅ Colores específicos para dark mode
<div className="
  bg-white dark:bg-neutral-900
  text-neutral-900 dark:text-neutral-50
  border-neutral-200 dark:border-neutral-800
  shadow-lg dark:shadow-neutral-900/50
">
  {/* Contenido */}
</div>

// ✅ Reducir intensidad en dark mode
<h1 className="
  text-primary-600 dark:text-primary-400
  font-bold text-4xl
">
  Título Principal
</h1>
```

#### ❌ Anti-Patterns

```typescript
// ❌ NUNCA: Colores primarios vibrantes sin contexto
<div className="bg-red-500 text-blue-500 border-green-500">
  // Carnaval de colores sin significado
</div>

// ❌ NUNCA: Bajo contraste
<p className="text-gray-400 bg-gray-300">
  // Ilegible
</p>

// ❌ NUNCA: Demasiados colores de marca
<div>
  <button className="bg-purple-500">Click</button>
  <button className="bg-orange-500">Submit</button>
  <button className="bg-teal-500">Cancel</button>
  // Confuso y poco profesional
</div>

// ❌ NUNCA: Mismo color para dark mode
<div className="bg-white text-black dark:bg-black dark:text-white">
  // Demasiado contraste en dark mode
</div>
```

### 2. Typography (Jerarquía y Legibilidad)

#### ✅ Best Practices

**Sistema de Tipografía Escalable**
```typescript
// ✅ Escala tipográfica consistente (1.25 ratio)
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

// ✅ Jerarquía visual clara
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

**Font Pairing Profesional**
```typescript
// ✅ Combinar serif + sans-serif
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

// ✅ O usar una sola font con variaciones
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

**Responsive Typography**
```typescript
// ✅ Escalado inteligente con Tailwind
<h1 className="
  text-3xl sm:text-4xl md:text-5xl lg:text-6xl
  font-bold
  leading-tight
  max-w-4xl
">
  Título que escala bien en todos los tamaños
</h1>

// ✅ Limitar ancho para legibilidad
<p className="
  text-base md:text-lg
  leading-relaxed
  max-w-prose  {/* ~65 caracteres por línea */}
">
  El texto largo es más fácil de leer cuando está limitado a 65-75 caracteres por línea
</p>
```

#### ❌ Anti-Patterns

```typescript
// ❌ NUNCA: Demasiados tamaños de fuente
<div>
  <h1 className="text-6xl">Title</h1>
  <h2 className="text-4.5xl">Subtitle</h2>  // Tamaño arbitrario
  <p className="text-17px">Text</p>         // Valor custom sin escala
</div>

// ❌ NUNCA: Mala legibilidad
<p className="text-xs leading-tight max-w-full">
  Texto pequeño, apretado y ancho completo = ilegible
</p>

// ❌ NUNCA: Mixing demasiadas fonts
<div className="font-roboto">
  <h1 className="font-montserrat">Title</h1>
  <h2 className="font-raleway">Subtitle</h2>
  <p className="font-lato">Body</p>
  // Caos tipográfico
</div>

// ❌ NUNCA: All caps para párrafos largos
<p className="uppercase">
  LEER TEXTOS LARGOS EN MAYÚSCULAS ES EXTREMADAMENTE DIFÍCIL Y CANSADO PARA LOS OJOS...
</p>
```

### 3. Spacing (Respiración y Balance)

#### ✅ Best Practices

**Sistema de Espaciado Consistente**
```typescript
// ✅ Escala de espaciado (8px base)
const spacing = {
  xs: 'p-2',      // 8px
  sm: 'p-4',      // 16px
  md: 'p-6',      // 24px
  lg: 'p-8',      // 32px
  xl: 'p-12',     // 48px
  '2xl': 'p-16',  // 64px
  '3xl': 'p-24',  // 96px
}

// ✅ Espaciado vertical coherente
<section className="py-24 px-6">
  <div className="max-w-6xl mx-auto space-y-16">

    <div className="space-y-4">
      <h2 className="text-3xl font-bold">
        Título de Sección
      </h2>
      <p className="text-lg text-neutral-600">
        Descripción con espacio suficiente
      </p>
    </div>

    <div className="grid grid-cols-3 gap-8">
      {/* Cards con espaciado uniforme */}
      <Card className="p-6 space-y-4">
        <h3 className="text-xl font-semibold">Card Title</h3>
        <p className="text-neutral-600">Description</p>
      </Card>
    </div>

  </div>
</section>
```

**White Space Estratégico**
```typescript
// ✅ Agrupar elementos relacionados
<form className="space-y-8">

  {/* Grupo 1: Info personal */}
  <div className="space-y-4">
    <h3 className="text-lg font-semibold mb-3">
      Información Personal
    </h3>
    <div className="space-y-3">
      <Input label="Nombre" />
      <Input label="Email" />
    </div>
  </div>

  {/* Grupo 2: Preferencias */}
  <div className="space-y-4">
    <h3 className="text-lg font-semibold mb-3">
      Preferencias
    </h3>
    <div className="space-y-3">
      <Select label="País" />
      <Select label="Idioma" />
    </div>
  </div>

  {/* CTA separado claramente */}
  <div className="pt-6 border-t">
    <Button>Guardar Cambios</Button>
  </div>

</form>
```

**Padding y Margin Balanceados**
```typescript
// ✅ Contenedores con respiración
<div className="
  max-w-4xl mx-auto
  px-6 sm:px-8 lg:px-12
  py-12 sm:py-16 lg:py-24
">
  {/* Contenido con espacio cómodo en todos los breakpoints */}
</div>

// ✅ Cards con padding proporcional
<Card className="
  p-6 sm:p-8
  space-y-4
  hover:shadow-lg
  transition-shadow
">
  <Icon className="w-12 h-12 mb-2" />
  <h3 className="text-xl font-semibold">Feature</h3>
  <p className="text-neutral-600 leading-relaxed">
    Description with comfortable spacing
  </p>
</Card>
```

#### ❌ Anti-Patterns

```typescript
// ❌ NUNCA: Sin espaciado entre elementos
<div>
  <h1>Title</h1>
  <p>No space between elements makes it hard to read</p>
  <button>Action</button>
</div>

// ❌ NUNCA: Espaciado inconsistente
<div className="p-3">
  <h2 className="mb-7">Title</h2>
  <p className="mb-2">Text</p>
  <p className="mb-9">More text</p>
  // Números arbitrarios sin sistema
</div>

// ❌ NUNCA: Padding excesivo en mobile
<section className="px-20 py-32">
  {/* Demasiado padding desperdicia espacio en mobile */}
</section>

// ❌ NUNCA: Todo pegado a los bordes
<div className="p-0 m-0">
  <img src="/image.jpg" className="w-full" />
  <h1>No breathing room</h1>
  // Claustrofóbico
</div>
```

### 4. Layout (Estructura y Flujo)

#### ✅ Best Practices

**Grid Systems Profesionales**
```typescript
// ✅ Grid responsive con gaps consistentes
<div className="
  grid
  grid-cols-1
  sm:grid-cols-2
  lg:grid-cols-3
  xl:grid-cols-4
  gap-6 lg:gap-8
">
  {items.map(item => (
    <Card key={item.id} className="h-full">
      {/* Content */}
    </Card>
  ))}
</div>

// ✅ Asymmetric grid para jerarquía
<div className="grid grid-cols-12 gap-8">

  {/* Main content - 8 columnas */}
  <article className="col-span-12 lg:col-span-8">
    <h1 className="text-4xl font-bold mb-6">
      Artículo Principal
    </h1>
    <p className="text-lg leading-relaxed">
      Contenido principal con más espacio
    </p>
  </article>

  {/* Sidebar - 4 columnas */}
  <aside className="col-span-12 lg:col-span-4">
    <div className="sticky top-8 space-y-6">
      <Card>Related Links</Card>
      <Card>Newsletter</Card>
    </div>
  </aside>

</div>
```

**Container y Max-Width**
```typescript
// ✅ Sistema de containers consistente
const containers = {
  sm: 'max-w-2xl',   // 672px - Forms, artículos
  md: 'max-w-4xl',   // 896px - Content pages
  lg: 'max-w-6xl',   // 1152px - Dashboards
  xl: 'max-w-7xl',   // 1280px - Landing pages
  full: 'max-w-full', // Full width
}

// ✅ Centrado con padding responsivo
<div className="
  max-w-6xl
  mx-auto
  px-4 sm:px-6 lg:px-8
">
  {/* Contenido centrado con padding lateral */}
</div>
```

**Flexbox para Componentes**
```typescript
// ✅ Navbar con flex
<nav className="
  flex items-center justify-between
  px-6 py-4
  bg-white border-b
">
  <div className="flex items-center gap-8">
    <Logo />
    <NavLinks />
  </div>
  <div className="flex items-center gap-4">
    <SearchBar />
    <UserMenu />
  </div>
</nav>

// ✅ Card con flex para footer sticky
<Card className="flex flex-col h-full">

  <div className="flex-1">
    {/* Content que crece */}
    <h3 className="text-xl font-semibold mb-2">
      Card Title
    </h3>
    <p className="text-neutral-600">
      Variable length content
    </p>
  </div>

  <div className="mt-4 pt-4 border-t">
    {/* Footer siempre al fondo */}
    <Button>Action</Button>
  </div>

</Card>
```

**Sticky y Fixed Positioning**
```typescript
// ✅ Sticky header
<header className="
  sticky top-0 z-50
  bg-white/80 backdrop-blur-md
  border-b border-neutral-200
">
  <nav className="max-w-7xl mx-auto px-6 py-4">
    {/* Navigation */}
  </nav>
</header>

// ✅ Sticky sidebar
<aside className="
  hidden lg:block
  sticky top-20
  h-[calc(100vh-5rem)]
  overflow-y-auto
">
  {/* Sidebar content */}
</aside>

// ✅ Fixed bottom CTA (mobile)
<div className="
  lg:hidden
  fixed bottom-0 inset-x-0
  p-4 bg-white border-t
  shadow-lg
">
  <Button className="w-full">
    Continuar
  </Button>
</div>
```

#### ❌ Anti-Patterns

```typescript
// ❌ NUNCA: Layouts que no son responsive
<div className="grid grid-cols-4 gap-4">
  {/* Se rompe en mobile */}
</div>

// ❌ NUNCA: Anchos fijos en lugar de max-width
<div className="w-[1200px] mx-auto">
  {/* Se desborda en pantallas pequeñas */}
</div>

// ❌ NUNCA: Demasiados niveles de nesting
<div className="container">
  <div className="wrapper">
    <div className="inner">
      <div className="content">
        <div className="actual-content">
          {/* Complejidad innecesaria */}
        </div>
      </div>
    </div>
  </div>
</div>

// ❌ NUNCA: Fixed heights arbitrarias
<div className="h-[347px]">
  {/* Número mágico sin razón */}
</div>
```

### 5. Motion (Animaciones y Transiciones)

#### ✅ Best Practices

**Transiciones Sutiles**
```typescript
// ✅ Hover states suaves
<button className="
  bg-primary-600
  hover:bg-primary-700
  transform hover:scale-105
  transition-all duration-200 ease-out
  active:scale-95
">
  Hover Me
</button>

// ✅ Animaciones de entrada con Framer Motion
import { motion } from 'framer-motion'

<motion.div
  initial={{ opacity: 0, y: 20 }}
  animate={{ opacity: 1, y: 0 }}
  transition={{ duration: 0.5, ease: 'easeOut' }}
>
  {/* Content */}
</motion.div>

// ✅ Stagger children
<motion.div variants={containerVariants}>
  {items.map((item, i) => (
    <motion.div
      key={item.id}
      variants={itemVariants}
      custom={i}
    >
      {item.content}
    </motion.div>
  ))}
</motion.div>

const containerVariants = {
  hidden: { opacity: 0 },
  visible: {
    opacity: 1,
    transition: {
      staggerChildren: 0.1
    }
  }
}

const itemVariants = {
  hidden: { opacity: 0, y: 20 },
  visible: {
    opacity: 1,
    y: 0,
    transition: { duration: 0.4 }
  }
}
```

**Micro-interacciones**
```typescript
// ✅ Loading states
<button
  disabled={isLoading}
  className="relative"
>
  <span className={isLoading ? 'opacity-0' : 'opacity-100'}>
    Submit
  </span>
  {isLoading && (
    <span className="
      absolute inset-0
      flex items-center justify-center
    ">
      <Spinner className="animate-spin" />
    </span>
  )}
</button>

// ✅ Success feedback
<motion.div
  initial={{ scale: 0 }}
  animate={{ scale: 1 }}
  className="
    bg-green-50 border border-green-200
    text-green-800 p-4 rounded-lg
    flex items-center gap-3
  "
>
  <CheckCircle className="w-5 h-5" />
  <span>Guardado exitosamente</span>
</motion.div>

// ✅ Skeleton loading
<div className="space-y-4">
  {[...Array(3)].map((_, i) => (
    <div key={i} className="animate-pulse">
      <div className="h-4 bg-neutral-200 rounded w-3/4 mb-2" />
      <div className="h-4 bg-neutral-200 rounded w-1/2" />
    </div>
  ))}
</div>
```

**Page Transitions**
```typescript
// ✅ Transiciones entre páginas (Next.js + Framer Motion)
import { AnimatePresence, motion } from 'framer-motion'
import { useRouter } from 'next/router'

export default function App({ Component, pageProps }) {
  const router = useRouter()

  return (
    <AnimatePresence mode="wait">
      <motion.div
        key={router.pathname}
        initial={{ opacity: 0, x: -20 }}
        animate={{ opacity: 1, x: 0 }}
        exit={{ opacity: 0, x: 20 }}
        transition={{ duration: 0.3 }}
      >
        <Component {...pageProps} />
      </motion.div>
    </AnimatePresence>
  )
}
```

**Parallax y Scroll Effects**
```typescript
// ✅ Parallax sutil en hero
import { useScroll, useTransform, motion } from 'framer-motion'

export function ParallaxHero() {
  const { scrollY } = useScroll()
  const y = useTransform(scrollY, [0, 500], [0, 150])
  const opacity = useTransform(scrollY, [0, 300], [1, 0])

  return (
    <section className="relative h-screen overflow-hidden">
      <motion.div
        style={{ y, opacity }}
        className="absolute inset-0"
      >
        <Image src="/hero.jpg" alt="Hero" fill />
      </motion.div>
      <div className="relative z-10 flex items-center justify-center h-full">
        <h1 className="text-6xl font-bold text-white">
          Welcome
        </h1>
      </div>
    </section>
  )
}

// ✅ Reveal on scroll
import { motion } from 'framer-motion'
import { useInView } from 'react-intersection-observer'

export function RevealOnScroll({ children }) {
  const [ref, inView] = useInView({
    triggerOnce: true,
    threshold: 0.1,
  })

  return (
    <motion.div
      ref={ref}
      initial={{ opacity: 0, y: 50 }}
      animate={inView ? { opacity: 1, y: 0 } : {}}
      transition={{ duration: 0.6, ease: 'easeOut' }}
    >
      {children}
    </motion.div>
  )
}
```

#### ❌ Anti-Patterns

```typescript
// ❌ NUNCA: Animaciones demasiado lentas
<motion.div
  animate={{ opacity: 1 }}
  transition={{ duration: 3 }}  // Demasiado lento
>
  {/* Usuario pierde interés */}
</motion.div>

// ❌ NUNCA: Animaciones que distraen
<div className="
  animate-bounce  // Rebota infinitamente
  animate-spin    // Gira sin parar
  animate-pulse   // Pulsa constantemente
">
  {/* Mareante y molesto */}
</div>

// ❌ NUNCA: Transitions en todo
<div className="transition-all">
  {/* Muy pesado, anima todas las propiedades */}
</div>

// ❌ NUNCA: Sin reduced motion
// Siempre respetar prefers-reduced-motion
<motion.div
  initial={{ opacity: 0, scale: 0.5, rotate: 360 }}
  animate={{ opacity: 1, scale: 1, rotate: 0 }}
  // Sin considerar usuarios con sensibilidad al movimiento
/>

// ✅ Correcto:
<motion.div
  initial={{ opacity: 0 }}
  animate={{ opacity: 1 }}
  transition={{
    duration: prefersReducedMotion ? 0 : 0.5
  }}
/>
```

## 🎯 Patrones de Componentes Comunes

### Hero Section

```typescript
// ✅ Hero moderno con gradiente y CTA
export function HeroSection() {
  return (
    <section className="
      relative overflow-hidden
      bg-gradient-to-br from-primary-600 via-primary-700 to-primary-900
      py-24 sm:py-32 lg:py-40
    ">

      {/* Background pattern */}
      <div className="
        absolute inset-0
        bg-[url('/grid.svg')]
        opacity-10
      " />

      <div className="relative max-w-7xl mx-auto px-6 lg:px-8">

        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6 }}
          className="max-w-3xl"
        >

          {/* Badge */}
          <div className="
            inline-flex items-center gap-2
            px-4 py-2 rounded-full
            bg-white/10 backdrop-blur-sm
            text-white text-sm font-medium
            mb-6
          ">
            <Sparkles className="w-4 h-4" />
            <span>Nuevo: Feature Launch</span>
          </div>

          {/* Headline */}
          <h1 className="
            text-5xl sm:text-6xl lg:text-7xl
            font-bold text-white
            leading-tight mb-6
          ">
            Transforma tu negocio con{' '}
            <span className="
              bg-gradient-to-r from-accent-400 to-accent-600
              bg-clip-text text-transparent
            ">
              nuestra solución
            </span>
          </h1>

          {/* Subheadline */}
          <p className="
            text-xl sm:text-2xl
            text-primary-100
            leading-relaxed mb-10
          ">
            La plataforma todo-en-uno para gestionar tu empresa de manera eficiente y escalable
          </p>

          {/* CTAs */}
          <div className="flex flex-col sm:flex-row gap-4">
            <Button
              size="lg"
              className="
                bg-white text-primary-700
                hover:bg-primary-50
                shadow-xl hover:shadow-2xl
              "
            >
              Comenzar gratis
              <ArrowRight className="ml-2 w-5 h-5" />
            </Button>

            <Button
              size="lg"
              variant="outline"
              className="
                border-2 border-white/20
                text-white
                hover:bg-white/10
                backdrop-blur-sm
              "
            >
              Ver demo
              <Play className="ml-2 w-5 h-5" />
            </Button>
          </div>

          {/* Social proof */}
          <div className="mt-12 flex items-center gap-6">
            <div className="flex -space-x-2">
              {[1,2,3,4].map(i => (
                <Image
                  key={i}
                  src={`/avatars/${i}.jpg`}
                  alt="User"
                  width={40}
                  height={40}
                  className="rounded-full border-2 border-white"
                />
              ))}
            </div>
            <div className="text-white/90">
              <div className="font-semibold">+10,000 empresas</div>
              <div className="text-sm text-white/70">confían en nosotros</div>
            </div>
          </div>

        </motion.div>

      </div>

      {/* Decorative elements */}
      <div className="
        absolute -top-24 -right-24
        w-96 h-96
        bg-accent-500/20
        rounded-full
        blur-3xl
      " />
      <div className="
        absolute -bottom-24 -left-24
        w-96 h-96
        bg-primary-400/20
        rounded-full
        blur-3xl
      " />

    </section>
  )
}
```

### Feature Cards

```typescript
// ✅ Feature cards con iconos y hover effects
export function FeatureCards() {
  const features = [
    {
      icon: Zap,
      title: 'Ultra rápido',
      description: 'Rendimiento optimizado para experiencias instantáneas',
      color: 'from-yellow-400 to-orange-500',
    },
    {
      icon: Shield,
      title: 'Seguro',
      description: 'Encriptación de nivel empresarial para tus datos',
      color: 'from-blue-400 to-cyan-500',
    },
    {
      icon: Users,
      title: 'Colaborativo',
      description: 'Trabaja en equipo sin fricción ni límites',
      color: 'from-purple-400 to-pink-500',
    },
  ]

  return (
    <section className="py-24 bg-neutral-50">
      <div className="max-w-7xl mx-auto px-6 lg:px-8">

        <div className="text-center max-w-2xl mx-auto mb-16">
          <h2 className="text-4xl font-bold text-neutral-900 mb-4">
            Todo lo que necesitas
          </h2>
          <p className="text-xl text-neutral-600">
            Potencia tu productividad con features diseñadas para tu éxito
          </p>
        </div>

        <div className="grid md:grid-cols-3 gap-8">
          {features.map((feature, index) => (
            <motion.div
              key={feature.title}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: index * 0.1 }}
            >
              <Card className="
                group
                h-full p-8
                border-2 border-neutral-200
                hover:border-primary-300
                hover:shadow-xl hover:shadow-primary-100
                transition-all duration-300
                cursor-pointer
              ">

                {/* Icon */}
                <div className={`
                  w-14 h-14 rounded-2xl
                  bg-gradient-to-br ${feature.color}
                  flex items-center justify-center
                  mb-6
                  group-hover:scale-110
                  transition-transform duration-300
                `}>
                  <feature.icon className="w-7 h-7 text-white" />
                </div>

                {/* Content */}
                <h3 className="
                  text-2xl font-bold text-neutral-900 mb-3
                  group-hover:text-primary-600
                  transition-colors
                ">
                  {feature.title}
                </h3>

                <p className="text-neutral-600 leading-relaxed mb-6">
                  {feature.description}
                </p>

                {/* Link */}
                <div className="
                  inline-flex items-center gap-2
                  text-primary-600 font-medium
                  group-hover:gap-3
                  transition-all
                ">
                  <span>Conocer más</span>
                  <ArrowRight className="w-4 h-4" />
                </div>

              </Card>
            </motion.div>
          ))}
        </div>

      </div>
    </section>
  )
}
```

### Dashboard Layout

```typescript
// ✅ Dashboard moderno con sidebar y stats
export function DashboardLayout({ children }: { children: React.ReactNode }) {
  return (
    <div className="flex h-screen bg-neutral-50">

      {/* Sidebar */}
      <aside className="
        w-64 bg-white border-r border-neutral-200
        flex flex-col
      ">

        {/* Logo */}
        <div className="p-6 border-b border-neutral-200">
          <Logo className="h-8" />
        </div>

        {/* Navigation */}
        <nav className="flex-1 p-4 space-y-1 overflow-y-auto">
          <NavItem icon={LayoutDashboard} label="Dashboard" active />
          <NavItem icon={Users} label="Clientes" />
          <NavItem icon={FileText} label="Documentos" />
          <NavItem icon={Settings} label="Configuración" />
        </nav>

        {/* User menu */}
        <div className="p-4 border-t border-neutral-200">
          <UserMenu />
        </div>

      </aside>

      {/* Main content */}
      <div className="flex-1 flex flex-col overflow-hidden">

        {/* Header */}
        <header className="
          bg-white border-b border-neutral-200
          px-8 py-4
          flex items-center justify-between
        ">
          <div>
            <h1 className="text-2xl font-bold text-neutral-900">
              Dashboard
            </h1>
            <p className="text-neutral-600">
              Bienvenido de vuelta, Juan
            </p>
          </div>

          <div className="flex items-center gap-4">
            <SearchBar />
            <NotificationsButton />
          </div>
        </header>

        {/* Content area */}
        <main className="flex-1 overflow-y-auto p-8">

          {/* Stats grid */}
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
            <StatCard
              label="Ingresos totales"
              value="$48,574"
              change="+12.5%"
              trend="up"
              icon={DollarSign}
            />
            <StatCard
              label="Nuevos clientes"
              value="324"
              change="+8.2%"
              trend="up"
              icon={Users}
            />
            <StatCard
              label="Tasa de conversión"
              value="3.24%"
              change="-2.1%"
              trend="down"
              icon={TrendingUp}
            />
            <StatCard
              label="Proyectos activos"
              value="12"
              change="+3"
              trend="up"
              icon={Briefcase}
            />
          </div>

          {/* Main content */}
          {children}

        </main>

      </div>

    </div>
  )
}

function StatCard({ label, value, change, trend, icon: Icon }) {
  return (
    <Card className="p-6">
      <div className="flex items-start justify-between mb-4">
        <div className={`
          w-12 h-12 rounded-lg
          flex items-center justify-center
          ${trend === 'up'
            ? 'bg-green-100 text-green-600'
            : 'bg-red-100 text-red-600'
          }
        `}>
          <Icon className="w-6 h-6" />
        </div>
        <div className={`
          text-sm font-medium
          ${trend === 'up' ? 'text-green-600' : 'text-red-600'}
        `}>
          {change}
        </div>
      </div>
      <div className="text-3xl font-bold text-neutral-900 mb-1">
        {value}
      </div>
      <div className="text-neutral-600">
        {label}
      </div>
    </Card>
  )
}
```

### Form Design

```typescript
// ✅ Formulario con validación y UX pulida
export function ModernForm() {
  const [isLoading, setIsLoading] = useState(false)
  const [errors, setErrors] = useState({})

  return (
    <div className="min-h-screen bg-neutral-50 flex items-center justify-center p-6">

      <Card className="w-full max-w-md p-8">

        {/* Header */}
        <div className="text-center mb-8">
          <div className="
            w-16 h-16 mx-auto mb-4
            bg-gradient-to-br from-primary-500 to-primary-700
            rounded-2xl
            flex items-center justify-center
          ">
            <Rocket className="w-8 h-8 text-white" />
          </div>
          <h2 className="text-3xl font-bold text-neutral-900 mb-2">
            Crear cuenta
          </h2>
          <p className="text-neutral-600">
            Comienza tu prueba gratuita de 14 días
          </p>
        </div>

        {/* Form */}
        <form onSubmit={handleSubmit} className="space-y-5">

          {/* Name field */}
          <div>
            <label className="
              block text-sm font-medium text-neutral-700 mb-2
            ">
              Nombre completo
            </label>
            <div className="relative">
              <User className="
                absolute left-3 top-1/2 -translate-y-1/2
                w-5 h-5 text-neutral-400
              " />
              <input
                type="text"
                placeholder="Juan Pérez"
                className={`
                  w-full pl-10 pr-4 py-3
                  border-2 rounded-lg
                  focus:outline-none focus:ring-4
                  transition-all
                  ${errors.name
                    ? 'border-red-300 focus:border-red-500 focus:ring-red-100'
                    : 'border-neutral-200 focus:border-primary-500 focus:ring-primary-100'
                  }
                `}
              />
            </div>
            {errors.name && (
              <p className="mt-2 text-sm text-red-600 flex items-center gap-1">
                <AlertCircle className="w-4 h-4" />
                {errors.name}
              </p>
            )}
          </div>

          {/* Email field */}
          <div>
            <label className="
              block text-sm font-medium text-neutral-700 mb-2
            ">
              Email
            </label>
            <div className="relative">
              <Mail className="
                absolute left-3 top-1/2 -translate-y-1/2
                w-5 h-5 text-neutral-400
              " />
              <input
                type="email"
                placeholder="juan@ejemplo.com"
                className="
                  w-full pl-10 pr-4 py-3
                  border-2 border-neutral-200 rounded-lg
                  focus:outline-none focus:ring-4
                  focus:border-primary-500 focus:ring-primary-100
                  transition-all
                "
              />
            </div>
          </div>

          {/* Password field */}
          <div>
            <label className="
              block text-sm font-medium text-neutral-700 mb-2
            ">
              Contraseña
            </label>
            <div className="relative">
              <Lock className="
                absolute left-3 top-1/2 -translate-y-1/2
                w-5 h-5 text-neutral-400
              " />
              <input
                type="password"
                placeholder="••••••••"
                className="
                  w-full pl-10 pr-4 py-3
                  border-2 border-neutral-200 rounded-lg
                  focus:outline-none focus:ring-4
                  focus:border-primary-500 focus:ring-primary-100
                  transition-all
                "
              />
            </div>
            <p className="mt-2 text-xs text-neutral-500">
              Mínimo 8 caracteres con mayúsculas y números
            </p>
          </div>

          {/* Terms */}
          <div className="flex items-start gap-3">
            <input
              type="checkbox"
              id="terms"
              className="
                mt-1 w-4 h-4
                text-primary-600 rounded
                focus:ring-2 focus:ring-primary-200
              "
            />
            <label htmlFor="terms" className="text-sm text-neutral-600">
              Acepto los{' '}
              <a href="#" className="text-primary-600 hover:underline">
                términos y condiciones
              </a>
              {' '}y la{' '}
              <a href="#" className="text-primary-600 hover:underline">
                política de privacidad
              </a>
            </label>
          </div>

          {/* Submit button */}
          <Button
            type="submit"
            disabled={isLoading}
            className="
              w-full py-3
              bg-gradient-to-r from-primary-600 to-primary-700
              hover:from-primary-700 hover:to-primary-800
              text-white font-medium
              shadow-lg hover:shadow-xl
              transition-all
            "
          >
            {isLoading ? (
              <span className="flex items-center justify-center gap-2">
                <Loader className="w-5 h-5 animate-spin" />
                Creando cuenta...
              </span>
            ) : (
              <span className="flex items-center justify-center gap-2">
                Crear cuenta
                <ArrowRight className="w-5 h-5" />
              </span>
            )}
          </Button>

          {/* Footer */}
          <p className="text-center text-sm text-neutral-600">
            ¿Ya tienes cuenta?{' '}
            <a href="#" className="
              text-primary-600 font-medium
              hover:text-primary-700
            ">
              Inicia sesión
            </a>
          </p>

        </form>

      </Card>

    </div>
  )
}
```

## 🚀 Ejemplos de Uso

### 1. Landing Page Completa

```bash
# Usuario solicita:
"Crea una landing page para una app de productividad SaaS.
Target: Profesionales 25-40 años.
Estilo: Moderno y minimalista.
Debe incluir hero, features, pricing, testimonios y footer."

# El skill pregunta contexto adicional:
¿Nombre de la app? → "TaskFlow"
¿Colores de marca? → "Azul (#0066FF) y Gris oscuro"
¿Precio mensual? → "$9.99/mes"
¿USP principal? → "Gestión de tareas con IA"

# Genera código completo con:
- Hero con gradiente y CTAs
- Features grid con iconos
- Pricing cards con highlight
- Testimonials carousel
- Footer con links
- Responsive design
- Dark mode support
- Smooth animations
```

### 2. Dashboard de Analytics

```bash
# Usuario solicita:
"Diseña un dashboard de analytics para e-commerce.
Debe mostrar: ventas, conversiones, productos top, gráficas."

# El skill pregunta:
¿Qué framework? → "Next.js 14 con shadcn/ui"
¿Gráficas? → "Sí, usar Recharts"
¿Filtros de fecha? → "Sí, últimos 7/30/90 días"

# Genera:
- Sidebar con navegación
- Header con filtros
- Stats cards con trends
- Gráficas responsivas
- Tabla de productos
- Exportación de datos
```

### 3. Formulario Multi-paso

```bash
# Usuario solicita:
"Formulario de onboarding en 3 pasos: datos personales,
preferencias, confirmación. Con progress bar."

# Genera:
- Stepper visual
- Validación por paso
- Animaciones entre pasos
- Preview antes de enviar
- Success state
```

### 4. Modal/Dialog Avanzado

```bash
# Usuario solicita:
"Modal para confirmar eliminación de cuenta con
animación de entrada, blur background y botones de confirmar/cancelar"

# Genera:
- Overlay con backdrop blur
- Modal centrado con shadow
- Animación scale + fade
- Focus trap
- Escape key handler
- Confirmation input
```

## 📚 Recursos y Referencias

### Herramientas Recomendadas

- **Design Systems**: shadcn/ui, Radix UI, Headless UI
- **Animaciones**: Framer Motion, React Spring
- **Iconos**: Lucide React, Heroicons, Phosphor
- **Colores**: Coolors.co, Tailwind Colors
- **Tipografía**: Google Fonts, Font Pair
- **Imágenes**: Unsplash, Pexels (placeholders)

### Inspiración de Diseño

- Dribbble (dribbble.com)
- Behance (behance.net)
- Awwwards (awwwards.com)
- Land-book (land-book.com)
- SaaS Landing Pages (saaslandingpage.com)

### Accessibility

- WCAG 2.1 Level AA mínimo
- Contrast ratio 4.5:1 para texto normal
- Contrast ratio 3:1 para texto grande
- Keyboard navigation completo
- Screen reader friendly
- Focus indicators visibles

## ✅ Checklist de Calidad

Antes de entregar código, verificar:

### Visual Design
- [ ] Paleta de colores consistente (máximo 3-4 colores)
- [ ] Tipografía jerárquica (máximo 2 familias de fuentes)
- [ ] Espaciado uniforme (sistema de 8px)
- [ ] Contraste WCAG AA cumplido
- [ ] Iconos consistentes (mismo set)

### Responsive
- [ ] Mobile first approach
- [ ] Breakpoints: sm (640), md (768), lg (1024), xl (1280)
- [ ] Touch targets mínimo 44x44px
- [ ] Texto legible sin zoom
- [ ] No scroll horizontal

### Performance
- [ ] Imágenes optimizadas (WebP, lazy loading)
- [ ] Fonts optimizados (preload, display: swap)
- [ ] Animaciones con GPU (transform, opacity)
- [ ] Code splitting en rutas
- [ ] CSS crítico inlined

### Accessibility
- [ ] Landmarks semánticos (header, nav, main, footer)
- [ ] Alt text en imágenes
- [ ] Labels en inputs
- [ ] Focus visible
- [ ] Keyboard navigation
- [ ] ARIA attributes donde necesario

### User Experience
- [ ] Loading states en acciones async
- [ ] Error handling visible
- [ ] Success feedback
- [ ] Empty states diseñados
- [ ] Confirmación en acciones destructivas

### Code Quality
- [ ] Componentes reutilizables
- [ ] Props tipadas (TypeScript)
- [ ] Sin hardcoded values
- [ ] Comentarios en lógica compleja
- [ ] Convenciones del proyecto seguidas

## 🎓 Mensajes al Usuario

### Antes de Empezar
```
🎨 Voy a diseñar [componente/página] para ti.

Primero, necesito entender mejor tu visión:

1. ¿Qué objetivo tiene este diseño?
2. ¿Quién lo usará? (audiencia target)
3. ¿Tienes colores de marca o preferencias?
4. ¿Qué stack técnico estás usando?
5. ¿Alguna referencia que te guste?

Esto me ayudará a crear algo perfecto para tu caso.
```

### Durante el Trabajo
```
🔧 Estoy creando tu [componente] con:
- Sistema de colores coherente
- Tipografía jerárquica
- Espaciado uniforme
- Responsive design
- Animaciones sutiles
- Accesibilidad completa

Trabajando en ello...
```

### Al Entregar
```
✨ ¡Listo! He creado tu [componente/página] con:

📱 Responsive: Mobile, tablet y desktop
🎨 Design System: Colores, tipografía y espaciado consistentes
♿ Accesible: WCAG AA, keyboard navigation
⚡ Performante: Optimizado para carga rápida
🌓 Dark Mode: Soporte completo (opcional)

📝 Próximos pasos sugeridos:
1. [Acción 1]
2. [Acción 2]
3. [Acción 3]

¿Quieres ajustar algo? (colores, espaciado, animaciones, etc.)
```

## 🚨 Errores Comunes a Evitar

### 1. Generic AI Design
```typescript
// ❌ Diseño genérico de IA
<div className="bg-blue-500 text-white p-4 rounded">
  <h1>Welcome</h1>
  <p>This is a generic card</p>
  <button className="bg-white text-blue-500 px-4 py-2 rounded">
    Click me
  </button>
</div>

// ✅ Diseño distintivo y profesional
<Card className="
  relative overflow-hidden
  bg-gradient-to-br from-primary-600 via-primary-700 to-primary-900
  p-8 rounded-2xl
  shadow-2xl shadow-primary-900/20
">
  <div className="absolute -top-24 -right-24 w-48 h-48 bg-white/10 rounded-full blur-3xl" />
  <div className="relative z-10">
    <h1 className="text-4xl font-bold text-white mb-3">
      Welcome back
    </h1>
    <p className="text-primary-100 text-lg mb-6 leading-relaxed">
      Your personalized dashboard is ready
    </p>
    <Button className="
      bg-white text-primary-700
      hover:bg-primary-50 hover:shadow-xl
      font-semibold px-6 py-3
      transition-all duration-200
    ">
      Get started
      <ArrowRight className="ml-2 w-5 h-5" />
    </Button>
  </div>
</Card>
```

### 2. Over-engineering
```typescript
// ❌ Demasiado complejo
<div className="grid grid-cols-12">
  <div className="col-span-12 lg:col-span-8 xl:col-span-9">
    <div className="grid grid-cols-6">
      <div className="col-span-3 md:col-span-2 lg:col-span-3">
        {/* Complejidad innecesaria */}
      </div>
    </div>
  </div>
</div>

// ✅ Simple y efectivo
<div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
  <Card>{/* Content */}</Card>
  <Card>{/* Content */}</Card>
  <Card>{/* Content */}</Card>
</div>
```

### 3. Inconsistencia
```typescript
// ❌ Espaciado inconsistente
<div className="mb-3">
  <h2 className="mb-7">Title</h2>
  <p className="mb-2">Text</p>
  <button className="mt-5">Action</button>
</div>

// ✅ Sistema consistente
<div className="space-y-6">
  <h2 className="text-2xl font-bold">Title</h2>
  <p className="text-neutral-600">Text</p>
  <Button>Action</Button>
</div>
```

## 🎯 Mindset Final

Cuando uses este skill, recuerda:

1. **Pregunta primero, diseña después** - El contexto es clave
2. **Simplicidad elegante > Complejidad** - Less is more
3. **Usuario primero** - Diseña para humanos, no para impresionar
4. **Detalles importan** - Pequeños toques hacen gran diferencia
5. **Consistencia > Creatividad caótica** - Sistemático pero distintivo

---

**¡A crear interfaces excepcionales!** 🚀

Este skill está aquí para ayudarte a producir frontend de **calidad profesional** que tus usuarios amarán. Úsalo sabiamente y siempre prioriza la experiencia del usuario.
