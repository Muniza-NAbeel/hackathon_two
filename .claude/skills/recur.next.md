---
name: recur.next
description: Generate the next occurrence of a recurring task
arguments:
  - name: task_id
    description: ID of the completed recurring task
    required: true
  - name: completion_date
    description: When the task was completed (defaults to now)
    required: false
agent: recurring-task-engine
---

# Recur Next Skill

Generate the next occurrence of a recurring task.

## Calculation Logic

### Anchored Recurrence
Next date based on original schedule:
- Weekly on Monday → Always Monday
- Monthly on 15th → Always 15th
- Yearly on Jan 1 → Always Jan 1

### Floating Recurrence
Next date based on completion:
- Every 7 days → 7 days from completion
- Every 2 weeks → 14 days from completion

## Process

1. **Load** completed task with recurrence pattern
2. **Parse** recurrence rule (RRULE format)
3. **Calculate** next occurrence date
4. **Apply** adjustments (skip weekends, holidays)
5. **Create** new task instance
6. **Link** to recurring series

## Output

```
NEXT OCCURRENCE GENERATED
=========================
Completed Task: [task title]
Completion Date: {{completion_date}}

Recurrence Pattern: [description]
Calculation Mode: [Anchored/Floating]

Next Task Created:
  ID: [new task id]
  Title: [task title]
  Due Date: [calculated date]
  Occurrence: #[n] in series

Series Status:
  Total Occurrences: [count]
  Remaining: [count or "Ongoing"]
  End Date: [date or "None"]
```
