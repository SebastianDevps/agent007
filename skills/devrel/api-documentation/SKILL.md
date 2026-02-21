---
name: api-documentation
description: "Crear documentación de API: OpenAPI specs, guides, error catalogs. Para developer experience."
invokable: true
accepts_args: true
auto-activate: false
version: 1.0.0
when:
  - task_type: documentation
  - user_mentions: ["api docs", "documentation", "openapi", "swagger", "developer portal"]
---

# API Documentation - Developer-First Documentation

**Propósito**: Crear documentación de API que permita a developers obtener valor en menos de 10 minutos.

---

## Estructura de Documentación (Diátaxis)

### 1. Quick Start (PRIORIDAD #1)

```markdown
# Quick Start

Get up and running in 5 minutes.

## 1. Get your API key

1. Go to [Settings > API Keys](link)
2. Click "Create API Key"
3. Copy your key (starts with `sk_live_`)

> ⚠️ Keep your API key secret. Never share it in client-side code.

## 2. Make your first request

```bash
curl https://api.yourapp.com/v1/users \
  -H "Authorization: Bearer sk_live_YOUR_API_KEY" \
  -H "Content-Type: application/json"
```

## 3. Create a resource

```bash
curl -X POST https://api.yourapp.com/v1/projects \
  -H "Authorization: Bearer sk_live_YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "My First Project",
    "description": "Created via API"
  }'
```

**Response:**
```json
{
  "status": 201,
  "message": "Project created successfully",
  "data": {
    "id": "proj_abc123",
    "name": "My First Project",
    "createdAt": "2026-02-16T10:00:00Z"
  }
}
```

## Next Steps
- [Authentication Guide](#authentication)
- [API Reference](#reference)
- [SDKs](#sdks)
```

---

### 2. Authentication Guide

```markdown
# Authentication

All API requests require authentication via Bearer token.

## API Keys

Include your API key in the `Authorization` header:

```
Authorization: Bearer sk_live_YOUR_API_KEY
```

### Key Types

| Type | Prefix | Use for |
|------|--------|---------|
| Live | `sk_live_` | Production requests |
| Test | `sk_test_` | Development & testing |

### Security Best Practices

✅ **DO:**
- Store keys in environment variables
- Use test keys in development
- Rotate keys periodically
- Use server-side requests only

❌ **DON'T:**
- Hardcode keys in source code
- Commit keys to version control
- Use keys in client-side JavaScript
- Share keys via Slack/email
```

---

### 3. API Reference (per endpoint)

```markdown
# API Reference

## Base URL

```
https://api.yourapp.com/v1
```

## Response Format

All responses follow this structure:

**Success:**
```json
{
  "status": 200,
  "message": "Description of result",
  "data": { ... }
}
```

**Error:**
```json
{
  "statusCode": 400,
  "message": "What went wrong",
  "errors": ["Specific error 1", "Specific error 2"],
  "timestamp": "2026-02-16T10:00:00Z",
  "path": "/api/v1/users",
  "method": "POST"
}
```

## Pagination

List endpoints return paginated results:

```json
{
  "data": [...],
  "meta": {
    "page": 1,
    "limit": 10,
    "total": 45,
    "totalPages": 5,
    "hasNextPage": true,
    "hasPreviousPage": false
  }
}
```

Query parameters:
- `page` (default: 1) - Page number
- `limit` (default: 10, max: 100) - Items per page

---

## Endpoints

### [Resource Name]

#### List [Resources]

`GET /[resources]`

Returns a paginated list of [resources].

**Query Parameters:**
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| page | integer | No | Page number (default: 1) |
| limit | integer | No | Items per page (default: 10, max: 100) |
| status | string | No | Filter by status |
| sortBy | string | No | Sort field (default: createdAt) |
| sortOrder | string | No | ASC or DESC (default: DESC) |

**Example Request:**
```bash
curl "https://api.yourapp.com/v1/[resources]?page=1&limit=10&status=active" \
  -H "Authorization: Bearer sk_live_YOUR_API_KEY"
```

**Example Response (200):**
```json
{
  "status": 200,
  "message": "[Resources] retrieved successfully",
  "data": [
    {
      "id": "res_abc123",
      "name": "Example Resource",
      "status": "active",
      "createdAt": "2026-02-16T10:00:00Z"
    }
  ],
  "meta": {
    "page": 1,
    "limit": 10,
    "total": 1,
    "totalPages": 1,
    "hasNextPage": false,
    "hasPreviousPage": false
  }
}
```

#### Create [Resource]

`POST /[resources]`

Creates a new [resource].

**Request Body:**
| Field | Type | Required | Description |
|-------|------|----------|-------------|
| name | string | Yes | Resource name (3-100 chars) |
| description | string | No | Optional description |

**Example Request:**
```bash
curl -X POST "https://api.yourapp.com/v1/[resources]" \
  -H "Authorization: Bearer sk_live_YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"name": "New Resource", "description": "Created via API"}'
```

**Responses:**
| Status | Description |
|--------|-------------|
| 201 | Resource created successfully |
| 400 | Validation error (see errors array) |
| 401 | Invalid or missing API key |
| 409 | Resource with this name already exists |
```

---

### 4. Error Catalog

```markdown
# Error Reference

## Error Response Format

```json
{
  "statusCode": 400,
  "message": "Human-readable error message",
  "errors": ["Specific validation error"],
  "timestamp": "ISO 8601 timestamp",
  "path": "/api/v1/endpoint",
  "method": "POST"
}
```

## Common Errors

### Authentication Errors (401)

| Error | Message | Fix |
|-------|---------|-----|
| INVALID_API_KEY | "Invalid API key" | Check your API key in Settings |
| EXPIRED_API_KEY | "API key has expired" | Generate a new key |
| MISSING_AUTH | "Authorization header required" | Add `Authorization: Bearer sk_...` |

### Authorization Errors (403)

| Error | Message | Fix |
|-------|---------|-----|
| INSUFFICIENT_PERMISSIONS | "You don't have permission" | Check your role/permissions |
| RESOURCE_FORBIDDEN | "Cannot access this resource" | Verify resource ownership |

### Validation Errors (400)

| Error | Message | Fix |
|-------|---------|-----|
| MISSING_FIELD | "Field '{field}' is required" | Include all required fields |
| INVALID_FORMAT | "'{field}' must be a valid {type}" | Check field type requirements |
| VALUE_TOO_LONG | "'{field}' exceeds max length" | Reduce field value length |

### Rate Limiting (429)

| Error | Message | Fix |
|-------|---------|-----|
| RATE_LIMITED | "Too many requests" | Wait and retry with exponential backoff |

**Rate Limit Headers:**
```
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 0
X-RateLimit-Reset: 1708083600
Retry-After: 60
```
```

---

## Process: Documentar un Módulo

### Input
Nombre del módulo a documentar (ej: "users", "projects", "payments")

### Steps

1. **Read controller**: Identify all endpoints, DTOs, responses
2. **Read service**: Understand business logic, validations, errors
3. **Read DTOs**: Extract field definitions, validations
4. **Generate OpenAPI**: Create or update spec
5. **Write examples**: curl + response for each endpoint
6. **Document errors**: All possible error scenarios
7. **Create guide**: How-to for common use cases

---

## Quality Checklist

- [ ] **Quick start works** in < 10 minutes (tested)
- [ ] **Every endpoint** has working curl example
- [ ] **Every endpoint** has example response
- [ ] **All error codes** documented with fix suggestions
- [ ] **Authentication** clearly explained with security warnings
- [ ] **Rate limits** documented
- [ ] **Pagination** pattern documented
- [ ] **Examples use realistic data** (not foo/bar)
- [ ] **OpenAPI spec** matches actual implementation
- [ ] **Changelog** exists for breaking changes

---

**Next Step**: Generate OpenAPI spec from code → Create static site → Deploy developer portal
