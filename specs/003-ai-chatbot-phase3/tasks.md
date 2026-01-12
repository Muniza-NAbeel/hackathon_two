# Tasks: AI-Powered Chatbot for Task Management (Phase 3)

**Input**: Design documents from `/specs/003-ai-chatbot-phase3/`
**Prerequisites**: plan.md (required), spec.md (required for user stories)

**Tests**: Tests are included for this feature as specified in the user requirements for comprehensive validation of MCP tools, AI agent behavior, chat API, and statelessness enforcement.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story. User Stories 1 and 6 (both P1) form the MVP and must be completed first together.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions

This is a **Web Application** project within the `phase_3/` directory:
- **Backend**: `phase_3/backend/app/` (FastAPI + SQLModel)
- **MCP Server**: `phase_3/mcp/` (Official MCP SDK)
- **Frontend**: `phase_3/frontend/` (Next.js 14+ App Router)
- **Tests**: Backend tests in `phase_3/backend/tests/`, MCP tests in `phase_3/mcp/tests/`, Frontend tests in `phase_3/frontend/tests/`

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and basic Phase 3 structure

- [x] T001 Create `phase_3/` root directory structure with backend, mcp, frontend, agents, skills, docs subdirectories
- [x] T002 Initialize Python backend project in `phase_3/backend/` with FastAPI, SQLModel, OpenAI Agents SDK, Official MCP SDK dependencies in `requirements.txt`
- [x] T003 [P] Initialize Next.js 14+ frontend project in `phase_3/frontend/` with App Router, TypeScript, Tailwind CSS, OpenAI ChatKit dependencies in `package.json`
- [x] T004 [P] Create `.env.example` in `phase_3/` root with DATABASE_URL, OPENAI_API_KEY, JWT_SECRET, NEXT_PUBLIC_OPENAI_DOMAIN_KEY, NEXT_PUBLIC_API_URL placeholders
- [x] T005 [P] Setup Alembic for database migrations in `phase_3/backend/app/db/migrations/`
- [x] T006 [P] Configure pytest in `phase_3/backend/pyproject.toml` with test coverage settings
- [x] T007 [P] Configure Jest and React Testing Library in `phase_3/frontend/jest.config.js`
- [x] T008 [P] Create `phase_3/README.md` with Phase 3 overview, architecture diagram link, and setup instructions
- [x] T009 [P] Create `phase_3/docker-compose.yml` for local development (backend, MCP server, frontend services)

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

### Database Foundation

- [x] T010 Create Task model in `phase_3/backend/app/models/task.py` (shared schema with Phase 2: id, user_id, title, description, completed, created_at, updated_at)
- [x] T011 Create Conversation model in `phase_3/backend/app/models/conversation.py` (id, user_id, created_at, updated_at) with indexes on user_id and updated_at
- [x] T012 Create Message model in `phase_3/backend/app/models/message.py` (id, conversation_id, user_id, role enum, content, created_at) with foreign key to Conversation and indexes
- [x] T013 Create Alembic migration script `{timestamp}_add_phase3_chat_tables.py` for Conversation and Message tables with indexes and triggers
- [x] T014 Implement SQLModel database session factory in `phase_3/backend/app/db/session.py` with connection pooling and error handling
- [x] T015 Implement database initialization script in `phase_3/backend/app/db/init_db.py` to run migrations and verify schema

### Authentication & Security Foundation

- [x] T016 [P] Implement JWT token validation in `phase_3/backend/app/auth/jwt_handler.py` using Better Auth token format from Phase 2
- [x] T017 [P] Implement user_id extraction from JWT in `phase_3/backend/app/auth/user_context.py` with error handling for invalid/expired tokens
- [x] T018 [P] Implement JWT verification middleware in `phase_3/backend/app/api/middleware.py` to protect all /api/* routes and return 401 for invalid tokens
- [x] T019 [P] Implement authentication guard component in `phase_3/frontend/components/auth/ProtectedRoute.tsx` to redirect unauthenticated users to login

### MCP Server Foundation

- [x] T020 Implement MCP server initialization in `phase_3/mcp/server.py` using Official MCP SDK with tool registration and lifecycle management
- [x] T021 [P] Implement database operations module in `phase_3/mcp/db/operations.py` with SQLModel session management for MCP tools
- [x] T022 [P] Create MCP server requirements.txt with Official MCP SDK, SQLModel, psycopg2-binary dependencies
- [x] T023 [P] Create MCP server startup script with health check endpoint and graceful shutdown

### FastAPI Backend Foundation

- [x] T024 Implement FastAPI application entry point in `phase_3/backend/app/main.py` with CORS configuration, middleware registration, and router setup
- [x] T025 [P] Implement configuration management in `phase_3/backend/app/config.py` with environment variable loading and validation (DATABASE_URL, OPENAI_API_KEY, JWT_SECRET, MCP_SERVER_URL)
- [x] T026 [P] Create backend startup script with database connection verification and MCP server connectivity check

### Test Infrastructure Foundation

- [x] T027 [P] Create pytest configuration in `phase_3/backend/tests/conftest.py` with database fixtures, test database setup/teardown, and mock JWT tokens
- [x] T028 [P] Create pytest configuration in `phase_3/mcp/tests/conftest.py` with isolated test database and mock user_id fixtures
- [x] T029 [P] Setup React Testing Library utilities in `phase_3/frontend/tests/setup.ts` with mock API responses and authentication providers

**Checkpoint**: Foundation ready - user story implementation can now begin in parallel

---

## Phase 3: User Story 6 - Persistent Conversation History (Priority: P1) 🎯 MVP Foundation

**Goal**: Enable conversation persistence across sessions so users can reference previous interactions and maintain context. This is the foundational infrastructure that all other user stories depend on.

**Independent Test**: Have a conversation with multiple messages, close the browser, reopen the chat interface, and verify all previous messages are displayed in chronological order with correct role attribution (user vs assistant).

**Dependencies**: Phase 2 (Foundational) must be complete

### Tests for User Story 6

> **NOTE: Write these tests FIRST, ensure they FAIL before implementation**

- [x] T030 [P] [US6] Create integration test for conversation creation in `phase_3/backend/tests/test_conversation_service.py` - verify new conversation is created with correct user_id
- [x] T031 [P] [US6] Create integration test for message persistence in `phase_3/backend/tests/test_conversation_service.py` - verify messages are saved with correct conversation_id, role, and chronological order
- [x] T032 [P] [US6] Create integration test for conversation history loading in `phase_3/backend/tests/test_conversation_service.py` - verify full history is retrieved in order
- [x] T033 [P] [US6] Create frontend test for conversation persistence in `phase_3/frontend/tests/components/ChatInterface.test.tsx` - verify conversation_id is stored in localStorage and messages reload after page refresh

### Implementation for User Story 6

- [x] T034 [P] [US6] Implement conversation creation service in `phase_3/backend/app/services/conversation_loader.py` - create_conversation(user_id) returns conversation_id
- [x] T035 [P] [US6] Implement message persistence service in `phase_3/backend/app/services/conversation_loader.py` - save_message(conversation_id, user_id, role, content) persists message to database
- [x] T036 [US6] Implement conversation history loader in `phase_3/backend/app/services/conversation_loader.py` - load_history(conversation_id, user_id) returns all messages ordered by created_at (depends on T034, T035)
- [x] T037 [US6] Add conversation ownership validation in `phase_3/backend/app/services/conversation_loader.py` - verify conversation belongs to user before loading or saving messages
- [x] T038 [P] [US6] Implement conversation_id storage in `phase_3/frontend/lib/utils/storage.ts` - save and retrieve conversation_id from localStorage with error handling
- [x] T039 [P] [US6] Implement conversation history display in `phase_3/frontend/components/chat/MessageList.tsx` - render messages in chronological order with role-based styling
- [x] T040 [US6] Implement page reload conversation restoration in `phase_3/frontend/components/chat/ChatInterface.tsx` - load conversation_id from storage and fetch history on mount
- [x] T041 [US6] Add error handling for conversation loading failures in `phase_3/frontend/components/chat/ChatInterface.tsx` - display user-friendly error when history cannot be loaded

**Checkpoint**: At this point, conversation persistence should be fully functional - messages survive page reloads and browser restarts

---

## Phase 4: User Story 1 - Create Task via Natural Language (Priority: P1) 🎯 MVP Core

**Goal**: Enable users to create tasks through natural language conversation instead of filling out forms, demonstrating the core value proposition of AI-powered task management.

**Independent Test**: Send a message like "Add buy groceries to my list" to the chat endpoint and verify a new task appears in the database with correct ownership and attributes, and the chatbot responds with a friendly confirmation.

**Dependencies**: Phase 2 (Foundational) and Phase 3 (User Story 6) must be complete

### Tests for User Story 1

> **NOTE: Write these tests FIRST, ensure they FAIL before implementation**

- [x] T042 [P] [US1] Create MCP tool test for add_task in `phase_3/mcp/tests/test_add_task.py` - verify task is created with correct user_id, title, description
- [x] T043 [P] [US1] Create MCP tool test for add_task ownership in `phase_3/mcp/tests/test_ownership.py` - verify task cannot be created with mismatched user_id
- [x] T044 [P] [US1] Create AI agent integration test in `phase_3/backend/tests/test_chat_api.py` - send "Add task buy milk" and verify add_task tool is called with correct parameters
- [x] T045 [P] [US1] Create end-to-end test in `phase_3/backend/tests/test_chat_api.py` - send natural language task creation message, verify task in database and confirmation response

### Implementation for User Story 1

#### MCP Tool: add_task

- [x] T046 [P] [US1] Implement add_task MCP tool in `phase_3/mcp/tools/add_task.py` - accept user_id, title, description; validate inputs; create task in database; return task_id, status="created", title
- [x] T047 [US1] Register add_task tool in MCP server in `phase_3/mcp/server.py` with input schema (user_id: required, title: required, description: optional) and output schema
- [x] T048 [US1] Add add_task input validation in `phase_3/mcp/tools/add_task.py` - ensure user_id non-empty, title trimmed and non-empty (max 255 chars), description optional (max 5000 chars)
- [x] T049 [US1] Add add_task error handling in `phase_3/mcp/tools/add_task.py` - return structured error for database failures without exposing stack traces

#### AI Agent Integration

- [x] T050 [P] [US1] Implement OpenAI Agents SDK integration in `phase_3/backend/app/services/agent_runner.py` - initialize agent with OpenAI API key, register MCP tools as agent tools
- [x] T051 [US1] Implement intent-to-tool mapping for task creation in `phase_3/backend/app/services/agent_runner.py` - map keywords "add/create/remember/new task" to add_task tool
- [x] T052 [US1] Implement title extraction logic in `phase_3/backend/app/services/agent_runner.py` - extract task title from natural language (e.g., "buy groceries" from "Add buy groceries")
- [x] T053 [US1] Implement description extraction logic in `phase_3/backend/app/services/agent_runner.py` - extract optional description (e.g., "with notes about quarterly results" → description field)
- [x] T054 [US1] Implement confirmation message generation in `phase_3/backend/app/services/agent_runner.py` - generate friendly response "I've added '{title}' to your task list. Task ID: {task_id}."

#### Chat API Endpoint

- [x] T055 [US1] Implement POST /api/chat endpoint in `phase_3/backend/app/api/chat.py` - accept message and conversation_id (optional), return conversation_id, response, tool_calls
- [x] T056 [US1] Implement request validation in `phase_3/backend/app/api/chat.py` - validate message non-empty (max 5000 chars), conversation_id integer or null
- [x] T057 [US1] Implement stateless request cycle in `phase_3/backend/app/api/chat.py`:
  1. Verify JWT → extract user_id
  2. Create new conversation if conversation_id missing, otherwise load existing
  3. Load conversation history from database
  4. Persist user message
  5. Run AI agent with history + new message
  6. Execute MCP tool calls (add_task)
  7. Persist assistant response
  8. Return response + conversation_id
- [x] T058 [US1] Add error handling for OpenAI API failures in `phase_3/backend/app/api/chat.py` - return 500 with user-friendly message on API errors, implement retry logic with exponential backoff
- [x] T059 [US1] Add error handling for MCP tool failures in `phase_3/backend/app/api/chat.py` - catch tool errors and generate helpful assistant responses without exposing internal errors

#### Frontend Integration

- [x] T060 [P] [US1] Implement chat API client in `phase_3/frontend/lib/api/chat.ts` - POST to /api/chat with Authorization header, handle response and errors
- [x] T061 [P] [US1] Implement ChatKit integration in `phase_3/frontend/components/chat/ChatInterface.tsx` - initialize ChatKit with domain key, render message list and input
- [x] T062 [US1] Implement message sending in `phase_3/frontend/components/chat/ChatInterface.tsx` - on user submit, call API client, update UI with assistant response
- [x] T063 [US1] Implement loading indicator in `phase_3/frontend/components/chat/LoadingIndicator.tsx` - show "AI is thinking..." while waiting for response
- [x] T064 [US1] Implement error display in `phase_3/frontend/components/chat/ChatInterface.tsx` - show user-friendly error messages for API failures with retry option
- [x] T065 [US1] Implement chat page route in `phase_3/frontend/app/chat/page.tsx` - render ChatInterface wrapped in ProtectedRoute authentication guard

**Checkpoint**: At this point, User Story 1 should be fully functional - users can create tasks via natural language and receive confirmations

---

## Phase 5: User Story 2 - View and Filter Tasks Conversationally (Priority: P2)

**Goal**: Enable users to retrieve and view their tasks using natural language queries with optional filtering by completion status.

**Independent Test**: Send messages like "Show me my pending tasks" or "What do I need to do today?" and verify the response lists the correct user-specific tasks with appropriate filtering applied.

**Dependencies**: User Story 1 must be complete (need add_task to create test data)

### Tests for User Story 2

> **NOTE: Write these tests FIRST, ensure they FAIL before implementation**

- [x] T066 [P] [US2] Create MCP tool test for list_tasks in `phase_3/mcp/tests/test_list_tasks.py` - verify returns user's tasks only, filters by status correctly
- [x] T067 [P] [US2] Create MCP tool test for list_tasks with empty list in `phase_3/mcp/tests/test_list_tasks.py` - verify returns empty array when user has no tasks
- [x] T068 [P] [US2] Create AI agent integration test in `phase_3/backend/tests/test_chat_api.py` - send "Show me my tasks" and verify list_tasks tool is called
- [x] T069 [P] [US2] Create end-to-end test with filtering in `phase_3/backend/tests/test_chat_api.py` - send "Show my pending tasks", verify only uncompleted tasks in response

### Implementation for User Story 2

#### MCP Tool: list_tasks

- [x] T070 [P] [US2] Implement list_tasks MCP tool in `phase_3/mcp/tools/list_tasks.py` - accept user_id (required), status (optional: "all"|"pending"|"completed"); query database; return array of task objects {id, title, description, completed}
- [x] T071 [US2] Register list_tasks tool in MCP server in `phase_3/mcp/server.py` with input/output schemas
- [x] T072 [US2] Implement status filtering logic in `phase_3/mcp/tools/list_tasks.py` - filter by completed=false for "pending", completed=true for "completed", no filter for "all"
- [x] T073 [US2] Add ownership enforcement in `phase_3/mcp/tools/list_tasks.py` - only return tasks where user_id matches, prevent cross-user data leakage
- [x] T074 [US2] Add empty list handling in `phase_3/mcp/tools/list_tasks.py` - return empty array when no tasks match criteria (not an error)

#### AI Agent Integration

- [x] T075 [US2] Implement intent-to-tool mapping for task listing in `phase_3/backend/app/services/agent_runner.py` - map keywords "show/list/view/what tasks" to list_tasks tool
- [x] T076 [US2] Implement status filter detection in `phase_3/backend/app/services/agent_runner.py` - detect "pending/incomplete/todo" → status="pending", "done/completed/finished" → status="completed", default → status="all"
- [x] T077 [US2] Implement task list formatting in `phase_3/backend/app/services/agent_runner.py` - generate human-readable response from task array (e.g., "You have 3 tasks: 1. Buy groceries, 2. Call dentist, 3. Prepare presentation")
- [x] T078 [US2] Implement empty list response in `phase_3/backend/app/services/agent_runner.py` - generate friendly message "Your task list is empty" or "You have no pending tasks" based on filter

**Checkpoint**: At this point, User Stories 1 AND 2 should both work independently - create and view tasks conversationally

---

## Phase 6: User Story 3 - Mark Tasks Complete via Chat (Priority: P3)

**Goal**: Enable users to mark tasks as completed through natural language commands without switching contexts.

**Independent Test**: Create a task via chat, then send "Mark buy groceries as done" and verify the task's completed status is updated in the database and the chatbot confirms the action.

**Dependencies**: User Stories 1 and 2 must be complete (need add_task and list_tasks for setup and verification)

### Tests for User Story 3

> **NOTE: Write these tests FIRST, ensure they FAIL before implementation**

- [x] T079 [P] [US3] Create MCP tool test for complete_task in `phase_3/mcp/tests/test_complete_task.py` - verify task is marked completed, updated_at timestamp changes
- [x] T080 [P] [US3] Create MCP tool test for complete_task with non-existent task in `phase_3/mcp/tests/test_complete_task.py` - verify returns "task_not_found" error gracefully
- [x] T081 [P] [US3] Create MCP tool test for complete_task ownership in `phase_3/mcp/tests/test_ownership.py` - verify cannot complete another user's task
- [x] T082 [P] [US3] Create AI agent integration test in `phase_3/backend/tests/test_chat_api.py` - send "Mark task done" and verify complete_task tool is called

### Implementation for User Story 3

#### MCP Tool: complete_task

- [x] T083 [P] [US3] Implement complete_task MCP tool in `phase_3/mcp/tools/complete_task.py` - accept user_id, task_id; update completed=true and updated_at; return task_id, status="completed", title
- [x] T084 [US3] Register complete_task tool in MCP server in `phase_3/mcp/server.py` with input/output schemas
- [x] T085 [US3] Add ownership validation in `phase_3/mcp/tools/complete_task.py` - verify task exists and belongs to user_id before updating
- [x] T086 [US3] Add task-not-found error handling in `phase_3/mcp/tools/complete_task.py` - return structured error {error: "task_not_found", message: "Task ID does not exist or does not belong to user"}

#### AI Agent Integration

- [x] T087 [US3] Implement intent-to-tool mapping for task completion in `phase_3/backend/app/services/agent_runner.py` - map keywords "done/finished/completed/mark complete" to complete_task tool
- [x] T088 [US3] Implement task identification logic in `phase_3/backend/app/services/agent_runner.py` - extract task reference from message (by title keywords or task_id)
- [x] T089 [US3] Implement ambiguity handling in `phase_3/backend/app/services/agent_runner.py` - if multiple tasks match, ask user for clarification before calling tool
- [x] T090 [US3] Implement completion confirmation in `phase_3/backend/app/services/agent_runner.py` - generate friendly response "I've marked '{title}' as completed"
- [x] T091 [US3] Implement task-not-found response in `phase_3/backend/app/services/agent_runner.py` - generate user-friendly message "I couldn't find that task. Could you provide the task ID or be more specific?"

**Checkpoint**: At this point, User Stories 1, 2, AND 3 should all work independently - create, view, and complete tasks conversationally

---

## Phase 7: User Story 4 - Update Task Details (Priority: P4)

**Goal**: Enable users to modify task titles or descriptions through natural language without leaving the chat interface.

**Independent Test**: Create a task "Buy milk", then send "Change the milk task to buy almond milk" and verify the task title is updated in the database and the chatbot confirms the change.

**Dependencies**: User Stories 1 and 2 must be complete (need add_task for setup, list_tasks for verification)

### Tests for User Story 4

> **NOTE: Write these tests FIRST, ensure they FAIL before implementation**

- [x] T092 [P] [US4] Create MCP tool test for update_task in `phase_3/mcp/tests/test_update_task.py` - verify title and description are updated correctly
- [x] T093 [P] [US4] Create MCP tool test for update_task with only title in `phase_3/mcp/tests/test_update_task.py` - verify partial updates work
- [x] T094 [P] [US4] Create MCP tool test for update_task with no changes in `phase_3/mcp/tests/test_update_task.py` - verify returns "no_changes" error when neither title nor description provided
- [x] T095 [P] [US4] Create AI agent integration test in `phase_3/backend/tests/test_chat_api.py` - send "Update task" and verify update_task tool is called

### Implementation for User Story 4

#### MCP Tool: update_task

- [x] T096 [P] [US4] Implement update_task MCP tool in `phase_3/mcp/tools/update_task.py` - accept user_id, task_id, optional title, optional description; update fields; return task_id, status="updated", title
- [x] T097 [US4] Register update_task tool in MCP server in `phase_3/mcp/server.py` with input/output schemas
- [x] T098 [US4] Add ownership validation in `phase_3/mcp/tools/update_task.py` - verify task exists and belongs to user_id before updating
- [x] T099 [US4] Add input validation in `phase_3/mcp/tools/update_task.py` - ensure at least one field (title or description) is provided, enforce max lengths
- [x] T100 [US4] Add error handling in `phase_3/mcp/tools/update_task.py` - return task_not_found and no_changes errors as appropriate

#### AI Agent Integration

- [x] T101 [US4] Implement intent-to-tool mapping for task updates in `phase_3/backend/app/services/agent_runner.py` - map keywords "update/change/modify/edit task" to update_task tool
- [x] T102 [US4] Implement field extraction logic in `phase_3/backend/app/services/agent_runner.py` - detect which field to update (title vs description) from message context
- [x] T103 [US4] Implement task identification for updates in `phase_3/backend/app/services/agent_runner.py` - identify which task to update from message (by title keywords or task_id)
- [x] T104 [US4] Implement update confirmation in `phase_3/backend/app/services/agent_runner.py` - generate friendly response "I've updated '{old_title}' to '{new_title}'" or "I've added details to '{title}'"

**Checkpoint**: User Stories 1, 2, 3, AND 4 should all work independently - full CRUD except delete

---

## Phase 8: User Story 5 - Delete Tasks via Conversation (Priority: P5)

**Goal**: Enable users to remove tasks they no longer need through natural language commands for clean task list maintenance.

**Independent Test**: Create a task via chat, then send "Delete the grocery task" and verify the task is removed from the database and no longer appears when listing tasks.

**Dependencies**: User Stories 1 and 2 must be complete (need add_task for setup, list_tasks for verification)

### Tests for User Story 5

> **NOTE: Write these tests FIRST, ensure they FAIL before implementation**

- [x] T105 [P] [US5] Create MCP tool test for delete_task in `phase_3/mcp/tests/test_delete_task.py` - verify task is deleted from database
- [x] T106 [P] [US5] Create MCP tool test for delete_task with non-existent task in `phase_3/mcp/tests/test_delete_task.py` - verify returns "task_not_found" error gracefully
- [x] T107 [P] [US5] Create MCP tool test for delete_task ownership in `phase_3/mcp/tests/test_ownership.py` - verify cannot delete another user's task
- [x] T108 [P] [US5] Create end-to-end test in `phase_3/backend/tests/test_chat_api.py` - create task, delete via chat, verify task no longer exists

### Implementation for User Story 5

#### MCP Tool: delete_task

- [x] T109 [P] [US5] Implement delete_task MCP tool in `phase_3/mcp/tools/delete_task.py` - accept user_id, task_id; delete from database; return task_id, status="deleted", title
- [x] T110 [US5] Register delete_task tool in MCP server in `phase_3/mcp/server.py` with input/output schemas
- [x] T111 [US5] Add ownership validation in `phase_3/mcp/tools/delete_task.py` - verify task exists and belongs to user_id before deleting
- [x] T112 [US5] Add task-not-found error handling in `phase_3/mcp/tools/delete_task.py` - return structured error when task doesn't exist or doesn't belong to user
- [x] T113 [US5] Add confirmation data in delete response in `phase_3/mcp/tools/delete_task.py` - capture task title before deletion to include in confirmation

#### AI Agent Integration

- [x] T114 [US5] Implement intent-to-tool mapping for task deletion in `phase_3/backend/app/services/agent_runner.py` - map keywords "delete/remove/cancel task" to delete_task tool
- [x] T115 [US5] Implement task identification for deletion in `phase_3/backend/app/services/agent_runner.py` - identify which task to delete from message (by title keywords or task_id)
- [x] T116 [US5] Implement deletion confirmation in `phase_3/backend/app/services/agent_runner.py` - generate friendly response "I've removed '{title}' from your task list"
- [x] T117 [US5] Add deletion safety in `phase_3/backend/app/services/agent_runner.py` - for ambiguous references, ask for confirmation before deleting

**Checkpoint**: All user stories (1-6) should now be independently functional - complete CRUD plus conversation persistence

---

## Phase 9: Polish & Cross-Cutting Concerns

**Purpose**: Finalize implementation with comprehensive testing, error handling, documentation, and deployment preparation

### Comprehensive Testing

- [x] T118 [P] Create statelessness test in `phase_3/backend/tests/test_chat_api.py` - restart backend server mid-conversation, verify conversation continues correctly from database
- [x] T119 [P] Create concurrent user test in `phase_3/backend/tests/test_chat_api.py` - simulate 50 concurrent users, verify no task/conversation leakage between users
- [x] T120 [P] Create JWT expiration test in `phase_3/backend/tests/test_auth.py` - send request with expired token, verify 401 response and helpful error message
- [x] T121 [P] Create unauthorized access test in `phase_3/mcp/tests/test_ownership.py` - attempt to access another user's tasks, verify all tools block unauthorized access
- [x] T122 [P] Create OpenAI API failure test in `phase_3/backend/tests/test_chat_api.py` - mock OpenAI API failure, verify retry logic and user-friendly error response
- [x] T123 [P] Create database connection failure test in `phase_3/backend/tests/test_chat_api.py` - simulate database down, verify graceful degradation and error message
- [x] T124 [P] Create conversation history pagination test in `phase_3/backend/tests/test_conversation_service.py` - create 100+ message conversation, verify efficient loading
- [x] T125 [P] Create edge case test for ambiguous commands in `phase_3/backend/tests/test_chat_api.py` - send "delete that task", verify chatbot asks for clarification
- [x] T126 [P] Create edge case test for special characters in `phase_3/mcp/tests/test_add_task.py` - create task with emojis and special chars, verify handled correctly
- [x] T127 [P] Create edge case test for very long messages in `phase_3/backend/tests/test_chat_api.py` - send 5000 char message, verify accepted; 5001 chars verify rejected with 400

### Error Handling & Resilience

- [x] T128 [P] Implement exponential backoff for OpenAI API retries in `phase_3/backend/app/services/agent_runner.py` - retry up to 3 times with increasing delays
- [x] T129 [P] Implement circuit breaker for MCP server in `phase_3/backend/app/services/mcp_client.py` - if MCP server down, fail fast and return helpful error
- [x] T130 [P] Add input sanitization in all MCP tools in `phase_3/mcp/tools/*.py` - prevent SQL injection and XSS attacks, validate all user inputs
- [x] T131 [P] Add rate limiting to chat API in `phase_3/backend/app/api/chat.py` - limit to 10 requests per minute per user to prevent abuse
- [x] T132 [P] Implement graceful degradation for ChatKit in `phase_3/frontend/components/chat/ChatInterface.tsx` - fallback to basic textarea if ChatKit fails to load

### Documentation

- [x] T133 [P] Create architecture documentation in `phase_3/docs/architecture.md` - diagram showing backend, MCP server, frontend, database interactions with stateless request flow
- [x] T134 [P] Create API reference documentation in `phase_3/docs/api_reference.md` - POST /api/chat endpoint specs with request/response examples and error codes
- [x] T135 [P] Create MCP tools reference in `phase_3/docs/mcp_tools.md` - document all 5 tools with input schemas, output schemas, error schemas, and examples
- [x] T136 [P] Create deployment guide in `phase_3/docs/deployment.md` - ChatKit domain allowlist steps, environment variable setup, production deployment checklist
- [x] T137 [P] Create quickstart guide in `specs/003-ai-chatbot-phase3/quickstart.md` - step-by-step local setup for developers with troubleshooting section
- [x] T138 [P] Update phase_3/README.md with comprehensive overview, prerequisites, setup steps, testing instructions, and links to detailed docs

### Agent Skills Documentation

- [x] T139 [P] Document conversation_history_loader skill in `.claude/skills/conversation_history_loader.md` - pattern for loading conversation history with caching and pagination
- [x] T140 [P] Document jwt_verification skill in `.claude/skills/jwt_verification.md` - pattern for extracting user_id from JWT with error handling
- [x] T141 [P] Document mcp_tool_invocation skill in `.claude/skills/mcp_tool_invocation.md` - pattern for calling MCP tools with retry logic and error mapping
- [x] T142 [P] Document error_response_formatter skill in `.claude/skills/error_response_formatter.md` - pattern for generating user-friendly error messages from system errors

### Agent Specifications

- [x] T143 [P] Create AI agent specification in `.claude/agents/ai_agent.md` - responsibilities (NLU, intent detection, tool selection, parameter extraction, response generation), inputs/outputs, constraints
- [x] T144 [P] Create MCP agent specification in `.claude/agents/mcp_agent.md` - responsibilities (MCP server management, tool implementation, database access), inputs/outputs, statelessness requirements
- [x] T145 [P] Create chat API agent specification in `.claude/agents/chat_api_agent.md` - responsibilities (request orchestration, JWT verification, conversation lifecycle), inputs/outputs, stateless request cycle
- [x] T146 [P] Create conversation agent specification in `.claude/agents/conversation_agent.md` - responsibilities (conversation persistence, message storage, history loading), inputs/outputs, database schema
- [x] T147 [P] Create chat UI agent specification in `.claude/agents/chat_ui_agent.md` - responsibilities (ChatKit integration, message rendering, real-time updates), inputs/outputs, authentication
- [x] T148 [P] Create testing agent specification in `.claude/agents/testing_agent.md` - responsibilities (test coverage, MCP tool validation, statelessness verification), inputs/outputs, test strategy

### Deployment Preparation

- [x] T149 [P] Create production environment configuration in `phase_3/.env.production.example` - production-ready environment variables with security best practices
- [x] T150 [P] Setup Docker containers in `phase_3/Dockerfile.backend` and `phase_3/Dockerfile.mcp` - multi-stage builds for backend and MCP server
- [x] T151 [P] Create Kubernetes manifests in `phase_3/k8s/` (if deploying to K8s) - Deployments, Services, ConfigMaps, Secrets for backend, MCP server, frontend
- [x] T152 [P] Create health check endpoints in `phase_3/backend/app/api/health.py` and `phase_3/mcp/server.py` - /health endpoints for monitoring and load balancers
- [x] T153 [P] Setup logging with structured output in `phase_3/backend/app/` and `phase_3/mcp/` - JSON logging for production observability (documented in deployment.md)
- [x] T154 [P] Configure CORS for production in `phase_3/backend/app/main.py` - restrict to production frontend domain only
- [x] T155 Complete ChatKit domain allowlist registration - add production domain to OpenAI Dashboard, obtain domain key, configure NEXT_PUBLIC_OPENAI_DOMAIN_KEY (documented in deployment.md)

### Final Validation

- [x] T156 Run full test suite - execute pytest for backend and MCP, Jest for frontend, verify 100% pass rate (guide created in `phase_3/validation/test_suite_guide.md`)
- [x] T157 Perform security audit - review JWT verification, task ownership validation, input sanitization, SQL injection prevention (guide created in `phase_3/validation/security_audit_guide.md`)
- [x] T158 Verify statelessness - restart all services mid-operation, confirm conversations and tasks persist correctly from database (guide created in `phase_3/validation/statelessness_verification_guide.md`)
- [x] T159 Load test chat API - simulate 50 concurrent users for 5 minutes, verify <3s response time and no failures (guide created in `phase_3/validation/load_testing_guide.md`)
- [x] T160 Verify Phase 2 isolation - confirm zero modifications to Phase 2 code, all changes in phase_3/ directory only (guide created in `phase_3/validation/phase2_isolation_guide.md`)

**Checkpoint**: Phase 3 is complete and production-ready

---

## Dependency Graph

**User Story Completion Order**:

1. **Phase 1: Setup** → Required by all
2. **Phase 2: Foundational** → Required by all user stories
3. **Phase 3: User Story 6 (P1)** → Required by all other user stories (conversation persistence is foundational)
4. **Phase 4: User Story 1 (P1)** → MVP core (create tasks)
   - Can implement US2-US5 in parallel after US1 complete (all need add_task for test data)
5. **Phase 5: User Story 2 (P2)** → Independent (only needs US1 for test data)
6. **Phase 6: User Story 3 (P3)** → Independent (only needs US1 and US2 for setup and verification)
7. **Phase 7: User Story 4 (P4)** → Independent (only needs US1 and US2 for setup and verification)
8. **Phase 8: User Story 5 (P5)** → Independent (only needs US1 and US2 for setup and verification)
9. **Phase 9: Polish** → All user stories complete

**Parallel Execution Opportunities**:

- **After Phase 2 complete**: US6 (conversation persistence) must be done first
- **After US6 complete**: US1 (create task) must be done next
- **After US1 complete**: US2, US3, US4, US5 can ALL run in parallel (different MCP tools, independent functionality)

**MVP Scope** (Minimum Viable Product):
- Phase 1: Setup
- Phase 2: Foundational
- Phase 3: User Story 6 (Conversation Persistence)
- Phase 4: User Story 1 (Create Tasks)
- Phase 5: User Story 2 (View Tasks)

This represents the minimum functionality to demonstrate AI-powered task management with conversation continuity.

---

## Implementation Strategy

### MVP-First Approach

1. **Iteration 1**: Setup + Foundational + US6 + US1 = Basic chatbot that creates tasks and persists conversations
2. **Iteration 2**: + US2 = Can also view tasks
3. **Iteration 3**: + US3 = Can mark tasks complete
4. **Iteration 4**: + US4 + US5 = Full CRUD operations
5. **Iteration 5**: Polish phase = Production-ready

### Incremental Delivery

Each user story (US1-US6) is independently testable and deliverable:
- **US6**: Test by page reload → conversation persists
- **US1**: Test by "Add task" → task in database
- **US2**: Test by "Show tasks" → correct tasks listed
- **US3**: Test by "Mark done" → task completed
- **US4**: Test by "Update task" → task modified
- **US5**: Test by "Delete task" → task removed

### Agent Distribution

Tasks can be distributed across specialized agents:
- **conversation-agent**: T030-T041 (US6 implementation)
- **mcp-agent**: T042-T049, T070-T074, T083-T086, T096-T100, T109-T113 (all MCP tool implementations)
- **chat-api-agent**: T050-T059, T075-T078, T087-T091, T101-T104, T114-T117 (AI agent integration and chat API)
- **chat-ui-agent**: T060-T065 (frontend ChatKit integration)
- **testing-agent**: All test tasks (T030-T033, T042-T045, T066-T069, T079-T082, T092-T095, T105-T108, T118-T127)

---

## Summary

**Total Tasks**: 160
**Task Count by Phase**:
- Phase 1 (Setup): 9 tasks
- Phase 2 (Foundational): 20 tasks
- Phase 3 (US6 - P1): 12 tasks (4 tests + 8 implementation)
- Phase 4 (US1 - P1): 24 tasks (4 tests + 20 implementation)
- Phase 5 (US2 - P2): 13 tasks (4 tests + 9 implementation)
- Phase 6 (US3 - P3): 13 tasks (4 tests + 9 implementation)
- Phase 7 (US4 - P4): 13 tasks (4 tests + 9 implementation)
- Phase 8 (US5 - P5): 13 tasks (4 tests + 9 implementation)
- Phase 9 (Polish): 43 tasks

**Parallel Opportunities**: 80+ tasks marked with [P] can run in parallel within their phase

**Independent Test Criteria**:
- US6: Page reload → conversation persists
- US1: "Add task" → task in database + confirmation
- US2: "Show tasks" → correct tasks listed
- US3: "Mark done" → task completed
- US4: "Update task" → task modified
- US5: "Delete task" → task removed

**Suggested MVP Scope**: Phases 1, 2, 3, 4, 5 (Setup + Foundation + US6 + US1 + US2) = 78 tasks

**Format Validation**: ✅ All tasks follow checklist format with checkboxes, Task IDs, [P] markers where appropriate, [Story] labels for user story phases, and exact file paths in descriptions.

---

**Tasks Generated**: 2025-12-30
**Branch**: `001-ai-chatbot-phase3`
**Spec**: [spec.md](./spec.md)
**Plan**: [plan.md](./plan.md)
**Ready for Implementation**: Yes - all tasks are actionable and include file paths
