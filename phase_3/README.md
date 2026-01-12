# Phase 3: AI-Powered Chatbot for Task Management

AI-powered chatbot that enables users to manage their tasks through natural language conversation using **OpenAI ChatKit**, Google Gemini AI, and Model Context Protocol (MCP).

## Architecture Overview

```
┌─────────────┐      ┌──────────────┐      ┌─────────────┐      ┌──────────────┐
│  Next.js    │─────▶│   FastAPI    │─────▶│ MCP Server  │─────▶│  PostgreSQL  │
│  ChatKit UI │      │  Chat API    │      │ Task Tools  │      │   Database   │
└─────────────┘      └──────────────┘      └─────────────┘      └──────────────┘
                            │
                            ▼
                     ┌──────────────┐
                     │ Google       │
                     │ Gemini AI    │
                     └──────────────┘
```

**Key Principles**:
- ✅ **Stateless Architecture**: No in-memory session state
- ✅ **MCP-Only Data Access**: AI agent cannot access database directly
- ✅ **Conversation Persistence**: All chat history stored in PostgreSQL
- ✅ **Phase Isolation**: Zero modifications to Phase 2 code

## Technology Stack

| Component | Technology |
|-----------|------------|
| **Frontend** | Next.js 14+ with **OpenAI ChatKit React** |
| **Backend** | Python FastAPI |
| **AI Engine** | Google Gemini AI (via OpenAI SDK compatibility) |
| **MCP Server** | Official MCP SDK (Python) |
| **ORM** | SQLModel |
| **Database** | Neon Serverless PostgreSQL |
| **Authentication** | JWT (Better Auth compatible) |

**Key Features:**
- ✅ **OpenAI ChatKit**: Professional chat UI with streaming support
- ✅ **MCP Protocol**: Stateless task management tools
- ✅ **Gemini AI**: Free AI inference (OpenAI SDK compatible)
- ✅ **Full CRUD**: Create, read, update, delete, complete tasks via chat

## Quick Start

### Prerequisites

- Python 3.11+
- Node.js 18+
- PostgreSQL database (Neon Serverless)
- OpenAI API key

### 1. Environment Setup

```bash
# Copy environment template
cp .env.example .env

# Edit .env with your credentials:
# - DATABASE_URL
# - OPENAI_API_KEY
# - JWT_SECRET (shared with Phase 2)
# - NEXT_PUBLIC_OPENAI_DOMAIN_KEY
```

### 2. Backend Setup

```bash
cd phase_3/backend

# Using UV (recommended)
uv venv && source .venv/bin/activate
uv pip install -r requirements.txt

# Or using pip
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt

# Run database migrations
alembic upgrade head

# Start FastAPI server
uvicorn app.main:app --reload --port 8000
```

### 3. MCP Server Setup

```bash
cd phase_3/mcp

# Install dependencies
uv pip install -r requirements.txt
# or: pip install -r requirements.txt

# Start MCP server
python server.py
```

### 4. Frontend Setup

```bash
cd phase_3/frontend

# Install dependencies
npm install

# Start Next.js development server
npm run dev
```

### 5. Access the Application

- Frontend: http://localhost:3000/chat
- Backend API: http://localhost:8000/docs
- MCP Server: http://localhost:8001

## Project Structure

```
phase_3/
├── backend/          # FastAPI backend + AI agent
│   ├── app/
│   │   ├── api/      # Chat endpoint
│   │   ├── auth/     # JWT verification
│   │   ├── db/       # Database session + migrations
│   │   ├── models/   # Task, Conversation, Message models
│   │   └── services/ # AI agent runner, conversation loader
│   └── tests/        # Backend tests
│
├── mcp/              # MCP server (stateless task tools)
│   ├── tools/        # add_task, list_tasks, etc.
│   ├── db/           # Database operations for MCP tools
│   └── tests/        # MCP tool tests
│
├── frontend/         # Next.js + ChatKit UI
│   ├── app/          # App Router pages
│   ├── components/   # React components (ChatInterface, MessageList)
│   └── lib/          # API client, utilities
│
├── agents/           # Agent specifications
├── skills/           # Reusable Agent Skills
└── docs/             # Architecture + API reference
```

## User Stories (MVP Scope)

### ✅ P1: Conversation Persistence (US6)
Messages survive page reloads and browser restarts.

### ✅ P1: Create Tasks via Natural Language (US1)
"Add buy groceries to my list" → Task created with confirmation

### ✅ P2: View and Filter Tasks (US2)
"Show me my pending tasks" → Lists uncompleted tasks

### ✅ P3: Complete Tasks via Chat (US3)
"Mark task 5 as done" → Task marked complete with confirmation

### ✅ P4: Update Task Details (US4)
"Update task 3 to buy almond milk" → Task title/description updated

### ✅ P5: Delete Tasks via Conversation (US5)
"Delete the grocery task" → Task removed from database

**All CRUD operations complete! 🎉**

## 💬 Natural Language Examples

Try these commands in the chat interface:

**Create Tasks:**
- "Add task to buy groceries"
- "Create a task: call dentist tomorrow at 2pm"
- "Remember to prepare presentation with quarterly results"
- "New task: review PR #123"

**View Tasks:**
- "Show my tasks"
- "List pending tasks"
- "What tasks have I completed?"
- "Display all my tasks"

**Complete Tasks:**
- "Mark task 5 as done"
- "Complete the groceries task"
- "Finished with the presentation"
- "Done with task 3"

**Update Tasks:**
- "Update task 3 to buy almond milk"
- "Change the dentist task to 3pm"
- "Modify task 2 description to include quarterly data"

**Delete Tasks:**
- "Delete task 7"
- "Remove the groceries task"
- "Cancel the meeting task"

## Testing

### Backend Tests

```bash
cd phase_3/backend
pytest                    # Run all tests
pytest --cov             # With coverage
pytest tests/test_chat_api.py  # Specific test file
```

### MCP Server Tests

```bash
cd phase_3/mcp
pytest                    # Test all MCP tools
pytest tests/test_ownership.py  # Security tests
```

### Frontend Tests

```bash
cd phase_3/frontend
npm test                  # Run Jest tests
npm run test:coverage     # With coverage
```

## Deployment

### ChatKit Domain Setup

1. Deploy frontend to production domain (e.g., `https://chat.example.com`)
2. Go to OpenAI Dashboard → ChatKit → Domain Allowlist
3. Add your domain to the allowlist
4. Generate ChatKit domain key
5. Set `NEXT_PUBLIC_OPENAI_DOMAIN_KEY` in production environment
6. Restart frontend service

### Docker Deployment

```bash
# Build and run all services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

## Documentation

- [Architecture Overview](./docs/architecture.md)
- [API Reference](./docs/api_reference.md)
- [MCP Tools Documentation](./docs/mcp_tools.md)
- [Deployment Guide](./docs/deployment.md)

## Troubleshooting

### Database Connection Errors

- Verify `DATABASE_URL` in `.env`
- Ensure PostgreSQL is running
- Check database migrations: `alembic current`

### OpenAI API Errors

- Verify `OPENAI_API_KEY` is valid
- Check API usage limits
- Review error logs for rate limiting

### MCP Server Not Responding

- Ensure MCP server is running on port 8001
- Check `MCP_SERVER_URL` in backend `.env`
- Verify database connectivity from MCP server

### ChatKit Not Loading

- Verify `NEXT_PUBLIC_OPENAI_DOMAIN_KEY` is set
- Check domain is added to OpenAI allowlist
- Review browser console for CORS errors

## Development Workflow

1. **Make changes** to backend, MCP server, or frontend
2. **Write tests** for new functionality
3. **Run tests** to ensure nothing breaks
4. **Test locally** with all services running
5. **Commit changes** following SDD workflow
6. **Deploy** to staging/production

## Contributing

This project follows Spec-Driven Development (SDD):
- All features start with a specification
- Implementation follows tasks defined in `/specs/003-ai-chatbot-phase3/tasks.md`
- No manual code modifications - all code generated from specs

## License

MIT
