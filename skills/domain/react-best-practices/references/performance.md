---
title: Performance
parent: react-best-practices
rules: 6
---

# Performance (6 reglas)

## 4.1 Usar React.memo para Componentes Puros
**✅ HACER:**
```typescript
const ProductCard = memo(function ProductCard({ product }: ProductCardProps) {
  return (
    <div>
      <h3>{product.name}</h3>
      <p>${product.price}</p>
    </div>
  );
});

function ProductList({ products }: ProductListProps) {
  return (
    <div>
      {products.map(product => (
        <ProductCard key={product.id} product={product} />
      ))}
    </div>
  );
}
```

## 4.2 Implementar Code Splitting
**✅ HACER:**
```typescript
import { lazy, Suspense } from 'react';

const AdminDashboard = lazy(() => import('./AdminDashboard'));
const UserSettings = lazy(() => import('./UserSettings'));
const Analytics = lazy(() => import('./Analytics'));

function App() {
  return (
    <Suspense fallback={<LoadingSpinner />}>
      <Routes>
        <Route path="/admin" element={<AdminDashboard />} />
        <Route path="/settings" element={<UserSettings />} />
        <Route path="/analytics" element={<Analytics />} />
      </Routes>
    </Suspense>
  );
}
```

## 4.3 Optimizar Listas con Virtualización
**✅ HACER (usando react-window):**
```typescript
import { FixedSizeList } from 'react-window';

function VirtualizedList({ items }: VirtualizedListProps) {
  const Row = ({ index, style }: { index: number; style: CSSProperties }) => (
    <div style={style}>
      <ProductCard product={items[index]} />
    </div>
  );

  return (
    <FixedSizeList
      height={600}
      itemCount={items.length}
      itemSize={120}
      width="100%"
    >
      {Row}
    </FixedSizeList>
  );
}
```

## 4.4 Usar Imágenes Optimizadas
**✅ HACER (Next.js Image):**
```typescript
import Image from 'next/image';

function ProductImage({ src, alt }: ProductImageProps) {
  return (
    <Image
      src={src}
      alt={alt}
      width={800}
      height={600}
      placeholder="blur"
      blurDataURL="/placeholder.jpg"
      loading="lazy"
    />
  );
}
```

## 4.5 Debounce y Throttle Input Handlers
**✅ HACER:**
```typescript
import { useDebouncedCallback } from 'use-debounce';

function SearchInput() {
  const [query, setQuery] = useState('');

  const debouncedSearch = useDebouncedCallback(
    (value: string) => {
      performSearch(value);
    },
    500
  );

  const handleChange = (e: ChangeEvent<HTMLInputElement>) => {
    const value = e.target.value;
    setQuery(value);
    debouncedSearch(value);
  };

  return <input value={query} onChange={handleChange} />;
}
```

## 4.6 Evitar Re-renders Innecesarios
**✅ HACER:**
```typescript
function ExpensiveComponent({ data, onUpdate }: ExpensiveComponentProps) {
  const processedData = useMemo(() => {
    return expensiveComputation(data);
  }, [data]);

  const handleUpdate = useCallback(() => {
    onUpdate(processedData);
  }, [processedData, onUpdate]);

  return <div onClick={handleUpdate}>{processedData.result}</div>;
}

const MemoizedComponent = memo(ExpensiveComponent);
```
