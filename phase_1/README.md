# Phase I - Todo In-Memory Console Application

A command-line Todo application with in-memory storage for task management.

## Requirements

- Python 3.13+
- UV virtual environment (recommended)

## Setup

```bash
# Create and activate UV virtual environment
uv venv
source .venv/bin/activate  # Unix/macOS
# OR
.venv\Scripts\activate     # Windows

# No external dependencies required - uses Python stdlib only
```

## Running the Application

```bash
cd phase_1
python -m src.main
```

## Features

1. **Add Task** - Create new tasks with title (required) and description (optional)
2. **View Tasks** - Display all tasks with status indicators `[ ]` / `[x]`
3. **Update Task** - Edit title and/or description of existing tasks
4. **Delete Task** - Remove tasks with confirmation prompt
5. **Toggle Complete** - Mark tasks as complete/incomplete

## Project Structure

```
phase_1/
├── README.md           # This file
└── src/
    ├── __init__.py     # Package constants (MAX_TITLE_LENGTH, MAX_DESCRIPTION_LENGTH)
    ├── models.py       # Task dataclass
    ├── storage.py      # In-memory TaskStorage class
    ├── task_manager.py # Business logic functions
    ├── menu.py         # Console UI and input handlers
    └── main.py         # Application entry point
```

## Specifications

See `specs/001-todo-console-app/` for:
- `spec.md` - Feature specification and user stories
- `plan.md` - Implementation plan
- `tasks.md` - Task breakdown
