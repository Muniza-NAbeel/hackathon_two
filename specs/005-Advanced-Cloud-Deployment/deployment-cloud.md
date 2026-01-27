# Cloud Deployment Specification (DOKS/GKE/AKS)

## Overview

This specification defines production-grade Kubernetes deployment on cloud providers: DigitalOcean Kubernetes (DOKS), Google Kubernetes Engine (GKE), or Azure Kubernetes Service (AKS). The architecture remains consistent across providers with provider-specific configurations.

## Provider Options

| Provider | Service | Free Credits | Recommended For |
|----------|---------|--------------|-----------------|
| DigitalOcean | DOKS | $200/60 days | Simplicity, cost |
| Google Cloud | GKE | $300/90 days | GCP ecosystem |
| Azure | AKS | $200/30 days | Enterprise, .NET |

**Recommendation**: DigitalOcean DOKS for hackathon (simplest setup, generous credits).

---

## Architecture

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                        CLOUD KUBERNETES CLUSTER                              │
│                                                                              │
│  ┌────────────────────────────────────────────────────────────────────────┐ │
│  │                         INGRESS CONTROLLER                              │ │
│  │                    (nginx / cloud load balancer)                        │ │
│  └──────────────────────────────┬─────────────────────────────────────────┘ │
│                                 │                                            │
│  ┌──────────────────────────────┴─────────────────────────────────────────┐ │
│  │                           todo-app namespace                            │ │
│  │                                                                         │ │
│  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐    │ │
│  │  │  Frontend   │  │  Backend    │  │ Notification│  │  Recurring  │    │ │
│  │  │   (2 pods)  │  │  (3 pods)   │  │   (2 pods)  │  │  (2 pods)   │    │ │
│  │  │  + Dapr     │  │  + Dapr     │  │  + Dapr     │  │  + Dapr     │    │ │
│  │  └─────────────┘  └─────────────┘  └─────────────┘  └─────────────┘    │ │
│  │                                                                         │ │
│  │  ┌─────────────────────────────────────────────────────────────────┐   │ │
│  │  │                    DAPR CONTROL PLANE                            │   │ │
│  │  └─────────────────────────────────────────────────────────────────┘   │ │
│  └─────────────────────────────────────────────────────────────────────────┘ │
│                                                                              │
└──────────────────────────────────────────────────────────────────────────────┘
              │                    │                      │
              ▼                    ▼                      ▼
    ┌─────────────────┐   ┌─────────────────┐   ┌─────────────────┐
    │  Redpanda Cloud │   │  Neon PostgreSQL│   │ Container       │
    │  (Kafka)        │   │  (Database)     │   │ Registry        │
    │                 │   │                 │   │ (DOCR/GCR/ACR)  │
    └─────────────────┘   └─────────────────┘   └─────────────────┘
```

---

## Step 1: Cloud Provider Setup

### DigitalOcean (DOKS)

```bash
# Install doctl CLI
brew install doctl  # macOS
# or
snap install doctl  # Linux

# Authenticate
doctl auth init

# Create Kubernetes cluster
doctl kubernetes cluster create todo-cluster \
  --region nyc1 \
  --size s-2vcpu-4gb \
  --count 3 \
  --version 1.28.2-do.0

# Get kubeconfig
doctl kubernetes cluster kubeconfig save todo-cluster

# Verify
kubectl get nodes
```

### Google Cloud (GKE)

```bash
# Install gcloud CLI
# https://cloud.google.com/sdk/docs/install

# Authenticate
gcloud auth login
gcloud config set project YOUR_PROJECT_ID

# Create cluster
gcloud container clusters create todo-cluster \
  --zone us-central1-a \
  --num-nodes 3 \
  --machine-type e2-standard-2

# Get credentials
gcloud container clusters get-credentials todo-cluster --zone us-central1-a

# Verify
kubectl get nodes
```

### Azure (AKS)

```bash
# Install Azure CLI
# https://docs.microsoft.com/en-us/cli/azure/install-azure-cli

# Login
az login

# Create resource group
az group create --name todo-rg --location eastus

# Create cluster
az aks create \
  --resource-group todo-rg \
  --name todo-cluster \
  --node-count 3 \
  --node-vm-size Standard_B2s \
  --generate-ssh-keys

# Get credentials
az aks get-credentials --resource-group todo-rg --name todo-cluster

# Verify
kubectl get nodes
```

---

## Step 2: Container Registry Setup

### DigitalOcean Container Registry (DOCR)

```bash
# Create registry
doctl registry create todo-registry

# Login to registry
doctl registry login

# Get registry URL
REGISTRY="registry.digitalocean.com/todo-registry"

# Connect registry to cluster
doctl kubernetes cluster registry add todo-cluster
```

### Google Container Registry (GCR)

```bash
# Enable API
gcloud services enable containerregistry.googleapis.com

# Configure Docker
gcloud auth configure-docker

# Registry URL
REGISTRY="gcr.io/YOUR_PROJECT_ID"
```

### Azure Container Registry (ACR)

```bash
# Create registry
az acr create --resource-group todo-rg --name todoregistry --sku Basic

# Login
az acr login --name todoregistry

# Get registry URL
REGISTRY="todoregistry.azurecr.io"

# Attach to AKS
az aks update -n todo-cluster -g todo-rg --attach-acr todoregistry
```

---

## Step 3: Build and Push Images

```bash
# Build and tag images
docker build -t $REGISTRY/todo-backend:v1.0.0 -f phase_5/backend/Dockerfile phase_5/backend/
docker build -t $REGISTRY/todo-frontend:v1.0.0 -f phase_5/frontend/Dockerfile phase_5/frontend/
docker build -t $REGISTRY/notification-service:v1.0.0 -f phase_5/services/notification/Dockerfile phase_5/services/notification/
docker build -t $REGISTRY/recurring-task-service:v1.0.0 -f phase_5/services/recurring/Dockerfile phase_5/services/recurring/

# Push images
docker push $REGISTRY/todo-backend:v1.0.0
docker push $REGISTRY/todo-frontend:v1.0.0
docker push $REGISTRY/notification-service:v1.0.0
docker push $REGISTRY/recurring-task-service:v1.0.0
```

---

## Step 4: Setup External Services

### Redpanda Cloud (Kafka)

1. Sign up at https://redpanda.com/cloud
2. Create a Serverless cluster
3. Create topics:
   - `task-events` (3 partitions)
   - `reminders` (3 partitions)
   - `task-updates` (3 partitions)
4. Create service account credentials
5. Note the bootstrap server URL

### Neon PostgreSQL

Use existing Neon database from Phase 3/4:
- Ensure connection allows cloud IPs
- Note connection string

---

## Step 5: Install Dapr on Cloud Cluster

```bash
# Initialize Dapr (production mode)
dapr init -k --runtime-version 1.12.0

# Enable HA mode for production
dapr upgrade -k --runtime-version 1.12.0 --enable-ha=true

# Verify
dapr status -k
```

---

## Step 6: Create Namespace and Secrets

### Create Namespace

```bash
kubectl create namespace todo-app
kubectl config set-context --current --namespace=todo-app
```

### Create Secrets

**File**: `k8s/cloud/secrets.yaml`

```yaml
apiVersion: v1
kind: Secret
metadata:
  name: db-secrets
  namespace: todo-app
type: Opaque
stringData:
  connection-string: "postgresql://user:pass@neon-host:5432/todo?sslmode=require"
---
apiVersion: v1
kind: Secret
metadata:
  name: kafka-secrets
  namespace: todo-app
type: Opaque
stringData:
  brokers: "your-cluster.cloud.redpanda.com:9092"
  username: "your-username"
  password: "your-password"
---
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

```bash
# Apply secrets (edit with actual values first!)
kubectl apply -f k8s/cloud/secrets.yaml
```

---

## Step 7: Deploy Dapr Components (Cloud)

**File**: `k8s/cloud/dapr-components.yaml`

```yaml
# Kafka Pub/Sub - Cloud Configuration
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
      secretKeyRef:
        name: kafka-secrets
        key: brokers
    - name: consumerGroup
      value: "todo-app-consumers"
    - name: initialOffset
      value: "oldest"
    - name: authType
      value: "password"
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
    - name: tls
      value: "true"
---
# PostgreSQL State Store - Cloud Configuration
apiVersion: dapr.io/v1alpha1
kind: Component
metadata:
  name: statestore
  namespace: todo-app
spec:
  type: state.postgresql
  version: v1
  metadata:
    - name: connectionString
      secretKeyRef:
        name: db-secrets
        key: connection-string
    - name: tableName
      value: "dapr_state"
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
---
# Kubernetes Secrets Store
apiVersion: dapr.io/v1alpha1
kind: Component
metadata:
  name: kubernetes-secrets
  namespace: todo-app
spec:
  type: secretstores.kubernetes
  version: v1
```

```bash
kubectl apply -f k8s/cloud/dapr-components.yaml
```

---

## Step 8: Deploy Application (Cloud)

### Helm Chart Values (Cloud)

**File**: `helm/todo-app/values-cloud.yaml`

```yaml
global:
  registry: "registry.digitalocean.com/todo-registry"  # Change per provider
  imageTag: "v1.0.0"
  namespace: todo-app

backend:
  replicaCount: 3
  image: todo-backend
  port: 8000
  resources:
    requests:
      memory: "256Mi"
      cpu: "200m"
    limits:
      memory: "512Mi"
      cpu: "500m"
  dapr:
    enabled: true
    appId: "chat-backend"
    appPort: 8000

frontend:
  replicaCount: 2
  image: todo-frontend
  port: 3000
  resources:
    requests:
      memory: "256Mi"
      cpu: "200m"
    limits:
      memory: "512Mi"
      cpu: "500m"
  dapr:
    enabled: true
    appId: "chat-frontend"
    appPort: 3000

notificationService:
  replicaCount: 2
  image: notification-service
  port: 8001
  resources:
    requests:
      memory: "128Mi"
      cpu: "100m"
    limits:
      memory: "256Mi"
      cpu: "300m"
  dapr:
    enabled: true
    appId: "notification-service"
    appPort: 8001

recurringTaskService:
  replicaCount: 2
  image: recurring-task-service
  port: 8002
  resources:
    requests:
      memory: "128Mi"
      cpu: "100m"
    limits:
      memory: "256Mi"
      cpu: "300m"
  dapr:
    enabled: true
    appId: "recurring-task-service"
    appPort: 8002

ingress:
  enabled: true
  className: nginx
  annotations:
    cert-manager.io/cluster-issuer: letsencrypt-prod
  hosts:
    - host: todo.yourdomain.com
      paths:
        - path: /
          service: frontend
        - path: /api
          service: backend
  tls:
    - secretName: todo-tls
      hosts:
        - todo.yourdomain.com
```

### Deploy with Helm

```bash
# Install/upgrade
helm upgrade --install todo-app ./helm/todo-app \
  -f helm/todo-app/values-cloud.yaml \
  -n todo-app

# Verify
kubectl get pods -n todo-app
kubectl get svc -n todo-app
kubectl get ingress -n todo-app
```

---

## Step 9: Setup Ingress and TLS

### Install NGINX Ingress Controller

```bash
# DigitalOcean
kubectl apply -f https://raw.githubusercontent.com/kubernetes/ingress-nginx/controller-v1.9.0/deploy/static/provider/do/deploy.yaml

# GKE
kubectl apply -f https://raw.githubusercontent.com/kubernetes/ingress-nginx/controller-v1.9.0/deploy/static/provider/cloud/deploy.yaml

# AKS
kubectl apply -f https://raw.githubusercontent.com/kubernetes/ingress-nginx/controller-v1.9.0/deploy/static/provider/cloud/deploy.yaml
```

### Install Cert-Manager for TLS

```bash
# Install cert-manager
kubectl apply -f https://github.com/cert-manager/cert-manager/releases/download/v1.13.0/cert-manager.yaml

# Create ClusterIssuer for Let's Encrypt
cat <<EOF | kubectl apply -f -
apiVersion: cert-manager.io/v1
kind: ClusterIssuer
metadata:
  name: letsencrypt-prod
spec:
  acme:
    server: https://acme-v02.api.letsencrypt.org/directory
    email: your-email@example.com
    privateKeySecretRef:
      name: letsencrypt-prod
    solvers:
    - http01:
        ingress:
          class: nginx
EOF
```

---

## Step 10: Configure DNS

1. Get Load Balancer IP:
```bash
kubectl get svc -n ingress-nginx
# Note EXTERNAL-IP
```

2. Create DNS A record:
   - `todo.yourdomain.com` → Load Balancer IP

3. Verify DNS propagation:
```bash
dig todo.yourdomain.com
```

---

## Step 11: Monitoring and Logging

### Option 1: DigitalOcean Monitoring

```bash
# Enable monitoring addon
doctl kubernetes cluster update todo-cluster --enable-monitoring
```

### Option 2: Prometheus + Grafana

```bash
# Add Helm repo
helm repo add prometheus-community https://prometheus-community.github.io/helm-charts

# Install kube-prometheus-stack
helm install prometheus prometheus-community/kube-prometheus-stack \
  -n monitoring --create-namespace

# Access Grafana
kubectl port-forward svc/prometheus-grafana 3000:80 -n monitoring
# Default credentials: admin/prom-operator
```

### Dapr Dashboard

```bash
# Port forward Dapr dashboard
dapr dashboard -k -p 8080
```

---

## Verification Checklist

| Check | Command | Expected |
|-------|---------|----------|
| All pods running | `kubectl get pods -n todo-app` | All STATUS=Running, READY=2/2 |
| Dapr components | `kubectl get components -n todo-app` | All components listed |
| Ingress configured | `kubectl get ingress -n todo-app` | ADDRESS populated |
| TLS certificate | `kubectl get certificate -n todo-app` | Ready=True |
| Kafka connected | Check Dapr sidecar logs | "Connected to Kafka" |
| API health | `curl https://todo.yourdomain.com/api/health` | 200 OK |

---

## Cost Optimization

### DigitalOcean

| Resource | Size | Monthly Cost |
|----------|------|--------------|
| DOKS Cluster (3 nodes) | s-2vcpu-4gb | ~$36 |
| Load Balancer | Small | ~$12 |
| Container Registry | Basic | ~$5 |
| **Total** | | ~$53/month |

### Tips

1. Use Horizontal Pod Autoscaler to scale down during low traffic
2. Choose smaller node sizes for dev/staging
3. Use spot/preemptible instances where available
4. Monitor and right-size resources

---

## Rollback Procedure

```bash
# List releases
helm history todo-app -n todo-app

# Rollback to previous version
helm rollback todo-app 1 -n todo-app

# Or rollback to specific revision
helm rollback todo-app <REVISION> -n todo-app
```

---

## Cleanup

```bash
# Delete Helm release
helm uninstall todo-app -n todo-app

# Delete namespace
kubectl delete namespace todo-app

# Delete cluster (provider-specific)
# DigitalOcean
doctl kubernetes cluster delete todo-cluster

# GKE
gcloud container clusters delete todo-cluster --zone us-central1-a

# AKS
az aks delete --resource-group todo-rg --name todo-cluster
```
