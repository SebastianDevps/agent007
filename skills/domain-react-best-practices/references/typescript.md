---
title: TypeScript with React
parent: react-best-practices
rules: 6
---

# TypeScript (6 reglas)

## 5.1 Tipar Props Explícitamente
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

## 5.2 Usar Type Guards
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

## 5.3 Usar Generics para Componentes Reutilizables
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

## 5.4 Evitar 'any' y Usar 'unknown'
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

## 5.5 Usar Utility Types
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

## 5.6 Tipar Event Handlers
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
