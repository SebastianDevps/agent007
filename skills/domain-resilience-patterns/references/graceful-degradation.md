# Graceful Degradation

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
