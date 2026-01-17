---
name: minikube-deployment
description: Deploy containerized applications to local Minikube Kubernetes clusters. Includes starting Minikube, building Docker images, installing Helm charts, exposing services via NodePort or port-forwarding, and verifying application accessibility. Use when deploying to local Kubernetes, testing deployments locally, or setting up Phase IV development environments.
allowed-tools: Bash(minikube:*), Bash(docker:*), Bash(kubectl:*), Bash(helm:*), Bash(curl:*), Read, Write, Glob
---

# Minikube Deployment Skill

## Purpose

I help you deploy and test the Todo AI Chatbot application in a local Minikube Kubernetes cluster. This provides a safe environment to test Kubernetes deployments before pushing to production (Phase V).

## When to Use This Skill

Ask me to help with:
- Starting and managing local Minikube cluster
- Building Docker images in Minikube environment
- Deploying applications using Helm charts
- Exposing services via NodePort or port-forwarding
- Verifying application accessibility
- Troubleshooting local Kubernetes deployments
- Testing Helm chart configurations
- Phase IV local Kubernetes checkpoint

## Prerequisites

Required software:
- Docker Desktop installed and running
- Minikube installed
- kubectl installed
- Helm 3+ installed

## Complete Deployment Workflow

### Step 1: Start Minikube Cluster

```bash
# Start with Docker driver (recommended for WSL2)
minikube start --driver=docker --cpus=4 --memory=8192

# Verify cluster is running
minikube status

# Check cluster info
kubectl cluster-info
kubectl get nodes
```

### Step 2: Configure Docker Environment

```bash
# Point Docker CLI to Minikube's Docker daemon
# IMPORTANT: Run this in every new terminal session
eval $(minikube docker-env)

# Verify - should show Minikube's Docker
docker info | grep -i name
```

### Step 3: Build Docker Images

```bash
# Navigate to project root
cd /mnt/d/assignments/hackathon_two

# Build backend image
docker build -t todo-backend:latest ./phase_3/backend

# Build frontend image
docker build -t todo-frontend:latest ./phase_3/frontend

# Verify images are in Minikube
docker images | grep todo
```

### Step 4: Deploy with Helm

```bash
# Create namespace (optional)
kubectl create namespace todo-app

# Install backend
helm install todo-backend ./helm/backend \
  --namespace todo-app \
  --set image.repository=todo-backend \
  --set image.tag=latest \
  --set image.pullPolicy=Never

# Install frontend
helm install todo-frontend ./helm/frontend \
  --namespace todo-app \
  --set image.repository=todo-frontend \
  --set image.tag=latest \
  --set image.pullPolicy=Never

# Check deployment status
kubectl get all -n todo-app
```

### Step 5: Expose Services

**Option A: NodePort (Persistent Access)**

```bash
# Upgrade service to NodePort
helm upgrade todo-backend ./helm/backend \
  --namespace todo-app \
  --set service.type=NodePort \
  --set service.nodePort=30800

helm upgrade todo-frontend ./helm/frontend \
  --namespace todo-app \
  --set service.type=NodePort \
  --set service.nodePort=30300

# Get Minikube IP and access URLs
minikube service todo-backend -n todo-app --url
minikube service todo-frontend -n todo-app --url
```

**Option B: Port-Forward (Temporary Access)**

```bash
# Terminal 1: Backend
kubectl port-forward svc/todo-backend 8000:8000 -n todo-app

# Terminal 2: Frontend
kubectl port-forward svc/todo-frontend 3000:3000 -n todo-app

# Access at:
# Backend: http://localhost:8000
# Frontend: http://localhost:3000
```

**Option C: Minikube Tunnel (LoadBalancer)**

```bash
# Start tunnel (requires sudo)
minikube tunnel

# Services with type LoadBalancer get external IPs
kubectl get svc -n todo-app
```

### Step 6: Verify Deployment

```bash
# Check all resources
kubectl get all -n todo-app

# Check pod status
kubectl get pods -n todo-app -o wide

# View pod logs
kubectl logs deployment/todo-backend -n todo-app
kubectl logs deployment/todo-frontend -n todo-app

# Test backend health
curl http://localhost:8000/api/health

# Test frontend
curl http://localhost:3000
```

## Troubleshooting Commands

### Pod Issues

```bash
# Pod stuck in Pending
kubectl describe pod <pod-name> -n todo-app
# Usually: resource constraints or image not found

# Pod in CrashLoopBackOff
kubectl logs <pod-name> -n todo-app --previous
# Check application errors

# Pod in ImagePullBackOff
# Verify image exists in Minikube Docker
eval $(minikube docker-env)
docker images | grep todo
# Ensure imagePullPolicy: Never in Helm values
```

### Service Issues

```bash
# Service not accessible
kubectl get svc -n todo-app
kubectl get endpoints -n todo-app

# Check if pods are ready
kubectl get pods -n todo-app

# Test service internally
kubectl run curl --image=curlimages/curl -it --rm -- \
  curl http://todo-backend.todo-app.svc.cluster.local:8000/api/health
```

### Resource Issues

```bash
# Check resource usage
kubectl top pods -n todo-app
kubectl top nodes

# Describe node for capacity
kubectl describe node minikube

# Increase Minikube resources
minikube stop
minikube config set cpus 4
minikube config set memory 8192
minikube start
```

## Common Issues & Solutions

| Issue | Cause | Solution |
|-------|-------|----------|
| Image not found | Built outside Minikube Docker | Run `eval $(minikube docker-env)` first |
| Pods Pending | Resource constraints | Increase Minikube resources |
| CrashLoopBackOff | App error | Check logs: `kubectl logs <pod>` |
| Service unreachable | Wrong service type | Use NodePort or port-forward |
| Connection refused | Pod not ready | Wait for readiness probe |
| DNS not resolving | CoreDNS issue | `kubectl rollout restart deployment/coredns -n kube-system` |

## Useful Minikube Commands

```bash
# Dashboard (visual management)
minikube dashboard

# SSH into Minikube VM
minikube ssh

# Check addons
minikube addons list

# Enable ingress addon
minikube addons enable ingress

# Get Minikube IP
minikube ip

# Pause/Unpause (save resources)
minikube pause
minikube unpause

# Stop cluster
minikube stop

# Delete cluster
minikube delete
```

## Cleanup

```bash
# Delete Helm releases
helm uninstall todo-backend -n todo-app
helm uninstall todo-frontend -n todo-app

# Delete namespace
kubectl delete namespace todo-app

# Stop Minikube (preserves cluster)
minikube stop

# Delete Minikube cluster (permanent)
minikube delete --all
```

## Quick Reference

| Task | Command |
|------|---------|
| Start cluster | `minikube start --driver=docker` |
| Use Minikube Docker | `eval $(minikube docker-env)` |
| Build image | `docker build -t name:tag .` |
| Install Helm chart | `helm install name ./chart` |
| Port-forward | `kubectl port-forward svc/name 8000:8000` |
| View logs | `kubectl logs deployment/name` |
| Check status | `kubectl get all` |
| Stop cluster | `minikube stop` |
