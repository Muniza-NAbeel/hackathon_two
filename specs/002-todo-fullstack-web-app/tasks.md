# Tasks: Todo Full-Stack Web Application (Phase II)

**Input**: Design documents from `/specs/002-todo-fullstack-web-app/`
**Prerequisites**: plan.md (complete), spec.md (complete), data-model.md (complete), contracts/ (complete)

**Tests**: Test tasks are included as Feature 006 (Testing & Validation) per user request.

**Organization**: Tasks are grouped by feature to enable structured implementation with clear agent assignments.

## Format: `[ID] [P?] [Feature] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Feature]**: Which feature this task belongs to (e.g., F001, F002)
- Include exact file paths in descriptions

## Path Conventions

- **Backend**: `phase_2/backend/` (FastAPI + SQLModel)
- **Frontend**: `phase_2/frontend/` (Next.js App Router)
- **Specs**: `specs/002-todo-fullstack-web-app/`

---

## Phase 1: Setup (Project Foundation)

**Purpose**: Initialize Phase II folder structure and project scaffolding
**Assigned Agent**: general-purpose

- [X] T001 Create phase_2/ directory structure per plan.md
- [X] T002 [P] Initialize backend with FastAPI in phase_2/backend/
- [X] T003 [P] Initialize frontend with Next.js 14+ App Router in phase_2/frontend/
- [X] T004 [P] Create phase_2/backend/requirements.txt with dependencies (fastapi, sqlmodel, uvicorn, python-jose, passlib, alembic, asyncpg, pydantic[email])
- [X] T005 [P] Create phase_2/frontend/package.json with dependencies (next, react, tailwindcss, typescript)
- [X] T006 [P] Create phase_2/backend/.env.example with DATABASE_URL, BETTER_AUTH_SECRET, HOST, PORT, DEBUG
- [X] T007 [P] Create phase_2/frontend/.env.example with NEXT_PUBLIC_API_URL, BETTER_AUTH_SECRET
- [X] T008 Create phase_2/docker-compose.yml for local development
- [X] T009 [P] Configure Tailwind CSS in phase_2/frontend/tailwind.config.ts
- [X] T010 [P] Create phase_2/frontend/tsconfig.json with strict mode
- [X] T011 Create phase_2/CLAUDE.md with Phase II instructions

**Checkpoint**: Project structure ready - foundational phase can begin

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY feature can be implemented

**⚠️ CRITICAL**: No feature work can begin until this phase is complete

### Database Layer

- [X] T012 Create phase_2/backend/app/__init__.py
- [X] T013 Create phase_2/backend/app/config.py with environment configuration (DATABASE_URL, BETTER_AUTH_SECRET, etc.)
- [X] T014 Create phase_2/backend/app/database.py with Neon PostgreSQL connection using SQLModel
- [X] T015 Initialize Alembic in phase_2/backend/alembic/
- [X] T016 Create initial migration for tasks table in phase_2/backend/alembic/versions/001_create_tasks_table.py
- [X] T017 Add database indexes per data-model.md (idx_tasks_user_id, idx_tasks_completed, etc.)

### Core Application Structure

- [X] T018 Create phase_2/backend/app/main.py with FastAPI application entry point and CORS middleware
- [X] T019 [P] Create phase_2/backend/app/models/__init__.py
- [X] T020 [P] Create phase_2/backend/app/schemas/__init__.py
- [X] T021 [P] Create phase_2/backend/app/routers/__init__.py
- [X] T022 [P] Create phase_2/backend/app/services/__init__.py
- [X] T023 [P] Create phase_2/backend/app/middleware/__init__.py

### Frontend Base Structure

- [X] T024 Create phase_2/frontend/app/layout.tsx with root layout and Tailwind CSS
- [X] T025 Create phase_2/frontend/app/page.tsx with home redirect logic
- [X] T026 [P] Create phase_2/frontend/lib/utils.ts with helper functions
- [X] T027 [P] Create phase_2/frontend/types/index.ts with TypeScript type definitions per contracts

**Checkpoint**: Foundation ready - feature implementation can now begin

---

## Phase 3: Feature 001 - Authentication (Priority: P1) 🎯

**Goal**: User registration, login, logout with JWT (7-day expiry)
**Assigned Agent**: general-purpose (auth implementation)

**Independent Test**: Create account → Login → Verify session persists → Logout → Verify redirect to login

### User Story 1: User Registration and Authentication (spec.md)

**Acceptance Criteria**:
- Register with email/password → account created, auto-logged in
- Login with valid credentials → authenticated, redirected to dashboard
- Session persists across page refresh (7-day token)
- Logout → session ends, redirected to login
- Unauthenticated access → redirected to login

### Backend Implementation (F001)

- [X] T028 [P] [F001] Create User Pydantic schemas in phase_2/backend/app/schemas/user.py (UserRegister, UserLogin, UserRead)
- [X] T029 [P] [F001] Create Auth response schemas in phase_2/backend/app/schemas/auth.py (AuthResponse, ErrorResponse)
- [X] T030 [F001] Create auth service in phase_2/backend/app/services/auth.py (register, login, logout, get_current_user)
- [X] T031 [F001] Implement JWT creation and validation with 7-day expiry in phase_2/backend/app/services/auth.py
- [X] T032 [F001] Create JWT middleware in phase_2/backend/app/middleware/auth.py (verify token, extract user)
- [X] T033 [F001] Create auth router in phase_2/backend/app/routers/auth.py with endpoints:
  - POST /api/auth/register
  - POST /api/auth/login
  - POST /api/auth/logout
  - GET /api/auth/me
- [X] T034 [F001] Register auth router in phase_2/backend/app/main.py
- [X] T035 [F001] Add password hashing with passlib in phase_2/backend/app/services/auth.py

### Frontend Implementation (F001)

- [X] T036 [P] [F001] Create auth utilities in phase_2/frontend/lib/auth.ts (token storage, get/set/clear)
- [X] T037 [P] [F001] Create API client with JWT headers in phase_2/frontend/lib/api.ts
- [X] T038 [P] [F001] Create Button component in phase_2/frontend/components/ui/Button.tsx
- [X] T039 [P] [F001] Create Input component in phase_2/frontend/components/ui/Input.tsx
- [X] T040 [P] [F001] Create LoadingSpinner component in phase_2/frontend/components/ui/LoadingSpinner.tsx
- [X] T041 [F001] Create LoginForm component in phase_2/frontend/components/auth/LoginForm.tsx
- [X] T042 [F001] Create SignupForm component in phase_2/frontend/components/auth/SignupForm.tsx
- [X] T043 [F001] Create login page in phase_2/frontend/app/(auth)/login/page.tsx
- [X] T044 [F001] Create signup page in phase_2/frontend/app/(auth)/signup/page.tsx
- [X] T045 [F001] Create protected layout in phase_2/frontend/app/(dashboard)/layout.tsx with auth check
- [X] T046 [F001] Add form validation feedback for email/password in LoginForm and SignupForm

**Checkpoint**: Authentication fully functional - users can register, login, logout

---

## Phase 4: Feature 002 - Task CRUD Operations (Priority: P1) 🎯

**Goal**: Create, read, update, delete tasks with ownership enforcement
**Assigned Agent**: todo-crud-orchestrator

**Independent Test**: Login → Create task → View task → Edit task → Delete task

### User Stories Covered:
- **US2**: Task Creation (P1)
- **US3**: Task List Viewing (P1)
- **US4**: Task Completion Toggle (P2)
- **US5**: Task Editing (P2)
- **US6**: Task Deletion (P2)

### Backend Implementation (F002)

- [X] T047 [F002] Create Task SQLModel entity in phase_2/backend/app/models/task.py per data-model.md
- [X] T048 [P] [F002] Create Task Pydantic schemas in phase_2/backend/app/schemas/task.py (TaskCreate, TaskUpdate, TaskRead, TaskListResponse)
- [X] T049 [F002] Create task service in phase_2/backend/app/services/task.py with:
  - create_task(user_id, task_data)
  - get_tasks(user_id, filters)
  - get_task(task_id, user_id) with ownership check
  - update_task(task_id, user_id, task_data)
  - delete_task(task_id, user_id)
  - toggle_complete(task_id, user_id)
- [X] T050 [F002] Implement ownership enforcement in phase_2/backend/app/services/task.py (403 if user_id mismatch)
- [X] T051 [F002] Create tasks router in phase_2/backend/app/routers/tasks.py with endpoints:
  - GET /api/{user_id}/tasks
  - POST /api/{user_id}/tasks
  - GET /api/{user_id}/tasks/{task_id}
  - PUT /api/{user_id}/tasks/{task_id}
  - DELETE /api/{user_id}/tasks/{task_id}
  - PATCH /api/{user_id}/tasks/{task_id}/complete
- [X] T052 [F002] Add validation (title 1-200 chars, description max 1000 chars) in phase_2/backend/app/schemas/task.py
- [X] T053 [F002] Register tasks router in phase_2/backend/app/main.py
- [X] T054 [F002] Add pagination support (default 50, max 100) in phase_2/backend/app/services/task.py

### Frontend Implementation (F002)

- [X] T055 [P] [F002] Create TaskItem component in phase_2/frontend/components/tasks/TaskItem.tsx
- [X] T056 [P] [F002] Create TaskList component in phase_2/frontend/components/tasks/TaskList.tsx
- [X] T057 [P] [F002] Create TaskForm component in phase_2/frontend/components/tasks/TaskForm.tsx (create/edit)
- [X] T058 [P] [F002] Create EmptyState component in phase_2/frontend/components/tasks/EmptyState.tsx
- [X] T059 [P] [F002] Create Modal component in phase_2/frontend/components/ui/Modal.tsx for edit/delete dialogs
- [X] T060 [F002] Create task dashboard page in phase_2/frontend/app/(dashboard)/tasks/page.tsx
- [X] T061 [F002] Implement task creation UI with form validation in TaskForm
- [X] T062 [F002] Implement task edit functionality with inline editing or modal
- [X] T063 [F002] Implement task deletion with confirmation dialog
- [X] T064 [F002] Implement task completion toggle with visual indicator
- [X] T065 [F002] Add loading indicators during API operations in TaskList

**Checkpoint**: Full CRUD operations working - users can manage their tasks

---

## Phase 5: Feature 003 - Filtering & Sorting (Priority: P3)

**Goal**: Filter tasks by status, sort by title/created_at/due_date
**Assigned Agent**: filter-sort-agent

**Independent Test**: Create tasks with different statuses → Apply filters → Verify correct tasks shown → Apply sort → Verify order

### User Stories Covered:
- **US7**: Task Filtering (P3)
- **US8**: Task Sorting (P3)

### Backend Implementation (F003)

- [X] T066 [F003] Add query parameter handling in phase_2/backend/app/routers/tasks.py:
  - status: all | pending | completed
  - sort_by: title | created_at | due_date
  - sort_order: asc | desc
- [X] T067 [F003] Implement filtering logic in phase_2/backend/app/services/task.py (get_tasks function)
- [X] T068 [F003] Implement sorting logic with null due_date handling in phase_2/backend/app/services/task.py
- [X] T069 [F003] Add TaskStatus, TaskSortBy, SortOrder enums in phase_2/backend/app/schemas/task.py

### Frontend Implementation (F003)

- [X] T070 [P] [F003] Create TaskFilters component in phase_2/frontend/components/tasks/TaskFilters.tsx
- [X] T071 [F003] Add filter dropdown UI (All, Pending, Completed) in TaskFilters
- [X] T072 [F003] Add sort dropdown UI (Title, Created Date, Due Date) in TaskFilters
- [X] T073 [F003] Update phase_2/frontend/lib/api.ts to include filter/sort query params
- [X] T074 [F003] Integrate TaskFilters with task dashboard page
- [X] T075 [F003] Persist filter/sort preferences in session storage

**Checkpoint**: Filtering and sorting working - users can organize task view

---

## Phase 6: Feature 004 - Frontend UI Pages & Components (Priority: P1-P3)

**Goal**: Complete responsive UI with all pages and reusable components
**Assigned Agent**: ui-agent

**Independent Test**: Navigate through all pages → Test on mobile viewport → Verify responsive design

### UI Polish and Enhancements

- [X] T076 [P] [F004] Style Button component with Tailwind variants (primary, secondary, danger) in phase_2/frontend/components/ui/Button.tsx
- [X] T077 [P] [F004] Style Input component with validation states in phase_2/frontend/components/ui/Input.tsx
- [X] T078 [P] [F004] Style Modal component with overlay and animations in phase_2/frontend/components/ui/Modal.tsx
- [X] T079 [F004] Add responsive styles to LoginForm and SignupForm (mobile-first)
- [X] T080 [F004] Add responsive styles to TaskList and TaskItem (mobile-first)
- [X] T081 [F004] Create responsive navigation/header component in phase_2/frontend/components/ui/Header.tsx
- [X] T082 [F004] Add success toast notifications for task operations in phase_2/frontend/components/ui/Toast.tsx
- [X] T083 [F004] Implement error toast notifications for failed operations
- [X] T084 [F004] Add accessibility attributes (aria-labels, focus states) to all interactive elements
- [X] T085 [F004] Test and adjust layout for screens 320px to 1920px width

**Checkpoint**: Polished, responsive UI ready for user testing

---

## Phase 7: Feature 005 - Integration & API Calls with JWT (Priority: P1)

**Goal**: Ensure frontend-backend integration with proper JWT handling and error management
**Assigned Agent**: integration-agent

**Independent Test**: Perform full user flow → Verify JWT attached to all requests → Test token expiry handling → Test error states

### Integration Tasks

- [X] T086 [F005] Verify API client attaches JWT to Authorization header in phase_2/frontend/lib/api.ts
- [X] T087 [F005] Implement 401 response handling with redirect to login in phase_2/frontend/lib/api.ts
- [X] T088 [F005] Add request/response interceptors for error handling in API client
- [X] T089 [F005] Implement token expiry detection and session expired message
- [X] T090 [F005] Verify backend JWT middleware validates token on all /api/{user_id}/tasks endpoints
- [X] T091 [F005] Verify user_id path parameter matches authenticated user in all task endpoints
- [X] T092 [F005] Test full user flows: register → create tasks → filter → edit → delete → logout
- [X] T093 [F005] Add network error handling with retry mechanism
- [X] T094 [F005] Implement optimistic UI updates for task operations

**Checkpoint**: Full integration complete - production-ready user flows

---

## Phase 8: Feature 006 - Testing & Validation (Priority: P2)

**Goal**: Comprehensive test coverage for backend endpoints and frontend components
**Assigned Agent**: testing-agent

**Independent Test**: Run pytest → Run npm test → Verify all tests pass

### Backend Tests (pytest)

- [X] T095 [P] [F006] Create test fixtures in phase_2/backend/tests/conftest.py (test client, mock database, mock user)
- [X] T096 [P] [F006] Create auth endpoint tests in phase_2/backend/tests/test_auth.py:
  - test_register_success
  - test_register_duplicate_email
  - test_register_invalid_email
  - test_register_weak_password
  - test_login_success
  - test_login_invalid_credentials
  - test_logout_success
  - test_get_current_user
- [X] T097 [P] [F006] Create task endpoint tests in phase_2/backend/tests/test_tasks.py:
  - test_create_task_success
  - test_create_task_validation_error
  - test_list_tasks
  - test_list_tasks_with_filters
  - test_get_task_success
  - test_get_task_not_found
  - test_get_task_forbidden (ownership)
  - test_update_task_success
  - test_delete_task_success
  - test_toggle_complete
- [X] T098 [F006] Add edge case tests:
  - test_title_max_length (200 chars)
  - test_description_max_length (1000 chars)
  - test_empty_title_rejected
  - test_pagination

### Frontend Tests (React Testing Library)

- [X] T099 [P] [F006] Setup Vitest and React Testing Library in phase_2/frontend/
- [X] T100 [P] [F006] Create LoginForm tests in phase_2/frontend/tests/components/LoginForm.test.tsx
- [X] T101 [P] [F006] Create SignupForm tests in phase_2/frontend/tests/components/SignupForm.test.tsx
- [X] T102 [P] [F006] Create TaskItem tests in phase_2/frontend/tests/components/TaskItem.test.tsx
- [X] T103 [P] [F006] Create TaskList tests in phase_2/frontend/tests/components/TaskList.test.tsx
- [X] T104 [P] [F006] Create TaskForm tests in phase_2/frontend/tests/components/TaskForm.test.tsx
- [X] T105 [P] [F006] Create TaskFilters tests in phase_2/frontend/tests/components/TaskFilters.test.tsx
- [X] T106 [F006] Test validation error display in forms
- [X] T107 [F006] Test loading states during API calls
- [X] T108 [F006] Test empty state display

**Checkpoint**: All tests passing - ready for deployment

---

## Phase 9: Polish & Cross-Cutting Concerns

**Purpose**: Final cleanup and production readiness

- [X] T109 [P] Run backend linting and formatting (black, isort)
- [X] T110 [P] Run frontend linting and formatting (eslint, prettier)
- [X] T111 Create phase_2/backend/Dockerfile for production
- [X] T112 Create phase_2/frontend/Dockerfile for production
- [X] T113 Update phase_2/docker-compose.yml with production configuration
- [X] T114 Validate all endpoints against contracts/openapi.yaml
- [X] T115 Run quickstart.md validation steps
- [X] T116 Security review: verify no secrets in code, proper error handling, input sanitization
- [X] T117 Performance check: verify <3s page load, <2s task operations

---

## Dependencies & Execution Order

### Phase Dependencies

```
Phase 1: Setup
    ↓
Phase 2: Foundational (BLOCKS ALL)
    ↓
    ├── Phase 3: F001 Authentication ──────────────────────┐
    │       ↓                                              │
    ├── Phase 4: F002 Task CRUD (depends on F001) ─────────┤
    │       ↓                                              │
    ├── Phase 5: F003 Filtering/Sorting (depends on F002) ─┤
    │       ↓                                              │
    ├── Phase 6: F004 UI Polish (depends on F001-F003) ────┤
    │       ↓                                              │
    ├── Phase 7: F005 Integration (depends on F001-F004) ──┤
    │       ↓                                              │
    └── Phase 8: F006 Testing (depends on F001-F005) ──────┘
                          ↓
                  Phase 9: Polish
```

### Feature Dependencies

| Feature | Depends On | Assigned Agent |
|---------|------------|----------------|
| F001: Authentication | Phase 2 (Foundational) | general-purpose |
| F002: Task CRUD | F001 | todo-crud-orchestrator |
| F003: Filtering/Sorting | F002 | filter-sort-agent |
| F004: UI Pages & Components | F001, F002, F003 | ui-agent |
| F005: Integration | F001, F002, F003, F004 | integration-agent |
| F006: Testing | F001-F005 | testing-agent |

### Parallel Opportunities

Within each phase, tasks marked [P] can run in parallel:

- **Phase 1**: T002-T003 (backend/frontend init), T004-T007 (config files), T009-T010 (frontend config)
- **Phase 2**: T019-T023 (module init files), T024-T027 (frontend base)
- **Phase 3**: T028-T029 (schemas), T036-T040 (frontend utilities/components)
- **Phase 4**: T055-T059 (frontend components)
- **Phase 5**: T070 (TaskFilters)
- **Phase 6**: T076-T078 (component styling)
- **Phase 8**: T095-T097 (backend tests), T099-T105 (frontend tests)
- **Phase 9**: T109-T110 (linting)

---

## Implementation Strategy

### MVP First (Features 001-002)

1. Complete Phase 1: Setup
2. Complete Phase 2: Foundational (CRITICAL - blocks all features)
3. Complete Phase 3: Feature 001 (Authentication)
4. Complete Phase 4: Feature 002 (Task CRUD)
5. **STOP and VALIDATE**: Test core functionality independently
6. Deploy/demo if ready

### Full Implementation Order

1. Phase 1: Setup (T001-T011)
2. Phase 2: Foundational (T012-T027)
3. Phase 3: F001 Authentication (T028-T046)
4. Phase 4: F002 Task CRUD (T047-T065)
5. Phase 5: F003 Filtering/Sorting (T066-T075)
6. Phase 6: F004 UI Polish (T076-T085)
7. Phase 7: F005 Integration (T086-T094)
8. Phase 8: F006 Testing (T095-T108)
9. Phase 9: Polish (T109-T117)

---

## Summary

| Phase | Task Range | Count | Description |
|-------|------------|-------|-------------|
| 1 | T001-T011 | 11 | Setup |
| 2 | T012-T027 | 16 | Foundational |
| 3 | T028-T046 | 19 | F001: Authentication |
| 4 | T047-T065 | 19 | F002: Task CRUD |
| 5 | T066-T075 | 10 | F003: Filtering/Sorting |
| 6 | T076-T085 | 10 | F004: UI Polish |
| 7 | T086-T094 | 9 | F005: Integration |
| 8 | T095-T108 | 14 | F006: Testing |
| 9 | T109-T117 | 9 | Polish |
| **Total** | | **117** | |

### Tasks Per User Story (from spec.md)

| User Story | Priority | Related Tasks |
|------------|----------|---------------|
| US1: Registration/Auth | P1 | T028-T046 (19 tasks) |
| US2: Task Creation | P1 | T047-T054, T057, T060-T061 (12 tasks) |
| US3: Task List Viewing | P1 | T055-T056, T058, T060 (4 tasks) |
| US4: Task Completion Toggle | P2 | T049, T064 (2 tasks) |
| US5: Task Editing | P2 | T049, T062 (2 tasks) |
| US6: Task Deletion | P2 | T049, T063 (2 tasks) |
| US7: Task Filtering | P3 | T066-T068, T070-T075 (9 tasks) |
| US8: Task Sorting | P3 | T066-T068, T070-T075 (9 tasks) |

### Suggested MVP Scope

- **MVP**: Phases 1-4 (Features 001-002)
- **Total MVP Tasks**: 65 tasks
- **Delivers**: User registration, login, full task CRUD

---

## Notes

- [P] tasks = different files, no dependencies
- [Feature] label maps task to specific feature for traceability
- Each feature should be independently completable and testable
- Commit after each task or logical group
- Stop at any checkpoint to validate feature independently
- All file paths are relative to repository root
