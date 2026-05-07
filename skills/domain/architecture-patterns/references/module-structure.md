# Estructura de Módulo Individual

**Límite máximo**: 450 líneas por archivo (refactorizar si se excede).

```typescript
// src/modules/payroll-context/cutoffs/cutoffs.module.ts
import { Module } from '@nestjs/common';
import { TypeOrmModule } from '@nestjs/typeorm';
import { CutoffsController } from './cutoffs.controller';
import { CutoffsService } from './cutoffs.service';
import { Cutoff } from './entities/cutoff.entity';
import { PeriodsModule } from '../periods/periods.module';

@Module({
  imports: [
    TypeOrmModule.forFeature([Cutoff]),
    PeriodsModule  // Mismo contexto, import directo OK
  ],
  controllers: [CutoffsController],
  providers: [CutoffsService],
  exports: [CutoffsService]  // Exportar para otros módulos del contexto
})
export class CutoffsModule {}

// src/modules/payroll-context/cutoffs/cutoffs.controller.ts
import { Controller, Get, Post, Body, Param } from '@nestjs/common';
import { ApiTags, ApiOperation } from '@nestjs/swagger';
import { CutoffsService } from './cutoffs.service';
import { CreateCutoffDto } from './dto/create-cutoff.dto';
import { CutoffResponse } from './types/cutoff-response.type';

@ApiTags('Cortes de Nómina')
@Controller('cutoffs')
export class CutoffsController {
  constructor(private readonly cutoffsService: CutoffsService) {}

  @Post()
  @ApiOperation({ summary: 'Crear nuevo corte' })
  async create(@Body() dto: CreateCutoffDto): Promise<CutoffResponse> {
    return this.cutoffsService.create(dto);
  }
}

// src/modules/payroll-context/cutoffs/cutoffs.service.ts
import { Injectable, NotFoundException } from '@nestjs/common';
import { InjectRepository } from '@nestjs/typeorm';
import { Repository } from 'typeorm';
import { Cutoff } from './entities/cutoff.entity';
import { CreateCutoffDto } from './dto/create-cutoff.dto';
import { CutoffResponse, CutoffData } from './types/cutoff-response.type';

@Injectable()
export class CutoffsService {
  private readonly logger = new Logger(CutoffsService.name);

  constructor(
    @InjectRepository(Cutoff)
    private readonly cutoffRepository: Repository<Cutoff>,
  ) {}

  async create(dto: CreateCutoffDto): Promise<CutoffResponse> {
    const cutoff = this.cutoffRepository.create(dto);
    const saved = await this.cutoffRepository.save(cutoff);

    return {
      status: 201,
      message: 'Corte creado exitosamente',
      data: this.mapToData(saved)
    };
  }

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

  // Método privado de mapeo
  private mapToData(cutoff: Cutoff): CutoffData {
    return {
      id: cutoff.id,
      periodId: cutoff.periodId,
      status: cutoff.status,
      notes: cutoff.notes,
      createdAt: cutoff.createdAt.toISOString(),
      updatedAt: cutoff.updatedAt.toISOString()
    };
  }
}
```
