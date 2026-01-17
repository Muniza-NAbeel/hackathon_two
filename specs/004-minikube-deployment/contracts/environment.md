# Environment Variable Contract

**Feature**: 004-minikube-deployment | **Date**: 2026-01-13

## Overview

This contract defines all environment variables required for Phase 4 Kubernetes deployment. Variables are categorized by sensitivity and source.

---

## Backend Service Variables

### Secrets (Sensitive - via Kubernetes Secret)

| Variable | Type | Required | Example | Description |
|----------|------|----------|---------|-------------|
| `DATABASE_URL` | string | Yes | `postgresql://user:pass@host/db?sslmode=require` | Neon PostgreSQL connection string |
| `GEMINI_API_KEY` | string | Yes | `AIza...` | Google Gemini API key for AI chatbot |
| `JWT_SECRET` | string | Yes | `<random-256-bit>` | JWT token signing secret |

### ConfigMap (Non-Sensitive - via Kubernetes ConfigMap)

| Variable | Type | Required | Default | Description |
|----------|------|----------|---------|-------------|
| `JWT_ALGORITHM` | string | No | `HS256` | JWT algorithm for token signing |
| `ACCESS_TOKEN_EXPIRE_DAYS` | int | No | `7` | Number of days before access token expires |
| `DEBUG` | bool | No | `False` | Enable debug mode (logs SQL queries) |
| `CORS_ORIGINS` | list | No | `["http://localhost:3000"]` | Allowed CORS origins |

---

## Frontend Service Variables

### Build-Time Variables (Embedded in Image)

| Variable | Type | Required | Default | Description |
|----------|------|----------|---------|-------------|
| `NODE_ENV` | enum | No | `production` | Node environment mode |

### Runtime Variables (via ConfigMap)

| Variable | Type | Required | Example | Description |
|----------|------|----------|---------|-------------|
| `NEXT_PUBLIC_API_URL` | URL | Yes | `http://backend:8000` | Backend API base URL |

---

## Kubernetes Secret Creation

```bash
kubectl create secret generic backend-secrets \
  --from-literal=DATABASE_URL="${DATABASE_URL}" \
  --from-literal=GEMINI_API_KEY="${GEMINI_API_KEY}" \
  --from-literal=JWT_SECRET="${JWT_SECRET}"
```

---

## Helm Values Override

```bash
# Backend
helm install backend ./helm/backend \
  --set env.DEBUG=True \
  --set env.JWT_ALGORITHM=HS256

# Frontend
helm install frontend ./helm/frontend \
  --set env.NEXT_PUBLIC_API_URL="http://localhost:30080"
```

---

## Validation Rules

1. `DATABASE_URL` must be a valid PostgreSQL connection string with SSL
2. `GEMINI_API_KEY` must be a valid Google API key
3. `JWT_SECRET` should be at least 32 characters
4. `NEXT_PUBLIC_API_URL` must be a valid HTTP/HTTPS URL
