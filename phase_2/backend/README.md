---
title: Todo Backend API
emoji: 📝
colorFrom: blue
colorTo: purple
sdk: docker
pinned: false
app_port: 7860
---

# 📝 Todo Full-Stack Web Application - Backend API

A RESTful API for multi-user task management with JWT authentication.

## 🚀 Features

- ✅ User authentication (register, login, logout)
- ✅ JWT-based authorization (7-day expiry)
- ✅ CRUD operations for tasks
- ✅ User-scoped task isolation
- ✅ PostgreSQL database with migrations
- ✅ FastAPI with automatic OpenAPI docs

## 🛠️ Tech Stack

- **Framework**: FastAPI 0.109.0
- **ORM**: SQLModel 0.0.14
- **Database**: PostgreSQL (Neon Serverless)
- **Authentication**: JWT (python-jose)
- **Migration**: Alembic 1.13.1

## 📡 API Endpoints

### Authentication
- `POST /api/auth/register` - Register new user
- `POST /api/auth/login` - Login user
- `POST /api/auth/logout` - Logout user
- `GET /api/auth/me` - Get current user

### Tasks
- `GET /api/{user_id}/tasks` - List user tasks
- `POST /api/{user_id}/tasks` - Create task
- `GET /api/{user_id}/tasks/{task_id}` - Get task
- `PUT /api/{user_id}/tasks/{task_id}` - Update task
- `DELETE /api/{user_id}/tasks/{task_id}` - Delete task
- `PATCH /api/{user_id}/tasks/{task_id}/complete` - Toggle complete

## 🔧 Environment Variables

Required environment variables (set in Hugging Face Space settings):

```env
# Note: asyncpg uses ssl=True in connect_args, do not add ?sslmode=require
DATABASE_URL=postgresql+asyncpg://user:password@host/db
BETTER_AUTH_SECRET=your-secret-key-min-32-characters
ALLOWED_ORIGINS=https://your-frontend.vercel.app,http://localhost:3000
DEBUG=false
```

## 📚 API Documentation

Once deployed, visit:
- Swagger UI: `https://your-space.hf.space/docs`
- ReDoc: `https://your-space.hf.space/redoc`

## 🏥 Health Check

`GET /health` - Returns `{"status": "healthy"}`

## 🔗 Frontend Integration

This backend is designed to work with the Next.js 14+ frontend.

Update your frontend environment variable:
```env
NEXT_PUBLIC_API_URL=https://your-space.hf.space
```

## 📝 License

MIT License

## 👨‍💻 Developer

Built with FastAPI and deployed on Hugging Face Spaces 🤗
