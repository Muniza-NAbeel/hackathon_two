---
description: Delete a task from the todo list
---

## User Input

```text
$ARGUMENTS
```

## Execution

Use the `todo-task-manager` agent to delete task(s).

### Delete Options

| Target | Example |
|--------|---------|
| By ID | `/todo.delete 5` |
| By title | `/todo.delete "Buy groceries"` |
| Completed tasks | `/todo.delete completed` |
| All tasks | `/todo.delete all` (requires confirmation) |

### Safety Rules

- Confirm before bulk deletions
- Show task details before deleting
- Offer undo information if available

### Response Format

```
Task Deleted
ID: [id]
Title: [title]
Was: [status]

[X] tasks remaining
```

## Examples

```
/todo.delete 3
/todo.delete "Buy groceries"
/todo.delete completed
/todo.delete all
```
