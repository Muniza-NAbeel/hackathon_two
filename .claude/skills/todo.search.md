---
name: todo.search
description: Search tasks by keyword or criteria
arguments:
  - name: query
    description: Search query
    required: true
  - name: scope
    description: Search scope (title|description|all)
    required: false
agent: todo-task-manager
---

# Todo Search Skill

Search across all tasks.

## Search Capabilities

### Text Search
- Search in task titles
- Search in descriptions
- Full-text across all fields

### Filter Search
- By status: `status:pending`
- By priority: `priority:high`
- By date: `due:today`
- By tag: `tag:work`

### Combined Search
```
"meeting" status:pending priority:high
```

## Output

```
SEARCH RESULTS
==============
Query: "{{query}}"
Scope: {{scope | "all"}}

Found [X] tasks:

1. [Title] ⭐ High
   Due: [date] | Status: [status]
   Match: "...[highlighted]..."

2. [Title]
   Due: [date] | Status: [status]
   Match: "...[highlighted]..."

No more results.
```
