# NestJS Architecture Patterns — Reference

Detailed code samples for the architecture portion of the NestJS review checklist.

## 1. Arquitectura NestJS

### Controllers — delegar lógica de negocio

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

### Validaciones

- ✅ Todos los DTOs deben usar `class-validator` decorators
- ✅ Usar `ValidationPipe` global con `whitelist: true`
- ❌ No validar manualmente con if/else en controladores

### Inyección de Dependencias

- ✅ Usar constructor injection, no property injection
- ✅ Inyectar interfaces/abstracciones, no implementaciones concretas
- ❌ No usar `@Inject()` a menos que sea necesario (circular deps)

---

## 2. TypeORM Best Practices

### Queries N+1

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

### Transacciones

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

### Índices

- ✅ Columnas con `@Index()` en campos de búsqueda frecuente
- ✅ `@Unique()` para constraints de unicidad
- ❌ No crear índices en columnas booleanas o de baja cardinalidad

### Repository Patterns

- ✅ Usar custom repositories para queries complejas
- ❌ No escribir SQL crudo a menos que sea absolutamente necesario
- ✅ Preferir QueryBuilder para queries dinámicas
