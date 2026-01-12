#!/bin/bash
# Backend Startup Script for Phase 3 AI Chatbot

set -e

echo "🚀 Starting Phase 3 Backend..."

# Check required environment variables
if [ -z "$DATABASE_URL" ]; then
    echo "❌ DATABASE_URL not set"
    exit 1
fi

if [ -z "$OPENAI_API_KEY" ]; then
    echo "❌ OPENAI_API_KEY not set"
    exit 1
fi

if [ -z "$JWT_SECRET" ]; then
    echo "❌ JWT_SECRET not set"
    exit 1
fi

# Verify database connection
echo "📊 Verifying database connection..."
python -c "from app.db import engine; from sqlmodel import Session; Session(engine).execute('SELECT 1')" || {
    echo "❌ Database connection failed"
    exit 1
}

echo "✅ Database connection verified"

# Verify MCP server connectivity
echo "🤖 Verifying MCP server connectivity..."
curl -f -s "$MCP_SERVER_URL/health" > /dev/null || {
    echo "⚠️  MCP server not reachable (will retry on first request)"
}

echo "✅ MCP server check complete"

# Run database migrations
echo "🔄 Running database migrations..."
alembic upgrade head || {
    echo "⚠️  Migration warning (continuing anyway)"
}

# Start backend server
echo "🚀 Starting FastAPI backend on port 8000..."
exec uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
