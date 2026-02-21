---
name: developer-portal
description: "Crear developer portal: getting started, tutorials, SDK guides. Para onboarding de developers."
invokable: true
accepts_args: true
auto-activate: false
version: 1.0.0
when:
  - user_mentions: ["developer portal", "getting started", "tutorial", "sdk", "onboarding developers"]
---

# Developer Portal - Developer Onboarding Experience

**Propósito**: Crear un portal de desarrollo que minimice el time-to-first-value para developers que integran con tu API.

---

## Estructura del Developer Portal

```
Developer Portal
├── 🏠 Home / Overview
│   ├── Value proposition
│   ├── Quick start CTA
│   └── Feature highlights
│
├── 🚀 Getting Started
│   ├── Quick Start (5 min)
│   ├── Authentication
│   ├── Making requests
│   └── Handling errors
│
├── 📖 Guides
│   ├── [Use case 1] tutorial
│   ├── [Use case 2] tutorial
│   ├── Webhooks guide
│   ├── Pagination guide
│   └── Rate limiting guide
│
├── 📋 API Reference
│   ├── Authentication
│   ├── [Resource 1]
│   ├── [Resource 2]
│   └── Error codes
│
├── 🔧 SDKs & Libraries
│   ├── JavaScript/TypeScript
│   ├── Python
│   ├── Go
│   └── Community libraries
│
├── 📝 Changelog
│   ├── Latest changes
│   ├── Breaking changes
│   └── Migration guides
│
└── 💬 Support
    ├── FAQ
    ├── Community forum
    └── Contact support
```

---

## Content Templates

### Home Page

```markdown
# [Product] API

Build [value proposition] with our API.

## Why [Product]?
- ✅ [Benefit 1]: [Description]
- ✅ [Benefit 2]: [Description]
- ✅ [Benefit 3]: [Description]

## Get Started in 5 Minutes
[Quick Start button → /getting-started]

## Popular Use Cases
- 🔗 [Use case 1]
- 🔗 [Use case 2]
- 🔗 [Use case 3]

## SDKs
| Language | Install |
|----------|---------|
| Node.js | `npm install @yourapp/sdk` |
| Python | `pip install yourapp` |
| Go | `go get github.com/yourapp/go-sdk` |
```

---

### Tutorial Template

```markdown
# Tutorial: [Goal]

**Time**: ~15 minutes
**Prerequisites**: API key, Node.js 18+

## What you'll build
[Description of end result]

## Step 1: Setup

Install the SDK:
```bash
npm install @yourapp/sdk
```

Create a file `app.js`:
```javascript
const { YourApp } = require('@yourapp/sdk');

const client = new YourApp({
  apiKey: process.env.YOURAPP_API_KEY
});
```

## Step 2: [First action]

[Explanation of what this step does]

```javascript
// Code that works when copy-pasted
const result = await client.resources.create({
  name: 'My Resource',
  type: 'example'
});

console.log('Created:', result.id);
```

**Expected output:**
```
Created: res_abc123
```

## Step 3: [Next action]

[Continue building on previous step]

## Complete Code

[Full working example]

## Next Steps
- [Related tutorial 1]
- [Related tutorial 2]
- [API Reference]
```

---

### SDK Design Template

```typescript
// SDK Design Principles:
// 1. Type-safe (full TypeScript support)
// 2. Idiomatic (follows language conventions)
// 3. Minimal dependencies
// 4. Clear error handling
// 5. Auto-pagination support

// Example SDK structure
import { YourApp } from '@yourapp/sdk';

// Initialize
const client = new YourApp({
  apiKey: 'sk_live_...',
  baseUrl: 'https://api.yourapp.com/v1', // optional
  timeout: 30000, // optional, default 30s
});

// CRUD operations (typed)
const user = await client.users.create({
  email: 'dev@example.com',
  name: 'Developer',
});

const users = await client.users.list({
  page: 1,
  limit: 10,
  status: 'active',
});

const user = await client.users.get('usr_abc123');

const updated = await client.users.update('usr_abc123', {
  name: 'Updated Name',
});

await client.users.delete('usr_abc123');

// Auto-pagination
for await (const user of client.users.listAll()) {
  console.log(user.id);
}

// Error handling
try {
  await client.users.create({ email: 'invalid' });
} catch (error) {
  if (error instanceof YourApp.ValidationError) {
    console.log(error.errors); // ['email must be valid']
  } else if (error instanceof YourApp.AuthenticationError) {
    console.log('Check your API key');
  } else if (error instanceof YourApp.RateLimitError) {
    console.log(`Retry after ${error.retryAfter} seconds`);
  }
}
```

---

## Developer Experience Metrics

### Quantitative
| Metric | Target | How to measure |
|--------|--------|---------------|
| Time to first API call | < 5 min | Track from docs page view to first API request |
| Quick start completion | > 60% | Analytics funnel |
| Docs search success | > 80% | Search analytics (found vs not found) |
| Support tickets | < 10/week | Ticket count |
| SDK adoption | > 50% | Track User-Agent headers |

### Qualitative
- Developer satisfaction surveys (quarterly)
- User interviews (monthly)
- GitHub issues / discussions sentiment
- Community feedback

---

## Checklist: Developer Portal Completo

### Must Have
- [ ] Quick start guide (< 10 min to first API call)
- [ ] Authentication documentation
- [ ] API reference for all endpoints
- [ ] Error catalog with fix suggestions
- [ ] At least 1 SDK (JavaScript/TypeScript)
- [ ] Search functionality
- [ ] Changelog

### Should Have
- [ ] 2+ tutorials for common use cases
- [ ] Interactive API playground (try it now)
- [ ] Multiple SDKs (Python, Go)
- [ ] Webhook documentation
- [ ] Rate limiting guide
- [ ] Postman/Insomnia collection

### Nice to Have
- [ ] Community forum / Discord
- [ ] Status page integration
- [ ] SDK auto-generation from OpenAPI
- [ ] Code samples in 3+ languages
- [ ] Video tutorials

---

**Next Step**: Start with Quick Start + API Reference → Add tutorials → Build SDK
