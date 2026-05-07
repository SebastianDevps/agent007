# Circuit Breaker Pattern

**Problema**: Integraciones externas que fallan causan cascada de errores y timeout en toda la aplicación.

**Solución**: Detener llamadas a servicios que están fallando, dar tiempo para recuperación.

## Implementación con @nestjs/terminus

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
