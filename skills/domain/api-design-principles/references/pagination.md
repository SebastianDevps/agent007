# Paginación Estándar

Implementación obligatoria para listados.

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
