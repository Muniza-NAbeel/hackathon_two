# CI/CD Pipeline Specification

## Overview

This specification defines the GitHub Actions CI/CD pipeline for automated testing, building, and deployment of Phase 5 services to Kubernetes.

## Pipeline Goals

1. Automated testing on every push/PR
2. Build and push Docker images on merge to main
3. Deploy to staging environment automatically
4. Deploy to production with manual approval
5. Rollback capability on failure

---

## Pipeline Architecture

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           GITHUB ACTIONS WORKFLOW                           │
│                                                                             │
│  ┌─────────────┐    ┌─────────────┐    ┌─────────────┐    ┌─────────────┐  │
│  │    LINT     │    │    TEST     │    │    BUILD    │    │   DEPLOY    │  │
│  │             │───▶│             │───▶│             │───▶│             │  │
│  │  - Ruff     │    │  - Pytest   │    │  - Docker   │    │  - Helm     │  │
│  │  - ESLint   │    │  - Jest     │    │  - Push     │    │  - kubectl  │  │
│  └─────────────┘    └─────────────┘    └─────────────┘    └─────────────┘  │
│                                                                             │
│  Triggers:                                                                  │
│  - Push to main branch                                                      │
│  - Pull request to main                                                     │
│  - Manual workflow dispatch                                                 │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## Workflow Files

### Main CI/CD Workflow

**File**: `.github/workflows/ci-cd.yaml`

```yaml
name: CI/CD Pipeline

on:
  push:
    branches: [main]
    paths:
      - 'phase_5/**'
      - '.github/workflows/ci-cd.yaml'
  pull_request:
    branches: [main]
    paths:
      - 'phase_5/**'
  workflow_dispatch:
    inputs:
      environment:
        description: 'Deployment environment'
        required: true
        default: 'staging'
        type: choice
        options:
          - staging
          - production

env:
  REGISTRY: registry.digitalocean.com/todo-registry
  CLUSTER_NAME: todo-cluster

jobs:
  # ============================================
  # JOB 1: Lint
  # ============================================
  lint:
    name: Lint Code
    runs-on: ubuntu-latest
    steps:
      - name: Checkout code
        uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.11'

      - name: Install Python dependencies
        run: |
          pip install ruff

      - name: Lint Python code
        run: |
          ruff check phase_5/backend/
          ruff check phase_5/services/

      - name: Set up Node.js
        uses: actions/setup-node@v4
        with:
          node-version: '20'

      - name: Install Node dependencies
        working-directory: phase_5/frontend
        run: npm ci

      - name: Lint TypeScript code
        working-directory: phase_5/frontend
        run: npm run lint

  # ============================================
  # JOB 2: Test
  # ============================================
  test:
    name: Run Tests
    runs-on: ubuntu-latest
    needs: lint
    services:
      postgres:
        image: postgres:15
        env:
          POSTGRES_USER: test
          POSTGRES_PASSWORD: test
          POSTGRES_DB: test
        ports:
          - 5432:5432
        options: >-
          --health-cmd pg_isready
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5

      redis:
        image: redis:7
        ports:
          - 6379:6379
        options: >-
          --health-cmd "redis-cli ping"
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5

    steps:
      - name: Checkout code
        uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.11'

      - name: Install backend dependencies
        working-directory: phase_5/backend
        run: |
          pip install -r requirements.txt
          pip install pytest pytest-asyncio pytest-cov

      - name: Run backend tests
        working-directory: phase_5/backend
        env:
          DATABASE_URL: postgresql://test:test@localhost:5432/test
          REDIS_URL: redis://localhost:6379
        run: |
          pytest tests/ -v --cov=app --cov-report=xml

      - name: Set up Node.js
        uses: actions/setup-node@v4
        with:
          node-version: '20'

      - name: Install frontend dependencies
        working-directory: phase_5/frontend
        run: npm ci

      - name: Run frontend tests
        working-directory: phase_5/frontend
        run: npm test -- --coverage

      - name: Upload coverage reports
        uses: codecov/codecov-action@v3
        with:
          files: phase_5/backend/coverage.xml,phase_5/frontend/coverage/lcov.info

  # ============================================
  # JOB 3: Build and Push
  # ============================================
  build:
    name: Build and Push Images
    runs-on: ubuntu-latest
    needs: test
    if: github.event_name == 'push' && github.ref == 'refs/heads/main'
    outputs:
      image_tag: ${{ steps.meta.outputs.version }}
    steps:
      - name: Checkout code
        uses: actions/checkout@v4

      - name: Set up Docker Buildx
        uses: docker/setup-buildx-action@v3

      - name: Install doctl
        uses: digitalocean/action-doctl@v2
        with:
          token: ${{ secrets.DIGITALOCEAN_ACCESS_TOKEN }}

      - name: Log in to Container Registry
        run: doctl registry login --expiry-seconds 1200

      - name: Extract metadata
        id: meta
        run: |
          echo "version=$(git rev-parse --short HEAD)" >> $GITHUB_OUTPUT
          echo "date=$(date +'%Y%m%d')" >> $GITHUB_OUTPUT

      - name: Build and push backend
        uses: docker/build-push-action@v5
        with:
          context: phase_5/backend
          push: true
          tags: |
            ${{ env.REGISTRY }}/todo-backend:${{ steps.meta.outputs.version }}
            ${{ env.REGISTRY }}/todo-backend:latest
          cache-from: type=gha
          cache-to: type=gha,mode=max

      - name: Build and push frontend
        uses: docker/build-push-action@v5
        with:
          context: phase_5/frontend
          push: true
          tags: |
            ${{ env.REGISTRY }}/todo-frontend:${{ steps.meta.outputs.version }}
            ${{ env.REGISTRY }}/todo-frontend:latest
          cache-from: type=gha
          cache-to: type=gha,mode=max

      - name: Build and push notification service
        uses: docker/build-push-action@v5
        with:
          context: phase_5/services/notification
          push: true
          tags: |
            ${{ env.REGISTRY }}/notification-service:${{ steps.meta.outputs.version }}
            ${{ env.REGISTRY }}/notification-service:latest
          cache-from: type=gha
          cache-to: type=gha,mode=max

      - name: Build and push recurring task service
        uses: docker/build-push-action@v5
        with:
          context: phase_5/services/recurring
          push: true
          tags: |
            ${{ env.REGISTRY }}/recurring-task-service:${{ steps.meta.outputs.version }}
            ${{ env.REGISTRY }}/recurring-task-service:latest
          cache-from: type=gha
          cache-to: type=gha,mode=max

  # ============================================
  # JOB 4: Deploy to Staging
  # ============================================
  deploy-staging:
    name: Deploy to Staging
    runs-on: ubuntu-latest
    needs: build
    environment: staging
    steps:
      - name: Checkout code
        uses: actions/checkout@v4

      - name: Install doctl
        uses: digitalocean/action-doctl@v2
        with:
          token: ${{ secrets.DIGITALOCEAN_ACCESS_TOKEN }}

      - name: Save kubeconfig
        run: |
          doctl kubernetes cluster kubeconfig save ${{ env.CLUSTER_NAME }}

      - name: Install Helm
        uses: azure/setup-helm@v3
        with:
          version: v3.13.0

      - name: Deploy to staging
        run: |
          helm upgrade --install todo-app-staging ./helm/todo-app \
            -f helm/todo-app/values-staging.yaml \
            --set global.imageTag=${{ needs.build.outputs.image_tag }} \
            --namespace todo-staging \
            --create-namespace \
            --wait \
            --timeout 5m

      - name: Verify deployment
        run: |
          kubectl rollout status deployment/chat-backend -n todo-staging
          kubectl rollout status deployment/chat-frontend -n todo-staging
          kubectl rollout status deployment/notification-service -n todo-staging
          kubectl rollout status deployment/recurring-task-service -n todo-staging

      - name: Run smoke tests
        run: |
          STAGING_URL=$(kubectl get ingress -n todo-staging -o jsonpath='{.items[0].status.loadBalancer.ingress[0].ip}')
          curl -f http://$STAGING_URL/api/health || exit 1

  # ============================================
  # JOB 5: Deploy to Production
  # ============================================
  deploy-production:
    name: Deploy to Production
    runs-on: ubuntu-latest
    needs: [build, deploy-staging]
    environment: production
    if: github.event_name == 'push' || (github.event_name == 'workflow_dispatch' && github.event.inputs.environment == 'production')
    steps:
      - name: Checkout code
        uses: actions/checkout@v4

      - name: Install doctl
        uses: digitalocean/action-doctl@v2
        with:
          token: ${{ secrets.DIGITALOCEAN_ACCESS_TOKEN }}

      - name: Save kubeconfig
        run: |
          doctl kubernetes cluster kubeconfig save ${{ env.CLUSTER_NAME }}

      - name: Install Helm
        uses: azure/setup-helm@v3
        with:
          version: v3.13.0

      - name: Deploy to production
        run: |
          helm upgrade --install todo-app ./helm/todo-app \
            -f helm/todo-app/values-production.yaml \
            --set global.imageTag=${{ needs.build.outputs.image_tag }} \
            --namespace todo-app \
            --create-namespace \
            --wait \
            --timeout 5m

      - name: Verify deployment
        run: |
          kubectl rollout status deployment/chat-backend -n todo-app
          kubectl rollout status deployment/chat-frontend -n todo-app
          kubectl rollout status deployment/notification-service -n todo-app
          kubectl rollout status deployment/recurring-task-service -n todo-app

      - name: Run production smoke tests
        run: |
          curl -f https://todo.yourdomain.com/api/health || exit 1

      - name: Notify on success
        if: success()
        run: |
          echo "Deployment successful!"
          # Add Slack/Discord notification here

      - name: Rollback on failure
        if: failure()
        run: |
          echo "Deployment failed, rolling back..."
          helm rollback todo-app -n todo-app
```

---

## Environment Configuration

### GitHub Secrets Required

| Secret | Description | Used In |
|--------|-------------|---------|
| `DIGITALOCEAN_ACCESS_TOKEN` | DO API token | All deploy jobs |
| `DOCKERHUB_USERNAME` | DockerHub username (optional) | Build job |
| `DOCKERHUB_TOKEN` | DockerHub token (optional) | Build job |

### GitHub Environments

Create these environments in GitHub repository settings:

**Staging**
- No protection rules
- Auto-deploy after tests pass

**Production**
- Required reviewers (1 approval)
- Wait timer: 5 minutes (optional)
- Branch restriction: main only

---

## Helm Values Files

### Staging Values

**File**: `helm/todo-app/values-staging.yaml`

```yaml
global:
  registry: "registry.digitalocean.com/todo-registry"
  namespace: todo-staging

backend:
  replicaCount: 1
  resources:
    requests:
      memory: "128Mi"
      cpu: "100m"
    limits:
      memory: "256Mi"
      cpu: "300m"

frontend:
  replicaCount: 1
  resources:
    requests:
      memory: "128Mi"
      cpu: "100m"
    limits:
      memory: "256Mi"
      cpu: "300m"

notificationService:
  replicaCount: 1

recurringTaskService:
  replicaCount: 1

ingress:
  enabled: true
  annotations:
    kubernetes.io/ingress.class: nginx
  hosts:
    - host: staging-todo.yourdomain.com
      paths:
        - path: /
          service: frontend
        - path: /api
          service: backend
```

### Production Values

**File**: `helm/todo-app/values-production.yaml`

```yaml
global:
  registry: "registry.digitalocean.com/todo-registry"
  namespace: todo-app

backend:
  replicaCount: 3
  resources:
    requests:
      memory: "256Mi"
      cpu: "200m"
    limits:
      memory: "512Mi"
      cpu: "500m"
  autoscaling:
    enabled: true
    minReplicas: 3
    maxReplicas: 10
    targetCPUUtilization: 70

frontend:
  replicaCount: 2
  resources:
    requests:
      memory: "256Mi"
      cpu: "200m"
    limits:
      memory: "512Mi"
      cpu: "500m"
  autoscaling:
    enabled: true
    minReplicas: 2
    maxReplicas: 5
    targetCPUUtilization: 70

notificationService:
  replicaCount: 2
  autoscaling:
    enabled: true
    minReplicas: 2
    maxReplicas: 5

recurringTaskService:
  replicaCount: 2
  autoscaling:
    enabled: true
    minReplicas: 2
    maxReplicas: 5

ingress:
  enabled: true
  className: nginx
  annotations:
    cert-manager.io/cluster-issuer: letsencrypt-prod
    nginx.ingress.kubernetes.io/rate-limit: "100"
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

---

## Rollback Workflow

**File**: `.github/workflows/rollback.yaml`

```yaml
name: Rollback Deployment

on:
  workflow_dispatch:
    inputs:
      environment:
        description: 'Environment to rollback'
        required: true
        type: choice
        options:
          - staging
          - production
      revision:
        description: 'Helm revision number (leave empty for previous)'
        required: false

env:
  CLUSTER_NAME: todo-cluster

jobs:
  rollback:
    name: Rollback
    runs-on: ubuntu-latest
    environment: ${{ github.event.inputs.environment }}
    steps:
      - name: Install doctl
        uses: digitalocean/action-doctl@v2
        with:
          token: ${{ secrets.DIGITALOCEAN_ACCESS_TOKEN }}

      - name: Save kubeconfig
        run: |
          doctl kubernetes cluster kubeconfig save ${{ env.CLUSTER_NAME }}

      - name: Install Helm
        uses: azure/setup-helm@v3

      - name: Get release name
        id: release
        run: |
          if [ "${{ github.event.inputs.environment }}" == "production" ]; then
            echo "name=todo-app" >> $GITHUB_OUTPUT
            echo "namespace=todo-app" >> $GITHUB_OUTPUT
          else
            echo "name=todo-app-staging" >> $GITHUB_OUTPUT
            echo "namespace=todo-staging" >> $GITHUB_OUTPUT
          fi

      - name: Show history
        run: |
          helm history ${{ steps.release.outputs.name }} -n ${{ steps.release.outputs.namespace }}

      - name: Rollback
        run: |
          if [ -n "${{ github.event.inputs.revision }}" ]; then
            helm rollback ${{ steps.release.outputs.name }} ${{ github.event.inputs.revision }} -n ${{ steps.release.outputs.namespace }}
          else
            helm rollback ${{ steps.release.outputs.name }} -n ${{ steps.release.outputs.namespace }}
          fi

      - name: Verify rollback
        run: |
          kubectl rollout status deployment/chat-backend -n ${{ steps.release.outputs.namespace }}
          kubectl rollout status deployment/chat-frontend -n ${{ steps.release.outputs.namespace }}
```

---

## Pull Request Workflow

**File**: `.github/workflows/pr-check.yaml`

```yaml
name: PR Checks

on:
  pull_request:
    branches: [main]
    types: [opened, synchronize, reopened]

jobs:
  pr-checks:
    name: PR Checks
    runs-on: ubuntu-latest
    steps:
      - name: Checkout code
        uses: actions/checkout@v4
        with:
          fetch-depth: 0

      - name: Check commit messages
        uses: wagoid/commitlint-github-action@v5

      - name: Check for secrets
        uses: trufflesecurity/trufflehog@main
        with:
          path: ./
          base: ${{ github.event.pull_request.base.sha }}
          head: ${{ github.event.pull_request.head.sha }}

      - name: Lint PR title
        uses: amannn/action-semantic-pull-request@v5
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
```

---

## Branch Protection Rules

Configure in GitHub repository settings:

### Main Branch

- Require pull request before merging
- Require approvals: 1
- Require status checks:
  - `lint`
  - `test`
- Require branches to be up to date
- Do not allow bypassing

---

## Monitoring Pipeline

### Workflow Run Notifications

Add to end of deploy job:

```yaml
- name: Notify Slack on success
  if: success()
  uses: 8398a7/action-slack@v3
  with:
    status: ${{ job.status }}
    text: 'Deployment to ${{ matrix.environment }} succeeded!'
    webhook_url: ${{ secrets.SLACK_WEBHOOK }}

- name: Notify Slack on failure
  if: failure()
  uses: 8398a7/action-slack@v3
  with:
    status: ${{ job.status }}
    text: 'Deployment to ${{ matrix.environment }} failed!'
    webhook_url: ${{ secrets.SLACK_WEBHOOK }}
```

---

## Best Practices

1. **Never commit secrets** - Use GitHub Secrets
2. **Pin action versions** - Use `@v4` not `@main`
3. **Use caching** - Docker layer cache, npm cache
4. **Fail fast** - Run lint before tests
5. **Separate environments** - Staging and production
6. **Manual approval for production** - Use environment protection
7. **Automate rollbacks** - Have rollback workflow ready
8. **Monitor pipeline** - Alert on failures
