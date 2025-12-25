---
id: "0006"
title: "Implement Intermediate Features Priority Tags Search Filter Sort"
stage: green
date: 2025-12-24
surface: agent
model: claude-opus-4-5-20251101
feature: 001-todo-console-app
branch: 001-todo-console-app
user: user
command: /sp.implement
labels: ["intermediate-features", "priority", "tags", "search", "filter", "sort"]
links:
  spec: specs/001-todo-console-app/spec.md
  ticket: null
  adr: null
  pr: null
files:
  - phase_1/src/models.py
  - phase_1/src/task_manager.py
  - phase_1/src/menu.py
  - phase_1/src/ui.py
  - phase_1/src/main.py
tests:
  - Manual verification of imports and function execution
---

## Prompt

/sp.implement-intermediate

# Phase I – Todo CLI: Intermediate Features (Priority, Tags, Search, Filter, Sort)

Objective:
Enhance existing Phase I Todo CLI app with smart organization & usability features:
- Task priority (High/Medium/Low)
- Task tags/categories (Work/Home/Personal)
- Search by keyword
- Filter by status, priority, tag
- Sort by priority, title, or future due date

Requirements:
- Python 3.13+ CLI-based application
- Safe, spec-driven code generation
- Modular design: integrate into existing `phase_1/src/` structure
- Respect CLAUDE.md safety rules (no scripts/install, only file creation and content generation)
- Use agents/sub-agents and skills for task decomposition

---

Generate safe Python code additions for the following files:

1. **models.py** - Update Task class with priority field and tags field
2. **task_manager.py** - Add search_tasks, filter_tasks, sort_tasks functions
3. **menu.py** - Add new menu options for Search, Filter, Sort
4. **main.py** - Integrate new menu options into main loop

## Response snapshot

Successfully implemented intermediate features for Phase I Todo CLI:

### Changes Made:

1. **models.py**:
   - Added `Priority` enum (HIGH=1, MEDIUM=2, LOW=3)
   - Added `VALID_TAGS` frozenset (Work, Home, Personal, Shopping, Health, Finance, Learning)
   - Extended `Task` dataclass with `priority` and `tags` fields
   - Added `matches_keyword()` method for search functionality

2. **task_manager.py**:
   - Updated `add_task()` to accept priority and tags parameters
   - Added `search_tasks(storage, keyword)` - searches title, description, tags
   - Added `filter_tasks(storage, status, priority, tag)` - AND-combined filters
   - Added `sort_tasks(storage, by, reverse)` - sorts by priority/title/created/status
   - Added `update_task_priority()` and `update_task_tags()` helper functions

3. **ui.py**:
   - Updated menu to show 9 options (added Search, Filter, Sort)
   - Updated `print_tasks_table()` to display Priority and Tags columns
   - Updated `print_task_details()` to show priority and tags
   - Added helper functions: `display_priority_menu()`, `display_tags_menu()`, `display_filter_menu()`, `display_sort_menu()`
   - Added result display functions: `print_search_results()`, `print_filter_results()`, `print_sort_results()`

4. **menu.py**:
   - Added `get_priority_choice()` and `get_tags_input()` input helpers
   - Added `handle_search_tasks()`, `handle_filter_tasks()`, `handle_sort_tasks()` handlers
   - Added `handle_add_task_with_options()` for creating tasks with priority and tags
   - Updated validation to support 1-9 menu choices

5. **main.py**:
   - Updated imports to include new handlers
   - Extended main loop to handle options 6 (Search), 7 (Filter), 8 (Sort), 9 (Exit)

### Testing:
- All imports verified successful
- Task creation with priority and tags works correctly
- Search, filter, and sort functions return expected results

## Outcome

- Impact: Major feature enhancement - added 5 intermediate features (priority, tags, search, filter, sort)
- Tests: Manual verification passed - all imports work, functions execute correctly
- Files: 5 files modified (models.py, task_manager.py, menu.py, ui.py, main.py)
- Next prompts: Consider adding due dates, recurring tasks, or data persistence
- Reflection: Implementation followed spec-driven approach, maintained backward compatibility

## Evaluation notes (flywheel)

- Failure modes observed: None - implementation completed successfully
- Graders run and results (PASS/FAIL): PASS - all manual tests passed
- Prompt variant (if applicable): N/A
- Next experiment (smallest change to try): Add automated unit tests for new functions
