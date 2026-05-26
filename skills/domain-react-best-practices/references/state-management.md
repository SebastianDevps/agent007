---
title: State Management
parent: react-best-practices
rules: 7
---

# State Management (7 reglas)

## 7.1 Minimizar State
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

## 7.2 Colocar State en el Nivel Correcto
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

## 7.3 Usar Context para State Global
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

## 7.4 Usar Zustand para State Management Complejo
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

## 7.5 Separar UI State de Server State
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

## 7.6 Usar TanStack Query para Server State
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

## 7.7 Evitar Prop Drilling con Composition
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
