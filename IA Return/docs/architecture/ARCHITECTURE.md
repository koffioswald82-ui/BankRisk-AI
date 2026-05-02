# Platform Architecture

## Overview

The AI GenPerf & FinOps Intelligence Framework follows a **Clean Architecture** pattern with clear separation between data, business logic, and presentation layers.

---

## Layer Diagram

```
┌─────────────────────────────────────────────────────────────────────┐
│                        PRESENTATION LAYER                            │
│                                                                       │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐               │
│  │  Executive   │  │   Analytics  │  │   FinOps     │               │
│  │  Overview    │  │   Engine     │  │ Intelligence │               │
│  └──────────────┘  └──────────────┘  └──────────────┘               │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐               │
│  │    Team      │  │  AI Forecast │  │  Governance  │               │
│  │ Intelligence │  │              │  │  & Insights  │               │
│  └──────────────┘  └──────────────┘  └──────────────┘               │
│                  Next.js 14 + TypeScript + Tailwind                  │
└────────────────────────────────┬────────────────────────────────────┘
                                  │ REST/JSON
┌────────────────────────────────▼────────────────────────────────────┐
│                         API GATEWAY LAYER                             │
│                     FastAPI + Pydantic v2                             │
│                                                                       │
│   /api/v1/analytics/*    /api/v1/finops/*    /api/v1/insights/*      │
│   /api/v1/teams/*                                                     │
└────────────────────────────────┬────────────────────────────────────┘
                                  │
┌────────────────────────────────▼────────────────────────────────────┐
│                        SERVICE LAYER                                  │
│                                                                       │
│  ┌─────────────────┐  ┌──────────────────┐  ┌──────────────────┐    │
│  │ Analytics Engine │  │  FinOps Engine   │  │Insights Generator│    │
│  │                 │  │                  │  │                  │    │
│  │ · KPI aggregation│  │ · ROI modeling  │  │ · Rule engine    │    │
│  │ · Time-series   │  │ · Monte Carlo   │  │ · Anomaly detect │    │
│  │ · Heatmaps      │  │ · Forecasting   │  │ · Exec briefing  │    │
│  │ · Radar data    │  │ · Scenarios     │  │                  │    │
│  └─────────────────┘  └──────────────────┘  └──────────────────┘    │
│                                                                       │
│  ┌─────────────────────────────────────────────────────────────────┐ │
│  │               AOVI™ Calculator (Scikit-learn)                    │ │
│  │  AOVI = (Productivity^0.35 × Quality^0.30 × Velocity^0.25)      │ │
│  │                   / AI_Cost^0.10                                  │ │
│  │  MinMaxScaler normalization · Team ranking · Performance tiers   │ │
│  └─────────────────────────────────────────────────────────────────┘ │
└────────────────────────────────┬────────────────────────────────────┘
                                  │
┌────────────────────────────────▼────────────────────────────────────┐
│                         DATA LAYER                                    │
│                                                                       │
│  ┌──────────────────────────┐   ┌──────────────────────────────┐    │
│  │   Synthetic Data Engine  │   │       In-Memory Store         │    │
│  │   (Faker + NumPy)        │   │   (startup pre-load)          │    │
│  │                          │   │                               │    │
│  │ · Realistic enterprise   │   │ · Zero-latency API responses  │    │
│  │   engineering datasets   │   │ · Thread-safe singleton       │    │
│  │ · 12 teams × 12 months   │   │ · Replaces PostgreSQL in      │    │
│  │ · 4 AI adoption tiers    │   │   demo/simulation mode        │    │
│  └──────────────────────────┘   └──────────────────────────────┘    │
│                                                                       │
│  ┌─────────────────────────────────────────────────────────────────┐ │
│  │                       PostgreSQL 16                              │ │
│  │  teams · engineers · sprint_metrics · deployment_metrics         │ │
│  │  quality_metrics · ai_usage_records · ai_token_costs             │ │
│  └─────────────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────────┘
```

---

## AOWI™ Scoring Formula

The proprietary AI Operational Value Index uses a weighted geometric mean:

```
AOWI = (Productivity^0.35 × Quality^0.30 × Velocity^0.25) / AI_Cost^0.10
```

**Productivity Index** (weight 0.35):
- Story points delivered
- Commit count
- PRs merged
- AI-assisted tasks

**Quality Index** (weight 0.30):
- Code quality score
- Test coverage %
- Documentation coverage %
- Inverse: bug rate, change failure rate, critical bugs

**Velocity Index** (weight 0.25):
- Sprint velocity
- Deployment frequency
- Inverse: avg dev time, lead time, MTTR

**Cost Efficiency** (weight 0.10):
- AI spend (inverse — higher cost reduces score unless matched by output)

All components are normalized 0.01–1.0 via MinMaxScaler.
Final AOWI scaled 1–100 for executive reporting.

---

## FinOps Engine

### Savings Model
```
Monthly savings = (AI adoption rate / 100) × $520 per engineer
Annual savings  = monthly savings × engineer count × 12
```

The $520/engineer benchmark is derived from:
- Industry average: 15–25% productivity improvement (McKinsey, GitHub research)
- Average loaded engineer cost: $125/hr × 160 hrs/month = $20,000/month
- AI capture rate at full adoption: ~2.6% of monthly cost recovered as hard savings

### ROI Scenarios
| Scenario    | Savings Multiplier | Cost Multiplier | Probability |
|-------------|-------------------|-----------------|-------------|
| Pessimistic | 0.65×             | 1.20×           | 20%         |
| Realistic   | 1.00×             | 1.00×           | 55%         |
| Optimistic  | 1.35×             | 0.90×           | 25%         |

### Monte Carlo
- 5,000 simulations
- Savings sampled: Normal(base, 18% σ)
- Cost sampled: Normal(base, 12% σ)
- Reports: P10/P50/P90 ROI, P(positive ROI)

---

## Data Flow

```
Startup → initialize_store() → build_full_dataset(months=12)
        → 12 teams × 12 months synthetic data
        → held in memory

API Request
→ FastAPI endpoint
→ data_store.get_*() [in-memory]
→ analytics_engine.aggregate_team_kpis()
→ aowi_calculator.calculate_aowi()
→ serialize Pydantic schema
→ JSON response
```

---

## Frontend Data Flow

```
Page load
→ React Query useQuery()
→ axios GET /api/v1/*
→ typed response (TypeScript interfaces)
→ Recharts visualization
→ Framer Motion animation
```

Stale time: 5 minutes (data is static in demo mode)
Cache time: 10 minutes

---

## Security Considerations

For production deployment:
- Replace in-memory store with PostgreSQL + connection pooling
- Add JWT authentication (SECRET_KEY in .env)
- Enable HTTPS with TLS termination at load balancer
- Restrict CORS origins to your domain
- Add rate limiting on API endpoints
- Use secrets manager for DATABASE_URL, SECRET_KEY
