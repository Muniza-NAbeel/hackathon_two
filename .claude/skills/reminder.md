---
description: Schedule, manage, and trigger reminders for tasks and notifications
---

## User Input

```text
$ARGUMENTS
```

## Overview

This skill handles all reminder and notification operations. Use this when you need to:

- **Create** reminders with natural language times ("tomorrow at 2pm", "in 30 minutes")
- **List** upcoming reminders grouped by timeframe
- **Modify** existing reminder times or messages
- **Cancel** reminders
- **Snooze** triggered reminders

## Execution

Use the `todo-reminder-scheduler` agent to process the user's request.

### Time Parsing Defaults

- "Morning" = 9:00 AM
- "Afternoon" = 2:00 PM
- "Evening" = 6:00 PM
- "End of day" = 5:00 PM (business) or 9:00 PM (personal)
- "Soon" = 15 minutes from now

### Response Requirements

1. Confirm reminder creation with both absolute and relative time
2. Group listed reminders by: OVERDUE, TODAY, THIS WEEK, LATER
3. Highlight any overdue reminders prominently
4. Offer snooze options when triggering notifications

### Output Format

When creating:
```
Reminder Set
Task: [description]
When: [time] ([relative])
Recurrence: [pattern or "One-time"]
```

When listing:
```
Upcoming Reminders

OVERDUE
- [time] - [description]

TODAY
- [time] - [description]

THIS WEEK
- [day, time] - [description]
```

## Examples

```
/reminder set Review PR tomorrow at 2pm
/reminder list
/reminder reschedule 1 to 4pm
/reminder cancel meeting reminder
/reminder snooze 15min
```
