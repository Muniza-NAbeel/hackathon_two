---
name: intent.parse
description: Parse natural language input to extract structured intent
arguments:
  - name: message
    description: Natural language message to parse
    required: true
  - name: context
    description: Additional context for disambiguation
    required: false
agent: chat-intent-resolver
---

# Intent Parse Skill

Extract structured intent from natural language messages.

## Intent Structure

```json
{
  "primary_intent": "string",
  "secondary_intents": ["string"],
  "entities": {
    "task_title": "string",
    "date": "ISO date",
    "priority": "low|medium|high",
    "tags": ["string"]
  },
  "modifiers": {
    "urgency": "low|normal|high",
    "scope": "single|multiple|all"
  },
  "confidence": 0.0-1.0
}
```

## Intent Categories

### Task Intents
- `task.create` - Create a new task
- `task.list` - View tasks
- `task.update` - Modify a task
- `task.complete` - Mark task done
- `task.delete` - Remove a task

### Query Intents
- `query.status` - Check task status
- `query.search` - Find specific tasks
- `query.count` - Get task counts
- `query.overdue` - Find overdue items

### System Intents
- `system.help` - Get assistance
- `system.settings` - Modify preferences
- `system.undo` - Revert last action

## Output

```
INTENT ANALYSIS
===============
Input: "{{message}}"

Primary Intent: [intent.category]
Confidence: [0-100]%

Entities Extracted:
- task_title: "[extracted title]"
- due_date: "[extracted date]"
- priority: "[extracted priority]"

Suggested Action:
[Tool/command to invoke with parameters]

Ambiguities:
[List any unclear elements requiring clarification]
```
