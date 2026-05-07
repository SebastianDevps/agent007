# Separación DTOs vs Types vs Interfaces

## DTOs (Data Transfer Objects)

- Para **validación de entrada** (request body, query params)
- Usan `class-validator`
- Van en `dto/`

```typescript
// dto/create-cutoff.dto.ts
export class CreateCutoffDto {
  @IsUUID('4', { message: 'El periodId debe ser un UUID válido' })
  @IsNotEmpty({ message: 'El periodId es requerido' })
  periodId: string;

  @IsOptional()
  @IsString({ message: 'Las notas deben ser texto' })
  @MaxLength(500, { message: 'Las notas no pueden exceder 500 caracteres' })
  notes?: string;
}
```

## Types (TypeScript types)

- Para **respuestas de API** (OBLIGATORIO patrón `{ status, message, data }`)
- Para **tipado interno**
- Van en `types/`

```typescript
// types/cutoff-response.type.ts
export type CutoffCreatedResponse = {
  status: 201;
  message: string;
  data: CutoffData;
};

export type CutoffResponse = {
  status: number;
  message: string;
  data?: CutoffData | CutoffData[];
};

export type CutoffData = {
  id: string;
  periodId: string;
  status: string;
  notes?: string;
  createdAt: string;
  updatedAt: string;
};
```

## Interfaces (Contratos)

- Para **contratos de servicios**
- Para **inyección de dependencias**
- Van en `interfaces/`

```typescript
// interfaces/cutoff-repository.interface.ts
export interface ICutoffRepository {
  findById(id: string): Promise<Cutoff | null>;
  save(cutoff: Cutoff): Promise<Cutoff>;
}
```
