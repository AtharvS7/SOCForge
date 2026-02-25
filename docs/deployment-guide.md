# SOCForge Deployment Guide

## Docker Compose (Recommended)

### Prerequisites
- Docker Engine 20.10+
- Docker Compose V2
- 4GB RAM minimum

### Steps

1. **Clone the repository**
   ```bash
   git clone <repo-url>
   cd SOCForge
   ```

2. **Configure environment**
   ```bash
   cp .env.example .env
   # Edit .env with your secrets (especially JWT_SECRET, DB passwords)
   ```

3. **Start services**
   ```bash
   docker compose up --build -d
   ```

4. **Verify**
   ```bash
   # Check health
   curl http://localhost:8000/api/health

   # Access UI
   open http://localhost:5173
   ```

5. **Register a user** at `/login` and select your role

### Stopping
```bash
docker compose down          # Stop services
docker compose down -v       # Stop and remove volumes
```

## Local Development

### Backend
```bash
cd backend
python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows
pip install -r requirements.txt

# Requires PostgreSQL and Redis running locally
uvicorn app.main:app --reload --port 8000
```

### Frontend
```bash
cd frontend
npm install
npm run dev
```

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `DATABASE_URL` | See .env.example | PostgreSQL connection string |
| `REDIS_URL` | See .env.example | Redis connection string |
| `JWT_SECRET` | Random string | **MUST CHANGE** in production |
| `JWT_ALGORITHM` | HS256 | JWT signing algorithm |
| `JWT_EXPIRATION_MINUTES` | 480 | Token validity (8 hours) |
| `ENVIRONMENT` | development | dev / staging / production |

## Security Hardening Checklist
- [ ] Change all default passwords
- [ ] Set a strong, unique JWT_SECRET
- [ ] Enable HTTPS (reverse proxy)
- [ ] Restrict CORS origins in production
- [ ] Set ENVIRONMENT=production
- [ ] Enable firewall rules for ports
- [ ] Regular dependency updates
- [ ] Database backup schedule
