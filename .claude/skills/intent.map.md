---
name: intent.map
description: Map parsed intents to specific MCP tools or CLI commands
arguments:
  - name: intent
    description: Parsed intent object or natural language
    required: true
  - name: execute
    description: Execute the mapped command (default false)
    required: false
agent: chat-intent-resolver
---

# Intent Map Skill

Map intents to executable tools and commands.

## Mapping Rules

### Task Intents → Tools
| Intent | Tool | Parameters |
|--------|------|------------|
| task.create | todo.add | title, due_date, priority |
| task.list | todo.list | filter, sort |
| task.complete | todo.complete | task_id |
| task.delete | todo.delete | task_id |
| task.update | todo.update | task_id, fields |

### Workflow Intents → Skills
| Intent | Skill | Parameters |
|--------|-------|------------|
| spec.create | /sp.specify | feature_name |
| plan.create | /sp.plan | feature_name |
| task.generate | /sp.tasks | feature_name |

### System Intents → Commands
| Intent | Command |
|--------|---------|
| git.status | git status |
| git.commit | /sp.git.commit_pr |
| help | /help |

## Execution Flow

1. **Receive** parsed intent
2. **Lookup** matching tool/command
3. **Extract** required parameters
4. **Validate** all parameters present
5. **Execute** (if execute=true) or **Preview**

## Output

```
INTENT MAPPING
==============
Intent: {{intent}}

Mapped To: [Tool/Skill/Command]
Parameters:
  - param1: [value]
  - param2: [value]

{{execute ? "Executing..." : "Preview mode - add execute=true to run"}}

[Execution result or preview]
```
