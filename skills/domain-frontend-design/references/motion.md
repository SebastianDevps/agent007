---
name: frontend-design/motion
---

# Motion (Animaciones y Transiciones)

## Best Practices

### Transiciones Sutiles
```typescript
// Hover states suaves
<button className="
  bg-primary-600
  hover:bg-primary-700
  transform hover:scale-105
  transition-all duration-200 ease-out
  active:scale-95
">
  Hover Me
</button>

// Animaciones de entrada con Framer Motion
import { motion } from 'framer-motion'

<motion.div
  initial={{ opacity: 0, y: 20 }}
  animate={{ opacity: 1, y: 0 }}
  transition={{ duration: 0.5, ease: 'easeOut' }}
>
  {/* Content */}
</motion.div>

// Stagger children
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

### Micro-interacciones
```typescript
// Loading states
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

// Success feedback
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

// Skeleton loading
<div className="space-y-4">
  {[...Array(3)].map((_, i) => (
    <div key={i} className="animate-pulse">
      <div className="h-4 bg-neutral-200 rounded w-3/4 mb-2" />
      <div className="h-4 bg-neutral-200 rounded w-1/2" />
    </div>
  ))}
</div>
```

### Page Transitions
```typescript
// Transiciones entre páginas (Next.js + Framer Motion)
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

### Parallax y Scroll Effects
```typescript
// Parallax sutil en hero
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

// Reveal on scroll
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

## Anti-Patterns

```typescript
// NUNCA: Animaciones demasiado lentas
<motion.div
  animate={{ opacity: 1 }}
  transition={{ duration: 3 }}  // Demasiado lento
>
  {/* Usuario pierde interés */}
</motion.div>

// NUNCA: Animaciones que distraen
<div className="
  animate-bounce  // Rebota infinitamente
  animate-spin    // Gira sin parar
  animate-pulse   // Pulsa constantemente
">
  {/* Mareante y molesto */}
</div>

// NUNCA: Transitions en todo
<div className="transition-all">
  {/* Muy pesado, anima todas las propiedades */}
</div>

// NUNCA: Sin reduced motion
// Siempre respetar prefers-reduced-motion
<motion.div
  initial={{ opacity: 0, scale: 0.5, rotate: 360 }}
  animate={{ opacity: 1, scale: 1, rotate: 0 }}
  // Sin considerar usuarios con sensibilidad al movimiento
/>

// Correcto:
<motion.div
  initial={{ opacity: 0 }}
  animate={{ opacity: 1 }}
  transition={{
    duration: prefersReducedMotion ? 0 : 0.5
  }}
/>
```
