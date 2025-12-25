---
id: "0003"
title: "Phase I Tasks Generation"
stage: tasks
date: 2025-12-24
surface: agent
model: claude-opus-4-5-20251101
feature: 001-todo-console-app
branch: 001-todo-console-app
user: system
command: /sp.tasks
labels: ["phase-1", "tasks", "todo-app", "implementation-tasks"]
links:
  spec: /specs/001-todo-console-app/spec.md
  ticket: null
  adr: null
  pr: null
files:
  - specs/001-todo-console-app/tasks.md
tests:
  - Manual testing scenarios defined (T031)
---

## Prompt

/sp.tasks

# Phase I – Todo In-Memory Console App: Tasks Generation

Create step-by-step coding tasks for Phase I in the folder `phase_1/src/`.

Requirements:
- Python 3.13+ CLI-based application
- Implement all 5 basic features: Add, Delete, Update, View/List, Mark Complete/Incomplete
- Follow clean code principles and modular design
- In-memory task storage only
- Map each task to the corresponding spec in `specs-history/phase_1_specs.md`
- Use agents, sub-agents, and skills workflow for task decomposition
- Respect CLAUDE.md safety rules
- Folder boundaries: `phase_1/src/` for code

Generate tasks in safe, ordered, step-by-step manner covering:
1. Setup Folder Structure
2. Define Task Model
3. Create In-Memory Storage
4. Implement Core Functions
5. Design Console Menu & UX
6. Main Entry Point
7. Validation & Error Handling
8. Manual Testing Task
9. Clean Code & Extensibility
10. Task Output

## Response snapshot

Generated `specs/001-todo-console-app/tasks.md` with 31 tasks organized by user story:

**Phase Structure:**
- Phase 1: Setup (3 tasks) - Project structure
- Phase 2: Foundational (4 tasks) - Models, storage, helpers
- Phase 3: US6 Menu Navigation (4 tasks) - Entry point (blocking)
- Phase 4: US1 View Tasks (3 tasks)
- Phase 5: US2 Add Tasks (3 tasks)
- Phase 6: US3 Toggle Complete (4 tasks)
- Phase 7: US4 Update Tasks (3 tasks)
- Phase 8: US5 Delete Tasks (3 tasks)
- Phase 9: Polish (4 tasks) - Integration

**Key Features:**
- Tasks organized by user story for independent testing
- Proper checklist format: `- [ ] T00X [P?] [USX?] Description with file path`
- Parallel opportunities identified (5 tasks can run in parallel)
- Dependency graph showing execution order
- MVP strategy: US6 + US1 + US2 first
- Each task maps to functional requirements (FR-XXX)

**Files to Create:**
1. `phase_1/src/__init__.py`
2. `phase_1/src/models.py`
3. `phase_1/src/storage.py`
4. `phase_1/src/menu.py`
5. `phase_1/src/task_manager.py`
6. `phase_1/src/main.py`

## Outcome

- Impact: 31 actionable tasks ready for implementation
- Tests: Manual testing defined in T031 (full workflow)
- Files: specs/001-todo-console-app/tasks.md created
- Next prompts: /sp.implement to execute tasks
- Reflection: Tasks properly organized by user story with clear dependencies

## Evaluation notes (flywheel)

- Failure modes observed: None
- Graders run and results (PASS/FAIL): N/A (task generation phase)
- Prompt variant (if applicable): Standard /sp.tasks workflow
- Next experiment (smallest change to try): Execute /sp.implement
