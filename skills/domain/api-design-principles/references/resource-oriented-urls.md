# Arquitectura Orientada a Recursos

## Reglas

- URLs representan RECURSOS (sustantivos), no acciones (verbos)
- Usar nombres en plural: `/users`, `/cutoffs`, `/providers`
- Jerarquías para relaciones: `/cutoffs/:id/charges`
- Evitar verbos en URLs

## Ejemplos

```typescript
// Correcto
GET    /api/v1/cutoffs              // Listar cortes
GET    /api/v1/cutoffs/:id          // Obtener corte específico
POST   /api/v1/cutoffs              // Crear corte
PATCH  /api/v1/cutoffs/:id          // Actualizar corte
DELETE /api/v1/cutoffs/:id          // Eliminar corte

// Relaciones anidadas
GET    /api/v1/cutoffs/:id/charges  // Cargos de un corte específico

// Incorrecto
POST   /api/v1/createCutoff
GET    /api/v1/getCutoffById/:id
POST   /api/v1/cutoffs/delete/:id
```
