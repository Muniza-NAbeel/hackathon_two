---
name: recur.pattern
description: Define or modify a recurrence pattern for a task
arguments:
  - name: task_id
    description: Task to make recurring
    required: true
  - name: pattern
    description: Recurrence pattern (daily|weekly|monthly|custom)
    required: true
  - name: interval
    description: Interval between occurrences (default 1)
    required: false
  - name: days
    description: Specific days (for weekly, e.g., "Mon,Wed,Fri")
    required: false
  - name: end_date
    description: End date for recurrence
    required: false
  - name: count
    description: Maximum number of occurrences
    required: false
agent: recurring-task-engine
---

# Recur Pattern Skill

Define or modify recurrence patterns for tasks.

## Pattern Types

### Daily
```
RRULE:FREQ=DAILY;INTERVAL=1
Every day

RRULE:FREQ=DAILY;INTERVAL=2
Every 2 days

RRULE:FREQ=DAILY;BYDAY=MO,TU,WE,TH,FR
Every weekday
```

### Weekly
```
RRULE:FREQ=WEEKLY;INTERVAL=1;BYDAY=MO
Every Monday

RRULE:FREQ=WEEKLY;INTERVAL=2;BYDAY=MO,WE,FR
Every 2 weeks on Mon/Wed/Fri
```

### Monthly
```
RRULE:FREQ=MONTHLY;BYMONTHDAY=15
15th of every month

RRULE:FREQ=MONTHLY;BYDAY=2TU
2nd Tuesday of every month

RRULE:FREQ=MONTHLY;BYMONTHDAY=-1
Last day of every month
```

### Yearly
```
RRULE:FREQ=YEARLY;BYMONTH=1;BYMONTHDAY=1
Every January 1st
```

## Process

1. **Validate** task exists
2. **Parse** pattern parameters
3. **Generate** RRULE string
4. **Calculate** first occurrence
5. **Save** pattern to task
6. **Create** initial occurrence if needed

## Output

```
RECURRENCE PATTERN SET
======================
Task: [task title]
Pattern: {{pattern}}

RRULE: [generated rrule]

Human Readable:
[Natural language description]

Next 5 Occurrences:
1. [date]
2. [date]
3. [date]
4. [date]
5. [date]

End Condition: [date or count or "Ongoing"]
```
