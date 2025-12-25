---
name: todo.stats
description: View task statistics and productivity metrics
arguments:
  - name: period
    description: Time period (today|week|month|all)
    required: false
agent: todo-task-manager
---

# Todo Stats Skill

View productivity statistics.

## Metrics

### Completion Rate
Tasks completed vs total tasks.

### On-Time Rate
Tasks completed by due date.

### Priority Distribution
Breakdown by priority level.

### Activity Trends
Tasks created/completed over time.

## Output

```
TASK STATISTICS
===============
Period: {{period | "all time"}}

📊 Overview
-----------
Total Tasks: [count]
Completed: [count] ([%])
Pending: [count]
Overdue: [count]

⏱️ Performance
--------------
Completion Rate: [%]
On-Time Rate: [%]
Avg Time to Complete: [days/hours]

📈 This Week
------------
Created: [count]
Completed: [count]
Streak: [X] days

📊 By Priority
--------------
🔴 Urgent: [count] ([%] complete)
🟠 High: [count] ([%] complete)
🟡 Medium: [count] ([%] complete)
🟢 Low: [count] ([%] complete)

🏷️ Top Tags
-----------
1. #work - [count] tasks
2. #personal - [count] tasks
3. #shopping - [count] tasks

🎯 Productivity Score: [X]/100
```
