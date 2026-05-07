---
name: frontend-design/common-errors
---

# Errores Comunes a Evitar

## 1. Generic AI Design

```typescript
// Diseño genérico de IA
<div className="bg-blue-500 text-white p-4 rounded">
  <h1>Welcome</h1>
  <p>This is a generic card</p>
  <button className="bg-white text-blue-500 px-4 py-2 rounded">
    Click me
  </button>
</div>

// Diseño distintivo y profesional
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

## 2. Over-engineering

```typescript
// Demasiado complejo
<div className="grid grid-cols-12">
  <div className="col-span-12 lg:col-span-8 xl:col-span-9">
    <div className="grid grid-cols-6">
      <div className="col-span-3 md:col-span-2 lg:col-span-3">
        {/* Complejidad innecesaria */}
      </div>
    </div>
  </div>
</div>

// Simple y efectivo
<div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
  <Card>{/* Content */}</Card>
  <Card>{/* Content */}</Card>
  <Card>{/* Content */}</Card>
</div>
```

## 3. Inconsistencia

```typescript
// Espaciado inconsistente
<div className="mb-3">
  <h2 className="mb-7">Title</h2>
  <p className="mb-2">Text</p>
  <button className="mt-5">Action</button>
</div>

// Sistema consistente
<div className="space-y-6">
  <h2 className="text-2xl font-bold">Title</h2>
  <p className="text-neutral-600">Text</p>
  <Button>Action</Button>
</div>
```

## Mindset Final

1. **Pregunta primero, diseña después** — El contexto es clave
2. **Simplicidad elegante > Complejidad** — Less is more
3. **Usuario primero** — Diseña para humanos, no para impresionar
4. **Detalles importan** — Pequeños toques hacen gran diferencia
5. **Consistencia > Creatividad caótica** — Sistemático pero distintivo
