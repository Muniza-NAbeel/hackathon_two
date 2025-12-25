---
name: event.subscribe
description: Subscribe to Kafka topics and process events
arguments:
  - name: topic
    description: Kafka topic to subscribe to
    required: true
  - name: group_id
    description: Consumer group ID
    required: true
  - name: handler
    description: Handler function or webhook URL
    required: false
agent: event-notification-agent
---

# Event Subscribe Skill

Subscribe to Kafka topics and process events.

## Subscription Configuration

### Consumer Settings
```yaml
bootstrap.servers: ${KAFKA_BROKERS}
group.id: {{group_id}}
auto.offset.reset: earliest
enable.auto.commit: false
max.poll.records: 100
```

### Topic Patterns
- Exact: `reminders.notifications`
- Wildcard: `tasks.*`
- Regex: `^audit\..*`

## Processing Flow

1. **Subscribe** to topic(s)
2. **Poll** for messages
3. **Deserialize** event payload
4. **Validate** against schema
5. **Process** with handler
6. **Commit** offset on success
7. **DLQ** on failure

## Handler Interface

```typescript
interface EventHandler {
  handle(event: Event): Promise<void>;
  onError(event: Event, error: Error): Promise<void>;
}
```

## Output

```
SUBSCRIPTION ACTIVE
===================
Topic: {{topic}}
Consumer Group: {{group_id}}
Partitions Assigned: [list]

Status: CONSUMING
Messages Processed: [count]
Current Lag: [messages behind]

Last Event:
  ID: [uuid]
  Type: [event type]
  Processed: [timestamp]

[Ctrl+C to stop subscription]
```
