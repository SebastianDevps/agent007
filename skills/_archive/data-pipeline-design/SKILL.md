---
name: data-pipeline-design
description: "Diseñar data pipelines: ETL/ELT, data modeling, warehouse. Para infraestructura de datos."
invokable: true
accepts_args: true
auto-activate: false
version: 1.0.0
when:
  - user_mentions: ["data pipeline", "etl", "data warehouse", "data model", "reporting"]
---

# Data Pipeline Design - From Raw Data to Insights

**Propósito**: Diseñar pipelines de datos robustos que transformen datos raw en insights accionables para el equipo.

---

## Arquitectura de Datos para Startups

### Stage 1: Early Stage (0-1000 users)

```
Application DB (PostgreSQL)
      ↓
  SQL Views / Queries
      ↓
  Metabase / Grafana (dashboards)
```

**Cuándo usar**: Pocos datos, equipo pequeño, necesidades básicas de reporting.

**Ventajas**: Simple, sin infraestructura adicional, queries directos.
**Limitaciones**: Queries pesados afectan performance de producción.

---

### Stage 2: Growth Stage (1000-50000 users)

```
Application DB ──→ Read Replica ──→ dbt models ──→ Metabase
                                                     ↕
Event Tracking ──→ Analytics Tool (PostHog/Mixpanel)
```

**Cuándo usar**: Queries de analytics afectan producción, necesitas transformaciones.

**Componentes**:
- **Read Replica**: Aísla queries analíticos de producción
- **dbt**: Transforma datos en modelos analíticos
- **Analytics Tool**: Product analytics separado

---

### Stage 3: Scale Stage (50000+ users)

```
Application DB ──→ CDC ──→ Data Warehouse ──→ dbt ──→ BI Tool
                           (BigQuery/Snowflake)
Event Tracking ──→ Segment/Rudderstack ──→ ↑
External APIs ──→ Fivetran/Airbyte ──→ ↑
```

**Cuándo usar**: Múltiples fuentes de datos, equipo de datos dedicado.

---

## Data Modeling

### Dimensional Modeling (Star Schema)

```sql
-- Fact Table: Events/Transactions (what happened)
CREATE TABLE fact_user_actions (
  id BIGSERIAL PRIMARY KEY,
  action_timestamp TIMESTAMPTZ NOT NULL,
  user_id UUID NOT NULL,
  action_type VARCHAR(50) NOT NULL,
  -- Dimension keys
  date_key INTEGER REFERENCES dim_date(date_key),
  user_key INTEGER REFERENCES dim_users(user_key),
  -- Measures
  duration_seconds INTEGER,
  items_count INTEGER,
  revenue_cents BIGINT
);

-- Dimension Table: Users (who)
CREATE TABLE dim_users (
  user_key SERIAL PRIMARY KEY,
  user_id UUID UNIQUE NOT NULL,
  email VARCHAR(255),
  name VARCHAR(255),
  plan VARCHAR(50),
  signed_up_at TIMESTAMPTZ,
  -- SCD Type 2 for tracking changes
  valid_from TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  valid_to TIMESTAMPTZ DEFAULT '9999-12-31',
  is_current BOOLEAN DEFAULT TRUE
);

-- Dimension Table: Date (when)
CREATE TABLE dim_date (
  date_key INTEGER PRIMARY KEY, -- YYYYMMDD
  full_date DATE NOT NULL,
  day_of_week INTEGER,
  day_name VARCHAR(10),
  week_of_year INTEGER,
  month INTEGER,
  month_name VARCHAR(10),
  quarter INTEGER,
  year INTEGER,
  is_weekend BOOLEAN,
  is_holiday BOOLEAN
);
```

### dbt Model Example

```sql
-- models/marts/core/fct_daily_active_users.sql
{{ config(materialized='table', schema='marts') }}

WITH user_actions AS (
  SELECT
    DATE_TRUNC('day', action_timestamp) AS activity_date,
    user_id,
    COUNT(*) AS action_count,
    COUNT(DISTINCT action_type) AS unique_actions
  FROM {{ ref('stg_user_actions') }}
  WHERE action_timestamp >= CURRENT_DATE - INTERVAL '90 days'
  GROUP BY 1, 2
),

user_details AS (
  SELECT * FROM {{ ref('dim_users') }}
  WHERE is_current = TRUE
)

SELECT
  ua.activity_date,
  ua.user_id,
  ud.plan,
  ud.signed_up_at,
  ua.action_count,
  ua.unique_actions,
  DATEDIFF('day', ud.signed_up_at, ua.activity_date) AS days_since_signup
FROM user_actions ua
JOIN user_details ud ON ua.user_id = ud.user_id
```

---

## Data Quality Framework

### Quality Checks

```yaml
# dbt tests or custom checks

tests:
  # Freshness: Data is up to date
  - name: freshness_check
    query: |
      SELECT MAX(updated_at) as last_update
      FROM source_table
    assert: last_update > NOW() - INTERVAL '2 hours'

  # Completeness: No missing critical fields
  - name: not_null_user_id
    query: |
      SELECT COUNT(*) FROM events WHERE user_id IS NULL
    assert: count = 0

  # Uniqueness: No duplicate records
  - name: unique_event_ids
    query: |
      SELECT event_id, COUNT(*)
      FROM events
      GROUP BY event_id
      HAVING COUNT(*) > 1
    assert: rows = 0

  # Accuracy: Values in expected range
  - name: valid_revenue
    query: |
      SELECT COUNT(*) FROM payments WHERE amount_cents < 0
    assert: count = 0

  # Consistency: Cross-source agreement
  - name: user_count_match
    query: |
      SELECT
        (SELECT COUNT(*) FROM app_users) as app_count,
        (SELECT COUNT(*) FROM analytics_users) as analytics_count
    assert: ABS(app_count - analytics_count) < 100
```

### Monitoring & Alerting

```
Pipeline Health:
  □ Run success rate > 99%
  □ Data freshness < SLA
  □ Row count changes within expected range
  □ Schema changes detected

Data Quality:
  □ Null rate for critical fields < 0.1%
  □ Duplicate rate < 0.01%
  □ Value distribution within expected range
  □ Cross-source consistency

Alerts:
  □ Pipeline failure → Slack + PagerDuty
  □ Data freshness SLA breach → Slack
  □ Quality check failure → Slack + email
  □ Schema change detected → Slack
```

---

## Implementation Checklist

### Phase 1: Basic Analytics (Week 1)
- [ ] Choose analytics tool (PostHog recommended for startups)
- [ ] Define top 10 events to track
- [ ] Implement server-side tracking for critical events
- [ ] Implement client-side tracking for UI events
- [ ] Create basic executive dashboard
- [ ] Validate events are firing correctly

### Phase 2: Data Models (Week 2-3)
- [ ] Set up read replica (if PostgreSQL)
- [ ] Create SQL views for common queries
- [ ] Define key metrics with exact SQL formulas
- [ ] Build retention cohort query
- [ ] Build funnel analysis query
- [ ] Create product dashboard

### Phase 3: Automated Pipeline (Month 2+)
- [ ] Set up dbt project
- [ ] Create staging models
- [ ] Create mart models (dimensions + facts)
- [ ] Add data quality tests
- [ ] Schedule daily runs
- [ ] Set up monitoring and alerting

---

**Next Step**: Start with Phase 1 (basic analytics) → Iterate based on business needs
