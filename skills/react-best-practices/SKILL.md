# React Best Practices - Guía Completa

---
name: react-best-practices
description: Guía completa de mejores prácticas para desarrollo React/Next.js basada en Vercel Labs
version: 1.0.0
author: Vercel Labs (adaptado)
tags: [react, nextjs, best-practices, performance, typescript]
---

## Descripción

Skill especializado en aplicar las mejores prácticas de React y Next.js según los estándares de Vercel Labs. Incluye 57 reglas organizadas en 8 categorías que cubren desde fundamentos de React hasta optimización de performance y Server Components.

## Uso

```bash
# Aplicar al revisar código React
"Revisa este componente siguiendo react-best-practices"

# Optimizar performance
"Optimiza este código usando react-best-practices para performance"

# Validar arquitectura de componentes
"¿Este diseño sigue react-best-practices?"
```

## Categorías de Reglas

1. **React Fundamentals** (10 reglas)
2. **Components** (7 reglas)
3. **Hooks** (8 reglas)
4. **Performance** (6 reglas)
5. **TypeScript** (6 reglas)
6. **Server Components** (8 reglas)
7. **State Management** (7 reglas)
8. **Testing** (5 reglas)

---

## 1. React Fundamentals (10 reglas)

### 1.1 Usar Functional Components
**✅ HACER:**
```typescript
// Componente funcional moderno
function UserProfile({ name, email }: UserProfileProps) {
  return (
    <div>
      <h1>{name}</h1>
      <p>{email}</p>
    </div>
  );
}
```

**❌ EVITAR:**
```typescript
// Class component (obsoleto)
class UserProfile extends React.Component {
  render() {
    return <div>{this.props.name}</div>;
  }
}
```

### 1.2 Mantener Componentes Puros
**Principio:** Los componentes deben retornar la misma salida para las mismas props.

**✅ HACER:**
```typescript
function PriceDisplay({ price, currency }: PriceDisplayProps) {
  // Función pura - mismo input, mismo output
  const formattedPrice = formatPrice(price, currency);
  return <span>{formattedPrice}</span>;
}
```

**❌ EVITAR:**
```typescript
function PriceDisplay({ price }: PriceDisplayProps) {
  // Impuro - depende de estado externo
  const formattedPrice = formatPrice(price, globalCurrency);
  return <span>{formattedPrice}</span>;
}
```

### 1.3 Usar Keys Estables en Listas
**✅ HACER:**
```typescript
function UserList({ users }: UserListProps) {
  return (
    <ul>
      {users.map((user) => (
        <li key={user.id}>{user.name}</li>
      ))}
    </ul>
  );
}
```

**❌ EVITAR:**
```typescript
function UserList({ users }: UserListProps) {
  return (
    <ul>
      {users.map((user, index) => (
        <li key={index}>{user.name}</li>
      ))}
    </ul>
  );
}
```

### 1.4 Evitar Mutación Directa de State
**✅ HACER:**
```typescript
function TodoList() {
  const [todos, setTodos] = useState<Todo[]>([]);

  const addTodo = (text: string) => {
    setTodos([...todos, { id: Date.now(), text }]);
  };

  const toggleTodo = (id: number) => {
    setTodos(todos.map(todo =>
      todo.id === id ? { ...todo, completed: !todo.completed } : todo
    ));
  };

  return <div>{/* render */}</div>;
}
```

**❌ EVITAR:**
```typescript
function TodoList() {
  const [todos, setTodos] = useState<Todo[]>([]);

  const addTodo = (text: string) => {
    todos.push({ id: Date.now(), text }); // ❌ Mutación directa
    setTodos(todos);
  };

  return <div>{/* render */}</div>;
}
```

### 1.5 Usar Fragment para Múltiples Elementos
**✅ HACER:**
```typescript
function UserCard({ user }: UserCardProps) {
  return (
    <>
      <h2>{user.name}</h2>
      <p>{user.bio}</p>
      <ContactInfo email={user.email} />
    </>
  );
}
```

**❌ EVITAR:**
```typescript
function UserCard({ user }: UserCardProps) {
  return (
    <div> {/* div innecesario */}
      <h2>{user.name}</h2>
      <p>{user.bio}</p>
    </div>
  );
}
```

### 1.6 Usar Conditional Rendering Apropiado
**✅ HACER:**
```typescript
function Dashboard({ user, isLoading }: DashboardProps) {
  if (isLoading) return <LoadingSpinner />;
  if (!user) return <LoginPrompt />;

  return (
    <div>
      <h1>Bienvenido, {user.name}</h1>
      {user.isPremium && <PremiumBadge />}
    </div>
  );
}
```

**❌ EVITAR:**
```typescript
function Dashboard({ user, isLoading }: DashboardProps) {
  return (
    <div>
      {isLoading ? <LoadingSpinner /> :
        !user ? <LoginPrompt /> :
          <div>
            <h1>Bienvenido, {user.name}</h1>
            {user.isPremium ? <PremiumBadge /> : null}
          </div>
      }
    </div>
  );
}
```

### 1.7 Evitar Lógica Compleja en JSX
**✅ HACER:**
```typescript
function OrderSummary({ order }: OrderSummaryProps) {
  const totalPrice = calculateTotalPrice(order.items);
  const discountAmount = calculateDiscount(totalPrice, order.discountCode);
  const finalPrice = totalPrice - discountAmount;
  const shippingCost = calculateShipping(order.destination);

  return (
    <div>
      <p>Subtotal: ${totalPrice}</p>
      <p>Descuento: -${discountAmount}</p>
      <p>Envío: ${shippingCost}</p>
      <p>Total: ${finalPrice + shippingCost}</p>
    </div>
  );
}
```

**❌ EVITAR:**
```typescript
function OrderSummary({ order }: OrderSummaryProps) {
  return (
    <div>
      <p>Total: ${order.items.reduce((sum, item) => sum + item.price * item.qty, 0) - (order.discountCode ? order.items.reduce((sum, item) => sum + item.price * item.qty, 0) * 0.1 : 0)}</p>
    </div>
  );
}
```

### 1.8 Usar PropTypes o TypeScript
**✅ HACER (TypeScript - recomendado):**
```typescript
interface ButtonProps {
  variant: 'primary' | 'secondary' | 'danger';
  size?: 'small' | 'medium' | 'large';
  disabled?: boolean;
  onClick: () => void;
  children: React.ReactNode;
}

function Button({ variant, size = 'medium', disabled = false, onClick, children }: ButtonProps) {
  return (
    <button className={`btn-${variant} btn-${size}`} disabled={disabled} onClick={onClick}>
      {children}
    </button>
  );
}
```

### 1.9 Separar Concerns (UI vs Lógica)
**✅ HACER:**
```typescript
// useUserData.ts - Lógica
function useUserData(userId: string) {
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchUser(userId).then(data => {
      setUser(data);
      setLoading(false);
    });
  }, [userId]);

  return { user, loading };
}

// UserProfile.tsx - UI
function UserProfile({ userId }: UserProfileProps) {
  const { user, loading } = useUserData(userId);

  if (loading) return <Spinner />;
  if (!user) return <NotFound />;

  return (
    <div>
      <Avatar src={user.avatar} />
      <h1>{user.name}</h1>
    </div>
  );
}
```

### 1.10 Usar Children Prop Apropiadamente
**✅ HACER:**
```typescript
function Card({ title, children }: CardProps) {
  return (
    <div className="card">
      <h2>{title}</h2>
      <div className="card-content">{children}</div>
    </div>
  );
}

// Uso
<Card title="Usuario">
  <UserAvatar />
  <UserInfo />
  <UserActions />
</Card>
```

---

## 2. Components (7 reglas)

### 2.1 Un Componente por Archivo
**✅ HACER:**
```typescript
// Button.tsx
export function Button({ children, onClick }: ButtonProps) {
  return <button onClick={onClick}>{children}</button>;
}

// Input.tsx
export function Input({ value, onChange }: InputProps) {
  return <input value={value} onChange={onChange} />;
}
```

**❌ EVITAR:**
```typescript
// FormComponents.tsx
export function Button() { /* ... */ }
export function Input() { /* ... */ }
export function Select() { /* ... */ }
export function Checkbox() { /* ... */ }
```

### 2.2 Nombrar Componentes Descriptivamente
**✅ HACER:**
```typescript
function UserProfileCard({ user }: UserProfileCardProps) { /* ... */ }
function ProductPriceDisplay({ price }: ProductPriceDisplayProps) { /* ... */ }
function ShoppingCartCheckoutButton({ onCheckout }: ShoppingCartCheckoutButtonProps) { /* ... */ }
```

**❌ EVITAR:**
```typescript
function Card({ user }: CardProps) { /* ... */ }
function Display({ price }: DisplayProps) { /* ... */ }
function Button({ onCheckout }: ButtonProps) { /* ... */ }
```

### 2.3 Usar Composición sobre Herencia
**✅ HACER:**
```typescript
function PageLayout({ children }: PageLayoutProps) {
  return (
    <div>
      <Header />
      <main>{children}</main>
      <Footer />
    </div>
  );
}

function DashboardPage() {
  return (
    <PageLayout>
      <DashboardContent />
    </PageLayout>
  );
}
```

**❌ EVITAR:**
```typescript
class BasePage extends React.Component {
  renderHeader() { return <Header />; }
  renderFooter() { return <Footer />; }
}

class DashboardPage extends BasePage {
  render() {
    return (
      <div>
        {this.renderHeader()}
        <DashboardContent />
        {this.renderFooter()}
      </div>
    );
  }
}
```

### 2.4 Extraer Componentes Pequeños y Reutilizables
**✅ HACER:**
```typescript
function Avatar({ src, alt, size = 40 }: AvatarProps) {
  return <img src={src} alt={alt} width={size} height={size} className="rounded-full" />;
}

function Badge({ text, variant }: BadgeProps) {
  return <span className={`badge badge-${variant}`}>{text}</span>;
}

function UserCard({ user }: UserCardProps) {
  return (
    <div>
      <Avatar src={user.avatar} alt={user.name} />
      <h3>{user.name}</h3>
      {user.isPremium && <Badge text="Premium" variant="gold" />}
    </div>
  );
}
```

### 2.5 Usar Render Props para Lógica Compartida
**✅ HACER:**
```typescript
function DataFetcher<T>({ url, children }: DataFetcherProps<T>) {
  const [data, setData] = useState<T | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetch(url)
      .then(res => res.json())
      .then(data => {
        setData(data);
        setLoading(false);
      });
  }, [url]);

  return children({ data, loading });
}

// Uso
<DataFetcher<User> url="/api/user">
  {({ data: user, loading }) =>
    loading ? <Spinner /> : <UserProfile user={user} />
  }
</DataFetcher>
```

### 2.6 Evitar Props Drilling Excesivo
**✅ HACER (usar Context):**
```typescript
const ThemeContext = createContext<Theme>('light');

function App() {
  const [theme, setTheme] = useState<Theme>('light');

  return (
    <ThemeContext.Provider value={theme}>
      <Layout>
        <Content />
      </Layout>
    </ThemeContext.Provider>
  );
}

function DeepNestedComponent() {
  const theme = useContext(ThemeContext);
  return <div className={theme}>{/* ... */}</div>;
}
```

**❌ EVITAR:**
```typescript
function App() {
  const [theme, setTheme] = useState('light');
  return <Layout theme={theme}><Content theme={theme} /></Layout>;
}

function Layout({ theme, children }: LayoutProps) {
  return <div><Sidebar theme={theme} />{children}</div>;
}

function Sidebar({ theme }: SidebarProps) {
  return <nav><Menu theme={theme} /></nav>;
}

function Menu({ theme }: MenuProps) {
  return <ul className={theme}>{/* ... */}</ul>;
}
```

### 2.7 Usar Controlled Components para Forms
**✅ HACER:**
```typescript
function LoginForm() {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');

  const handleSubmit = (e: FormEvent) => {
    e.preventDefault();
    login(email, password);
  };

  return (
    <form onSubmit={handleSubmit}>
      <input
        type="email"
        value={email}
        onChange={(e) => setEmail(e.target.value)}
      />
      <input
        type="password"
        value={password}
        onChange={(e) => setPassword(e.target.value)}
      />
      <button type="submit">Login</button>
    </form>
  );
}
```

---

## 3. Hooks (8 reglas)

### 3.1 Seguir Reglas de Hooks
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

### 3.2 Usar Custom Hooks para Lógica Reutilizable
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

### 3.3 Optimizar con useMemo y useCallback
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

### 3.4 Limpiar Effects Apropiadamente
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

### 3.5 Usar useReducer para State Complejo
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

### 3.6 Evitar Dependencias Faltantes en useEffect
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

### 3.7 Usar useRef para Valores que No Causan Re-render
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

### 3.8 Nombrar Custom Hooks con 'use' Prefix
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

---

## 4. Performance (6 reglas)

### 4.1 Usar React.memo para Componentes Puros
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

### 4.2 Implementar Code Splitting
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

### 4.3 Optimizar Listas con Virtualización
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

### 4.4 Usar Imágenes Optimizadas
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

### 4.5 Debounce y Throttle Input Handlers
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

### 4.6 Evitar Re-renders Innecesarios
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

---

## 5. TypeScript (6 reglas)

### 5.1 Tipar Props Explícitamente
**✅ HACER:**
```typescript
interface UserCardProps {
  user: {
    id: string;
    name: string;
    email: string;
    avatar?: string;
  };
  onEdit?: (id: string) => void;
  className?: string;
}

function UserCard({ user, onEdit, className }: UserCardProps) {
  return (
    <div className={className}>
      <h3>{user.name}</h3>
      <p>{user.email}</p>
      {onEdit && <button onClick={() => onEdit(user.id)}>Editar</button>}
    </div>
  );
}
```

### 5.2 Usar Type Guards
**✅ HACER:**
```typescript
type SuccessResponse = { status: 'success'; data: User };
type ErrorResponse = { status: 'error'; message: string };
type ApiResponse = SuccessResponse | ErrorResponse;

function isSuccessResponse(response: ApiResponse): response is SuccessResponse {
  return response.status === 'success';
}

function handleResponse(response: ApiResponse) {
  if (isSuccessResponse(response)) {
    console.log(response.data.name); // ✅ TypeScript sabe que es SuccessResponse
  } else {
    console.error(response.message); // ✅ TypeScript sabe que es ErrorResponse
  }
}
```

### 5.3 Usar Generics para Componentes Reutilizables
**✅ HACER:**
```typescript
interface SelectProps<T> {
  options: T[];
  value: T;
  onChange: (value: T) => void;
  getLabel: (option: T) => string;
  getValue: (option: T) => string;
}

function Select<T>({ options, value, onChange, getLabel, getValue }: SelectProps<T>) {
  return (
    <select
      value={getValue(value)}
      onChange={(e) => {
        const selected = options.find(opt => getValue(opt) === e.target.value);
        if (selected) onChange(selected);
      }}
    >
      {options.map(option => (
        <option key={getValue(option)} value={getValue(option)}>
          {getLabel(option)}
        </option>
      ))}
    </select>
  );
}

// Uso
<Select
  options={users}
  value={selectedUser}
  onChange={setSelectedUser}
  getLabel={(user) => user.name}
  getValue={(user) => user.id}
/>
```

### 5.4 Evitar 'any' y Usar 'unknown'
**✅ HACER:**
```typescript
function parseJSON(jsonString: string): unknown {
  return JSON.parse(jsonString);
}

function handleData(data: unknown) {
  if (typeof data === 'object' && data !== null && 'name' in data) {
    const user = data as { name: string };
    console.log(user.name);
  }
}
```

**❌ EVITAR:**
```typescript
function parseJSON(jsonString: string): any { // ❌ any desactiva type checking
  return JSON.parse(jsonString);
}

function handleData(data: any) {
  console.log(data.name); // ❌ Sin validación
}
```

### 5.5 Usar Utility Types
**✅ HACER:**
```typescript
interface User {
  id: string;
  name: string;
  email: string;
  password: string;
  createdAt: Date;
}

// Omitir campos sensibles
type UserPublicData = Omit<User, 'password'>;

// Hacer campos opcionales
type UserUpdateData = Partial<Pick<User, 'name' | 'email'>>;

// Solo lectura
type ReadonlyUser = Readonly<User>;

// Requeridos
type RequiredUser = Required<Partial<User>>;

function updateUser(id: string, data: UserUpdateData): UserPublicData {
  // implementación
  return {} as UserPublicData;
}
```

### 5.6 Tipar Event Handlers
**✅ HACER:**
```typescript
function SearchForm() {
  const handleSubmit = (e: FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    const formData = new FormData(e.currentTarget);
    const query = formData.get('query') as string;
    performSearch(query);
  };

  const handleInputChange = (e: ChangeEvent<HTMLInputElement>) => {
    console.log(e.target.value);
  };

  const handleKeyDown = (e: KeyboardEvent<HTMLInputElement>) => {
    if (e.key === 'Enter') {
      performSearch(e.currentTarget.value);
    }
  };

  return (
    <form onSubmit={handleSubmit}>
      <input onChange={handleInputChange} onKeyDown={handleKeyDown} />
    </form>
  );
}
```

---

## 6. Server Components (Next.js) (8 reglas)

### 6.1 Usar Server Components por Defecto
**✅ HACER:**
```typescript
// app/dashboard/page.tsx - Server Component por defecto
async function DashboardPage() {
  const user = await getCurrentUser();
  const stats = await fetchDashboardStats(user.id);

  return (
    <div>
      <h1>Dashboard de {user.name}</h1>
      <StatsDisplay stats={stats} />
    </div>
  );
}

export default DashboardPage;
```

### 6.2 Marcar Client Components con 'use client'
**✅ HACER:**
```typescript
// components/InteractiveButton.tsx
'use client';

import { useState } from 'react';

export function InteractiveButton() {
  const [count, setCount] = useState(0);

  return (
    <button onClick={() => setCount(count + 1)}>
      Clicks: {count}
    </button>
  );
}
```

### 6.3 Fetch Data en Server Components
**✅ HACER:**
```typescript
// app/posts/page.tsx
async function PostsPage() {
  // Fetch directo en Server Component
  const posts = await db.post.findMany({
    orderBy: { createdAt: 'desc' },
    take: 10,
  });

  return (
    <div>
      <h1>Posts Recientes</h1>
      {posts.map(post => (
        <PostCard key={post.id} post={post} />
      ))}
    </div>
  );
}
```

**❌ EVITAR (en Server Components):**
```typescript
// ❌ No usar useEffect para fetch en Server Components
function PostsPage() {
  const [posts, setPosts] = useState([]);

  useEffect(() => {
    fetch('/api/posts').then(res => res.json()).then(setPosts);
  }, []);

  return <div>{/* ... */}</div>;
}
```

### 6.4 Usar Streaming y Suspense
**✅ HACER:**
```typescript
// app/dashboard/page.tsx
import { Suspense } from 'react';

async function RecentOrders() {
  const orders = await fetchRecentOrders();
  return <OrdersList orders={orders} />;
}

async function Analytics() {
  const data = await fetchAnalytics();
  return <AnalyticsChart data={data} />;
}

export default function Dashboard() {
  return (
    <div>
      <h1>Dashboard</h1>

      <Suspense fallback={<Skeleton />}>
        <RecentOrders />
      </Suspense>

      <Suspense fallback={<ChartSkeleton />}>
        <Analytics />
      </Suspense>
    </div>
  );
}
```

### 6.5 Pasar Solo Datos Serializables a Client Components
**✅ HACER:**
```typescript
// app/user/page.tsx - Server Component
async function UserPage({ params }: { params: { id: string } }) {
  const user = await fetchUser(params.id);

  // Convertir Date a string antes de pasar a Client Component
  const userData = {
    ...user,
    createdAt: user.createdAt.toISOString(),
  };

  return <UserProfile user={userData} />;
}

// components/UserProfile.tsx - Client Component
'use client';

interface UserProfileProps {
  user: {
    name: string;
    email: string;
    createdAt: string; // ✅ String, no Date
  };
}

export function UserProfile({ user }: UserProfileProps) {
  const date = new Date(user.createdAt);
  return <div>Miembro desde: {date.toLocaleDateString()}</div>;
}
```

### 6.6 Usar Server Actions para Mutaciones
**✅ HACER:**
```typescript
// app/actions.ts
'use server';

export async function createPost(formData: FormData) {
  const title = formData.get('title') as string;
  const content = formData.get('content') as string;

  await db.post.create({
    data: { title, content },
  });

  revalidatePath('/posts');
  redirect('/posts');
}

// app/posts/new/page.tsx
import { createPost } from '@/app/actions';

export default function NewPostPage() {
  return (
    <form action={createPost}>
      <input name="title" required />
      <textarea name="content" required />
      <button type="submit">Crear Post</button>
    </form>
  );
}
```

### 6.7 Implementar Loading y Error States
**✅ HACER:**
```typescript
// app/posts/loading.tsx
export default function Loading() {
  return <PostsListSkeleton />;
}

// app/posts/error.tsx
'use client';

export default function Error({ error, reset }: ErrorProps) {
  return (
    <div>
      <h2>Algo salió mal</h2>
      <p>{error.message}</p>
      <button onClick={reset}>Intentar de nuevo</button>
    </div>
  );
}

// app/posts/page.tsx
export default async function PostsPage() {
  const posts = await fetchPosts(); // Si falla, muestra error.tsx
  return <PostsList posts={posts} />;
}
```

### 6.8 Optimizar con Metadata API
**✅ HACER:**
```typescript
// app/posts/[id]/page.tsx
import { Metadata } from 'next';

export async function generateMetadata({ params }: Props): Promise<Metadata> {
  const post = await fetchPost(params.id);

  return {
    title: post.title,
    description: post.excerpt,
    openGraph: {
      title: post.title,
      description: post.excerpt,
      images: [post.coverImage],
    },
  };
}

export default async function PostPage({ params }: Props) {
  const post = await fetchPost(params.id);
  return <PostContent post={post} />;
}
```

---

## 7. State Management (7 reglas)

### 7.1 Minimizar State
**✅ HACER:**
```typescript
function PriceCalculator({ basePrice, taxRate }: PriceCalculatorProps) {
  const [quantity, setQuantity] = useState(1);

  // Derivar valores en lugar de almacenarlos
  const subtotal = basePrice * quantity;
  const tax = subtotal * taxRate;
  const total = subtotal + tax;

  return (
    <div>
      <input
        type="number"
        value={quantity}
        onChange={(e) => setQuantity(Number(e.target.value))}
      />
      <p>Subtotal: ${subtotal}</p>
      <p>Impuesto: ${tax}</p>
      <p>Total: ${total}</p>
    </div>
  );
}
```

**❌ EVITAR:**
```typescript
function PriceCalculator({ basePrice, taxRate }: PriceCalculatorProps) {
  const [quantity, setQuantity] = useState(1);
  const [subtotal, setSubtotal] = useState(basePrice);
  const [tax, setTax] = useState(0);
  const [total, setTotal] = useState(basePrice);

  // ❌ State redundante que necesita sincronización manual
  const handleQuantityChange = (newQuantity: number) => {
    setQuantity(newQuantity);
    const newSubtotal = basePrice * newQuantity;
    setSubtotal(newSubtotal);
    const newTax = newSubtotal * taxRate;
    setTax(newTax);
    setTotal(newSubtotal + newTax);
  };

  return <div>{/* ... */}</div>;
}
```

### 7.2 Colocar State en el Nivel Correcto
**✅ HACER:**
```typescript
// State compartido en componente padre
function ProductPage() {
  const [selectedVariant, setSelectedVariant] = useState('default');

  return (
    <div>
      <VariantSelector
        selected={selectedVariant}
        onChange={setSelectedVariant}
      />
      <ProductImage variant={selectedVariant} />
      <ProductPrice variant={selectedVariant} />
    </div>
  );
}

// State local en componente que lo necesita
function ExpandableSection({ children }: ExpandableSectionProps) {
  const [isExpanded, setIsExpanded] = useState(false);

  return (
    <div>
      <button onClick={() => setIsExpanded(!isExpanded)}>
        {isExpanded ? 'Contraer' : 'Expandir'}
      </button>
      {isExpanded && children}
    </div>
  );
}
```

### 7.3 Usar Context para State Global
**✅ HACER:**
```typescript
// contexts/CartContext.tsx
interface CartContextType {
  items: CartItem[];
  addItem: (item: CartItem) => void;
  removeItem: (id: string) => void;
  clearCart: () => void;
}

const CartContext = createContext<CartContextType | undefined>(undefined);

export function CartProvider({ children }: { children: ReactNode }) {
  const [items, setItems] = useState<CartItem[]>([]);

  const addItem = (item: CartItem) => {
    setItems(prev => [...prev, item]);
  };

  const removeItem = (id: string) => {
    setItems(prev => prev.filter(item => item.id !== id));
  };

  const clearCart = () => {
    setItems([]);
  };

  return (
    <CartContext.Provider value={{ items, addItem, removeItem, clearCart }}>
      {children}
    </CartContext.Provider>
  );
}

export function useCart() {
  const context = useContext(CartContext);
  if (!context) {
    throw new Error('useCart must be used within CartProvider');
  }
  return context;
}
```

### 7.4 Usar Zustand para State Management Complejo
**✅ HACER:**
```typescript
import { create } from 'zustand';

interface UserStore {
  user: User | null;
  isLoading: boolean;
  error: string | null;
  login: (email: string, password: string) => Promise<void>;
  logout: () => void;
}

export const useUserStore = create<UserStore>((set) => ({
  user: null,
  isLoading: false,
  error: null,

  login: async (email, password) => {
    set({ isLoading: true, error: null });
    try {
      const user = await signIn(email, password);
      set({ user, isLoading: false });
    } catch (error) {
      set({ error: error.message, isLoading: false });
    }
  },

  logout: () => {
    signOut();
    set({ user: null });
  },
}));

// Uso
function Header() {
  const { user, logout } = useUserStore();
  return <nav>{user && <button onClick={logout}>Salir</button>}</nav>;
}
```

### 7.5 Separar UI State de Server State
**✅ HACER:**
```typescript
// UI State con useState
function ProductModal() {
  const [isOpen, setIsOpen] = useState(false);
  const [activeTab, setActiveTab] = useState('details');

  // Server State con TanStack Query
  const { data: product, isLoading } = useQuery({
    queryKey: ['product', productId],
    queryFn: () => fetchProduct(productId),
  });

  return (
    <Modal open={isOpen} onClose={() => setIsOpen(false)}>
      {isLoading ? <Spinner /> : <ProductDetails product={product} />}
    </Modal>
  );
}
```

### 7.6 Usar TanStack Query para Server State
**✅ HACER:**
```typescript
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';

function UserProfile({ userId }: UserProfileProps) {
  const queryClient = useQueryClient();

  // Fetch data
  const { data: user, isLoading, error } = useQuery({
    queryKey: ['user', userId],
    queryFn: () => fetchUser(userId),
    staleTime: 5 * 60 * 1000, // 5 minutos
  });

  // Mutation
  const updateMutation = useMutation({
    mutationFn: (data: UpdateUserData) => updateUser(userId, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['user', userId] });
    },
  });

  if (isLoading) return <Spinner />;
  if (error) return <ErrorMessage error={error} />;

  return (
    <div>
      <h1>{user.name}</h1>
      <button onClick={() => updateMutation.mutate({ name: 'New Name' })}>
        Actualizar
      </button>
    </div>
  );
}
```

### 7.7 Evitar Prop Drilling con Composition
**✅ HACER:**
```typescript
function Dashboard() {
  const [selectedDate, setSelectedDate] = useState(new Date());

  return (
    <DashboardLayout
      header={<DatePicker value={selectedDate} onChange={setSelectedDate} />}
      sidebar={<FilterPanel />}
      main={<Analytics date={selectedDate} />}
    />
  );
}

function DashboardLayout({ header, sidebar, main }: DashboardLayoutProps) {
  return (
    <div>
      <header>{header}</header>
      <aside>{sidebar}</aside>
      <main>{main}</main>
    </div>
  );
}
```

---

## 8. Testing (5 reglas)

### 8.1 Escribir Tests Centrados en Comportamiento
**✅ HACER:**
```typescript
import { render, screen, fireEvent } from '@testing-library/react';
import { LoginForm } from './LoginForm';

describe('LoginForm', () => {
  it('permite al usuario iniciar sesión con credenciales válidas', async () => {
    const handleLogin = jest.fn();
    render(<LoginForm onLogin={handleLogin} />);

    // Usuario ingresa email
    const emailInput = screen.getByLabelText(/email/i);
    fireEvent.change(emailInput, { target: { value: 'user@example.com' } });

    // Usuario ingresa password
    const passwordInput = screen.getByLabelText(/contraseña/i);
    fireEvent.change(passwordInput, { target: { value: 'password123' } });

    // Usuario hace click en submit
    const submitButton = screen.getByRole('button', { name: /iniciar sesión/i });
    fireEvent.click(submitButton);

    // Verifica que se llamó la función con los datos correctos
    expect(handleLogin).toHaveBeenCalledWith({
      email: 'user@example.com',
      password: 'password123',
    });
  });
});
```

### 8.2 Usar Testing Library Queries Apropiadas
**✅ HACER (orden de prioridad):**
```typescript
// 1. Accesible para todos (mejor)
screen.getByRole('button', { name: /submit/i });
screen.getByLabelText(/email/i);
screen.getByPlaceholderText(/enter email/i);

// 2. Queries semánticas
screen.getByAltText(/profile picture/i);
screen.getByTitle(/close/i);

// 3. Test IDs (último recurso)
screen.getByTestId('custom-element');
```

**❌ EVITAR:**
```typescript
// ❌ Queries frágiles
screen.getByClassName('submit-button');
container.querySelector('.email-input');
```

### 8.3 Mockear Dependencias Externas
**✅ HACER:**
```typescript
import { render, screen, waitFor } from '@testing-library/react';
import { UserProfile } from './UserProfile';
import * as api from '@/lib/api';

// Mock del módulo API
jest.mock('@/lib/api');
const mockedApi = api as jest.Mocked<typeof api>;

describe('UserProfile', () => {
  it('muestra datos del usuario después de cargar', async () => {
    // Setup mock
    mockedApi.fetchUser.mockResolvedValue({
      id: '1',
      name: 'John Doe',
      email: 'john@example.com',
    });

    render(<UserProfile userId="1" />);

    // Esperar a que se carguen los datos
    await waitFor(() => {
      expect(screen.getByText('John Doe')).toBeInTheDocument();
    });

    expect(screen.getByText('john@example.com')).toBeInTheDocument();
  });

  it('muestra error cuando falla la carga', async () => {
    mockedApi.fetchUser.mockRejectedValue(new Error('Network error'));

    render(<UserProfile userId="1" />);

    await waitFor(() => {
      expect(screen.getByText(/error/i)).toBeInTheDocument();
    });
  });
});
```

### 8.4 Test de Accesibilidad
**✅ HACER:**
```typescript
import { render } from '@testing-library/react';
import { axe, toHaveNoViolations } from 'jest-axe';
import { LoginForm } from './LoginForm';

expect.extend(toHaveNoViolations);

describe('LoginForm Accessibility', () => {
  it('no debe tener violaciones de accesibilidad', async () => {
    const { container } = render(<LoginForm />);
    const results = await axe(container);
    expect(results).toHaveNoViolations();
  });

  it('debe tener labels apropiados', () => {
    render(<LoginForm />);

    expect(screen.getByLabelText(/email/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/contraseña/i)).toBeInTheDocument();
  });

  it('debe ser navegable con teclado', () => {
    render(<LoginForm />);

    const emailInput = screen.getByLabelText(/email/i);
    const passwordInput = screen.getByLabelText(/contraseña/i);
    const submitButton = screen.getByRole('button', { name: /iniciar sesión/i });

    // Verificar orden de tabulación
    emailInput.focus();
    expect(document.activeElement).toBe(emailInput);

    userEvent.tab();
    expect(document.activeElement).toBe(passwordInput);

    userEvent.tab();
    expect(document.activeElement).toBe(submitButton);
  });
});
```

### 8.5 Usar MSW para Mock de Requests
**✅ HACER:**
```typescript
import { rest } from 'msw';
import { setupServer } from 'msw/node';
import { render, screen, waitFor } from '@testing-library/react';
import { UserList } from './UserList';

// Setup MSW server
const server = setupServer(
  rest.get('/api/users', (req, res, ctx) => {
    return res(
      ctx.json([
        { id: '1', name: 'John Doe' },
        { id: '2', name: 'Jane Smith' },
      ])
    );
  })
);

beforeAll(() => server.listen());
afterEach(() => server.resetHandlers());
afterAll(() => server.close());

describe('UserList', () => {
  it('carga y muestra usuarios', async () => {
    render(<UserList />);

    await waitFor(() => {
      expect(screen.getByText('John Doe')).toBeInTheDocument();
      expect(screen.getByText('Jane Smith')).toBeInTheDocument();
    });
  });

  it('maneja errores de red', async () => {
    // Override del handler para este test
    server.use(
      rest.get('/api/users', (req, res, ctx) => {
        return res(ctx.status(500));
      })
    );

    render(<UserList />);

    await waitFor(() => {
      expect(screen.getByText(/error al cargar usuarios/i)).toBeInTheDocument();
    });
  });
});
```

---

## Quick Reference - Cheatsheet

### Estructura de Componentes
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

### Custom Hooks Pattern
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

### Server Component Pattern (Next.js)
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

### Testing Pattern
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

---

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

---

**Versión**: 1.0.0
**Última actualización**: 2026-01-25
**Fuente**: Vercel Labs React Best Practices (adaptado)
