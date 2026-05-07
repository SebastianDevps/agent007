---
title: Quick Reference - Cheatsheet
parent: react-best-practices
---

# Quick Reference - Cheatsheet

## Estructura de Componentes
```typescript
// ✅ Template básico
interface ComponentProps {
  // Props tipadas
}

function Component({ prop1, prop2 }: ComponentProps) {
  // Hooks primero
  const [state, setState] = useState();
  const data = useMemo(() => compute(), [deps]);
  const callback = useCallback(() => {}, [deps]);

  useEffect(() => {
    // Effects
    return () => cleanup();
  }, [deps]);

  // Event handlers
  const handleEvent = () => {};

  // Render
  return <div>{/* JSX */}</div>;
}
```

## Custom Hooks Pattern
```typescript
function useFeature(param: string) {
  const [state, setState] = useState();

  useEffect(() => {
    // Logic
  }, [param]);

  const actions = useMemo(() => ({
    action1: () => {},
    action2: () => {},
  }), [deps]);

  return { state, ...actions };
}
```

## Server Component Pattern (Next.js)
```typescript
// Server Component
async function Page() {
  const data = await fetchData();
  return <ClientComponent data={serialize(data)} />;
}

// Client Component
'use client';
function ClientComponent({ data }: Props) {
  const [state, setState] = useState();
  return <div onClick={() => setState(x)}>{data}</div>;
}
```

## Testing Pattern
```typescript
describe('Component', () => {
  it('comportamiento esperado', async () => {
    // Arrange
    const props = { /* ... */ };

    // Act
    render(<Component {...props} />);
    fireEvent.click(screen.getByRole('button'));

    // Assert
    await waitFor(() => {
      expect(screen.getByText(/resultado/i)).toBeInTheDocument();
    });
  });
});
```

## Convenciones de Idioma

- **Código**: Variables, funciones, clases → INGLÉS
- **Mensajes de usuario**: Validaciones, errores → ESPAÑOL
- **Comentarios**: Explicaciones → ESPAÑOL
- **Tests**: Descriptions → ESPAÑOL, assertions → INGLÉS

## Recursos Adicionales

- [React Docs](https://react.dev)
- [Next.js Docs](https://nextjs.org/docs)
- [TypeScript Handbook](https://www.typescriptlang.org/docs)
- [Testing Library](https://testing-library.com)
- [TanStack Query](https://tanstack.com/query)
