# Manejo de Errores Consistente

## Estructura estándar de error

```typescript
// types/error-response.type.ts
export type ErrorResponse = {
  statusCode: number;
  message: string;
  errors?: string[];       // Errores de validación
  timestamp: string;
  path: string;
  method: string;
};

// filters/http-exception.filter.ts
@Catch()
export class AllExceptionsFilter implements ExceptionFilter {
  catch(exception: unknown, host: ArgumentsHost) {
    const ctx = host.switchToHttp();
    const response = ctx.getResponse<Response>();
    const request = ctx.getRequest<Request>();

    const status = exception instanceof HttpException
      ? exception.getStatus()
      : 500;

    const errorResponse: ErrorResponse = {
      statusCode: status,
      message: this.getErrorMessage(exception),
      errors: this.getValidationErrors(exception),
      timestamp: new Date().toISOString(),
      path: request.url,
      method: request.method
    };

    this.logger.error(
      `${request.method} ${request.url} - ${status}`,
      exception instanceof Error ? exception.stack : ''
    );

    response.status(status).json(errorResponse);
  }

  private getErrorMessage(exception: unknown): string {
    if (exception instanceof HttpException) {
      const response = exception.getResponse();
      return typeof response === 'string' ? response : (response as any).message;
    }
    return 'Error interno del servidor';
  }

  private getValidationErrors(exception: unknown): string[] | undefined {
    if (exception instanceof BadRequestException) {
      const response = exception.getResponse() as any;
      if (Array.isArray(response.message)) {
        return response.message;
      }
    }
    return undefined;
  }
}
```

## Uso en servicios

```typescript
@Injectable()
export class CutoffsService {
  async findOne(id: string): Promise<CutoffResponse> {
    const cutoff = await this.cutoffRepository.findOne({ where: { id } });

    if (!cutoff) {
      throw new NotFoundException(`Corte con ID ${id} no encontrado`);
    }

    return {
      status: 200,
      message: 'Corte obtenido exitosamente',
      data: this.mapToData(cutoff)
    };
  }

  async create(dto: CreateCutoffDto): Promise<CutoffCreatedResponse> {
    // Validar duplicados
    const existing = await this.cutoffRepository.findOne({
      where: { periodId: dto.periodId, status: CutoffStatus.ACTIVE }
    });

    if (existing) {
      throw new ConflictException(
        `Ya existe un corte activo para el período ${dto.periodId}`
      );
    }

    const cutoff = this.cutoffRepository.create(dto);
    const saved = await this.cutoffRepository.save(cutoff);

    return {
      status: 201,
      message: 'Corte creado exitosamente',
      data: this.mapToData(saved)
    };
  }
}
```
