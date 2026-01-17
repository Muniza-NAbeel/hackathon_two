# Tasks: Phase 4 - Local Kubernetes Deployment (Minikube)

**Input**: Design documents from `/specs/004-minikube-deployment/`
**Prerequisites**: plan.md (completed), spec.md (completed), research.md, data-model.md, quickstart.md, contracts/

**Tests**: Manual verification via kubectl commands and browser access (no automated tests for infrastructure deployment)

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions

- **Phase 4 Infrastructure**: `phase_4/` at repository root
- **Phase 3 Source (READ-ONLY)**: `phase_3/backend/`, `phase_3/frontend/`
- **Dockerfiles**: `phase_4/backend/Dockerfile`, `phase_4/frontend/Dockerfile`
- **Helm Charts**: `phase_4/helm/backend/`, `phase_4/helm/frontend/`

---

## Phase 1: Setup (Project Structure)

**Purpose**: Create phase_4 directory structure for deployment artifacts

- [x] T001 Create phase_4 directory structure with subdirectories: `phase_4/backend/`, `phase_4/frontend/`, `phase_4/helm/backend/templates/`, `phase_4/helm/frontend/templates/`
- [x] T002 [P] Create `.gitkeep` placeholder files in each template directory

**Checkpoint**: Directory structure ready for infrastructure artifact generation

---

## Phase 2: Foundational (Containerization)

**Purpose**: Generate Dockerfiles and build Docker images - MUST be complete before Kubernetes deployment

**AI Tools**: docker-ai-agent (Claude Code if Gordon unavailable)

**⚠️ CRITICAL**: Both Docker images must build successfully before ANY Kubernetes deployment can begin

### Backend Containerization

- [x] T003 [P] Analyze phase_3/backend/ structure (requirements.txt, app/ layout, start.sh)
- [x] T004 Generate multi-stage Dockerfile for FastAPI backend in `phase_4/backend/Dockerfile`
  - Stage 1: python:3.11-slim builder with pip install to /app/dependencies
  - Stage 2: Production image copying dependencies, non-root user (appuser uid 1000)
  - Expose port 8000, set PYTHONUNBUFFERED=1
  - CMD: uvicorn app.main:app --host 0.0.0.0 --port 8000
- [x] T005 [P] Create `.dockerignore` for backend in `phase_4/backend/.dockerignore`
  - Exclude: __pycache__, *.pyc, .env, .git, tests/, venv/, .pytest_cache/

### Frontend Containerization

- [x] T006 [P] Analyze phase_3/frontend/ structure (package.json, next.config.ts, app/ layout)
- [x] T007 Generate multi-stage Dockerfile for Next.js frontend in `phase_4/frontend/Dockerfile`
  - Stage 1: node:18-alpine deps with npm ci --only=production
  - Stage 2: node:18-alpine builder with npm run build
  - Stage 3: node:18-alpine runner with standalone output, non-root user (nextjs uid 1001)
  - Expose port 3000, set NODE_ENV=production
  - CMD: node server.js
- [x] T008 [P] Create `.dockerignore` for frontend in `phase_4/frontend/.dockerignore`
  - Exclude: node_modules/, .next/, .env*, .git/, coverage/

### Docker Compose (Development Convenience)

- [x] T009 Create `phase_4/docker-compose.yml` for local development without Kubernetes
  - Backend service with environment variable references
  - Frontend service with backend URL configuration
  - Network bridge for inter-container communication

**Checkpoint**: Dockerfiles ready - Helm chart generation can now begin

---

## Phase 3: User Story 1 - Deploy Backend to Local Kubernetes (Priority: P1) 🎯 MVP

**Goal**: Deploy FastAPI backend service to Minikube cluster with health checks and secrets management

**Independent Test**: `kubectl get pods -l app=backend` shows 1/1 Ready; `curl $(minikube service backend --url)/health` returns 200 OK

**AI Tools**: helm-chart-agent (Claude Code for Helm templates), kubectl-ai for initial setup

### Helm Chart Generation for Backend

- [x] T010 [US1] Create `phase_4/helm/backend/Chart.yaml` with metadata
  - apiVersion: v2, name: backend, version: 0.1.0, appVersion: 1.0.0
- [x] T011 [US1] Create `phase_4/helm/backend/values.yaml` with configurable values
  - image.repository: todo-backend, image.tag: latest, image.pullPolicy: Never
  - replicaCount: 1
  - service.type: NodePort, service.port: 8000, service.nodePort: 30080
  - resources.requests: 100m CPU, 128Mi memory; limits: 500m CPU, 512Mi memory
  - probes.liveness.path: /health, initialDelaySeconds: 30
  - probes.readiness.path: /health, initialDelaySeconds: 10
- [x] T012 [P] [US1] Create `phase_4/helm/backend/templates/_helpers.tpl` with template functions
  - backend.name, backend.fullname, backend.labels, backend.selectorLabels
- [x] T013 [US1] Create `phase_4/helm/backend/templates/deployment.yaml`
  - Deployment with pod spec referencing values.yaml
  - Container with image, ports, resources, probes
  - envFrom referencing ConfigMap and Secret
- [x] T014 [US1] Create `phase_4/helm/backend/templates/service.yaml`
  - NodePort service selecting backend pods
  - Port 8000 mapped to nodePort 30080
- [x] T015 [US1] Create `phase_4/helm/backend/templates/configmap.yaml`
  - Non-sensitive environment variables: LOG_LEVEL, APP_ENV, CORS_ORIGINS
- [ ] T016 [US1] Validate backend Helm chart: `helm lint phase_4/helm/backend`

### Minikube Setup and Backend Deployment

- [ ] T017 [US1] Start Minikube cluster with adequate resources
  - Command: `minikube start --cpus=4 --memory=8192 --driver=docker`
  - Verify: `kubectl cluster-info` shows healthy cluster
- [ ] T018 [US1] Configure Docker environment for Minikube
  - Command: `eval $(minikube docker-env)`
  - Verify: `docker info` shows Minikube's Docker daemon
- [ ] T019 [US1] Build backend Docker image inside Minikube
  - Command: `docker build -t todo-backend:latest -f phase_4/backend/Dockerfile phase_3/backend`
  - Verify: `docker images | grep todo-backend` shows image
- [ ] T020 [US1] Create Kubernetes secret for backend sensitive variables
  - Command: `kubectl create secret generic backend-secrets --from-literal=DATABASE_URL="$DATABASE_URL" --from-literal=GEMINI_API_KEY="$GEMINI_API_KEY" --from-literal=JWT_SECRET="$JWT_SECRET"`
- [ ] T021 [US1] Deploy backend using Helm
  - Command: `helm install backend phase_4/helm/backend --set image.pullPolicy=Never`
  - Verify: `kubectl rollout status deployment/backend --timeout=120s`
- [ ] T022 [US1] Verify backend deployment
  - Check pod status: `kubectl get pods -l app=backend` shows 1/1 Ready
  - Check logs: `kubectl logs -l app=backend` shows successful startup
  - Test health endpoint: `curl $(minikube service backend --url)/health` returns 200 OK

**Checkpoint**: Backend deployed and healthy - User Story 1 complete. Frontend deployment can now begin.

---

## Phase 4: User Story 2 - Deploy Frontend to Local Kubernetes (Priority: P2)

**Goal**: Deploy Next.js frontend service to Minikube cluster connecting to backend

**Independent Test**: `kubectl get pods -l app=frontend` shows 1/1 Ready; `minikube service frontend` opens browser with login page

**AI Tools**: helm-chart-agent (Claude Code for Helm templates)

### Kubernetes YAML Tasks for Frontend (New)

- [ ] T028a [US2] Create `phase_4/k8s/frontend-deployment.yaml`
  - Deployment for frontend
  - Container: image `todo-frontend:latest`, port 3000
  - Environment variable: `NEXT_PUBLIC_API_URL=http://backend:8000`
  - Liveness & readiness probes to `/`

- [ ] T028b [US2] Create `phase_4/k8s/frontend-service.yaml`
  - NodePort service selecting frontend pods
  - Port 3000 mapped to nodePort 30000

- [ ] T028c [US2] Create `phase_4/k8s/frontend-configmap.yaml` (optional)
  - Non-sensitive frontend environment variables (e.g., LOG_LEVEL, NEXT_PUBLIC_OPENAI_DOMAIN_KEY)

### Helm Chart Generation for Frontend (Preferred)

- [x] T023 [US2] Create `phase_4/helm/frontend/Chart.yaml` with metadata
- [x] T024 [US2] Create `phase_4/helm/frontend/values.yaml` with configurable values
- [x] T025 [P] [US2] Create `phase_4/helm/frontend/templates/_helpers.tpl` with template functions
- [x] T026 [US2] Create `phase_4/helm/frontend/templates/deployment.yaml`
- [x] T027 [US2] Create `phase_4/helm/frontend/templates/service.yaml`
- [ ] T028 [US2] Validate frontend Helm chart: `helm lint phase_4/helm/frontend`

### Frontend Deployment

- [ ] T029 [US2] Build frontend Docker image inside Minikube
- [ ] T030 [US2] Deploy frontend using Helm
- [ ] T031 [US2] Verify frontend deployment
