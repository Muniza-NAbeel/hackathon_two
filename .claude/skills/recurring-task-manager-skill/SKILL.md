---
name: recurring-task-manager-skill
description: Handles recurring task automation including spawning next task instances when recurring tasks are completed, setting up recurrence rules (daily, weekly, monthly patterns), debugging recurring task generation, and validating due date calculations. Use when implementing recurring task completion handlers, configuring recurrence patterns, or verifying recurring task lifecycle.
allowed-tools: Read, Write, Edit, Bash
user-invocable: false
---

# Recurring Task Manager Skill

## Purpose

This Skill implements the recurring task system for automated task generation. It ensures:
- Correct spawning of next task instances when recurring tasks complete
- Proper handling of recurrence patterns (daily, weekly, monthly)
- Accurate due date calculations for next instances
- Event-driven task generation from completion events

## When to Use This Skill

Use this Skill when:
- Implementing task completion handlers that trigger next instance creation
- Setting up or modifying recurrence rules (daily, weekly, monthly patterns)
- Debugging issues with recurring task generation or scheduling
- Validating due date calculations for recurring tasks
- Auditing the recurring task system
- Testing recurrence patterns and edge cases

## Core Patterns

### 1. Recurring Task Model

```python
# Recurring task configuration
{
    "task_id": "uuid",
    "user_id": "uuid",
    "title": "string",
    "recurrence_rule": {
        "pattern": "daily | weekly | monthly",
        "interval": 1,  # every N days/weeks/months
        "day_of_week": "MON | TUE | WED | THU | FRI | SAT | SUN",  # for weekly
        "day_of_month": 1-31,  # for monthly
        "end_date": "datetime or null (no end)"
    },
    "created_at": "datetime",
    "completed_at": "datetime or null"
}
```

### 2. Recurrence Pattern Types

**Daily Pattern**:
- Interval: 1 = every day, 2 = every other day, etc.
- Next due date: current_due_date + interval days

**Weekly Pattern**:
- Interval: 1 = every week, 2 = every other week, etc.
- Day of week: which day(s) the task occurs
- Next due date: same day of week + interval weeks
- Handle multiple day selection (e.g., Monday and Friday)

**Monthly Pattern**:
- Interval: 1 = every month, 2 = every other month, etc.
- Day of month: fixed day (e.g., 15th) or relative (e.g., last Monday)
- Next due date: same day + interval months
- Handle month-end edge cases (Jan 31 → Feb 28/29)

### 3. Task Completion Event Handler

When a recurring task is completed:

```python
async def on_task_completed(task: Task):
    if not task.recurrence_rule:
        return  # Not recurring

    # Calculate next due date
    next_due_date = calculate_next_due_date(
        current_due_date=task.due_date,
        recurrence_rule=task.recurrence_rule
    )

    # Check if past end date
    if task.recurrence_rule.end_date and next_due_date > task.recurrence_rule.end_date:
        return  # Recurrence ended

    # Create next instance
    next_task = Task(
        user_id=task.user_id,
        title=task.title,
        description=task.description,
        due_date=next_due_date,
        priority=task.priority,
        tags=task.tags,
        recurrence_rule=task.recurrence_rule,
        parent_task_id=task.id  # Link to original
    )

    # Save to database
    db.add(next_task)
    await db.commit()

    # Publish event
    await event_publisher.publish("task_created", {
        "task_id": next_task.id,
        "user_id": task.user_id,
        "recurrence_parent_id": task.id
    })
```

### 4. Due Date Calculation Logic

Implement accurate due date calculation:

```python
def calculate_next_due_date(current_due_date: datetime,
                           recurrence_rule: RecurrenceRule) -> datetime:
    if recurrence_rule.pattern == "daily":
        return current_due_date + timedelta(days=recurrence_rule.interval)

    elif recurrence_rule.pattern == "weekly":
        # Add weeks, maintain day of week
        next_date = current_due_date + timedelta(weeks=recurrence_rule.interval)
        # Adjust to correct day of week if needed
        return next_date

    elif recurrence_rule.pattern == "monthly":
        # Add months, handle month-end edge cases
        year = current_due_date.year
        month = current_due_date.month + recurrence_rule.interval

        # Handle year rollover
        year += (month - 1) // 12
        month = ((month - 1) % 12) + 1

        # Handle day-of-month edge cases
        day = min(current_due_date.day, calendar.monthrange(year, month)[1])

        return current_due_date.replace(year=year, month=month, day=day)
```

## Implementation Checklist

- [ ] Create RecurrenceRule data model
- [ ] Implement due date calculation functions for each pattern
- [ ] Add task completion event handler
- [ ] Create next instance generation logic
- [ ] Add recurrence end date validation
- [ ] Implement timezone-aware date calculations
- [ ] Create recurring task repository queries
- [ ] Add metrics for recurring task generation
- [ ] Test all recurrence patterns and edge cases
- [ ] Handle daylight saving time transitions
- [ ] Document recurrence rule format
- [ ] Add task linking (parent/child relationships)
- [ ] Implement task chain history retrieval

## Key Considerations

- **Date Calculations**: Use timezone-aware datetime objects
- **Edge Cases**: Handle month-end (Jan 31 → Feb), leap years, DST transitions
- **Interval Flexibility**: Support every N days/weeks/months (not just 1)
- **End Dates**: Stop generating when recurrence end_date is passed
- **Task Linking**: Store parent_task_id to track recurring chains
- **Event Publishing**: Emit task_created event for new instances
- **Validation**: Validate recurrence_rule before creating recurring tasks
- **Timezone Handling**: Calculate due dates in user's timezone
- **Audit Trail**: Maintain history of recurring task instances

## Recurrence Pattern Examples

### Daily Standup (every day at 9 AM)
```python
recurrence_rule = RecurrenceRule(
    pattern="daily",
    interval=1
)
```

### Weekly Status Report (every Monday)
```python
recurrence_rule = RecurrenceRule(
    pattern="weekly",
    interval=1,
    day_of_week="MON"
)
```

### Biweekly 1-on-1 (every other week on Wednesday)
```python
recurrence_rule = RecurrenceRule(
    pattern="weekly",
    interval=2,
    day_of_week="WED"
)
```

### Monthly Review (15th of every month)
```python
recurrence_rule = RecurrenceRule(
    pattern="monthly",
    interval=1,
    day_of_month=15
)
```

### Quarterly Business Review (first Monday of quarter)
```python
# Calculate to first Monday + quarterly
recurrence_rule = RecurrenceRule(
    pattern="monthly",
    interval=3,
    day_of_week="MON"  # Requires special handling
)
```
