---
description: List all scheduled reminders
---

## User Input

```text
$ARGUMENTS
```

## Execution

Use the `todo-reminder-scheduler` agent to list reminders.

### Filter Options

| Filter | Description |
|--------|-------------|
| (default) | All upcoming reminders |
| today | Only today's reminders |
| week | This week's reminders |
| overdue | Past due reminders |
| task:[id] | Reminders for specific task |

### Response Format

```
Upcoming Reminders

OVERDUE
- [time] - [description] (was due [date])

TODAY
- [time] - [description]

THIS WEEK
- [day, time] - [description]

LATER
- [date] - [description]

Summary: [X] total, [Y] today, [Z] overdue
```

### Actions Available

- Snooze: `/todo.remind snooze [id] 15min`
- Cancel: `/todo.remind cancel [id]`
- Reschedule: `/todo.remind [id] at [new time]`

## Examples

```
/todo.reminders
/todo.reminders today
/todo.reminders week
/todo.reminders overdue
/todo.reminders task:5
```
