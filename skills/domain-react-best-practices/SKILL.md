---
name: react-best-practices
description: "React/Next.js patterns for performant, maintainable, accessible components"
version: 2.0.0
allowed-tools: ["Read", "Grep", "Glob", "WebFetch"]
load_when:
  - writing_react_components
  - reviewing_react_code
  - optimizing_react_performance
inputs:
  - name: component_requirements
    type: string
    required: true
  - name: existing_design_system
    type: string
    required: false
outputs:
  - name: component_implementation
    type: string
    format: "TypeScript React functional component, hooks, accessible"
  - name: performance_checklist
    type: checklist
    format: "useMemo | useCallback | lazy loading | bundle size"
constraints:
  - functional_components_only_no_class_components
  - accessibility_attributes_required_on_interactive_elements
  - no_prop_drilling_beyond_2_levels
mandatory-fetch-rule: |
  Antes de afirmar "best practice" sobre React, Next.js o React Router,
  invocar WebFetch contra el dominio canónico correspondiente y citar
  la URL exacta. NUNCA recitar best practices de memoria — la API
  evoluciona rápido (Server Components, Server Actions, use, useTransition,
  useOptimistic, useFormState).
---

# React Best Practices

Skill especializado en patrones React/Next.js. 57 reglas en 8 categorías, organizadas como referencias modulares. Inspirado en estándares Vercel Labs.

## When to invoke

Activar este skill cuando:

- Se escriben o revisan componentes React (`.tsx`, `.jsx`)
- Se diseñan custom hooks o utilidades reactivas
- Se optimiza performance (re-renders, memoization, bundle size)
- Se trabaja con Next.js App Router (Server Components, Server Actions, streaming)
- Se modela estado (local, contexto, server state, store global)
- Se escriben tests de componentes con React Testing Library
- Se evalúa accesibilidad (a11y) de UI

NO activar para: lógica de backend pura, scripts CLI, código no-React.

## Anti-patterns explícitos (NUNCA hacer)

Violaciones duras detectadas durante revisión de código React/Next.js. Cada una mapea a una regla en `references/`:

1. **NUNCA usar `useEffect` para data fetching del servidor en Next.js 13+ App Router.** Usar Server Components con `await` directo, o TanStack Query en Client Components. Ver `references/server-components.md` §6.3.
2. **NUNCA llamar `setState` dentro del render** (sin `useEffect`). Causa loops infinitos. Ver `references/fundamentals.md` §1.2.
3. **NUNCA mutar state directamente** (`array.push`, `obj.prop = x`). Usar spread o `useReducer`. Ver `references/fundamentals.md` §1.4.
4. **NUNCA usar `index` como `key`** en listas que pueden reordenarse. Usar IDs estables. Ver `references/fundamentals.md` §1.3.
5. **NUNCA props drilling más de 2 niveles** (constraint del frontmatter). Usar Context, composition o store. Ver `references/components.md` §2.6 y `references/state-management.md` §7.7.
6. **NUNCA llamar hooks condicionalmente o en loops.** Solo en el top level del componente o custom hook. Ver `references/hooks.md` §3.1.
7. **NUNCA omitir dependencias en `useEffect`/`useMemo`/`useCallback`.** Stale closures. Ver `references/hooks.md` §3.6.
8. **NUNCA olvidar el cleanup de subscripciones, listeners o conexiones** en `useEffect`. Memory leaks. Ver `references/hooks.md` §3.4.
9. **NUNCA usar Class Components** en código nuevo. Solo functional + hooks. Ver `references/fundamentals.md` §1.1.
10. **NUNCA pasar objetos no-serializables (Date, Map, funciones)** de Server Component a Client Component. Serializar primero. Ver `references/server-components.md` §6.5.
11. **NUNCA usar `any` en TypeScript.** Usar `unknown` + type guards. Ver `references/typescript.md` §5.4.
12. **NUNCA testear implementación interna** (`getByClassName`, querySelector). Testear comportamiento desde la perspectiva del usuario. Ver `references/testing.md` §8.2.
13. **NUNCA marcar como `'use client'` un árbol completo** cuando solo una hoja necesita interactividad. Mover el boundary lo más abajo posible.
14. **NUNCA almacenar valores derivables como state.** Calcularlos en render. Ver `references/state-management.md` §7.1.

## Need → Reference

| Necesito... | Referencia |
|---|---|
| Estructura básica de componente, JSX, keys, fragments, pureza | `references/fundamentals.md` |
| Composición, naming, render props, controlled forms, props drilling | `references/components.md` |
| `useState`, `useEffect`, `useMemo`, `useCallback`, `useReducer`, `useRef`, custom hooks | `references/hooks.md` |
| `React.memo`, code splitting, virtualización, debounce, lazy loading, imágenes | `references/performance.md` |
| Tipar props, generics, type guards, utility types, event handlers | `references/typescript.md` |
| Server Components, `'use client'`, Server Actions, Suspense, Metadata API, loading/error | `references/server-components.md` |
| State minimal, lifting state, Context, Zustand, TanStack Query, composition vs drilling | `references/state-management.md` |
| Testing Library, MSW, jest-axe, behavioral tests, a11y tests | `references/testing.md` |
| Templates rápidos, patrón de Server Component, patrón de custom hook | `references/cheatsheet.md` |

## Uso

```bash
# Revisar componente
"Revisa este componente siguiendo react-best-practices"

# Optimizar performance
"Optimiza este código usando react-best-practices para performance"

# Validar arquitectura
"¿Este diseño sigue react-best-practices?"
```

## Convenciones de idioma

- Código (variables, funciones, tipos) → INGLÉS
- Mensajes al usuario, validaciones, errores → ESPAÑOL
- Comentarios → ESPAÑOL
- Test descriptions → ESPAÑOL · assertions → INGLÉS

---

**Versión**: 2.0.0 (split en references por regla del proyecto: max 200 líneas/archivo)
**Última actualización**: 2026-05-06
**Fuente**: Vercel Labs React Best Practices (adaptado)

## Sources

- https://react.dev/learn — React official documentation
- https://react.dev/reference/react — React API reference (hooks, memo, Suspense)
- https://nextjs.org/docs — Next.js documentation
- https://nextjs.org/docs/app — Next.js App Router (Server Components, Server Actions, streaming)
- https://react-router.com/ — React Router documentation
