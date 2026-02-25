# SOCForge — Zero-Cost Deployment & GitHub Publication Guide

> **For college students with ₹0 infrastructure budget.**

---

## Part 1: Free-Tier Deployment Options

### Recommended Zero-Cost Architecture ⭐

| Component | Free Provider | Limit | Cost |
|-----------|--------------|-------|------|
| **Backend** | [Render](https://render.com) | 750 hours/month, auto-sleep | ₹0 |
| **Frontend** | [Vercel](https://vercel.com) | Unlimited for personal | ₹0 |
| **PostgreSQL** | [Neon.tech](https://neon.tech) | 0.5 GB, auto-suspend | ₹0 |
| **Redis** | [Upstash](https://upstash.com) | 10K commands/day | ₹0 |
| **TLS/HTTPS** | Automatic (Render + Vercel) | Included | ₹0 |
| **CI/CD** | GitHub Actions | 2000 min/month | ₹0 |
| **Total** | | | **₹0/month** |

### Full Comparison Table

| Option | Cost | Backend | DB | Pros | Cons |
|--------|------|---------|-----|------|------|
| **Render + Neon** | ₹0 | ✅ | ✅ | Easy deploy, auto-HTTPS, GitHub integration | Backend sleeps after 15min inactivity |
| Railway | ₹0 (trial) | ✅ | ✅ | Fast deploy | Free tier credits expire (~$5/month) |
| Fly.io | ₹0 | ✅ | ❌ | Global edge | Needs separate DB, complex CLI setup |
| Oracle Cloud Always Free | ₹0 | ✅ | ✅ | 2 VMs forever, full control | Complex setup, slow provisioning |
| Vercel (frontend only) | ₹0 | ❌ | ❌ | Best for React, instant deploys | Backend needs separate host |
| AWS Free Tier | ₹0 (12 months) | ✅ | ✅ | Full AWS, student credits | Expires after 12 months, complex |
| Self-hosted (your PC) | ₹0 | ✅ | ✅ | Full control, no limits | Not accessible externally, needs Ngrok |

---

## Part 2: Step-by-Step Deployment (₹0)

### Step 1: Deploy Frontend on Vercel

```bash
# 1. Push code to GitHub first (see Part 4 below)
# 2. Go to https://vercel.com → Sign in with GitHub
# 3. Click "Import Project" → Select your SOCForge repo
# 4. Set:
#    - Framework: Vite
#    - Root directory: frontend
#    - Build command: npm run build
#    - Output directory: dist
# 5. Add environment variable:
#    VITE_API_URL = https://your-backend.onrender.com
# 6. Click Deploy
```

### Step 2: Deploy Backend on Render

```bash
# 1. Go to https://render.com → Sign in with GitHub
# 2. Click "New Web Service" → Select SOCForge repo
# 3. Set:
#    - Root directory: backend
#    - Runtime: Python 3
#    - Build command: pip install -r requirements.txt
#    - Start command: uvicorn app.main:app --host 0.0.0.0 --port $PORT
# 4. Add environment variables:
#    DATABASE_URL = (from Neon.tech, see Step 3)
#    REDIS_URL = (from Upstash, see Step 4)
#    JWT_SECRET = (generate: python -c "import secrets; print(secrets.token_hex(32))")
#    ENVIRONMENT = production
# 5. Click Deploy
```

### Step 3: Free PostgreSQL on Neon.tech

```bash
# 1. Go to https://neon.tech → Sign up (free)
# 2. Create project "socforge"
# 3. Copy the connection string:
#    postgresql://user:pass@ep-xxx.region.aws.neon.tech/socforge?sslmode=require
# 4. IMPORTANT: Change the driver to asyncpg:
#    postgresql+asyncpg://user:pass@ep-xxx.region.aws.neon.tech/socforge?ssl=require
# 5. Paste as DATABASE_URL in Render
```

### Step 4: Free Redis on Upstash

```bash
# 1. Go to https://upstash.com → Sign up (free)
# 2. Create a Redis database (pick closest region)
# 3. Copy the Redis URL:
#    rediss://default:xxx@sharp-xxx.upstash.io:6379
# 4. Paste as REDIS_URL in Render
```

### Step 5: Update Frontend API URL

After Render gives you a URL (e.g., `https://socforge-api.onrender.com`), update the Vercel environment variable:

```
VITE_API_URL = https://socforge-api.onrender.com
```

Redeploy on Vercel → **Done! Your app is live at ₹0.**

---

## Part 3: Low-Cost Backup (Under ₹300/month)

If you outgrow free tiers:

| Service | Cost |
|---------|------|
| Railway Hobby ($5/month) | ~₹420/month |
| **Render Starter ($7/month)** | **~₹590/month (no sleep)** |
| DigitalOcean Droplet ($4/month) | ~₹330/month |

> **Recommendation**: Stay on free tier for portfolio/demo purposes. Paid only needed if real users use it daily.

---

## Part 4: GitHub Publication Guide

### ⚠️ Security First — CHANGE YOUR PASSWORD

> **You shared your GitHub password in the chat.** Change it **immediately** at https://github.com/settings/security. Use a **Personal Access Token** (PAT) instead of a password for Git operations.

### Pre-Push Security Checklist

- [x] `.gitignore` blocks `.env`, `venv/`, `node_modules/`, `.gemini/`
- [ ] **Remove `.env` from Git history** (if ever committed)
- [ ] Generate a fresh `JWT_SECRET` for production
- [ ] Verify no passwords in any source file

### Recommended: **Public Repository** ✅

**Why public?**
- Recruiters can view your code → stronger resume
- Shows confidence in code quality
- Enables GitHub Pages for docs
- Open-source credibility

### Step-by-Step Git Commands

```powershell
# Navigate to project
cd d:\SOCForge

# Initialize Git (if not already)
git init

# Add all files (`.gitignore` protects secrets)
git add .

# Verify no secrets are staged
git status
# CHECK: .env should NOT appear in the list

# First commit
git commit -m "feat: SOCForge - Enterprise SOC Platform with MITRE ATT&CK simulation"

# Create repository on GitHub:
# Go to https://github.com/new
# Name: SOCForge
# Description: Enterprise SOC Threat Detection & Attack Simulation Platform
# Public ✅
# Do NOT initialize with README (you already have one)

# Add remote and push
git remote add origin https://github.com/AtharvS7/SOCForge.git
git branch -M main
git push -u origin main
```

### If `.env` Was Previously Committed

```powershell
# Remove .env from Git tracking (keeps the local file)
git rm --cached .env
git commit -m "security: remove .env from tracking"
git push
```

---

## Part 5: Resume Positioning

### Short Summary (2–3 lines)
> Built SOCForge, a full-stack SOC platform that simulates MITRE ATT&CK-mapped cyber attacks, detects threats via configurable rule engines, and correlates alerts into multi-stage incidents. Features JWT auth, RBAC, real-time WebSocket streaming, SIEM integration, and Kubernetes deployment — all at zero infrastructure cost.

### Long Summary (6–8 lines)
> Designed and built SOCForge, an enterprise-grade Security Operations Center platform from scratch using FastAPI, PostgreSQL, Redis, and React. The system features a 5-scenario attack simulation engine mapped to 13 MITRE ATT&CK tactics and 27 techniques, a configurable detection engine with 6 rule types, and a correlation engine that groups alerts into multi-stage incidents with kill chain tracking. Infrastructure includes JWT authentication with bcrypt, RBAC across admin/analyst/viewer roles, Redis-backed rate limiting, WebSocket alert streaming, Splunk/ELK SIEM connectors, and Kubernetes deployment manifests. Validated under load at 122 requests/second with zero errors. Deployed at ₹0 using open-source tools and free-tier cloud resources.

### Resume Bullet Points

**For Technical Recruiter:**
> - Built a full-stack SOC platform (FastAPI + React) with 13 API endpoints, real-time WebSocket streaming, and MITRE ATT&CK attack simulation — sustained 122 req/sec under load testing

**For Security Engineer Role:**
> - Engineered a threat detection pipeline with MITRE ATT&CK-mapped simulation (13 tactics, 27 techniques), rule-based detection engine, and correlation engine grouping alerts into kill-chain-tracked incidents

**For Academic/Professor:**
> - Developed SOCForge, an open-source SOC platform demonstrating automated threat detection, alert correlation, and incident response workflows — deployed at zero infrastructure cost using free-tier cloud services

---

## Part 6: Cost Justification Statement

> *"This project was built and deployed at ₹0 infrastructure cost using exclusively open-source frameworks (FastAPI, PostgreSQL, React) and free-tier cloud resources (Render for backend hosting, Vercel for frontend, Neon.tech for managed PostgreSQL, Upstash for Redis). TLS encryption is provided automatically by the hosting platforms at no additional cost. The CI/CD pipeline runs on GitHub Actions' free tier (2,000 minutes/month). The entire system — from attack simulation to incident correlation — operates without any paid dependencies or licensed software."*

---

## Part 7: Quick Reference

| What | Where |
|------|-------|
| **Live frontend** | `https://socforge.vercel.app` (after deploy) |
| **Live API** | `https://socforge-api.onrender.com` (after deploy) |
| **GitHub repo** | `https://github.com/AtharvS7/SOCForge` |
| **API docs** | `https://socforge-api.onrender.com/api/docs` |
| **Monthly cost** | **₹0** |
| **Deploy time** | ~30 minutes (first time) |
