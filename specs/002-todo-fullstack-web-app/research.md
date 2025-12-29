# Research: Todo Full-Stack Web Application (Phase II)

**Feature Branch**: `002-todo-fullstack-web-app`
**Date**: 2025-12-25
**Status**: Complete

---

## Overview

This document consolidates research findings for Phase II implementation decisions. All items marked "NEEDS CLARIFICATION" in the technical context have been resolved.

---

## 1. Authentication Architecture

### Decision: Better Auth with JWT (7-day expiry)

**Rationale**:
- Better Auth is mandated by Constitution (Section VI - Authentication Layer)
- JWT provides stateless authentication suitable for API-first architecture
- 7-day expiry specified in feature spec (FR-006)

**Alternatives Considered**:
| Alternative | Rejected Because |
|-------------|------------------|
| Session-based auth | Not stateless; violates Constitution Principle 1 |
| OAuth2 only | Adds complexity for email/password use case |
| Shorter token expiry (1 hour) | User requirement specifies 7 days |

**Implementation Pattern**:
- Frontend: Better Auth client handles token storage and refresh
- Backend: JWT middleware validates token on every request
- Shared secret: `BETTER_AUTH_SECRET` environment variable

---

## 2. Database Design

### Decision: Neon Serverless PostgreSQL with SQLModel ORM

**Rationale**:
- Neon is mandated by Constitution (Section VI - Database Layer)
- SQLModel integrates naturally with FastAPI (Pydantic models + SQLAlchemy)
- Serverless model aligns with stateless service principle

**Alternatives Considered**:
| Alternative | Rejected Because |
|-------------|------------------|
| SQLAlchemy Core | Less type safety; manual Pydantic conversion |
| Prisma | Not Python-native; adds complexity |
| Raw SQL | Loses type safety and validation benefits |

**Implementation Pattern**:
- Connection pooling via `DATABASE_URL` environment variable
- Async database operations using SQLModel async support
- Indexes on `tasks.user_id` and `tasks.completed` for query performance

---

## 3. Frontend Framework

### Decision: Next.js 14+ with App Router

**Rationale**:
- Constitution mandates Next.js App Router (Section VI - Frontend Layer)
- App Router provides server components for improved performance
- TypeScript strict mode required by Constitution

**Alternatives Considered**:
| Alternative | Rejected Because |
|-------------|------------------|
| Pages Router | App Router is Constitution mandate |
| Vite + React | Not specified in Constitution stack |
| Remix | Not in approved technology list |

**Implementation Pattern**:
- App directory structure: `/app` for routes, `/components` for shared UI
- Server components for initial data fetching
- Client components for interactive elements (forms, toggles)
- API client in `/lib/api.ts` using fetch with JWT headers

---

## 4. Backend Framework

### Decision: FastAPI with Pydantic validation

**Rationale**:
- Constitution mandates FastAPI (Section VI - Backend Layer)
- Pydantic provides automatic request/response validation
- OpenAPI documentation generated automatically

**Alternatives Considered**:
| Alternative | Rejected Because |
|-------------|------------------|
| Flask | Less built-in validation; manual OpenAPI |
| Django REST | Heavier; not in Constitution stack |
| Litestar | Not in approved technology list |

**Implementation Pattern**:
- Route prefix: `/api/` for all endpoints
- JWT middleware for authentication
- HTTPException for error handling
- Pydantic models for request/response schemas

---

## 5. API Design

### Decision: RESTful API with user-scoped routes

**Rationale**:
- REST aligns with CRUD operations in spec
- User-scoped routes (`/api/{user_id}/tasks`) enforce ownership
- Simple, well-understood pattern for task management

**Alternatives Considered**:
| Alternative | Rejected Because |
|-------------|------------------|
| GraphQL | Overengineering for simple CRUD |
| RPC-style | Less conventional for web apps |
| Nested resources only | user_id in path aids debugging/logging |

**Implementation Pattern**:
- `GET /api/{user_id}/tasks` - List with filter/sort query params
- `POST /api/{user_id}/tasks` - Create task
- `GET /api/{user_id}/tasks/{task_id}` - Get single task
- `PUT /api/{user_id}/tasks/{task_id}` - Update task
- `DELETE /api/{user_id}/tasks/{task_id}` - Delete task
- `PATCH /api/{user_id}/tasks/{task_id}/complete` - Toggle completion

---

## 6. Folder Structure

### Decision: Phase-isolated structure under `/phase_2/`

**Rationale**:
- User requirement explicitly states Phase I folder must remain untouched
- Clear separation prevents accidental modifications
- Each phase is independently deployable

**Selected Structure**:
```
phase_2/
├── backend/
│   ├── app/
│   │   ├── main.py           # FastAPI application
│   │   ├── config.py         # Environment configuration
│   │   ├── models/           # SQLModel entities
│   │   ├── schemas/          # Pydantic request/response
│   │   ├── routers/          # API route handlers
│   │   ├── services/         # Business logic
│   │   └── middleware/       # JWT auth middleware
│   ├── tests/
│   ├── requirements.txt
│   └── Dockerfile
├── frontend/
│   ├── app/                  # Next.js App Router
│   │   ├── (auth)/           # Auth route group
│   │   ├── (dashboard)/      # Protected routes
│   │   └── layout.tsx
│   ├── components/           # React components
│   ├── lib/                  # Utilities and API client
│   ├── package.json
│   └── Dockerfile
├── specs/                    # Feature specifications
├── docker-compose.yml
├── .env.example
└── CLAUDE.md
```

---

## 7. Error Handling Strategy

### Decision: Structured error responses with HTTPException

**Rationale**:
- FastAPI HTTPException provides consistent error format
- Frontend can parse structured error responses
- Aligns with REST conventions

**Error Response Format**:
```json
{
  "detail": "Human-readable error message",
  "code": "ERROR_CODE",
  "field": "optional_field_name"
}
```

**Error Codes**:
| Code | HTTP Status | Description |
|------|-------------|-------------|
| `UNAUTHORIZED` | 401 | Missing or invalid token |
| `FORBIDDEN` | 403 | Task ownership violation |
| `NOT_FOUND` | 404 | Task/User not found |
| `VALIDATION_ERROR` | 422 | Request validation failed |
| `INTERNAL_ERROR` | 500 | Unexpected server error |

---

## 8. Performance Considerations

### Decision: Pagination for large task lists

**Rationale**:
- Spec edge case mentions >1000 tasks scenario
- Pagination prevents memory issues and slow responses
- Keeps response sizes manageable

**Implementation Pattern**:
- Default page size: 50 tasks
- Maximum page size: 100 tasks
- Query params: `?page=1&per_page=50`
- Response includes: `total_count`, `page`, `per_page`, `total_pages`

---

## 9. Testing Strategy

### Decision: pytest for backend, React Testing Library for frontend

**Rationale**:
- pytest is standard for FastAPI testing
- RTL is standard for Next.js/React testing
- Constitution specifies testing requirements

**Test Categories**:
| Category | Tool | Focus |
|----------|------|-------|
| Unit (Backend) | pytest | Services, validators |
| Integration (Backend) | pytest + httpx | API endpoints |
| Unit (Frontend) | Vitest + RTL | Components |
| E2E (Optional) | Playwright | Full user flows |

---

## 10. Security Measures

### Decision: Defense-in-depth approach

**Rationale**:
- Multi-layer security reduces risk surface
- Aligns with spec requirements (FR-008, FR-017)

**Security Layers**:
| Layer | Measure |
|-------|---------|
| Transport | HTTPS only (enforced by deployment) |
| Authentication | JWT with secure signing |
| Authorization | User ownership check on every operation |
| Input Validation | Pydantic schemas with length limits |
| Output Sanitization | No raw user input in responses |

---

## Summary of Resolved Items

| Item | Resolution |
|------|------------|
| Auth method | Better Auth + JWT (Constitution mandate) |
| Database | Neon PostgreSQL + SQLModel (Constitution mandate) |
| Frontend | Next.js 14+ App Router + TypeScript (Constitution mandate) |
| Backend | FastAPI + Pydantic (Constitution mandate) |
| API style | RESTful with user-scoped routes |
| Error handling | HTTPException with structured responses |
| Performance | Pagination (50 items default) |
| Testing | pytest + RTL |
| Security | JWT + ownership enforcement |

All "NEEDS CLARIFICATION" items have been resolved. Ready for Phase 1: Design & Contracts.
