# Clean Architecture - Capas

```
┌─────────────────────────────────────────┐
│        Presentation Layer               │
│  (Controllers, DTOs, Guards, Filters)   │
├─────────────────────────────────────────┤
│        Application Layer                │
│     (Services, Use Cases, Types)        │
├─────────────────────────────────────────┤
│          Domain Layer                   │
│  (Entities, Value Objects, Interfaces)  │
├─────────────────────────────────────────┤
│      Infrastructure Layer               │
│   (TypeORM Repositories, External APIs) │
└─────────────────────────────────────────┘
```

**Regla de dependencias**: Las dependencias SIEMPRE apuntan hacia adentro (hacia el dominio).

- Domain layer no depende de NADA externo (ni framework, ni ORM, ni infraestructura).
- Application layer depende del Domain.
- Infrastructure implementa interfaces del Domain (repositorios concretos).
- Presentation invoca Application (servicios/casos de uso).
