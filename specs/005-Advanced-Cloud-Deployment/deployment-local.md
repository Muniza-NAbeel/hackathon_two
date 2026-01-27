# Local Deployment Specification (Minikube)

## Overview

This specification defines the local Kubernetes deployment using Minikube. All Phase 5 services, Dapr components, and infrastructure (Redpanda) are deployed locally for development and testing.

## Prerequisites

| Component | Version | Purpose |
|-----------|---------|---------|
| Minikube | 1.32+ | Local Kubernetes cluster |
| kubectl | 1.28+ | Kubernetes CLI |
| Helm | 3.12+ | Package manager |
| Docker | 24+ | Container runtime |
| Dapr CLI | 1.12+ | Dapr installation |

---

## Architecture

```
┌─────────────────────────────────────────────────────────────────────────┐
│                         MINIKUBE CLUSTER                                │
│                                                                         │
│  ┌──────────────────┐  ┌──────────────────┐  ┌──────────────────┐      │
│  │   Frontend Pod   │  │   Backend Pod    │  │  Notification    │      │
│  │  ┌────┐ ┌─────┐  │  │  ┌────┐ ┌─────┐  │  │     Pod          │      │
│  │  │Next│ │Dapr │  │  │  │Fast│ │Dapr │  │  │  ┌────┐ ┌─────┐  │      │
│  │  │ js │ │Side │  │  │  │API │ │Side │  │  │  │Svc │ │Dapr │  │      │
│  │  └────┘ └─────┘  │  │  └────┘ └─────┘  │  │  └────┘ └─────┘  │      │
│  └──────────────────┘  └──────────────────┘  └──────────────────┘      │
│                                                                         │
│  ┌──────────────────┐  ┌──────────────────┐  ┌──────────────────┐      │
│  │ Recurring Task   │  │    Redpanda      │  │     Redis        │      │
│  │     Pod          │  │   (Kafka)        │  │  (State Store)   │      │
│  │  ┌────┐ ┌─────┐  │  │                  │  │                  │      │
│  │  │Svc │ │Dapr │  │  │  Port: 9092      │  │  Port: 6379      │      │
│  │  └────┘ └─────┘  │  │                  │  │                  │      │
│  └──────────────────┘  └──────────────────┘  └──────────────────┘      │
│                                                                         │
│  ┌──────────────────────────────────────────────────────────────┐      │
│  │                    DAPR CONTROL PLANE                         │      │
│  │   dapr-operator  │  dapr-sidecar-injector  │  dapr-placement  │      │
│  └──────────────────────────────────────────────────────────────┘      │
└─────────────────────────────────────────────────────────────────────────┘
                              │
                    ┌─────────┴─────────┐
                    │   External Access  │
                    │   NodePort / Tunnel│
                    └───────────────────┘
```

---

## Step 1: Start Minikube

### Configuration

```bash
# Start Minikube with adequate resources
minikube start \
  --cpus=4 \
  --memory=8192 \
  --disk-size=30g \
  --driver=docker \
  --kubernetes-version=v1.28.0

# Enable required addons
minikube addons enable ingress
minikube addons enable metrics-server
minikube addons enable dashboard
```

### Verify Cluster

```bash
# Check cluster status
minikube status

# Verify kubectl connection
kubectl cluster-info
kubectl get nodes
```

---

## Step 2: Install Dapr

### Install Dapr Runtime

```bash
# Initialize Dapr on Kubernetes
dapr init -k --runtime-version 1.12.0

# Wait for Dapr pods to be ready
kubectl rollout status deploy/dapr-operator -n dapr-system
kubectl rollout status deploy/dapr-sidecar-injector -n dapr-system
kubectl rollout status deploy/dapr-placement-server -n dapr-system

# Verify installation
dapr status -k
```

### Expected Output

```
NAME                   NAMESPACE    HEALTHY  STATUS   REPLICAS  VERSION  AGE
dapr-dashboard         dapr-system  True     Running  1         0.14.0   1m
dapr-operator          dapr-system  True     Running  1         1.12.0   1m
dapr-placement-server  dapr-system  True     Running  1         1.12.0   1m
dapr-sentry            dapr-system  True     Running  1         1.12.0   1m
dapr-sidecar-injector  dapr-system  True     Running  1         1.12.0   1m
```

---

## Step 3: Create Namespace

```bash
# Create application namespace
kubectl create namespace todo-app

# Set as default for convenience
kubectl config set-context --current --namespace=todo-app
```

---

## Step 4: Deploy Infrastructure

### 4.1 Deploy Redpanda (Kafka)

**File**: `k8s/local/redpanda.yaml`

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: redpanda
  namespace: todo-app
spec:
  replicas: 1
  selector:
    matchLabels:
      app: redpanda
  template:
    metadata:
      labels:
        app: redpanda
    spec:
      containers:
        - name: redpanda
          image: redpandadata/redpanda:v23.3.5
          command:
            - redpanda
            - start
            - --smp=1
            - --memory=512M
            - --overprovisioned
            - --kafka-addr=PLAINTEXT://0.0.0.0:9092
            - --advertise-kafka-addr=PLAINTEXT://redpanda:9092
            - --pandaproxy-addr=0.0.0.0:8082
            - --advertise-pandaproxy-addr=redpanda:8082
          ports:
            - containerPort: 9092
              name: kafka
            - containerPort: 8082
              name: proxy
          resources:
            requests:
              memory: "512Mi"
              cpu: "500m"
            limits:
              memory: "1Gi"
              cpu: "1000m"
---
apiVersion: v1
kind: Service
metadata:
  name: redpanda
  namespace: todo-app
spec:
  selector:
    app: redpanda
  ports:
    - port: 9092
      targetPort: 9092
      name: kafka
    - port: 8082
      targetPort: 8082
      name: proxy
```

### 4.2 Deploy Redis (State Store)

**File**: `k8s/local/redis.yaml`

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: redis
  namespace: todo-app
spec:
  replicas: 1
  selector:
    matchLabels:
      app: redis
  template:
    metadata:
      labels:
        app: redis
    spec:
      containers:
        - name: redis
          image: redis:7-alpine
          ports:
            - containerPort: 6379
          resources:
            requests:
              memory: "64Mi"
              cpu: "100m"
            limits:
              memory: "128Mi"
              cpu: "200m"
---
apiVersion: v1
kind: Service
metadata:
  name: redis
  namespace: todo-app
spec:
  selector:
    app: redis
  ports:
    - port: 6379
      targetPort: 6379
```

### Deploy Infrastructure

```bash
kubectl apply -f k8s/local/redpanda.yaml
kubectl apply -f k8s/local/redis.yaml

# Wait for pods
kubectl wait --for=condition=ready pod -l app=redpanda --timeout=120s
kubectl wait --for=condition=ready pod -l app=redis --timeout=60s
```

---

## Step 5: Create Kafka Topics

```bash
# Exec into Redpanda pod
kubectl exec -it deploy/redpanda -- rpk topic create task-events --partitions 3
kubectl exec -it deploy/redpanda -- rpk topic create reminders --partitions 3
kubectl exec -it deploy/redpanda -- rpk topic create task-updates --partitions 3

# Verify topics
kubectl exec -it deploy/redpanda -- rpk topic list
```

---

## Step 6: Deploy Dapr Components

**File**: `k8s/local/dapr-components.yaml`

```yaml
# Kafka Pub/Sub
apiVersion: dapr.io/v1alpha1
kind: Component
metadata:
  name: kafka-pubsub
  namespace: todo-app
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
---
# Redis State Store
apiVersion: dapr.io/v1alpha1
kind: Component
metadata:
  name: statestore
  namespace: todo-app
spec:
  type: state.redis
  version: v1
  metadata:
    - name: redisHost
      value: "redis:6379"
    - name: redisPassword
      value: ""
---
# Cron Binding for Reminders
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
      value: "*/5 * * * *"
scopes:
  - chat-backend
```

```bash
kubectl apply -f k8s/local/dapr-components.yaml

# Verify components
kubectl get components -n todo-app
```

---

## Step 7: Build and Load Docker Images

### Configure Docker to use Minikube's registry

```bash
# Point Docker CLI to Minikube's Docker daemon
eval $(minikube docker-env)
```

### Build Images

```bash
# Build backend image
docker build -t todo-backend:local -f phase_5/backend/Dockerfile phase_5/backend/

# Build frontend image
docker build -t todo-frontend:local -f phase_5/frontend/Dockerfile phase_5/frontend/

# Build notification service
docker build -t notification-service:local -f phase_5/services/notification/Dockerfile phase_5/services/notification/

# Build recurring task service
docker build -t recurring-task-service:local -f phase_5/services/recurring/Dockerfile phase_5/services/recurring/

# Verify images
docker images | grep todo
```

---

## Step 8: Create Secrets

**File**: `k8s/local/secrets.yaml`

```yaml
apiVersion: v1
kind: Secret
metadata:
  name: db-secrets
  namespace: todo-app
type: Opaque
stringData:
  connection-string: "postgresql://user:password@neon-host:5432/todo?sslmode=require"
---
apiVersion: v1
kind: Secret
metadata:
  name: api-secrets
  namespace: todo-app
type: Opaque
stringData:
  openai-api-key: "sk-your-openai-key"
  better-auth-secret: "your-auth-secret"
```

```bash
# Apply secrets (edit with actual values first)
kubectl apply -f k8s/local/secrets.yaml
```

---

## Step 9: Deploy Application Services

### 9.1 Backend Deployment

**File**: `k8s/local/backend.yaml`

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: chat-backend
  namespace: todo-app
spec:
  replicas: 1
  selector:
    matchLabels:
      app: chat-backend
  template:
    metadata:
      labels:
        app: chat-backend
      annotations:
        dapr.io/enabled: "true"
        dapr.io/app-id: "chat-backend"
        dapr.io/app-port: "8000"
        dapr.io/enable-api-logging: "true"
    spec:
      containers:
        - name: backend
          image: todo-backend:local
          imagePullPolicy: Never
          ports:
            - containerPort: 8000
          env:
            - name: DATABASE_URL
              valueFrom:
                secretKeyRef:
                  name: db-secrets
                  key: connection-string
            - name: OPENAI_API_KEY
              valueFrom:
                secretKeyRef:
                  name: api-secrets
                  key: openai-api-key
          resources:
            requests:
              memory: "256Mi"
              cpu: "200m"
            limits:
              memory: "512Mi"
              cpu: "500m"
---
apiVersion: v1
kind: Service
metadata:
  name: chat-backend
  namespace: todo-app
spec:
  selector:
    app: chat-backend
  ports:
    - port: 8000
      targetPort: 8000
  type: ClusterIP
```

### 9.2 Frontend Deployment

**File**: `k8s/local/frontend.yaml`

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: chat-frontend
  namespace: todo-app
spec:
  replicas: 1
  selector:
    matchLabels:
      app: chat-frontend
  template:
    metadata:
      labels:
        app: chat-frontend
      annotations:
        dapr.io/enabled: "true"
        dapr.io/app-id: "chat-frontend"
        dapr.io/app-port: "3000"
    spec:
      containers:
        - name: frontend
          image: todo-frontend:local
          imagePullPolicy: Never
          ports:
            - containerPort: 3000
          env:
            - name: NEXT_PUBLIC_API_URL
              value: "http://chat-backend:8000"
          resources:
            requests:
              memory: "256Mi"
              cpu: "200m"
            limits:
              memory: "512Mi"
              cpu: "500m"
---
apiVersion: v1
kind: Service
metadata:
  name: chat-frontend
  namespace: todo-app
spec:
  selector:
    app: chat-frontend
  ports:
    - port: 3000
      targetPort: 3000
  type: NodePort
```

### 9.3 Notification Service Deployment

**File**: `k8s/local/notification-service.yaml`

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: notification-service
  namespace: todo-app
spec:
  replicas: 1
  selector:
    matchLabels:
      app: notification-service
  template:
    metadata:
      labels:
        app: notification-service
      annotations:
        dapr.io/enabled: "true"
        dapr.io/app-id: "notification-service"
        dapr.io/app-port: "8001"
    spec:
      containers:
        - name: notification
          image: notification-service:local
          imagePullPolicy: Never
          ports:
            - containerPort: 8001
          resources:
            requests:
              memory: "128Mi"
              cpu: "100m"
            limits:
              memory: "256Mi"
              cpu: "300m"
---
apiVersion: v1
kind: Service
metadata:
  name: notification-service
  namespace: todo-app
spec:
  selector:
    app: notification-service
  ports:
    - port: 8001
      targetPort: 8001
```

### 9.4 Recurring Task Service Deployment

**File**: `k8s/local/recurring-task-service.yaml`

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: recurring-task-service
  namespace: todo-app
spec:
  replicas: 1
  selector:
    matchLabels:
      app: recurring-task-service
  template:
    metadata:
      labels:
        app: recurring-task-service
      annotations:
        dapr.io/enabled: "true"
        dapr.io/app-id: "recurring-task-service"
        dapr.io/app-port: "8002"
    spec:
      containers:
        - name: recurring
          image: recurring-task-service:local
          imagePullPolicy: Never
          ports:
            - containerPort: 8002
          resources:
            requests:
              memory: "128Mi"
              cpu: "100m"
            limits:
              memory: "256Mi"
              cpu: "300m"
---
apiVersion: v1
kind: Service
metadata:
  name: recurring-task-service
  namespace: todo-app
spec:
  selector:
    app: recurring-task-service
  ports:
    - port: 8002
      targetPort: 8002
```

### Deploy All Services

```bash
kubectl apply -f k8s/local/backend.yaml
kubectl apply -f k8s/local/frontend.yaml
kubectl apply -f k8s/local/notification-service.yaml
kubectl apply -f k8s/local/recurring-task-service.yaml

# Wait for all pods
kubectl wait --for=condition=ready pod -l app=chat-backend --timeout=120s
kubectl wait --for=condition=ready pod -l app=chat-frontend --timeout=120s
kubectl wait --for=condition=ready pod -l app=notification-service --timeout=120s
kubectl wait --for=condition=ready pod -l app=recurring-task-service --timeout=120s
```

---

## Step 10: Access the Application

### Option 1: Minikube Tunnel

```bash
# Start tunnel (requires sudo)
minikube tunnel

# Access via localhost
# Frontend: http://localhost:3000
# Backend: http://localhost:8000
```

### Option 2: Port Forwarding

```bash
# Frontend
kubectl port-forward svc/chat-frontend 3000:3000 &

# Backend
kubectl port-forward svc/chat-backend 8000:8000 &
```

### Option 3: NodePort

```bash
# Get NodePort URL
minikube service chat-frontend --url -n todo-app
```

---

## Verification

### Check All Pods Running

```bash
kubectl get pods -n todo-app

# Expected output:
# NAME                                     READY   STATUS    RESTARTS   AGE
# chat-backend-xxx                         2/2     Running   0          5m
# chat-frontend-xxx                        2/2     Running   0          5m
# notification-service-xxx                 2/2     Running   0          5m
# recurring-task-service-xxx               2/2     Running   0          5m
# redpanda-xxx                             1/1     Running   0          10m
# redis-xxx                                1/1     Running   0          10m
```

### Verify Dapr Sidecars

```bash
# Check sidecar logs
kubectl logs deploy/chat-backend -c daprd | tail -20

# Should see:
# "msg":"dapr initialized. Status: Running."
```

### Test Pub/Sub

```bash
# Publish test event
kubectl exec -it deploy/chat-backend -c backend -- \
  curl -X POST http://localhost:3500/v1.0/publish/kafka-pubsub/task-events \
  -H "Content-Type: application/json" \
  -d '{"test": true}'

# Check notification service logs
kubectl logs deploy/notification-service -c notification
```

### Test API

```bash
# Health check
curl http://localhost:8000/health

# Chat endpoint
curl -X POST http://localhost:8000/api/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Add a task to test the system"}'
```

---

## Troubleshooting

| Issue | Command | Solution |
|-------|---------|----------|
| Pod not starting | `kubectl describe pod <pod>` | Check events for errors |
| Dapr sidecar issues | `kubectl logs <pod> -c daprd` | Check sidecar logs |
| Kafka connection | `kubectl exec -it deploy/redpanda -- rpk cluster info` | Verify Redpanda |
| Image not found | `docker images` | Rebuild with `eval $(minikube docker-env)` |

---

## Cleanup

```bash
# Delete application
kubectl delete namespace todo-app

# Stop Minikube
minikube stop

# Delete cluster (optional)
minikube delete
```
