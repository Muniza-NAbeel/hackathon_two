"""
MCP Server Module (Integrated)

This module provides MCP (Model Context Protocol) tools directly within the FastAPI backend.
Replaces the separate MCP server for PDF spec compliance.

Architecture:
    FastAPI Server
    ├── Chat Endpoint
    ├── AI Agent (Gemini)
    └── MCP Server (this module) ──> Database

Tools:
    - add_task: Create a new task
    - list_tasks: List all tasks with filters
    - complete_task: Mark task as complete
    - delete_task: Remove a task
    - update_task: Update task details
"""

from app.mcp_server.tools import (
    add_task,
    list_tasks,
    complete_task,
    delete_task,
    update_task,
    MCPResponse,
)

__all__ = [
    "add_task",
    "list_tasks",
    "complete_task",
    "delete_task",
    "update_task",
    "MCPResponse",
]
