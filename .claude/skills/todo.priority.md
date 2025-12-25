---
name: todo.priority
description: Change task priority
arguments:
  - name: task
    description: Task ID or title
    required: true
  - name: priority
    description: New priority (low|medium|high|urgent)
    required: true
agent: todo-task-manager
---

# Todo Priority Skill

Change task priority level.

## Priority Levels

| Level | Description | Visual |
|-------|-------------|--------|
| urgent | Must do now | 🔴 |
| high | Important | 🟠 |
| medium | Normal | 🟡 |
| low | Can wait | 🟢 |

## Usage

```
todo.priority task="Buy groceries" priority=high
todo.priority task=task-123 priority=urgent
```

## Output

```
PRIORITY UPDATED
================
Task: {{task}}
Previous: [old priority]
New: {{priority}}

📋 [Task title]
   🔴 URGENT → Needs immediate attention

Tasks by Priority:
- 🔴 Urgent: [count]
- 🟠 High: [count]
- 🟡 Medium: [count]
- 🟢 Low: [count]
```
