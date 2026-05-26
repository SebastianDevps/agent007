# Versionado de API

**Estrategia recomendada**: Versionado por URL.

```typescript
// main.ts
async function bootstrap() {
  const app = await NestFactory.create(AppModule);

  // Habilitar versionado global
  app.setGlobalPrefix('api/v1');

  await app.listen(3000);
}

// Estructura de módulos
src/
├── modules/
│   ├── cutoffs/
│   │   └── v1/
│   │       ├── cutoffs.controller.ts     // /api/v1/cutoffs
│   │       ├── cutoffs.service.ts
│   │       └── dto/
│   └── providers/
│       └── v1/
│           └── providers.controller.ts   // /api/v1/providers

// Para versiones futuras
src/modules/cutoffs/v2/cutoffs.controller.ts  // /api/v2/cutoffs
```

## Deprecación de versiones

```typescript
@Controller('cutoffs')
@ApiTags('Cutoffs (v1) - DEPRECATED')
@ApiHeader({
  name: 'X-API-Version',
  description: 'Esta versión será descontinuada el 2026-06-01. Migrar a v2.'
})
export class CutoffsV1Controller {
  // Implementación legacy
}
```
