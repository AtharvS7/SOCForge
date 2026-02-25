# SOCForge Architecture Documentation

## System Architecture

SOCForge follows a **modular microservices-inspired** architecture deployed as a monorepo with Docker Compose orchestration.

### Technology Stack

| Layer | Technology | Purpose |
|-------|-----------|---------|
| Frontend | React 18 + Vite 5 + Tailwind CSS 3 | SOC Dashboard UI |
| Backend | Python FastAPI | REST API, Business Logic |
| Database | PostgreSQL 15 | Persistent data storage |
| Cache | Redis 7 | Rate limiting, session cache |
| Auth | JWT + bcrypt | Authentication & RBAC |
| Reports | ReportLab | PDF report generation |
| Visualization | Recharts | Interactive charts |

### Data Flow

```
User → Frontend (React)
  → REST API (FastAPI) → JWT Auth Middleware
    → Router → Service Layer → SQLAlchemy ORM → PostgreSQL

Attack Simulation Flow:
  Simulation Engine → Generate Events → Detection Engine → Generate Alerts
    → Correlation Engine → Create Incidents → Timeline Builder
```

### API Contracts

All endpoints require JWT authentication (except `/api/auth/*` and `/api/health`).

**Base URL**: `http://localhost:8000/api`

**Auth Header**: `Authorization: Bearer <JWT_TOKEN>`

**Standard Response Codes**:
- 200: Success
- 201: Created
- 400: Bad Request
- 401: Unauthorized
- 403: Forbidden
- 404: Not Found
- 429: Rate Limited

### Database Schema

**Users** → Roles (admin, analyst, viewer), JWT tokens
**Events** → Normalized security events with MITRE mapping
**Alerts** → Detection-generated alerts linked to rules and events
**DetectionRules** → Configurable detection logic with thresholds
**Incidents** → Correlated alert groups with kill chain tracking
**Reports** → Generated investigation reports with PDF paths

### Security Controls

1. **JWT Authentication** — Token-based auth with configurable expiration
2. **RBAC** — Role-based access for admin/analyst/viewer
3. **Input Validation** — Pydantic schemas enforce type safety
4. **Rate Limiting** — Per-IP sliding window limiter
5. **Audit Logging** — All API requests logged with timing
6. **Secrets Management** — Environment variables, never hardcoded
