# Workflow de Refactorización

Cuando se invoque este skill para refactorizar un módulo:

## 1. Analizar módulo actual

```bash
src/modules/$ARGUMENTS/
```

## 2. Identificar bounded context

- ¿A qué dominio pertenece? (payroll, provider, financial, audit, organizational)
- ¿Qué otros módulos están relacionados?

## 3. Verificar checklist

- [ ] Módulo < 450 líneas (cada archivo)
- [ ] Separación correcta: DTOs vs Types vs Interfaces
- [ ] Inyección de dependencias (no instanciación manual)
- [ ] Lógica de negocio en entidades (DDD)
- [ ] Comunicación cross-context vía eventos
- [ ] Repository pattern implementado
- [ ] Value objects para conceptos de dominio

## 4. Proponer estructura mejorada

```typescript
src/modules/{bounded-context}/{módulo}/
├── {módulo}.module.ts
├── {módulo}.controller.ts
├── {módulo}.service.ts
├── entities/
│   ├── {entity}.entity.ts
│   └── index.ts
├── dto/
│   ├── create-{entity}.dto.ts
│   └── index.ts
├── types/
│   ├── {entity}-response.type.ts
│   └── index.ts
└── interfaces/
    └── {entity}-repository.interface.ts
```

## 5. Implementar refactorización

- Mover archivos a bounded context apropiado
- Dividir archivos >450 líneas
- Extraer value objects
- Implementar domain events si hay cross-context

## Comandos de Uso

```bash
# Auditar módulo existente
/architecture-patterns audit:cutoffs

# Refactorizar módulo grande
/architecture-patterns refactor:providers

# Definir bounded contexts
/architecture-patterns define-contexts

# Migrar a Clean Architecture
/architecture-patterns migrate:cutoffs
```
