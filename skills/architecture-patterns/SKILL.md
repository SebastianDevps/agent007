---
name: architecture-patterns
version: 1.0.0
description: Implementar y auditar patrones arquitectónicos (Clean Architecture, DDD, Bounded Contexts) en NestJS con TypeORM
argument-hint: [módulo o contexto a analizar]
user-invocable: true
allowed-tools: Read, Grep, Glob, Edit, Write
model: sonnet
---

# Architecture Patterns - NestJS Clean Architecture & DDD

Skill para implementar, auditar y refactorizar módulos siguiendo Clean Architecture y Domain-Driven Design en NestJS.

## Principios Fundamentales

### 1. Clean Architecture

**Capas de la arquitectura**:

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

---

### 2. Estructura Modular por Bounded Contexts

**Organización recomendada para nuestro proyecto**:

```typescript
src/
├── main.ts
├── app.module.ts
│
├── common/                          // Recursos compartidos globales
│   ├── decorators/
│   ├── guards/
│   ├── filters/
│   └── interceptors/
│
├── shared/                          // Servicios de infraestructura
│   ├── database/
│   │   ├── database.module.ts
│   │   └── database.service.ts
│   ├── storage/                     // S3, uploads
│   ├── email/
│   └── cache/                       // Redis
│
└── modules/                         // Bounded Contexts
    │
    ├── payroll-context/             // Contexto de Nómina
    │   ├── payroll-context.module.ts
    │   ├── cutoffs/
    │   │   ├── cutoffs.module.ts
    │   │   ├── cutoffs.controller.ts
    │   │   ├── cutoffs.service.ts
    │   │   ├── entities/
    │   │   │   ├── cutoff.entity.ts
    │   │   │   └── index.ts
    │   │   ├── dto/
    │   │   │   ├── create-cutoff.dto.ts
    │   │   │   ├── update-cutoff.dto.ts
    │   │   │   └── index.ts
    │   │   ├── types/
    │   │   │   ├── cutoff-response.type.ts
    │   │   │   └── index.ts
    │   │   └── interfaces/
    │   │       └── cutoff-repository.interface.ts
    │   │
    │   ├── periods/
    │   │   └── [misma estructura]
    │   │
    │   ├── payroll-requirements/
    │   │   └── [misma estructura]
    │   │
    │   └── shared/                  // Compartido SOLO en payroll-context
    │       ├── enums/
    │       │   └── cutoff-status.enum.ts
    │       └── value-objects/
    │           └── payroll-period.vo.ts
    │
    ├── provider-context/            // Contexto de Proveedores
    │   ├── provider-context.module.ts
    │   ├── providers/
    │   │   ├── providers.module.ts
    │   │   ├── providers.controller.ts
    │   │   ├── providers.service.ts
    │   │   └── [estructura completa]
    │   │
    │   ├── provider-audit/
    │   ├── daily-assignments/
    │   │
    │   └── shared/
    │       └── enums/
    │           └── provider-status.enum.ts
    │
    ├── financial-context/           // Contexto Financiero
    │   ├── financial-context.module.ts
    │   ├── withholdings/
    │   │   ├── general-withholdings/
    │   │   └── company-city-withholdings/
    │   │
    │   ├── collection-accounts/
    │   ├── ceco-charges/
    │   │
    │   └── shared/
    │       └── value-objects/
    │           └── money.vo.ts
    │
    ├── audit-context/               // Contexto de Auditoría
    │   ├── audit-context.module.ts
    │   ├── audit-logs/
    │   ├── data-changes/
    │   ├── security-events/
    │   │
    │   └── shared/
    │       └── enums/
    │           └── audit-event-type.enum.ts
    │
    └── organizational-context/      // Contexto Organizacional
        ├── organizational-context.module.ts
        ├── companies/
        ├── cecos/
        ├── charges/
        ├── cities/
        │
        └── shared/
            └── interfaces/
                └── organizational-entity.interface.ts
```

---

### 3. Bounded Contexts - Reglas de Comunicación

**Regla 1**: Módulos dentro del MISMO contexto pueden importarse directamente.

```typescript
// ✅ Correcto: Mismo bounded context (payroll-context)
// src/modules/payroll-context/cutoffs/cutoffs.service.ts
import { PeriodsService } from '../periods/periods.service';
import { PayrollRequirementsService } from '../payroll-requirements/payroll-requirements.service';

@Injectable()
export class CutoffsService {
  constructor(
    private readonly periodsService: PeriodsService,
    private readonly payrollRequirementsService: PayrollRequirementsService
  ) {}
}
```

**Regla 2**: Módulos de DIFERENTES contextos deben comunicarse vía **eventos** o **interfaces**.

```typescript
// ❌ Incorrecto: Cross-context import directo
// src/modules/payroll-context/cutoffs/cutoffs.service.ts
import { ProvidersService } from '../../provider-context/providers/providers.service';

// ✅ Correcto: Comunicación vía eventos
// src/modules/payroll-context/cutoffs/cutoffs.service.ts
@Injectable()
export class CutoffsService {
  constructor(private readonly eventEmitter: EventEmitter2) {}

  async closeCutoff(id: string): Promise<void> {
    // ... lógica de cierre

    // Emitir evento para otros contextos
    this.eventEmitter.emit('cutoff.closed', {
      cutoffId: id,
      closedAt: new Date(),
      totalAmount: cutoff.totalAmount
    });
  }
}

// src/modules/provider-context/providers/providers.service.ts
@Injectable()
export class ProvidersService {
  @OnEvent('cutoff.closed')
  async handleCutoffClosed(payload: CutoffClosedEvent): Promise<void> {
    // Reaccionar al cierre de corte
    this.logger.log(`Cutoff ${payload.cutoffId} cerrado. Notificando proveedores...`);
  }
}
```

**Regla 3**: Shared entre contextos SOLO para infraestructura (database, email, cache).

```typescript
// ✅ Correcto: Infraestructura compartida
import { DatabaseService } from '@shared/database/database.service';
import { EmailService } from '@shared/email/email.service';
```

---

### 4. Estructura de Módulo Individual

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

---

### 5. Domain-Driven Design (DDD)

**Aggregates**: Cluster de entidades con una raíz.

```typescript
// src/modules/payroll-context/cutoffs/entities/cutoff.entity.ts
import { Entity, PrimaryGeneratedColumn, Column, OneToMany } from 'typeorm';
import { CutoffCharge } from './cutoff-charge.entity';

@Entity('cutoffs')
export class Cutoff {  // Aggregate Root
  @PrimaryGeneratedColumn('uuid')
  id: string;

  @Column({ type: 'enum', enum: CutoffStatus })
  status: CutoffStatus;

  // Relación con entidades del agregado
  @OneToMany(() => CutoffCharge, charge => charge.cutoff, { cascade: true })
  charges: CutoffCharge[];

  // Lógica de dominio (business logic en entidad)
  canBeClosed(): boolean {
    return this.status === CutoffStatus.SUBMITTED && this.charges.length > 0;
  }

  close(): void {
    if (!this.canBeClosed()) {
      throw new Error('El corte no puede ser cerrado en su estado actual');
    }
    this.status = CutoffStatus.CLOSED;
  }
}

// Entidad del agregado (no se accede directamente)
@Entity('cutoff_charges')
export class CutoffCharge {
  @PrimaryGeneratedColumn('uuid')
  id: string;

  @Column({ type: 'uuid', name: 'cutoff_id' })
  cutoffId: string;

  @ManyToOne(() => Cutoff, cutoff => cutoff.charges)
  cutoff: Cutoff;

  @Column({ type: 'decimal', precision: 10, scale: 2 })
  amount: number;
}
```

**Value Objects**: Objetos inmutables sin identidad.

```typescript
// src/modules/financial-context/shared/value-objects/money.vo.ts
export class Money {
  constructor(
    public readonly amount: number,
    public readonly currency: string = 'COP'
  ) {
    if (amount < 0) {
      throw new Error('El monto no puede ser negativo');
    }
  }

  add(other: Money): Money {
    if (this.currency !== other.currency) {
      throw new Error('No se pueden sumar montos de diferentes monedas');
    }
    return new Money(this.amount + other.amount, this.currency);
  }

  equals(other: Money): boolean {
    return this.amount === other.amount && this.currency === other.currency;
  }

  toString(): string {
    return `${this.currency} ${this.amount.toFixed(2)}`;
  }
}

// Uso en servicio
@Injectable()
export class CecoChargesService {
  calculateTotal(charges: CecoCharge[]): Money {
    return charges.reduce(
      (total, charge) => total.add(new Money(charge.amount)),
      new Money(0)
    );
  }
}
```

**Domain Events**: Comunicación entre bounded contexts.

```typescript
// src/modules/payroll-context/shared/events/cutoff-closed.event.ts
export class CutoffClosedEvent {
  constructor(
    public readonly cutoffId: string,
    public readonly periodId: string,
    public readonly totalAmount: number,
    public readonly closedAt: Date,
    public readonly closedBy: string
  ) {}
}

// Emisión en servicio
@Injectable()
export class CutoffsService {
  constructor(
    private readonly eventEmitter: EventEmitter2
  ) {}

  async closeCutoff(id: string, userId: string): Promise<void> {
    const cutoff = await this.findOneOrFail(id);
    cutoff.close();  // Lógica de dominio
    await this.cutoffRepository.save(cutoff);

    // Emitir evento de dominio
    this.eventEmitter.emit(
      'cutoff.closed',
      new CutoffClosedEvent(
        cutoff.id,
        cutoff.periodId,
        cutoff.totalAmount,
        new Date(),
        userId
      )
    );
  }
}

// Suscripción en otro contexto
@Injectable()
export class AuditLogsService {
  @OnEvent('cutoff.closed')
  async handleCutoffClosed(event: CutoffClosedEvent): Promise<void> {
    await this.createAuditLog({
      eventType: 'CUTOFF_CLOSED',
      entityId: event.cutoffId,
      userId: event.closedBy,
      metadata: { totalAmount: event.totalAmount }
    });
  }
}
```

---

### 6. Repository Pattern

**Interfaz de repositorio** (opcional, pero recomendado para testabilidad):

```typescript
// src/modules/payroll-context/cutoffs/interfaces/cutoff-repository.interface.ts
export interface ICutoffRepository {
  findById(id: string): Promise<Cutoff | null>;
  findByPeriod(periodId: string): Promise<Cutoff[]>;
  save(cutoff: Cutoff): Promise<Cutoff>;
  delete(id: string): Promise<void>;
}

// Implementación con TypeORM
@Injectable()
export class CutoffRepository implements ICutoffRepository {
  constructor(
    @InjectRepository(Cutoff)
    private readonly repository: Repository<Cutoff>
  ) {}

  async findById(id: string): Promise<Cutoff | null> {
    return this.repository.findOne({ where: { id } });
  }

  async findByPeriod(periodId: string): Promise<Cutoff[]> {
    return this.repository.find({ where: { periodId } });
  }

  async save(cutoff: Cutoff): Promise<Cutoff> {
    return this.repository.save(cutoff);
  }

  async delete(id: string): Promise<void> {
    await this.repository.delete(id);
  }
}

// Servicio usa la interfaz
@Injectable()
export class CutoffsService {
  constructor(
    @Inject('ICutoffRepository')
    private readonly cutoffRepository: ICutoffRepository
  ) {}
}
```

---

### 7. Separación DTOs vs Types vs Interfaces

**DTOs** (Data Transfer Objects):
- Para **validación de entrada** (request body, query params)
- Usan `class-validator`
- Van en `dto/`

```typescript
// dto/create-cutoff.dto.ts
export class CreateCutoffDto {
  @IsUUID('4', { message: 'El periodId debe ser un UUID válido' })
  @IsNotEmpty({ message: 'El periodId es requerido' })
  periodId: string;

  @IsOptional()
  @IsString({ message: 'Las notas deben ser texto' })
  @MaxLength(500, { message: 'Las notas no pueden exceder 500 caracteres' })
  notes?: string;
}
```

**Types** (Tipos de TypeScript):
- Para **respuestas de API** (OBLIGATORIO patrón `{ status, message, data }`)
- Para **tipado interno**
- Van en `types/`

```typescript
// types/cutoff-response.type.ts
export type CutoffCreatedResponse = {
  status: 201;
  message: string;
  data: CutoffData;
};

export type CutoffResponse = {
  status: number;
  message: string;
  data?: CutoffData | CutoffData[];
};

export type CutoffData = {
  id: string;
  periodId: string;
  status: string;
  notes?: string;
  createdAt: string;
  updatedAt: string;
};
```

**Interfaces** (Contratos):
- Para **contratos de servicios**
- Para **inyección de dependencias**
- Van en `interfaces/`

```typescript
// interfaces/cutoff-repository.interface.ts
export interface ICutoffRepository {
  findById(id: string): Promise<Cutoff | null>;
  save(cutoff: Cutoff): Promise<Cutoff>;
}
```

---

## Workflow de Refactorización

Cuando se invoque este skill para refactorizar un módulo:

1. **Analizar módulo actual**:
   ```bash
   src/modules/$ARGUMENTS/
   ```

2. **Identificar bounded context**:
   - ¿A qué dominio pertenece? (payroll, provider, financial, audit, organizational)
   - ¿Qué otros módulos están relacionados?

3. **Verificar checklist**:
   - [ ] Módulo < 450 líneas (cada archivo)
   - [ ] Separación correcta: DTOs vs Types vs Interfaces
   - [ ] Inyección de dependencias (no instanciación manual)
   - [ ] Lógica de negocio en entidades (DDD)
   - [ ] Comunicación cross-context vía eventos
   - [ ] Repository pattern implementado
   - [ ] Value objects para conceptos de dominio

4. **Proponer estructura mejorada**:
   ```typescript
   src/modules/{bounded-context}/{módulo}/
   ├── {módulo}.module.ts
   ├── {módulo}.controller.ts
   ├── {módulo}.service.ts
   ├── entities/
   │   ├── {entity}.entity.ts
   │   └── index.ts
   ├── dto/
   │   ├── create-{entity}.dto.ts
   │   └── index.ts
   ├── types/
   │   ├── {entity}-response.type.ts
   │   └── index.ts
   └── interfaces/
       └── {entity}-repository.interface.ts
   ```

5. **Implementar refactorización**:
   - Mover archivos a bounded context apropiado
   - Dividir archivos >450 líneas
   - Extraer value objects
   - Implementar domain events si hay cross-context

---

## Comandos de Uso

```bash
# Auditar módulo existente
/architecture-patterns audit:cutoffs

# Refactorizar módulo grande
/architecture-patterns refactor:providers

# Definir bounded contexts
/architecture-patterns define-contexts

# Migrar a Clean Architecture
/architecture-patterns migrate:cutoffs
```

---

## Referencias

- [Clean Architecture - Robert C. Martin](https://blog.cleancoder.com/uncle-bob/2012/08/13/the-clean-architecture.html)
- [Domain-Driven Design - Eric Evans](https://www.domainlanguage.com/ddd/)
- [NestJS Modules Documentation](https://docs.nestjs.com/modules)
