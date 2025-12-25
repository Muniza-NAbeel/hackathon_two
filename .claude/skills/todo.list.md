---
description: List all tasks with optional filtering and sorting
---

## User Input

```text
$ARGUMENTS
```

## Execution

Use the `todo-task-manager` agent to list tasks.

### Filter Options

| Filter | Description | Example |
|--------|-------------|---------|
| (default) | All pending & in-progress | `/todo.list` |
| all | All tasks including completed | `/todo.list all` |
| pending | Only pending tasks | `/todo.list pending` |
| completed | Only completed tasks | `/todo.list completed` |
| priority:X | Filter by priority | `/todo.list priority:high` |
| overdue | Past due date tasks | `/todo.list overdue` |

### Sort Options

| Sort | Description |
|------|-------------|
| due | By due date (default) |
| priority | By priority level |
| created | By creation date |
| alpha | Alphabetically by title |

### Response Format

```
Tasks ([count] total)

[id] [title]
    Due: [date] | Priority: [level] | Status: [status]

[id] [title]
    Due: [date] | Priority: [level] | Status: [status]

Summary: [X] pending, [Y] in-progress, [Z] completed
```

## Examples

```
/todo.list
/todo.list all
/todo.list pending sort:priority
/todo.list priority:high
/todo.list overdue
```
