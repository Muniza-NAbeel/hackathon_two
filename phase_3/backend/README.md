---
title: Todo App Ai Assistant
emoji: ⚡
colorFrom: blue
colorTo: purple
sdk: docker
app_port: 7860
pinned: false
license: mit
---

# Phase 3 Backend - AI-Powered Chatbot API

FastAPI backend for AI-powered task management chatbot using OpenAI Agents SDK and MCP tools.

## API Endpoints

- `GET /` - Root endpoint
- `GET /health` - Health check
- `GET /docs` - Swagger UI documentation
- `POST /api/auth/register` - User registration
- `POST /api/auth/login` - User login
- `GET /api/{user_id}/tasks` - Get user tasks
- `POST /api/{user_id}/chat` - AI Chat endpoint

## Environment Variables

Configure in Hugging Face Space Settings > Secrets:

- `DATABASE_URL` - PostgreSQL connection string (Neon)
- `OPENAI_API_KEY` - OpenAI API key
- `JWT_SECRET` - Secret for JWT tokens
- `CORS_ORIGINS` - Allowed frontend origins

## Local Development

```bash
cd phase_3/backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```
