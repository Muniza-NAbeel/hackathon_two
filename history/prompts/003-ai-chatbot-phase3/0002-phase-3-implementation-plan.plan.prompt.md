---
id: 0002
title: Phase 3 Implementation Plan
stage: plan
date: 2025-12-30
surface: agent
model: claude-sonnet-4-5-20250929
feature: 003-ai-chatbot-phase3
branch: 001-ai-chatbot-phase3
user: munizanabeel
command: /sp.plan
labels: ["phase3", "implementation-plan", "architecture", "mcp", "openai-agents", "stateless"]
links:
  spec: specs/003-ai-chatbot-phase3/spec.md
  ticket: null
  adr: null
  pr: null
files:
  - specs/003-ai-chatbot-phase3/plan.md
tests:
  - Constitution compliance check (all principles passed)
---

## Prompt

You are planning Phase_3 of a full-stack Todo application based strictly on the finalized Phase_3 specification.

REFERENCE:
- Phase_3 specification is finalized via /sp.specify
- Follow the specification exactly
- Do NOT introduce new features, agents, tools, or architecture
- Do NOT modify or reference Phase_2

PLANNING OBJECTIVE:
Create a clear, step-by-step implementation plan for Phase_3 that:
- Preserves a fully stateless architecture
- Keeps Phase_3 fully isolated inside phase_3/
- Uses MCP, OpenAI Agents SDK, and ChatKit correctly
- Is safe to execute incrementally
- Can be distributed across multiple agents

[Full user prompt with folder structure, testing requirements, deployment setup, and documentation requirements included]

## Response snapshot

Created comprehensive implementation plan for Phase 3 AI-powered chatbot with complete architectural design:

**Plan Structure**:
- Summary: Natural language task management via stateless AI chatbot
- Technical Context: Python 3.11+, FastAPI, SQLModel, MCP SDK, OpenAI Agents SDK, ChatKit, Neon PostgreSQL
- Constitution Check: All 13 applicable principles PASSED (event-driven deferred to Phase 5)
- Project Structure: Detailed `phase_3/` directory tree with backend, mcp, frontend, agents, skills, docs

**Phase 0 - Research** (10 research tasks):
- R-001: OpenAI Agents SDK + FastAPI integration
- R-002: MCP SDK server setup and tool registration
- R-003: ChatKit deployment and domain allowlist
- R-004: Conversation history pagination strategies
- R-005: JWT verification with Better Auth
- R-006: SQLModel relationship patterns
- R-007: OpenAI API error handling
- R-008: MCP tool input validation
- R-009: Agent Skills definition patterns
- R-010: Testing stateless chat endpoints
Output: research.md with consolidated findings

**Phase 1 - Design & Contracts**:
- Data Model: 3 entities (Task [shared], Conversation, Message) with full ERD, validation rules, state transitions, indexes
- API Contracts: chat-api.openapi.yaml (POST /api/chat with request/response schemas)
- MCP Tools Contract: mcp-tools.json (5 tools: add_task, list_tasks, complete_task, update_task, delete_task)
- Database Schema: database-schema.sql (DDL for conversations, messages tables + triggers)
- Quickstart Guide: Developer onboarding documentation
Output: data-model.md, contracts/, quickstart.md

**Key Architectural Decisions**:
- MCP server runs as separate process with isolated database access
- Backend loads full conversation history from PostgreSQL per request
- AI agent cannot access database (MCP tools only)
- Phase 3 shares database but adds new tables (Conversation, Message)
- Frontend isolated in phase_3/frontend/ (no Phase 2 modifications)

**Deployment Plan**:
- Environment variables: DATABASE_URL, OPENAI_API_KEY, NEXT_PUBLIC_OPENAI_DOMAIN_KEY
- ChatKit deployment checklist (domain allowlist, domain key generation)
- MCP server process management (systemd/Docker)
- Alembic migrations for new tables

**Compliance**:
- Stateless architecture enforced (no in-memory state)
- Agent Skills identified (conversation loading, JWT verification, MCP invocation, error formatting)
- Technology stack adheres to Constitution (no deviations)

## Outcome

- ✅ Impact: Production-ready implementation plan defining complete Phase 3 architecture with stateless design
- 🧪 Tests: Constitution Check validated (13/13 applicable principles passed)
- 📁 Files: 1 file created (plan.md with 10 research tasks, 3 data models, 5 API contracts)
- 🔁 Next prompts: Execute Phase 0 research tasks → Phase 1 design artifacts → /sp.tasks for task breakdown
- 🧠 Reflection: Plan successfully translates specification requirements into concrete technical design. Research phase identifies 10 critical unknowns requiring authoritative documentation review before implementation. Design phase provides complete contracts (OpenAPI, MCP schemas, SQL DDL) for type-safe development.

## Evaluation notes (flywheel)

- Failure modes observed: None - plan adheres to Constitution and specification constraints
- Graders run and results (PASS/FAIL): Constitution Check - PASS (13/13 applicable, event-driven correctly deferred)
- Prompt variant (if applicable): Standard /sp.plan workflow with Constitution compliance gates
- Next experiment (smallest change to try): Execute research phase to validate technology integration patterns before committing to design decisions
