---
name: memory.cleanup
description: Clean up old conversation data based on retention policy
arguments:
  - name: older_than
    description: Delete conversations older than (e.g., "30d", "6m", "1y")
    required: true
  - name: dry_run
    description: Preview what would be deleted
    required: false
  - name: archive
    description: Archive instead of delete
    required: false
agent: conversation-memory-manager
---

# Memory Cleanup Skill

Clean up old conversation data.

## Cleanup Options

### Age-Based Cleanup
Delete or archive conversations older than specified period.

### Size-Based Cleanup
Remove oldest conversations when storage limit reached.

### User-Specific Cleanup
Clean up data for specific user account.

## Cleanup Process

1. **Identify** conversations matching criteria
2. **Preview** affected data (count, size)
3. **Confirm** with user (if not dry_run)
4. **Archive** or **Delete** data
5. **Update** indexes and statistics
6. **Report** cleanup results

## Output

```
MEMORY CLEANUP
==============
Criteria: older_than={{older_than}}
Mode: {{dry_run ? "DRY RUN" : archive ? "ARCHIVE" : "DELETE"}}

Affected Conversations: [count]
Total Messages: [count]
Storage to Free: [size]

Preview:
1. [Session Title] - [date] - [message count] messages
2. [Session Title] - [date] - [message count] messages
...

{{dry_run ?
  "Run without --dry_run to execute cleanup" :
  "Cleanup complete. [X] conversations removed."
}}

Remaining Storage: [size] / [limit]
```
