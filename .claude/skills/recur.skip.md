---
name: recur.skip
description: Skip the next occurrence of a recurring task
arguments:
  - name: task_id
    description: Current recurring task to skip
    required: true
  - name: reason
    description: Reason for skipping (optional)
    required: false
  - name: reschedule
    description: Reschedule to specific date instead of skipping
    required: false
agent: recurring-task-engine
---

# Recur Skip Skill

Skip or reschedule a recurring task occurrence.

## Skip Options

### Skip Entirely
Remove this occurrence, generate next one normally.

### Skip with Reason
Log the reason for skipping (vacation, holiday, etc.).

### Reschedule
Move to a different date instead of skipping.

## Process

1. **Validate** task is part of recurring series
2. **Mark** current occurrence as skipped
3. **Log** reason if provided
4. **Calculate** next normal occurrence
5. **Create** next occurrence (or rescheduled one)
6. **Update** series statistics

## Output

### Skip
```
OCCURRENCE SKIPPED
==================
Task: [task title]
Original Due: [date]
Reason: {{reason | "Not specified"}}

Series continues:
Next Occurrence: [calculated date]

Skip logged in series history.
```

### Reschedule
```
OCCURRENCE RESCHEDULED
======================
Task: [task title]
Original Due: [date]
New Due: {{reschedule}}

Note: This is a one-time change.
Regular pattern resumes after this occurrence.

Next Regular Occurrence: [date]
```
