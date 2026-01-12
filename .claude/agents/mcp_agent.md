# MCP Agent Specification (T144)

**Primary Responsibility:** MCP server management, tool implementation, and database access orchestration

## Overview

The MCP (Model Context Protocol) Agent manages the MCP server infrastructure, implements MCP tools for task management, and orchestrates database access for all CRUD operations. It provides a stateless, tool-based interface for task management that can be consumed by the AI Agent.

## Responsibilities

### 1. MCP Server Management
- Initialize and run MCP server process
- Register MCP tools with the Official MCP SDK
- Handle server lifecycle (startup, shutdown, health checks)
- Implement circuit breaker for resilience
- Monitor server health and availability

### 2. Tool Implementation
Implement 5 core MCP tools:

#### add_task
- **Purpose:** Create a new task
- **Inputs:** `user_id`, `title`, `description?`, `priority?`, `due_date?`
- **Outputs:** `task_id`, `created_at`, `status="created"`
- **Database:** INSERT into tasks table

#### list_tasks
- **Purpose:** Retrieve tasks with filtering
- **Inputs:** `user_id`, `completed?`, `priority?`, `limit?`, `offset?`
- **Outputs:** List of tasks with all attributes
- **Database:** SELECT from tasks WHERE user_id = ? [filters]

#### update_task
- **Purpose:** Modify task attributes
- **Inputs:** `user_id`, `task_id`, `title?`, `description?`, `priority?`, `due_date?`
- **Outputs:** Updated task object
- **Database:** UPDATE tasks SET ... WHERE id = ? AND user_id = ?

#### complete_task
- **Purpose:** Mark task as completed
- **Inputs:** `user_id`, `task_id`
- **Outputs:** Updated task with `completed=true`, `completed_at=<timestamp>`
- **Database:** UPDATE tasks SET completed = true WHERE id = ? AND user_id = ?

#### delete_task
- **Purpose:** Remove a task
- **Inputs:** `user_id`, `task_id`
- **Outputs:** `status="deleted"`, `task_id`
- **Database:** DELETE FROM tasks WHERE id = ? AND user_id = ?

### 3. Database Access
- Connect to Neon PostgreSQL via SQLModel
- Execute CRUD operations with proper error handling
- Enforce user isolation (all queries filter by user_id)
- Use transactions for data integrity
- Handle database connection pooling

### 4. Statelessness Requirements
- **No Server-Side State:** Each tool invocation is independent
- **No Session Management:** No user sessions or caching between calls
- **Database as Source of Truth:** All state persists in PostgreSQL
- **Idempotent Operations:** Same input → same output (where applicable)

## Inputs

### Tool Invocation Input (Generic)
```python
{
    "tool_name": str,      # MCP tool name
    "arguments": {         # Tool-specific arguments
        "user_id": int,    # Always required (for user isolation)
        # ... tool-specific parameters
    }
}
```

### Specific Tool Inputs

#### add_task
```python
{
    "user_id": int,              # Required
    "title": str,                # Required (1-200 chars)
    "description": str | None,   # Optional
    "priority": "low" | "medium" | "high" | None,  # Optional, default: "medium"
    "due_date": str | None,      # Optional, ISO 8601 format
}
```

#### list_tasks
```python
{
    "user_id": int,         # Required
    "completed": bool | None,  # Optional filter
    "priority": str | None,    # Optional filter
    "limit": int = 50,         # Optional, default: 50
    "offset": int = 0,         # Optional, default: 0
}
```

#### update_task
```python
{
    "user_id": int,         # Required
    "task_id": int,         # Required
    "title": str | None,    # Optional
    "description": str | None,  # Optional
    "priority": str | None,     # Optional
    "due_date": str | None,     # Optional
}
```

#### complete_task
```python
{
    "user_id": int,    # Required
    "task_id": int,    # Required
}
```

#### delete_task
```python
{
    "user_id": int,    # Required
    "task_id": int,    # Required
}
```

## Outputs

### Success Response (Generic)
```python
{
    "status": "success",
    "data": {
        # Tool-specific response data
    },
    "metadata": {
        "tool_name": str,
        "execution_time_ms": float,
    }
}
```

### Error Response (Generic)
```python
{
    "status": "error",
    "error": {
        "code": str,           # Error code (validation_error, not_found, etc.)
        "message": str,        # User-friendly error message
        "details": Dict | None,  # Additional error context
    },
    "metadata": {
        "tool_name": str,
        "execution_time_ms": float,
    }
}
```

### Specific Tool Outputs

#### add_task (Success)
```python
{
    "status": "success",
    "data": {
        "task_id": 123,
        "title": "Buy milk",
        "description": None,
        "priority": "medium",
        "due_date": None,
        "completed": false,
        "created_at": "2025-12-31T10:30:00Z",
        "updated_at": "2025-12-31T10:30:00Z",
    }
}
```

#### list_tasks (Success)
```python
{
    "status": "success",
    "data": {
        "tasks": [
            {
                "id": 123,
                "title": "Buy milk",
                "completed": false,
                # ... all task attributes
            },
            # ... more tasks
        ],
        "total": 10,
        "limit": 50,
        "offset": 0,
    }
}
```

## Constraints

### Statelessness Requirements
- **No In-Memory State:** All data in PostgreSQL (no caching)
- **No User Sessions:** Each tool call is independent
- **No Cross-Request Context:** Tools don't share state between invocations
- **Database is Source of Truth:** Always query database for current state

### Performance Constraints
- **Tool Execution Time:** < 100ms (p95, excluding network)
- **Database Query Time:** < 50ms per query
- **Concurrent Requests:** Support 100+ concurrent tool invocations
- **Connection Pool:** Max 20 database connections

### Security Constraints
- **User Isolation:** All queries MUST filter by user_id
- **Input Validation:** Validate all inputs before database access
- **SQL Injection Prevention:** Use parameterized queries (SQLModel handles this)
- **No Direct SQL:** Only use SQLModel ORM (no raw SQL)

### Functional Constraints
- **Idempotency:**
  - add_task: Multiple calls create multiple tasks (NOT idempotent by design)
  - update_task: Same update applied multiple times → same result (idempotent)
  - delete_task: Deleting already-deleted task → 404 error (fail gracefully)
- **Atomicity:** Each tool invocation is a single database transaction
- **Ownership Validation:** Tasks can only be modified by their owner (user_id match)

## Architecture

### MCP Server Implementation

```python
from mcp.server import Server
from mcp.types import Tool, TextContent
from sqlmodel import Session, select
from app.models.task import Task
from app.db.database import get_session

class MCPTaskServer:
    """MCP server for task management tools."""

    def __init__(self):
        self.server = Server("task-manager")
        self._register_tools()

    def _register_tools(self):
        """Register all MCP tools."""
        self.server.add_tool(
            Tool(
                name="add_task",
                description="Add a new task to the user's todo list",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "user_id": {"type": "integer"},
                        "title": {"type": "string", "minLength": 1, "maxLength": 200},
                        "description": {"type": "string"},
                        "priority": {"type": "string", "enum": ["low", "medium", "high"]},
                        "due_date": {"type": "string", "format": "date"},
                    },
                    "required": ["user_id", "title"]
                }
            ),
            handler=self._handle_add_task
        )
        # ... register other tools

    async def _handle_add_task(self, arguments: dict) -> list[TextContent]:
        """Handle add_task tool invocation."""
        db = get_session()

        try:
            # Validate inputs
            user_id = arguments["user_id"]
            title = arguments["title"]

            # Create task
            task = Task(
                user_id=user_id,
                title=title,
                description=arguments.get("description"),
                priority=arguments.get("priority", "medium"),
                due_date=arguments.get("due_date"),
                completed=False,
            )

            db.add(task)
            db.commit()
            db.refresh(task)

            # Return success response
            return [
                TextContent(
                    type="text",
                    text=json.dumps({
                        "status": "success",
                        "data": {
                            "task_id": task.id,
                            "title": task.title,
                            "created_at": task.created_at.isoformat(),
                        }
                    })
                )
            ]

        except ValueError as e:
            return self._error_response("validation_error", str(e))
        except Exception as e:
            logger.error(f"add_task failed: {e}")
            return self._error_response("internal_error", "Failed to create task")
        finally:
            db.close()

    def _error_response(self, code: str, message: str) -> list[TextContent]:
        """Generate error response."""
        return [
            TextContent(
                type="text",
                text=json.dumps({
                    "status": "error",
                    "error": {
                        "code": code,
                        "message": message,
                    }
                })
            )
        ]
```

### Database Schema (SQLModel)

```python
from sqlmodel import SQLModel, Field
from datetime import datetime
from typing import Optional

class Task(SQLModel, table=True):
    """Task model for MCP server."""

    __tablename__ = "tasks"

    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="users.id", index=True)
    title: str = Field(max_length=200)
    description: Optional[str] = None
    priority: str = Field(default="medium")  # low, medium, high
    due_date: Optional[datetime] = None
    completed: bool = Field(default=False)
    completed_at: Optional[datetime] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        indexes = [
            ("user_id", "completed"),  # For filtered queries
            ("user_id", "created_at"),  # For sorting
        ]
```

### Circuit Breaker Integration

```python
from app.middleware.circuit_breaker import CircuitBreaker, CircuitBreakerError

class MCPClient:
    """Client for invoking MCP tools with circuit breaker."""

    def __init__(self):
        self.circuit_breaker = CircuitBreaker(
            failure_threshold=5,
            recovery_timeout=30,
            expected_exception=Exception,
        )

    async def call_tool(self, tool_name: str, arguments: dict) -> dict:
        """
        Call MCP tool with circuit breaker protection.

        Raises:
            CircuitBreakerError: If circuit breaker is open
        """
        return await self.circuit_breaker.call(
            self._invoke_tool,
            tool_name,
            arguments
        )

    async def _invoke_tool(self, tool_name: str, arguments: dict) -> dict:
        """Actual tool invocation logic."""
        # Call MCP server via SDK
        result = await mcp_server.call_tool(tool_name, arguments)
        return json.loads(result[0].text)
```

## Error Handling

### Validation Errors
- **Missing Required Field:** Return 400 with field name
- **Invalid Field Format:** Return 400 with expected format
- **Value Out of Range:** Return 400 with valid range

### Database Errors
- **Task Not Found:** Return 404 with task_id
- **Permission Denied:** Return 403 (task doesn't belong to user)
- **Constraint Violation:** Return 409 (e.g., duplicate task)
- **Connection Error:** Return 503 (database unavailable)

### MCP Server Errors
- **Tool Not Found:** Return 404 (invalid tool name)
- **Server Unavailable:** Circuit breaker opens, return 503
- **Timeout:** Return 504 after 5 seconds

## Testing Strategy

### Unit Tests
- Each MCP tool with valid inputs
- Each MCP tool with invalid inputs (missing fields, wrong types)
- User isolation (user A can't access user B's tasks)
- Edge cases (empty lists, non-existent IDs)

### Integration Tests
- MCP server startup and tool registration
- Database CRUD operations end-to-end
- Circuit breaker behavior (open/close transitions)
- Concurrent tool invocations

### Acceptance Tests
- add_task creates database record
- list_tasks returns correct filtered results
- update_task modifies only specified fields
- complete_task sets completed=true and completed_at
- delete_task removes record from database

### Statelessness Verification
- Multiple identical tool calls produce identical results (for idempotent operations)
- Server restart doesn't affect tool behavior
- No shared state between concurrent tool invocations

## Metrics and Monitoring

### Key Metrics
- **Tool Invocation Count:** Per tool, per user
- **Tool Execution Time:** p50, p95, p99 latency per tool
- **Tool Success Rate:** % of successful invocations per tool
- **Database Query Time:** Average time per query type
- **Circuit Breaker State:** Open/closed transitions

### Alerts
- Tool execution time > 200ms (p95)
- Tool error rate > 5%
- Circuit breaker open for > 1 minute
- Database connection pool exhausted

## Security Considerations

### User Isolation
```python
# ✅ GOOD: Always filter by user_id
tasks = db.exec(
    select(Task).where(
        Task.id == task_id,
        Task.user_id == user_id  # Critical!
    )
).first()

# ❌ BAD: No user_id filter (security vulnerability!)
tasks = db.exec(
    select(Task).where(Task.id == task_id)
).first()
```

### Input Validation
```python
def validate_add_task_input(arguments: dict):
    """Validate add_task inputs."""
    # Required fields
    if "user_id" not in arguments:
        raise ValueError("user_id is required")
    if "title" not in arguments:
        raise ValueError("title is required")

    # Field validation
    if not isinstance(arguments["user_id"], int) or arguments["user_id"] <= 0:
        raise ValueError("user_id must be positive integer")
    if not arguments["title"] or len(arguments["title"]) > 200:
        raise ValueError("title must be 1-200 characters")

    # Optional field validation
    if "priority" in arguments and arguments["priority"] not in ["low", "medium", "high"]:
        raise ValueError("priority must be low, medium, or high")
```

## Related Documentation

- [MCP Tool Invocation Skill](../skills/mcp_tool_invocation.md) - Calling patterns
- [AI Agent Spec](./ai_agent.md) - Tool consumer
- [Architecture](../docs/architecture.md) - System design
- [Database Schema](../docs/database_schema.md) - Task model
- [MCP SDK Documentation](https://modelcontextprotocol.io/docs) - Official SDK

---

**Agent Owner:** Backend Team
**Dependencies:** Official MCP SDK, SQLModel, Neon PostgreSQL
**Security Level:** Critical (direct database access)
**Deployment:** Standalone MCP server process
**Performance Target:** < 100ms tool execution (p95), 100+ concurrent requests
**Statelessness:** Full statelessness - all state in database
