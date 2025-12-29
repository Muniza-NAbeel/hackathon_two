# Quickstart Guide: Todo Full-Stack Web Application (Phase II)

**Feature Branch**: `002-todo-fullstack-web-app`
**Date**: 2025-12-25

---

## Prerequisites

| Requirement | Version | Purpose |
|-------------|---------|---------|
| Python | 3.11+ | Backend runtime |
| Node.js | 18+ | Frontend runtime |
| Docker | 24+ | Containerization |
| Git | 2.x | Version control |

---

## Environment Setup

### 1. Clone and Navigate

```bash
cd hackathon_two/phase_2
```

### 2. Create Environment Files

#### Backend `.env`

Create `phase_2/backend/.env`:

```env
# Database
DATABASE_URL=postgresql://user:password@host:5432/todo_db

# Authentication
BETTER_AUTH_SECRET=your-secret-key-here-min-32-chars

# Server
HOST=0.0.0.0
PORT=8000
DEBUG=true
```

#### Frontend `.env.local`

Create `phase_2/frontend/.env.local`:

```env
# API
NEXT_PUBLIC_API_URL=http://localhost:8000

# Authentication
BETTER_AUTH_SECRET=your-secret-key-here-min-32-chars
```

> **Important**: `BETTER_AUTH_SECRET` must be identical in both frontend and backend.

---

## Backend Setup

### 1. Create Virtual Environment

```bash
cd phase_2/backend
python -m venv venv

# Windows
venv\Scripts\activate

# macOS/Linux
source venv/bin/activate
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Initialize Database

```bash
# Run migrations
python -m alembic upgrade head
```

### 4. Start Backend Server

```bash
# Development mode with hot reload
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### 5. Verify Backend

Open http://localhost:8000/docs for Swagger UI.

---

## Frontend Setup

### 1. Install Dependencies

```bash
cd phase_2/frontend
npm install
```

### 2. Start Development Server

```bash
npm run dev
```

### 3. Verify Frontend

Open http://localhost:3000 in browser.

---

## Docker Setup (Alternative)

### 1. Build and Start All Services

```bash
cd phase_2
docker-compose up --build
```

### 2. Services Overview

| Service | Port | URL |
|---------|------|-----|
| Frontend | 3000 | http://localhost:3000 |
| Backend | 8000 | http://localhost:8000 |
| API Docs | 8000 | http://localhost:8000/docs |

### 3. Stop Services

```bash
docker-compose down
```

---

## Database Setup (Neon)

### 1. Create Neon Project

1. Go to https://neon.tech
2. Create new project
3. Copy connection string

### 2. Configure Connection

Update `DATABASE_URL` in backend `.env`:

```env
DATABASE_URL=postgresql://user:password@ep-xxx.region.aws.neon.tech/neondb?sslmode=require
```

---

## Verification Checklist

### Backend Verification

```bash
# Health check
curl http://localhost:8000/health

# Expected response
{"status": "healthy"}
```

### Database Verification

```bash
# Check migrations applied
python -m alembic current

# Should show current revision
```

### API Verification

```bash
# Test registration endpoint
curl -X POST http://localhost:8000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email": "test@example.com", "password": "testpassword123"}'
```

### Frontend Verification

1. Open http://localhost:3000
2. See login/signup page
3. No console errors

---

## Common Issues

### Issue: Database Connection Failed

**Symptoms**: `Connection refused` or `timeout`

**Solutions**:
- Verify DATABASE_URL is correct
- Check if Neon project is active
- Ensure SSL mode is included for Neon

### Issue: JWT Token Invalid

**Symptoms**: `401 Unauthorized` on all requests

**Solutions**:
- Verify BETTER_AUTH_SECRET is identical in frontend and backend
- Check token expiration (7 days default)
- Clear browser storage and re-login

### Issue: CORS Errors

**Symptoms**: Browser blocks API requests

**Solutions**:
- Ensure backend CORS allows frontend origin
- Check NEXT_PUBLIC_API_URL matches backend URL

### Issue: Port Already in Use

**Symptoms**: `Address already in use`

**Solutions**:
```bash
# Kill process on port
# Windows
netstat -ano | findstr :8000
taskkill /PID <pid> /F

# macOS/Linux
lsof -i :8000
kill -9 <pid>
```

---

## Development Workflow

### 1. Start Development

```bash
# Terminal 1: Backend
cd phase_2/backend
source venv/bin/activate
uvicorn app.main:app --reload

# Terminal 2: Frontend
cd phase_2/frontend
npm run dev
```

### 2. Run Tests

```bash
# Backend tests
cd phase_2/backend
pytest

# Frontend tests
cd phase_2/frontend
npm test
```

### 3. Format Code

```bash
# Backend
cd phase_2/backend
black .
isort .

# Frontend
cd phase_2/frontend
npm run lint
npm run format
```

---

## Next Steps

1. Review `spec.md` for feature requirements
2. Review `data-model.md` for database schema
3. Review `contracts/openapi.yaml` for API specification
4. Run `/sp.tasks` to generate implementation tasks
