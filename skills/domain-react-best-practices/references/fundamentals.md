---
title: React Fundamentals
parent: react-best-practices
rules: 10
---

# React Fundamentals (10 reglas)

## 1.1 Usar Functional Components
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

## 1.2 Mantener Componentes Puros
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

## 1.3 Usar Keys Estables en Listas
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

## 1.4 Evitar Mutación Directa de State
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

## 1.5 Usar Fragment para Múltiples Elementos
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

## 1.6 Usar Conditional Rendering Apropiado
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

## 1.7 Evitar Lógica Compleja en JSX
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

## 1.8 Usar PropTypes o TypeScript
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

## 1.9 Separar Concerns (UI vs Lógica)
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

## 1.10 Usar Children Prop Apropiadamente
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
