---
name: remind.snooze
description: Snooze a reminder for later
arguments:
  - name: reminder_id
    description: Reminder to snooze
    required: true
  - name: duration
    description: Snooze duration (15m|30m|1h|3h|tomorrow)
    required: false
agent: todo-reminder-scheduler
---

# Remind Snooze Skill

Postpone a reminder temporarily.

## Snooze Durations

| Input | Duration |
|-------|----------|
| 15m | 15 minutes |
| 30m | 30 minutes |
| 1h | 1 hour |
| 3h | 3 hours |
| tomorrow | Next day 9 AM |
| custom | Specific time |

## Snooze Limits

- Max snoozes per reminder: 3
- After max snoozes: escalate or dismiss
- Reset count on reminder edit

## Output

```
REMINDER SNOOZED
================
Reminder: [description]
Original Time: [time]
Snoozed Until: [new time]

Snooze Count: [X] of 3

[New time calculated]

I'll remind you again at [time].

{{snooze_count >= 2 ?
  "⚠️ Last snooze available. Consider rescheduling or completing the task." :
  ""
}}
```
