# Recurring Task Service Specification

## Overview

The Recurring Task Service is a stateless Kafka consumer that listens for task completion events and automatically creates the next instance of recurring tasks. This enables hands-free task scheduling for daily, weekly, and monthly patterns.

## Service Identity

| Attribute | Value |
|-----------|-------|
| Service Name | recurring-task-service |
| Dapr App ID | recurring-task-service |
| Port | 8002 |
| Replicas | 2 (for HA) |

---

## Responsibilities

1. Consume task events from `task-events` Kafka topic
2. Filter for `task_completed` event types
3. Check if completed task has a recurring rule
4. Calculate next occurrence date based on rule
5. Create new task instance in database
6. Publish `task_created` event for the new task
7. Ensure idempotent processing

---

## Inputs

### Kafka Topic Subscription

**Topic**: `task-events`
**Consumer Group**: `recurring-task-service-group`
**Filter**: Only process events where `event_type = "completed"`

### Task Completed Event Structure

```json
{
  "event_id": "uuid-v4",
  "event_type": "completed",
  "timestamp": "2026-01-17T10:30:00Z",
  "user_id": "user-uuid",
  "task_id": 123,
  "task_data": {
    "id": 123,
    "title": "Morning standup",
    "description": "Daily team sync",
    "completed": true,
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

---

## Outputs

### New Task Creation

Create a new task in the database with:

| Field | Value |
|-------|-------|
| title | Same as completed task |
| description | Same as completed task |
| completed | false |
| priority | Same as completed task |
| tags | Same as completed task |
| due_at | Calculated next occurrence |
| remind_at | Calculated based on original offset |
| recurring_rule | Same as completed task |
| user_id | Same as completed task |

### Task Created Event

Publish to `task-events` topic:

```json
{
  "event_id": "new-uuid-v4",
  "event_type": "created",
  "timestamp": "2026-01-17T10:30:05Z",
  "user_id": "user-uuid",
  "task_id": 124,
  "task_data": {
    "id": 124,
    "title": "Morning standup",
    "description": "Daily team sync",
    "completed": false,
    "priority": "high",
    "tags": ["work", "daily"],
    "due_at": "2026-01-18T09:00:00Z",
    "remind_at": "2026-01-18T08:45:00Z",
    "recurring_rule": "daily",
    "created_at": "2026-01-17T10:30:05Z",
    "updated_at": "2026-01-17T10:30:05Z"
  },
  "metadata": {
    "source": "recurring-task-service",
    "version": "1.0"
  }
}
```

---

## Processing Logic

### Event Processing Flow

```
1. Receive event from Dapr Pub/Sub
2. Filter: Is event_type == "completed"?
   - If no: ACK and skip
   - If yes: continue
3. Check: Does task have recurring_rule?
   - If no: ACK and skip
   - If yes: continue
4. Check idempotency (already processed this event?)
   - If yes: ACK and skip
   - If no: continue
5. Calculate next due_at based on recurring_rule
6. Calculate next remind_at (preserve original offset)
7. Create new task in database via Dapr Service Invocation
8. Publish task_created event via Dapr Pub/Sub
9. Record event_id as processed
10. ACK message to Dapr
```

### Recurring Rule Calculation

**Daily**
```
next_due_at = original_due_at + 1 day
```

**Weekly**
```
next_due_at = original_due_at + 7 days
```

**Monthly**
```
next_due_at = original_due_at + 1 month
# Handle month-end edge cases:
# - Jan 31 + 1 month = Feb 28/29
# - Use last day of month if original day doesn't exist
```

### Reminder Offset Preservation

```
if original_remind_at and original_due_at:
    offset = original_due_at - original_remind_at
    next_remind_at = next_due_at - offset
else:
    next_remind_at = None
```

### Example Calculations

| Original Due | Rule | Next Due |
|--------------|------|----------|
| 2026-01-17 09:00 | daily | 2026-01-18 09:00 |
| 2026-01-17 09:00 | weekly | 2026-01-24 09:00 |
| 2026-01-17 09:00 | monthly | 2026-02-17 09:00 |
| 2026-01-31 09:00 | monthly | 2026-02-28 09:00 |

---

## API Endpoints

### Health Check

**GET** `/health`

```json
{
  "status": "healthy",
  "service": "recurring-task-service",
  "kafka_connected": true,
  "database_connected": true,
  "uptime_seconds": 3600
}
```

### Dapr Subscription Declaration

**GET** `/dapr/subscribe`

```json
[
  {
    "pubsubname": "kafka-pubsub",
    "topic": "task-events",
    "route": "/events/task"
  }
]
```

### Event Handler

**POST** `/events/task`

Receives CloudEvents from Dapr Pub/Sub.

**Response**:
- `200 OK` - Event processed (or skipped if not applicable)
- `400 Bad Request` - Invalid event format
- `500 Internal Server Error` - Processing failed (Dapr will retry)

---

## Database Interaction

### Task Creation via Dapr Service Invocation

Instead of direct database access, use Dapr to call the backend API:

```
POST http://localhost:3500/v1.0/invoke/chat-backend/method/api/internal/tasks

Body:
{
  "user_id": "user-uuid",
  "title": "Morning standup",
  "description": "Daily team sync",
  "priority": "high",
  "tags": ["work", "daily"],
  "due_at": "2026-01-18T09:00:00Z",
  "remind_at": "2026-01-18T08:45:00Z",
  "recurring_rule": "daily"
}
```

This maintains:
- Single source of truth for task creation
- Proper validation in backend
- Automatic event publishing from backend

### Alternative: Direct Database via Dapr State

For performance, could use Dapr State Store directly:

```
POST http://localhost:3500/v1.0/state/statestore

Body:
[{
  "key": "task:user-uuid:124",
  "value": { ... task data ... }
}]
```

**Recommendation**: Use Service Invocation for consistency with existing backend logic.

---

## Idempotency Implementation

### Deduplication Key

```
dedup_key = f"recurring:processed:{event_id}"
```

### Processing Check

```
# Check if already processed
exists = await dapr_state.get(dedup_key)
if exists:
    log.info(f"Skipping duplicate event {event_id}")
    return ACK

# Process event...

# Mark as processed (24h TTL)
await dapr_state.save(dedup_key, {"processed_at": now}, ttl=86400)
```

### Edge Cases

| Scenario | Handling |
|----------|----------|
| Service crash mid-processing | On restart, event redelivered and processed |
| Event processed but not marked | May create duplicate task (acceptable, user can delete) |
| State store unavailable | Log warning, process anyway (risk duplicate) |

---

## Error Handling

### Event Validation Errors

| Error | Action |
|-------|--------|
| Missing event_type | Log error, return 400 |
| Invalid recurring_rule | Log warning, skip event |
| Missing task_data | Log error, return 400 |

### Processing Errors

| Error | Action |
|-------|--------|
| Database unavailable | Return 500, Dapr retries |
| Task creation failed | Return 500, Dapr retries |
| Event publish failed | Log error, task still created |

### Retry Configuration

```yaml
retryPolicy:
  maxRetries: 3
  backoffInitialDelay: 1s
  backoffMultiplier: 2
  backoffMaxDelay: 10s
```

---

## Stateless Guarantees

1. **No in-memory state**: All state in external stores
2. **Event-driven**: Reacts to events, doesn't poll
3. **Horizontally scalable**: Multiple replicas via Kafka partitions
4. **Crash recovery**: Kafka redelivers unacknowledged events

---

## Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| DAPR_HTTP_PORT | Dapr sidecar port | 3500 |
| APP_PORT | Service port | 8002 |
| LOG_LEVEL | Logging verbosity | INFO |
| PUBSUB_NAME | Dapr pubsub component | kafka-pubsub |
| STATE_STORE_NAME | Dapr state component | statestore |
| BACKEND_APP_ID | Backend Dapr app ID | chat-backend |

---

## Deployment

### Resource Requirements

| Resource | Request | Limit |
|----------|---------|-------|
| CPU | 100m | 500m |
| Memory | 128Mi | 256Mi |

### Probes

```yaml
livenessProbe:
  httpGet:
    path: /health
    port: 8002
  initialDelaySeconds: 10
  periodSeconds: 30

readinessProbe:
  httpGet:
    path: /health
    port: 8002
  initialDelaySeconds: 5
  periodSeconds: 10
```

---

## Testing Scenarios

### Unit Tests

| Test | Description |
|------|-------------|
| test_daily_recurrence | Next day calculated correctly |
| test_weekly_recurrence | Next week calculated correctly |
| test_monthly_recurrence | Next month calculated correctly |
| test_month_end_handling | Feb 28/29 edge case handled |
| test_reminder_offset | Reminder offset preserved |
| test_non_recurring_skipped | Events without rule skipped |
| test_non_completed_skipped | Non-completed events skipped |

### Integration Tests

| Test | Description |
|------|-------------|
| test_full_flow | Complete → new task created → event published |
| test_idempotency | Same event processed only once |
| test_service_invocation | Backend called successfully |

### End-to-End Tests

| Test | Description |
|------|-------------|
| test_user_completes_recurring | User completes task, sees new one |
| test_chain_recurrence | Multiple completions create chain |

---

## Monitoring

### Metrics

| Metric | Type | Description |
|--------|------|-------------|
| recurring_events_received_total | Counter | Total task events received |
| recurring_events_processed_total | Counter | Events that triggered recurrence |
| recurring_events_skipped_total | Counter | Non-recurring/non-completed skipped |
| recurring_tasks_created_total | Counter | New tasks created |
| recurring_processing_latency_ms | Histogram | Processing time |
| recurring_errors_total | Counter | Processing failures |

### Alerts

| Alert | Condition | Severity |
|-------|-----------|----------|
| HighFailureRate | failures > 5/min | Warning |
| TaskCreationFailing | creation_errors > 0 for 5min | Critical |
| ConsumerLag | lag > 500 | Warning |

### Logs

```json
{
  "timestamp": "2026-01-17T10:30:05Z",
  "level": "INFO",
  "service": "recurring-task-service",
  "event_id": "uuid",
  "original_task_id": 123,
  "new_task_id": 124,
  "recurring_rule": "daily",
  "action": "recurring_task_created",
  "latency_ms": 150
}
```
