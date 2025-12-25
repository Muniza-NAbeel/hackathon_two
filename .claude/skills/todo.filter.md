---
name: todo.filter
description: Filter tasks by multiple criteria
arguments:
  - name: status
    description: Filter by status (pending|in_progress|completed|all)
    required: false
  - name: priority
    description: Filter by priority (low|medium|high|urgent)
    required: false
  - name: due
    description: Filter by due date (overdue|today|week|month)
    required: false
  - name: tag
    description: Filter by tag
    required: false
agent: todo-task-manager
---

# Todo Filter Skill

Filter tasks by multiple criteria.

## Filter Options

### Status
- `pending` - Not started
- `in_progress` - In progress
- `completed` - Done
- `all` - All statuses

### Priority
- `urgent` - Must do immediately
- `high` - Important
- `medium` - Normal
- `low` - Can wait

### Due Date
- `overdue` - Past due
- `today` - Due today
- `tomorrow` - Due tomorrow
- `week` - Due this week
- `month` - Due this month
- `none` - No due date

### Tags
Filter by any assigned tag.

## Output

```
FILTERED TASKS
==============
Filters Applied:
- Status: {{status | "all"}}
- Priority: {{priority | "all"}}
- Due: {{due | "all"}}
- Tag: {{tag | "none"}}

Results: [X] tasks

OVERDUE (if applicable)
-----------------------
1. [Task] - [days] days late

TODAY
-----
2. [Task] - Due [time]

THIS WEEK
---------
3. [Task] - Due [day]

Summary:
- Showing: [X] of [Y] total tasks
- Matching criteria: [filter description]
```
