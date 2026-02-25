# SOCForge: Enterprise SOC Threat Detection & Attack Simulation Platform

## Technical Report

---

### Executive Summary

SOCForge is a full-stack Security Operations Center (SOC) platform designed for automated threat detection, attack simulation, and incident response. It provides security analysts with an integrated environment to simulate adversary behavior using MITRE ATT&CK-mapped attack scenarios, detect threats through configurable rule engines, correlate individual alerts into multi-stage incidents, and produce structured investigation reports. The system is built on a modern asynchronous architecture using FastAPI, PostgreSQL, Redis, and React, with a focus on modularity, extensibility, and enterprise-grade security.

---

### 1. Problem Statement

Modern organizations face an increasing volume and sophistication of cyber threats. Security Operations Centers (SOCs) are tasked with monitoring, detecting, and responding to these threats in real-time. However, several challenges persist:

1. **Detection Gap**: Many SOC teams lack the ability to test their detection capabilities against realistic attack scenarios before real incidents occur.
2. **Alert Fatigue**: High volumes of uncorrelated alerts overwhelm analysts, leading to missed critical threats.
3. **Integration Complexity**: SOC tools are often fragmented across multiple vendors, making unified analysis difficult.
4. **Training Deficit**: Junior analysts rarely encounter real attack chains during training, leaving them unprepared for sophisticated threats.

SOCForge addresses these challenges by providing a self-contained platform that simulates realistic attack traffic, applies detection logic in real-time, correlates alerts into actionable incidents, and presents the results through an intuitive dashboard.

---

### 2. Purpose of the Platform

SOCForge serves three primary purposes:

- **Detection Engineering**: Enables security teams to develop, test, and refine detection rules against known attack patterns without requiring live threat traffic.
- **Analyst Training**: Provides realistic attack simulations with MITRE ATT&CK mapping, allowing analysts to practice investigation workflows in a controlled environment.
- **Architecture Demonstration**: Serves as a reference implementation of a modern SOC platform, demonstrating the integration of event ingestion, rule-based detection, alert correlation, and incident management.

---

### 3. System Architecture Overview

SOCForge follows a layered, service-oriented architecture:

```
┌──────────────────────────────────────────────────────┐
│                    Frontend (React/Vite)              │
│  Dashboard │ Alerts │ Simulation │ Investigation │ ...│
└──────────────────────┬───────────────────────────────┘
                       │ REST API + WebSocket
┌──────────────────────┴───────────────────────────────┐
│                 FastAPI Application Layer             │
│  ┌─────────┐ ┌─────────┐ ┌──────────┐ ┌───────────┐ │
│  │  Auth   │ │ Events  │ │Detection │ │Simulation │ │
│  │ Router  │ │ Router  │ │ Router   │ │  Router   │ │
│  └─────────┘ └─────────┘ └──────────┘ └───────────┘ │
│  ┌─────────┐ ┌─────────┐ ┌──────────┐ ┌───────────┐ │
│  │ Alerts  │ │Incidents│ │ Reports  │ │   Users   │ │
│  │ Router  │ │ Router  │ │ Router   │ │  Router   │ │
│  └─────────┘ └─────────┘ └──────────┘ └───────────┘ │
│                                                      │
│  ┌───────────────── Services Layer ────────────────┐ │
│  │ SimulationEngine │ DetectionEngine │ Correlation │ │
│  │ MITREMapper │ Timeline │ SIEM │ Notify │ IOC    │ │
│  └─────────────────────────────────────────────────┘ │
│                                                      │
│  ┌─────── Middleware ──────┐ ┌──── Security ───────┐ │
│  │ RateLimit │ AuditLog   │ │ JWT │ bcrypt │ RBAC  │ │
│  └────────────────────────┘ └─────────────────────┘ │
└──────────────────────┬───────────────────────────────┘
                       │
        ┌──────────────┴──────────────┐
        │  PostgreSQL    │    Redis    │
        │  (async/pgp)   │  (cache/RL) │
        └─────────────────────────────┘
```

**Key architectural decisions:**

- **Asynchronous I/O**: All database and network operations use Python's `async/await` with SQLAlchemy 2.0's async driver (`asyncpg`), enabling high-throughput event processing without thread blocking.
- **Modular services**: Each business capability (detection, correlation, simulation) is encapsulated in a dedicated service module with no cross-dependencies.
- **Fail-safe integrations**: External services (SIEM, notifications, IOC enrichment) are designed as optional modules that gracefully degrade when not configured.

---

### 4. Detailed Workflow

#### 4.1 Authentication

The authentication subsystem implements a stateless JWT-based flow with role-based access control (RBAC).

**Flow**: User registers with email, username, and password → password is hashed using `bcrypt` with a cost factor of 12 → JWT token is issued containing the user ID and role → subsequent requests include the token in the `Authorization` header → the `get_current_user` dependency validates the token and retrieves the user from the database → protected endpoints use `require_role()` to enforce access control.

**Roles**: `admin` (full access), `analyst` (read/write on operational data), `viewer` (read-only).

#### 4.2 Simulation Engine

The simulation engine generates synthetic security telemetry that mimics real-world attack patterns.

**Available scenarios:**

| Scenario | MITRE Phases | Events |
|----------|-------------|--------|
| Full Attack Chain | Recon → Initial Access → Execution → C2 → Lateral → Exfiltration | 80–200 |
| SSH Brute Force | Credential Access | 15–60 |
| Port Scan | Reconnaissance | 30–120 |
| Web Application Attack | Initial Access | 12–50 |
| Lateral Movement | Lateral Movement, Discovery | 5–20 |

Each scenario generates events with realistic IP addresses, ports, protocols, timestamps, and MITRE ATT&CK annotations. Benign background traffic is optionally mixed in to simulate noise.

#### 4.3 Detection Engine

The detection engine applies configurable rules to incoming events to generate alerts.

**Rule types:**

- **Threshold rules**: Trigger when the count of matching events exceeds a threshold within a time window (e.g., >5 failed SSH logins in 60 seconds).
- **Pattern rules**: Trigger on a single event matching specific criteria (e.g., reverse shell execution detected).

Each rule specifies: event type filter, threshold count, time window, grouping field, MITRE mapping, and severity. When a rule fires, an Alert object is created with links to the triggering events, IOC indicators, and MITRE context.

#### 4.4 Correlation Engine

The correlation engine groups related alerts into multi-stage incidents.

**Algorithm**: Alerts are grouped by source IP address. For each group with ≥2 alerts, the engine checks for an existing open incident involving the same IP. If found, the incident is updated with new alert counts and MITRE technique coverage. If not, a new incident is created with kill chain phase determination, severity escalation, and IOC aggregation.

**Kill chain mapping**: The engine maps observed MITRE tactics to kill chain phases and reports the furthest phase reached, providing analysts with immediate context about attack progression.

#### 4.5 Incident Management

Incidents aggregate correlated alerts into investigable cases. Each incident tracks: affected hosts and users, MITRE tactics and techniques observed, IOC summary, chronological timeline, severity, status, and priority. The timeline service reconstructs event-level chronology from all linked alerts and events.

#### 4.6 External Integrations

SOCForge supports three categories of optional external integrations:

- **SIEM Export** (Splunk HEC, Elasticsearch): Automatically forwards alerts and incidents to external SIEM platforms for centralized visibility.
- **Notifications** (SMTP Email, Slack Webhook): Sends real-time notifications for critical and high-severity alerts.
- **IOC Enrichment** (VirusTotal, AbuseIPDB): Enriches IP addresses with threat reputation scores, abuse reports, and geolocation data.

All integrations use environment variables for configuration and are designed to fail silently when not configured.

---

### 5. Technology Stack

| Layer | Technology | Rationale |
|-------|-----------|-----------|
| Backend Framework | FastAPI 0.109 | High-performance async Python framework with automatic OpenAPI documentation |
| ORM | SQLAlchemy 2.0 + asyncpg | Type-safe async database access with PostgreSQL-native features (JSONB, UUID) |
| Database | PostgreSQL 15 | ACID compliance, JSONB support for flexible metadata, UUID primary keys |
| Cache/Rate Limiting | Redis 7 | Sub-millisecond key-value operations, sorted sets for sliding window rate limiting |
| Authentication | python-jose + bcrypt 5.0 | JWT token generation with direct bcrypt hashing (cost factor 12) |
| Frontend | React 18 + Vite 5 | Component-based UI with fast HMR development, Tailwind CSS for styling |
| Visualization | Recharts | React-native charting for dashboard analytics |
| Containerization | Docker Compose | Multi-service orchestration for development and staging |
| Orchestration | Kubernetes | Production deployment with auto-scaling, health probes, and secret management |
| CI/CD | GitHub Actions | Automated linting, testing, and container image builds |

---

### 6. Security Considerations

SOCForge implements defense-in-depth across multiple layers:

- **Authentication**: bcrypt password hashing with cost factor 12; JWT tokens with configurable expiry; stateless authentication with no server-side session storage.
- **Authorization**: Role-based access control enforced at the route level via FastAPI dependencies; self-protection guards prevent admin self-demotion or self-deactivation.
- **Input validation**: Pydantic schema enforcement on all API inputs; hostname and IP address sanitization on event ingestion.
- **Rate limiting**: Redis-backed sliding window (100 requests/minute/IP) with in-memory fallback; `Retry-After` header on 429 responses.
- **Audit logging**: All API requests are logged with method, path, client IP, and response status.
- **CORS**: Environment-conditional origin policy (permissive in development, locked in production).
- **Secrets management**: All sensitive values loaded from environment variables; no hardcoded credentials in source code; Kubernetes Secrets for production deployment.

---

### 7. Scalability Considerations

The architecture supports horizontal scaling through several design choices:

- **Stateless backend**: JWT-based authentication and Redis-backed rate limiting allow multiple backend replicas behind a load balancer without session affinity.
- **Async I/O**: The async event loop handles concurrent requests without thread pool exhaustion, enabling high throughput on modest hardware.
- **Database connection pooling**: SQLAlchemy's async connection pool with PostgreSQL minimizes connection overhead.
- **Kubernetes deployment**: The provided K8s manifests include 2-replica deployments with resource limits, health probes, and ingress-based routing.

---

### 8. Deployment Model

SOCForge supports three deployment models:

1. **Local development**: Direct execution via `uvicorn --reload` with PostgreSQL and Redis running locally or via WSL.
2. **Docker Compose**: Multi-container orchestration with PostgreSQL, Redis, backend, and frontend services.
3. **Kubernetes**: Production-ready deployment with Deployment, Service, Ingress, and Secret resources; TLS termination via cert-manager; health and readiness probes.

---

### 9. Limitations

1. **Simulated data only**: The current implementation generates synthetic telemetry. Integration with live SIEM data sources (syslog, Beats agents) requires additional connector development.
2. **Single-database architecture**: All data resides in a single PostgreSQL instance. For high-volume production environments, partitioning or a time-series database (e.g., TimescaleDB) would be appropriate for event storage.
3. **No real-time ML**: Detection relies on rule-based logic. Machine learning models for anomaly detection and behavioral analysis are not yet implemented.
4. **Limited IOC enrichment**: Enrichment depends on external API availability and rate limits; no local threat intelligence database is maintained.

---

### 10. Future Enhancements

| Enhancement | Priority | Complexity |
|-------------|----------|-----------|
| Live SIEM data ingestion (syslog, Filebeat) | High | Medium |
| ML-based anomaly detection | High | High |
| Automated playbook execution (SOAR) | Medium | High |
| Threat intelligence feed integration (STIX/TAXII) | Medium | Medium |
| Multi-tenancy support | Low | High |
| Mobile companion application | Low | Medium |

---

### 11. Real-World Applicability

SOCForge is directly applicable in the following contexts:

- **Security team training**: Organizations can use the simulation engine to train analysts on realistic attack scenarios without exposing production systems.
- **Detection rule development**: Security engineers can iterate on detection rules against deterministic attack simulations, measuring true/false positive rates.
- **SOC architecture reference**: The platform demonstrates a complete, modern SOC data pipeline and can serve as a foundation for custom SOC tool development.
- **Academic research**: The MITRE ATT&CK integration and configurable detection rules enable controlled experiments in threat detection and correlation algorithm research.

---

### 12. Conclusion

SOCForge demonstrates that a comprehensive SOC platform can be built on modern open-source technologies without sacrificing security, scalability, or operational integrity. The platform's modular architecture allows each component — simulation, detection, correlation, integration — to evolve independently while maintaining a cohesive end-to-end workflow. With its MITRE ATT&CK alignment, role-based access control, and fail-safe external integrations, SOCForge provides a production-grade foundation for security operations, analyst training, and detection engineering.

---

*Report generated: February 2026*
*Platform version: 1.0.0*
*Architecture: FastAPI + SQLAlchemy 2.0 + PostgreSQL + Redis + React*
