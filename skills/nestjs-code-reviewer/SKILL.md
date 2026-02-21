---
name: nestjs-code-reviewer
version: 1.0.0
description: Revisa código NestJS + TypeORM siguiendo mejores prácticas, detecta vulnerabilidades OWASP y anti-patterns
license: MIT
metadata:
  author: DevPartners
  stack: NestJS, TypeORM, PostgreSQL, TypeScript
  categories: [code-review, quality-assurance, security]
allowed-tools: Read Grep Bash(npm:*) Bash(tsc:*)
---

# NestJS Code Reviewer

Skill especializado para revisar código de aplicaciones NestJS con TypeORM y PostgreSQL, enfocado en calidad, seguridad y arquitectura.

## 🎯 When to Use This Skill

Activa este skill cuando el usuario:
- Pida "revisar código", "code review", "auditar"
- Mencione "mejores prácticas", "clean code", "refactorizar"
- Pregunte "¿está bien este código?", "¿hay bugs?"
- Solicite validación de seguridad o performance

## 📋 Review Checklist

### 1. Arquitectura NestJS

**Controllers**:
```typescript
// ❌ MAL: Lógica de negocio en controlador
@Post()
async create(@Body() dto: CreateUserDto) {
  const user = await this.userRepository.save(dto);
  await this.emailService.send(user.email);
  return user;
}

// ✅ BIEN: Delegar a servicios
@Post()
async create(@Body() dto: CreateUserDto) {
  return this.userService.create(dto);
}
```

**Validaciones**:
- ✅ Todos los DTOs deben usar `class-validator` decorators
- ✅ Usar `ValidationPipe` global con `whitelist: true`
- ❌ No validar manualmente con if/else en controladores

**Inyección de Dependencias**:
- ✅ Usar constructor injection, no property injection
- ✅ Inyectar interfaces/abstracciones, no implementaciones concretas
- ❌ No usar `@Inject()` a menos que sea necesario (circular deps)

---

### 2. TypeORM Best Practices

**Queries N+1**:
```typescript
// ❌ MAL: N+1 queries
const users = await this.userRepository.find();
for (const user of users) {
  user.orders = await this.orderRepository.find({ userId: user.id });
}

// ✅ BIEN: Eager loading con relations
const users = await this.userRepository.find({
  relations: ['orders']
});
```

**Transacciones**:
```typescript
// ❌ MAL: Sin transacción en operaciones múltiples
await this.userRepository.save(user);
await this.profileRepository.save(profile);

// ✅ BIEN: Usar transacciones
await this.dataSource.transaction(async (manager) => {
  await manager.save(User, user);
  await manager.save(Profile, profile);
});
```

**Índices**:
- ✅ Columnas con `@Index()` en campos de búsqueda frecuente
- ✅ `@Unique()` para constraints de unicidad
- ❌ No crear índices en columnas booleanas o de baja cardinalidad

**Repository Patterns**:
- ✅ Usar custom repositories para queries complejas
- ❌ No escribir SQL crudo a menos que sea absolutamente necesario
- ✅ Preferir QueryBuilder para queries dinámicas

---

### 3. Seguridad (OWASP Top 10)

**SQL Injection** (A03:2021):
```typescript
// ❌ CRÍTICO: SQL injection
await this.repo.query(`SELECT * FROM users WHERE id = ${userId}`);

// ✅ SEGURO: Parámetros preparados
await this.repo.query('SELECT * FROM users WHERE id = $1', [userId]);
```

**Auth & AuthZ** (A01:2021):
```typescript
// ❌ MAL: Sin guards
@Delete(':id')
async delete(@Param('id') id: string) { ... }

// ✅ BIEN: Guards + validación de ownership
@UseGuards(JwtAuthGuard, OwnershipGuard)
@Delete(':id')
async delete(@Param('id') id: string, @CurrentUser() user: User) { ... }
```

**Sensitive Data Exposure** (A02:2021):
- ❌ No retornar passwords en respuestas (usar `@Exclude()` en entities)
- ✅ Usar bcrypt/argon2 para hash (min 10 rounds)
- ✅ Variables sensibles en `.env`, nunca hardcodeadas

**Mass Assignment**:
```typescript
// ❌ VULNERABLE: Acepta cualquier campo
@Post()
create(@Body() data: any) {
  return this.repo.save(data); // Puede modificar "isAdmin"
}

// ✅ SEGURO: DTO estricto + whitelist
@Post()
create(@Body() dto: CreateUserDto) { // Solo campos permitidos
  return this.service.create(dto);
}
```

---

### 4. Performance

**Database Connections**:
- ✅ Usar connection pooling (default en TypeORM)
- ❌ No abrir conexiones manualmente sin cerrarlas
- ✅ Configurar `max` y `idleTimeoutMillis` en producción

**Caching**:
```typescript
// ✅ BIEN: Cache para datos estáticos
@Injectable()
export class ProductService {
  @Cacheable({ ttl: 300 })
  async findAll() { ... }
}
```

**Pagination**:
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

### 5. TypeScript Quality

**Tipos estrictos**:
- ❌ No usar `any` (excepto en casos extremos)
- ✅ Usar `unknown` para tipos desconocidos
- ✅ Habilitar `strict: true` en tsconfig.json

**Error Handling**:
```typescript
// ❌ MAL: Errores genéricos
throw new Error('Something failed');

// ✅ BIEN: Excepciones de NestJS
throw new NotFoundException(`User #${id} not found`);
throw new BadRequestException('Invalid email format');
```

**Async/Await**:
- ✅ Siempre usar try/catch en async functions
- ✅ No olvidar `await` (puede causar bugs silenciosos)
- ❌ No mezclar callbacks con promises

---

### 6. Testing

**Cobertura mínima**:
- ✅ Unit tests para servicios críticos (>80% coverage)
- ✅ Integration tests para endpoints
- ✅ E2E tests para flujos principales

**Mocks**:
```typescript
// ✅ BIEN: Mock de dependencias
const mockRepository = {
  find: jest.fn().mockResolvedValue([]),
  save: jest.fn()
};
```

---

## 🔍 Cómo Usar Este Skill

### Paso 1: Identificar archivos a revisar
```bash
# Buscar archivos relevantes
grep -r "class.*Controller" src/
grep -r "class.*Service" src/
grep -r "@Entity" src/
```

### Paso 2: Leer código y aplicar checklist
- Lee cada archivo con `Read tool`
- Compara contra los patrones de arriba
- Identifica violaciones (❌) y buenas prácticas (✅)

### Paso 3: Generar reporte
```markdown
## 🔴 CRÍTICO (fix inmediato)
- `src/users/users.controller.ts:42` - SQL Injection vulnerable
- `src/auth/auth.service.ts:15` - Password sin hash

## 🟡 MEJORAS (refactor recomendado)
- `src/products/products.service.ts:28` - Query N+1
- `src/orders/orders.controller.ts:12` - Lógica de negocio en controller

## ✅ BUENAS PRÁCTICAS DETECTADAS
- Uso correcto de DTOs con validación
- Transacciones en operaciones críticas
```

### Paso 4: Sugerir código mejorado
Para cada issue, provee un snippet corregido usando el formato:
```typescript
// Archivo: src/path/to/file.ts:línea

// ❌ ANTES
[código problemático]

// ✅ DESPUÉS
[código corregido]

// 📝 RAZÓN
[explicación breve]
```

---

## 📚 Referencias Adicionales

Para análisis profundo, consulta:
- `references/NESTJS_PATTERNS.md` - Patrones arquitectónicos avanzados
- `references/TYPEORM_ANTIPATTERNS.md` - Anti-patterns comunes TypeORM
- `references/SECURITY_CHECKLIST.md` - Checklist completo OWASP

---

## 🚫 Limitaciones

Este skill NO cubre:
- Performance profiling (usa Clinic.js o 0x)
- Dependency vulnerabilities (usa `npm audit`)
- Infrastructure/DevOps (usa otro skill)

---

## 🎯 Output Format

```markdown
# Code Review: [Módulo/Feature]

## 📊 Resumen
- Archivos revisados: X
- Issues críticos: Y
- Mejoras sugeridas: Z
- Score de calidad: A/B/C

## 🔴 Issues Críticos
[lista con file:line]

## 🟡 Mejoras Recomendadas
[lista con file:line]

## ✅ Aspectos Positivos
[buenas prácticas encontradas]

## 📝 Sugerencias de Refactor
[código antes/después]
```

---

## 💡 Tips para el Agente

1. **Prioriza seguridad**: Issues OWASP son críticos
2. **Sé específico**: Siempre menciona `file:line`
3. **Da contexto**: Explica el "por qué", no solo el "qué"
4. **Sugiere, no impongas**: Usa "considera..." en lugar de "debes..."
5. **Limita scope**: Si hay >10 files, pide al usuario enfocarse en un módulo
