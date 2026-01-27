# Notification Service Specification

## Overview

The Notification Service is a stateless Kafka consumer that processes reminder events and delivers notifications to users. Initially, notifications are logged to console with the architecture supporting future channels (push, email, SMS).

## Service Identity

| Attribute | Value |
|-----------|-------|
| Service Name | notification-service |
| Dapr App ID | notification-service |
| Port | 8001 |
| Replicas | 2 (for HA) |

---

## Responsibilities

1. Consume reminder events from `reminders` Kafka topic
2. Validate and parse reminder event data
3. Deliver notification (console/log initially)
4. Track delivered notifications to prevent duplicates
5. Handle errors gracefully with retry logic

---

## Inputs

### Kafka Topic Subscription

**Topic**: `reminders`
**Consumer Group**: `notification-service-group`
**Subscription via Dapr**: `/dapr/subscribe` endpoint

### Reminder Event Structure

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

---

## Outputs

### Console Notification (Initial Implementation)

```
[REMINDER] User: {user_id} | Task: {title} | Due: {due_at}
Message: "{title}" is due in {time_until_due}
```

### Future Notification Channels

| Channel | Status | Description |
|---------|--------|-------------|
| Console/Log | Phase 5 | Log to stdout |
| WebSocket | Future | Real-time browser notification |
| Push Notification | Future | Mobile/browser push |
| Email | Future | Email delivery |
| SMS | Future | Text message |

---

## Processing Logic

### Event Processing Flow

```
1. Receive event from Dapr Pub/Sub
2. Validate event schema
3. Check idempotency (already processed?)
   - If yes: ACK and skip
   - If no: continue
4. Extract notification details
5. Calculate time until due
6. Format notification message
7. Deliver notification (log)
8. Record event_id as processed
9. ACK message to Dapr
```

### Idempotency Implementation

Track processed events to prevent duplicate notifications:

**Option A: In-Memory (Development)**
```
processed_events = Set()

if event_id in processed_events:
    return ACK  # Skip duplicate

# Process...
processed_events.add(event_id)
```

**Option B: Dapr State Store (Production)**
```
key = f"notification:processed:{event_id}"
exists = dapr_state.get(key)

if exists:
    return ACK  # Skip duplicate

# Process...
dapr_state.save(key, {"processed_at": now}, ttl=86400)  # 24h TTL
```

### Time Calculation

```
time_until_due = due_at - current_time

if time_until_due > 0:
    message = f"'{title}' is due in {humanize(time_until_due)}"
else:
    message = f"'{title}' is overdue by {humanize(abs(time_until_due))}"
```

---

## API Endpoints

### Health Check

**GET** `/health`

```json
{
  "status": "healthy",
  "service": "notification-service",
  "kafka_connected": true,
  "uptime_seconds": 3600
}
```

### Dapr Subscription Declaration

**GET** `/dapr/subscribe`

```json
[
  {
    "pubsubname": "kafka-pubsub",
    "topic": "reminders",
    "route": "/events/reminder"
  }
]
```

### Event Handler

**POST** `/events/reminder`

Receives CloudEvents from Dapr Pub/Sub.

**Request Body** (CloudEvents format):
```json
{
  "specversion": "1.0",
  "type": "reminder.event",
  "source": "reminder-cron",
  "id": "event-uuid",
  "data": {
    "event_id": "...",
    "user_id": "...",
    "task_id": 123,
    "title": "...",
    "due_at": "..."
  }
}
```

**Response**:
- `200 OK` - Event processed successfully
- `400 Bad Request` - Invalid event format
- `500 Internal Server Error` - Processing failed (Dapr will retry)

---

## Error Handling

### Validation Errors

| Error | Action |
|-------|--------|
| Missing required field | Log error, return 400, skip message |
| Invalid date format | Log error, return 400, skip message |
| Unknown event version | Log warning, attempt processing |

### Processing Errors

| Error | Action |
|-------|--------|
| State store unavailable | Retry 3 times, then process anyway (risk duplicate) |
| Notification delivery failed | Log error, return 500 (Dapr retries) |

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

The Notification Service maintains no in-process state:

1. **No persistent connections**: Each request is independent
2. **No session state**: User context from event only
3. **Idempotency via external store**: Dapr State or Redis
4. **Horizontally scalable**: Multiple replicas share load

### Scaling Behavior

- Kafka partitions distribute load across replicas
- Each replica processes different partitions
- Consumer group rebalancing on scale up/down
- No coordination required between replicas

---

## Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| DAPR_HTTP_PORT | Dapr sidecar port | 3500 |
| APP_PORT | Service port | 8001 |
| LOG_LEVEL | Logging verbosity | INFO |
| PUBSUB_NAME | Dapr pubsub component | kafka-pubsub |
| STATE_STORE_NAME | Dapr state component | statestore |

### Dapr Configuration

Service requires these Dapr components:
- `kafka-pubsub` - For subscribing to reminders topic
- `statestore` - For idempotency tracking (optional in dev)

---

## Deployment

### Resource Requirements

| Resource | Request | Limit |
|----------|---------|-------|
| CPU | 100m | 500m |
| Memory | 128Mi | 256Mi |

### Liveness Probe

```yaml
livenessProbe:
  httpGet:
    path: /health
    port: 8001
  initialDelaySeconds: 10
  periodSeconds: 30
```

### Readiness Probe

```yaml
readinessProbe:
  httpGet:
    path: /health
    port: 8001
  initialDelaySeconds: 5
  periodSeconds: 10
```

---

## Testing Scenarios

### Unit Tests

| Test | Description |
|------|-------------|
| test_valid_event_processing | Valid reminder event processes correctly |
| test_duplicate_event_skipped | Same event_id not processed twice |
| test_invalid_event_rejected | Malformed event returns 400 |
| test_time_calculation | Time until due calculated correctly |

### Integration Tests

| Test | Description |
|------|-------------|
| test_kafka_consumption | Service receives events from Kafka |
| test_dapr_state_idempotency | Duplicate check works with state store |
| test_concurrent_events | Multiple events processed correctly |

### Load Tests

| Test | Description |
|------|-------------|
| test_throughput | Process 100 events/second |
| test_latency | p99 latency < 500ms |

---

## Monitoring

### Metrics

| Metric | Type | Description |
|--------|------|-------------|
| notifications_processed_total | Counter | Total events processed |
| notifications_delivered_total | Counter | Successfully delivered |
| notifications_skipped_total | Counter | Duplicates skipped |
| notifications_failed_total | Counter | Processing failures |
| notification_latency_ms | Histogram | Processing time |

### Alerts

| Alert | Condition | Severity |
|-------|-----------|----------|
| HighFailureRate | failures > 10/min | Warning |
| ConsumerLag | lag > 1000 | Warning |
| ServiceDown | health check fails | Critical |

### Logs

Structured JSON logging:
```json
{
  "timestamp": "2026-01-17T08:45:00Z",
  "level": "INFO",
  "service": "notification-service",
  "event_id": "uuid",
  "user_id": "hashed-uuid",
  "task_id": 123,
  "action": "notification_delivered",
  "latency_ms": 50
}
```
