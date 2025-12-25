---
name: event.dlq
description: Manage dead letter queue for failed events
arguments:
  - name: action
    description: Action to perform (list|retry|purge|inspect)
    required: true
  - name: event_id
    description: Specific event ID for retry/inspect
    required: false
  - name: filter
    description: Filter criteria for list/purge
    required: false
agent: event-notification-agent
---

# Event DLQ Management Skill

Manage the dead letter queue for failed events.

## DLQ Actions

### List Failed Events
View events in the DLQ with failure details.

### Retry Events
Reprocess failed events with optional modifications.

### Purge Events
Remove events from DLQ (with confirmation).

### Inspect Event
View detailed information about a specific failed event.

## Event Failure Record

```json
{
  "dlq_id": "uuid",
  "original_event": { ... },
  "failure_reason": "string",
  "failure_timestamp": "ISO-8601",
  "retry_count": 3,
  "last_retry": "ISO-8601",
  "source_topic": "string",
  "consumer_group": "string"
}
```

## Output

### List
```
DEAD LETTER QUEUE
=================
Total Events: [count]
Oldest: [timestamp]
Newest: [timestamp]

Events:
1. [event_id] | [type] | [failure_reason] | [retry_count]
2. [event_id] | [type] | [failure_reason] | [retry_count]
...

Actions:
> event.dlq action=retry event_id=[id]
> event.dlq action=purge older_than=7d
```

### Retry
```
RETRY RESULT
============
Event: [event_id]
Original Failure: [reason]
Retry Attempt: [n]

Status: [SUCCESS/FAILED]
{{success ? "Event reprocessed successfully" : "Failure: [new error]"}}
```
