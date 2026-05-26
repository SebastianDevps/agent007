# Health Checks

**Problema**: No hay visibilidad del estado de dependencias externas.

**Solución**: Endpoints de salud que verifican todas las integraciones.

## Implementación con @nestjs/terminus

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

## Response de health check

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
