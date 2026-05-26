# Architecture Patterns - Quick Reference

> **Full details**: See SKILL.md for complete examples and implementation guides

## Core Principles

### Clean Architecture (4 Capas)
```
Presentation → Application → Domain → Infrastructure
```
- Dependencies flow INWARD (toward domain)
- Domain layer has NO external dependencies

### Bounded Contexts
- **Same context**: Direct imports OK
- **Cross-context**: Communicate via events (EventEmitter2)
- **Shared**: Only for infrastructure (database, email, cache)

## Module Structure Template

```
modules/{context}/{module}/
├── {module}.module.ts
├── {module}.controller.ts
├── {module}.service.ts
├── entities/
│   └── {entity}.entity.ts
├── dto/
│   ├── create-{entity}.dto.ts
│   └── update-{entity}.dto.ts
├── types/
│   └── {entity}-response.type.ts
└── interfaces/
    └── {entity}-repository.interface.ts
```

## Quick Checklist

**Architecture**:
- [ ] Módulo < 450 líneas por archivo
- [ ] DTOs separados de Types separados de Interfaces
- [ ] Repository pattern implementado
- [ ] Lógica de negocio en entidades (DDD)
- [ ] Comunicación cross-context vía eventos

**DTOs vs Types vs Interfaces**:
- **DTOs**: Validación de entrada (class-validator)
- **Types**: Respuestas de API (patrón `{status, message, data}`)
- **Interfaces**: Contratos de servicios

**Domain Events** (cross-context):
```typescript
// Emisión
this.eventEmitter.emit('cutoff.closed', event);

// Suscripción
@OnEvent('cutoff.closed')
async handleCutoffClosed(event) { }
```

## Bounded Context Examples

**5 Contexts Típicos**:
1. `payroll-context` - Nómina
2. `provider-context` - Proveedores
3. `financial-context` - Finanzas
4. `audit-context` - Auditoría
5. `organizational-context` - Organizacional

## Key Patterns

**Repository Pattern**:
```typescript
interface IUserRepository {
  findById(id): Promise<User | null>;
  save(user): Promise<User>;
}
```

**Value Objects** (immutable, no identity):
```typescript
class Money {
  constructor(
    public readonly amount: number,
    public readonly currency: string = 'COP'
  ) {}
}
```

**Aggregates** (cluster with root):
```typescript
@Entity()
class Cutoff {  // Aggregate Root
  @OneToMany(() => CutoffCharge)
  charges: CutoffCharge[];

  // Domain logic
  canBeClosed(): boolean { }
  close(): void { }
}
```

---

Ver SKILL.md para ejemplos completos de código y workflows de refactorización.
