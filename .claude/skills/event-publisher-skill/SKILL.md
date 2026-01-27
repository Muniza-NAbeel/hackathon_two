---
name: event-publisher-skill
description: Implements event publishing logic for Todo domain events including task_created, task_updated, task_completed, and task_deleted. Use when implementing or reviewing event publishing, validating event schemas, implementing Kafka/Dapr event emission, or ensuring event-driven architecture patterns.
allowed-tools: Read, Write, Edit, Bash
user-invocable: false
---

# Event Publisher Skill

## Purpose

This Skill helps implement robust event publishing for the Todo domain. It ensures:
- Consistent event schema validation across all Todo lifecycle events
- Proper event emission to message brokers (Kafka/Dapr)
- Error handling and retry logic
- Idempotent event publishing

## When to Use This Skill

Use this Skill when:
- Creating new Todo lifecycle event endpoints (POST /todos, PATCH /todos/{id}, etc.)
- Implementing event publishers for task_created, task_updated, task_completed, task_deleted
- Reviewing event schemas for consistency
- Debugging event delivery or missing events
- Adding retry logic or error handling for event publishing

## Core Patterns

### 1. Event Schema Structure

All Todo events follow this pattern:

```python
# Event schema pattern
{
    "event_id": "uuid",
    "event_type": "task_created | task_updated | task_completed | task_deleted",
    "timestamp": "ISO-8601",
    "user_id": "uuid",
    "task_id": "uuid",
    "data": {
        # Event-specific payload
    },
    "version": "1.0"
}
```

### 2. Event Publisher Implementation

When implementing event publishing:
1. Create event payload from Todo state change
2. Validate against schema (use Pydantic models)
3. Emit to Kafka/Dapr with proper partition/topic routing
4. Handle failures with exponential backoff
5. Log event emission for observability

### 3. Event Types and Schemas

**task_created**: Emitted when a new task is created
- Required fields: task_id, user_id, title, description (if provided)
- Optional fields: priority, tags, due_date, recurring

**task_updated**: Emitted when task details change
- Required fields: task_id, user_id, changed_fields (list)
- Previous and new values for changed fields

**task_completed**: Emitted when task marked complete
- Required fields: task_id, user_id, completed_at
- Optional: completion_notes

**task_deleted**: Emitted when task is deleted
- Required fields: task_id, user_id, deleted_at
- Optional: deletion_reason

## Implementation Checklist

- [ ] Define all event schemas as Pydantic models
- [ ] Implement event builder with validation
- [ ] Create publisher service with retry logic
- [ ] Add proper error handling and logging
- [ ] Implement idempotency keys for deduplication
- [ ] Configure Kafka topic/partition strategy
- [ ] Add metrics for event emission success/failure
- [ ] Test event delivery with message broker
- [ ] Document event versioning strategy

## Key Considerations

- **Idempotency**: Use event_id to prevent duplicate event processing downstream
- **Ordering**: Use task_id as partition key to maintain event ordering per task
- **Retention**: Configure message broker retention per event type
- **Versioning**: Include version field for schema evolution
- **Monitoring**: Emit metrics for event publishing latency and error rates
