# SOCForge

**Enterprise SOC Threat Detection & Attack Simulation Platform**

A production-grade, full-stack security operations platform that simulates real-world cyber attacks, ingests telemetry, applies detection engineering logic, correlates security events, reconstructs incident timelines, and produces structured investigation reports aligned with MITRE ATT&CK.

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────┐
│               Frontend (React + Vite)            │
│   Dashboard │ Simulation │ Alerts │ Investigation │
│   Rule Editor │ Reports                          │
└──────────────────┬──────────────────────────────┘
                   │ REST API + JWT
┌──────────────────┴──────────────────────────────┐
│               Backend (FastAPI)                  │
│  ┌──────────┐ ┌──────────┐ ┌──────────────────┐ │
│  │   Auth   │ │ Ingest   │ │ Detection Engine │ │
│  │  (RBAC)  │ │ Service  │ │  (6 Rules)       │ │
│  └──────────┘ └──────────┘ └──────────────────┘ │
│  ┌──────────┐ ┌──────────┐ ┌──────────────────┐ │
│  │ Correlate│ │ Simulate │ │ Report Service   │ │
│  │ Engine   │ │ Engine   │ │ (PDF Export)     │ │
│  └──────────┘ └──────────┘ └──────────────────┘ │
└──────────────────┬──────────────────────────────┘
          ┌────────┴────────┐
     ┌────┴────┐      ┌────┴────┐
     │PostgreSQL│      │  Redis  │
     └─────────┘      └─────────┘
```

## 🚀 Quick Start

### Prerequisites
- Docker & Docker Compose
- Node.js 18+ (for local frontend dev)
- Python 3.11+ (for local backend dev)

### Docker Deployment
```bash
# Clone and start
cd SOCForge
docker compose up --build
```

### Local Development
```bash
# Backend
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000

# Frontend (separate terminal)
cd frontend
npm install
npm run dev
```

### Access
- **Frontend**: http://localhost:5173
- **Backend API**: http://localhost:8000
- **API Docs**: http://localhost:8000/api/docs

## 🔐 Default Credentials
Register a new account at `/login`. Choose role:
- **Admin**: Full access to all features
- **Analyst**: Can run simulations, manage rules, investigate
- **Viewer**: Read-only dashboard access

## 🎯 Core Features

| Feature | Description |
|---------|-------------|
| **Attack Simulation** | 5 scenarios: Full Kill Chain, SSH Brute Force, Port Scan, Web Attack, Lateral Movement |
| **Detection Engine** | 6 built-in rules with threshold & pattern matching |
| **Event Correlation** | IP-based correlation with kill chain phase tracking |
| **MITRE ATT&CK** | Full mapping with coverage matrix visualization |
| **Timeline Reconstruction** | Chronological attack timeline from correlated events |
| **Report Generation** | PDF export with exec summary, findings, IOCs, recommendations |
| **False Positive Tuning** | Mark FPs, track FP rate per rule |
| **Role-Based Access** | Admin, Analyst, Viewer roles with JWT auth |

## 📊 Detection Rules

| Rule | Event Type | Threshold | MITRE |
|------|-----------|-----------|-------|
| SSH Brute Force | ssh_login_failed | ≥5 in 60s | T1110 |
| Port Scan | port_scan | ≥20 ports in 30s | T1595 |
| Reverse Shell | reverse_shell | ≥1 in 10s | T1059.004 |
| C2 Beaconing | c2_beacon | ≥5 in 300s | T1071 |
| Web Attack | web_exploit | ≥1 in 60s | T1190 |
| Lateral Movement | lateral_movement | ≥3 in 120s | T1021 |

## 🛡️ Security Controls
- JWT-based authentication with configurable expiration
- Role-based access control (RBAC)
- Input validation & sanitization
- API rate limiting
- Audit logging of all requests
- Secure secrets management via environment variables

## 📁 Project Structure
```
SOCForge/
├── docker-compose.yml
├── backend/
│   ├── app/
│   │   ├── main.py           # FastAPI app
│   │   ├── config.py          # Settings
│   │   ├── database.py        # SQLAlchemy
│   │   ├── models/            # DB models
│   │   ├── schemas/           # Pydantic schemas
│   │   ├── routers/           # API endpoints
│   │   ├── services/          # Business logic
│   │   ├── middleware/        # Rate limit, audit
│   │   └── utils/             # Auth, validation
│   └── requirements.txt
├── frontend/
│   └── src/
│       ├── App.jsx
│       ├── api/client.js
│       ├── context/AuthContext.jsx
│       ├── components/layout/
│       └── pages/
│           ├── Dashboard.jsx
│           ├── SimulationPanel.jsx
│           ├── AlertMonitor.jsx
│           ├── Investigation.jsx
│           ├── RuleEditor.jsx
│           └── Reports.jsx
└── docs/
```

## 📖 API Endpoints

| Method | Path | Description |
|--------|------|-------------|
| POST | `/api/auth/register` | User registration |
| POST | `/api/auth/login` | JWT authentication |
| GET | `/api/dashboard/stats` | Dashboard metrics |
| POST | `/api/simulation/start` | Launch attack sim |
| GET | `/api/alerts/` | List alerts |
| GET | `/api/detection/rules` | List detection rules |
| GET | `/api/incidents/` | List incidents |
| GET | `/api/incidents/{id}/timeline` | Attack timeline |
| POST | `/api/reports/generate` | Generate report |
| GET | `/api/reports/{id}/pdf` | Download PDF |

---

*Built with ❤️ for Security Operations*
