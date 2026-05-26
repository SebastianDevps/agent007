---
title: Hooks
parent: react-best-practices
rules: 8
---

# Hooks (8 reglas)

## 3.1 Seguir Reglas de Hooks
**Reglas obligatorias:**
- Solo llamar hooks en el nivel superior (no dentro de loops, condiciones o funciones anidadas)
- Solo llamar hooks desde componentes funcionales o custom hooks

**✅ HACER:**
```typescript
function UserDashboard({ userId }: UserDashboardProps) {
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchUser(userId).then(data => {
      setUser(data);
      setLoading(false);
    });
  }, [userId]);

  if (loading) return <Spinner />;
  return <div>{user?.name}</div>;
}
```

**❌ EVITAR:**
```typescript
function UserDashboard({ userId, showDetails }: UserDashboardProps) {
  if (showDetails) {
    const [user, setUser] = useState(null); // ❌ Hook condicional
  }

  for (let i = 0; i < 5; i++) {
    useEffect(() => {}); // ❌ Hook en loop
  }

  return <div>...</div>;
}
```

## 3.2 Usar Custom Hooks para Lógica Reutilizable
**✅ HACER:**
```typescript
// useAuth.ts
function useAuth() {
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const unsubscribe = onAuthStateChanged((user) => {
      setUser(user);
      setLoading(false);
    });
    return unsubscribe;
  }, []);

  const login = async (email: string, password: string) => {
    const user = await signIn(email, password);
    setUser(user);
  };

  const logout = async () => {
    await signOut();
    setUser(null);
  };

  return { user, loading, login, logout };
}

// Uso en componentes
function Header() {
  const { user, logout } = useAuth();
  return <nav>{user ? <button onClick={logout}>Salir</button> : <LoginButton />}</nav>;
}
```

## 3.3 Optimizar con useMemo y useCallback
**✅ HACER:**
```typescript
function ProductList({ products, category }: ProductListProps) {
  // Memoizar cálculos costosos
  const filteredProducts = useMemo(() =>
    products.filter(p => p.category === category),
    [products, category]
  );

  // Memoizar callbacks para evitar re-renders
  const handleAddToCart = useCallback((productId: string) => {
    addToCart(productId);
  }, []);

  return (
    <div>
      {filteredProducts.map(product => (
        <ProductCard
          key={product.id}
          product={product}
          onAddToCart={handleAddToCart}
        />
      ))}
    </div>
  );
}
```

**❌ EVITAR:**
```typescript
function ProductList({ products, category }: ProductListProps) {
  // Se recalcula en cada render
  const filteredProducts = products.filter(p => p.category === category);

  // Nueva función en cada render causa re-renders innecesarios
  const handleAddToCart = (productId: string) => {
    addToCart(productId);
  };

  return <div>{/* ... */}</div>;
}
```

## 3.4 Limpiar Effects Apropiadamente
**✅ HACER:**
```typescript
function ChatRoom({ roomId }: ChatRoomProps) {
  useEffect(() => {
    const connection = createConnection(roomId);
    connection.connect();

    // Cleanup function
    return () => {
      connection.disconnect();
    };
  }, [roomId]);

  return <div>{/* UI */}</div>;
}

function WindowSize() {
  const [size, setSize] = useState({ width: 0, height: 0 });

  useEffect(() => {
    const handleResize = () => {
      setSize({ width: window.innerWidth, height: window.innerHeight });
    };

    window.addEventListener('resize', handleResize);

    // Cleanup
    return () => window.removeEventListener('resize', handleResize);
  }, []);

  return <div>{size.width} x {size.height}</div>;
}
```

## 3.5 Usar useReducer para State Complejo
**✅ HACER:**
```typescript
type CartState = {
  items: CartItem[];
  total: number;
};

type CartAction =
  | { type: 'ADD_ITEM'; payload: CartItem }
  | { type: 'REMOVE_ITEM'; payload: string }
  | { type: 'UPDATE_QUANTITY'; payload: { id: string; quantity: number } }
  | { type: 'CLEAR_CART' };

function cartReducer(state: CartState, action: CartAction): CartState {
  switch (action.type) {
    case 'ADD_ITEM':
      return {
        items: [...state.items, action.payload],
        total: state.total + action.payload.price,
      };
    case 'REMOVE_ITEM':
      const item = state.items.find(i => i.id === action.payload);
      return {
        items: state.items.filter(i => i.id !== action.payload),
        total: state.total - (item?.price ?? 0),
      };
    case 'CLEAR_CART':
      return { items: [], total: 0 };
    default:
      return state;
  }
}

function ShoppingCart() {
  const [state, dispatch] = useReducer(cartReducer, { items: [], total: 0 });

  const addItem = (item: CartItem) => {
    dispatch({ type: 'ADD_ITEM', payload: item });
  };

  return <div>{/* UI */}</div>;
}
```

## 3.6 Evitar Dependencias Faltantes en useEffect
**✅ HACER:**
```typescript
function UserProfile({ userId }: UserProfileProps) {
  const [user, setUser] = useState<User | null>(null);

  useEffect(() => {
    fetchUser(userId).then(setUser);
  }, [userId]); // ✅ Todas las dependencias incluidas

  return <div>{user?.name}</div>;
}
```

**❌ EVITAR:**
```typescript
function UserProfile({ userId }: UserProfileProps) {
  const [user, setUser] = useState<User | null>(null);

  useEffect(() => {
    fetchUser(userId).then(setUser);
  }, []); // ❌ Falta userId en dependencias

  return <div>{user?.name}</div>;
}
```

## 3.7 Usar useRef para Valores que No Causan Re-render
**✅ HACER:**
```typescript
function VideoPlayer({ src }: VideoPlayerProps) {
  const videoRef = useRef<HTMLVideoElement>(null);
  const [isPlaying, setIsPlaying] = useState(false);

  const togglePlay = () => {
    if (videoRef.current) {
      if (isPlaying) {
        videoRef.current.pause();
      } else {
        videoRef.current.play();
      }
      setIsPlaying(!isPlaying);
    }
  };

  return (
    <div>
      <video ref={videoRef} src={src} />
      <button onClick={togglePlay}>{isPlaying ? 'Pausar' : 'Reproducir'}</button>
    </div>
  );
}
```

## 3.8 Nombrar Custom Hooks con 'use' Prefix
**✅ HACER:**
```typescript
function useLocalStorage<T>(key: string, initialValue: T) {
  const [storedValue, setStoredValue] = useState<T>(() => {
    try {
      const item = window.localStorage.getItem(key);
      return item ? JSON.parse(item) : initialValue;
    } catch (error) {
      return initialValue;
    }
  });

  const setValue = (value: T) => {
    try {
      setStoredValue(value);
      window.localStorage.setItem(key, JSON.stringify(value));
    } catch (error) {
      console.error(error);
    }
  };

  return [storedValue, setValue] as const;
}
```
