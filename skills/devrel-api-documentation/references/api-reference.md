# API Reference Templates

Templates for the per-endpoint reference section.

## Base URL & Response Format

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
```

---

## Endpoint — List Resources

```markdown
### List [Resources]

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
```

---

## Endpoint — Create Resource

```markdown
### Create [Resource]

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
