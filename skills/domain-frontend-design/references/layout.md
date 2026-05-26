---
name: frontend-design/layout
---

# Layout (Estructura y Flujo)

## Best Practices

### Grid Systems Profesionales
```typescript
// Grid responsive con gaps consistentes
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

// Asymmetric grid para jerarquía
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

### Container y Max-Width
```typescript
// Sistema de containers consistente
const containers = {
  sm: 'max-w-2xl',   // 672px - Forms, artículos
  md: 'max-w-4xl',   // 896px - Content pages
  lg: 'max-w-6xl',   // 1152px - Dashboards
  xl: 'max-w-7xl',   // 1280px - Landing pages
  full: 'max-w-full', // Full width
}

// Centrado con padding responsivo
<div className="
  max-w-6xl
  mx-auto
  px-4 sm:px-6 lg:px-8
">
  {/* Contenido centrado con padding lateral */}
</div>
```

### Flexbox para Componentes
```typescript
// Navbar con flex
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

// Card con flex para footer sticky
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

### Sticky y Fixed Positioning
```typescript
// Sticky header
<header className="
  sticky top-0 z-50
  bg-white/80 backdrop-blur-md
  border-b border-neutral-200
">
  <nav className="max-w-7xl mx-auto px-6 py-4">
    {/* Navigation */}
  </nav>
</header>

// Sticky sidebar
<aside className="
  hidden lg:block
  sticky top-20
  h-[calc(100vh-5rem)]
  overflow-y-auto
">
  {/* Sidebar content */}
</aside>

// Fixed bottom CTA (mobile)
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

## Anti-Patterns

```typescript
// NUNCA: Layouts que no son responsive
<div className="grid grid-cols-4 gap-4">
  {/* Se rompe en mobile */}
</div>

// NUNCA: Anchos fijos en lugar de max-width
<div className="w-[1200px] mx-auto">
  {/* Se desborda en pantallas pequeñas */}
</div>

// NUNCA: Demasiados niveles de nesting
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

// NUNCA: Fixed heights arbitrarias
<div className="h-[347px]">
  {/* Número mágico sin razón */}
</div>
```
