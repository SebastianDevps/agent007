# Bulkhead Pattern (Aislamiento de Recursos)

**Problema**: Una operación lenta consume todos los threads y bloquea otras operaciones.

**Solución**: Pools de recursos separados para diferentes tipos de operaciones.

```typescript
// shared/resilience/bulkhead.service.ts
import PQueue from 'p-queue';

@Injectable()
export class BulkheadService {
  // Pools separados para diferentes tipos de operaciones
  private readonly criticalPool = new PQueue({ concurrency: 10 });
  private readonly backgroundPool = new PQueue({ concurrency: 5 });
  private readonly reportsPool = new PQueue({ concurrency: 2 });

  async executeCritical<T>(fn: () => Promise<T>): Promise<T> {
    return this.criticalPool.add(fn);
  }

  async executeBackground<T>(fn: () => Promise<T>): Promise<T> {
    return this.backgroundPool.add(fn);
  }

  async executeReport<T>(fn: () => Promise<T>): Promise<T> {
    return this.reportsPool.add(fn);
  }

  getStats() {
    return {
      critical: {
        pending: this.criticalPool.pending,
        size: this.criticalPool.size
      },
      background: {
        pending: this.backgroundPool.pending,
        size: this.backgroundPool.size
      },
      reports: {
        pending: this.reportsPool.pending,
        size: this.reportsPool.size
      }
    };
  }
}

// Uso en servicio
@Injectable()
export class ReportsService {
  constructor(private readonly bulkhead: BulkheadService) {}

  async generateCutoffReport(cutoffId: string): Promise<Buffer> {
    // Ejecutar en pool de reportes (no bloquea operaciones críticas)
    return this.bulkhead.executeReport(async () => {
      const data = await this.fetchCutoffData(cutoffId);
      return this.renderPDF(data);
    });
  }
}
```
