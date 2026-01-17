# Quickstart: Phase 4 - Local Kubernetes Deployment

**Feature**: 004-minikube-deployment | **Date**: 2026-01-13

## Prerequisites

- Docker 24+ installed and running
- Minikube 1.32+ installed
- Helm 3+ installed
- kubectl configured
- Environment variables set:
  - `DATABASE_URL` - Neon PostgreSQL connection string
  - `GEMINI_API_KEY` - Google Gemini API key
  - `JWT_SECRET` - JWT signing secret

---

## Quick Deploy (5 Commands)

```bash
# 1. Start Minikube
minikube start --cpus=4 --memory=8192 --driver=docker

# 2. Set Docker environment
eval $(minikube docker-env)

# 3. Build images
docker build -t todo-backend:latest -f phase_4/backend/Dockerfile phase_3/backend
docker build -t todo-frontend:latest -f phase_4/frontend/Dockerfile phase_3/frontend

# 4. Create secrets and deploy
kubectl create secret generic backend-secrets \
  --from-literal=DATABASE_URL="$DATABASE_URL" \
  --from-literal=GEMINI_API_KEY="$GEMINI_API_KEY" \
  --from-literal=JWT_SECRET="$JWT_SECRET"

helm install backend phase_4/helm/backend --set image.pullPolicy=Never
helm install frontend phase_4/helm/frontend --set image.pullPolicy=Never

# 5. Access application
minikube service frontend
```

---

## Verification Commands

```bash
# Check pod status
kubectl get pods

# Check services
kubectl get svc

# View backend logs
kubectl logs -l app=backend

# View frontend logs
kubectl logs -l app=frontend

# Test backend health
curl $(minikube service backend --url)/health
```

---

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

---

## Troubleshooting

| Issue | Solution |
|-------|----------|
| ImagePullBackOff | Run `eval $(minikube docker-env)` before building |
| Pod CrashLoopBackOff | Check logs: `kubectl logs <pod-name>` |
| Service unreachable | Use `minikube service <name> --url` |
| Out of memory | Restart with more memory: `minikube start --memory=8192` |
