---
name: todo.bulk
description: Perform bulk operations on multiple tasks
arguments:
  - name: action
    description: Bulk action (complete|delete|update|tag)
    required: true
  - name: filter
    description: Filter to select tasks
    required: true
  - name: value
    description: Value for update/tag action
    required: false
agent: todo-task-manager
---

# Todo Bulk Skill

Perform operations on multiple tasks.

## Bulk Actions

### Bulk Complete
Mark multiple tasks as done.
```
todo.bulk action=complete filter="status:pending tag:sprint-1"
```

### Bulk Delete
Remove multiple tasks.
```
todo.bulk action=delete filter="status:completed older:30d"
```

### Bulk Update
Update field on multiple tasks.
```
todo.bulk action=update filter="tag:work" value="priority:high"
```

### Bulk Tag
Add tag to multiple tasks.
```
todo.bulk action=tag filter="due:this-week" value="urgent"
```

## Safety Features

- Preview before execution
- Confirmation required for destructive actions
- Undo capability for recent bulk operations

## Output

```
BULK OPERATION
==============
Action: {{action}}
Filter: {{filter}}
{{value ? "Value: " + value : ""}}

Preview:
Tasks affected: [count]

1. [Task title]
2. [Task title]
3. [Task title]
... and [X] more

⚠️ This action will {{action}} [count] tasks.
Proceed? [Y/N]

---

Result:
✅ Successful: [count]
❌ Failed: [count]
⏭️ Skipped: [count]

{{action == "delete" ? "Undo available for 5 minutes" : ""}}
```
