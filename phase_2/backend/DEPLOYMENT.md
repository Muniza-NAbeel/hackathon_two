# 🚀 Backend Deployment Guide - Render

## Deploy Karne Ka Tareeqa (Step-by-Step)

### ✅ Pre-requisites (Pehle ye ready rakhein)

1. **GitHub Account** - Apna code GitHub pe push karna hoga
2. **Render Account** - [render.com](https://render.com) pe free account banayen
3. **Neon Database** - Apka Neon PostgreSQL URL ready ho

---

## 📋 Step 1: GitHub Pe Code Push Karein

```bash
# Agar abhi tak push nahi kiya
cd /mnt/d/assignments/hackathon_two
git add phase_2/backend/
git commit -m "Add Render deployment configuration"
git push origin main
```

---

## 📋 Step 2: Render Dashboard Setup

### 2.1 Render Pe Login Karein
1. [https://dashboard.render.com](https://dashboard.render.com) pe jayen
2. GitHub se login karein

### 2.2 New Web Service Banayen
1. **"New +"** button pe click karein
2. **"Web Service"** select karein
3. Apni GitHub repository connect karein
4. Repository search karein aur select karein

### 2.3 Configuration Settings

**Basic Settings:**
- **Name**: `todo-backend-api` (ya koi bhi naam)
- **Region**: Oregon (ya nearest)
- **Branch**: `main`
- **Root Directory**: `phase_2/backend`
- **Runtime**: `Python 3`
- **Build Command**:
  ```bash
  chmod +x build.sh && ./build.sh
  ```
- **Start Command**:
  ```bash
  uvicorn app.main:app --host 0.0.0.0 --port $PORT
  ```

**Instance Type:**
- **Free** (512 MB RAM, sleeps after 15 min inactivity)

---

## 📋 Step 3: Environment Variables Setup

Render dashboard mein **"Environment"** tab pe jayen aur ye variables add karein:

### Required Environment Variables:

| Key | Value | Notes |
|-----|-------|-------|
| `DATABASE_URL` | `postgresql+asyncpg://user:pass@host/db?sslmode=require` | Apna Neon database URL paste karein |
| `BETTER_AUTH_SECRET` | (Auto-generate karein ya custom) | Minimum 32 characters |
| `ALLOWED_ORIGINS` | `https://your-frontend.vercel.app,http://localhost:3000` | Frontend URL yahan add karein |
| `PYTHON_VERSION` | `3.11.0` | Python version |
| `DEBUG` | `false` | Production mein false rakhein |

### Environment Variables Kaise Add Karein:

1. **"Environment"** tab pe click karein
2. **"Add Environment Variable"** pe click karein
3. Key aur Value enter karein
4. **"Add"** button pe click karein
5. Sab variables add karne ke baad **"Save Changes"**

**⚠️ Important:**
- `DATABASE_URL` mein apna actual Neon PostgreSQL connection string use karein
- `ALLOWED_ORIGINS` mein apni deployed frontend ka URL add karein

---

## 📋 Step 4: Deploy Karein!

1. Sab settings confirm karne ke baad neeche **"Create Web Service"** pe click karein
2. Render automatically:
   - Code pull karega
   - Dependencies install karega
   - Database migrations run karega
   - App start karega

**Deployment logs live dekh sakte hain** console mein.

---

## 🎉 Step 5: Verify Deployment

Deployment complete hone ke baad:

1. Render aap ko ek URL dega: `https://todo-backend-api-xxxx.onrender.com`
2. Health check test karein:
   ```
   https://todo-backend-api-xxxx.onrender.com/health
   ```
3. Response aye to sab theek hai: `{"status": "healthy"}`

---

## 🔗 Step 6: Frontend Se Connect Karein

Ab apni deployed backend ka URL apne frontend mein use karein:

### Frontend Environment Variable Update:
```env
NEXT_PUBLIC_API_URL=https://todo-backend-api-xxxx.onrender.com
```

Vercel dashboard mein:
1. **Settings** > **Environment Variables**
2. `NEXT_PUBLIC_API_URL` update karein
3. **Redeploy** karein

---

## 🐛 Troubleshooting (Agar koi issue aaye)

### Issue 1: Build Fail
**Solution:** Logs check karein. Usually:
- `requirements.txt` mein missing dependencies
- Database connection issue

### Issue 2: Database Connection Error
**Solution:**
- `DATABASE_URL` correct hai check karein
- Neon database ka format: `postgresql+asyncpg://...`
- SSL mode `?sslmode=require` jaroor ho

### Issue 3: CORS Error
**Solution:**
- `ALLOWED_ORIGINS` mein frontend URL sahi hai check karein
- Multiple origins comma se separate karein

### Issue 4: 15 Min Sleep Mode
**Solution:**
- Free tier limitation hai
- Pehli request slow hogi (30-60 sec)
- Upgrade to paid plan for always-on

---

## 📊 Monitoring

### Logs Dekhne Ke Liye:
1. Render dashboard > Your Service
2. **"Logs"** tab pe click karein
3. Real-time logs dekh sakte hain

### Metrics:
- **"Metrics"** tab: CPU, Memory usage dekh sakte hain

---

## 🔄 Updates Deploy Karna

Future mein code update karna ho to:

1. Code change karein locally
2. Git push karein:
   ```bash
   git add .
   git commit -m "Your update message"
   git push origin main
   ```
3. Render **automatically redeploy karega**

---

## 💰 Cost (Free Tier)

- **✅ Monthly Cost**: $0
- **✅ Bandwidth**: Unlimited
- **✅ Hours**: 750/month (ek app ke liye enough)
- **❌ Limitation**: 15 min inactivity = sleep mode

---

## 🎯 Quick Reference - Important URLs

After deployment:
- **Backend URL**: `https://your-app.onrender.com`
- **Health Check**: `https://your-app.onrender.com/health`
- **API Docs**: `https://your-app.onrender.com/docs`
- **Dashboard**: [https://dashboard.render.com](https://dashboard.render.com)

---

## ✨ Next Steps

1. ✅ Backend deploy ho gaya
2. 🔗 Frontend environment variables update karein
3. 🧪 API endpoints test karein
4. 🎉 Full-stack app live!

**Need help? Render documentation: https://render.com/docs**
