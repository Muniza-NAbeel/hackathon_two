---
description: Set a reminder for a task or standalone notification
---

## User Input

```text
$ARGUMENTS
```

## Execution

Use the `todo-reminder-scheduler` agent to create a reminder.

### Reminder Options

| Option | Description | Example |
|--------|-------------|---------|
| Task reminder | Link to existing task | `/todo.remind 3 at 2pm` |
| Standalone | Independent reminder | `/todo.remind "Call mom" tomorrow 6pm` |
| Recurring | Repeating reminder | `/todo.remind "Daily standup" every day 9am` |

### Time Formats

| Format | Interpretation |
|--------|----------------|
| "in 30 minutes" | 30 min from now |
| "at 2pm" | Today at 2:00 PM |
| "tomorrow 9am" | Tomorrow at 9:00 AM |
| "next Monday" | Coming Monday, 9:00 AM |
| "every day 9am" | Daily at 9:00 AM |

### Response Format

```
Reminder Set
Task: [description]
When: [absolute time] ([relative])
Recurrence: [pattern or "One-time"]
```

## Examples

```
/todo.remind 3 at 2pm
/todo.remind "Review PR" tomorrow morning
/todo.remind "Team meeting" in 30 minutes
/todo.remind "Take medication" every day 8am
```
