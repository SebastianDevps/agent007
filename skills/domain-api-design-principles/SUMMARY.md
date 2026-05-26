# API Design Principles - Quick Reference

> **Full details**: See SKILL.md for complete implementation guides

## Core Principles

### RESTful Design
- **Resources** (nouns): `/users`, `/posts`, not `/getUser`
- **HTTP verbs**: GET (read), POST (create), PUT/PATCH (update), DELETE
- **Status codes**: 200 OK, 201 Created, 400 Bad Request, 404 Not Found, 500 Server Error

### Response Pattern (OBLIGATORIO)
```typescript
{
  status: 200 | 201 | 400 | 404 | 500,
  message: string,
  data?: T | T[]
}
```

## Quick Checklist

**Diseño**:
- [ ] Versionado (URL: `/api/v1/users` o headers)
- [ ] Paginación (cursor-based para escala)
- [ ] Rate limiting y throttling
- [ ] Autenticación y autorización (JWT, roles)
- [ ] Validación de input (class-validator DTOs)
- [ ] Manejo de errores consistente
- [ ] Documentación (OpenAPI/Swagger)
- [ ] Idempotencia para POST/PUT/DELETE

**Seguridad**:
- [ ] HTTPS only
- [ ] Input sanitization
- [ ] CORS configurado
- [ ] Rate limiting
- [ ] No secrets en responses

**Performance**:
- [ ] Caching headers (Cache-Control, ETag)
- [ ] Compression (gzip)
- [ ] Pagination (default limit: 20-50)
- [ ] Filtering + Sorting query params

## Endpoint Patterns

### Collection endpoints
```
GET    /api/v1/users              # List (paginated)
POST   /api/v1/users              # Create
GET    /api/v1/users/:id          # Get one
PUT    /api/v1/users/:id          # Replace
PATCH  /api/v1/users/:id          # Update
DELETE /api/v1/users/:id          # Delete
```

### Nested resources
```
GET /api/v1/users/:userId/posts           # User's posts
POST /api/v1/users/:userId/posts          # Create post for user
```

### Query parameters
```
GET /users?page=2&limit=20&sort=-createdAt&status=active
```

## Paginación (Cursor-based)

```typescript
// Request
GET /users?cursor=eyJpZCI6MTIzfQ&limit=20

// Response
{
  status: 200,
  message: "Users retrieved successfully",
  data: [...],
  pagination: {
    nextCursor: "eyJpZCI6MTQzfQ",
    prevCursor: "eyJpZCI6MTAzfQ",
    hasMore: true
  }
}
```

## Error Handling

```typescript
{
  status: 400,
  message: "Validation failed",
  errors: [
    {
      field: "email",
      message: "Email must be valid",
      code: "INVALID_EMAIL"
    }
  ]
}
```

## Idempotency

```typescript
// Client sends idempotency key
POST /api/v1/payments
Headers: { "Idempotency-Key": "uuid-123" }

// Server: same key = same response (no duplicate charge)
```

## Versioning Strategies

**URL-based** (recommended):
```
/api/v1/users
/api/v2/users
```

**Header-based**:
```
Headers: { "API-Version": "2" }
```

---

Ver SKILL.md para ejemplos completos de DTOs, validación, y NestJS implementation.
