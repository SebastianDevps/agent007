---
title: Testing
parent: react-best-practices
rules: 5
---

# Testing (5 reglas)

## 8.1 Escribir Tests Centrados en Comportamiento
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

## 8.2 Usar Testing Library Queries Apropiadas
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

## 8.3 Mockear Dependencias Externas
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

## 8.4 Test de Accesibilidad
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

## 8.5 Usar MSW para Mock de Requests
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
