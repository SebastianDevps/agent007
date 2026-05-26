---
name: frontend-design/spacing
---

# Spacing (Respiración y Balance)

## Best Practices

### Sistema de Espaciado Consistente
```typescript
// Escala de espaciado (8px base)
const spacing = {
  xs: 'p-2',      // 8px
  sm: 'p-4',      // 16px
  md: 'p-6',      // 24px
  lg: 'p-8',      // 32px
  xl: 'p-12',     // 48px
  '2xl': 'p-16',  // 64px
  '3xl': 'p-24',  // 96px
}

// Espaciado vertical coherente
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

### White Space Estratégico
```typescript
// Agrupar elementos relacionados
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

### Padding y Margin Balanceados
```typescript
// Contenedores con respiración
<div className="
  max-w-4xl mx-auto
  px-6 sm:px-8 lg:px-12
  py-12 sm:py-16 lg:py-24
">
  {/* Contenido con espacio cómodo en todos los breakpoints */}
</div>

// Cards con padding proporcional
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

## Anti-Patterns

```typescript
// NUNCA: Sin espaciado entre elementos
<div>
  <h1>Title</h1>
  <p>No space between elements makes it hard to read</p>
  <button>Action</button>
</div>

// NUNCA: Espaciado inconsistente
<div className="p-3">
  <h2 className="mb-7">Title</h2>
  <p className="mb-2">Text</p>
  <p className="mb-9">More text</p>
  // Números arbitrarios sin sistema
</div>

// NUNCA: Padding excesivo en mobile
<section className="px-20 py-32">
  {/* Demasiado padding desperdicia espacio en mobile */}
</section>

// NUNCA: Todo pegado a los bordes
<div className="p-0 m-0">
  <img src="/image.jpg" className="w-full" />
  <h1>No breathing room</h1>
  // Claustrofóbico
</div>
```
