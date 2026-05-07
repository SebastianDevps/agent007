# Retry con Exponential Backoff

**Problema**: Fallos transitorios (network glitches) causan errores innecesarios.

**Solución**: Reintentar con delays crecientes (1s, 2s, 4s, 8s...).

## Implementación con decorador personalizado

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
