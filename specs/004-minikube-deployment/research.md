# Research: Phase 4 - Local Kubernetes Deployment

**Feature**: 004-minikube-deployment | **Date**: 2026-01-13

## Overview

This research document captures technical findings for deploying the Phase 3 Todo AI Chatbot application to a local Kubernetes cluster using Minikube. Focus areas include containerization best practices, Helm chart patterns, and local Kubernetes configuration.

---

## 1. Docker Multi-Stage Build Patterns

### 1.1 Python/FastAPI Backend

**Best Practice Pattern**:
```dockerfile
# Stage 1: Dependencies
FROM python:3.11-slim as builder
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir --target=/app/dependencies -r requirements.txt

# Stage 2: Production
FROM python:3.11-slim
WORKDIR /app
COPY --from=builder /app/dependencies /usr/local/lib/python3.11/site-packages
COPY . .
RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app
USER appuser
EXPOSE 8000
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

**Key Findings**:
- Use `python:3.11-slim` over `alpine` for better compatibility with compiled dependencies
- Install dependencies in builder stage to reduce final image size
- Non-root user (uid 1000) is Kubernetes best practice
- `PYTHONUNBUFFERED=1` ensures logs appear immediately

**Image Size Comparison**:
| Approach | Size |
|----------|------|
| Single stage (python:3.11) | ~1.2GB |
| Multi-stage (python:3.11-slim) | ~200-300MB |

### 1.2 Next.js Frontend

**Best Practice Pattern**:
```dockerfile
# Stage 1: Dependencies
FROM node:18-alpine AS deps
WORKDIR /app
COPY package*.json ./
RUN npm ci --only=production

# Stage 2: Build
FROM node:18-alpine AS builder
WORKDIR /app
COPY --from=deps /app/node_modules ./node_modules
COPY . .
RUN npm run build

# Stage 3: Production
FROM node:18-alpine AS runner
WORKDIR /app
ENV NODE_ENV=production
RUN addgroup -g 1001 -S nodejs && adduser -S nextjs -u 1001
COPY --from=builder --chown=nextjs:nodejs /app/.next/standalone ./
COPY --from=builder --chown=nextjs:nodejs /app/.next/static ./.next/static
COPY --from=builder --chown=nextjs:nodejs /app/public ./public
USER nextjs
EXPOSE 3000
CMD ["node", "server.js"]
```

**Key Findings**:
- Requires `output: 'standalone'` in next.config.js
- Three stages optimal: deps, build, production
- Alpine base works well for Node.js
- Standalone output reduces image to ~100MB vs ~1GB with node_modules

**Next.js Configuration Required**:
```javascript
// next.config.js
module.exports = {
  output: 'standalone',
}
```

---

## 2. Kubernetes Deployment Patterns

### 2.1 Deployment Resource Best Practices

**Recommended Deployment Structure**:
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: backend
  labels:
    app: backend
spec:
  replicas: 1
  selector:
    matchLabels:
      app: backend
  template:
    metadata:
      labels:
        app: backend
    spec:
      containers:
      - name: backend
        image: todo-backend:latest
        imagePullPolicy: Never  # For local images
        ports:
        - containerPort: 8000
        resources:
          requests:
            cpu: "100m"
            memory: "128Mi"
          limits:
            cpu: "500m"
            memory: "512Mi"
        livenessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 10
          periodSeconds: 5
        envFrom:
        - configMapRef:
            name: backend-config
        - secretRef:
            name: backend-secrets
```

**Key Findings**:
- `imagePullPolicy: Never` required for local Minikube images
- Resource requests/limits prevent node exhaustion
- Liveness vs Readiness probes serve different purposes:
  - Liveness: Restart unhealthy containers
  - Readiness: Remove from service until ready
- Separate ConfigMaps and Secrets for configuration

### 2.2 Service Exposure Methods

| Method | Use Case | Pros | Cons |
|--------|----------|------|------|
| **NodePort** | Local development | Simple, direct access | Port range 30000-32767 |
| **LoadBalancer** | Cloud deployment | External IP | Not available in Minikube without tunnel |
| **Ingress** | Production | Path-based routing | Requires Ingress controller |
| **Port-forward** | Debugging | No service changes | Temporary, single user |

**Recommendation for Minikube**: NodePort services for persistent access, with `minikube service` command for automatic URL discovery.

### 2.3 ConfigMap vs Secret

**ConfigMap** (non-sensitive):
```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: backend-config
data:
  LOG_LEVEL: "INFO"
  APP_ENV: "production"
```

**Secret** (sensitive):
```yaml
apiVersion: v1
kind: Secret
metadata:
  name: backend-secrets
type: Opaque
stringData:
  DATABASE_URL: "postgresql://..."
  GEMINI_API_KEY: "AIza..."
  JWT_SECRET: "your-jwt-secret"
```

**Key Finding**: Never commit Secrets to version control. Use `kubectl create secret` with environment variables at deployment time.

---

## 3. Helm Chart Conventions

### 3.1 Standard Directory Structure

```
chart-name/
├── Chart.yaml          # Chart metadata
├── values.yaml         # Default configuration
├── templates/
│   ├── _helpers.tpl    # Template helpers
│   ├── deployment.yaml
│   ├── service.yaml
│   ├── configmap.yaml
│   └── NOTES.txt       # Post-install instructions
└── .helmignore
```

### 3.2 Values.yaml Best Practices

```yaml
# values.yaml
replicaCount: 1

image:
  repository: todo-backend
  tag: "latest"
  pullPolicy: Never

service:
  type: NodePort
  port: 8000
  nodePort: 30080

resources:
  requests:
    cpu: "100m"
    memory: "128Mi"
  limits:
    cpu: "500m"
    memory: "512Mi"

probes:
  liveness:
    path: /health
    initialDelaySeconds: 30
  readiness:
    path: /health
    initialDelaySeconds: 10

env: {}
  # DATABASE_URL: ""
  # Set via --set or values override
```

**Key Findings**:
- Use hierarchical structure for related values
- Provide sensible defaults for local development
- Document required overrides with comments
- Use `{{ .Values.x }}` templating for flexibility

### 3.3 Template Helpers (_helpers.tpl)

```yaml
{{/*
Common labels
*/}}
{{- define "backend.labels" -}}
helm.sh/chart: {{ .Chart.Name }}-{{ .Chart.Version }}
app.kubernetes.io/name: {{ .Chart.Name }}
app.kubernetes.io/instance: {{ .Release.Name }}
{{- end }}

{{/*
Selector labels
*/}}
{{- define "backend.selectorLabels" -}}
app.kubernetes.io/name: {{ .Chart.Name }}
app.kubernetes.io/instance: {{ .Release.Name }}
{{- end }}
```

---

## 4. Minikube Configuration

### 4.1 Resource Requirements

**Minimum Requirements**:
- CPUs: 4
- Memory: 8GB
- Disk: 20GB

**Recommended Start Command**:
```bash
minikube start --cpus=4 --memory=8192 --disk-size=20g --driver=docker
```

### 4.2 Docker Environment Configuration

**Critical Step**: Build images inside Minikube's Docker daemon:
```bash
eval $(minikube docker-env)
```

**Verification**:
```bash
docker images  # Should show Minikube's images, not host's
```

### 4.3 Useful Minikube Commands

| Command | Purpose |
|---------|---------|
| `minikube start` | Start cluster |
| `minikube stop` | Stop cluster (preserves state) |
| `minikube delete` | Delete cluster |
| `minikube status` | Check cluster status |
| `minikube service <name>` | Open service in browser |
| `minikube service <name> --url` | Get service URL |
| `minikube dashboard` | Open Kubernetes dashboard |
| `minikube logs` | View cluster logs |

### 4.4 Common Issues and Solutions

| Issue | Cause | Solution |
|-------|-------|----------|
| ImagePullBackOff | Image not in Minikube | Run `eval $(minikube docker-env)` before build |
| Pod CrashLoopBackOff | Missing env vars | Check `kubectl logs <pod>` for details |
| Service not accessible | Wrong service type | Use NodePort for local access |
| Out of memory | Insufficient resources | Increase Minikube memory allocation |

---

## 5. Phase 3 Application Analysis

### 5.1 Backend (FastAPI)

**Entry Point**: `app/main.py`
**Health Endpoint**: `/health` (assumed, needs verification)
**Port**: 8000
**Dependencies**: requirements.txt

**Required Environment Variables**:
- `DATABASE_URL` - Neon PostgreSQL connection string
- `GEMINI_API_KEY` - Google Gemini API key for AI chatbot
- `JWT_SECRET` - JWT signing secret

### 5.2 Frontend (Next.js)

**Build Command**: `npm run build`
**Start Command**: `npm start` (or `node server.js` for standalone)
**Port**: 3000

**Required Environment Variables**:
- `NEXT_PUBLIC_API_URL` - Backend API base URL

### 5.3 Service Communication

```
┌─────────────┐     HTTP      ┌─────────────┐     PostgreSQL    ┌──────────┐
│   Browser   │───────────────▶│   Frontend  │                   │          │
│             │                │   (Next.js) │                   │   Neon   │
└─────────────┘                └──────┬──────┘                   │ Database │
                                      │                          │          │
                                      │ API calls                └────▲─────┘
                                      │                               │
                               ┌──────▼──────┐                        │
                               │   Backend   │────────────────────────┘
                               │  (FastAPI)  │
                               └─────────────┘
```

---

## 6. Security Considerations

### 6.1 Container Security

- [x] Non-root user in containers
- [x] Minimal base images (slim/alpine)
- [x] No secrets in Dockerfiles
- [x] Read-only root filesystem (when possible)

### 6.2 Kubernetes Security

- [x] Secrets for sensitive data
- [x] Resource limits to prevent DoS
- [x] Network policies (optional for local)
- [ ] Pod Security Standards (optional for local)

---

## 7. References

- Docker multi-stage builds: https://docs.docker.com/build/building/multi-stage/
- Kubernetes best practices: https://kubernetes.io/docs/concepts/configuration/overview/
- Helm chart development: https://helm.sh/docs/chart_template_guide/
- Minikube handbook: https://minikube.sigs.k8s.io/docs/handbook/
- Next.js standalone output: https://nextjs.org/docs/app/api-reference/next-config-js/output
