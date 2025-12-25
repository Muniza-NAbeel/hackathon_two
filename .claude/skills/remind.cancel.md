---
name: remind.cancel
description: Cancel a scheduled reminder
arguments:
  - name: reminder_id
    description: Reminder ID to cancel
    required: true
  - name: series
    description: Cancel entire series (for recurring)
    required: false
agent: todo-reminder-scheduler
---

# Remind Cancel Skill

Cancel scheduled reminders.

## Cancel Options

### Single Reminder
Cancel one specific reminder.

### Single Occurrence
Cancel one occurrence of a recurring reminder.

### Entire Series
Cancel all future occurrences of a recurring reminder.

## Confirmation

For important reminders:
```
⚠️ Are you sure you want to cancel this reminder?

📝 "{{message}}"
⏰ Scheduled: {{time}}
{{recurring ? "🔁 This is a recurring reminder" : ""}}

[Cancel This Only] [Cancel Entire Series] [Keep Reminder]
```

## Output

```
REMINDER CANCELLED
==================
{{series ?
  "Recurring series cancelled" :
  "Reminder cancelled"
}}

📝 Message: {{message}}
⏰ Was scheduled: {{time}}

{{series ?
  "All future occurrences have been removed." :
  "This reminder will not fire."
}}

Active reminders remaining: [count]

To undo (within 5 minutes):
remind.restore id={{reminder_id}}
```
