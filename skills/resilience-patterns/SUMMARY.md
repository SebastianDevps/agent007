# Resilience Patterns - Quick Reference

> **Full details**: See SKILL.md for complete implementation examples

## Core Patterns

### 1. Circuit Breaker
**Problem**: Cascading failures from external services
**Solution**: Stop calling failing services, give time to recover

```typescript
new CircuitBreakerService({
  threshold: 5,      // 5 failures → OPEN
  timeout: 30000,    // 30s timeout
  resetTimeout: 60000 // 1min before retry
});
```

**States**: CLOSED (normal) → OPEN (failing) → HALF_OPEN (testing)

### 2. Retry with Exponential Backoff
**Problem**: Transient failures
**Solution**: Retry with increasing delays (1s, 2s, 4s, 8s...)

```typescript
@Retry({
  maxAttempts: 3,
  backoff: {
    type: 'exponential',
    delay: 1000,
    maxDelay: 10000
  }
})
async sendEmail() { }
```

### 3. Timeout
**Problem**: Hanging requests block threads
**Solution**: Aggressive timeouts (< 5s for external APIs)

```typescript
@Timeout(5000)  // 5 seconds max
async processPayment() { }
```

### 4. Health Checks
**Problem**: No visibility of dependencies
**Solution**: `/health`, `/liveness`, `/readiness` endpoints

```typescript
@Get('health')
@HealthCheck()
async check() {
  return this.health.check([
    () => this.db.pingCheck('database'),
    () => this.s3Health.isHealthy('s3'),
    () => this.redisHealth.isHealthy('redis')
  ]);
}
```

### 5. Graceful Degradation
**Problem**: Non-critical service failure kills app
**Solution**: Reduced functionality vs total failure

```typescript
try {
  await this.s3Service.uploadFile(file);
} catch (error) {
  // Fallback: save locally
  await this.saveFileLocally(file);
}
```

### 6. Bulkhead Isolation
**Problem**: One slow operation blocks all threads
**Solution**: Separate resource pools

```typescript
const criticalPool = new PQueue({ concurrency: 10 });
const backgroundPool = new PQueue({ concurrency: 5 });
const reportsPool = new PQueue({ concurrency: 2 });
```

## Quick Checklist

- [ ] Circuit breakers on external integrations (S3, email, APIs)
- [ ] Retry with exponential backoff for transient failures
- [ ] Timeouts < 5s for external APIs
- [ ] Health checks (liveness + readiness)
- [ ] Graceful degradation for non-critical ops
- [ ] Bulkhead isolation for heavy operations
- [ ] Logging of circuit breaker states
- [ ] Fallbacks documented

## Common Use Cases

**S3 Integration**:
- Circuit breaker (5 failures → OPEN, 60s reset)
- Fallback: save locally
- Timeout: 30s

**Email Service**:
- Retry: 3 attempts, exponential backoff
- Graceful degradation: queue for later
- Timeout: 10s

**Payment Gateway**:
- Timeout: 5s (strict)
- Retry: 2 attempts max
- No graceful degradation (fail fast)

## Health Check Response

```json
{
  "status": "ok",
  "info": {
    "database": { "status": "up" },
    "s3": { "status": "up" },
    "redis": { "status": "up" }
  }
}
```

---

Ver SKILL.md para ejemplos completos de implementación con @nestjs/terminus.
