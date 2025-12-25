---
name: crud.sync
description: Synchronize tasks across all interfaces (console, web, chatbot)
arguments:
  - name: direction
    description: Sync direction (push|pull|bidirectional)
    required: false
  - name: interface
    description: Target interface (console|web|chatbot|all)
    required: false
agent: todo-crud-orchestrator
---

# CRUD Sync Skill

Synchronize task data across multiple application interfaces.

## Sync Operations

### Push Sync
- Push local changes to all interfaces
- Handle conflicts with last-write-wins or merge strategy
- Update sync timestamps

### Pull Sync
- Fetch latest data from all interfaces
- Merge changes into local state
- Resolve conflicts interactively

### Bidirectional Sync
- Full two-way synchronization
- Conflict detection and resolution
- Consistency verification

## Sync Process

1. **Lock**: Acquire sync lock to prevent concurrent modifications
2. **Fetch**: Get current state from all interfaces
3. **Diff**: Calculate differences between states
4. **Merge**: Apply non-conflicting changes
5. **Resolve**: Handle conflicts (prompt user or use strategy)
6. **Push**: Propagate merged state to all interfaces
7. **Verify**: Confirm all interfaces have consistent state
8. **Unlock**: Release sync lock

## Output

```
SYNC REPORT
===========
Direction: {{direction}}
Interfaces: {{interface}}

Changes Applied:
- Console: [+X added, ~Y modified, -Z deleted]
- Web: [+X added, ~Y modified, -Z deleted]
- Chatbot: [+X added, ~Y modified, -Z deleted]

Conflicts Resolved: [count]
Sync Status: [SUCCESS/PARTIAL/FAILED]
Last Sync: [timestamp]
```
