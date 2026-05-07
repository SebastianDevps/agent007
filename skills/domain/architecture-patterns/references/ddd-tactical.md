# Domain-Driven Design (DDD) — Patrones Tácticos

## Aggregates

Cluster de entidades con una raíz que mantiene la consistencia.

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

## Value Objects

Objetos inmutables sin identidad — la igualdad se basa en los atributos.

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

## Domain Events

Comunicación entre bounded contexts.

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
