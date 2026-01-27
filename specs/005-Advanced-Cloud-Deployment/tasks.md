# Tasks: Phase 5 - Advanced Cloud Deployment

**Input**: Design documents from `/specs/005-Advanced-Cloud-Deployment/`
**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/

**Tests**: Included as requested in implementation scope (Part J)

**Organization**: Tasks grouped by user story for independent implementation and testing

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (US1-US10)
- Include exact file paths in descriptions

## Path Conventions

Phase 5 uses microservices architecture:
- **Backend extensions**: `phase_5/backend/`
- **Notification Service**: `phase_5/services/notification-service/`
- **Recurring Task Service**: `phase_5/services/recurring-task-service/`
- **Dapr Components**: `phase_5/dapr/`
- **Kubernetes**: `phase_5/k8s/`
- **Helm Charts**: `phase_5/helm/`
- **CI/CD**: `phase_5/.github/workflows/`

---

## Phase 1: Setup (Project Initialization)

**Purpose**: Create Phase 5 project structure and initialize all service directories

- [ ] T001 Create phase_5 directory structure per plan.md
- [ ] T002 [P] Initialize phase_5/backend/ with Python 3.11+ pyproject.toml
- [ ] T003 [P] Initialize phase_5/services/notification-service/ with pyproject.toml
- [ ] T004 [P] Initialize phase_5/services/recurring-task-service/ with pyproject.toml
- [ ] T005 [P] Create phase_5/dapr/ directory structure (pubsub/, statestore/, bindings/)
- [ ] T006 [P] Create phase_5/k8s/ directory structure (base/, local/, cloud/)
- [ ] T007 [P] Create phase_5/helm/ directory structure
- [ ] T008 [P] Create phase_5/.github/workflows/ directory
- [ ] T009 Configure shared dependencies: FastAPI, httpx, pydantic, structlog in all services

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

### Database Migration

- [ ] T010 Create Alembic migration: add remind_at (datetime, nullable) to tasks in phase_5/backend/alembic/versions/
- [ ] T011 Create Alembic migration: add reminder_sent (boolean, default false) to tasks
- [ ] T012 Create Alembic migration: add recurrence_rule (string, nullable) to tasks
- [ ] T013 Create Alembic migration: create index on remind_at where reminder_sent=false
- [ ] T014 Create Alembic migration: create dapr_state table for PostgreSQL state store

### CloudEvents Schemas

- [ ] T015 [P] Create CloudEvents base schema in phase_5/backend/app/events/schemas.py
- [ ] T016 [P] Create TaskEvent schema (created/updated/completed/deleted) in phase_5/backend/app/events/schemas.py
- [ ] T017 [P] Create ReminderEvent schema in phase_5/backend/app/events/schemas.py

### Dapr Event Publisher

- [ ] T018 Create Dapr HTTP client wrapper in phase_5/backend/app/events/dapr_client.py
- [ ] T019 Create EventPublisher service in phase_5/backend/app/events/publisher.py
- [ ] T020 Add publish_task_event method for task lifecycle events
- [ ] T021 Add publish_reminder_event method for reminder notifications

**Checkpoint**: Foundation ready - user story implementation can now begin

---

## Phase 3: User Story 1 - Event Publishing (Priority: P1) 🎯 MVP

**Goal**: Backend publishes CloudEvents to Kafka via Dapr on all task CRUD operations

**Independent Test**: Create/update/complete/delete a task and verify events appear in Kafka topic

### Tests for User Story 1

- [ ] T022 [P] [US1] Unit test for EventPublisher in phase_5/backend/tests/unit/test_event_publisher.py
- [ ] T023 [P] [US1] Unit test for CloudEvents schema validation in phase_5/backend/tests/unit/test_event_schemas.py
- [ ] T024 [P] [US1] Integration test for task event flow in phase_5/backend/tests/integration/test_task_events.py

### Implementation for User Story 1

- [ ] T025 [US1] Integrate EventPublisher into task creation flow in phase_5/backend/app/services/task_service.py
- [ ] T026 [US1] Integrate EventPublisher into task update flow
- [ ] T027 [US1] Integrate EventPublisher into task completion flow
- [ ] T028 [US1] Integrate EventPublisher into task deletion flow
- [ ] T029 [US1] Add /dapr/subscribe endpoint in phase_5/backend/app/api/dapr.py
- [ ] T030 [US1] Add structured logging for all event publishing in phase_5/backend/app/events/publisher.py

**Checkpoint**: Task CRUD operations now publish events to Kafka

---

## Phase 4: User Story 2 - Notification Service (Priority: P1)

**Goal**: New microservice consumes reminder events and logs notifications with idempotency

**Independent Test**: Publish reminder event to Kafka, verify notification logged exactly once

### Tests for User Story 2

- [ ] T031 [P] [US2] Unit test for idempotency service in phase_5/services/notification-service/tests/unit/test_idempotency.py
- [ ] T032 [P] [US2] Unit test for reminder handler in phase_5/services/notification-service/tests/unit/test_reminder_handler.py
- [ ] T033 [P] [US2] Integration test for notification flow in phase_5/services/notification-service/tests/integration/test_notification_flow.py

### Implementation for User Story 2

- [ ] T034 [P] [US2] Create FastAPI main.py with Dapr subscription in phase_5/services/notification-service/app/main.py
- [ ] T035 [P] [US2] Create IdempotencyService using Dapr State Store in phase_5/services/notification-service/app/services/idempotency.py
- [ ] T036 [US2] Create ReminderHandler in phase_5/services/notification-service/app/handlers/reminder.py
- [ ] T037 [US2] Implement /events/reminder endpoint with idempotency check
- [ ] T038 [US2] Add /health and /ready endpoints in phase_5/services/notification-service/app/api/health.py
- [ ] T039 [US2] Add structured JSON logging with structlog
- [ ] T040 [US2] Create Dockerfile in phase_5/services/notification-service/Dockerfile
- [ ] T041 [US2] Create requirements.txt in phase_5/services/notification-service/requirements.txt

**Checkpoint**: Notification service receives and logs reminders idempotently

---

## Phase 5: User Story 3 - Recurring Task Service (Priority: P1)

**Goal**: New microservice handles task completion events and creates next recurring task instance

**Independent Test**: Complete a recurring task, verify new task created with correct next due date

### Tests for User Story 3

- [ ] T042 [P] [US3] Unit test for recurrence calculator in phase_5/services/recurring-task-service/tests/unit/test_recurrence.py
- [ ] T043 [P] [US3] Unit test for task creator service in phase_5/services/recurring-task-service/tests/unit/test_task_creator.py
- [ ] T044 [P] [US3] Integration test for recurring flow in phase_5/services/recurring-task-service/tests/integration/test_recurring_flow.py

### Implementation for User Story 3

- [ ] T045 [P] [US3] Create FastAPI main.py with Dapr subscription in phase_5/services/recurring-task-service/app/main.py
- [ ] T046 [P] [US3] Create RecurrenceCalculator in phase_5/services/recurring-task-service/app/services/recurrence.py
- [ ] T047 [P] [US3] Create TaskCreator using Dapr Service Invocation in phase_5/services/recurring-task-service/app/services/task_creator.py
- [ ] T048 [US3] Create TaskCompletedHandler in phase_5/services/recurring-task-service/app/handlers/task_completed.py
- [ ] T049 [US3] Implement /events/task endpoint filtering for task_completed
- [ ] T050 [US3] Add recurrence logic: daily (+1 day), weekly (+7 days), monthly (+1 month)
- [ ] T051 [US3] Add /health and /ready endpoints in phase_5/services/recurring-task-service/app/api/health.py
- [ ] T052 [US3] Add idempotency service reusing pattern from notification-service
- [ ] T053 [US3] Create Dockerfile in phase_5/services/recurring-task-service/Dockerfile
- [ ] T054 [US3] Create requirements.txt in phase_5/services/recurring-task-service/requirements.txt

**Checkpoint**: Recurring tasks automatically create next instance on completion

---

## Phase 6: User Story 4 - Reminder Cron (Priority: P1)

**Goal**: Backend checks for due reminders every 5 minutes via Dapr cron binding

**Independent Test**: Create task with remind_at in past, trigger cron, verify reminder event published

### Tests for User Story 4

- [ ] T055 [P] [US4] Unit test for reminder checker in phase_5/backend/tests/unit/test_reminder_checker.py
- [ ] T056 [P] [US4] Integration test for cron flow in phase_5/backend/tests/integration/test_reminder_cron.py

### Implementation for User Story 4

- [ ] T057 [US4] Create ReminderChecker service in phase_5/backend/app/services/reminder_checker.py
- [ ] T058 [US4] Implement query: tasks where remind_at <= now AND reminder_sent = false
- [ ] T059 [US4] Publish reminder event for each due task
- [ ] T060 [US4] Mark reminder_sent = true after publishing
- [ ] T061 [US4] Add /reminder-cron endpoint in phase_5/backend/app/api/cron.py
- [ ] T062 [US4] Add structured logging for cron execution

**Checkpoint**: Reminders are automatically triggered within 5 minutes of remind_at

---

## Phase 7: User Story 5 - Internal Task API (Priority: P1)

**Goal**: Backend exposes internal endpoint for service-to-service task creation

**Independent Test**: Call /api/internal/tasks from another service, verify task created

### Tests for User Story 5

- [ ] T063 [P] [US5] Contract test for internal API in phase_5/backend/tests/contract/test_internal_api.py
- [ ] T064 [P] [US5] Integration test for service invocation in phase_5/backend/tests/integration/test_internal_tasks.py

### Implementation for User Story 5

- [ ] T065 [US5] Create InternalTaskCreate schema in phase_5/backend/app/schemas/internal.py
- [ ] T066 [US5] Create /api/internal/tasks POST endpoint in phase_5/backend/app/api/internal.py
- [ ] T067 [US5] Implement task creation with source_task_id tracking
- [ ] T068 [US5] Ensure internal endpoint publishes task_created event
- [ ] T069 [US5] Add Dapr app-id validation for internal calls

**Checkpoint**: Recurring Task Service can create new tasks via internal API

---

## Phase 8: User Story 6 - Dapr Components (Priority: P2)

**Goal**: All Dapr components configured for local and cloud environments

**Independent Test**: Deploy to Minikube, verify all components show in `dapr components -k`

### Implementation for User Story 6

- [ ] T070 [P] [US6] Create kafka-pubsub.yaml (base) in phase_5/dapr/pubsub/kafka-pubsub.yaml
- [ ] T071 [P] [US6] Create kafka-pubsub.yaml (local) in phase_5/dapr/pubsub/local/kafka-pubsub.yaml
- [ ] T072 [P] [US6] Create kafka-pubsub.yaml (cloud) in phase_5/dapr/pubsub/cloud/kafka-pubsub.yaml
- [ ] T073 [P] [US6] Create statestore.yaml (base) in phase_5/dapr/statestore/statestore.yaml
- [ ] T074 [P] [US6] Create statestore.yaml (local - Redis) in phase_5/dapr/statestore/local/statestore.yaml
- [ ] T075 [P] [US6] Create statestore.yaml (cloud - PostgreSQL) in phase_5/dapr/statestore/cloud/statestore.yaml
- [ ] T076 [P] [US6] Create reminder-cron.yaml in phase_5/dapr/bindings/reminder-cron.yaml
- [ ] T077 [P] [US6] Create kubernetes-secrets.yaml in phase_5/dapr/secrets/kubernetes-secrets.yaml
- [ ] T078 [US6] Create kustomization.yaml for local overlay in phase_5/dapr/local/kustomization.yaml
- [ ] T079 [US6] Create kustomization.yaml for cloud overlay in phase_5/dapr/cloud/kustomization.yaml

**Checkpoint**: Dapr components ready for deployment

---

## Phase 9: User Story 7 - Kubernetes Local (Priority: P2)

**Goal**: All services deployable to Minikube with Dapr sidecars

**Independent Test**: `kubectl apply`, verify all pods running with 2/2 containers (app + sidecar)

### Implementation for User Story 7

- [ ] T080 [P] [US7] Create namespace.yaml in phase_5/k8s/base/namespace.yaml
- [ ] T081 [P] [US7] Create backend deployment.yaml with Dapr annotations in phase_5/k8s/base/backend/deployment.yaml
- [ ] T082 [P] [US7] Create backend service.yaml in phase_5/k8s/base/backend/service.yaml
- [ ] T083 [P] [US7] Create notification-service deployment.yaml in phase_5/k8s/base/notification-service/deployment.yaml
- [ ] T084 [P] [US7] Create notification-service service.yaml in phase_5/k8s/base/notification-service/service.yaml
- [ ] T085 [P] [US7] Create recurring-task-service deployment.yaml in phase_5/k8s/base/recurring-task-service/deployment.yaml
- [ ] T086 [P] [US7] Create recurring-task-service service.yaml in phase_5/k8s/base/recurring-task-service/service.yaml
- [ ] T087 [P] [US7] Create redpanda deployment in phase_5/k8s/base/infrastructure/redpanda.yaml
- [ ] T088 [P] [US7] Create redis deployment in phase_5/k8s/base/infrastructure/redis.yaml
- [ ] T089 [P] [US7] Create configmap.yaml for environment variables in phase_5/k8s/base/configmap.yaml
- [ ] T090 [P] [US7] Create secrets.yaml template in phase_5/k8s/base/secrets.yaml
- [ ] T091 [US7] Create local kustomization.yaml in phase_5/k8s/local/kustomization.yaml

**Checkpoint**: Full stack deployable to Minikube

---

## Phase 10: User Story 8 - Kubernetes Cloud (Priority: P2)

**Goal**: Cloud-specific Kubernetes configuration for DOKS/GKE/AKS deployment

**Independent Test**: Deploy to cloud cluster, access via HTTPS ingress

### Implementation for User Story 8

- [ ] T092 [P] [US8] Create cloud kustomization.yaml in phase_5/k8s/cloud/kustomization.yaml
- [ ] T093 [P] [US8] Create ingress.yaml with TLS in phase_5/k8s/cloud/ingress.yaml
- [ ] T094 [P] [US8] Create cert-manager ClusterIssuer in phase_5/k8s/cloud/cluster-issuer.yaml
- [ ] T095 [P] [US8] Create external-secrets config for Redpanda Cloud in phase_5/k8s/cloud/external-secrets.yaml
- [ ] T096 [US8] Update configmap with cloud-specific values in phase_5/k8s/cloud/configmap-patch.yaml

**Checkpoint**: Application deployable to production cloud

---

## Phase 11: User Story 9 - Helm Charts (Priority: P2)

**Goal**: Helm charts for all services with configurable values

**Independent Test**: `helm install` with custom values, verify deployment matches values

### Implementation for User Story 9

- [ ] T097 [P] [US9] Create todo-backend Chart.yaml in phase_5/helm/todo-backend/Chart.yaml
- [ ] T098 [P] [US9] Create todo-backend values.yaml in phase_5/helm/todo-backend/values.yaml
- [ ] T099 [P] [US9] Create todo-backend templates/ in phase_5/helm/todo-backend/templates/
- [ ] T100 [P] [US9] Create notification-service Chart.yaml in phase_5/helm/notification-service/Chart.yaml
- [ ] T101 [P] [US9] Create notification-service values.yaml in phase_5/helm/notification-service/values.yaml
- [ ] T102 [P] [US9] Create notification-service templates/ in phase_5/helm/notification-service/templates/
- [ ] T103 [P] [US9] Create recurring-task-service Chart.yaml in phase_5/helm/recurring-task-service/Chart.yaml
- [ ] T104 [P] [US9] Create recurring-task-service values.yaml in phase_5/helm/recurring-task-service/values.yaml
- [ ] T105 [P] [US9] Create recurring-task-service templates/ in phase_5/helm/recurring-task-service/templates/
- [ ] T106 [US9] Create values-local.yaml overrides for all charts
- [ ] T107 [US9] Create values-production.yaml overrides for all charts

**Checkpoint**: Services installable via Helm

---

## Phase 12: User Story 10 - CI/CD Pipeline (Priority: P2)

**Goal**: GitHub Actions for automated CI/CD with staging and production deployments

**Independent Test**: Push PR, verify CI runs; merge, verify staging deploy

### Implementation for User Story 10

- [ ] T108 [P] [US10] Create ci.yaml workflow in phase_5/.github/workflows/ci.yaml
- [ ] T109 [P] [US10] Create deploy-staging.yaml workflow in phase_5/.github/workflows/deploy-staging.yaml
- [ ] T110 [P] [US10] Create deploy-production.yaml workflow in phase_5/.github/workflows/deploy-production.yaml
- [ ] T111 [P] [US10] Create rollback.yaml workflow in phase_5/.github/workflows/rollback.yaml
- [ ] T112 [US10] Document required GitHub secrets in phase_5/.github/workflows/README.md
- [ ] T113 [US10] Add Docker build and push steps for all services
- [ ] T114 [US10] Add Helm upgrade steps for deployments
- [ ] T115 [US10] Add manual approval gate for production

**Checkpoint**: Full CI/CD pipeline operational

---

## Phase 13: User Story 11 - MCP Extensions (Priority: P1)

**Goal**: Extend MCP tools to support all new task fields and event publishing

**Independent Test**: Use chatbot: "Add task buy groceries with high priority, remind me tomorrow"

### Tests for User Story 11

- [ ] T116 [P] [US11] Unit test for extended MCP tools in phase_5/backend/tests/unit/test_mcp_tools.py

### Implementation for User Story 11

- [ ] T117 [US11] Extend add_task MCP tool with priority, tags, due_date, remind_at, recurrence_rule in phase_5/backend/app/mcp_server/tools.py
- [ ] T118 [US11] Extend update_task MCP tool with new fields
- [ ] T119 [US11] Add list_tasks filtering by priority, tags, status
- [ ] T120 [US11] Add list_tasks sorting by due_date, priority, created_at
- [ ] T121 [US11] Add search_tasks for keyword search in title/description
- [ ] T122 [US11] Ensure all MCP tool operations trigger event publishing
- [ ] T123 [US11] Update agent prompts to understand reminder/recurrence language

**Checkpoint**: Chatbot fully supports advanced task features

---

## Phase 14: User Story 12 - Observability (Priority: P3)

**Goal**: All services emit structured logs and expose health/metrics endpoints

**Independent Test**: Check logs are JSON formatted, health endpoints return 200

### Implementation for User Story 12

- [ ] T124 [P] [US12] Configure structlog for JSON output in all services
- [ ] T125 [P] [US12] Add correlation ID (event_id, user_id) to all log entries
- [ ] T126 [P] [US12] Ensure health endpoints in all services return detailed status
- [ ] T127 [P] [US12] Add readiness checks for Dapr sidecar, Kafka, state store
- [ ] T128 [US12] Add Prometheus annotations to Kubernetes deployments (optional)
- [ ] T129 [US12] Document log format and key fields in phase_5/docs/observability.md

**Checkpoint**: Production-ready observability

---

## Phase 15: Polish & Cross-Cutting Concerns

**Purpose**: Documentation, cleanup, and final validation

- [ ] T130 [P] Update phase_5/README.md with complete setup instructions
- [ ] T131 [P] Create phase_5/docs/architecture.md with system diagram
- [ ] T132 [P] Create phase_5/docs/event-catalog.md documenting all events
- [ ] T133 Run quickstart.md validation end-to-end
- [ ] T134 Security review: ensure no secrets in code, all via K8s secrets
- [ ] T135 Performance validation: test event processing latency < 2 seconds
- [ ] T136 Final integration test: complete recurring task flow end-to-end

---

## Dependencies & Execution Order

### Phase Dependencies

```
Phase 1 (Setup)
    ↓
Phase 2 (Foundational) ← BLOCKS ALL USER STORIES
    ↓
┌───────────────────────────────────────────────────────────┐
│ User Stories can proceed in parallel after Phase 2:       │
│                                                           │
│ Phase 3 (US1: Event Publishing) ←─── MVP Core             │
│ Phase 4 (US2: Notification Service)                       │
│ Phase 5 (US3: Recurring Task Service)                     │
│ Phase 6 (US4: Reminder Cron)                              │
│ Phase 7 (US5: Internal Task API)                          │
│ Phase 13 (US11: MCP Extensions)                           │
│                                                           │
│ Infrastructure can also proceed in parallel:              │
│ Phase 8 (US6: Dapr Components)                            │
│ Phase 9 (US7: K8s Local)                                  │
│ Phase 10 (US8: K8s Cloud)                                 │
│ Phase 11 (US9: Helm Charts)                               │
│ Phase 12 (US10: CI/CD)                                    │
│ Phase 14 (US12: Observability)                            │
└───────────────────────────────────────────────────────────┘
    ↓
Phase 15 (Polish) ← Requires all desired stories complete
```

### User Story Dependencies

| Story | Depends On | Can Parallel With |
|-------|------------|-------------------|
| US1 (Event Publishing) | Phase 2 | US6, US7, US8, US9, US10 |
| US2 (Notification Service) | US1 (needs events) | US3, US4, US5 |
| US3 (Recurring Task Service) | US1, US5 (needs internal API) | US2 |
| US4 (Reminder Cron) | US1 (needs publisher) | US2, US3, US5 |
| US5 (Internal Task API) | Phase 2 | US1, US2, US4, US6-US12 |
| US6-US10 (Infrastructure) | Phase 2 | All other stories |
| US11 (MCP Extensions) | US1 (needs event publishing) | US2-US5, US6-US10 |
| US12 (Observability) | Phase 2 | All other stories |

### Critical Path (MVP)

```
T001-T009 (Setup) → T010-T021 (Foundation) → T025-T030 (Event Publishing) → MVP COMPLETE
```

---

## Parallel Execution Examples

### Example 1: Foundation Phase (Phase 2)

```bash
# These can all run in parallel:
Task T015: "Create CloudEvents base schema"
Task T016: "Create TaskEvent schema"
Task T017: "Create ReminderEvent schema"
```

### Example 2: After Foundation Complete

```bash
# Launch multiple user stories in parallel:
Story US1: Event Publishing (T022-T030)
Story US6: Dapr Components (T070-T079)
Story US7: K8s Local (T080-T091)
```

### Example 3: Service Implementation

```bash
# Within US2 (Notification Service), these can run in parallel:
Task T034: "Create FastAPI main.py"
Task T035: "Create IdempotencyService"
```

---

## Implementation Strategy

### MVP First (Recommended)

1. ✅ Phase 1: Setup (T001-T009)
2. ✅ Phase 2: Foundation (T010-T021)
3. ✅ Phase 3: US1 Event Publishing (T022-T030)
4. **STOP and VALIDATE**: Events appearing in Kafka
5. Deploy to Minikube for demo

### Full Feature Set

1. Complete MVP above
2. Add US2 (Notification) + US4 (Cron) for reminders
3. Add US3 (Recurring) + US5 (Internal API) for recurring tasks
4. Add US11 (MCP) for chatbot integration
5. Add US6-US10 for production infrastructure
6. Add US12 for observability
7. Polish phase for documentation

### Parallel Team Strategy

With 3 developers after Foundation:
- **Dev A**: US1, US4, US5 (Backend core)
- **Dev B**: US2, US3 (New microservices)
- **Dev C**: US6, US7, US8, US9, US10 (Infrastructure)

---

## Summary

| Metric | Count |
|--------|-------|
| Total Tasks | 136 |
| Setup Tasks | 9 |
| Foundation Tasks | 12 |
| User Story Tasks | 107 |
| Polish Tasks | 8 |
| Parallelizable Tasks | 78 (57%) |
| User Stories | 12 |

### Tasks per User Story

| Story | Tasks | Complexity |
|-------|-------|------------|
| US1: Event Publishing | 9 | M |
| US2: Notification Service | 11 | M |
| US3: Recurring Task Service | 13 | L |
| US4: Reminder Cron | 8 | S |
| US5: Internal Task API | 7 | S |
| US6: Dapr Components | 10 | M |
| US7: K8s Local | 12 | M |
| US8: K8s Cloud | 5 | S |
| US9: Helm Charts | 11 | M |
| US10: CI/CD | 8 | M |
| US11: MCP Extensions | 8 | M |
| US12: Observability | 6 | S |

---

## Notes

- [P] tasks = different files, no dependencies on incomplete tasks
- [Story] label maps task to specific user story for traceability
- Each user story is independently testable after completion
- Phase 3/4 code is READ-ONLY - all work in phase_5/
- Commit after each task or logical group
- Stop at any checkpoint to validate independently
