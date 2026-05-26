# Documentación Swagger

Configuración completa en controladores.

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
