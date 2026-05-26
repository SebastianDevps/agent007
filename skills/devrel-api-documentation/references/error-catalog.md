# Error Catalog Template

Template for the error-reference section of any API documentation set.

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
