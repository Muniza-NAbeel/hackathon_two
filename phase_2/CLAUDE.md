# Claude Code Instructions: Phase II Todo Full-Stack Web Application

## Overview

This is Phase II of the Todo application - a multi-user full-stack web application.

**Branch**: `002-todo-fullstack-web-app`

## Tech Stack

- **Backend**: Python 3.11+ with FastAPI and SQLModel
- **Frontend**: Next.js 14+ (App Router) with TypeScript and Tailwind CSS
- **Database**: Neon Serverless PostgreSQL
- **Authentication**: JWT with 7-day expiry

## Project Structure

```
phase_2/
├── backend/
│   ├── app/
│   │   ├── main.py              # FastAPI entry point
│   │   ├── config.py            # Environment configuration
│   │   ├── database.py          # Database connection
│   │   ├── models/              # SQLModel entities
│   │   ├── schemas/             # Pydantic schemas
│   │   ├── routers/             # API endpoints
│   │   ├── services/            # Business logic
│   │   └── middleware/          # JWT authentication
│   ├── tests/                   # pytest tests
│   ├── alembic/                 # Database migrations
│   └── requirements.txt
├── frontend/
│   ├── app/                     # Next.js App Router pages
│   │   ├── (auth)/              # Login/signup pages
│   │   └── (dashboard)/         # Protected pages
│   ├── components/              # React components
│   ├── lib/                     # Utilities and API client
│   ├── types/                   # TypeScript definitions
│   └── package.json
└── docker-compose.yml
```

## Key Rules

1. **Ownership Enforcement**: Users can only access their own tasks
2. **JWT Required**: All task endpoints require valid JWT in Authorization header
3. **Validation**: Title 1-200 chars, description max 1000 chars
4. **Stateless**: No server-side sessions, JWT-based authentication only

## API Endpoints

- `POST /api/auth/register` - Register new user
- `POST /api/auth/login` - Login user
- `POST /api/auth/logout` - Logout user
- `GET /api/auth/me` - Get current user
- `GET /api/{user_id}/tasks` - List user tasks
- `POST /api/{user_id}/tasks` - Create task
- `GET /api/{user_id}/tasks/{task_id}` - Get task
- `PUT /api/{user_id}/tasks/{task_id}` - Update task
- `DELETE /api/{user_id}/tasks/{task_id}` - Delete task
- `PATCH /api/{user_id}/tasks/{task_id}/complete` - Toggle complete

## Running Locally

### Backend
```bash
cd phase_2/backend
python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows
pip install -r requirements.txt
cp .env.example .env  # Configure DATABASE_URL and BETTER_AUTH_SECRET
uvicorn app.main:app --reload
```

### Frontend
```bash
cd phase_2/frontend
npm install
cp .env.example .env.local
npm run dev
```

### Docker
```bash
cd phase_2
docker-compose up --build
```

## Specifications

See `/specs/002-todo-fullstack-web-app/` for:
- `spec.md` - Feature requirements
- `plan.md` - Implementation plan
- `data-model.md` - Database schema
- `contracts/` - API specifications
- `tasks.md` - Implementation tasks
