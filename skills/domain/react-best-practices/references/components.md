---
title: Components
parent: react-best-practices
rules: 7
---

# Components (7 reglas)

## 2.1 Un Componente por Archivo
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

## 2.2 Nombrar Componentes Descriptivamente
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

## 2.3 Usar Composición sobre Herencia
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

## 2.4 Extraer Componentes Pequeños y Reutilizables
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

## 2.5 Usar Render Props para Lógica Compartida
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

## 2.6 Evitar Props Drilling Excesivo
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

## 2.7 Usar Controlled Components para Forms
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
