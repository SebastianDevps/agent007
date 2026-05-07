# Semántica HTTP

## Métodos HTTP

| Método | Uso | Idempotente | Body Request | Body Response |
|--------|-----|-------------|--------------|---------------|
| GET | Obtener recursos | Sí | No | Sí |
| POST | Crear recurso | No | Sí | Sí |
| PUT | Reemplazar completo | Sí | Sí | Sí |
| PATCH | Actualización parcial | No | Sí | Sí |
| DELETE | Eliminar recurso | Sí | Opcional | Opcional |

## Status Codes Estándar

```typescript
// Éxito
200 OK              // GET, PATCH, DELETE exitoso
201 Created         // POST exitoso (nuevo recurso)
204 No Content      // DELETE exitoso sin body

// Errores del Cliente
400 Bad Request     // Validación falló
401 Unauthorized    // No autenticado
403 Forbidden       // Autenticado pero sin permisos
404 Not Found       // Recurso no existe
409 Conflict        // Email duplicado, estado inválido

// Errores del Servidor
500 Internal Server Error  // Error inesperado
503 Service Unavailable    // Servicio temporalmente caído
```
