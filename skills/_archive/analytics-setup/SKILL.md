---
name: analytics-setup
description: "Configurar analytics: event taxonomy, métricas, dashboards. Para tracking de producto."
invokable: true
accepts_args: true
auto-activate: false
version: 1.0.0
when:
  - task_type: analytics
  - user_mentions: ["analytics", "tracking", "metrics", "events", "dashboard", "funnel"]
---

# Analytics Setup - Product Metrics & Event Tracking

**Propósito**: Configurar analytics correctamente desde el inicio. Definir métricas, eventos y dashboards para tomar decisiones basadas en datos.

---

## Proceso de Setup

### Fase 1: Define Business Questions

```markdown
**Q1: ¿Qué preguntas de negocio necesitamos responder?**

Categorías comunes:
  - Acquisition: ¿De dónde vienen los usuarios?
  - Activation: ¿Tienen una primera experiencia valiosa?
  - Engagement: ¿Con qué frecuencia usan el producto?
  - Retention: ¿Vuelven después de la primera semana?
  - Revenue: ¿Están pagando? ¿Cuánto?
  - Referral: ¿Recomiendan a otros?

[Wait for answer]

**Q2: ¿Quién consume estos datos?**
  A) CEO/Founders (high-level KPIs)
  B) Product Manager (feature usage, funnels)
  C) Engineering (performance, errors)
  D) Marketing (acquisition, campaigns)
  E) All of the above

[Wait for answer]
```

---

### Fase 2: Define Key Metrics

```markdown
## North Star Metric

La métrica que mejor representa valor entregado al usuario.

Ejemplos por tipo de producto:
- SaaS B2B: "Weekly active teams" o "Tasks completed per week"
- Marketplace: "Transactions completed per week"
- Social: "Daily active users" o "Posts created per day"
- E-commerce: "Weekly purchases"
- Dev tools: "API calls per week" o "Deployments per week"

**Tu North Star**: _______________

## Input Metrics (alimentan la North Star)

| Metric | Formula | Target | Owner |
|--------|---------|--------|-------|
| Signup Rate | New signups / visitors | 5% | Marketing |
| Activation Rate | Activated / signups | 40% | Product |
| D7 Retention | Active day 7 / signups | 25% | Product |
| Engagement | Actions per session | 5 | Product |

## Guardrail Metrics (no deben empeorar)

| Metric | Threshold | Alert if |
|--------|-----------|----------|
| Error rate | < 1% | > 2% |
| Page load time | < 2s | > 3s |
| Support tickets | < 50/week | > 100/week |
```

---

### Fase 3: Design Event Taxonomy

```markdown
## Naming Convention

**Format**: `object_action` (snake_case)
**Language**: English
**Tense**: Past tense for completed actions

### Core Events (Track ALWAYS)

#### User Lifecycle
| Event | Trigger | Properties |
|-------|---------|-----------|
| user_signed_up | POST /auth/register | source, plan |
| user_logged_in | POST /auth/login | method (email, google, github) |
| user_activated | First key action completed | activation_action |
| user_upgraded | Plan change to paid | plan_from, plan_to, mrr |
| user_churned | Subscription cancelled | reason, plan, lifetime_days |

#### Core Product Actions
| Event | Trigger | Properties |
|-------|---------|-----------|
| [object]_created | POST /[objects] | object_type, properties_count |
| [object]_updated | PATCH /[objects]/:id | fields_changed |
| [object]_deleted | DELETE /[objects]/:id | object_age_days |
| [object]_viewed | GET /[objects]/:id | source (list, search, link) |

#### UI Interactions
| Event | Trigger | Properties |
|-------|---------|-----------|
| page_viewed | Route change | page_name, referrer |
| button_clicked | Click on CTA | button_name, page, section |
| search_performed | Search submit | query, results_count |
| feature_used | Key feature interaction | feature_name, context |

### Standard Properties (incluir en TODOS los eventos)

```javascript
// Auto-captured (SDK handles)
{
  timestamp: "2026-02-16T10:30:00Z",  // ISO 8601
  user_id: "usr_abc123",               // After identification
  anonymous_id: "anon_xyz789",          // Before identification
  session_id: "sess_def456",
  platform: "web",                      // web, ios, android
  device_type: "desktop",               // desktop, tablet, mobile
  browser: "Chrome 120",
  os: "macOS 14.2"
}

// Business context (add manually)
{
  plan: "pro",                          // User's current plan
  team_id: "team_abc",                  // For B2B
  feature_flag: "new_dashboard_v2"      // If in experiment
}
```
```

---

### Fase 4: Implementation Plan

```markdown
## Backend Implementation (Server-Side)

### Critical Events (MUST be server-side)
- user_signed_up, user_upgraded, user_churned
- payment_completed, subscription_renewed
- Any event tied to business metrics

### Pattern (NestJS)
```typescript
// analytics/analytics.service.ts
@Injectable()
export class AnalyticsService {
  track(event: string, userId: string, properties: Record<string, any>) {
    // Send to analytics provider
    // Include: timestamp, user context, event properties
  }

  identify(userId: string, traits: Record<string, any>) {
    // Update user profile in analytics
    // Include: email, name, plan, signup_date
  }
}

// Usage in services
@Injectable()
export class UsersService {
  constructor(private analytics: AnalyticsService) {}

  async register(dto: RegisterDto) {
    const user = await this.userRepo.save(dto);

    this.analytics.identify(user.id, {
      email: user.email,
      name: user.name,
      plan: 'free',
      signed_up_at: new Date().toISOString()
    });

    this.analytics.track('user_signed_up', user.id, {
      source: dto.source,
      method: dto.method
    });

    return user;
  }
}
```

## Frontend Implementation (Client-Side)

### UI Interaction Events
- page_viewed, button_clicked, search_performed
- Form interactions, feature usage

### Pattern (React/Next.js)
```typescript
// hooks/useAnalytics.ts
export function useAnalytics() {
  const track = (event: string, properties?: Record<string, any>) => {
    analytics.track(event, {
      ...properties,
      page: window.location.pathname
    });
  };

  const page = (name: string) => {
    analytics.page(name);
  };

  return { track, page };
}

// Usage in components
function DashboardPage() {
  const { track, page } = useAnalytics();

  useEffect(() => {
    page('Dashboard');
  }, []);

  return (
    <Button onClick={() => {
      track('button_clicked', { button_name: 'create_project' });
      createProject();
    }}>
      Create Project
    </Button>
  );
}
```
```

---

### Fase 5: Dashboard Design

```markdown
## Executive Dashboard
Show to: CEO, Founders

| KPI | Visualization | Timeframe |
|-----|--------------|-----------|
| North Star Metric | Big number + trend line | Weekly |
| Revenue (MRR) | Line chart | Monthly |
| Active Users (DAU/WAU/MAU) | Line chart | Daily |
| Signup → Activation funnel | Funnel chart | Weekly |
| Churn Rate | Line chart | Monthly |

## Product Dashboard
Show to: Product Manager

| KPI | Visualization | Timeframe |
|-----|--------------|-----------|
| Feature adoption rates | Bar chart | Weekly |
| User engagement by feature | Heatmap | Weekly |
| Activation funnel (detailed) | Funnel chart | Daily |
| Retention cohorts | Cohort table | Weekly |
| Error rates by feature | Table | Daily |

## Engineering Dashboard
Show to: Engineering Team

| KPI | Visualization | Timeframe |
|-----|--------------|-----------|
| API response times (p50, p95, p99) | Line chart | Hourly |
| Error rates by endpoint | Bar chart | Hourly |
| Deployment frequency | Counter | Weekly |
| Build success rate | Gauge | Daily |
```

---

## Privacy Checklist

- [ ] **No PII in event names** (❌ "john@email.com_signed_up")
- [ ] **No PII in properties** (❌ email in button_clicked properties)
- [ ] **Consent mechanism** before tracking (GDPR/CCPA)
- [ ] **Data retention policy** defined (90 days, 1 year, etc.)
- [ ] **Anonymization** for analytics (hash IDs, strip PII)
- [ ] **Opt-out mechanism** for users
- [ ] **Documentation** of what we track and why

---

## Validation Checklist

Before shipping:

- [ ] Events firing correctly (check in analytics debugger)
- [ ] Properties captured with correct types
- [ ] User identification working (identify + track linked)
- [ ] No duplicate events
- [ ] No missing events on critical paths
- [ ] Dashboard showing data correctly
- [ ] Funnel steps in correct order
- [ ] Retention cohorts calculating properly
- [ ] Privacy requirements met

---

**Next Step**: Create dashboards → Monitor for 1 week → Iterate based on gaps
