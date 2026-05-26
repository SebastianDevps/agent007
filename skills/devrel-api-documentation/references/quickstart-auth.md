# Quick Start + Authentication — Templates

Templates for the first two sections of any API documentation set.

## 1. Quick Start (PRIORIDAD #1)

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

## 2. Authentication Guide

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
