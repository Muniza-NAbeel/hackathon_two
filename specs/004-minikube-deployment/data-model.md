# Data Model: Phase 4 - Infrastructure Entities

**Feature**: 004-minikube-deployment | **Date**: 2026-01-13

## Overview

This document defines the key infrastructure entities for Phase 4 Kubernetes deployment. Unlike application phases, Phase 4 focuses on deployment artifacts rather than database models.

---

## 1. Docker Image Entities

### 1.1 Backend Image

| Attribute | Value | Description |
|-----------|-------|-------------|
| **Name** | `todo-backend` | Image name in Minikube registry |
| **Tag** | `latest` | Version tag (latest for dev) |
| **Base Image** | `python:3.11-slim` | Production base |
| **Exposed Port** | `8000` | FastAPI server port |
| **User** | `appuser (uid 1000)` | Non-root runtime user |
| **Entrypoint** | `uvicorn app.main:app` | Application startup |

**Build Context**: `phase_3/backend/`
**Dockerfile Location**: `phase_4/backend/Dockerfile`

### 1.2 Frontend Image

| Attribute | Value | Description |
|-----------|-------|-------------|
| **Name** | `todo-frontend` | Image name in Minikube registry |
| **Tag** | `latest` | Version tag (latest for dev) |
| **Base Image** | `node:18-alpine` | Production base |
| **Exposed Port** | `3000` | Next.js server port |
| **User** | `nextjs (uid 1001)` | Non-root runtime user |
| **Entrypoint** | `node server.js` | Standalone server |

**Build Context**: `phase_3/frontend/`
**Dockerfile Location**: `phase_4/frontend/Dockerfile`

---

## 2. Kubernetes Resource Entities

### 2.1 Deployment Resources

#### Backend Deployment

```yaml
Entity: Deployment
Name: backend
Namespace: default
Labels:
  app: backend
  tier: api
Spec:
  Replicas: 1
  Container:
    Image: todo-backend:latest
    Port: 8000
    Resources:
      Requests: 100m CPU, 128Mi Memory
      Limits: 500m CPU, 512Mi Memory
    Probes:
      Liveness: /health, delay 30s
      Readiness: /health, delay 10s
```

#### Frontend Deployment

```yaml
Entity: Deployment
Name: frontend
Namespace: default
Labels:
  app: frontend
  tier: ui
Spec:
  Replicas: 1
  Container:
    Image: todo-frontend:latest
    Port: 3000
    Resources:
      Requests: 50m CPU, 64Mi Memory
      Limits: 250m CPU, 256Mi Memory
    Probes:
      Liveness: /, delay 30s
      Readiness: /, delay 10s
```

### 2.2 Service Resources

#### Backend Service

| Attribute | Value |
|-----------|-------|
| **Name** | `backend` |
| **Type** | `NodePort` |
| **Port** | `8000` |
| **TargetPort** | `8000` |
| **NodePort** | `30080` |
| **Selector** | `app: backend` |

#### Frontend Service

| Attribute | Value |
|-----------|-------|
| **Name** | `frontend` |
| **Type** | `NodePort` |
| **Port** | `3000` |
| **TargetPort** | `3000` |
| **NodePort** | `30000` |
| **Selector** | `app: frontend` |

### 2.3 Configuration Resources

#### Backend ConfigMap

```yaml
Entity: ConfigMap
Name: backend-config
Data:
  LOG_LEVEL: "INFO"
  APP_ENV: "production"
  CORS_ORIGINS: "*"
```

#### Backend Secrets

```yaml
Entity: Secret
Name: backend-secrets
Type: Opaque
Data:
  DATABASE_URL: <base64-encoded>
  GEMINI_API_KEY: <base64-encoded>
  JWT_SECRET: <base64-encoded>
```

---

## 3. Helm Chart Entities

### 3.1 Backend Chart

| Attribute | Value |
|-----------|-------|
| **Chart Name** | `backend` |
| **Version** | `0.1.0` |
| **App Version** | `1.0.0` |
| **API Version** | `v2` |

**Templates**:
- `deployment.yaml` - Backend Deployment
- `service.yaml` - NodePort Service
- `configmap.yaml` - Configuration data
- `_helpers.tpl` - Template functions

### 3.2 Frontend Chart

| Attribute | Value |
|-----------|-------|
| **Chart Name** | `frontend` |
| **Version** | `0.1.0` |
| **App Version** | `1.0.0` |
| **API Version** | `v2` |

**Templates**:
- `deployment.yaml` - Frontend Deployment
- `service.yaml` - NodePort Service
- `_helpers.tpl` - Template functions

---

## 4. Environment Variable Contract

### 4.1 Backend Required Variables

| Variable | Source | Required | Description |
|----------|--------|----------|-------------|
| `DATABASE_URL` | Secret | Yes | Neon PostgreSQL connection string |
| `GEMINI_API_KEY` | Secret | Yes | Google Gemini API key |
| `JWT_SECRET` | Secret | Yes | JWT token signing key |
| `JWT_ALGORITHM` | ConfigMap | No | JWT algorithm (default: HS256) |
| `ACCESS_TOKEN_EXPIRE_DAYS` | ConfigMap | No | Token expiry days (default: 7) |
| `DEBUG` | ConfigMap | No | Debug mode (default: False) |
| `CORS_ORIGINS` | ConfigMap | No | Allowed CORS origins |

### 4.2 Frontend Required Variables

| Variable | Source | Required | Description |
|----------|--------|----------|-------------|
| `NEXT_PUBLIC_API_URL` | ConfigMap | Yes | Backend API base URL |
| `NODE_ENV` | Dockerfile | No | Runtime environment (default: production) |

---

## 5. Resource Relationships

```
┌─────────────────────────────────────────────────────────────────┐
│                        Minikube Cluster                         │
│                                                                 │
│  ┌──────────────────┐           ┌──────────────────┐           │
│  │   Frontend Pod   │           │   Backend Pod    │           │
│  │  ┌────────────┐  │           │  ┌────────────┐  │           │
│  │  │ Container  │  │    HTTP   │  │ Container  │  │           │
│  │  │ (Next.js)  │──┼───────────┼─▶│ (FastAPI)  │──┼──────┐    │
│  │  └────────────┘  │           │  └────────────┘  │      │    │
│  └────────┬─────────┘           └────────┬─────────┘      │    │
│           │                              │                │    │
│  ┌────────▼─────────┐           ┌────────▼─────────┐      │    │
│  │ Frontend Service │           │ Backend Service  │      │    │
│  │   (NodePort)     │           │   (NodePort)     │      │    │
│  │   Port: 30000    │           │   Port: 30080    │      │    │
│  └──────────────────┘           └──────────────────┘      │    │
│                                                           │    │
│  ┌──────────────────┐           ┌──────────────────┐      │    │
│  │  Frontend Helm   │           │  Backend Helm    │      │    │
│  │     Chart        │           │     Chart        │      │    │
│  └──────────────────┘           └──────────────────┘      │    │
│                                                           │    │
└───────────────────────────────────────────────────────────┼────┘
                                                            │
                                                   ┌────────▼────────┐
                                                   │  Neon Database  │
                                                   │  (PostgreSQL)   │
                                                   │    External     │
                                                   └─────────────────┘
```

---

## 6. File Artifact Mapping

| Entity | File Path | Generated By |
|--------|-----------|--------------|
| Backend Dockerfile | `phase_4/backend/Dockerfile` | docker-ai-agent |
| Backend .dockerignore | `phase_4/backend/.dockerignore` | docker-ai-agent |
| Frontend Dockerfile | `phase_4/frontend/Dockerfile` | docker-ai-agent |
| Frontend .dockerignore | `phase_4/frontend/.dockerignore` | docker-ai-agent |
| Backend Chart.yaml | `phase_4/helm/backend/Chart.yaml` | helm-chart-agent |
| Backend values.yaml | `phase_4/helm/backend/values.yaml` | helm-chart-agent |
| Backend deployment.yaml | `phase_4/helm/backend/templates/deployment.yaml` | helm-chart-agent |
| Backend service.yaml | `phase_4/helm/backend/templates/service.yaml` | helm-chart-agent |
| Backend configmap.yaml | `phase_4/helm/backend/templates/configmap.yaml` | helm-chart-agent |
| Frontend Chart.yaml | `phase_4/helm/frontend/Chart.yaml` | helm-chart-agent |
| Frontend values.yaml | `phase_4/helm/frontend/values.yaml` | helm-chart-agent |
| Frontend deployment.yaml | `phase_4/helm/frontend/templates/deployment.yaml` | helm-chart-agent |
| Frontend service.yaml | `phase_4/helm/frontend/templates/service.yaml` | helm-chart-agent |
| README.md | `phase_4/README.md` | documentation-agent |
