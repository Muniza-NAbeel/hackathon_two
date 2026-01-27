# Kafka Events Specification

## Overview

This specification defines the Kafka topics, event schemas, and messaging patterns for Phase 5 event-driven architecture.

## Kafka Topics

### Topic: `task-events`

**Purpose**: All task CRUD operation events
**Producers**: Chat API (MCP Tools via Dapr)
**Consumers**: Recurring Task Service, Audit Service (future)
**Retention**: 7 days
**Partitions**: 3 (partitioned by user_id)

### Topic: `reminders`

**Purpose**: Scheduled reminder triggers
**Producers**: Chat API (when due date/reminder set), Dapr Cron Binding
**Consumers**: Notification Service
**Retention**: 1 day
**Partitions**: 3 (partitioned by user_id)

### Topic: `task-updates`

**Purpose**: Real-time client synchronization (future)
**Producers**: Chat API
**Consumers**: WebSocket Service (future)
**Retention**: 1 hour
**Partitions**: 3 (partitioned by user_id)

---

## Event Schemas

### Task Event Schema

Published to `task-events` topic for all task operations.

```json
{
  "event_id": "uuid-v4",
  "event_type": "created | updated | completed | deleted",
  "timestamp": "2026-01-17T10:30:00Z",
  "user_id": "user-uuid",
  "task_id": 123,
  "task_data": {
    "id": 123,
    "title": "Morning standup",
    "description": "Daily team sync",
    "completed": false,
    "priority": "high",
    "tags": ["work", "daily"],
    "due_at": "2026-01-17T09:00:00Z",
    "remind_at": "2026-01-17T08:45:00Z",
    "recurring_rule": "daily",
    "created_at": "2026-01-15T10:00:00Z",
    "updated_at": "2026-01-17T10:30:00Z"
  },
  "metadata": {
    "source": "chat-api",
    "version": "1.0"
  }
}
```

#### Field Definitions

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| event_id | string (UUID) | Yes | Unique identifier for this event |
| event_type | enum | Yes | One of: created, updated, completed, deleted |
| timestamp | ISO 8601 datetime | Yes | When the event occurred |
| user_id | string (UUID) | Yes | Owner of the task |
| task_id | integer | Yes | Database ID of the task |
| task_data | object | Yes | Full task object at time of event |
| metadata.source | string | Yes | Service that produced the event |
| metadata.version | string | Yes | Schema version for compatibility |

#### Event Type Specifics

**task_created**
- Published when a new task is added
- task_data contains full new task

**task_updated**
- Published when task fields are modified
- task_data contains updated task state
- Consider adding `changed_fields` array for optimization

**task_completed**
- Published when task is marked complete
- Triggers Recurring Task Service if recurring_rule present
- task_data.completed = true

**task_deleted**
- Published when task is removed
- task_data contains last known state before deletion

---

### Reminder Event Schema

Published to `reminders` topic for notification triggers.

```json
{
  "event_id": "uuid-v4",
  "timestamp": "2026-01-17T08:45:00Z",
  "user_id": "user-uuid",
  "task_id": 123,
  "title": "Morning standup",
  "description": "Daily team sync",
  "due_at": "2026-01-17T09:00:00Z",
  "remind_at": "2026-01-17T08:45:00Z",
  "reminder_type": "before_due",
  "metadata": {
    "source": "reminder-cron",
    "version": "1.0"
  }
}
```

#### Field Definitions

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| event_id | string (UUID) | Yes | Unique identifier for deduplication |
| timestamp | ISO 8601 datetime | Yes | When reminder was triggered |
| user_id | string (UUID) | Yes | User to notify |
| task_id | integer | Yes | Related task ID |
| title | string | Yes | Task title for notification |
| description | string | No | Task description |
| due_at | ISO 8601 datetime | Yes | When task is due |
| remind_at | ISO 8601 datetime | Yes | When reminder was scheduled |
| reminder_type | enum | Yes | Type: before_due, overdue |
| metadata.source | string | Yes | Service that produced event |

---

### Task Update Event Schema (Future)

For real-time client synchronization.

```json
{
  "event_id": "uuid-v4",
  "timestamp": "2026-01-17T10:30:00Z",
  "user_id": "user-uuid",
  "action": "sync",
  "tasks": [
    {
      "id": 123,
      "title": "Updated task",
      "completed": true
    }
  ],
  "metadata": {
    "source": "chat-api",
    "version": "1.0"
  }
}
```

---

## Event Flow Diagrams

### Task Creation Flow

```
User Request → Chat API → MCP add_task Tool
                              ↓
                         Save to DB
                              ↓
                    Publish task_created to Kafka
                              ↓
                    (Consumers process async)
```

### Task Completion with Recurring

```
User Request → Chat API → MCP complete_task Tool
                              ↓
                         Update DB (completed=true)
                              ↓
                    Publish task_completed to Kafka
                              ↓
              ┌───────────────┴───────────────┐
              ↓                               ↓
    Recurring Task Service              (Other Consumers)
              ↓
    Check recurring_rule
              ↓ (if rule exists)
    Calculate next due_at
              ↓
    Create new task in DB
              ↓
    Publish task_created to Kafka
```

### Reminder Flow

```
Dapr Cron Binding (every 5 min) → Backend /reminder-cron endpoint
                                          ↓
                                  Query tasks where:
                                  - remind_at <= now
                                  - reminder_sent = false
                                          ↓
                                  For each task:
                                  - Publish reminder event
                                  - Mark reminder_sent = true
                                          ↓
                              Notification Service consumes
                                          ↓
                                  Log/Display reminder
                                          ↓
                                  Track as delivered (idempotent)
```

---

## Partitioning Strategy

All topics use `user_id` as the partition key to ensure:

1. **Ordering**: Events for a single user processed in order
2. **Locality**: User's events go to same partition
3. **Parallelism**: Different users processed concurrently

### Partition Key Format

```
partition_key = user_id (UUID string)
```

---

## Error Handling

### Producer Errors

| Error | Handling |
|-------|----------|
| Kafka unavailable | Retry with exponential backoff (3 attempts) |
| Serialization error | Log error, fail request, alert |
| Timeout | Retry once, then fail with error to user |

### Consumer Errors

| Error | Handling |
|-------|----------|
| Deserialization error | Log, skip message, send to DLQ |
| Processing error | Retry 3 times, then send to DLQ |
| Database error | Retry with backoff, alert if persistent |

### Dead Letter Queue (DLQ)

Failed messages after retries go to:
- `task-events-dlq`
- `reminders-dlq`

DLQ messages include original message + error details for debugging.

---

## Idempotency

### Producer Idempotency

- Each event has unique `event_id` (UUID v4)
- Dapr Pub/Sub handles producer retries

### Consumer Idempotency

Consumers must track processed `event_id` values:

1. Before processing, check if `event_id` already processed
2. If yes, skip (already handled)
3. If no, process and record `event_id` as processed

Storage options:
- In-memory set (loses on restart)
- Database table `processed_events(event_id, processed_at)`
- Redis set with TTL (recommended)

---

## Schema Evolution

### Versioning Strategy

- Schema version in `metadata.version`
- Consumers must handle unknown fields gracefully
- Breaking changes require new topic or version negotiation

### Backward Compatibility Rules

1. New optional fields can be added
2. Required fields cannot be removed
3. Field types cannot be changed
4. Enum values can be added (consumers ignore unknown)

---

## Monitoring

### Key Metrics

| Metric | Description | Alert Threshold |
|--------|-------------|-----------------|
| events_published_total | Count by topic and type | N/A (baseline) |
| events_consumed_total | Count by consumer | N/A (baseline) |
| consumer_lag | Messages behind | > 1000 messages |
| processing_latency_ms | Time to process event | p99 > 5000ms |
| dlq_messages_total | Failed messages | > 10/hour |

### Logging

All events should log:
- event_id
- event_type
- user_id (hashed for privacy)
- processing_time_ms
- status (success/failure)
