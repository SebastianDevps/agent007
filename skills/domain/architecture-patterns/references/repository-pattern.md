# Repository Pattern

Interfaz de repositorio (opcional, pero recomendado para testabilidad).

```typescript
// src/modules/payroll-context/cutoffs/interfaces/cutoff-repository.interface.ts
export interface ICutoffRepository {
  findById(id: string): Promise<Cutoff | null>;
  findByPeriod(periodId: string): Promise<Cutoff[]>;
  save(cutoff: Cutoff): Promise<Cutoff>;
  delete(id: string): Promise<void>;
}

// Implementación con TypeORM
@Injectable()
export class CutoffRepository implements ICutoffRepository {
  constructor(
    @InjectRepository(Cutoff)
    private readonly repository: Repository<Cutoff>
  ) {}

  async findById(id: string): Promise<Cutoff | null> {
    return this.repository.findOne({ where: { id } });
  }

  async findByPeriod(periodId: string): Promise<Cutoff[]> {
    return this.repository.find({ where: { periodId } });
  }

  async save(cutoff: Cutoff): Promise<Cutoff> {
    return this.repository.save(cutoff);
  }

  async delete(id: string): Promise<void> {
    await this.repository.delete(id);
  }
}

// Servicio usa la interfaz
@Injectable()
export class CutoffsService {
  constructor(
    @Inject('ICutoffRepository')
    private readonly cutoffRepository: ICutoffRepository
  ) {}
}
```
