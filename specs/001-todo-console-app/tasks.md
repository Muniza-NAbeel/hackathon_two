# Tasks: Phase I – Todo In-Memory Console App

**Input**: Design documents from `/specs/001-todo-console-app/`
**Prerequisites**: plan.md (required), spec.md (required for user stories)

**Tests**: Manual testing only (no automated tests for Phase I per spec)

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story?] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions

- **Code location**: `phase_1/src/`
- **Environment**: Use UV virtual environment for Python 3.13+ dependencies and isolation
- Python 3.13+ with stdlib only (dataclasses, datetime)

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and package structure

- [x] T001 Create `phase_1/src/` directory structure
- [x] T002 [P] Create package marker `phase_1/src/__init__.py`
- [x] T003 [P] Define constants (MAX_TITLE_LENGTH=100, MAX_DESCRIPTION_LENGTH=500) in `phase_1/src/__init__.py`

**Checkpoint**: Project structure ready for module creation

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core data model and storage that ALL user stories depend on

**CRITICAL**: No user story work can begin until this phase is complete

- [x] T004 [P] Create Task dataclass with 5 fields in `phase_1/src/models.py`
  - Fields: id (int), title (str), description (str), is_completed (bool), created_at (datetime)
  - Include `__str__` method for display formatting with status indicators
  - Maps to: FR-002, FR-004, FR-005, FR-006

- [x] T005 [P] Create TaskStorage class in `phase_1/src/storage.py`
  - Internal: `_tasks: dict[int, Task]`, `_next_id: int = 1`
  - Methods: `create()`, `read()`, `read_all()`, `update()`, `delete()`, `next_id()`
  - Maps to: FR-003

- [x] T006 Create input validation helpers in `phase_1/src/menu.py`
  - `validate_menu_choice(choice: str) -> tuple[bool, str]`
  - `validate_task_id(input_str: str) -> tuple[bool, int, str]`
  - `sanitize_title(title: str) -> tuple[str, str]` (trim, truncate to 100)
  - `sanitize_description(desc: str) -> tuple[str, str]` (trim, truncate to 500)
  - Maps to: FR-009, FR-012, FR-013

- [x] T007 Create display helpers in `phase_1/src/menu.py`
  - `print_error(message: str)` - [ERROR] prefix
  - `print_warning(message: str)` - [WARNING] prefix
  - `print_success(message: str)` - [SUCCESS] prefix
  - `print_task(task: Task)` - formatted task display
  - Maps to: FR-007, FR-009

**Checkpoint**: Foundation ready - user story implementation can now begin

---

## Phase 3: User Story 6 - Navigate Application Menu (Priority: P1)

**Goal**: Main menu with numbered options for all operations and exit

**Independent Test**: Launch app, verify menu displays, test valid/invalid selections, verify exit

**Why First**: Menu is the entry point to all functionality (blocking for other stories)

### Implementation for User Story 6

- [x] T008 [US6] Create menu display function `display_menu()` in `phase_1/src/menu.py`
  - Show welcome header with "TODO APPLICATION" banner
  - Display numbered options 1-6: Add, View, Update, Delete, Toggle, Exit
  - Maps to: FR-001

- [x] T009 [US6] Create menu input handler `get_menu_choice()` in `phase_1/src/menu.py`
  - Prompt "Enter your choice (1-6):"
  - Validate input is 1-6
  - Return choice or display error and re-prompt
  - Maps to: FR-001, FR-009

- [x] T010 [US6] Create main loop in `phase_1/src/main.py`
  - Initialize TaskStorage
  - Display welcome message
  - Loop: display_menu() -> get_menu_choice() -> route to handler
  - Handle exit option (6) with goodbye message
  - Maps to: FR-001, FR-010

- [x] T011 [US6] Add "Press Enter to continue" prompt after each operation in `phase_1/src/menu.py`
  - `wait_for_enter()` helper function
  - Maps to: FR-010

**Checkpoint**: Application launches with menu, handles navigation, exits gracefully

---

## Phase 4: User Story 1 - View All Tasks (Priority: P1)

**Goal**: Display all tasks with status indicators, IDs, and timestamps

**Independent Test**: Pre-populate tasks, select "View Tasks", verify display format

### Implementation for User Story 1

- [x] T012 [US1] Implement `list_tasks(storage)` in `phase_1/src/task_manager.py`
  - Return `storage.read_all()` as list[Task]
  - Maps to: FR-007

- [x] T013 [US1] Create view tasks flow `handle_view_tasks(storage)` in `phase_1/src/menu.py`
  - Call `list_tasks(storage)`
  - If empty: display "No tasks yet! Use 'Add Task' to create your first task."
  - If tasks: display each with `[ ]`/`[✓]` status, ID, title, description preview, timestamp
  - Show summary: "Total: X tasks (Y completed, Z incomplete)"
  - Maps to: FR-007, FR-014

- [x] T014 [US1] Wire view handler to menu option 2 in `phase_1/src/main.py`
  - Route choice "2" to `handle_view_tasks(storage)`
  - Maps to: FR-001

**Checkpoint**: User can view all tasks with proper formatting and empty state message

---

## Phase 5: User Story 2 - Add New Task (Priority: P1)

**Goal**: Create tasks with title (required) and description (optional), auto-ID and timestamp

**Independent Test**: Add task with title/description, verify in task list with correct ID and timestamp

### Implementation for User Story 2

- [x] T015 [US2] Implement `add_task(storage, title, description="")` in `phase_1/src/task_manager.py`
  - Validate title not empty after trim
  - Truncate title to 100 chars, description to 500 chars (with warning)
  - Create Task with next_id(), is_completed=False, created_at=now
  - Store via `storage.create(task)`
  - Return created Task
  - Maps to: FR-002, FR-004, FR-005, FR-006, FR-012, FR-013

- [x] T016 [US2] Create add task flow `handle_add_task(storage)` in `phase_1/src/menu.py`
  - Prompt for title (required)
  - Validate title not empty, re-prompt if needed
  - Prompt for description (optional, Enter to skip)
  - Call `add_task(storage, title, description)`
  - Display success message with created task
  - Maps to: FR-005, FR-013

- [x] T017 [US2] Wire add handler to menu option 1 in `phase_1/src/main.py`
  - Route choice "1" to `handle_add_task(storage)`
  - Maps to: FR-001

**Checkpoint**: User can add tasks with validation, auto-ID, and timestamp

---

## Phase 6: User Story 3 - Mark Task Complete/Incomplete (Priority: P2)

**Goal**: Toggle task completion status by ID

**Independent Test**: Toggle incomplete task to complete, verify status change, toggle back

### Implementation for User Story 3

- [x] T018 [US3] Implement `get_task(storage, task_id)` in `phase_1/src/task_manager.py`
  - Return `storage.read(task_id)` (Task or None)
  - Maps to: FR-008

- [x] T019 [US3] Implement `toggle_completion(storage, task_id)` in `phase_1/src/task_manager.py`
  - Get task by ID
  - If not found: return None
  - Toggle `is_completed` flag
  - Update via `storage.update(task)`
  - Return updated Task
  - Maps to: FR-006, FR-008

- [x] T020 [US3] Create toggle flow `handle_toggle_completion(storage)` in `phase_1/src/menu.py`
  - Prompt for task ID
  - Validate ID is positive integer
  - Call `toggle_completion(storage, task_id)`
  - If None: display "Task #X not found."
  - Else: display "Task status changed!" with new status
  - Maps to: FR-006, FR-008, FR-009

- [x] T021 [US3] Wire toggle handler to menu option 5 in `phase_1/src/main.py`
  - Route choice "5" to `handle_toggle_completion(storage)`
  - Maps to: FR-001

**Checkpoint**: User can toggle task completion status with proper error handling

---

## Phase 7: User Story 4 - Update Task Details (Priority: P2)

**Goal**: Edit title and/or description of existing task (partial updates supported)

**Independent Test**: Update task title, verify change; update description only, verify title unchanged

### Implementation for User Story 4

- [x] T022 [US4] Implement `update_task(storage, task_id, title=None, description=None)` in `phase_1/src/task_manager.py`
  - Get task by ID
  - If not found: return None
  - If title provided and not empty: update task.title (trim, truncate)
  - If title provided and empty: keep current (partial update)
  - If description provided: update task.description (trim, truncate)
  - Update via `storage.update(task)`
  - Return updated Task
  - Maps to: FR-008, FR-012, FR-015

- [x] T023 [US4] Create update flow `handle_update_task(storage)` in `phase_1/src/menu.py`
  - Prompt for task ID
  - Validate ID exists
  - Display current task details
  - Prompt for new title (Enter to keep current)
  - Prompt for new description (Enter to keep current)
  - Call `update_task(storage, task_id, title, description)`
  - Display updated task
  - Maps to: FR-008, FR-015

- [x] T024 [US4] Wire update handler to menu option 3 in `phase_1/src/main.py`
  - Route choice "3" to `handle_update_task(storage)`
  - Maps to: FR-001

**Checkpoint**: User can update task details with partial update support

---

## Phase 8: User Story 5 - Delete Task (Priority: P3)

**Goal**: Permanently remove task by ID with confirmation

**Independent Test**: Delete task, confirm, verify removed from list

### Implementation for User Story 5

- [x] T025 [US5] Implement `delete_task(storage, task_id)` in `phase_1/src/task_manager.py`
  - Check task exists via `storage.read(task_id)`
  - If not found: return False
  - Delete via `storage.delete(task_id)`
  - Return True
  - Maps to: FR-008

- [x] T026 [US5] Create delete flow `handle_delete_task(storage)` in `phase_1/src/menu.py`
  - Prompt for task ID
  - Validate ID exists
  - Display task to be deleted
  - Prompt for confirmation: "Are you sure? (y/n)"
  - If 'y': call `delete_task(storage, task_id)`, display success
  - If 'n': display "Deletion cancelled."
  - If other: re-prompt for y/n
  - Maps to: FR-008, FR-011

- [x] T027 [US5] Wire delete handler to menu option 4 in `phase_1/src/main.py`
  - Route choice "4" to `handle_delete_task(storage)`
  - Maps to: FR-001

**Checkpoint**: User can delete tasks with confirmation prompt

---

## Phase 9: Polish & Integration

**Purpose**: Final integration and validation

- [x] T028 Add welcome and goodbye messages in `phase_1/src/main.py`
  - Welcome: ASCII banner with "TODO APPLICATION"
  - Goodbye: "Thank you for using Todo App! Goodbye!"
  - Maps to: FR-001

- [x] T029 Verify all error messages are user-friendly in `phase_1/src/menu.py`
  - Review all error paths
  - Ensure [ERROR], [WARNING], [SUCCESS] prefixes consistent
  - Maps to: FR-009

- [x] T030 Add empty list check for update/delete/toggle operations in `phase_1/src/menu.py`
  - If no tasks: display "No tasks to [update/delete/toggle]. Add a task first."
  - Return to menu without prompting for ID
  - Maps to: Edge case handling

- [ ] T031 Final integration test: Run complete workflow
  - Launch app
  - Add 2 tasks
  - View tasks
  - Toggle task #1 complete
  - Update task #2 description
  - Delete task #1
  - View tasks (verify only #2 remains, ID not reused)
  - Exit app
  - Maps to: All FRs, SC-001 to SC-009

---

## Dependencies & Execution Order

### Phase Dependencies

```
Phase 1: Setup
    │
    ▼
Phase 2: Foundational (models.py, storage.py, validation helpers)
    │
    ▼
Phase 3: US6 - Menu Navigation (BLOCKING - required for all other stories)
    │
    ├── Phase 4: US1 - View Tasks ──────────┐
    │                                       │
    ├── Phase 5: US2 - Add Task ────────────┤ (Can run in parallel after US6)
    │                                       │
    ├── Phase 6: US3 - Toggle Complete ─────┤
    │                                       │
    ├── Phase 7: US4 - Update Task ─────────┤
    │                                       │
    └── Phase 8: US5 - Delete Task ─────────┘
                        │
                        ▼
                Phase 9: Polish
```

### User Story Dependencies

| Story | Depends On | Can Parallel With |
|-------|------------|-------------------|
| US6 (Menu) | Phase 2 | None (blocking) |
| US1 (View) | US6 | US2, US3, US4, US5 |
| US2 (Add) | US6 | US1, US3, US4, US5 |
| US3 (Toggle) | US6 | US1, US2, US4, US5 |
| US4 (Update) | US6 | US1, US2, US3, US5 |
| US5 (Delete) | US6 | US1, US2, US3, US4 |

### Parallel Opportunities

**Phase 2 (All parallel - different files)**:
```
T004: models.py
T005: storage.py
T006: menu.py (validation)
T007: menu.py (display helpers)
```

**After US6 Complete (All parallel - different functions)**:
```
US1: View Tasks (T012-T014)
US2: Add Task (T015-T017)
US3: Toggle (T018-T021)
US4: Update (T022-T024)
US5: Delete (T025-T027)
```

---

## Implementation Strategy

### MVP First (US6 + US1 + US2)

1. Complete Phase 1: Setup (T001-T003)
2. Complete Phase 2: Foundational (T004-T007)
3. Complete Phase 3: US6 Menu (T008-T011)
4. Complete Phase 4: US1 View (T012-T014)
5. Complete Phase 5: US2 Add (T015-T017)
6. **STOP and VALIDATE**: App can add and view tasks
7. Demo as MVP

### Incremental Delivery

1. MVP (US6 + US1 + US2) → Can add and view tasks
2. Add US3 (Toggle) → Can track progress
3. Add US4 (Update) → Can edit mistakes
4. Add US5 (Delete) → Full CRUD complete
5. Polish → Production ready

---

## Task Summary

| Phase | Tasks | Parallel | Description |
|-------|-------|----------|-------------|
| Phase 1: Setup | 3 | 2 | Project structure |
| Phase 2: Foundational | 4 | 3 | Models, storage, helpers |
| Phase 3: US6 Menu | 4 | 0 | Navigation (blocking) |
| Phase 4: US1 View | 3 | 0 | View tasks |
| Phase 5: US2 Add | 3 | 0 | Add tasks |
| Phase 6: US3 Toggle | 4 | 0 | Toggle completion |
| Phase 7: US4 Update | 3 | 0 | Update tasks |
| Phase 8: US5 Delete | 3 | 0 | Delete tasks |
| Phase 9: Polish | 4 | 0 | Integration |
| **Total** | **31** | **5** | |

---

## Files to Create

| Priority | File | Created In |
|----------|------|------------|
| 1 | `phase_1/src/__init__.py` | T002-T003 |
| 2 | `phase_1/src/models.py` | T004 |
| 3 | `phase_1/src/storage.py` | T005 |
| 4 | `phase_1/src/menu.py` | T006-T009, T013, T016, T020, T023, T026 |
| 5 | `phase_1/src/task_manager.py` | T012, T015, T018-T019, T022, T025 |
| 6 | `phase_1/src/main.py` | T010-T011, T014, T017, T021, T024, T027-T028 |

---

## Notes

- **UV Environment Setup**: `uv venv && source .venv/bin/activate` (or `.venv\Scripts\activate` on Windows)
- No automated tests for Phase I (manual testing per spec)
- All code in `phase_1/src/` only
- Python stdlib only (dataclasses, datetime)
- IDs never reused after deletion
- Status indicators: `[ ]` incomplete, `[✓]` complete
- FR-XXX references map to Functional Requirements in spec.md
- SC-XXX references map to Success Criteria in spec.md
