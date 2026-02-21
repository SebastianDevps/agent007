# NestJS Code Reviewer Skill

Skill especializado para revisar código NestJS + TypeORM con enfoque en seguridad, performance y mejores prácticas.

## 📦 Instalación

### En Claude Code:
```bash
# Copiar el skill a la carpeta de skills
cp -r nestjs-code-reviewer ~/.claude/skills/

# El skill se activará automáticamente cuando menciones:
# - "revisar código"
# - "code review"
# - "auditar seguridad"
# - "optimizar queries"
```

### En Cursor/VS Code:
```bash
# Agregar a .cursor/skills/ o .vscode/skills/
```

## 🎯 Casos de Uso

### 1. Review Completo de Módulo
```
Usuario: "Revisa el módulo de usuarios"

Agent:
- Lee src/users/users.controller.ts
- Lee src/users/users.service.ts
- Lee src/users/entities/user.entity.ts
- Aplica checklist de SKILL.md
- Genera reporte con issues encontrados
```

### 2. Auditoría de Seguridad
```
Usuario: "Audita seguridad en el código de autenticación"

Agent:
- Activa skill nestjs-code-reviewer
- Consulta references/SECURITY_CHECKLIST.md
- Busca vulnerabilidades OWASP
- Reporta findings críticos
```

### 3. Optimización de Queries
```
Usuario: "Optimiza las queries del módulo de productos"

Agent:
- Activa skill
- Consulta references/TYPEORM_ANTIPATTERNS.md
- Identifica N+1 queries
- Sugiere refactors con eager loading
```

### 4. Análisis Estático Rápido
```bash
# Ejecutar script de análisis
node .claude/skills/nestjs-code-reviewer/scripts/analyze.js src/
```

## 📚 Estructura

```
nestjs-code-reviewer/
├── SKILL.md                          # ⭐ Instrucciones principales
├── README.md                         # Esta guía
├── scripts/
│   └── analyze.js                    # Análisis estático automatizado
└── references/
    ├── SECURITY_CHECKLIST.md         # OWASP Top 10 para NestJS
    └── TYPEORM_ANTIPATTERNS.md       # Anti-patterns comunes TypeORM
```

## 🔍 Qué Revisa

### Seguridad (OWASP Top 10)
- ✅ SQL Injection
- ✅ XSS / Mass Assignment
- ✅ Broken Access Control (Guards missing)
- ✅ Cryptographic failures (passwords sin hash)
- ✅ CORS misconfiguration
- ✅ Sensitive data exposure

### Performance
- ✅ N+1 Queries
- ✅ Missing indexes
- ✅ Eager loading excesivo
- ✅ SELECT * en queries grandes
- ✅ Falta de paginación
- ✅ Connection leaks

### Arquitectura
- ✅ Separación de responsabilidades (Controller/Service)
- ✅ Uso correcto de DTOs
- ✅ Inyección de dependencias
- ✅ Manejo de errores
- ✅ Transacciones en operaciones críticas

### Code Quality
- ✅ TypeScript strict mode
- ✅ Tipos explícitos (no `any`)
- ✅ Async/await correcto
- ✅ Error handling
- ✅ Logging apropiado

## 📝 Formato de Reporte

```markdown
# Code Review: Módulo de Usuarios

## 📊 Resumen
- Archivos revisados: 3
- Issues críticos: 2
- Mejoras sugeridas: 5
- Score de calidad: B

## 🔴 Issues Críticos

### 1. SQL Injection Vulnerable
**Archivo**: `src/users/users.service.ts:42`

❌ ANTES:
```typescript
const users = await this.repo.query(
  `SELECT * FROM users WHERE role = '${role}'`
);
```

✅ DESPUÉS:
```typescript
const users = await this.repo.query(
  'SELECT * FROM users WHERE role = $1',
  [role]
);
```

📝 RAZÓN: String interpolation permite SQL injection. Usar parámetros preparados.

---

### 2. Password Sin Hash
**Archivo**: `src/auth/auth.service.ts:28`

❌ ANTES:
```typescript
user.password = newPassword;
await this.userRepo.save(user);
```

✅ DESPUÉS:
```typescript
user.password = await bcrypt.hash(newPassword, 12);
await this.userRepo.save(user);
```

📝 RAZÓN: Passwords deben hashearse antes de guardar en DB.

## 🟡 Mejoras Recomendadas

### 1. N+1 Query Pattern
**Archivo**: `src/users/users.service.ts:15`

Usar eager loading o joins para evitar múltiples queries...

## ✅ Aspectos Positivos

- ✅ DTOs correctamente validados con class-validator
- ✅ Guards aplicados en endpoints críticos
- ✅ Uso de transacciones en transferencias
```

## 🚀 Ejemplo de Uso

### Escenario: Revisar un controlador nuevo

```typescript
// src/products/products.controller.ts
@Controller('products')
export class ProductsController {
  constructor(private productsService: ProductsService) {}

  @Get()
  async findAll(@Query() query: any) { // ⚠️ any type
    return this.productsService.findAll(); // ⚠️ sin paginación
  }

  @Delete(':id')  // ⚠️ sin guards
  async remove(@Param('id') id: string) {
    return this.productsService.remove(id);
  }
}
```

**Prompt**:
```
Revisa el código de products.controller.ts
```

**Agent activará el skill y reportará**:
- ❌ Query parameter con tipo `any`
- ❌ Endpoint DELETE sin guards
- ⚠️ findAll sin paginación

## 🛠️ Personalización

### Agregar Reglas Custom

Edita `SKILL.md` y agrega en la sección "Review Checklist":

```markdown
### 7. Reglas Específicas del Proyecto

**Naming Convention**:
- ✅ Entities deben terminar en `.entity.ts`
- ✅ DTOs deben terminar en `.dto.ts`
- ✅ Services exportan interface `I{ServiceName}`
```

### Agregar Scripts

Crea nuevos scripts en `/scripts/`:

```bash
# scripts/check-dependencies.sh
npm audit --audit-level=moderate
npm outdated
```

Referencia en SKILL.md:
```markdown
## Dependencias
Ejecuta: `bash scripts/check-dependencies.sh`
```

## 🎓 Tips de Uso

1. **Review incremental**: Revisa módulo por módulo, no todo el proyecto de una vez
2. **Prioriza críticos**: Fija primero SQL injection, auth issues, etc.
3. **Contexto importa**: No todos los `any` son malos (ej: decorators de Swagger)
4. **Automatiza**: Ejecuta `analyze.js` en CI/CD para prevención

## 📖 Referencias Externas

- [NestJS Security Best Practices](https://docs.nestjs.com/security/authentication)
- [TypeORM Performance Tips](https://typeorm.io/find-options)
- [OWASP Top 10 2021](https://owasp.org/Top10/)

## 🤝 Contribuir

Mejoras bienvenidas:
1. Agrega nuevos patterns en `SKILL.md`
2. Mejora el script de análisis en `scripts/analyze.js`
3. Expande referencias con más ejemplos

## 📄 Licencia

MIT - Usa libremente en proyectos comerciales y open source
