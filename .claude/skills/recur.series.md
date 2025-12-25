---
name: recur.series
description: Manage a recurring task series
arguments:
  - name: series_id
    description: Recurring series identifier
    required: true
  - name: action
    description: Action (view|pause|resume|end|history)
    required: true
agent: recurring-task-engine
---

# Recur Series Skill

Manage recurring task series.

## Series Actions

### View
Display series information and upcoming occurrences.

### Pause
Temporarily stop generating new occurrences.

### Resume
Resume generating occurrences after pause.

### End
Terminate the series (no more occurrences).

### History
View all past occurrences in the series.

## Series Structure

```json
{
  "series_id": "uuid",
  "template_task": { ... },
  "rrule": "RRULE:...",
  "status": "active|paused|ended",
  "created_at": "timestamp",
  "last_occurrence": "timestamp",
  "next_occurrence": "timestamp",
  "occurrence_count": 12,
  "completed_count": 10
}
```

## Output

### View
```
RECURRING SERIES
================
Series ID: {{series_id}}
Task Template: [task title]
Status: [ACTIVE|PAUSED|ENDED]

Pattern: [human readable]
Started: [date]
Last Occurrence: [date]
Total Occurrences: [count]
Completed: [count] ([percentage]%)

Next 3 Occurrences:
1. [date]
2. [date]
3. [date]
```

### History
```
SERIES HISTORY
==============
Series: {{series_id}}

Occurrence | Due Date   | Status    | Completed
#1         | 2024-01-01 | Completed | 2024-01-01
#2         | 2024-01-08 | Completed | 2024-01-09
#3         | 2024-01-15 | Pending   | -
...
```
