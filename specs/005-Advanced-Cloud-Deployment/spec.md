# Phase 5: Advanced Cloud Deployment - Specification

## Overview

**Feature Name**: Phase 5 - Advanced Cloud Deployment
**Version**: 1.0
**Status**: Draft
**Created**: 2026-01-17
**Last Updated**: 2026-01-17

## Executive Summary

Phase 5 extends the Phase 3/4 Todo AI Chatbot with event-driven microservices architecture using Kafka and Dapr, then deploys to production-grade Kubernetes clusters. This phase transforms the monolithic chatbot into a scalable, cloud-native distributed system.

## Business Context

### Problem Statement

The current Phase 3/4 chatbot handles all operations synchronously within a single service. This limits:
- Scalability for advanced features like recurring tasks and reminders
- Decoupling of concerns (notifications, task automation)
- Production-readiness for cloud deployment

### Business Goals

1. Enable intelligent recurring task automation
2. Provide timely reminder notifications to users
3. Achieve production-grade deployment on cloud Kubernetes
4. Establish CI/CD pipeline for continuous delivery

### Success Criteria

| Criterion | Target | Measurement |
|-----------|--------|-------------|
| Recurring tasks auto-create next instance | 100% accuracy | Task completion triggers new task within 5 seconds |
| Reminder notifications delivered | 95% delivery rate | Notifications sent within 1 minute of due time |
| System handles concurrent users | 1000+ users | Load test verification |
| Deployment automation | Zero-downtime deploys | CI/CD pipeline success rate > 99% |
| Event processing latency | < 2 seconds | End-to-end event flow timing |

---

## Scope

### In Scope

**Part A: Advanced Features Enhancement**
- Priority levels (high/medium/low) for tasks
- Tags and categories for task organization
- Search by keyword functionality
- Filter by status, priority, and date
- Sort by due date, priority, or alphabetically
- Recurring tasks (daily, weekly, monthly patterns)
- Due dates with time selection
- Reminder notifications

**Part B: Event-Driven Architecture**
- Kafka topics for task events, reminders, and updates
- Event publishing from MCP tools via Dapr
- Notification Service (Kafka consumer)
- Recurring Task Service (Kafka consumer)

**Part C: Dapr Integration**
- Pub/Sub for Kafka abstraction
- State Management for conversation state
- Bindings for cron-based reminders
- Secrets Management for credentials
- Service Invocation for inter-service communication

**Part D: Local Deployment**
- Minikube cluster setup
- Dapr installation on Kubernetes
- Redpanda (local Kafka) deployment
- All services containerized and deployed

**Part E: Cloud Deployment**
- Production Kubernetes (DOKS/GKE/AKS)
- Redpanda Cloud for managed Kafka
- GitHub Actions CI/CD pipeline
- Monitoring and logging setup

### Out of Scope

- Mobile push notifications (console/log only initially)
- Email/SMS notification channels
- Multi-region deployment
- Custom recurring patterns beyond daily/weekly/monthly
- Real-time WebSocket sync (future enhancement)
- Modification of Phase 1-4 code structure

### Dependencies

| Dependency | Type | Description |
|------------|------|-------------|
| Phase 3/4 Chatbot | Internal | Existing MCP tools and chat infrastructure |
| Neon PostgreSQL | External | Existing database for tasks and conversations |
| Redpanda Cloud | External | Managed Kafka service |
| DOKS/GKE/AKS | External | Cloud Kubernetes provider |
| GitHub Actions | External | CI/CD platform |

---

## User Scenarios

### Scenario 1: Recurring Task Completion

**Actor**: Authenticated User
**Precondition**: User has a recurring daily task "Morning standup"

1. User tells chatbot "I finished my morning standup"
2. Chatbot marks task as complete via MCP tool
3. MCP tool publishes `task_completed` event to Kafka
4. Recurring Task Service consumes event
5. Service detects recurring rule (daily)
6. Service creates new task for next day
7. Service publishes `task_created` event
8. Chatbot confirms: "Great! I've marked it complete and scheduled tomorrow's standup."

**Acceptance Criteria**:
- Next recurring task created within 5 seconds
- New task has correct due date (next occurrence)
- User receives confirmation of both actions

### Scenario 2: Reminder Notification

**Actor**: Authenticated User
**Precondition**: User has task with due date and reminder set

1. User creates task "Team meeting at 2pm" with reminder 15 minutes before
2. Task stored with reminder_at timestamp
3. Dapr cron binding triggers reminder check every 5 minutes
4. Backend publishes reminder event when remind_at is reached
5. Notification Service consumes event
6. Service logs/displays reminder to user
7. User sees: "Reminder: Team meeting at 2pm in 15 minutes"

**Acceptance Criteria**:
- Reminder delivered within 1 minute of remind_at time
- No duplicate reminders for same task
- Reminder includes task title and time until due

### Scenario 3: Advanced Task Search

**Actor**: Authenticated User
**Precondition**: User has multiple tasks with various priorities and tags

1. User asks "Show me high priority work tasks due this week"
2. Chatbot parses: priority=high, tag=work, due_date=this_week
3. MCP tool queries with filters
4. Results returned sorted by due date
5. Chatbot displays filtered task list

**Acceptance Criteria**:
- Filters combine correctly (AND logic)
- Results respect user ownership
- Response within 2 seconds

---

## Functional Requirements

### FR-1: Priority Levels

| ID | Requirement | Acceptance Criteria |
|----|-------------|---------------------|
| FR-1.1 | Tasks support priority values: high, medium, low | Priority stored and retrieved correctly |
| FR-1.2 | Default priority is medium if not specified | New tasks without priority get medium |
| FR-1.3 | Users can update task priority via chatbot | "Set task X to high priority" works |
| FR-1.4 | Tasks can be filtered by priority | Filter returns only matching priorities |

### FR-2: Tags and Categories

| ID | Requirement | Acceptance Criteria |
|----|-------------|---------------------|
| FR-2.1 | Tasks support multiple tags | Task can have 0-10 tags |
| FR-2.2 | Tags are user-defined strings | Any alphanumeric tag allowed |
| FR-2.3 | Users can add/remove tags via chatbot | "Add work tag to task X" works |
| FR-2.4 | Tasks can be filtered by tag | Filter returns tasks with matching tag |

### FR-3: Search and Filter

| ID | Requirement | Acceptance Criteria |
|----|-------------|---------------------|
| FR-3.1 | Search tasks by keyword in title/description | Partial match supported |
| FR-3.2 | Filter by status (pending/completed/all) | Correct filtering |
| FR-3.3 | Filter by priority level | Correct filtering |
| FR-3.4 | Filter by due date range | Today, this week, overdue filters work |
| FR-3.5 | Combine multiple filters | AND logic applied |

### FR-4: Sorting

| ID | Requirement | Acceptance Criteria |
|----|-------------|---------------------|
| FR-4.1 | Sort by due date (ascending/descending) | Null dates handled appropriately |
| FR-4.2 | Sort by priority (high first) | Correct ordering |
| FR-4.3 | Sort alphabetically by title | Case-insensitive |
| FR-4.4 | Default sort is by due date ascending | Applied when no sort specified |

### FR-5: Recurring Tasks

| ID | Requirement | Acceptance Criteria |
|----|-------------|---------------------|
| FR-5.1 | Tasks support recurring rules: daily, weekly, monthly | Rule stored on task |
| FR-5.2 | Completing recurring task creates next instance | New task created automatically |
| FR-5.3 | Next instance due date calculated correctly | Daily=+1day, Weekly=+7days, Monthly=+1month |
| FR-5.4 | Recurring rule copied to new instance | Chain continues |
| FR-5.5 | Users can stop recurrence | "Stop recurring for task X" removes rule |

### FR-6: Due Dates and Reminders

| ID | Requirement | Acceptance Criteria |
|----|-------------|---------------------|
| FR-6.1 | Tasks support due date with time | DateTime stored correctly |
| FR-6.2 | Tasks support reminder time before due | remind_at calculated and stored |
| FR-6.3 | Reminders trigger at specified time | Notification sent within 1 minute |
| FR-6.4 | No duplicate reminders | Each reminder sent exactly once |
| FR-6.5 | Reminder includes task details | Title, due time shown |

### FR-7: Event Publishing

| ID | Requirement | Acceptance Criteria |
|----|-------------|---------------------|
| FR-7.1 | Task creation publishes task_created event | Event on Kafka within 1 second |
| FR-7.2 | Task update publishes task_updated event | Event includes changed fields |
| FR-7.3 | Task completion publishes task_completed event | Event triggers recurring logic |
| FR-7.4 | Task deletion publishes task_deleted event | Event for audit/sync |
| FR-7.5 | All events include user_id and timestamp | Required fields present |

### FR-8: Notification Service

| ID | Requirement | Acceptance Criteria |
|----|-------------|---------------------|
| FR-8.1 | Service consumes from reminders topic | Kafka consumer active |
| FR-8.2 | Service logs reminder to console | Visible in service logs |
| FR-8.3 | Service is idempotent | Same event processed once |
| FR-8.4 | Service tracks delivered reminders | Deduplication via event ID |

### FR-9: Recurring Task Service

| ID | Requirement | Acceptance Criteria |
|----|-------------|---------------------|
| FR-9.1 | Service consumes from task-events topic | Kafka consumer active |
| FR-9.2 | Service filters for task_completed events | Other events ignored |
| FR-9.3 | Service checks for recurring rule | Only processes recurring tasks |
| FR-9.4 | Service creates next task instance | Task persisted to database |
| FR-9.5 | Service publishes task_created event | Event chain continues |

---

## Non-Functional Requirements

### Performance

- Event processing latency: < 2 seconds end-to-end
- API response time: < 500ms for filtered queries
- Support 1000+ concurrent users
- Kafka throughput: 1000 events/second

### Reliability

- 99.9% uptime for core services
- Zero message loss in Kafka
- Automatic retry for failed event processing
- Graceful degradation if Kafka unavailable

### Security

- All inter-service communication via Dapr mTLS
- Secrets stored in Kubernetes secrets via Dapr
- No credentials in code or environment variables
- User data isolation maintained

### Scalability

- Horizontal scaling of all services
- Kafka partitioning for parallel processing
- Stateless services for easy replication

---

## Assumptions

1. Phase 3/4 infrastructure is stable and deployed
2. Neon PostgreSQL database is accessible from cloud
3. Users have accounts on chosen cloud provider (DO/GCP/Azure)
4. Redpanda Cloud free tier is sufficient for development
5. GitHub repository is set up for Actions

---

## Risks

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| Kafka message ordering issues | Medium | High | Use partition keys by user_id |
| Cloud provider quota limits | Low | Medium | Monitor usage, request increases |
| Dapr learning curve | Medium | Medium | Use official documentation, examples |
| CI/CD pipeline failures | Medium | Low | Comprehensive testing, rollback strategy |

---

## Related Specifications

- [Kafka Events Specification](./kafka-events.md)
- [Notification Service Specification](./notification-service.md)
- [Recurring Task Service Specification](./recurring-task-service.md)
- [Dapr Components Specification](./dapr-components.md)
- [Local Deployment Specification](./deployment-local.md)
- [Cloud Deployment Specification](./deployment-cloud.md)
- [CI/CD Pipeline Specification](./cicd-pipeline.md)
