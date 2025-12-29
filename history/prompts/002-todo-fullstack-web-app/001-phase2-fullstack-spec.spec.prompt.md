---
id: 001
title: Phase II Todo Fullstack Spec Creation
stage: spec
date: 2025-12-25
surface: agent
model: claude-opus-4-5-20251101
feature: 002-todo-fullstack-web-app
branch: 002-todo-fullstack-web-app
user: munizanabeel
command: /sp.specify
labels: ["phase-2", "fullstack", "specification", "todo-app", "web-application"]
links:
  spec: specs/002-todo-fullstack-web-app/spec.md
  ticket: null
  adr: null
  pr: null
files:
  - specs/002-todo-fullstack-web-app/spec.md
  - specs/002-todo-fullstack-web-app/checklists/requirements.md
tests:
  - null
---

## Prompt

# Phase II: Todo Full-Stack Web Application Specification

## Objective
Transform the existing console-based Todo app (Phase I) into a **multi-user full-stack web application** with persistent storage, JWT-based authentication, and a responsive UI.

## Features
1. Task CRUD Operations:
   - Create, view, update, delete tasks
   - Mark tasks complete/incomplete
   - Each task linked to logged-in user
   - Title: required, 1–200 chars
   - Description: optional, max 1000 chars
   - Filtering: pending, completed, all
   - Sorting: title, created date, due date

2. User Authentication:
   - Signup, login, logout
   - JWT-based auth
   - Frontend includes JWT in Authorization header
   - Backend verifies JWT on every request
   - Each API request requires valid JWT

3. API Endpoints:
   - GET /api/{user_id}/tasks → List tasks
   - POST /api/{user_id}/tasks → Create task
   - GET /api/{user_id}/tasks/{id} → Get task details
   - PUT /api/{user_id}/tasks/{id} → Update task
   - DELETE /api/{user_id}/tasks/{id} → Delete task
   - PATCH /api/{user_id}/tasks/{id}/complete → Toggle completion
   - All responses filtered by authenticated user
   - Generate **Pydantic models**, validation rules, and error handling for each endpoint

## Database
- Users table (managed by Better Auth):
  - id (PK), email, name, created_at
- Tasks table:
  - id (PK), user_id (FK), title, description, completed, created_at, updated_at
- Indexes: tasks.user_id, tasks.completed
- Database: Neon Serverless PostgreSQL
- ORM: SQLModel

## Frontend
- Framework: Next.js 16+ (App Router)
- Language: TypeScript
- Styling: Tailwind CSS
- Pages: /app for pages/layouts
- Components: /components for reusable components
- API Client: `/lib/api.ts` to call backend with JWT token
- Include validation and error handling in forms
- Responsive design for desktop & mobile

## Backend
- Framework: FastAPI
- ORM: SQLModel
- JWT middleware to verify token and extract user_id
- Database connection string via env: DATABASE_URL
- Routes under `/api/` returning JSON
- Pydantic models for request/response
- Error handling via HTTPException
- Task ownership enforced on every operation

## Security
- JWT token verification for all endpoints
- Shared secret: BETTER_AUTH_SECRET in frontend & backend
- Token expiry: 7 days
- Requests without token return 401 Unauthorized

## Folder Structure
hackathon_two/phase_2/
├── .spec-kit/          # Spec-Kit config for Phase II
├── specs/
│   ├── features/       # Each feature (CRUD, auth, filtering) as separate spec
│   ├── api/            # API endpoints specs
│   ├── db/             # Database schema & migration specs
│   └── ui/             # UI components/pages specs
├── CLAUDE.md           # Root Claude instructions
├── frontend/           # Next.js 16+ app
│   └── CLAUDE.md       # Frontend-specific instructions
├── backend/            # FastAPI app
│   └── CLAUDE.md       # Backend-specific instructions
└── docker-compose.yml  # Phase II docker setup

## Workflow
- Use the agents and sub-agents already created
- Apply their skills to implement features, APIs, and frontend/backend logic
- Follow **baby-step approach**:
  1. Authentication
  2. Task CRUD
  3. Filtering & Sorting
  4. Frontend UI Pages & Components
  5. Integration & API calls with JWT
  6. Testing & Validation

## Testing
- Generate pytest skeletons for all backend endpoints
- Generate React Testing Library skeletons for frontend components
- Include validation and edge-case tests for tasks

## Instruction for Claude Code
- Generate organized feature specs, API specs, database schema, and UI specs in **respective folders**
- Include **validation rules, error handling, JWT handling, and ownership enforcement**
- Output should be structured, actionable, and ready for Spec-Kit Plus
- Follow **baby-step approach** for each feature

## Response snapshot

Created comprehensive specification for Phase II Todo Full-Stack Web Application:

**Branch**: `002-todo-fullstack-web-app`
**Spec File**: `specs/002-todo-fullstack-web-app/spec.md`

The specification includes:
- 8 prioritized user stories (P1: Auth, Create, View; P2: Toggle, Edit, Delete; P3: Filter, Sort)
- 25 functional requirements across authentication, task management, filtering/sorting, and UI
- 10 measurable success criteria (technology-agnostic)
- 6 edge cases with defined behaviors
- Key entities (User, Task) with attributes
- Dependencies, assumptions, and risk mitigations

Quality checklist created and all 16 validation items passed.

## Outcome

- Impact: Created complete Phase II specification defining multi-user fullstack todo application
- Tests: N/A (specification phase - no tests created)
- Files: 2 files created (spec.md, checklists/requirements.md)
- Next prompts: `/sp.clarify` to refine or `/sp.plan` to begin architecture planning
- Reflection: Comprehensive spec created without clarification markers - user requirements were detailed enough to make informed defaults

## Evaluation notes (flywheel)

- Failure modes observed: None - spec created successfully on first pass
- Graders run and results (PASS/FAIL): Quality checklist - 16/16 PASS
- Prompt variant (if applicable): Standard /sp.specify workflow
- Next experiment (smallest change to try): Proceed to /sp.plan for architecture design
