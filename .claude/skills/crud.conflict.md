---
name: crud.conflict
description: Detect and resolve data conflicts between interfaces
arguments:
  - name: task_id
    description: Specific task ID to check (optional, checks all if omitted)
    required: false
  - name: strategy
    description: Resolution strategy (interactive|last-write|merge)
    required: false
agent: todo-crud-orchestrator
---

# CRUD Conflict Resolution Skill

Detect and resolve data conflicts across interfaces.

## Conflict Types

### Value Conflicts
- Same field modified differently on multiple interfaces
- Resolution: Interactive selection or last-write-wins

### Delete Conflicts
- Task deleted on one interface, modified on another
- Resolution: Ask user to keep or discard

### Create Conflicts
- Duplicate tasks created on multiple interfaces
- Resolution: Merge or keep both with different IDs

### Order Conflicts
- Different ordering/prioritization across interfaces
- Resolution: Use most recent ordering

## Resolution Strategies

### Interactive (Default)
```
CONFLICT DETECTED: Task [ID]
============================
Field: [field_name]

Console version: [value]
Web version: [value]
Chatbot version: [value]

Modified times:
- Console: [timestamp]
- Web: [timestamp]

Select resolution:
1. Use Console version
2. Use Web version
3. Use Chatbot version
4. Enter custom value
5. Skip (keep conflict)
```

### Last-Write-Wins
- Automatically use most recently modified value
- Log all overwritten values for audit

### Merge
- Combine non-conflicting changes
- Flag true conflicts for manual review

## Output

```
CONFLICT RESOLUTION REPORT
==========================
Tasks Checked: [count]
Conflicts Found: [count]
Conflicts Resolved: [count]
Pending Resolution: [count]

Resolution Summary:
- [Task ID]: [field] → [chosen value] (from [interface])
...
```
