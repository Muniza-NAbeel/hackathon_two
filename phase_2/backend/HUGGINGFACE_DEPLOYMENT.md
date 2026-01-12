# 🤗 Hugging Face Spaces Deployment Guide

## Bilkul Free Backend Deployment - Step by Step

---

## ✅ Kyun Hugging Face?

- **100% FREE forever** 🎉
- **No credit card** required
- **No sleep mode** (always running!)
- **2 CPU + 16 GB RAM** (basic tier)
- **GitHub integration** (auto-deploy)
- **Custom domain** support

---

## 📋 Step 1: Hugging Face Account Setup

1. [huggingface.co](https://huggingface.co) pe jayen
2. **Sign Up** - Email ya GitHub se
3. Email verify karein
4. Profile complete karein (optional)

---

## 📋 Step 2: Required Files Ready Karein

Ye files already bana di hain:

### ✅ Files Created:
1. **`Dockerfile.huggingface`** - Docker configuration
2. **`README_HUGGINGFACE.md`** - Space metadata
3. **`.env.example`** - Environment variables template

### 📁 File Structure Check:
```
phase_2/backend/
├── Dockerfile.huggingface      ← New (Hugging Face optimized)
├── README_HUGGINGFACE.md       ← New (Space configuration)
├── app/
│   ├── main.py
│   └── ...
├── requirements.txt
├── alembic.ini
└── alembic/
```

---

## 📋 Step 3: New Space Create Karein

### Dashboard pe jayen:

1. **Profile Icon** (top-right) > **New Space**

2. **Space Configuration:**
   - **Owner**: Your username
   - **Space name**: `todo-backend-api` (ya koi bhi naam)
   - **License**: MIT
   - **Select the Space SDK**: **Docker** ⚠️ (Important!)
   - **Space hardware**: **CPU basic (Free)** ✅
   - **Visibility**: **Public** (free tier requirement)

3. **Create Space** button click karein

---

## 📋 Step 4: Files Upload Karein

### Option A: Git Push (Recommended)

Space create hone ke baad, ye commands dikhayi denge:

```bash
cd /mnt/d/assignments/hackathon_two/phase_2/backend

# Hugging Face repository add karein
git remote add huggingface https://huggingface.co/spaces/YOUR_USERNAME/todo-backend-api

# Required files rename karein (Important!)
cp Dockerfile.huggingface Dockerfile
cp README_HUGGINGFACE.md README.md

# Files commit aur push karein
git add .
git commit -m "Initial Hugging Face deployment"
git push huggingface main
```

**⚠️ Important:**
- Hugging Face requires `Dockerfile` (not `Dockerfile.huggingface`)
- `README.md` mein metadata hona chahiye (YAML frontmatter)

### Option B: Web Upload (Easy but Manual)

1. Space dashboard mein **Files** tab pe jayen
2. **Add file** > **Upload files** click karein
3. Ye files upload karein:
   - `Dockerfile.huggingface` → rename to `Dockerfile`
   - `README_HUGGINGFACE.md` → rename to `README.md`
   - `app/` folder (pura)
   - `requirements.txt`
   - `alembic/` folder
   - `alembic.ini`
4. **Commit changes** button click karein

---

## 📋 Step 5: Environment Variables (Secrets)

**Important:** Database credentials aur secrets ko Space settings mein add karna hai, code mein nahi!

### Settings pe jayen:

1. Space dashboard > **Settings** tab
2. **Repository secrets** section scroll karein
3. **New secret** button click karein

### Add These Secrets:

**⚠️ CRITICAL: NO QUOTES around values!**

| Secret Name | Value | Example |
|------------|-------|---------|
| `DATABASE_URL` | Neon PostgreSQL URL (**NO QUOTES!** - asyncpg uses `ssl=True` in connect_args) | `postgresql+asyncpg://user:pass@ep-xxx.aws.neon.tech/db` |
| `BETTER_AUTH_SECRET` | Random 32+ character string (**NO QUOTES!**) | `abcd1234efgh5678ijkl9012mnop3456` |
| `ALLOWED_ORIGINS` | Frontend URLs (comma-separated) | `https://your-app.vercel.app,http://localhost:3000` |

**⚠️ Common Mistake:**
```
❌ WRONG: 'postgresql+asyncpg://...'  (has quotes)
❌ WRONG: "postgresql+asyncpg://..."  (has quotes)
✅ CORRECT: postgresql+asyncpg://...  (no quotes)
```

### Secret Generate Karne Ka Tareeqa:

```bash
# Python se random secret generate karein
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

**⚠️ Important:** Secrets ko `Dockerfile` ya code mein **kabhi hardcode na karein**!

---

## 📋 Step 6: Dockerfile Mein Environment Variables Use Karein

Hugging Face automatically secrets ko environment variables ki tarah inject karta hai.

Aap ki **`Dockerfile.huggingface`** already configured hai:

```dockerfile
# Environment variables Hugging Face se automatically inject hote hain
# No changes needed!
```

**App code mein:**
```python
# app/config.py already uses os.getenv()
DATABASE_URL = os.getenv("DATABASE_URL")
BETTER_AUTH_SECRET = os.getenv("BETTER_AUTH_SECRET")
```

---

## 📋 Step 7: Build & Deploy

### Automatic Deployment:

1. Files upload/push karne ke baad, Hugging Face **automatically build start karega**
2. **Logs** tab pe jayen - build progress dekh sakte hain
3. Build steps:
   - 🔵 Building Docker image...
   - 🔵 Installing dependencies...
   - 🔵 Running migrations...
   - 🟢 Starting server...
   - ✅ App running! 🎉

### Build Time:
- First build: ~5-10 minutes
- Subsequent builds: ~3-5 minutes

---

## 📋 Step 8: Verify Deployment

### ✅ Check Health Endpoint:

Aap ka Space URL: `https://YOUR_USERNAME-todo-backend-api.hf.space`

```bash
curl https://YOUR_USERNAME-todo-backend-api.hf.space/health
```

**Expected Response:**
```json
{"status": "healthy"}
```

### ✅ API Documentation:

- **Swagger UI**: `https://YOUR_USERNAME-todo-backend-api.hf.space/docs`
- **ReDoc**: `https://YOUR_USERNAME-todo-backend-api.hf.space/redoc`

---

## 📋 Step 9: Frontend Se Connect Karein

### Frontend Environment Variable Update:

Vercel dashboard mein jayen:

1. **Settings** > **Environment Variables**
2. `NEXT_PUBLIC_API_URL` update karein:
   ```
   https://YOUR_USERNAME-todo-backend-api.hf.space
   ```
3. **Save** aur **Redeploy** karein

### CORS Check:

`ALLOWED_ORIGINS` secret mein frontend URL add karna na bhulein:
```
https://your-app.vercel.app
```

---

## 🐛 Troubleshooting

### Issue 1: "Could not parse SQLAlchemy URL" ⚠️ MOST COMMON

**Error Message:**
```
sqlalchemy.exc.ArgumentError: Could not parse SQLAlchemy URL from given URL string
```

**Root Cause:** DATABASE_URL environment variable has quotes or is not set

**Solution (Step-by-step):**

1. **Check Hugging Face Space Settings:**
   - Go to Settings → Repository secrets
   - Find `DATABASE_URL`
   - **CRITICAL**: Value should have **NO quotes**

2. **Correct Format (asyncpg uses ssl=True in connect_args, not ?sslmode=require):**
   ```
   ✅ postgresql+asyncpg://neondb_owner:password@ep-xxx.neon.tech/neondb

   ❌ postgresql+asyncpg://...?sslmode=require  (WRONG - asyncpg doesn't support sslmode)
   ❌ 'postgresql+asyncpg://...'  (WRONG - has quotes)
   ❌ "postgresql+asyncpg://..."  (WRONG - has quotes)
   ```

3. **If you see this in logs:**
   ```
   [ALEMBIC ERROR] DATABASE_URL not set or using default value!
   [ALEMBIC ERROR] Available env vars: [...]
   ```
   This means the environment variable is not being passed to the container.

4. **Fix Steps:**
   - Delete the old `DATABASE_URL` secret
   - Create new secret WITHOUT quotes
   - Restart the Space (Settings → Factory reboot)
   - Check logs for: `[ALEMBIC DEBUG] DATABASE_URL source: os.environ`

### Issue 2: Build Fails - "requirements.txt not found"

**Solution:**
```bash
# Make sure requirements.txt root directory mein hai
ls -la requirements.txt

# Agar missing hai to check karein path
```

### Issue 3: Database Connection Timeout

**Error Message:**
```
asyncio.exceptions.CancelledError
TimeoutError
```

**Solution:**
- Neon database sleeping ho sakta hai (free tier)
- Neon Console → Projects → Resume database
- Check connection string is for **Pooled connection** (has `-pooler` in hostname)
- **IMPORTANT:** Do NOT add `?sslmode=require` - asyncpg uses `ssl=True` in connect_args instead

### Issue 4: Port 7860 Error

**Solution:**
Dockerfile mein port 7860 use karna **mandatory** hai Hugging Face ke liye:

```dockerfile
EXPOSE 7860
ENV PORT=7860
```

### Issue 4: Migrations Fail

**Solution:**
```bash
# Locally test migrations
cd phase_2/backend
alembic upgrade head

# Agar error aaye, alembic configuration check karein
```

### Issue 5: CORS Error Frontend Pe

**Solution:**
1. `ALLOWED_ORIGINS` secret mein frontend URL add karein
2. Multiple origins comma se separate karein:
   ```
   https://app.vercel.app,https://app-staging.vercel.app
   ```

---

## 📊 Monitoring & Logs

### Real-time Logs Dekhein:

1. Space dashboard > **Logs** tab
2. Live logs stream hota hai
3. Errors aur warnings yahan dikhenge

### Common Log Patterns:

✅ **Successful Start:**
```
INFO:     Uvicorn running on http://0.0.0.0:7860
INFO:     Application startup complete.
```

❌ **Database Error:**
```
ERROR:    Could not connect to database
```
→ `DATABASE_URL` secret check karein

❌ **Migration Error:**
```
ERROR:    alembic.util.exc.CommandError
```
→ Alembic configuration check karein

---

## 🔄 Updates Deploy Karna

### Code Update:

```bash
# Local changes
git add .
git commit -m "Update feature"

# Hugging Face pe push
git push huggingface main
```

**Automatic Rebuild:** Hugging Face automatically rebuild aur redeploy karega!

---

## 💰 Cost & Limits (Free Tier)

### ✅ What's FREE:
- **CPU**: 2 vCPUs
- **RAM**: 16 GB
- **Storage**: 50 GB
- **Bandwidth**: Unlimited
- **Build time**: Unlimited
- **Uptime**: 24/7 (no sleep!)

### ❌ Limitations:
- **Public only** (private spaces paid)
- **Community hardware** (shared resources)
- **No GPU** (free tier)

---

## 🎯 Quick Reference

### Important URLs:

| Resource | URL |
|----------|-----|
| **Your Space** | `https://huggingface.co/spaces/USERNAME/todo-backend-api` |
| **API Base** | `https://USERNAME-todo-backend-api.hf.space` |
| **Health Check** | `https://USERNAME-todo-backend-api.hf.space/health` |
| **API Docs** | `https://USERNAME-todo-backend-api.hf.space/docs` |
| **Settings** | Space dashboard > Settings tab |
| **Logs** | Space dashboard > Logs tab |

### Environment Secrets:
- `DATABASE_URL` - Neon PostgreSQL connection
- `BETTER_AUTH_SECRET` - JWT secret (32+ chars)
- `ALLOWED_ORIGINS` - Frontend URLs (comma-separated)

---

## ✨ Next Steps

1. ✅ Backend Hugging Face pe deploy
2. 🔗 Frontend environment variables update
3. 🧪 API endpoints test karein
4. 🎉 Full-stack app live!

---

## 📚 Resources

- **Hugging Face Docs**: [https://huggingface.co/docs/hub/spaces](https://huggingface.co/docs/hub/spaces)
- **Docker SDK Guide**: [https://huggingface.co/docs/hub/spaces-sdks-docker](https://huggingface.co/docs/hub/spaces-sdks-docker)
- **FastAPI Docs**: [https://fastapi.tiangolo.com](https://fastapi.tiangolo.com)

---

## 🆘 Need Help?

Deployment mein koi issue aaye to:
1. **Logs** tab check karein
2. **Community** forum pe question post karein
3. Mujhe batao, main help karungi! 😊

**Happy Deploying! 🚀🤗**
