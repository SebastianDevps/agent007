# Filtrado y Ordenamiento

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
