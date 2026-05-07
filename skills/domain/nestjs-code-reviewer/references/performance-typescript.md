# Performance, TypeScript Quality & Testing — NestJS Reference

Detailed code samples for the performance, TypeScript and testing portions of the review checklist.

## 4. Performance

### Database Connections

- ✅ Usar connection pooling (default en TypeORM)
- ❌ No abrir conexiones manualmente sin cerrarlas
- ✅ Configurar `max` y `idleTimeoutMillis` en producción

### Caching

```typescript
// ✅ BIEN: Cache para datos estáticos
@Injectable()
export class ProductService {
  @Cacheable({ ttl: 300 })
  async findAll() { ... }
}
```

### Pagination

```typescript
// ❌ MAL: Sin paginación
async findAll() {
  return this.repo.find(); // Puede retornar millones
}

// ✅ BIEN: Paginación obligatoria
async findAll(page: number, limit: number) {
  return this.repo.find({
    skip: (page - 1) * limit,
    take: Math.min(limit, 100) // Max 100
  });
}
```

---

## 5. TypeScript Quality

### Tipos estrictos

- ❌ No usar `any` (excepto en casos extremos)
- ✅ Usar `unknown` para tipos desconocidos
- ✅ Habilitar `strict: true` en tsconfig.json

### Error Handling

```typescript
// ❌ MAL: Errores genéricos
throw new Error('Something failed');

// ✅ BIEN: Excepciones de NestJS
throw new NotFoundException(`User #${id} not found`);
throw new BadRequestException('Invalid email format');
```

### Async/Await

- ✅ Siempre usar try/catch en async functions
- ✅ No olvidar `await` (puede causar bugs silenciosos)
- ❌ No mezclar callbacks con promises

---

## 6. Testing

### Cobertura mínima

- ✅ Unit tests para servicios críticos (>80% coverage)
- ✅ Integration tests para endpoints
- ✅ E2E tests para flujos principales

### Mocks

```typescript
// ✅ BIEN: Mock de dependencias
const mockRepository = {
  find: jest.fn().mockResolvedValue([]),
  save: jest.fn()
};
```
