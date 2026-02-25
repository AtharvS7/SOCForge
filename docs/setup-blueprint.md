# SOCForge — Complete Setup & Configuration Blueprint

---

## Phase 1: Frontend Page Mapping

### Page Inventory

| Page | Route | Component | Access | Backend API Group |
|------|-------|-----------|--------|-------------------|
| Login / Register | `/login` | `Login.jsx` | 🌐 Public | `POST /api/auth/register`, `POST /api/auth/login` |
| Dashboard | `/` (index) | `Dashboard.jsx` | 🔒 Any authenticated | `GET /api/dashboard/*` (6 endpoints) |
| Attack Simulation | `/simulation` | `SimulationPanel.jsx` | 🔒 Admin, Analyst | `GET /api/simulation/scenarios`, `POST /api/simulation/start` |
| Alert Monitor | `/alerts` | `AlertMonitor.jsx` | 🔒 Any authenticated (read), Admin/Analyst (update) | `GET/PATCH /api/alerts/*` |
| Investigation | `/investigation` | `Investigation.jsx` | 🔒 Any authenticated | `GET/PATCH /api/incidents/*` |
| Investigation Detail | `/investigation/:id` | `Investigation.jsx` | 🔒 Any authenticated | `GET /api/incidents/:id/timeline` |
| Detection Rules | `/rules` | `RuleEditor.jsx` | 🔒 Any (read), Analyst (create/edit), Admin (delete) | `GET/POST/PATCH/DELETE /api/detection/rules/*` |
| Reports | `/reports` | `Reports.jsx` | 🔒 Any (read/download), Admin/Analyst (generate) | `GET/POST /api/reports/*`, `GET /api/reports/:id/pdf` |

### Unprotected Endpoints (No JWT Required)

| Endpoint | Purpose |
|----------|---------|
| `GET /api/health` | Service health check with DB/Redis status |
| `GET /api/metrics` | Observability metrics (events, alerts, users) |
| `GET /api/docs` | Swagger UI documentation |
| `GET /api/redoc` | ReDoc documentation |

### RBAC Enforcement Summary

| Operation | Viewer | Analyst | Admin |
|-----------|--------|---------|-------|
| Read dashboards, alerts, events, incidents, rules, reports | ✅ | ✅ | ✅ |
| Ingest events | ❌ | ✅ | ✅ |
| Start simulations | ❌ | ✅ | ✅ |
| Update alerts (resolve, FP) | ❌ | ✅ | ✅ |
| Create/edit detection rules | ❌ | ✅ | ✅ |
| Delete detection rules | ❌ | ❌ | ✅ |
| Generate reports | ❌ | ✅ | ✅ |
| Download report PDFs | ✅ | ✅ | ✅ |

---

## Phase 2: API Key & Integration Dependency Matrix

### Required Integrations

| Integration | Type | Credential | Env Variable | Required? |
|-------------|------|-----------|--------------|-----------|
| **PostgreSQL** | Database | Connection string | `DATABASE_URL` | ✅ Required |
| **Redis** | Cache / Rate limit | Connection string w/ password | `REDIS_URL` | ✅ Required |
| **JWT Signing** | Internal auth | Secret key (self-generated) | `JWT_SECRET` | ✅ Required |

### No External API Keys Required

SOCForge is **self-contained** by design. All operations (simulation, detection, correlation, reporting) run locally. There are **zero external API key dependencies** for core functionality.

### Future External Integrations (Not Yet Implemented)

| Integration | Would Require | Env Variable Pattern |
|-------------|--------------|---------------------|
| Splunk SIEM | API token + base URL | `SPLUNK_TOKEN`, `SPLUNK_URL` |
| Elastic SIEM | API key + cluster URL | `ELASTIC_API_KEY`, `ELASTIC_URL` |
| Email alerts (SMTP) | SMTP credentials | `SMTP_HOST`, `SMTP_USER`, `SMTP_PASSWORD` |
| Slack notifications | Webhook URL | `SLACK_WEBHOOK_URL` |
| VirusTotal IOC enrichment | API key | `VIRUSTOTAL_API_KEY` |
| AbuseIPDB lookup | API key | `ABUSEIPDB_API_KEY` |

### Security Boundaries

| Principle | Implementation |
|-----------|---------------|
| Secrets stored in `.env` only | ✅ Never hardcoded |
| `.env` in `.gitignore` | ✅ Excluded from version control |
| Backend-only secrets | ✅ No secrets in frontend bundle |
| Environment-based CORS | ✅ Restricted origins in production |
| Docker secrets injection | ✅ Via `environment:` in `docker-compose.yml` |

---

## Phase 3: Software Installation (Windows)

### Required Software

| Software | Version | Purpose |
|----------|---------|---------|
| Python | 3.11+ | Backend runtime |
| Node.js | 20 LTS | Frontend build/dev |
| PostgreSQL | 15+ | Primary database |
| Redis | 7+ | Caching, rate limiting |
| Git | Latest | Version control |
| Docker Desktop | Latest | Container orchestration (optional) |

### Step-by-Step Installation

#### 1. Python 3.11+
```powershell
# Download from https://www.python.org/downloads/
# During install: CHECK "Add Python to PATH"

# Verify
python --version    # Expected: Python 3.11.x or higher
pip --version       # Expected: pip 23.x+
```

#### 2. Node.js 20 LTS
```powershell
# Download from https://nodejs.org/ (LTS version)
# Run installer with default options

# Verify
node --version    # Expected: v20.x.x
npm --version     # Expected: 10.x.x
```

#### 3. PostgreSQL 15
```powershell
# Download from https://www.postgresql.org/download/windows/
# Run installer → set superuser password → default port 5432

# After install, create SOCForge database:
psql -U postgres
CREATE USER socforge_admin WITH PASSWORD 'StrongPassword123!';
CREATE DATABASE socforge OWNER socforge_admin;
GRANT ALL PRIVILEGES ON DATABASE socforge TO socforge_admin;
\q

# Verify
psql -U socforge_admin -d socforge -c "SELECT 1;"
```

#### 4. Redis 7 (Windows via WSL or Memurai)
```powershell
# Option A: WSL (recommended)
wsl --install                    # If WSL not installed
wsl -d Ubuntu -e bash -c "sudo apt update && sudo apt install redis-server -y"
wsl -d Ubuntu -e bash -c "redis-server --daemonize yes --requirepass StrongRedisPassword123!"

# Option B: Memurai (native Windows Redis)
# Download from https://www.memurai.com/get-memurai
# Install → set password in config → start service

# Verify
redis-cli -a StrongRedisPassword123! ping   # Expected: PONG
```

#### 5. Docker Desktop (Optional — for containerized deployment)
```powershell
# Download from https://www.docker.com/products/docker-desktop/
# Enable WSL 2 backend during install

# Verify
docker --version          # Expected: Docker 24.x+
docker compose version    # Expected: v2.x+
```

### Common Installation Issues

| Issue | Fix |
|-------|-----|
| `python` not found | Add `C:\Python311` to PATH, or use `py` instead |
| `pip install` fails with SSL | Run: `pip install --trusted-host pypi.org --trusted-host files.pythonhosted.org <package>` |
| PostgreSQL service not starting | Check port 5432 isn't in use: `netstat -an \| findstr 5432` |
| Redis connection refused on Windows | Use WSL or Memurai; native Redis doesn't support Windows |
| npm EPERM errors | Run terminal as Administrator, or delete `node_modules` and retry |

---

## Phase 4: Project Setup & Running

### Local Development (Without Docker)

#### Backend Setup
```powershell
# 1. Navigate to backend
cd d:\SOCForge\backend

# 2. Create virtual environment
python -m venv venv
.\venv\Scripts\Activate.ps1

# 3. Install dependencies
pip install -r requirements.txt

# 4. Verify .env exists in project root
cat d:\SOCForge\.env
# Should contain DATABASE_URL, REDIS_URL, JWT_SECRET, etc.

# 5. Start backend
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# 6. Verify
# Visit: http://localhost:8000/api/docs  (Swagger UI)
# Visit: http://localhost:8000/api/health (Health check)
```

#### Frontend Setup
```powershell
# Open new terminal

# 1. Navigate to frontend
cd d:\SOCForge\frontend

# 2. Install dependencies
npm install

# 3. Start dev server
npm run dev

# 4. Verify
# Visit: http://localhost:5173
# You should see the SOCForge login page
```

### Docker Deployment (All-in-One)
```powershell
cd d:\SOCForge

# Build and start all services
docker compose up --build -d

# Check status
docker compose ps

# View logs
docker compose logs -f backend
docker compose logs -f frontend

# Stop
docker compose down
```

---

## Phase 5: Secure Configuration

### Environment Variables Reference

File: `d:\SOCForge\.env`

```env
# ── Database ──
POSTGRES_DB=socforge
POSTGRES_USER=socforge_admin
POSTGRES_PASSWORD=StrongPassword123!    # CHANGE IN PRODUCTION

# ── Redis ──
REDIS_PASSWORD=StrongRedisPassword123!             # CHANGE IN PRODUCTION

# ── Authentication ──
JWT_SECRET=SOCForge_JWT_Super_Secret_Key_2024!  # MUST CHANGE IN PRODUCTION
JWT_ALGORITHM=HS256
JWT_EXPIRATION_MINUTES=480                 # 8 hours

# ── Application ──
ENVIRONMENT=development                   # development | production
LOG_LEVEL=INFO                            # DEBUG | INFO | WARNING | ERROR
```

### How Each Variable Is Consumed

| Variable | Consumed By | File |
|----------|-------------|------|
| `POSTGRES_*` | Docker Compose → PostgreSQL container | `docker-compose.yml` line 8-10 |
| `DATABASE_URL` | Backend → SQLAlchemy engine | `backend/app/config.py` → `Settings.DATABASE_URL` |
| `REDIS_URL` | Backend → health check, rate cache | `backend/app/config.py` → `Settings.REDIS_URL` |
| `REDIS_PASSWORD` | Docker Compose → Redis container | `docker-compose.yml` line 28 |
| `JWT_SECRET` | Backend → token sign/verify | `backend/app/utils/security.py` → `create_access_token` |
| `JWT_ALGORITHM` | Backend → JWT encode/decode | `backend/app/utils/security.py` |
| `JWT_EXPIRATION_MINUTES` | Backend → token expiry | `backend/app/utils/security.py` |
| `ENVIRONMENT` | Backend → CORS mode, log format | `backend/app/main.py`, `logging_config.py` |
| `LOG_LEVEL` | Backend → structured logging | `backend/app/logging_config.py` |
| `VITE_API_TARGET` | Frontend (Docker) → Vite proxy | `frontend/vite.config.js` |

### Config Loading Chain

```
.env file
  ↓ loaded by pydantic-settings (BaseSettings)
  ↓
backend/app/config.py → Settings class
  ↓
Settings fields available as: settings.DATABASE_URL, settings.JWT_SECRET, etc.
  ↓
Consumed by: database.py, security.py, main.py, logging_config.py
```

### Production Hardening Checklist

- [ ] Generate a strong random `JWT_SECRET` (min 64 chars): `python -c "import secrets; print(secrets.token_urlsafe(64))"`
- [ ] Change `POSTGRES_PASSWORD` to a strong unique value
- [ ] Change `REDIS_PASSWORD` to a strong unique value
- [ ] Set `ENVIRONMENT=production` → restricts CORS, enables JSON logging
- [ ] Remove port exposures in Docker (5432, 6379) or bind to 127.0.0.1
- [ ] Place behind HTTPS reverse proxy (nginx/Caddy)
- [ ] Never commit `.env` to version control (already in `.gitignore`)

---

## Phase 6: Validation Checklist

### Configuration Validation
```powershell
# 1. Backend health check
curl http://localhost:8000/api/health
# Expected: {"status":"operational","database":"connected","redis":"connected",...}

# 2. API docs accessible
# Visit: http://localhost:8000/api/docs

# 3. Frontend loads
# Visit: http://localhost:5173

# 4. Register a user
# POST http://localhost:8000/api/auth/register
# Body: {"email":"test@soc.com","username":"analyst1","password":"Secure123!","role":"analyst"}

# 5. Login and get token
# POST http://localhost:8000/api/auth/login
# Body: {"username":"analyst1","password":"Secure123!"}

# 6. Run a simulation (with token)
# POST http://localhost:8000/api/simulation/start
# Header: Authorization: Bearer <token>
# Body: {"scenario":"full_attack_chain","intensity":"medium","duration_seconds":30}
```

### Security Exposure Audit

| Check | Status |
|-------|--------|
| No secrets in frontend bundle | ✅ All secrets backend-only |
| `.env` excluded from git | ✅ In `.gitignore` |
| CORS restricted in production | ✅ `ENVIRONMENT=production` locks origins |
| JWT tokens expire | ✅ 8-hour default expiry |
| Passwords hashed (bcrypt) | ✅ Never stored in plaintext |
| Rate limiting active | ✅ 100 req/min/IP |
| Input sanitization | ✅ On event ingestion |
| RBAC enforced server-side | ✅ All write endpoints protected |
| SQL injection prevented | ✅ SQLAlchemy ORM parameterized queries |
| Audit logging | ✅ All API requests logged with timing |
