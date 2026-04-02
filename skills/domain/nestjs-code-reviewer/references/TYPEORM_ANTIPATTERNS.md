# TypeORM Anti-Patterns & Solutions

## 🚨 Performance Killers

### 1. N+1 Query Problem

**❌ ANTI-PATTERN**:
```typescript
// Genera 1 query inicial + N queries por cada usuario
const users = await this.userRepository.find();

for (const user of users) {
  const orders = await this.orderRepository.find({
    where: { userId: user.id }
  });
  user.orders = orders;
}
// Si hay 100 usuarios = 101 queries 😱
```

**✅ SOLUTION**:
```typescript
// 1 sola query con JOIN
const users = await this.userRepository.find({
  relations: ['orders']
});

// O con QueryBuilder para más control
const users = await this.userRepository
  .createQueryBuilder('user')
  .leftJoinAndSelect('user.orders', 'order')
  .getMany();
```

**📊 IMPACTO**: 100 usuarios = de 101 queries → 1 query (100x más rápido)

---

### 2. SELECT * en Queries Grandes

**❌ ANTI-PATTERN**:
```typescript
// Trae TODAS las columnas (incluyendo BLOBs)
const products = await this.productRepository.find();
```

**✅ SOLUTION**:
```typescript
// Solo columnas necesarias
const products = await this.productRepository
  .createQueryBuilder('product')
  .select(['product.id', 'product.name', 'product.price'])
  .getMany();

// O con select en find
const products = await this.productRepository.find({
  select: ['id', 'name', 'price']
});
```

**📊 IMPACTO**: De 10MB → 500KB de datos transferidos

---

### 3. Falta de Índices

**❌ ANTI-PATTERN**:
```typescript
@Entity()
export class User {
  @Column()
  email: string; // Sin índice

  @Column()
  username: string; // Sin índice
}

// Query lenta (full table scan)
const user = await repo.findOne({ where: { email } });
```

**✅ SOLUTION**:
```typescript
@Entity()
@Index(['email']) // Índice compuesto si buscas por múltiples
export class User {
  @Column()
  @Index({ unique: true })
  email: string;

  @Column()
  @Index()
  username: string;
}
```

**📊 IMPACTO**: Query de 2000ms → 5ms en 1M de registros

---

### 4. Eager Loading Excesivo

**❌ ANTI-PATTERN**:
```typescript
@Entity()
export class User {
  @OneToMany(() => Order, order => order.user, { eager: true })
  orders: Order[]; // SIEMPRE carga orders, incluso si no se usan

  @ManyToOne(() => Company, { eager: true })
  company: Company; // SIEMPRE carga company
}

// Aunque solo quieras el nombre, trae TODO
const users = await repo.find({ select: ['name'] });
// ⚠️ Ignora select, trae orders y company igual
```

**✅ SOLUTION**:
```typescript
@Entity()
export class User {
  @OneToMany(() => Order, order => order.user)
  orders: Order[]; // Lazy loading por defecto

  @ManyToOne(() => Company)
  company: Company;
}

// Cargar relaciones solo cuando se necesiten
const users = await repo.find({
  where: { active: true },
  relations: ['company'] // Solo company, no orders
});
```

---

### 5. Transacciones Missing

**❌ ANTI-PATTERN**:
```typescript
async transferMoney(fromId: string, toId: string, amount: number) {
  const from = await this.accountRepo.findOne(fromId);
  from.balance -= amount;
  await this.accountRepo.save(from);

  // ⚠️ Si falla aquí, el dinero desaparece
  const to = await this.accountRepo.findOne(toId);
  to.balance += amount;
  await this.accountRepo.save(to);
}
```

**✅ SOLUTION**:
```typescript
async transferMoney(fromId: string, toId: string, amount: number) {
  await this.dataSource.transaction(async (manager) => {
    await manager.decrement(Account, { id: fromId }, 'balance', amount);
    await manager.increment(Account, { id: toId }, 'balance', amount);
  });
  // Si cualquier operación falla, ROLLBACK automático
}
```

---

## 🔧 Bad Practices

### 6. Raw SQL Sin Parametrización

**❌ ANTI-PATTERN**:
```typescript
// SQL Injection vulnerable
const users = await this.dataSource.query(
  `SELECT * FROM users WHERE role = '${role}'`
);
```

**✅ SOLUTION**:
```typescript
// Parámetros seguros
const users = await this.dataSource.query(
  'SELECT * FROM users WHERE role = $1',
  [role]
);

// Mejor aún: QueryBuilder
const users = await this.userRepo
  .createQueryBuilder('user')
  .where('user.role = :role', { role })
  .getMany();
```

---

### 7. Find + Update (Race Condition)

**❌ ANTI-PATTERN**:
```typescript
async incrementViews(postId: string) {
  const post = await this.postRepo.findOne(postId);
  post.views += 1; // ⚠️ Race condition si 2 requests simultáneos
  await this.postRepo.save(post);
}
```

**✅ SOLUTION**:
```typescript
async incrementViews(postId: string) {
  // Operación atómica en DB
  await this.postRepo.increment({ id: postId }, 'views', 1);
}

// O con raw query
await this.postRepo
  .createQueryBuilder()
  .update()
  .set({ views: () => 'views + 1' })
  .where('id = :id', { id: postId })
  .execute();
```

---

### 8. No Usar Soft Delete

**❌ ANTI-PATTERN**:
```typescript
// Elimina permanentemente (irreversible)
await this.userRepo.delete(id);
```

**✅ SOLUTION**:
```typescript
@Entity()
export class User {
  @DeleteDateColumn()
  deletedAt?: Date;
}

// Soft delete (recuperable)
await this.userRepo.softDelete(id);

// Queries automáticamente ignoran soft deleted
const users = await this.userRepo.find(); // No incluye deleted

// Ver incluidos deleted
const all = await this.userRepo.find({ withDeleted: true });

// Recuperar
await this.userRepo.restore(id);
```

---

### 9. Connection Leaks

**❌ ANTI-PATTERN**:
```typescript
async getData() {
  const queryRunner = this.dataSource.createQueryRunner();
  await queryRunner.connect();

  const result = await queryRunner.query('SELECT ...');

  // ⚠️ Si hay error, nunca se libera la conexión
  await queryRunner.release();
  return result;
}
```

**✅ SOLUTION**:
```typescript
async getData() {
  const queryRunner = this.dataSource.createQueryRunner();
  await queryRunner.connect();

  try {
    const result = await queryRunner.query('SELECT ...');
    return result;
  } finally {
    await queryRunner.release(); // SIEMPRE se ejecuta
  }
}
```

---

### 10. Validación Solo en Frontend

**❌ ANTI-PATTERN**:
```typescript
@Entity()
export class User {
  @Column()
  email: string; // Sin validación

  @Column()
  age: number; // Sin constraints
}
```

**✅ SOLUTION**:
```typescript
import { IsEmail, Min, Max } from 'class-validator';

@Entity()
export class User {
  @Column()
  @IsEmail()
  email: string;

  @Column()
  @Min(0)
  @Max(150)
  age: number;

  // Constraints en DB también
  @Column({ type: 'varchar', length: 255 })
  @Index({ unique: true })
  email: string;
}
```

---

## 🎯 Architecture Anti-Patterns

### 11. Repository Inheritance Abuse

**❌ ANTI-PATTERN**:
```typescript
@EntityRepository(User)
export class UserRepository extends Repository<User> {
  // ⚠️ Deprecated en TypeORM 0.3+
}
```

**✅ SOLUTION**:
```typescript
@Injectable()
export class UserRepository {
  constructor(
    @InjectRepository(User)
    private repo: Repository<User>,
  ) {}

  async findByEmail(email: string): Promise<User> {
    return this.repo.findOne({ where: { email } });
  }

  // Métodos custom aquí
}
```

---

### 12. Anemic Domain Model

**❌ ANTI-PATTERN**:
```typescript
@Entity()
export class Order {
  @Column()
  status: string;

  @Column()
  total: number;
}

// Lógica de negocio en service (anemic model)
class OrderService {
  async approve(order: Order) {
    if (order.status === 'pending' && order.total > 0) {
      order.status = 'approved';
    }
  }
}
```

**✅ SOLUTION (Rich Domain Model)**:
```typescript
@Entity()
export class Order {
  @Column()
  status: OrderStatus;

  @Column()
  total: number;

  // Lógica de negocio en la entity
  approve(): void {
    if (this.status !== OrderStatus.PENDING) {
      throw new Error('Only pending orders can be approved');
    }
    if (this.total <= 0) {
      throw new Error('Order total must be positive');
    }
    this.status = OrderStatus.APPROVED;
  }

  canBeShipped(): boolean {
    return this.status === OrderStatus.APPROVED && this.total > 0;
  }
}

// Service delgado
class OrderService {
  async approve(orderId: string) {
    const order = await this.repo.findOne(orderId);
    order.approve(); // Validación dentro de la entity
    await this.repo.save(order);
  }
}
```

---

### 13. Cascades Peligrosos

**❌ ANTI-PATTERN**:
```typescript
@Entity()
export class User {
  @OneToMany(() => Order, order => order.user, {
    cascade: true, // ⚠️ Elimina TODOS los orders al borrar user
    onDelete: 'CASCADE'
  })
  orders: Order[];
}

// Si borras el user, pierdes órdenes sin querer
await this.userRepo.remove(user);
```

**✅ SOLUTION**:
```typescript
@Entity()
export class User {
  @OneToMany(() => Order, order => order.user, {
    cascade: ['insert', 'update'], // Solo operaciones seguras
    onDelete: 'RESTRICT' // Previene borrado si hay orders
  })
  orders: Order[];
}

// O usar soft delete
@DeleteDateColumn()
deletedAt?: Date;
```

---

## 📊 Monitoring Tips

### Query Logging
```typescript
// ormconfig.ts
{
  logging: ['query', 'error'],
  logger: 'advanced-console',
  maxQueryExecutionTime: 1000, // Alerta si >1s
}
```

### Slow Query Detection
```typescript
import { Logger } from '@nestjs/common';

@Injectable()
export class QueryLogger {
  private logger = new Logger('QueryLogger');

  logQuery(query: string, parameters: any[], queryRunner: QueryRunner) {
    const start = Date.now();

    return () => {
      const duration = Date.now() - start;
      if (duration > 100) {
        this.logger.warn(`Slow query (${duration}ms): ${query}`);
      }
    };
  }
}
```

---

## ✅ Best Practices Summary

1. **Siempre usar relaciones explícitas** (no eager por defecto)
2. **Índices en columnas de búsqueda frecuente**
3. **Transacciones para operaciones múltiples**
4. **QueryBuilder > Raw SQL** (seguridad + type-safety)
5. **Soft delete para datos críticos**
6. **Connection pooling configurado** (max: 10-20 en prod)
7. **Paginación obligatoria** en endpoints que retornan listas
8. **Validación en DTO + Entity + DB constraints**
9. **Monitoring de queries lentas** (>100ms)
10. **Rich domain models** (lógica de negocio en entities)
