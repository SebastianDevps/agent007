# Security & OWASP — NestJS Reference

Detailed code samples for the security portion of the NestJS review checklist (OWASP Top 10).

## 3. Seguridad (OWASP Top 10)

### SQL Injection (A03:2021)

```typescript
// ❌ CRÍTICO: SQL injection
await this.repo.query(`SELECT * FROM users WHERE id = ${userId}`);

// ✅ SEGURO: Parámetros preparados
await this.repo.query('SELECT * FROM users WHERE id = $1', [userId]);
```

### Auth & AuthZ (A01:2021)

```typescript
// ❌ MAL: Sin guards
@Delete(':id')
async delete(@Param('id') id: string) { ... }

// ✅ BIEN: Guards + validación de ownership
@UseGuards(JwtAuthGuard, OwnershipGuard)
@Delete(':id')
async delete(@Param('id') id: string, @CurrentUser() user: User) { ... }
```

### Sensitive Data Exposure (A02:2021)

- ❌ No retornar passwords en respuestas (usar `@Exclude()` en entities)
- ✅ Usar bcrypt/argon2 para hash (min 10 rounds)
- ✅ Variables sensibles en `.env`, nunca hardcodeadas

### Mass Assignment

```typescript
// ❌ VULNERABLE: Acepta cualquier campo
@Post()
create(@Body() data: any) {
  return this.repo.save(data); // Puede modificar "isAdmin"
}

// ✅ SEGURO: DTO estricto + whitelist
@Post()
create(@Body() dto: CreateUserDto) { // Solo campos permitidos
  return this.service.create(dto);
}
```

---

Para checklist completo OWASP ver: `references/SECURITY_CHECKLIST.md`.
