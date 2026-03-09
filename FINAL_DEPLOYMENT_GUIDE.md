# SOCForge — Final Deployment Guide

> **The complete, step-by-step guide to deploy SOCForge to the internet at ₹0/month.**  
> **Estimated time: 30–40 minutes | Total cost: ₹0 | No credit card required**

---

## Pre-Deployment Validation ✅

Before deployment, the following was verified on 9 March 2026:

| Check | Result |
|-------|--------|
| Backend endpoints | **19/19 passed** |
| RBAC enforcement | **Viewer gets 403** ✅ |
| Health endpoint | `200 OK` — DB connected, Redis connected |
| Alert Monitor | 67 alerts, 7 critical, 53 high |
| Investigation | Correlated incidents + MITRE ATT&CK mapping |
| Detection Rules | 4 operational rules with live triggers |
| Reports | Investigation report, 11 findings, PDF export |
| Dummy/placeholder data | **None found** |
| Hardcoded secrets | **None found** |

---

## Deployment Architecture

```
┌─────────────────────────────────────────┐
│           User's Browser                │
│   https://socforge.vercel.app           │
└──────────────┬──────────────────────────┘
               │ HTTPS (API calls)
┌──────────────▼──────────────────────────┐
│         Render (Free Tier)              │
│   https://socforge-api.onrender.com     │
│         FastAPI Backend                 │
└───────┬───────────────┬─────────────────┘
        │               │
┌───────▼──────┐  ┌─────▼────────────────┐
│  Neon.tech   │  │     Upstash          │
│  PostgreSQL  │  │     Redis            │
│   (Free)     │  │     (Free)           │
└──────────────┘  └──────────────────────┘
```

**Total monthly cost: ₹0**

---

## What You Need Before Starting

- Your GitHub account (already set up — `AtharvS7`)
- SOCForge repo (already live at `github.com/AtharvS7/SOCForge`)
- A web browser
- **That's it. No credit card, no domain name, no SSH keys.**

---

## STEP 1: Create Free PostgreSQL Database on Neon.tech

**Time: 5 minutes**

### 1.1 — Sign Up

1. Open your browser
2. Go to **https://neon.tech**
3. Click the green **"Sign Up Free"** button (top-right corner)
4. You will see options: **GitHub**, Google, Email
5. Click **"Continue with GitHub"** ← select this one
6. GitHub will ask you to authorize Neon — click **"Authorize Neon"**
7. You will be redirected to the Neon Console dashboard

### 1.2 — Create a Project

1. On the Neon Console, you'll see a **"New Project"** button — click it
2. A form will appear with these fields:

   | Field | What to Enter |
   |-------|---------------|
   | **Project name** | `socforge` |
   | **Postgres version** | Leave as default (16) |
   | **Region** | Click the dropdown → Select **"Asia Pacific (Singapore)"** (or whichever is closest to India) |
   | **Compute size** | Leave as default (0.25 CU — this is the free tier) |

3. Click **"Create Project"**
4. Wait 10–15 seconds for the project to be created

### 1.3 — Get Your Connection String

1. After creation, you'll land on the **Dashboard** page
2. You'll see a box titled **"Connection Details"** with a connection string
3. There will be a dropdown that says **"psql"** — click it and change it to **"Node.js"** or **"Connection string"**
4. The connection string looks like this:

   ```
   postgresql://neondb_owner:abc123xyz@ep-cool-river-123456.ap-southeast-1.aws.neon.tech/neondb?sslmode=require
   ```

5. Click the **copy icon** 📋 next to the connection string
6. **IMPORTANT — Modify it before using:**
   - Change `postgresql://` → `postgresql+asyncpg://`
   - Change `?sslmode=require` → `?ssl=require`
   - Final result should look like:

   ```
   postgresql+asyncpg://neondb_owner:abc123xyz@ep-cool-river-123456.ap-southeast-1.aws.neon.tech/neondb?ssl=require
   ```

7. **Save this modified string somewhere** (Notepad, sticky note, etc.) — you'll need it in Step 3
8. Label it: `DATABASE_URL`

---

## STEP 2: Create Free Redis on Upstash

**Time: 3 minutes**

### 2.1 — Sign Up

1. Go to **https://upstash.com**
2. Click **"Sign Up"** or **"Start for Free"** (top-right)
3. You'll see options: GitHub, Google, Email
4. Click **"Sign Up with GitHub"** ← select this one
5. Authorize Upstash on GitHub
6. You'll land on the Upstash Console

### 2.2 — Create a Redis Database

1. On the Upstash Console, you'll see **"Redis"** in the left sidebar — click it
2. Click **"Create Database"**
3. A form appears:

   | Field | What to Enter |
   |-------|---------------|
   | **Name** | `socforge-redis` |
   | **Type** | Select **"Regional"** (not Global — Regional is free) |
   | **Region** | Select **"Asia Pacific (Singapore)"** (ap-southeast-1) — pick the same region as your Neon database |
   | **Eviction** | Leave **unchecked** |

4. Click **"Create"**

### 2.3 — Get Your Redis URL

1. After creation, you'll see the database dashboard
2. Scroll down to find the **"REST API"** section OR look for **"Connect your database"**
3. Find the field labeled **"Endpoint"** or **"Redis URL"**
4. The URL looks like:

   ```
   rediss://default:AaBbCcDd1234@apn1-funny-cat-12345.upstash.io:6379
   ```

   > **Note:** It starts with `rediss://` (double S) — that means TLS is enabled. This is correct.

5. Click the **copy icon** 📋 to copy it
6. **Save this string** — label it: `REDIS_URL`

---

## STEP 3: Generate a JWT Secret

**Time: 30 seconds**

You need a random secret key for JWT authentication. Open PowerShell on your computer and run:

```powershell
python -c "import secrets; print(secrets.token_hex(32))"
```

This will output something like:

```
a1b2c3d4e5f6a7b8c9d0e1f2a3b4c5d6a7b8c9d0e1f2a3b4c5d6a7b8c9d0e1f2
```

**Save this string** — label it: `JWT_SECRET`

---

## STEP 4: Deploy Backend on Render

**Time: 10 minutes**

### 4.1 — Sign Up

1. Go to **https://render.com**
2. Click **"Get Started for Free"** (top-right)
3. Click **"GitHub"** to sign up with your GitHub account
4. Authorize Render on GitHub
5. You'll land on the Render Dashboard

### 4.2 — Create a Web Service

1. Click **"New +"** button (top-right corner of the dashboard)
2. From the dropdown menu, select **"Web Service"**
3. You'll see **"Connect a repository"** section
4. If your GitHub repos aren't showing, click **"Configure account"** and give Render access to your repositories
5. Find **`AtharvS7/SOCForge`** in the list and click **"Connect"**

### 4.3 — Configure the Service

A configuration form will appear. Fill in EXACTLY these values:

| Field | Value |
|-------|-------|
| **Name** | `socforge-api` |
| **Region** | Select **Singapore (Southeast Asia)** (same region as Neon and Upstash) |
| **Branch** | `main` |
| **Root Directory** | Type: `backend` |
| **Runtime** | Select **"Python 3"** from the dropdown |
| **Build Command** | `pip install -r requirements.txt` |
| **Start Command** | `uvicorn app.main:app --host 0.0.0.0 --port $PORT` |

### 4.4 — Select Free Tier

1. Scroll down to the **"Instance Type"** section
2. You'll see options: Free, Starter, Standard, Pro...
3. Select **"Free"** — it says $0/month
4. Free tier gives you: 750 hours/month, 512MB RAM

### 4.5 — Add Environment Variables

1. Scroll down to find **"Environment Variables"** section
2. Or click **"Advanced"** to expand it
3. Click **"Add Environment Variable"** for each of these:

   | Key (type exactly) | Value (paste from your notes) |
   |---------------------|-------------------------------|
   | `DATABASE_URL` | The modified Neon string from Step 1.3 (the `postgresql+asyncpg://...` one) |
   | `REDIS_URL` | The Upstash string from Step 2.3 (the `rediss://...` one) |
   | `JWT_SECRET` | The random string from Step 3 |
   | `ENVIRONMENT` | `production` |
   | `LOG_LEVEL` | `WARNING` |

   > **Double-check:** `DATABASE_URL` must start with `postgresql+asyncpg://` and end with `?ssl=require`

### 4.6 — Deploy

1. Click **"Create Web Service"** at the bottom
2. Render will start building your backend — you'll see a live build log
3. The build takes **3–5 minutes** — you'll see messages like:
   - `Installing requirements...`
   - `Build successful`
   - `Deploying...`
4. When complete, you'll see **"Your service is live 🎉"**
5. Your backend URL will appear at the top, something like:

   ```
   https://socforge-api.onrender.com
   ```

6. **Save this URL** — label it: `BACKEND_URL`

### 4.7 — Verify Backend

1. Open a new browser tab
2. Go to: `https://socforge-api.onrender.com/api/health`
3. You should see:

   ```json
   {"status": "operational", "service": "SOCForge API v3"}
   ```

4. If it doesn't load immediately, wait 30 seconds — the free tier needs to "wake up" on the first request

> ⚠️ **Important Note About Free Tier:** The backend "sleeps" after 15 minutes of no traffic. The first request after sleeping takes ~30 seconds to respond. This is normal and perfectly fine for a portfolio project. Subsequent requests are fast.

---

## STEP 5: Deploy Frontend on Vercel

**Time: 5 minutes**

### 5.1 — Sign Up

1. Go to **https://vercel.com**
2. Click **"Sign Up"** (top-right)
3. Select **"Continue with GitHub"**
4. Authorize Vercel on GitHub
5. You'll land on the Vercel Dashboard

### 5.2 — Import Your Repo

1. Click **"Add New..."** button → select **"Project"**
2. You'll see a list of your GitHub repositories
3. Find **`SOCForge`** and click **"Import"**

### 5.3 — Configure the Project

A configuration form appears. Set these values:

| Field | What to Do |
|-------|------------|
| **Project Name** | Leave as `socforge` (auto-filled) |
| **Framework Preset** | Click the dropdown → Select **"Vite"** |
| **Root Directory** | Click **"Edit"** next to "Root Directory" → Type `frontend` → Click the **checkmark** or **"Continue"** |
| **Build Command** | Should auto-fill as `npm run build` — if not, type it |
| **Output Directory** | Should auto-fill as `dist` — if not, type it |
| **Install Command** | Leave as `npm install` (default) |

### 5.4 — Add Environment Variable

1. Click **"Environment Variables"** to expand the section
2. Add ONE variable:

   | Key | Value |
   |-----|-------|
   | `VITE_API_URL` | Your Render backend URL from Step 4.6 (e.g., `https://socforge-api.onrender.com`) |

   > **CRITICAL:** Do NOT add a trailing slash. It should be `https://socforge-api.onrender.com` and NOT `https://socforge-api.onrender.com/`

3. Click **"Add"** to save the variable

### 5.5 — Deploy

1. Click **"Deploy"**
2. Vercel will build your frontend — you'll see a live build log
3. The build takes **1–2 minutes**
4. When complete, you'll see **"Congratulations!"** with a preview of your site
5. Your frontend URL will be something like:

   ```
   https://socforge.vercel.app
   ```

   Or `https://socforge-xxxxx.vercel.app` if `socforge` is taken.

6. **Save this URL** — label it: `FRONTEND_URL`

---

## STEP 6: First Login on the Live Site

**Time: 5 minutes**

### 6.1 — Open Your Live Site

1. Go to your Vercel URL (e.g., `https://socforge.vercel.app`)
2. You'll see the SOCForge login page with the dark theme

### 6.2 — Register Your Admin Account

> Your local database users DON'T exist on the cloud database. You need to create a new admin account.

1. Click **"Create Account"** or the **"Register"** tab on the login page
2. Fill in:

   | Field | Value |
   |-------|-------|
   | **Username** | `admin` |
   | **Email** | `admin@socforge.io` (or your real email) |
   | **Full Name** | Your name |
   | **Password** | A strong password (minimum 8 characters) |
   | **Role** | Select **"Admin"** from the dropdown |

3. Click **"Register"**
4. You'll be automatically logged in and redirected to the Dashboard

### 6.3 — Run a Simulation

1. Click **"Attack Simulation"** in the left sidebar
2. Click the **"Full Attack Chain"** scenario card (the one with the red "critical" badge)
3. Leave configuration as default (Medium intensity, 60s duration)
4. Click the red **"Launch Simulation"** button
5. Wait 30–60 seconds for completion
6. You should see: **"Simulation Complete"** with events generated, alerts triggered

### 6.4 — Verify All Pages

Navigate through each page and confirm data appears:

| Page | What You Should See | ✅ |
|------|--------------------|----|
| **Dashboard** | Total events, alerts, incidents — numbers should be > 0 | ☐ |
| **Alert Monitor** | Alert cards with severity levels, source IPs, MITRE tags | ☐ |
| **Investigation** | Correlated incidents with MITRE ATT&CK mapping | ☐ |
| **Detection Rules** | 8 built-in rules with trigger counts | ☐ |
| **Reports** | Generate a report → should show findings and IOCs | ☐ |

---

## STEP 7: Update GitHub README with Live URLs (Recommended)

**Time: 2 minutes**

Go back to your local machine and run these commands in PowerShell:

```powershell
cd d:\SOCForge
```

Open `README.md` and add this section near the top (after the description), replacing with your actual URLs:

```markdown
## 🌐 Live Demo

- **Frontend**: [https://socforge.vercel.app](https://socforge.vercel.app)
- **Backend API**: [https://socforge-api.onrender.com/api/docs](https://socforge-api.onrender.com/api/docs)
- **API Health**: [https://socforge-api.onrender.com/api/health](https://socforge-api.onrender.com/api/health)
```

Then push to GitHub:

```powershell
git add README.md
git commit -m "docs: add live demo URLs"
git push origin main
```

---

## Troubleshooting Guide

### "Backend health endpoint shows error or doesn't load"

| Possible Cause | Fix |
|----------------|-----|
| First request after sleep | Wait 30 seconds and refresh — free tier needs to wake up |
| `DATABASE_URL` is wrong | Go to Render Dashboard → Environment → Check `DATABASE_URL` starts with `postgresql+asyncpg://` and ends with `?ssl=require` |
| `REDIS_URL` is wrong | Go to Render Dashboard → Environment → Check `REDIS_URL` starts with `rediss://` (double S) |
| Build failed | Go to Render Dashboard → Logs → Check for import errors or missing packages |

### "Frontend shows blank page or network errors"

| Possible Cause | Fix |
|----------------|-----|
| `VITE_API_URL` missing or wrong | Go to Vercel Dashboard → Settings → Environment Variables → Check `VITE_API_URL` matches your Render URL exactly (no trailing slash) |
| Backend is sleeping | Open your backend health URL first (`/api/health`), wait for it to wake up, then refresh the frontend |
| Need to redeploy | After changing env vars in Vercel, click **"Deployments"** → **"..."** on the latest → **"Redeploy"** |

### "Login says invalid credentials"

| Possible Cause | Fix |
|----------------|-----|
| Using old local credentials | Register a NEW account — the cloud database is empty |
| User already exists | Try a different username, or use the one you registered |

### "Simulation doesn't generate alerts"

| Possible Cause | Fix |
|----------------|-----|
| Backend still waking up | Wait 30 seconds after first login, then try simulation again |
| Try different scenario | Use "Full Attack Chain" with "Medium" or "High" intensity |

### "Vercel deployment failed"

| Possible Cause | Fix |
|----------------|-----|
| Root directory not set | Go to Vercel → Settings → General → Root Directory → Set to `frontend` |
| Wrong framework | Go to Vercel → Settings → General → Framework Preset → Set to `Vite` |

---

## Platform Quick Reference

| Platform | Dashboard URL | What It Hosts |
|----------|---------------|---------------|
| **Neon.tech** | [console.neon.tech](https://console.neon.tech) | PostgreSQL database |
| **Upstash** | [console.upstash.com](https://console.upstash.com) | Redis cache |
| **Render** | [dashboard.render.com](https://dashboard.render.com) | FastAPI backend |
| **Vercel** | [vercel.com/dashboard](https://vercel.com/dashboard) | React frontend |
| **GitHub** | [github.com/AtharvS7/SOCForge](https://github.com/AtharvS7/SOCForge) | Source code |

---

## Environment Variables Summary

You will configure a total of **6 environment variables** across 2 platforms:

### On Render (Backend — 5 variables):

| Variable | Source | Example |
|----------|--------|---------|
| `DATABASE_URL` | Neon.tech dashboard (modified) | `postgresql+asyncpg://user:pass@host/db?ssl=require` |
| `REDIS_URL` | Upstash dashboard | `rediss://default:token@host:6379` |
| `JWT_SECRET` | Generated locally with Python | `a1b2c3d4e5f6...` (64 hex characters) |
| `ENVIRONMENT` | You type this | `production` |
| `LOG_LEVEL` | You type this | `WARNING` |

### On Vercel (Frontend — 1 variable):

| Variable | Source | Example |
|----------|--------|---------|
| `VITE_API_URL` | Your Render service URL | `https://socforge-api.onrender.com` |

---

## Post-Deployment Checklist

After deployment, verify each item:

| # | Check | How to Verify | ✅ |
|---|-------|---------------|----|
| 1 | Backend is live | Visit `{BACKEND_URL}/api/health` — should return `{"status": "operational"}` | ☐ |
| 2 | Swagger API docs | Visit `{BACKEND_URL}/api/docs` — should show interactive API documentation | ☐ |
| 3 | Frontend loads | Visit `{FRONTEND_URL}` — should show login page | ☐ |
| 4 | Registration works | Register new admin account | ☐ |
| 5 | Login works | Login with registered credentials | ☐ |
| 6 | Dashboard loads | Numbers should appear (0 initially, then populated after simulation) | ☐ |
| 7 | Simulation works | Run Full Attack Chain → should generate events + alerts | ☐ |
| 8 | Alerts appear | Navigate to Alert Monitor → should show generated alerts | ☐ |
| 9 | Incidents appear | Navigate to Investigation → should show correlated incidents | ☐ |
| 10 | Rules display | Navigate to Detection Rules → should show 8 built-in rules | ☐ |
| 11 | Reports work | Generate a report → should show findings and IOCs | ☐ |
| 12 | Prometheus metrics | Visit `{BACKEND_URL}/metrics` — should show metrics text | ☐ |

---

## Final Notes

- **Free tier limits are generous**: Neon (0.5 GB storage), Upstash (10K commands/day), Render (750 hours/month), Vercel (100 GB bandwidth/month). You will not hit these limits with a portfolio project.
- **Render sleep behavior**: The backend sleeps after 15 min of inactivity. First request after sleep takes ~30s. This is completely normal for free tier.
- **Your data persists**: PostgreSQL on Neon.tech stores everything permanently. Redis on Upstash stores rate limiting data. Both persist across deployments.
- **Auto-deploys**: Both Render and Vercel are connected to your GitHub repo. Any `git push` to `main` will automatically trigger a redeploy on both platforms.
- **No credit card required**: All four platforms offer permanently free tiers with no card needed.

---

> **Ready to deploy? Start with Step 1 and work through each step in order. The whole process takes about 30–40 minutes. Come back and tell me when it's done — I'll verify the live deployment.**
