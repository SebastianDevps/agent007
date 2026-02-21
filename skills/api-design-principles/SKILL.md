---
name: api-design-principles
version: 1.0.0
description: Diseñar y auditar APIs REST siguiendo mejores prácticas para NestJS con TypeORM
argument-hint: [módulo o endpoint a revisar]
user-invocable: true
allowed-tools: Read, Grep, Glob, Edit, Write
model: sonnet
---

# API Design Principles - NestJS & TypeORM

Skill para diseñar, implementar y auditar APIs REST siguiendo mejores prácticas en NestJS.

## Principios Fundamentales

### 1. Arquitectura Orientada a Recursos

**Reglas**:
- URLs representan RECURSOS (sustantivos), no acciones (verbos)
- Usar nombres en plural: `/users`, `/cutoffs`, `/providers`
- Jerarquías para relaciones: `/cutoffs/:id/charges`
- Evitar verbos en URLs: ❌ `/getUser`, ✅ `/users/:id`

**Ejemplos**:
```typescript
// ✅ Correcto
GET    /api/v1/cutoffs              // Listar cortes
GET    /api/v1/cutoffs/:id          // Obtener corte específico
POST   /api/v1/cutoffs              // Crear corte
PATCH  /api/v1/cutoffs/:id          // Actualizar corte
DELETE /api/v1/cutoffs/:id          // Eliminar corte

// Relaciones anidadas
GET    /api/v1/cutoffs/:id/charges  // Cargos de un corte específico

// ❌ Incorrecto
POST   /api/v1/createCutoff
GET    /api/v1/getCutoffById/:id
POST   /api/v1/cutoffs/delete/:id
```

---

### 2. Semántica HTTP

**Métodos HTTP**:
| Método | Uso | Idempotente | Body Request | Body Response |
|--------|-----|-------------|--------------|---------------|
| GET | Obtener recursos | ✅ Sí | No | Sí |
| POST | Crear recurso | ❌ No | Sí | Sí |
| PUT | Reemplazar completo | ✅ Sí | Sí | Sí |
| PATCH | Actualización parcial | ❌ No | Sí | Sí |
| DELETE | Eliminar recurso | ✅ Sí | Opcional | Opcional |

**Status Codes Estándar**:
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

---

### 3. Paginación Estándar

**Implementación obligatoria para listados**:

```typescript
// dto/pagination.dto.ts
import { Type } from 'class-transformer';
import { IsInt, IsOptional, Min, Max } from 'class-validator';
import { ApiPropertyOptional } from '@nestjs/swagger';

export class PaginationDto {
  @ApiPropertyOptional({
    description: 'Número de página (inicia en 1)',
    example: 1,
    minimum: 1,
    default: 1
  })
  @IsOptional()
  @Type(() => Number)
  @IsInt({ message: 'La página debe ser un número entero' })
  @Min(1, { message: 'La página debe ser mayor o igual a 1' })
  page?: number = 1;

  @ApiPropertyOptional({
    description: 'Cantidad de elementos por página',
    example: 10,
    minimum: 1,
    maximum: 100,
    default: 10
  })
  @IsOptional()
  @Type(() => Number)
  @IsInt({ message: 'El límite debe ser un número entero' })
  @Min(1, { message: 'El límite debe ser mayor o igual a 1' })
  @Max(100, { message: 'El límite no puede exceder 100 elementos' })
  limit?: number = 10;
}

// types/paginated-response.type.ts
export type PaginatedResponse<T> = {
  status: 200;
  message: string;
  data: T[];
  meta: {
    page: number;
    limit: number;
    total: number;
    totalPages: number;
    hasNextPage: boolean;
    hasPreviousPage: boolean;
  };
};

// Servicio
@Injectable()
export class CutoffsService {
  async findAll(paginationDto: PaginationDto): Promise<PaginatedResponse<CutoffData>> {
    const { page, limit } = paginationDto;
    const skip = (page - 1) * limit;

    const [cutoffs, total] = await this.cutoffRepository.findAndCount({
      skip,
      take: limit,
      order: { createdAt: 'DESC' }
    });

    const totalPages = Math.ceil(total / limit);

    return {
      status: 200,
      message: 'Cortes obtenidos exitosamente',
      data: cutoffs.map(c => this.mapToData(c)),
      meta: {
        page,
        limit,
        total,
        totalPages,
        hasNextPage: page < totalPages,
        hasPreviousPage: page > 1
      }
    };
  }
}

// Controlador
@Get()
@ApiOperation({ summary: 'Listar cortes paginados' })
@ApiQuery({ type: PaginationDto })
async findAll(@Query() paginationDto: PaginationDto): Promise<PaginatedResponse<CutoffData>> {
  return this.cutoffsService.findAll(paginationDto);
}
```

---

### 4. Filtrado y Ordenamiento

```typescript
// dto/cutoff-filters.dto.ts
export class CutoffFiltersDto extends PaginationDto {
  @ApiPropertyOptional({
    description: 'Filtrar por estado',
    enum: CutoffStatus
  })
  @IsOptional()
  @IsEnum(CutoffStatus, { message: 'Estado inválido' })
  status?: CutoffStatus;

  @ApiPropertyOptional({
    description: 'Filtrar por período',
    example: 'uuid-del-periodo'
  })
  @IsOptional()
  @IsUUID('4', { message: 'El ID del período debe ser un UUID válido' })
  periodId?: string;

  @ApiPropertyOptional({
    description: 'Ordenar por campo',
    enum: ['createdAt', 'status', 'totalAmount'],
    default: 'createdAt'
  })
  @IsOptional()
  @IsIn(['createdAt', 'status', 'totalAmount'])
  sortBy?: string = 'createdAt';

  @ApiPropertyOptional({
    description: 'Dirección de ordenamiento',
    enum: ['ASC', 'DESC'],
    default: 'DESC'
  })
  @IsOptional()
  @IsIn(['ASC', 'DESC'])
  sortOrder?: 'ASC' | 'DESC' = 'DESC';
}

// Servicio con filtros
async findAll(filters: CutoffFiltersDto): Promise<PaginatedResponse<CutoffData>> {
  const { page, limit, status, periodId, sortBy, sortOrder } = filters;
  const skip = (page - 1) * limit;

  const where: any = {};
  if (status) where.status = status;
  if (periodId) where.periodId = periodId;

  const [cutoffs, total] = await this.cutoffRepository.findAndCount({
    where,
    skip,
    take: limit,
    order: { [sortBy]: sortOrder }
  });

  // ... resto de la lógica
}
```

---

### 5. Versionado de API

**Estrategia recomendada**: Versionado por URL

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

**Deprecación de versiones**:
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

---

### 6. Manejo de Errores Consistente

**Estructura estándar de error**:

```typescript
// types/error-response.type.ts
export type ErrorResponse = {
  statusCode: number;
  message: string;
  errors?: string[];       // Errores de validación
  timestamp: string;
  path: string;
  method: string;
};

// filters/http-exception.filter.ts
@Catch()
export class AllExceptionsFilter implements ExceptionFilter {
  catch(exception: unknown, host: ArgumentsHost) {
    const ctx = host.switchToHttp();
    const response = ctx.getResponse<Response>();
    const request = ctx.getRequest<Request>();

    const status = exception instanceof HttpException
      ? exception.getStatus()
      : 500;

    const errorResponse: ErrorResponse = {
      statusCode: status,
      message: this.getErrorMessage(exception),
      errors: this.getValidationErrors(exception),
      timestamp: new Date().toISOString(),
      path: request.url,
      method: request.method
    };

    this.logger.error(
      `${request.method} ${request.url} - ${status}`,
      exception instanceof Error ? exception.stack : ''
    );

    response.status(status).json(errorResponse);
  }

  private getErrorMessage(exception: unknown): string {
    if (exception instanceof HttpException) {
      const response = exception.getResponse();
      return typeof response === 'string' ? response : (response as any).message;
    }
    return 'Error interno del servidor';
  }

  private getValidationErrors(exception: unknown): string[] | undefined {
    if (exception instanceof BadRequestException) {
      const response = exception.getResponse() as any;
      if (Array.isArray(response.message)) {
        return response.message;
      }
    }
    return undefined;
  }
}
```

**Uso en servicios**:
```typescript
@Injectable()
export class CutoffsService {
  async findOne(id: string): Promise<CutoffResponse> {
    const cutoff = await this.cutoffRepository.findOne({ where: { id } });

    if (!cutoff) {
      throw new NotFoundException(`Corte con ID ${id} no encontrado`);
    }

    return {
      status: 200,
      message: 'Corte obtenido exitosamente',
      data: this.mapToData(cutoff)
    };
  }

  async create(dto: CreateCutoffDto): Promise<CutoffCreatedResponse> {
    // Validar duplicados
    const existing = await this.cutoffRepository.findOne({
      where: { periodId: dto.periodId, status: CutoffStatus.ACTIVE }
    });

    if (existing) {
      throw new ConflictException(
        `Ya existe un corte activo para el período ${dto.periodId}`
      );
    }

    const cutoff = this.cutoffRepository.create(dto);
    const saved = await this.cutoffRepository.save(cutoff);

    return {
      status: 201,
      message: 'Corte creado exitosamente',
      data: this.mapToData(saved)
    };
  }
}
```

---

### 7. Documentación Swagger

**Configuración completa en controladores**:

```typescript
@ApiTags('Cortes de Nómina')
@Controller('cutoffs')
@ApiBearerAuth('JWT-auth')
@UseGuards(JwtAuthGuard, RolesGuard)
export class CutoffsController {
  constructor(private readonly cutoffsService: CutoffsService) {}

  @Post()
  @Roles('admin', 'payroll-manager')
  @ApiOperation({
    summary: 'Crear nuevo corte de nómina',
    description: 'Crea un corte de nómina asociado a un período específico. Solo usuarios con rol admin o payroll-manager.'
  })
  @ApiBody({
    type: CreateCutoffDto,
    description: 'Datos del corte a crear',
    examples: {
      basic: {
        summary: 'Corte básico',
        value: {
          periodId: 'uuid-del-periodo',
          notes: 'Corte quincenal enero 2026'
        }
      }
    }
  })
  @ApiResponse({
    status: 201,
    description: 'Corte creado exitosamente',
    schema: {
      example: {
        status: 201,
        message: 'Corte creado exitosamente',
        data: {
          id: 'uuid-generado',
          periodId: 'uuid-del-periodo',
          status: 'draft',
          notes: 'Corte quincenal enero 2026',
          createdAt: '2026-01-24T12:00:00.000Z',
          updatedAt: '2026-01-24T12:00:00.000Z'
        }
      }
    }
  })
  @ApiResponse({
    status: 400,
    description: 'Datos de entrada inválidos',
    schema: {
      example: {
        statusCode: 400,
        message: 'Error de validación',
        errors: [
          'El periodId es requerido',
          'El periodId debe ser un UUID válido'
        ],
        timestamp: '2026-01-24T12:00:00.000Z',
        path: '/api/v1/cutoffs',
        method: 'POST'
      }
    }
  })
  @ApiResponse({
    status: 409,
    description: 'Ya existe un corte activo para el período',
    schema: {
      example: {
        statusCode: 409,
        message: 'Ya existe un corte activo para el período uuid-del-periodo',
        timestamp: '2026-01-24T12:00:00.000Z',
        path: '/api/v1/cutoffs',
        method: 'POST'
      }
    }
  })
  async create(@Body() createCutoffDto: CreateCutoffDto): Promise<CutoffCreatedResponse> {
    return this.cutoffsService.create(createCutoffDto);
  }

  @Get()
  @ApiOperation({ summary: 'Listar cortes con filtros y paginación' })
  @ApiQuery({ type: CutoffFiltersDto })
  @ApiResponse({
    status: 200,
    description: 'Cortes obtenidos exitosamente',
    schema: {
      example: {
        status: 200,
        message: 'Cortes obtenidos exitosamente',
        data: [/* ... */],
        meta: {
          page: 1,
          limit: 10,
          total: 45,
          totalPages: 5,
          hasNextPage: true,
          hasPreviousPage: false
        }
      }
    }
  })
  async findAll(@Query() filters: CutoffFiltersDto): Promise<PaginatedResponse<CutoffData>> {
    return this.cutoffsService.findAll(filters);
  }
}
```

---

## Workflow de Auditoría

Cuando se invoque este skill para auditar un módulo existente:

1. **Leer estructura del módulo**:
   ```bash
   src/modules/$ARGUMENTS/
   ├── *.controller.ts
   ├── *.service.ts
   ├── dto/
   └── types/
   ```

2. **Verificar checklist**:
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

3. **Generar reporte**:
   ```markdown
   # Auditoría de API: $ARGUMENTS

   ## ✅ Cumple
   - Paginación implementada
   - DTOs con validaciones

   ## ⚠️ Mejoras Necesarias
   - Falta versionado /api/v1/
   - Documentación Swagger incompleta
   - No hay filtrado por fecha

   ## 🔧 Acciones Recomendadas
   1. Añadir prefix global en main.ts
   2. Completar decoradores @ApiResponse
   3. Implementar FilterDto con fechas
   ```

---

## Comandos de Uso

```bash
# Auditar módulo existente
/api-design-principles cutoffs

# Implementar nuevo endpoint
/api-design-principles new:providers-assignments

# Revisar endpoints globales
/api-design-principles audit:all
```

---

## Referencias

- [REST API Design Best Practices](https://restfulapi.net/)
- [NestJS OpenAPI Documentation](https://docs.nestjs.com/openapi/introduction)
- [HTTP Status Codes Reference](https://developer.mozilla.org/en-US/docs/Web/HTTP/Status)
