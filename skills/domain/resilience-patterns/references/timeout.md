# Timeout Pattern

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
