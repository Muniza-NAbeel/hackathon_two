---
name: remind.list
description: List all scheduled reminders
arguments:
  - name: filter
    description: Filter (today|week|all|recurring)
    required: false
  - name: sort
    description: Sort order (time|created|priority)
    required: false
agent: todo-reminder-scheduler
---

# Remind List Skill

View all scheduled reminders.

## Filters

| Filter | Description |
|--------|-------------|
| today | Due today |
| week | Due this week |
| all | All reminders |
| recurring | Only recurring |
| overdue | Past due |

## Output

```
📅 SCHEDULED REMINDERS
======================
Filter: {{filter | "all"}}
Total: [count]

🔴 OVERDUE
----------
⏰ [time ago] - [message]
   Task: [linked task if any]

📍 TODAY
--------
⏰ [time] - [message]
   🔁 Recurring: [pattern]

⏰ [time] - [message]

📆 THIS WEEK
------------
[Day], [time] - [message]
[Day], [time] - [message]

📋 LATER
--------
[Date] - [message]

━━━━━━━━━━━━━━━━━━━━━━
Summary:
- Overdue: [count]
- Today: [count]
- This week: [count]
- Recurring active: [count]
```
