---
name: notification-skill
description: Implements reminder and notification scheduling for todo tasks using Dapr Cron bindings and Kafka subscriptions. Use when implementing reminders, scheduling notifications, ensuring idempotent delivery, preventing duplicates, or delivering notifications through various channels.
allowed-tools: Read, Write, Edit, Bash
user-invocable: false
---

# Notification Skill

## Purpose

This Skill helps implement a robust notification system for task reminders. It ensures:
- Reliable notification scheduling via Dapr Cron and Kafka
- Idempotent notification delivery (no duplicates)
- Support for multiple notification channels
- Graceful handling of scheduling failures

## When to Use This Skill

Use this Skill when:
- Implementing reminder scheduling for tasks with due dates
- Setting up Dapr Cron bindings or Kafka consumers for event-driven notifications
- Implementing idempotency controls to prevent duplicate notifications
- Adding notification delivery channels (email, push, in-app)
- Debugging missing or duplicate notifications
- Testing the notification delivery pipeline

## Core Patterns

### 1. Notification Architecture

```
Event Source (task_created, task_updated)
    ↓
Notification Service (subscribes to events)
    ↓
Scheduler (Dapr Cron or Kafka)
    ↓
Notification Delivery (multiple channels)
    ↓
Idempotency Check (prevent duplicates)
    ↓
Delivery Attempt (with retry logic)
```

### 2. Dapr Cron Binding Setup

Use Dapr Cron for scheduled reminders:

```python
# Schedule a reminder for task due date
@app.post("/dapr/reminders/{task_id}")
async def schedule_reminder(task_id: str, due_date: datetime):
    # Create Dapr scheduled reminder
    # Fire notification at due_date
    # Track notification state in database
```

### 3. Kafka Event Subscription

Subscribe to task events and trigger notifications:

```python
# Kafka consumer pattern
async def consume_task_events():
    # Listen for task_created, task_updated events
    # Extract reminder preferences from event
    # Schedule notification based on task details
    # Log notification scheduling decision
```

### 4. Idempotency Implementation

Prevent duplicate notifications using idempotency keys:

```python
# Idempotency pattern
{
    "notification_id": "uuid (idempotency key)",
    "task_id": "uuid",
    "user_id": "uuid",
    "scheduled_time": "datetime",
    "delivery_status": "pending | delivered | failed",
    "delivery_attempts": 0,
    "last_attempt_time": null,
    "created_at": "datetime"
}
```

## Implementation Checklist

- [ ] Create notification scheduling service
- [ ] Implement Dapr Cron binding configuration
- [ ] Set up Kafka consumer for task events
- [ ] Create notification repository with idempotency tracking
- [ ] Implement multiple notification channels
- [ ] Add retry logic with exponential backoff
- [ ] Create notification templates
- [ ] Implement preference-based filtering (user notification settings)
- [ ] Add metrics for notification delivery rates
- [ ] Set up alerting for failed notifications
- [ ] Test end-to-end notification flow
- [ ] Document notification channel setup

## Key Considerations

- **Idempotency Keys**: Store and check notification_id before sending
- **Channel Selection**: Support multiple channels (email, push, in-app)
- **User Preferences**: Respect user notification preferences
- **Timing**: Handle timezone-aware reminder scheduling
- **Retry Strategy**: Use exponential backoff (1s, 2s, 4s, 8s, max 5 attempts)
- **Observability**: Log all notification events (scheduled, delivered, failed)
- **State Tracking**: Update notification status in database after each attempt
- **Error Handling**: Distinguish between retryable and non-retryable failures

## Notification Delivery Channels

### Email
- Use task due date and user preferences
- Include task details in email body
- Handle unsubscribe preferences

### Push Notifications
- Require user opt-in
- Include action buttons (complete, snooze)
- Handle delivery token management

### In-App Notifications
- Store in notification center
- Link to task for quick access
- Mark as read when user views
