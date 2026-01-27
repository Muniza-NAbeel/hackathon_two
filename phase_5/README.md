# Phase 5: Advanced Cloud Deployment

Event-driven microservices architecture with Kafka, Dapr, and Kubernetes.

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────────────────┐
│                              Frontend (Next.js)                          │
└─────────────────────────────────┬───────────────────────────────────────┘
                                  │ HTTP
                                  ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                         Chat Backend (FastAPI)                           │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐    │
│  │ Task CRUD   │  │ Event       │  │ Reminder    │  │ MCP Tools   │    │
│  │ API         │  │ Publisher   │  │ Checker     │  │ (6 tools)   │    │
│  └─────────────┘  └──────┬──────┘  └─────────────┘  └─────────────┘    │
└──────────────────────────┼──────────────────────────────────────────────┘
                           │ Dapr Pub/Sub
                           ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                         Kafka / Redpanda                                 │
│  ┌─────────────────────┐          ┌─────────────────────┐               │
│  │ task-events topic   │          │ reminders topic     │               │
│  └──────────┬──────────┘          └──────────┬──────────┘               │
└─────────────┼────────────────────────────────┼──────────────────────────┘
              │                                │
              ▼                                ▼
┌─────────────────────────┐      ┌─────────────────────────┐
│ Recurring Task Service  │      │ Notification Service    │
│ ┌─────────────────────┐ │      │ ┌─────────────────────┐ │
│ │ TaskCompletedHandler│ │      │ │ ReminderHandler     │ │
│ │ RecurrenceCalculator│ │      │ │ IdempotencyService  │ │
│ │ TaskCreator (Dapr)  │ │      │ └─────────────────────┘ │
│ └─────────────────────┘ │      └─────────────────────────┘
└─────────────────────────┘
```

## Key Features

### Event-Driven Architecture
- **CloudEvents v1.0**: Standardized event format
- **Kafka/Redpanda**: Message broker for event streaming
- **Dapr**: Abstraction layer for pub/sub, state, service invocation

### Microservices
1. **Chat Backend**: Extended with event publishing
2. **Notification Service**: Consumes reminder events
3. **Recurring Task Service**: Creates next task instances

### Idempotent Processing
- 24-hour TTL deduplication via Dapr State Store
- Prevents duplicate notifications and task creation

## Project Structure

```
phase_5/
├── backend/                    # Extended backend with events
│   └── app/
│       ├── events/            # CloudEvents & Dapr publisher
│       ├── api/internal.py    # Internal APIs
│       └── services/          # Reminder checker
├── services/
│   ├── notification-service/  # Reminder notifications
│   └── recurring-task-service/# Recurring task handling
├── dapr/                      # Dapr components
│   ├── pubsub/               # Kafka pub/sub
│   ├── statestore/           # PostgreSQL state
│   ├── bindings/             # Cron binding
│   └── secrets/              # Secret store
├── k8s/                       # Kubernetes manifests
│   ├── base/                 # Namespace, secrets, configmap
│   ├── local/                # Minikube deployments
│   └── cloud/                # Cloud-specific (DOKS/GKE/AKS)
├── .github/workflows/         # CI/CD
└── docker-compose.yaml        # Local development
```

## Quick Start

### Prerequisites
- Docker & Docker Compose
- Python 3.11+
- Node.js 20+
- (Optional) Minikube + kubectl + Helm

### Local Development with Docker Compose

```bash
cd phase_5

# Start all services
docker-compose up -d

# Check service health
curl http://localhost:8000/health
curl http://localhost:8001/health
curl http://localhost:8002/health
```

### Run Backend Locally (without Docker)

```bash
cd phase_5/backend
pip install -r requirements.txt

# Disable events for local testing
export EVENTS_ENABLED=false
export DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost:5432/todoapp

uvicorn app.main:app --reload
```

## Event Types

### Task Events (topic: `task-events`)
- `com.todo.task.created` - New task created
- `com.todo.task.updated` - Task modified
- `com.todo.task.completed` - Task marked complete
- `com.todo.task.deleted` - Task removed

### Reminder Events (topic: `reminders`)
- `com.todo.reminder.due` - Reminder triggered

## API Endpoints

### Backend (port 8000)
- `GET /health` - Health check
- `GET /dapr/subscribe` - Dapr subscriptions
- `GET /dapr/config` - Dapr configuration
- `POST /api/internal/tasks` - Create task (internal)
- `POST /api/internal/reminder-cron` - Trigger reminder check

### Notification Service (port 8001)
- `GET /health` - Liveness probe
- `GET /ready` - Readiness probe
- `POST /events/reminder` - Handle reminder event

### Recurring Task Service (port 8002)
- `GET /health` - Liveness probe
- `GET /ready` - Readiness probe
- `POST /events/task` - Handle task event

## MCP Tools

Phase 5 adds the `set_reminder` tool:

```python
set_reminder(user_id, task_id, remind_at)
# Example: set_reminder("user-uuid", 42, "2026-01-20T09:00:00")
```

## Kubernetes Deployment

### Minikube

```bash
# Start Minikube
minikube start

# Enable Dapr
dapr init -k

# Apply manifests
kubectl apply -f k8s/base/
kubectl apply -f k8s/local/
kubectl apply -f dapr/

# Port forward
kubectl port-forward svc/chat-backend 8000:8000 -n todo-app
```

## CI/CD Pipeline

GitHub Actions workflow (`.github/workflows/ci.yaml`):
1. Lint (Ruff)
2. Test (pytest)
3. Build Docker images
4. (On main) Deploy to cloud

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `DATABASE_URL` | PostgreSQL connection | - |
| `DAPR_HTTP_PORT` | Dapr sidecar port | 3500 |
| `DAPR_PUBSUB_NAME` | Pub/Sub component | kafka-pubsub |
| `TASK_EVENTS_TOPIC` | Task events topic | task-events |
| `REMINDERS_TOPIC` | Reminders topic | reminders |
| `EVENTS_ENABLED` | Enable event publishing | true |
| `BACKEND_APP_ID` | Backend Dapr app ID | chat-backend |

## Technology Stack

- **Languages**: Python 3.11, TypeScript
- **Backend**: FastAPI, SQLModel, Alembic
- **Frontend**: Next.js 14, Tailwind CSS
- **Messaging**: Kafka/Redpanda, Dapr Pub/Sub
- **Database**: PostgreSQL (Neon Serverless)
- **Infrastructure**: Docker, Kubernetes, Helm
- **CI/CD**: GitHub Actions
