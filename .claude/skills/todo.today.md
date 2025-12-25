---
description: Show all tasks due today
---

## User Input

```text
$ARGUMENTS
```

## Execution

Use the `todo-task-manager` agent to list today's tasks.

### Display Options

| Option | Description |
|--------|-------------|
| (default) | All tasks due today |
| pending | Only pending tasks |
| completed | Only completed tasks |
| all | Include overdue tasks |

### Response Format

```
Today's Tasks ([date])

OVERDUE
- [id] [title] (was due [date]) [priority]

DUE TODAY
- [id] [title] [priority] [status]

Completed Today
- [id] [title] [completed time]

Summary: [X] pending, [Y] completed, [Z] overdue
```

### Sorting

Tasks sorted by:
1. Priority (urgent > high > medium > low)
2. Status (in-progress > pending)
3. Creation time

## Examples

```
/todo.today
/todo.today pending
/todo.today all
```
