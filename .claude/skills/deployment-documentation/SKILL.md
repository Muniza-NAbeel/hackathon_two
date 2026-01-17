---
name: deployment-documentation
description: Create and maintain Phase IV deployment documentation including README files with Minikube setup instructions, deployment steps, service access commands, and troubleshooting guides. Use when documenting deployment processes, writing setup instructions, updating documentation after infrastructure changes, or preparing Phase IV submission materials.
allowed-tools: Write, Read, Glob, Grep
---

# Deployment Documentation Skill

## Purpose

I help you create clear, comprehensive documentation for your Phase IV Kubernetes and containerized application deployments. Good documentation makes onboarding faster, troubleshooting easier, and ensures successful hackathon submission.

## When to Use This Skill

Ask me to help with:
- Writing deployment setup instructions
- Creating service access command references
- Documenting troubleshooting procedures
- Adding prerequisites and requirements
- Creating Quick Start guides
- Writing configuration documentation
- Maintaining deployment README files
- Preparing Phase IV submission documentation

## Documentation Structure

I create documentation following this structure:

```
# Service/Application Name

## Overview
Brief description and purpose

## Prerequisites
Required software and versions

## Quick Start
Step-by-step commands to get running

## Configuration
Environment variables and settings

## Accessing Services
URLs, ports, and access methods

## Troubleshooting
Common issues and solutions

## Commands Reference
Quick lookup table
```

## Phase IV README Template

```markdown
# Todo AI Chatbot - Phase IV: Local Kubernetes Deployment

## Overview

This guide covers deploying the Todo AI Chatbot application (Phase III) to a local
Minikube Kubernetes cluster using Docker containers and Helm charts.

### Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    MINIKUBE CLUSTER                         │
│                                                             │
│  ┌─────────────────┐         ┌─────────────────┐           │
│  │   Frontend      │         │   Backend       │           │
│  │   (Next.js)     │────────▶│   (FastAPI)     │           │
│  │   Port: 3000    │         │   Port: 8000    │           │
│  └─────────────────┘         └────────┬────────┘           │
│                                       │                     │
│                                       ▼                     │
│                              ┌─────────────────┐           │
│                              │   Neon DB       │           │
│                              │   (External)    │           │
│                              └─────────────────┘           │
└─────────────────────────────────────────────────────────────┘
```

## Prerequisites

### Required Software

| Software | Version | Installation |
|----------|---------|--------------|
| Docker Desktop | 20.10+ | [docker.com](https://docker.com) |
| Minikube | 1.30+ | `brew install minikube` or [minikube.sigs.k8s.io](https://minikube.sigs.k8s.io) |
| kubectl | 1.25+ | Comes with Docker Desktop |
| Helm | 3.10+ | `brew install helm` or [helm.sh](https://helm.sh) |

### Verify Installation

```bash
docker --version      # Docker version 20.10+
minikube version      # minikube version: v1.30+
kubectl version       # Client Version: v1.25+
helm version          # version.BuildInfo{Version:"v3.10+"}
```

### WSL2 Users (Windows)

Ensure WSL2 integration is enabled in Docker Desktop:
1. Docker Desktop → Settings → Resources → WSL Integration
2. Enable integration with your distro

## Quick Start

### 1. Clone and Navigate

```bash
git clone <repository-url>
cd hackathon_two
```

### 2. Start Minikube

```bash
# Start cluster with adequate resources
minikube start --driver=docker --cpus=4 --memory=8192

# Verify cluster is running
minikube status
kubectl get nodes
```

### 3. Build Docker Images

```bash
# IMPORTANT: Point to Minikube's Docker daemon
eval $(minikube docker-env)

# Build images
docker build -t todo-backend:latest ./phase_3/backend
docker build -t todo-frontend:latest ./phase_3/frontend

# Verify images
docker images | grep todo
```

### 4. Deploy with Helm

```bash
# Install backend
helm install todo-backend ./helm/backend \
  --set image.pullPolicy=Never

# Install frontend
helm install todo-frontend ./helm/frontend \
  --set image.pullPolicy=Never

# Verify deployments
kubectl get pods
kubectl get svc
```

### 5. Access Application

```bash
# Option A: Port-forward (recommended)
kubectl port-forward svc/todo-backend 8000:8000 &
kubectl port-forward svc/todo-frontend 3000:3000 &

# Option B: Minikube service
minikube service todo-frontend --url
```

### 6. Test Deployment

```bash
# Test backend health
curl http://localhost:8000/api/health

# Open frontend
open http://localhost:3000
```

## Configuration

### Environment Variables

Create `.env` files before building:

**Backend** (`phase_3/backend/.env`):
```env
DATABASE_URL=postgresql://user:pass@host:5432/dbname
OPENAI_API_KEY=sk-...
BETTER_AUTH_SECRET=your-secret-key
ENVIRONMENT=development
LOG_LEVEL=info
```

**Frontend** (`phase_3/frontend/.env`):
```env
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_BETTER_AUTH_URL=http://localhost:3000
```

### Helm Values Override

Create `values-local.yaml` for local settings:

```yaml
# values-local.yaml
replicaCount: 1
image:
  pullPolicy: Never
resources:
  requests:
    cpu: 100m
    memory: 128Mi
  limits:
    cpu: 500m
    memory: 512Mi
```

## Service Access Reference

| Service | Internal Port | Access Method | URL |
|---------|--------------|---------------|-----|
| Backend API | 8000 | Port-forward | http://localhost:8000 |
| Frontend | 3000 | Port-forward | http://localhost:3000 |
| Backend API | 8000 | NodePort | http://$(minikube ip):30800 |
| Frontend | 3000 | NodePort | http://$(minikube ip):30300 |

### Port-Forward Commands

```bash
# Backend (run in background)
kubectl port-forward svc/todo-backend 8000:8000 &

# Frontend (run in background)
kubectl port-forward svc/todo-frontend 3000:3000 &

# Stop port-forwards
pkill -f "port-forward"
```

### Test API Endpoints

```bash
# Health check
curl http://localhost:8000/api/health

# API docs
open http://localhost:8000/docs
```

## Troubleshooting

### Pods Not Starting (Pending)

```bash
# Check pod events
kubectl describe pod <pod-name>

# Common causes:
# - Insufficient resources → Increase Minikube memory
# - Image not found → Rebuild with eval $(minikube docker-env)
```

### Application Crashes (CrashLoopBackOff)

```bash
# View application logs
kubectl logs <pod-name>
kubectl logs <pod-name> --previous

# Common causes:
# - Missing environment variables
# - Database connection issues
# - Application errors
```

### Service Not Accessible

```bash
# Verify service exists
kubectl get svc

# Check endpoints
kubectl get endpoints

# Test internal connectivity
kubectl run test --rm -it --image=busybox -- wget -qO- http://todo-backend:8000/api/health
```

### Image Pull Errors

```bash
# Ensure using Minikube Docker
eval $(minikube docker-env)

# Verify image exists
docker images | grep todo

# Check Helm values
helm get values todo-backend
# Ensure: image.pullPolicy: Never
```

### Database Connection Issues

```bash
# Check environment variables in pod
kubectl exec deployment/todo-backend -- env | grep DATABASE

# Verify external connectivity
kubectl exec deployment/todo-backend -- nc -zv <db-host> 5432
```

## Cleanup

```bash
# Delete Helm releases
helm uninstall todo-backend
helm uninstall todo-frontend

# Stop Minikube (preserves data)
minikube stop

# Delete Minikube cluster (removes everything)
minikube delete
```

## Commands Quick Reference

| Task | Command |
|------|---------|
| Start Minikube | `minikube start --driver=docker` |
| Use Minikube Docker | `eval $(minikube docker-env)` |
| Build backend | `docker build -t todo-backend:latest ./phase_3/backend` |
| Build frontend | `docker build -t todo-frontend:latest ./phase_3/frontend` |
| Install backend | `helm install todo-backend ./helm/backend` |
| Install frontend | `helm install todo-frontend ./helm/frontend` |
| View pods | `kubectl get pods` |
| View logs | `kubectl logs deployment/todo-backend` |
| Port-forward backend | `kubectl port-forward svc/todo-backend 8000:8000` |
| Port-forward frontend | `kubectl port-forward svc/todo-frontend 3000:3000` |
| Stop Minikube | `minikube stop` |

## Project Structure

```
hackathon_two/
├── phase_3/
│   ├── backend/
│   │   ├── Dockerfile
│   │   ├── .dockerignore
│   │   └── ...
│   └── frontend/
│       ├── Dockerfile
│       ├── .dockerignore
│       └── ...
├── helm/
│   ├── backend/
│   │   ├── Chart.yaml
│   │   ├── values.yaml
│   │   └── templates/
│   └── frontend/
│       ├── Chart.yaml
│       ├── values.yaml
│       └── templates/
└── README.md
```
```

## Key Documentation Principles

1. **Progressive disclosure** - Start simple, add details progressively
2. **Copy-paste ready** - Provide exact commands users can run
3. **Troubleshooting first** - Anticipate and document common problems
4. **Visual aids** - Use ASCII diagrams and tables
5. **Step numbers** - Numbered steps for clarity
6. **Code blocks** - Use proper syntax highlighting
7. **Version specifics** - Document required versions

## When to Update Documentation

Update documentation when:
- Adding new services or components
- Changing port configurations
- Modifying deployment process
- Discovering new troubleshooting solutions
- Adding new environment variables
- After infrastructure changes
- Before Phase IV submission
