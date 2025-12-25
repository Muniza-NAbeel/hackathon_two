---
name: event.publish
description: Publish events to Kafka topics
arguments:
  - name: topic
    description: Target Kafka topic
    required: true
  - name: event_type
    description: Event type (reminder|recurring|audit)
    required: true
  - name: payload
    description: Event payload (JSON)
    required: true
agent: event-notification-agent
---

# Event Publish Skill

Publish events to Kafka topics.

## Event Types

### Reminder Event
```json
{
  "eventId": "uuid",
  "eventType": "reminder.triggered",
  "timestamp": "ISO-8601",
  "payload": {
    "reminderId": "uuid",
    "userId": "string",
    "taskId": "uuid",
    "scheduledTime": "ISO-8601",
    "channels": ["push", "email"],
    "message": "string"
  }
}
```

### Recurring Task Event
```json
{
  "eventId": "uuid",
  "eventType": "task.recurring.created",
  "timestamp": "ISO-8601",
  "payload": {
    "taskId": "uuid",
    "recurrenceRule": "RRULE:FREQ=WEEKLY",
    "nextExecutionTime": "ISO-8601",
    "occurrenceNumber": 1
  }
}
```

### Audit Event
```json
{
  "eventId": "uuid",
  "eventType": "audit.action",
  "timestamp": "ISO-8601",
  "payload": {
    "actor": "user-id",
    "action": "task.created",
    "entityType": "task",
    "entityId": "uuid",
    "changes": {}
  }
}
```

## Publish Process

1. **Validate** event structure
2. **Enrich** with standard envelope fields
3. **Serialize** to configured format
4. **Publish** with appropriate acks
5. **Confirm** delivery

## Output

```
EVENT PUBLISHED
===============
Topic: {{topic}}
Partition: [assigned partition]
Offset: [message offset]

Event:
  ID: [uuid]
  Type: {{event_type}}
  Timestamp: [ISO-8601]

Delivery: CONFIRMED
Latency: [ms]
```
