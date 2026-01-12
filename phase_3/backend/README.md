# Phase 3 Backend - AI-Powered Chatbot API

FastAPI backend for AI-powered task management chatbot using OpenAI Agents SDK and MCP tools.

## Setup

### Using UV (Recommended - Fast!)

```bash
# Install uv if not already installed
curl -LsSf https://astral.sh/uv/install.sh | sh

# Create virtual environment and install dependencies
cd phase_3/backend
uv venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
uv pip install -r requirements.txt
```

### Using pip (Traditional)

```bash
cd phase_3/backend
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

## Environment Variables

Create `.env` file in `phase_3/` root:

```env
DATABASE_URL=postgresql://user:password@localhost:5432/phase3_db
OPENAI_API_KEY=sk-your-key-here
JWT_SECRET=your-jwt-secret
MCP_SERVER_URL=http://localhost:8001
```

## Run Development Server

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

## Run Tests

```bash
pytest
pytest --cov  # With coverage
```

## Project Structure

```
app/
├── api/              # API endpoints
├── auth/             # JWT authentication
├── db/               # Database session and migrations
├── models/           # SQLModel database models
├── services/         # Business logic (AI agent, conversation loader)
└── config.py         # Configuration management
```
