---
name: frontend-design/checklist
---

# Checklist de Calidad

Antes de entregar código, verificar:

## Visual Design
- [ ] Paleta de colores consistente (máximo 3-4 colores)
- [ ] Tipografía jerárquica (máximo 2 familias de fuentes)
- [ ] Espaciado uniforme (sistema de 8px)
- [ ] Contraste WCAG AA cumplido
- [ ] Iconos consistentes (mismo set)

## Responsive
- [ ] Mobile first approach
- [ ] Breakpoints: sm (640), md (768), lg (1024), xl (1280)
- [ ] Touch targets mínimo 44x44px
- [ ] Texto legible sin zoom
- [ ] No scroll horizontal

## Performance
- [ ] Imágenes optimizadas (WebP, lazy loading)
- [ ] Fonts optimizados (preload, display: swap)
- [ ] Animaciones con GPU (transform, opacity)
- [ ] Code splitting en rutas
- [ ] CSS crítico inlined

## Accessibility
- [ ] Landmarks semánticos (header, nav, main, footer)
- [ ] Alt text en imágenes
- [ ] Labels en inputs
- [ ] Focus visible
- [ ] Keyboard navigation
- [ ] ARIA attributes donde necesario

## User Experience
- [ ] Loading states en acciones async
- [ ] Error handling visible
- [ ] Success feedback
- [ ] Empty states diseñados
- [ ] Confirmación en acciones destructivas

## Code Quality
- [ ] Componentes reutilizables
- [ ] Props tipadas (TypeScript)
- [ ] Sin hardcoded values
- [ ] Comentarios en lógica compleja
- [ ] Convenciones del proyecto seguidas

## Mensajes al Usuario

### Antes de Empezar
```
Voy a diseñar [componente/página] para ti.

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
Estoy creando tu [componente] con:
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
¡Listo! He creado tu [componente/página] con:

- Responsive: Mobile, tablet y desktop
- Design System: Colores, tipografía y espaciado consistentes
- Accesible: WCAG AA, keyboard navigation
- Performante: Optimizado para carga rápida
- Dark Mode: Soporte completo (opcional)

Próximos pasos sugeridos:
1. [Acción 1]
2. [Acción 2]
3. [Acción 3]

¿Quieres ajustar algo? (colores, espaciado, animaciones, etc.)
```
