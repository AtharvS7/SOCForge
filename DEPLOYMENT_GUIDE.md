# SOCForge — Production Deployment Guide

> **Exact steps to take SOCForge from your local machine to a live, working URL — at ₹0.**

---

## Current Status: ✅ READY TO DEPLOY

Everything works locally. The code is on GitHub. You just need to create accounts on 4 free platforms and paste URLs. **Estimated time: 30–45 minutes.**

---

## What You Need Before Starting

| Item | Status | Action |
|------|--------|--------|
| GitHub repo | ✅ Done | [github.com/AtharvS7/SOCForge](https://github.com/AtharvS7/SOCForge) |
| Vercel account | ❌ Needed | Sign up at [vercel.com](https://vercel.com) using GitHub |
| Render account | ❌ Needed | Sign up at [render.com](https://render.com) using GitHub |
| Neon.tech account | ❌ Needed | Sign up at [neon.tech](https://neon.tech) using GitHub |
| Upstash account | ❌ Needed | Sign up at [upstash.com](https://upstash.com) using GitHub |

> **All 4 accounts are free. No credit card required. Sign up with your GitHub account for fastest setup.**

---

## Step 1: Create Free PostgreSQL Database (Neon.tech)

**Time: 5 minutes**

1. Go to [https://neon.tech](https://neon.tech) → Click **Sign Up** → Use **GitHub login**
2. Click **Create Project**
   - Project name: `socforge`
   - Region: Pick the one closest to you (e.g., `Asia Pacific (Singapore)`)
   - Click **Create Project**
3. On the dashboard, you'll see a **Connection String**. It looks like:
   ```
   postgresql://neondb_owner:abc123@ep-cool-river-123.ap-southeast-1.aws.neon.tech/neondb?sslmode=require
   ```
4. **Modify it** — change `postgresql://` to `postgresql+asyncpg://` and `sslmode=require` to `ssl=require`:
   ```
   postgresql+asyncpg://neondb_owner:abc123@ep-cool-river-123.ap-southeast-1.aws.neon.tech/neondb?ssl=require
   ```
5. **Save this string** — you'll need it in Step 3 as `DATABASE_URL`

---

## Step 2: Create Free Redis (Upstash)

**Time: 3 minutes**

1. Go to [https://upstash.com](https://upstash.com) → Click **Sign Up** → Use **GitHub login**
2. Click **Create Database**
   - Name: `socforge-redis`
   - Region: Same region as your Neon database
   - Click **Create**
3. On the database page, find **REST URL** or **Redis URL**. It looks like:
   ```
   rediss://default:abc123xyz@apn1-funny-cat-12345.upstash.io:6379
   ```
4. **Save this string** — you'll need it in Step 3 as `REDIS_URL`

---

## Step 3: Deploy Backend on Render

**Time: 10 minutes**

1. Go to [https://render.com](https://render.com) → Click **Sign Up** → Use **GitHub login**
2. Click **New +** → **Web Service**
3. Click **Connect a Repository** → Select **AtharvS7/SOCForge**
4. Fill in:

   | Setting | Value |
   |---------|-------|
   | **Name** | `socforge-api` |
   | **Region** | Closest to you |
   | **Branch** | `main` |
   | **Root Directory** | `backend` |
   | **Runtime** | `Python 3` |
   | **Build Command** | `pip install -r requirements.txt` |
   | **Start Command** | `uvicorn app.main:app --host 0.0.0.0 --port $PORT` |
   | **Instance Type** | **Free** |

5. Click **Advanced** → **Add Environment Variable** → Add these **one by one**:

   | Key | Value |
   |-----|-------|
   | `DATABASE_URL` | The Neon string from Step 1 (the `postgresql+asyncpg://...` one) |
   | `REDIS_URL` | The Upstash string from Step 2 |
   | `JWT_SECRET` | A random string — generate one by running in your terminal: `python -c "import secrets; print(secrets.token_hex(32))"` |
   | `ENVIRONMENT` | `production` |
   | `LOG_LEVEL` | `WARNING` |

6. Click **Create Web Service**
7. Wait 3–5 minutes for the build and deploy
8. Render will give you a URL like: `https://socforge-api.onrender.com`
9. **Test it**: Open `https://socforge-api.onrender.com/api/health` in your browser — you should see `{"status": "operational"}`

> ⚠️ **Note**: On the free tier, the backend goes to sleep after 15 minutes of no traffic. The first request after sleep takes ~30 seconds to wake up. This is normal and fine for a portfolio project.

---

## Step 4: Deploy Frontend on Vercel

**Time: 5 minutes**

1. Go to [https://vercel.com](https://vercel.com) → Click **Sign Up** → Use **GitHub login**
2. Click **Add New Project** → **Import** the `AtharvS7/SOCForge` repository
3. Fill in:

   | Setting | Value |
   |---------|-------|
   | **Framework Preset** | `Vite` |
   | **Root Directory** | Click **Edit** → type `frontend` → Click **Continue** |
   | **Build Command** | `npm run build` |
   | **Output Directory** | `dist` |

4. Click **Environment Variables** → Add:

   | Key | Value |
   |-----|-------|
   | `VITE_API_URL` | Your Render backend URL (e.g., `https://socforge-api.onrender.com`) |

5. Click **Deploy**
6. Wait 1–2 minutes
7. Vercel will give you a URL like: `https://socforge.vercel.app`
8. **Test it**: Open the URL → You should see the SOCForge login page

---

## Step 5: First Login & Verification

**Time: 5 minutes**

After both services are deployed:

1. Open your Vercel URL (e.g., `https://socforge.vercel.app`)
2. You'll see the login page
3. **Register a new admin account** (the old local database accounts don't exist on Neon):
   - Click **Register** (or go to `/register`)
   - Username: `admin`
   - Email: `admin@socforge.io`
   - Password: `Admin123`
   - Role: `admin`
4. Login with those credentials
5. Run a simulation:
   - Go to **Attack Simulation**
   - Select **Full Attack Chain** → **Launch Simulation**
   - Wait for completion
6. Check **Dashboard** → Events, alerts, and incidents should appear
7. Check **Alert Monitor** → Alerts should be visible
8. Check **Investigation** → Incident should be visible

**If all of this works → your project is live! 🎉**

---

## Step 6: Update Your GitHub README (Optional but Recommended)

Add your live URLs to the README:

```markdown
## 🌐 Live Demo

- **Frontend**: [https://socforge.vercel.app](https://socforge.vercel.app)
- **Backend API**: [https://socforge-api.onrender.com/api/docs](https://socforge-api.onrender.com/api/docs)
```

---

## Troubleshooting

### "Backend returns 500 on first request"
- The free Render instance goes to sleep. Wait 30 seconds and try again.

### "Login says invalid credentials"
- You need to register a new account on the deployed version. The local database accounts don't carry over to Neon.

### "Frontend shows blank page or network error"
- Check that `VITE_API_URL` in Vercel matches your Render URL exactly (including `https://`).
- Redeploy on Vercel after changing environment variables.

### "Database connection error in Render logs"
- Verify the `DATABASE_URL` has `postgresql+asyncpg://` (not just `postgresql://`).
- Verify it ends with `?ssl=require` (not `?sslmode=require`).

### "Cannot register, says user already exists"
- This means the database is working. Try a different username, or login with the existing one.

---

## What's Running Where (Summary)

```
┌─────────────────────────────┐
│     Your Browser            │
│  https://socforge.vercel.app│
└─────────────┬───────────────┘
              │ API Calls
┌─────────────▼───────────────┐
│     Render (Free)           │
│  socforge-api.onrender.com  │
│  FastAPI Backend             │
└──────┬──────────┬───────────┘
       │          │
┌──────▼─────┐ ┌──▼──────────┐
│  Neon.tech │ │  Upstash    │
│ PostgreSQL │ │   Redis     │
│   (Free)   │ │  (Free)     │
└────────────┘ └─────────────┘
```

**Total monthly cost: ₹0**

---

## Optional: Enable Integrations (Not Required for Demo)

These are extras. They only activate if you add the environment variables in Render:

| Integration | Env Vars to Add | What It Does |
|-------------|----------------|--------------|
| Splunk SIEM | `SPLUNK_HEC_URL`, `SPLUNK_HEC_TOKEN` | Exports alerts to Splunk |
| Elasticsearch | `ELASTICSEARCH_URL`, `ELASTICSEARCH_API_KEY` | Exports alerts to ELK |
| Email alerts | `SMTP_HOST`, `SMTP_PORT`, `SMTP_USER`, `SMTP_PASSWORD` | Sends email on critical alerts |
| Slack alerts | `SLACK_WEBHOOK_URL` | Posts to Slack channel |
| VirusTotal | `VIRUSTOTAL_API_KEY` | Enriches IPs with threat data |
| AbuseIPDB | `ABUSEIPDB_API_KEY` | Checks IP abuse reports |

> None of these are required. The app works fully without them.

---

## You're Done!

Once Steps 1–5 are complete, SOCForge is live at ₹0/month. You can:
- Put the live URL on your resume
- Share it with professors
- Demo it in interviews
- Show it to recruiters

**Remember to change your GitHub password** since you shared it earlier in this session.
