# Dapr Components Specification

## Overview

This specification defines all Dapr components required for Phase 5 event-driven architecture. Dapr abstracts infrastructure concerns (Kafka, database, secrets) behind simple HTTP APIs, allowing the application to remain infrastructure-agnostic.

## Component Summary

| Component | Type | Purpose |
|-----------|------|---------|
| kafka-pubsub | pubsub.kafka | Event streaming via Kafka |
| statestore | state.postgresql | State management and idempotency |
| reminder-cron | bindings.cron | Scheduled reminder triggers |
| kubernetes-secrets | secretstores.kubernetes | Secure credential access |

---

## Component 1: Kafka Pub/Sub

### Purpose

Abstract Kafka producer/consumer operations. Services publish and subscribe to events via Dapr HTTP API instead of using Kafka client libraries directly.

### Configuration

**File**: `components/kafka-pubsub.yaml`

```yaml
apiVersion: dapr.io/v1alpha1
kind: Component
metadata:
  name: kafka-pubsub
  namespace: todo-app
spec:
  type: pubsub.kafka
  version: v1
  metadata:
    # Kafka broker configuration
    - name: brokers
      value: "kafka:9092"  # Local: kafka:9092, Cloud: from secret

    # Consumer configuration
    - name: consumerGroup
      value: "todo-app-consumers"
    - name: initialOffset
      value: "oldest"  # Process all unread messages on startup

    # Authentication (for Redpanda Cloud)
    - name: authType
      value: "password"  # none for local, password for cloud
    - name: saslUsername
      secretKeyRef:
        name: kafka-secrets
        key: username
    - name: saslPassword
      secretKeyRef:
        name: kafka-secrets
        key: password
    - name: saslMechanism
      value: "SCRAM-SHA-256"

    # TLS (for cloud)
    - name: tls
      value: "true"  # false for local

    # Performance tuning
    - name: maxMessageBytes
      value: "1048576"  # 1MB
    - name: consumeRetryInterval
      value: "1s"
```

### Local Development Override

**File**: `components/local/kafka-pubsub.yaml`

```yaml
apiVersion: dapr.io/v1alpha1
kind: Component
metadata:
  name: kafka-pubsub
spec:
  type: pubsub.kafka
  version: v1
  metadata:
    - name: brokers
      value: "redpanda:9092"
    - name: consumerGroup
      value: "todo-app-consumers"
    - name: initialOffset
      value: "oldest"
    - name: authType
      value: "none"
    - name: tls
      value: "false"
```

### Usage Examples

**Publishing an event:**
```
POST http://localhost:3500/v1.0/publish/kafka-pubsub/task-events
Content-Type: application/json

{
  "event_id": "uuid",
  "event_type": "created",
  "task_id": 123,
  ...
}
```

**Subscribing to events:**

Service declares subscription via `/dapr/subscribe` endpoint:
```json
[
  {
    "pubsubname": "kafka-pubsub",
    "topic": "task-events",
    "route": "/events/task"
  }
]
```

---

## Component 2: State Store

### Purpose

Provide key-value state storage for:
- Idempotency tracking (processed event IDs)
- Conversation state caching
- Temporary data storage

### Configuration

**File**: `components/statestore.yaml`

```yaml
apiVersion: dapr.io/v1alpha1
kind: Component
metadata:
  name: statestore
  namespace: todo-app
spec:
  type: state.postgresql
  version: v1
  metadata:
    # Connection string from secret
    - name: connectionString
      secretKeyRef:
        name: db-secrets
        key: connection-string

    # Table configuration
    - name: tableName
      value: "dapr_state"
    - name: metadataTableName
      value: "dapr_metadata"

    # Key prefix for isolation
    - name: keyPrefix
      value: "name"  # Uses component name as prefix

    # Cleanup configuration
    - name: cleanupIntervalInSeconds
      value: "3600"  # Clean expired entries hourly

    # Timeout
    - name: timeoutInSeconds
      value: "30"
```

### Local Development Override

**File**: `components/local/statestore.yaml`

```yaml
apiVersion: dapr.io/v1alpha1
kind: Component
metadata:
  name: statestore
spec:
  type: state.redis
  version: v1
  metadata:
    - name: redisHost
      value: "redis:6379"
    - name: redisPassword
      value: ""
```

### Usage Examples

**Save state:**
```
POST http://localhost:3500/v1.0/state/statestore
Content-Type: application/json

[
  {
    "key": "notification:processed:event-uuid",
    "value": {"processed_at": "2026-01-17T10:00:00Z"},
    "metadata": {
      "ttlInSeconds": "86400"
    }
  }
]
```

**Get state:**
```
GET http://localhost:3500/v1.0/state/statestore/notification:processed:event-uuid
```

**Delete state:**
```
DELETE http://localhost:3500/v1.0/state/statestore/notification:processed:event-uuid
```

---

## Component 3: Cron Binding

### Purpose

Trigger scheduled operations, specifically checking for due reminders every 5 minutes.

### Configuration

**File**: `components/reminder-cron.yaml`

```yaml
apiVersion: dapr.io/v1alpha1
kind: Component
metadata:
  name: reminder-cron
  namespace: todo-app
spec:
  type: bindings.cron
  version: v1
  metadata:
    - name: schedule
      value: "*/5 * * * *"  # Every 5 minutes
    - name: direction
      value: "input"
```

### Binding Target

The cron binding calls the backend service:

**Dapr calls**: `POST http://chat-backend:8000/reminder-cron`

The backend must implement this endpoint:

```python
@app.post("/reminder-cron")
async def check_reminders():
    """
    Called by Dapr cron every 5 minutes.
    Checks for tasks with due reminders and publishes events.
    """
    now = datetime.utcnow()

    # Query tasks where remind_at <= now and reminder_sent = false
    tasks = await get_pending_reminders(now)

    for task in tasks:
        # Publish reminder event
        await publish_reminder_event(task)
        # Mark as sent
        await mark_reminder_sent(task.id)

    return {"processed": len(tasks)}
```

### Scoping

To ensure only the backend receives cron triggers:

**File**: `components/reminder-cron.yaml`
```yaml
scopes:
  - chat-backend
```

---

## Component 4: Secrets Store

### Purpose

Securely access secrets (API keys, database credentials) without embedding them in code or environment variables.

### Configuration

**File**: `components/kubernetes-secrets.yaml`

```yaml
apiVersion: dapr.io/v1alpha1
kind: Component
metadata:
  name: kubernetes-secrets
  namespace: todo-app
spec:
  type: secretstores.kubernetes
  version: v1
  metadata: []
```

### Kubernetes Secrets Required

**File**: `secrets/db-secrets.yaml`
```yaml
apiVersion: v1
kind: Secret
metadata:
  name: db-secrets
  namespace: todo-app
type: Opaque
stringData:
  connection-string: "postgresql://user:pass@host:5432/db?sslmode=require"
```

**File**: `secrets/kafka-secrets.yaml`
```yaml
apiVersion: v1
kind: Secret
metadata:
  name: kafka-secrets
  namespace: todo-app
type: Opaque
stringData:
  username: "your-kafka-username"
  password: "your-kafka-password"
```

**File**: `secrets/api-secrets.yaml`
```yaml
apiVersion: v1
kind: Secret
metadata:
  name: api-secrets
  namespace: todo-app
type: Opaque
stringData:
  openai-api-key: "sk-..."
  better-auth-secret: "..."
```

### Usage Examples

**Get a secret:**
```
GET http://localhost:3500/v1.0/secrets/kubernetes-secrets/api-secrets/openai-api-key
```

**Response:**
```json
{
  "openai-api-key": "sk-..."
}
```

**In application code:**
```python
import httpx

async def get_secret(name: str, key: str) -> str:
    async with httpx.AsyncClient() as client:
        resp = await client.get(
            f"http://localhost:3500/v1.0/secrets/kubernetes-secrets/{name}/{key}"
        )
        return resp.json()[key]

# Usage
api_key = await get_secret("api-secrets", "openai-api-key")
```

---

## Component 5: Service Invocation (Built-in)

### Purpose

Enable service-to-service communication with:
- Automatic service discovery
- Built-in retries
- mTLS encryption
- Load balancing

### Configuration

Service Invocation is built into Dapr - no component configuration needed.

### Usage Examples

**Call another service:**
```
# Recurring Task Service calling Chat Backend
POST http://localhost:3500/v1.0/invoke/chat-backend/method/api/internal/tasks
Content-Type: application/json

{
  "user_id": "uuid",
  "title": "New recurring task",
  ...
}
```

**From code:**
```python
async def create_task_via_dapr(task_data: dict) -> dict:
    async with httpx.AsyncClient() as client:
        resp = await client.post(
            "http://localhost:3500/v1.0/invoke/chat-backend/method/api/internal/tasks",
            json=task_data
        )
        return resp.json()
```

### Service Discovery

Dapr uses Kubernetes DNS for service discovery:
- Service A calls Service B by Dapr app-id
- Dapr resolves app-id to actual pod IPs
- Automatic load balancing across replicas

---

## Component File Organization

```
dapr-components/
├── base/                       # Shared components
│   ├── kafka-pubsub.yaml
│   ├── statestore.yaml
│   ├── reminder-cron.yaml
│   └── kubernetes-secrets.yaml
├── local/                      # Local/Minikube overrides
│   ├── kafka-pubsub.yaml       # Points to local Redpanda
│   └── statestore.yaml         # Uses Redis
├── cloud/                      # Cloud-specific
│   ├── kafka-pubsub.yaml       # Points to Redpanda Cloud
│   └── statestore.yaml         # Uses Neon PostgreSQL
└── kustomization.yaml
```

### Kustomization

**File**: `dapr-components/kustomization.yaml`
```yaml
apiVersion: kustomize.config.k8s.io/v1beta1
kind: Kustomization

resources:
  - base/kafka-pubsub.yaml
  - base/statestore.yaml
  - base/reminder-cron.yaml
  - base/kubernetes-secrets.yaml
```

**File**: `dapr-components/local/kustomization.yaml`
```yaml
apiVersion: kustomize.config.k8s.io/v1beta1
kind: Kustomization

resources:
  - ../base

patchesStrategicMerge:
  - kafka-pubsub.yaml
  - statestore.yaml
```

---

## Deployment

### Installing Dapr on Kubernetes

```bash
# Install Dapr CLI
curl -fsSL https://raw.githubusercontent.com/dapr/cli/master/install/install.sh | bash

# Initialize Dapr on Kubernetes
dapr init -k --runtime-version 1.12.0

# Verify installation
dapr status -k
kubectl get pods -n dapr-system
```

### Deploying Components

```bash
# Local (Minikube)
kubectl apply -k dapr-components/local/

# Cloud
kubectl apply -k dapr-components/cloud/
```

### Verifying Components

```bash
# List components
dapr components -k

# Check component status
kubectl get components -n todo-app
```

---

## Security Considerations

### mTLS

Dapr enables mTLS by default between services:
- All service invocation encrypted
- Certificates auto-rotated
- Zero configuration required

### Secret Scoping

Restrict which services can access secrets:

```yaml
apiVersion: dapr.io/v1alpha1
kind: Component
metadata:
  name: kubernetes-secrets
spec:
  type: secretstores.kubernetes
  version: v1
scopes:
  - chat-backend
  - notification-service
  - recurring-task-service
```

### Component Scoping

Restrict which services can use components:

```yaml
# Only backend can use cron binding
apiVersion: dapr.io/v1alpha1
kind: Component
metadata:
  name: reminder-cron
spec:
  type: bindings.cron
  version: v1
scopes:
  - chat-backend
```

---

## Troubleshooting

### Common Issues

| Issue | Cause | Solution |
|-------|-------|----------|
| Component not found | Wrong namespace | Check namespace in component metadata |
| Pub/Sub not working | Broker unreachable | Verify broker connection string |
| State store timeout | DB connection issue | Check connection string, network |
| Secrets not found | Missing K8s secret | Create secret in correct namespace |

### Debugging Commands

```bash
# Check Dapr sidecar logs
kubectl logs <pod-name> -c daprd

# Test pubsub
dapr publish --pubsub kafka-pubsub --topic test --data '{"test": true}'

# Test state store
curl http://localhost:3500/v1.0/state/statestore/test-key
```
