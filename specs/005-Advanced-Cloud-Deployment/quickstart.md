# Phase 5 Quickstart Guide

**Date**: 2026-01-18
**Feature**: 005-Advanced-Cloud-Deployment

## Prerequisites

Before starting Phase 5 development, ensure you have:

### Required Tools

| Tool | Version | Installation |
|------|---------|--------------|
| Docker | 24+ | [Install Docker](https://docs.docker.com/get-docker/) |
| kubectl | 1.28+ | [Install kubectl](https://kubernetes.io/docs/tasks/tools/) |
| Minikube | Latest | [Install Minikube](https://minikube.sigs.k8s.io/docs/start/) |
| Helm | 3+ | [Install Helm](https://helm.sh/docs/intro/install/) |
| Dapr CLI | 1.12+ | [Install Dapr](https://docs.dapr.io/getting-started/install-dapr-cli/) |
| Python | 3.11+ | [Install Python](https://www.python.org/downloads/) |

### Verify Installations

```bash
# Check all tools
docker --version        # Docker version 24.x.x
kubectl version --client # Client Version: v1.28.x
minikube version        # minikube version: v1.x.x
helm version            # version.BuildInfo{Version:"v3.x.x"}
dapr --version          # CLI version: 1.12.x
python --version        # Python 3.11.x
```

---

## Local Development Setup

### Step 1: Start Minikube

```bash
# Start Minikube with sufficient resources
minikube start --cpus=4 --memory=8192 --driver=docker

# Verify cluster is running
kubectl cluster-info
```

### Step 2: Install Dapr on Kubernetes

```bash
# Initialize Dapr on the cluster
dapr init -k --runtime-version 1.12.0

# Wait for Dapr pods to be ready
kubectl wait --for=condition=ready pod -l app.kubernetes.io/part-of=dapr -n dapr-system --timeout=120s

# Verify Dapr installation
dapr status -k
```

### Step 3: Create Namespace

```bash
# Create todo-app namespace
kubectl create namespace todo-app

# Set as default
kubectl config set-context --current --namespace=todo-app
```

### Step 4: Deploy Infrastructure

```bash
# Deploy Redpanda (Kafka)
helm repo add redpanda https://charts.redpanda.com
helm install redpanda redpanda/redpanda \
  --namespace todo-app \
  --set statefulset.replicas=1 \
  --set resources.cpu.cores=1 \
  --set resources.memory.container.max=2Gi

# Deploy Redis (State Store)
helm repo add bitnami https://charts.bitnami.com/bitnami
helm install redis bitnami/redis \
  --namespace todo-app \
  --set auth.enabled=false \
  --set architecture=standalone

# Wait for infrastructure
kubectl wait --for=condition=ready pod -l app.kubernetes.io/name=redpanda -n todo-app --timeout=300s
kubectl wait --for=condition=ready pod -l app.kubernetes.io/name=redis -n todo-app --timeout=120s
```

### Step 5: Deploy Dapr Components

```bash
# Apply Dapr components for local development
kubectl apply -f phase_5/dapr-components/local/
```

### Step 6: Build and Deploy Services

```bash
# Point Docker to Minikube's registry
eval $(minikube docker-env)

# Build images
docker build -t chat-backend:latest phase_5/backend/
docker build -t notification-service:latest phase_5/notification-service/
docker build -t recurring-task-service:latest phase_5/recurring-task-service/

# Deploy services
kubectl apply -f phase_5/k8s/local/
```

### Step 7: Verify Deployment

```bash
# Check all pods are running
kubectl get pods -n todo-app

# Expected output:
# NAME                                      READY   STATUS    RESTARTS   AGE
# chat-backend-xxxxx                        2/2     Running   0          1m
# notification-service-xxxxx                2/2     Running   0          1m
# recurring-task-service-xxxxx              2/2     Running   0          1m
# redpanda-0                                1/1     Running   0          5m
# redis-master-0                            1/1     Running   0          5m

# Check Dapr sidecars are injected (2/2 means main + sidecar)
```

### Step 8: Access Services

```bash
# Port-forward backend
kubectl port-forward svc/chat-backend 8000:8000 -n todo-app &

# Port-forward notification service (for debugging)
kubectl port-forward svc/notification-service 8001:8001 -n todo-app &

# Test health endpoints
curl http://localhost:8000/health
curl http://localhost:8001/health
```

---

## Development Workflow

### Running Tests

```bash
# Install test dependencies
cd phase_5
pip install -r requirements-dev.txt

# Run unit tests
pytest tests/unit/ -v

# Run integration tests (requires running cluster)
pytest tests/integration/ -v
```

### Viewing Logs

```bash
# View backend logs
kubectl logs -f deployment/chat-backend -c chat-backend -n todo-app

# View notification service logs
kubectl logs -f deployment/notification-service -c notification-service -n todo-app

# View Dapr sidecar logs
kubectl logs -f deployment/chat-backend -c daprd -n todo-app
```

### Testing Event Flow

```bash
# Create a task with recurrence (via chat or API)
curl -X POST http://localhost:8000/api/tasks \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{
    "title": "Daily standup",
    "recurrence": "daily",
    "due_date": "2026-01-19T09:00:00Z"
  }'

# Complete the task
curl -X PATCH http://localhost:8000/api/tasks/1 \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{"completed": true}'

# Check notification service logs for recurring task creation
kubectl logs -f deployment/recurring-task-service -c recurring-task-service -n todo-app
```

### Debugging Dapr

```bash
# Check Dapr components
dapr components -k -n todo-app

# Test pub/sub
dapr publish --pubsub kafka-pubsub --topic test --data '{"test": true}' -k

# Check Dapr dashboard (optional)
dapr dashboard -k
```

---

## Project Structure

```
phase_5/
├── backend/                    # Enhanced chat backend
│   ├── app/
│   │   ├── events/            # Event publishing
│   │   └── api/               # New endpoints
│   ├── Dockerfile
│   └── requirements.txt
│
├── notification-service/       # New service
│   ├── app/
│   │   ├── handlers/          # Event handlers
│   │   └── services/          # Business logic
│   ├── Dockerfile
│   └── requirements.txt
│
├── recurring-task-service/     # New service
│   ├── app/
│   ├── Dockerfile
│   └── requirements.txt
│
├── dapr-components/
│   ├── local/                 # Local Minikube config
│   └── cloud/                 # Cloud config
│
└── k8s/
    ├── local/                 # Local manifests
    └── cloud/                 # Cloud manifests
```

---

## Environment Variables

### Backend Service

| Variable | Description | Default |
|----------|-------------|---------|
| DATABASE_URL | Neon PostgreSQL connection | Required |
| DAPR_HTTP_PORT | Dapr sidecar port | 3500 |
| KAFKA_PUBSUB_NAME | Dapr pub/sub component | kafka-pubsub |

### Notification Service

| Variable | Description | Default |
|----------|-------------|---------|
| DAPR_HTTP_PORT | Dapr sidecar port | 3500 |
| STATE_STORE_NAME | Dapr state store | statestore |

### Recurring Task Service

| Variable | Description | Default |
|----------|-------------|---------|
| DAPR_HTTP_PORT | Dapr sidecar port | 3500 |
| STATE_STORE_NAME | Dapr state store | statestore |
| BACKEND_APP_ID | Backend Dapr app ID | chat-backend |

---

## Troubleshooting

### Pod not starting

```bash
# Check pod events
kubectl describe pod <pod-name> -n todo-app

# Common issues:
# - ImagePullBackOff: Run `eval $(minikube docker-env)` before build
# - CrashLoopBackOff: Check logs for errors
```

### Dapr sidecar not injecting

```bash
# Ensure annotation is present
kubectl get deployment chat-backend -n todo-app -o yaml | grep -A5 annotations

# Required annotation:
# dapr.io/enabled: "true"
# dapr.io/app-id: "chat-backend"
# dapr.io/app-port: "8000"
```

### Events not flowing

```bash
# Check Kafka topics exist
kubectl exec -it redpanda-0 -n todo-app -- rpk topic list

# Check consumer groups
kubectl exec -it redpanda-0 -n todo-app -- rpk group list

# Test publish directly
dapr publish --pubsub kafka-pubsub --topic task-events --data '{"test": true}' -k
```

### State store not working

```bash
# Test state store
curl -X POST http://localhost:3500/v1.0/state/statestore \
  -H "Content-Type: application/json" \
  -d '[{"key": "test", "value": {"data": "test"}}]'

curl http://localhost:3500/v1.0/state/statestore/test
```

---

## Next Steps

1. **Run `/sp.tasks`** to generate implementation task breakdown
2. **Implement services** following the generated tasks
3. **Test locally** using this quickstart guide
4. **Deploy to cloud** following `deployment-cloud.md`

---

## References

- [Dapr Documentation](https://docs.dapr.io/)
- [Redpanda Quick Start](https://docs.redpanda.com/docs/get-started/quick-start/)
- [Minikube Documentation](https://minikube.sigs.k8s.io/docs/)
- [Phase 5 Specification](./spec.md)
