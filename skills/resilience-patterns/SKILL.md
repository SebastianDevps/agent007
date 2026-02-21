---
name: resilience-patterns
version: 1.0.0
description: Implementar patrones de resiliencia (circuit breakers, retry, health checks) en NestJS sin arquitectura de microservicios
argument-hint: [servicio o integración a mejorar]
user-invocable: true
allowed-tools: Read, Grep, Glob, Edit, Write, Bash
model: sonnet
---

# Resilience Patterns - NestJS Monolith

Skill para implementar patrones de resiliencia en aplicaciones monolíticas NestJS, enfocado en integraciones externas (S3, email, APIs de terceros).

## Principios Fundamentales

**Objetivo**: Mejorar la tolerancia a fallos sin migrar a microservicios.

**Patrones clave**:
1. Circuit Breaker (evitar cascadas de fallos)
2. Retry con Exponential Backoff (reintentos inteligentes)
3. Timeout (prevenir bloqueos)
4. Health Checks (monitoreo proactivo)
5. Graceful Degradation (funcionalidad reducida vs fallo total)

---

## 1. Circuit Breaker Pattern

**Problema**: Integraciones externas que fallan causan cascada de errores y timeout en toda la aplicación.

**Solución**: Detener llamadas a servicios que están fallando, dar tiempo para recuperación.

### Implementación con @nestjs/terminus

```bash
yarn add @nestjs/terminus @nestjs/axios
```

```typescript
// shared/resilience/circuit-breaker.decorator.ts
import { Injectable } from '@nestjs/common';

export interface CircuitBreakerOptions {
  threshold: number;        // Fallos consecutivos antes de abrir
  timeout: number;          // Tiempo en ms antes de considerar fallo
  resetTimeout: number;     // Tiempo en ms antes de reintentar (half-open)
}

export class CircuitBreakerService {
  private failureCount = 0;
  private lastFailureTime: number | null = null;
  private state: 'CLOSED' | 'OPEN' | 'HALF_OPEN' = 'CLOSED';

  constructor(private readonly options: CircuitBreakerOptions) {}

  async execute<T>(fn: () => Promise<T>): Promise<T> {
    // Estado OPEN: Rechazar llamada inmediatamente
    if (this.state === 'OPEN') {
      if (Date.now() - this.lastFailureTime! >= this.options.resetTimeout) {
        this.state = 'HALF_OPEN';
      } else {
        throw new Error('Circuit breaker is OPEN');
      }
    }

    try {
      const result = await this.executeWithTimeout(fn);
      this.onSuccess();
      return result;
    } catch (error) {
      this.onFailure();
      throw error;
    }
  }

  private async executeWithTimeout<T>(fn: () => Promise<T>): Promise<T> {
    return Promise.race([
      fn(),
      new Promise<T>((_, reject) =>
        setTimeout(() => reject(new Error('Timeout')), this.options.timeout)
      )
    ]);
  }

  private onSuccess(): void {
    this.failureCount = 0;
    this.state = 'CLOSED';
  }

  private onFailure(): void {
    this.failureCount++;
    this.lastFailureTime = Date.now();

    if (this.failureCount >= this.options.threshold) {
      this.state = 'OPEN';
    }
  }

  getState(): string {
    return this.state;
  }
}

// shared/storage/s3.service.ts
import { Injectable, Logger } from '@nestjs/common';
import { S3 } from 'aws-sdk';
import { CircuitBreakerService } from '../resilience/circuit-breaker.service';

@Injectable()
export class S3Service {
  private readonly logger = new Logger(S3Service.name);
  private readonly s3 = new S3();
  private readonly circuitBreaker: CircuitBreakerService;

  constructor() {
    this.circuitBreaker = new CircuitBreakerService({
      threshold: 5,           // 5 fallos consecutivos
      timeout: 30000,         // 30 segundos timeout
      resetTimeout: 60000     // Reintentar después de 1 minuto
    });
  }

  async uploadFile(bucket: string, key: string, file: Buffer): Promise<string> {
    try {
      return await this.circuitBreaker.execute(async () => {
        const result = await this.s3.upload({
          Bucket: bucket,
          Key: key,
          Body: file
        }).promise();

        return result.Location;
      });
    } catch (error) {
      this.logger.error(`S3 upload failed (circuit: ${this.circuitBreaker.getState()}): ${error.message}`);

      // Graceful degradation: Guardar localmente si S3 falla
      if (this.circuitBreaker.getState() === 'OPEN') {
        return this.saveFileLocally(key, file);
      }

      throw error;
    }
  }

  private async saveFileLocally(key: string, file: Buffer): Promise<string> {
    // Fallback: Guardar en filesystem local
    const fs = require('fs').promises;
    const path = `./uploads/fallback/${key}`;
    await fs.writeFile(path, file);
    this.logger.warn(`File saved locally due to S3 circuit breaker: ${path}`);
    return path;
  }
}
```

---

## 2. Retry con Exponential Backoff

**Problema**: Fallos transitorios (network glitches) causan errores innecesarios.

**Solución**: Reintentar con delays crecientes (1s, 2s, 4s, 8s...).

### Implementación con decorador personalizado

```typescript
// shared/resilience/retry.decorator.ts
export interface RetryOptions {
  maxAttempts: number;
  backoff: {
    type: 'exponential' | 'linear' | 'fixed';
    delay: number;        // Delay inicial en ms
    maxDelay?: number;    // Delay máximo (para exponential)
  };
  retryableErrors?: (error: any) => boolean;
}

export function Retry(options: RetryOptions) {
  return function (
    target: any,
    propertyKey: string,
    descriptor: PropertyDescriptor
  ) {
    const originalMethod = descriptor.value;

    descriptor.value = async function (...args: any[]) {
      let lastError: any;

      for (let attempt = 1; attempt <= options.maxAttempts; attempt++) {
        try {
          return await originalMethod.apply(this, args);
        } catch (error) {
          lastError = error;

          // Verificar si el error es retryable
          if (options.retryableErrors && !options.retryableErrors(error)) {
            throw error;
          }

          // No reintentar en el último intento
          if (attempt === options.maxAttempts) {
            break;
          }

          // Calcular delay
          const delay = calculateDelay(options.backoff, attempt);
          this.logger?.warn(
            `${propertyKey} falló (intento ${attempt}/${options.maxAttempts}). Reintentando en ${delay}ms...`
          );

          await sleep(delay);
        }
      }

      throw lastError;
    };

    return descriptor;
  };
}

function calculateDelay(backoff: RetryOptions['backoff'], attempt: number): number {
  switch (backoff.type) {
    case 'exponential':
      const exponentialDelay = backoff.delay * Math.pow(2, attempt - 1);
      return Math.min(exponentialDelay, backoff.maxDelay || Infinity);
    case 'linear':
      return backoff.delay * attempt;
    case 'fixed':
      return backoff.delay;
  }
}

function sleep(ms: number): Promise<void> {
  return new Promise(resolve => setTimeout(resolve, ms));
}

// shared/email/email.service.ts
import { Injectable, Logger } from '@nestjs/common';
import { Retry } from '../resilience/retry.decorator';

@Injectable()
export class EmailService {
  private readonly logger = new Logger(EmailService.name);

  @Retry({
    maxAttempts: 3,
    backoff: {
      type: 'exponential',
      delay: 1000,      // 1s, 2s, 4s
      maxDelay: 10000   // Máximo 10s
    },
    retryableErrors: (error) => {
      // Solo reintentar errores de red, no de validación
      return error.code === 'ECONNREFUSED' || error.code === 'ETIMEDOUT';
    }
  })
  async sendEmail(to: string, subject: string, body: string): Promise<void> {
    // Integración con servicio de email (SendGrid, AWS SES, etc.)
    const response = await fetch('https://api.email-service.com/send', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ to, subject, body })
    });

    if (!response.ok) {
      throw new Error(`Email service returned ${response.status}`);
    }

    this.logger.log(`Email enviado exitosamente a ${to}`);
  }
}
```

---

## 3. Timeout Pattern

**Problema**: Operaciones externas que no responden bloquean threads indefinidamente.

**Solución**: Establecer timeouts agresivos y manejar degradación.

```typescript
// shared/resilience/timeout.decorator.ts
export function Timeout(ms: number) {
  return function (
    target: any,
    propertyKey: string,
    descriptor: PropertyDescriptor
  ) {
    const originalMethod = descriptor.value;

    descriptor.value = async function (...args: any[]) {
      return Promise.race([
        originalMethod.apply(this, args),
        new Promise((_, reject) =>
          setTimeout(() => reject(new Error(`Timeout después de ${ms}ms`)), ms)
        )
      ]);
    };

    return descriptor;
  };
}

// shared/external-api/payment-gateway.service.ts
@Injectable()
export class PaymentGatewayService {
  private readonly logger = new Logger(PaymentGatewayService.name);

  @Timeout(5000)  // 5 segundos máximo
  @Retry({
    maxAttempts: 2,
    backoff: { type: 'fixed', delay: 1000 }
  })
  async processPayment(amount: number, cardToken: string): Promise<PaymentResult> {
    const response = await fetch('https://payment-gateway.com/charge', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ amount, cardToken })
    });

    return response.json();
  }
}
```

---

## 4. Health Checks

**Problema**: No hay visibilidad del estado de dependencias externas.

**Solución**: Endpoints de salud que verifican todas las integraciones.

### Implementación con @nestjs/terminus

```typescript
// shared/health/health.module.ts
import { Module } from '@nestjs/common';
import { TerminusModule } from '@nestjs/terminus';
import { HttpModule } from '@nestjs/axios';
import { HealthController } from './health.controller';
import { DatabaseHealthIndicator } from './indicators/database.health';
import { S3HealthIndicator } from './indicators/s3.health';
import { RedisHealthIndicator } from './indicators/redis.health';

@Module({
  imports: [TerminusModule, HttpModule],
  controllers: [HealthController],
  providers: [
    DatabaseHealthIndicator,
    S3HealthIndicator,
    RedisHealthIndicator
  ]
})
export class HealthModule {}

// shared/health/health.controller.ts
import { Controller, Get } from '@nestjs/common';
import { HealthCheck, HealthCheckService, TypeOrmHealthIndicator } from '@nestjs/terminus';
import { Public } from '@common/decorators/public.decorator';
import { DatabaseHealthIndicator } from './indicators/database.health';
import { S3HealthIndicator } from './indicators/s3.health';
import { RedisHealthIndicator } from './indicators/redis.health';

@Controller('health')
export class HealthController {
  constructor(
    private readonly health: HealthCheckService,
    private readonly db: TypeOrmHealthIndicator,
    private readonly databaseHealth: DatabaseHealthIndicator,
    private readonly s3Health: S3HealthIndicator,
    private readonly redisHealth: RedisHealthIndicator
  ) {}

  @Get()
  @Public()
  @HealthCheck()
  async check() {
    return this.health.check([
      // Base de datos
      () => this.db.pingCheck('database', { timeout: 3000 }),
      () => this.databaseHealth.checkConnections('database-connections'),

      // S3
      () => this.s3Health.isHealthy('s3'),

      // Redis
      () => this.redisHealth.isHealthy('redis')
    ]);
  }

  @Get('liveness')
  @Public()
  @HealthCheck()
  async liveness() {
    // Liveness: ¿La aplicación está viva? (solo verificar lo crítico)
    return this.health.check([
      () => this.db.pingCheck('database', { timeout: 1000 })
    ]);
  }

  @Get('readiness')
  @Public()
  @HealthCheck()
  async readiness() {
    // Readiness: ¿La aplicación está lista para recibir tráfico?
    return this.health.check([
      () => this.db.pingCheck('database', { timeout: 3000 }),
      () => this.redisHealth.isHealthy('redis'),
      () => this.s3Health.isHealthy('s3')
    ]);
  }
}

// shared/health/indicators/s3.health.ts
import { Injectable } from '@nestjs/common';
import { HealthIndicator, HealthIndicatorResult, HealthCheckError } from '@nestjs/terminus';
import { S3 } from 'aws-sdk';

@Injectable()
export class S3HealthIndicator extends HealthIndicator {
  private readonly s3 = new S3();

  async isHealthy(key: string): Promise<HealthIndicatorResult> {
    try {
      // Verificar con operación simple (list buckets)
      await Promise.race([
        this.s3.listBuckets().promise(),
        new Promise((_, reject) =>
          setTimeout(() => reject(new Error('S3 timeout')), 3000)
        )
      ]);

      return this.getStatus(key, true, { message: 'S3 is reachable' });
    } catch (error) {
      throw new HealthCheckError(
        'S3 health check failed',
        this.getStatus(key, false, { message: error.message })
      );
    }
  }
}

// shared/health/indicators/redis.health.ts
@Injectable()
export class RedisHealthIndicator extends HealthIndicator {
  constructor(@Inject('REDIS_CLIENT') private readonly redis: Redis) {}

  async isHealthy(key: string): Promise<HealthIndicatorResult> {
    try {
      await this.redis.ping();
      return this.getStatus(key, true, { message: 'Redis is responsive' });
    } catch (error) {
      throw new HealthCheckError(
        'Redis health check failed',
        this.getStatus(key, false, { message: error.message })
      );
    }
  }
}

// shared/health/indicators/database.health.ts
@Injectable()
export class DatabaseHealthIndicator extends HealthIndicator {
  constructor(private readonly dataSource: DataSource) {}

  async checkConnections(key: string): Promise<HealthIndicatorResult> {
    const driver = this.dataSource.driver as any;
    const pool = driver.master;

    const totalConnections = pool.totalCount;
    const idleConnections = pool.idleCount;
    const activeConnections = totalConnections - idleConnections;

    // Alertar si >80% de conexiones están en uso
    const isHealthy = activeConnections / totalConnections < 0.8;

    const result = this.getStatus(key, isHealthy, {
      total: totalConnections,
      idle: idleConnections,
      active: activeConnections,
      utilization: `${((activeConnections / totalConnections) * 100).toFixed(2)}%`
    });

    if (!isHealthy) {
      throw new HealthCheckError('Database connections exhausted', result);
    }

    return result;
  }
}
```

**Response de health check**:
```json
{
  "status": "ok",
  "info": {
    "database": {
      "status": "up"
    },
    "database-connections": {
      "status": "up",
      "total": 10,
      "idle": 7,
      "active": 3,
      "utilization": "30.00%"
    },
    "s3": {
      "status": "up",
      "message": "S3 is reachable"
    },
    "redis": {
      "status": "up",
      "message": "Redis is responsive"
    }
  },
  "error": {},
  "details": {
    "database": { "status": "up" },
    "database-connections": { "status": "up", "total": 10, "idle": 7, "active": 3, "utilization": "30.00%" },
    "s3": { "status": "up", "message": "S3 is reachable" },
    "redis": { "status": "up", "message": "Redis is responsive" }
  }
}
```

---

## 5. Graceful Degradation

**Problema**: Fallo de servicio no crítico tumba toda la aplicación.

**Solución**: Proveer funcionalidad reducida cuando dependencias fallan.

```typescript
// modules/payroll-context/cutoffs/cutoffs.service.ts
@Injectable()
export class CutoffsService {
  constructor(
    private readonly cutoffRepository: Repository<Cutoff>,
    private readonly s3Service: S3Service,
    private readonly emailService: EmailService
  ) {}

  async closeCutoff(id: string): Promise<CutoffResponse> {
    const cutoff = await this.findOneOrFail(id);
    cutoff.close();
    await this.cutoffRepository.save(cutoff);

    // Operaciones no críticas con degradación
    await this.notifyClosureWithDegradation(cutoff);
    await this.generateReportWithDegradation(cutoff);

    return {
      status: 200,
      message: 'Corte cerrado exitosamente',
      data: this.mapToData(cutoff)
    };
  }

  private async notifyClosureWithDegradation(cutoff: Cutoff): Promise<void> {
    try {
      await this.emailService.sendEmail(
        cutoff.managerEmail,
        'Corte cerrado',
        `El corte ${cutoff.id} ha sido cerrado`
      );
    } catch (error) {
      // Graceful degradation: Log error pero no fallar el cierre
      this.logger.warn(
        `No se pudo enviar email de notificación (corte cerrado exitosamente): ${error.message}`
      );

      // Fallback: Guardar en cola para reintentar después
      await this.queueEmailForRetry(cutoff.managerEmail, cutoff.id);
    }
  }

  private async generateReportWithDegradation(cutoff: Cutoff): Promise<void> {
    try {
      const reportBuffer = await this.generatePDFReport(cutoff);
      await this.s3Service.uploadFile('reports', `cutoff-${cutoff.id}.pdf`, reportBuffer);
    } catch (error) {
      // Graceful degradation: Permitir generar reporte manualmente después
      this.logger.warn(
        `No se pudo generar reporte automático (disponible para generación manual): ${error.message}`
      );

      await this.cutoffRepository.update(cutoff.id, {
        reportStatus: 'pending-manual-generation'
      });
    }
  }
}
```

---

## 6. Bulkhead Pattern (Aislamiento de Recursos)

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

---

## Comandos de Uso

```bash
# Añadir circuit breaker a servicio
/resilience-patterns add-circuit-breaker:S3Service

# Implementar retry con backoff
/resilience-patterns add-retry:EmailService

# Configurar health checks
/resilience-patterns setup-health-checks

# Auditar resiliencia de integraciones
/resilience-patterns audit
```

---

## Checklist de Implementación

- [ ] Circuit breakers en integraciones externas (S3, email, APIs)
- [ ] Retry con exponential backoff para fallos transitorios
- [ ] Timeouts agresivos (< 5s para APIs externas)
- [ ] Health checks (liveness + readiness)
- [ ] Graceful degradation para operaciones no críticas
- [ ] Bulkhead isolation para operaciones pesadas
- [ ] Logging de estados de circuit breakers
- [ ] Métricas de reintentos y fallos
- [ ] Fallbacks documentados

---

## Referencias

- [NestJS Terminus Documentation](https://docs.nestjs.com/recipes/terminus)
- [Circuit Breaker Pattern - Microsoft](https://docs.microsoft.com/en-us/azure/architecture/patterns/circuit-breaker)
- [Retry Pattern - AWS](https://aws.amazon.com/builders-library/timeouts-retries-and-backoff-with-jitter/)
