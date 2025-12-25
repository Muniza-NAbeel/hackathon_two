---
description: Add a new task to the todo list
---

## User Input

```text
$ARGUMENTS
```

## Execution

Use the `todo-task-manager` agent to create a new task.

### Task Fields

| Field | Required | Default | Example |
|-------|----------|---------|---------|
| title | Yes | - | "Buy groceries" |
| description | No | empty | "Get milk, eggs, bread" |
| due_date | No | none | "tomorrow", "2024-01-15" |
| priority | No | medium | low, medium, high, urgent |
| status | No | pending | pending, in-progress |

### Response Format

```
Task Created
ID: [id]
Title: [title]
Due: [date or "No due date"]
Priority: [priority]
Status: pending
```

## Examples

```
/todo.add Buy groceries
/todo.add Review PR by tomorrow priority:high
/todo.add Call dentist due:next Monday
/todo.add "Fix login bug" priority:urgent description:"Users can't login with SSO"
```
