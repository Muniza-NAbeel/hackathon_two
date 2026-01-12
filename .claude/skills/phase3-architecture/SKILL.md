---
name: phase3-architecture
description: Explain Phase 3 Todo app architecture, UI decisions, and AI integration clearly for exams or interviews. Trigger when user asks about project architecture, tech stack, design decisions, interview preparation, or how the app works.
allowed-tools:
  - Read
  - Glob
  - Grep
---

# Phase 3 Architecture Skill

Complete guide to explain the Todo AI Chatbot application architecture for exams, interviews, and presentations.

---

## 🎯 Project Overview (Elevator Pitch)

> "TaskFlow AI is a full-stack task management application with an AI-powered chatbot. Users can manage tasks through both a traditional UI and natural language conversations. The app supports voice input in multiple languages (English & Urdu), real-time task operations via MCP (Model Context Protocol), and secure JWT authentication."

**Key Differentiators:**
- AI chatbot with natural language understanding
- Voice input support (English + Urdu)
- MCP-based tool orchestration
- Real-time task synchronization
- Professional dark theme UI

---

## 🏗️ High-Level Architecture

```
┌────────────────────────────────────────────────────────────────┐
│                        CLIENT LAYER                             │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │                   Next.js 14 (Frontend)                   │  │
│  │  ┌─────────────┐ ┌─────────────┐ ┌─────────────────────┐ │  │
│  │  │ Auth Pages  │ │  Dashboard  │ │   Chat Interface    │ │  │
│  │  │ Login/Sign  │ │  Task CRUD  │ │  AI + Voice Input   │ │  │
│  │  └─────────────┘ └─────────────┘ └─────────────────────┘ │  │
│  └──────────────────────────────────────────────────────────┘  │
└────────────────────────────────────────────────────────────────┘
                              │
                              │ HTTPS (REST API)
                              ▼
┌────────────────────────────────────────────────────────────────┐
│                        SERVER LAYER                             │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │                   FastAPI (Backend)                       │  │
│  │  ┌─────────────┐ ┌─────────────┐ ┌─────────────────────┐ │  │
│  │  │ Auth Router │ │ Task Router │ │    Chat Router      │ │  │
│  │  │ JWT Tokens  │ │ CRUD APIs   │ │   AI Processing     │ │  │
│  │  └─────────────┘ └─────────────┘ └──────────┬──────────┘ │  │
│  └─────────────────────────────────────────────┼────────────┘  │
│                                                │               │
│  ┌─────────────────────────────────────────────▼────────────┐  │
│  │                    AI LAYER                               │  │
│  │  ┌─────────────────┐  ┌────────────────────────────────┐ │  │
│  │  │  Agent Runner   │  │        MCP Server              │ │  │
│  │  │  (Gemini AI)    │──│  add_task, list_tasks, etc.    │ │  │
│  │  └─────────────────┘  └────────────────────────────────┘ │  │
│  └──────────────────────────────────────────────────────────┘  │
└────────────────────────────────────────────────────────────────┘
                              │
                              │ SQL (Async)
                              ▼
┌────────────────────────────────────────────────────────────────┐
│                       DATABASE LAYER                            │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │              Neon PostgreSQL (Serverless)                 │  │
│  │  ┌─────────────┐ ┌─────────────┐ ┌─────────────────────┐ │  │
│  │  │    Users    │ │    Tasks    │ │   Conversations     │ │  │
│  │  └─────────────┘ └─────────────┘ └─────────────────────┘ │  │
│  └──────────────────────────────────────────────────────────┘  │
└────────────────────────────────────────────────────────────────┘
```

---

## 🛠️ Tech Stack Explanation

### Frontend

| Technology | Why We Chose It |
|------------|-----------------|
| **Next.js 14** | Server components, App Router, built-in optimization |
| **TypeScript** | Type safety, better IDE support, fewer runtime errors |
| **Tailwind CSS** | Utility-first, fast development, easy dark theme |
| **Framer Motion** | Smooth animations, professional feel |
| **Lucide Icons** | Consistent icon library, tree-shakeable |

### Backend

| Technology | Why We Chose It |
|------------|-----------------|
| **FastAPI** | Async support, auto-documentation, type hints |
| **SQLModel** | Combines SQLAlchemy + Pydantic, less boilerplate |
| **Alembic** | Database migrations, version control for schema |
| **JWT (PyJWT)** | Stateless authentication, scalable |
| **Uvicorn** | ASGI server, async performance |

### AI Layer

| Technology | Why We Chose It |
|------------|-----------------|
| **Google Gemini** | Powerful LLM, good multilingual support |
| **OpenAI SDK** | Compatibility layer for Gemini API |
| **MCP Protocol** | Standardized tool calling, clean architecture |

### Database

| Technology | Why We Chose It |
|------------|-----------------|
| **Neon PostgreSQL** | Serverless, auto-scaling, free tier |
| **AsyncPG** | Async database driver, better performance |

---

## 📁 Project Structure

```
phase_3/
├── frontend/                    # Next.js application
│   ├── app/                     # App Router pages
│   │   ├── (auth)/              # Auth group (login, signup)
│   │   ├── (dashboard)/         # Protected pages
│   │   └── layout.tsx           # Root layout
│   ├── components/              # Reusable components
│   │   ├── ui/                  # Generic UI (Button, Input)
│   │   ├── tasks/               # Task-specific components
│   │   ├── chat/                # Chat components
│   │   └── auth/                # Auth components
│   ├── lib/                     # Utilities
│   │   ├── api/                 # API clients
│   │   ├── auth.ts              # Auth helpers
│   │   └── utils/               # Storage, helpers
│   └── types/                   # TypeScript types
│
└── backend/                     # FastAPI application
    ├── app/
    │   ├── main.py              # FastAPI app entry
    │   ├── config.py            # Settings (env vars)
    │   ├── database.py          # DB connection
    │   ├── models/              # SQLModel models
    │   ├── schemas/             # Pydantic schemas
    │   ├── routers/             # API endpoints
    │   └── services/            # Business logic
    │       ├── agent_runner.py  # AI agent
    │       └── mcp_server.py    # MCP tools
    ├── alembic/                 # Migrations
    └── tests/                   # Test files
```

---

## 🔐 Authentication Flow

```
┌──────────┐     ┌──────────┐     ┌──────────┐     ┌──────────┐
│  User    │────▶│ Frontend │────▶│ Backend  │────▶│ Database │
└──────────┘     └──────────┘     └──────────┘     └──────────┘

1. SIGNUP:
   User ──▶ POST /auth/register ──▶ Hash password ──▶ Save to DB
        ◀── Return JWT token + user data ◀──

2. LOGIN:
   User ──▶ POST /auth/login ──▶ Verify password ──▶ Check DB
        ◀── Return JWT token + user data ◀──

3. PROTECTED REQUEST:
   User ──▶ Request + Authorization: Bearer <token>
        ──▶ Verify JWT ──▶ Extract user_id ──▶ Process request
        ◀── Return data ◀──
```

### JWT Token Structure

```python
{
    "sub": "user_id_uuid",        # Subject (user ID)
    "exp": 1704931200,            # Expiration timestamp
    "iat": 1704844800             # Issued at timestamp
}
```

### Frontend Token Storage

```typescript
// lib/auth.ts
localStorage.setItem('todo_auth_token', token)
localStorage.setItem('todo_user', JSON.stringify(user))
```

---

## 💬 AI Chatbot Flow

```
┌─────────────────────────────────────────────────────────────────┐
│                    User Message Flow                             │
└─────────────────────────────────────────────────────────────────┘

User: "Add buy groceries for tomorrow"
              │
              ▼
┌─────────────────────────────────────────────────────────────────┐
│ 1. INTENT DETECTION (agent_runner.py)                           │
│    - Scan keywords: "add" → add_task intent                     │
│    - Extract: title="buy groceries", due="tomorrow"             │
└─────────────────────────────────────────────────────────────────┘
              │
              ▼
┌─────────────────────────────────────────────────────────────────┐
│ 2. MCP TOOL CALL                                                │
│    Tool: add_task                                               │
│    Args: {user_id, title, description, priority, due_date}      │
└─────────────────────────────────────────────────────────────────┘
              │
              ▼
┌─────────────────────────────────────────────────────────────────┐
│ 3. DATABASE OPERATION                                           │
│    INSERT INTO tasks (user_id, title, ...) VALUES (...)         │
└─────────────────────────────────────────────────────────────────┘
              │
              ▼
┌─────────────────────────────────────────────────────────────────┐
│ 4. RESPONSE GENERATION                                          │
│    "Done 👍 I've added 'buy groceries' for tomorrow."           │
└─────────────────────────────────────────────────────────────────┘
              │
              ▼
┌─────────────────────────────────────────────────────────────────┐
│ 5. UI UPDATE                                                    │
│    - Show response in chat                                      │
│    - Dispatch 'taskModified' event                              │
│    - Task list refreshes automatically                          │
└─────────────────────────────────────────────────────────────────┘
```

---

## 🎨 UI Design Decisions

### Why Dark Theme?

1. **Eye Comfort** - Reduces strain for long usage
2. **Modern Look** - Professional, tech-forward appearance
3. **Battery Saving** - Better for OLED screens
4. **Contrast** - Neon colors pop on dark background

### Color Palette

```css
/* Neon Accent Colors */
--neon-cyan: #00f5d4;     /* Primary actions */
--neon-purple: #9b5de5;   /* Secondary/AI */
--neon-blue: #00bbf9;     /* Links/Info */

/* Background Colors */
--dark-bg: #0a0a0f;       /* Main background */
--dark-card: #12121a;     /* Card surfaces */
--dark-border: #1e1e2e;   /* Borders */
```

### Component Design Patterns

```tsx
// Glass morphism effect
className="bg-dark-card/40 backdrop-blur-xl"

// Neon glow on hover
className="hover:shadow-lg hover:shadow-neon-cyan/30"

// Smooth transitions
className="transition-all duration-300"

// Lift effect
className="hover:-translate-y-1"
```

---

## 📊 Database Schema

### Users Table

```sql
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email VARCHAR(255) UNIQUE NOT NULL,
    name VARCHAR(255),
    hashed_password VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);
```

### Tasks Table

```sql
CREATE TABLE tasks (
    id SERIAL PRIMARY KEY,
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    title VARCHAR(255) NOT NULL,
    description TEXT,
    status VARCHAR(20) DEFAULT 'pending',    -- pending, in_progress, completed
    priority VARCHAR(20) DEFAULT 'medium',   -- low, medium, high, urgent
    completed BOOLEAN DEFAULT FALSE,
    due_date TIMESTAMP,
    tags JSONB,                              -- ["Work", "Personal"]
    recurrence VARCHAR(20) DEFAULT 'none',   -- none, daily, weekly, monthly
    notes JSONB,                             -- [{text, timestamp}]
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);
```

### Conversations Table

```sql
CREATE TABLE conversations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE messages (
    id SERIAL PRIMARY KEY,
    conversation_id UUID REFERENCES conversations(id) ON DELETE CASCADE,
    role VARCHAR(20) NOT NULL,               -- user, assistant
    content TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT NOW()
);
```

---

## 🔌 API Endpoints Summary

### Authentication

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/auth/register` | Create new user |
| POST | `/auth/login` | Login, get JWT |
| GET | `/auth/me` | Get current user |

### Tasks

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/tasks` | List tasks (with filters) |
| POST | `/api/tasks` | Create task |
| GET | `/api/tasks/{id}` | Get single task |
| PUT | `/api/tasks/{id}` | Update task |
| DELETE | `/api/tasks/{id}` | Delete task |
| PATCH | `/api/tasks/{id}/toggle` | Toggle completion |

### Chat

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/chat` | Send message to AI |
| GET | `/api/chat/{conv_id}/history` | Get conversation history |

---

## ❓ Common Interview Questions

### Q1: "Why did you choose FastAPI over Django/Flask?"

> "FastAPI offers native async support which is crucial for AI operations that can have latency. It also provides automatic OpenAPI documentation, type validation with Pydantic, and better performance. For a real-time chat application with AI integration, async capabilities were essential."

### Q2: "How does the chatbot understand user intent?"

> "The chatbot uses a keyword-based intent detection system combined with Google Gemini AI. First, we scan for keywords like 'add', 'show', 'complete' to determine the action. Then we extract entities like task title, priority, and dates. For complex queries, Gemini AI handles natural language understanding. This hybrid approach is fast for common operations and flexible for edge cases."

### Q3: "What is MCP and why did you use it?"

> "MCP (Model Context Protocol) is a standardized way to connect AI models with external tools. Instead of the AI directly calling database functions, it calls MCP tools like 'add_task' or 'list_tasks'. This creates a clean separation between AI logic and business logic, makes testing easier, and allows tools to be reused across different AI models."

### Q4: "How do you handle authentication securely?"

> "We use JWT (JSON Web Tokens) for stateless authentication. Passwords are hashed with bcrypt before storage. Tokens expire after 7 days and are stored in localStorage on the frontend. All API routes are protected with a dependency that verifies the JWT and extracts the user ID. We never store plain passwords or expose sensitive data in tokens."

### Q5: "How does the app handle multiple languages?"

> "The chatbot supports English and Urdu (including Roman Urdu). Intent detection includes keywords in both languages - for example, 'add' and 'mujhy karna hai' both map to task creation. The AI's system prompt instructs it to respond in the same language the user speaks. Voice input uses Web Speech API with configurable language settings."

### Q6: "Explain the data flow when a user adds a task via chat."

> "1) User types 'Add buy milk' in ChatInterface
> 2) Frontend sends POST to /api/chat with message
> 3) Backend's AgentRunner detects 'add' intent
> 4) Agent calls MCP tool 'add_task' with extracted title
> 5) MCP tool inserts into PostgreSQL database
> 6) Agent generates friendly confirmation
> 7) Response returns to frontend
> 8) Frontend shows message and dispatches 'taskModified' event
> 9) Task list component refreshes to show new task"

### Q7: "How would you scale this application?"

> "The architecture is already designed for scaling:
> - Frontend: Vercel handles auto-scaling for Next.js
> - Backend: FastAPI is async, can run multiple workers with Uvicorn
> - Database: Neon PostgreSQL is serverless and auto-scales
> - AI: Gemini API handles scaling automatically
> - For higher scale: Add Redis for caching, use connection pooling, implement rate limiting"

---

## 🎓 Key Concepts to Remember

1. **Stateless Authentication** - JWT tokens contain all needed info
2. **Async/Await** - Non-blocking I/O for better performance
3. **MCP Pattern** - Clean separation of AI and business logic
4. **Intent Detection** - Hybrid keyword + AI approach
5. **Real-time Sync** - Event-driven UI updates
6. **Dark Theme** - CSS variables + Tailwind classes
7. **Type Safety** - TypeScript frontend + Pydantic backend
