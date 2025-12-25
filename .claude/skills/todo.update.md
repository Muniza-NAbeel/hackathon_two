---
description: Update an existing task's details
---

## User Input

```text
$ARGUMENTS
```

## Execution

Use the `todo-task-manager` agent to update task fields.

### Updatable Fields

| Field | Syntax | Example |
|-------|--------|---------|
| title | title:"new title" | title:"Updated task name" |
| description | desc:"text" | desc:"New description" |
| due_date | due:date | due:tomorrow, due:2024-01-20 |
| priority | priority:level | priority:high |
| status | status:value | status:in-progress |
| complete | complete | Marks as complete |

### Response Format

```
Task Updated
ID: [id]

Changes:
- [field]: [old] -> [new]

Current State:
Title: [title]
Due: [date]
Priority: [priority]
Status: [status]
```

## Examples

```
/todo.update 3 priority:high
/todo.update "Buy groceries" due:tomorrow
/todo.update 5 status:in-progress
/todo.update 2 title:"New title" priority:urgent
/todo.update 1 complete
```
