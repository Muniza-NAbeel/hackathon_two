"""
Todo In-Memory Console Application - Phase I

A command-line Todo application with in-memory storage for task management.
Use UV virtual environment for Python 3.13+ dependencies and isolation.

Setup:
    uv venv && source .venv/bin/activate  # Unix/macOS
    uv venv && .venv\\Scripts\\activate   # Windows

Features:
    - Add tasks with title and description
    - View all tasks with status indicators
    - Update task title and description
    - Delete tasks with confirmation
    - Toggle task completion status

Maps to: FR-001 to FR-015 (see specs/001-todo-console-app/spec.md)
"""

# Constants for input validation (FR-005)
MAX_TITLE_LENGTH: int = 100
MAX_DESCRIPTION_LENGTH: int = 500

# Application metadata
__version__ = "1.0.0"
__author__ = "Phase I Implementation"

__all__ = [
    "MAX_TITLE_LENGTH",
    "MAX_DESCRIPTION_LENGTH",
]
