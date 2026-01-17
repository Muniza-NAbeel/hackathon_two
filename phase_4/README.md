# Phase 4: Local Kubernetes Deployment (Minikube)

Deploy the Phase 3 AI-powered Todo Chatbot to a local Kubernetes cluster using Minikube.

## Prerequisites

| Tool | Version | Installation |
|------|---------|--------------|
| Docker | 24+ | [docker.com](https://docs.docker.com/get-docker/) |
| Minikube | 1.32+ | [minikube.sigs.k8s.io](https://minikube.sigs.k8s.io/docs/start/) |
| Helm | 3+ | [helm.sh](https://helm.sh/docs/intro/install/) |
| kubectl | 1.28+ | [kubernetes.io](https://kubernetes.io/docs/tasks/tools/) |

### System Requirements

- **CPU**: 4 cores minimum
- **Memory**: 8GB RAM minimum
- **Disk**: 20GB free space

## Environment Variables

Create a `.env` file or export these variables before deployment:

```bash
# Required - Database
export DATABASE_URL="postgresql://user:password@host/database?sslmode=require"

# Required - AI (Google Gemini)
export GEMINI_API_KEY="your-gemini-api-key"

# Required - Authentication
export JWT_SECRET="your-256-bit-secret"

# Optional (with defaults)
export JWT_ALGORITHM="HS256"
export ACCESS_TOKEN_EXPIRE_DAYS="7"
export DEBUG="False"
export CORS_ORIGINS="http://localhost:3000"
```

## Quick Deploy (5 Commands)

```bash
# 1. Start Minikube
minikube start --cpus=4 --memory=8192 --driver=docker

# 2. Configure Docker for Minikube
eval $(minikube docker-env)

# 3. Build Docker images
docker build -t todo-backend:latest -f phase_4/backend/Dockerfile phase_3/backend
docker build -t todo-frontend:latest -f phase_4/frontend/Dockerfile phase_3/frontend

# 4. Create secrets and deploy
kubectl create secret generic backend-secrets \
  --from-literal=DATABASE_URL="$DATABASE_URL" \
  --from-literal=GEMINI_API_KEY="$GEMINI_API_KEY" \
  --from-literal=JWT_SECRET="$JWT_SECRET"

helm install backend phase_4/helm/backend --set image.pullPolicy=Never
helm install frontend phase_4/helm/frontend --set image.pullPolicy=Never

# 5. Access the application
minikube service frontend
```

## Step-by-Step Deployment

### 1. Start Minikube Cluster

```bash
# Start with recommended resources
minikube start --cpus=4 --memory=8192 --driver=docker

# Verify cluster is running
kubectl cluster-info
kubectl get nodes
```

### 2. Configure Docker Environment

```bash
# Point Docker to Minikube's daemon
eval $(minikube docker-env)

# Verify (should show Minikube's images)
docker images
```

### 3. Build Docker Images

```bash
# Build backend image
docker build -t todo-backend:latest -f phase_4/backend/Dockerfile phase_3/backend

# Build frontend image
docker build -t todo-frontend:latest -f phase_4/frontend/Dockerfile phase_3/frontend

# Verify images exist
docker images | grep todo
```

### 4. Create Kubernetes Secret

```bash
kubectl create secret generic backend-secrets \
  --from-literal=DATABASE_URL="$DATABASE_URL" \
  --from-literal=GEMINI_API_KEY="$GEMINI_API_KEY" \
  --from-literal=JWT_SECRET="$JWT_SECRET"
```

### 5. Deploy Backend

```bash
# Install backend Helm chart
helm install backend phase_4/helm/backend --set image.pullPolicy=Never

# Wait for deployment
kubectl rollout status deployment/backend --timeout=120s

# Verify pod is ready
kubectl get pods -l app=backend
```

### 6. Deploy Frontend

```bash
# Install frontend Helm chart
helm install frontend phase_4/helm/frontend --set image.pullPolicy=Never

# Wait for deployment
kubectl rollout status deployment/frontend --timeout=120s

# Verify pod is ready
kubectl get pods -l app=frontend
```

### 7. Access Services

```bash
# Get service URLs
minikube service backend --url
minikube service frontend --url

# Open frontend in browser
minikube service frontend

# Test backend health
curl $(minikube service backend --url)/health
```

## Commands Reference

### Deployment Status

```bash
# Check all pods
kubectl get pods

# Check all services
kubectl get svc

# View pod logs
kubectl logs -l app=backend
kubectl logs -l app=frontend

# Describe pod (for debugging)
kubectl describe pod -l app=backend
```

### Helm Operations

```bash
# List releases
helm list

# Upgrade release
helm upgrade backend phase_4/helm/backend

# Uninstall release
helm uninstall backend
helm uninstall frontend
```

### Minikube Operations

```bash
# Check status
minikube status

# Stop cluster (preserves state)
minikube stop

# Delete cluster
minikube delete

# Open dashboard
minikube dashboard
```

## Troubleshooting

### ImagePullBackOff

**Cause**: Docker image not found in Minikube

**Solution**:
```bash
# Ensure Docker points to Minikube
eval $(minikube docker-env)

# Rebuild images
docker build -t todo-backend:latest -f phase_4/backend/Dockerfile phase_3/backend
```

### Pod CrashLoopBackOff

**Cause**: Application failing to start

**Solution**:
```bash
# Check pod logs
kubectl logs -l app=backend

# Check events
kubectl describe pod -l app=backend
```

### Service Unreachable

**Cause**: Service not exposed correctly

**Solution**:
```bash
# Use minikube service command
minikube service backend --url
minikube service frontend --url

# Or use port-forward
kubectl port-forward svc/backend 8000:8000
```

### Out of Memory

**Cause**: Insufficient Minikube resources

**Solution**:
```bash
# Stop and restart with more memory
minikube stop
minikube start --cpus=4 --memory=8192
```

### Database Connection Failed

**Cause**: DATABASE_URL not set or incorrect

**Solution**:
```bash
# Verify secret exists
kubectl get secret backend-secrets

# Check if DATABASE_URL is set
kubectl get secret backend-secrets -o jsonpath='{.data.DATABASE_URL}' | base64 -d
```

## Cleanup

```bash
# Remove deployments
helm uninstall frontend
helm uninstall backend
kubectl delete secret backend-secrets

# Stop Minikube (preserves state)
minikube stop

# Delete cluster (full cleanup)
minikube delete
```

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                      Minikube Cluster                       │
│                                                             │
│  ┌──────────────────┐         ┌──────────────────┐         │
│  │  Frontend Pod    │         │  Backend Pod     │         │
│  │  (Next.js)       │──HTTP──▶│  (FastAPI)       │──────┐  │
│  │  Port: 3000      │         │  Port: 8000      │      │  │
│  └────────┬─────────┘         └────────┬─────────┘      │  │
│           │                            │                │  │
│  ┌────────▼─────────┐         ┌────────▼─────────┐      │  │
│  │ Frontend Service │         │ Backend Service  │      │  │
│  │ NodePort: 30000  │         │ NodePort: 30080  │      │  │
│  └──────────────────┘         └──────────────────┘      │  │
│                                                         │  │
└─────────────────────────────────────────────────────────┼──┘
                                                          │
                                                 ┌────────▼────────┐
                                                 │  Neon Database  │
                                                 │  (PostgreSQL)   │
                                                 │    External     │
                                                 └─────────────────┘
```

## Files Structure

```
phase_4/
├── README.md                    # This file
├── docker-compose.yml           # Local development (non-K8s)
├── backend/
│   ├── Dockerfile               # Multi-stage FastAPI build
│   └── .dockerignore            # Build context exclusions
├── frontend/
│   ├── Dockerfile               # Multi-stage Next.js build
│   └── .dockerignore            # Build context exclusions
└── helm/
    ├── backend/
    │   ├── Chart.yaml           # Helm chart metadata
    │   ├── values.yaml          # Configurable values
    │   └── templates/
    │       ├── _helpers.tpl     # Template helpers
    │       ├── deployment.yaml  # Backend deployment
    │       ├── service.yaml     # Backend service
    │       └── configmap.yaml   # Environment config
    └── frontend/
        ├── Chart.yaml           # Helm chart metadata
        ├── values.yaml          # Configurable values
        └── templates/
            ├── _helpers.tpl     # Template helpers
            ├── deployment.yaml  # Frontend deployment
            └── service.yaml     # Frontend service
```

---

Generated by Claude Code following Spec-Driven Development principles.
