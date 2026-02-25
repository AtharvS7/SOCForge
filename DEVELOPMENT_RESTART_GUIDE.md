# SOCForge — Development Restart Guide

> **Use this guide to resume development after a full shutdown.**
> All terminals closed, services stopped, fresh start.

---

## Quick Start (Copy-Paste)

```powershell
# Terminal 1 — Backend
cd d:\SOCForge\backend
.\venv\Scripts\Activate.ps1
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

```powershell
# Terminal 2 — Frontend
cd d:\SOCForge\frontend
npm run dev
```

```powershell
# Terminal 3 — Verify
curl http://localhost:8000/api/health
# Expected: {"status":"operational","database":"connected",...}
```

---

## Detailed Steps

### 1. Prerequisites — Verify Services

#### PostgreSQL
```powershell
# Check if PostgreSQL is running
pg_isready -h localhost -p 5432
# Expected: localhost:5432 - accepting connections

# If not running, start the service:
net start postgresql-x64-15
# Or via Services app: Start "postgresql-x64-15"
```

#### Redis
```powershell
# If using WSL:
wsl -d Ubuntu -e bash -c "redis-server --daemonize yes --requirepass StrongRedisPassword123!"

# If using Memurai (native Windows):
net start MemuraiService

# Verify:
redis-cli -a StrongRedisPassword123! ping
# Expected: PONG
```

### 2. Backend

```powershell
cd d:\SOCForge\backend
.\venv\Scripts\Activate.ps1

# Verify dependencies
pip list | findstr fastapi
# Should show: fastapi 0.109.0

# Start server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

**Expected output:**
```
INFO:     Uvicorn running on http://0.0.0.0:8000
INFO:     SOCForge API starting up...
INFO:     Database tables initialized.
INFO:     Application startup complete.
```

### 3. Frontend

```powershell
# New terminal
cd d:\SOCForge\frontend
npm run dev
```

**Expected output:**
```
VITE v5.x.x ready in XXXms
➜ Local:   http://localhost:5173/
```

### 4. Verify Everything Works

```powershell
# Health check
curl http://localhost:8000/api/health

# Register a user (first time only)
curl -X POST http://localhost:8000/api/auth/register `
  -H "Content-Type: application/json" `
  -d '{"email":"admin@socforge.io","username":"admin","password":"SecurePass123!","role":"admin"}'

# Login
curl -X POST http://localhost:8000/api/auth/login `
  -H "Content-Type: application/json" `
  -d '{"username":"admin","password":"SecurePass123!"}'
# Copy the access_token from response

# Run simulation (replace TOKEN)
curl -X POST http://localhost:8000/api/simulation/start `
  -H "Content-Type: application/json" `
  -H "Authorization: Bearer TOKEN" `
  -d '{"scenario":"full_attack_chain","intensity":"medium","duration_seconds":30}'
```

### 5. Open Browser
- **Frontend**: http://localhost:5173
- **API Docs**: http://localhost:8000/api/docs
- **Health**: http://localhost:8000/api/health

---

## Docker Alternative

```powershell
cd d:\SOCForge
docker compose up --build -d
docker compose ps        # Check all 4 services running
docker compose logs -f    # Watch logs
```

---

## Environment Variables

File: `d:\SOCForge\.env`

| Variable | Purpose | Required |
|----------|---------|----------|
| `DATABASE_URL` | PostgreSQL connection | ✅ |
| `REDIS_URL` | Redis connection | ✅ |
| `JWT_SECRET` | Token signing key | ✅ |
| `POSTGRES_DB/USER/PASSWORD` | Docker Compose PG config | Docker only |
| `REDIS_PASSWORD` | Docker Compose Redis config | Docker only |
| `ENVIRONMENT` | `development` or `production` | ✅ |

---

## Troubleshooting

| Error | Fix |
|-------|-----|
| `ModuleNotFoundError: No module named 'X'` | Run: `.\venv\Scripts\pip.exe install -r requirements.txt` |
| `connection refused` on port 5432 | PostgreSQL not running → `net start postgresql-x64-15` |
| `connection refused` on port 6379 | Redis not running → start via WSL or Memurai |
| `venv\Scripts\Activate.ps1 not found` | Create venv: `python -m venv venv` then activate |
| Uvicorn uses wrong Python | Use `.\venv\Scripts\python.exe -m uvicorn app.main:app --reload` |
| Port 8000 already in use | Kill old process: `netstat -ano \| findstr :8000` then `taskkill /PID <pid> /F` |
| `npm run dev` fails | Run `npm install` first in `frontend/` directory |
| CORS errors in browser | Ensure backend is on `:8000` and frontend on `:5173` |

---

## Project Structure Reminder

```
d:\SOCForge\
├── .env                    # Environment variables (DO NOT COMMIT)
├── docker-compose.yml      # Container orchestration
├── backend/
│   ├── venv/               # Python virtual environment
│   ├── requirements.txt    # Python dependencies
│   ├── app/
│   │   ├── main.py         # FastAPI application entry
│   │   ├── config.py       # Settings from .env
│   │   ├── database.py     # Async SQLAlchemy engine
│   │   ├── routers/        # 8 API routers
│   │   ├── models/         # 6 SQLAlchemy models
│   │   ├── services/       # Detection, simulation, correlation
│   │   ├── schemas/        # Pydantic request/response schemas
│   │   └── utils/          # Security, validators
│   └── tests/              # Pytest test suite
└── frontend/
    ├── src/
    │   ├── App.jsx          # React router (8 pages)
    │   ├── api/client.js    # Axios API client
    │   ├── pages/           # Dashboard, Alerts, Simulation, etc.
    │   └── components/      # Reusable UI components
    └── package.json
```
