---
name: crud.batch
description: Execute batch CRUD operations on multiple tasks
arguments:
  - name: operation
    description: Batch operation (create|update|delete|complete)
    required: true
  - name: filter
    description: Filter criteria for selecting tasks
    required: false
  - name: data
    description: JSON data for the operation
    required: false
agent: todo-crud-orchestrator
---

# CRUD Batch Operations Skill

Execute bulk operations on multiple tasks efficiently.

## Supported Batch Operations

### Batch Create
```json
{
  "operation": "create",
  "tasks": [
    {"title": "Task 1", "priority": "high"},
    {"title": "Task 2", "due_date": "2024-12-25"}
  ]
}
```

### Batch Update
```json
{
  "operation": "update",
  "filter": {"status": "pending"},
  "update": {"priority": "high"}
}
```

### Batch Delete
```json
{
  "operation": "delete",
  "filter": {"status": "completed", "older_than": "30d"}
}
```

### Batch Complete
```json
{
  "operation": "complete",
  "filter": {"tag": "sprint-1"}
}
```

## Execution Flow

1. **Parse** operation and filter criteria
2. **Preview** affected tasks (count and sample)
3. **Confirm** with user for destructive operations
4. **Execute** in transaction with rollback capability
5. **Report** results with success/failure counts

## Output

```
BATCH OPERATION: {{operation}}
=============================
Filter: {{filter}}
Tasks Affected: [count]

Preview:
1. [Task title] - [current state]
2. [Task title] - [current state]
...

[Confirm to proceed? Y/N]

Result:
- Successful: [count]
- Failed: [count]
- Skipped: [count]

Errors (if any):
- Task [ID]: [error message]
```
