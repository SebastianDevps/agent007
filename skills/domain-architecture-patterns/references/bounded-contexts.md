# Bounded Contexts - Estructura Modular

## Organización recomendada

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

## Reglas de Comunicación entre Bounded Contexts

### Regla 1: Mismo contexto → import directo OK

```typescript
// Mismo bounded context (payroll-context)
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

### Regla 2: Diferentes contextos → eventos o interfaces

```typescript
// INCORRECTO: Cross-context import directo
// src/modules/payroll-context/cutoffs/cutoffs.service.ts
import { ProvidersService } from '../../provider-context/providers/providers.service';

// CORRECTO: Comunicación vía eventos
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
    this.logger.log(`Cutoff ${payload.cutoffId} cerrado. Notificando proveedores...`);
  }
}
```

### Regla 3: Shared cross-context SOLO infraestructura

```typescript
// CORRECTO: Infraestructura compartida
import { DatabaseService } from '@shared/database/database.service';
import { EmailService } from '@shared/email/email.service';
```
