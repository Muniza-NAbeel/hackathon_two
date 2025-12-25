---
name: remind.recurring
description: Set up a recurring reminder
arguments:
  - name: message
    description: Reminder message
    required: true
  - name: pattern
    description: Recurrence pattern (daily|weekly|monthly|custom)
    required: true
  - name: time
    description: Time for reminder
    required: true
  - name: days
    description: Specific days (for weekly)
    required: false
agent: todo-reminder-scheduler
---

# Remind Recurring Skill

Create recurring reminders.

## Patterns

### Daily
```
remind.recurring message="Take medication" pattern=daily time="9:00 AM"
```

### Weekly
```
remind.recurring message="Team standup" pattern=weekly time="10:00 AM" days="Mon,Wed,Fri"
```

### Monthly
```
remind.recurring message="Pay rent" pattern=monthly time="9:00 AM" day=1
```

### Custom
```
remind.recurring message="Check-in" pattern="every 3 days" time="2:00 PM"
```

## Output

```
RECURRING REMINDER SET
======================
📝 Message: {{message}}
🔁 Pattern: {{pattern}}
⏰ Time: {{time}}
{{days ? "📅 Days: " + days : ""}}

Schedule Preview (next 5):
1. [date] at [time]
2. [date] at [time]
3. [date] at [time]
4. [date] at [time]
5. [date] at [time]

To modify: remind.recurring id=[id] ...
To cancel: remind.cancel id=[id]
```
