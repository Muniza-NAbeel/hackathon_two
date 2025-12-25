---
description: Mark a task as complete
---

## User Input

```text
$ARGUMENTS
```

## Execution

Use the `todo-task-manager` agent to mark task(s) as complete.

### Complete Options

| Target | Example |
|--------|---------|
| By ID | `/todo.complete 5` |
| By title | `/todo.complete "Buy groceries"` |
| Multiple IDs | `/todo.complete 1 3 5` |
| All pending | `/todo.complete all` |

### Response Format

```
Task Completed
ID: [id]
Title: [title]
Completed at: [timestamp]

[X] tasks remaining
```

### For Multiple Tasks

```
Tasks Completed: [count]

- [id] [title]
- [id] [title]

[X] tasks remaining
```

### Undo

To mark as incomplete again:
`/todo.update [id] status:pending`

## Examples

```
/todo.complete 3
/todo.complete "Buy groceries"
/todo.complete 1 2 3
/todo.complete all
```
