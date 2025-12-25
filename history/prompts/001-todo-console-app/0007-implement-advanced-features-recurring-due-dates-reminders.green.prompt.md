---
id: 0007
title: Implement Advanced Features - Recurring Tasks, Due Dates, Reminders
stage: green
date: 2025-12-25
surface: agent
model: claude-opus-4-5-20251101
feature: 001-todo-console-app
branch: 001-todo-console-app
user: munizanabeel
command: /sp.implement-advanced
labels: [recurring-tasks, due-dates, reminders, AFR-001, AFR-002, AFR-003]
links:
  spec: specs/001-todo-console-app/spec.md
  ticket: null
  adr: null
  pr: null
files:
  - phase_1/src/models.py
  - phase_1/src/task_manager.py
  - phase_1/src/ui.py
  - phase_1/src/menu.py
  - phase_1/src/main.py
tests:
  - Manual import verification test
  - Recurrence enum get_next_due_date() test
  - Task creation with due_date and recurrence test
  - get_reminders() function test
  - complete_recurring_task() function test
---

## Prompt

/sp.implement-advanced

Implement advanced features for the Todo Console App:
- AFR-001: Recurring tasks (daily/weekly/monthly)
- AFR-002: Due dates for tasks
- AFR-003: CLI reminders/notifications for due/overdue tasks

## Response snapshot

Successfully implemented all advanced features across 5 files:

**models.py changes:**
- Added `Recurrence` enum with NONE=0, DAILY=1, WEEKLY=7, MONTHLY=30
- Added `get_next_due_date()` method to calculate next occurrence
- Extended Task dataclass with `due_date: datetime | None` and `recurrence: Recurrence` fields

**task_manager.py changes:**
- Updated `add_task()` to accept due_date and recurrence parameters
- Added `complete_recurring_task()` - marks task complete and creates next instance
- Added `get_reminders()` - returns dict with overdue, due_today, due_soon lists
- Added `get_due_tasks()`, `get_overdue_tasks()`, `get_upcoming_tasks()` helpers

**ui.py changes:**
- Extended menu to 10 options (1-9 plus 0 for Exit)
- Added Reminders option (choice 9)
- Updated `print_tasks_table()` with Due Date and Recurrence columns
- Added `print_reminders_panel()` for displaying due/overdue tasks
- Added `print_startup_reminders()` for app launch notifications

**menu.py changes:**
- Added `get_recurrence_choice()` for recurrence pattern selection
- Added `get_due_date_input()` for YYYY-MM-DD HH:MM input
- Updated `handle_add_task_with_options()` with due date and recurrence prompts
- Added `handle_toggle_with_recurrence()` for recurring task completion
- Added `handle_reminders()` to view due/overdue tasks

**main.py changes:**
- Added startup reminder check on application launch
- Integrated `get_reminders()` and `print_startup_reminders()`
- Added menu routing for Reminders (choice 9)

## Outcome

- Impact: Full advanced features implementation - recurring tasks auto-regenerate on completion, due dates tracked, reminders shown at startup and on demand
- Tests: All imports verified, Recurrence enum works, task creation with advanced fields works, reminders function returns correct categorization, recurring task completion creates next instance
- Files: 5 files modified (models.py, task_manager.py, ui.py, menu.py, main.py)
- Next prompts: Consider adding notification sounds, persistent reminder storage, or snooze functionality
- Reflection: Implementation followed spec requirements precisely; the Recurrence enum's get_next_due_date() method cleanly encapsulates date calculation logic

## Evaluation notes (flywheel)

- Failure modes observed: None - all tests passed
- Graders run and results (PASS/FAIL): PASS - All imports successful, all function tests passed
- Prompt variant (if applicable): Standard /sp.implement-advanced command
- Next experiment (smallest change to try): Add unit tests for edge cases like month boundaries
