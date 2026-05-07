# Workflow de Auditoría

Cuando se invoque este skill para auditar un módulo existente:

## 1. Leer estructura del módulo

```bash
src/modules/$ARGUMENTS/
├── *.controller.ts
├── *.service.ts
├── dto/
└── types/
```

## 2. Verificar checklist

- [ ] URLs siguen convención de recursos (sustantivos plurales)
- [ ] Métodos HTTP correctos (GET/POST/PATCH/DELETE)
- [ ] Status codes apropiados (200, 201, 400, 404, etc.)
- [ ] Paginación implementada en listados
- [ ] Filtrado y ordenamiento disponibles
- [ ] Versionado de API (/api/v1/)
- [ ] DTOs con validaciones completas
- [ ] Manejo de errores consistente
- [ ] Documentación Swagger completa
- [ ] Responses siguen patrón `{ status, message, data }`

## 3. Generar reporte

```markdown
# Auditoría de API: $ARGUMENTS

## Cumple
- Paginación implementada
- DTOs con validaciones

## Mejoras Necesarias
- Falta versionado /api/v1/
- Documentación Swagger incompleta
- No hay filtrado por fecha

## Acciones Recomendadas
1. Añadir prefix global en main.ts
2. Completar decoradores @ApiResponse
3. Implementar FilterDto con fechas
```

## Comandos de Uso

```bash
# Auditar módulo existente
/api-design-principles cutoffs

# Implementar nuevo endpoint
/api-design-principles new:providers-assignments

# Revisar endpoints globales
/api-design-principles audit:all
```
