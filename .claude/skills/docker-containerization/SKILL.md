---
name: docker-containerization
description: Containerize frontend and backend applications with optimized Dockerfiles, multi-stage builds, and docker-compose configurations. Use when setting up Docker containers, creating Dockerfiles, preparing applications for containerized deployment, or optimizing Docker images for Phase IV deployment.
allowed-tools: Write, Read, Bash(docker:*), Bash(cat:*), Glob, Grep
---

# Docker Containerization Skill

## Purpose

I help you containerize applications following Docker best practices for Phase IV Kubernetes deployment:

- Multi-stage builds for optimized images
- Layer caching optimization
- Security best practices (non-root users, minimal base images)
- Docker Compose configurations for local development

## When to Use This Skill

Ask me to help with:
- Creating Dockerfiles for FastAPI backend
- Creating Dockerfiles for Next.js frontend
- Setting up multi-stage builds
- Writing docker-compose.yml for development
- Optimizing Docker image size and build times
- Dockerfile security hardening

## Key Principles

1. **Multi-stage builds** - Reduce final image size significantly
2. **Layer ordering** - Place frequently changing layers near the end
3. **Non-root users** - Always specify a non-root user for security
4. **Minimal base images** - Prefer `python:3.11-slim` over `python:3.11`
5. **Explicit versions** - Avoid `latest` tags in production
6. **.dockerignore** - Exclude unnecessary files from build context

## Process

When you ask me to create Dockerfiles:

1. Analyze your application structure (backend/frontend)
2. Review dependencies and build requirements
3. Generate optimized multi-stage Dockerfile
4. Create .dockerignore file
5. Suggest docker-compose configuration
6. Provide build and run commands

## FastAPI Backend Dockerfile Template

```dockerfile
# Stage 1: Builder
FROM python:3.11-slim as builder

WORKDIR /app

# Install build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for caching
COPY requirements.txt .
RUN pip install --no-cache-dir --user -r requirements.txt

# Stage 2: Runtime
FROM python:3.11-slim

# Create non-root user
RUN useradd -m -u 1000 appuser

WORKDIR /app

# Copy installed packages from builder
COPY --from=builder /root/.local /home/appuser/.local

# Copy application code
COPY --chown=appuser:appuser . .

# Set PATH for user packages
ENV PATH=/home/appuser/.local/bin:$PATH

# Switch to non-root user
USER appuser

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

## Next.js Frontend Dockerfile Template

```dockerfile
# Stage 1: Dependencies
FROM node:20-alpine AS deps
WORKDIR /app
COPY package.json package-lock.json* ./
RUN npm ci --only=production

# Stage 2: Builder
FROM node:20-alpine AS builder
WORKDIR /app
COPY --from=deps /app/node_modules ./node_modules
COPY . .
ENV NEXT_TELEMETRY_DISABLED 1
RUN npm run build

# Stage 3: Runner
FROM node:20-alpine AS runner
WORKDIR /app

ENV NODE_ENV production
ENV NEXT_TELEMETRY_DISABLED 1

RUN addgroup --system --gid 1001 nodejs
RUN adduser --system --uid 1001 nextjs

COPY --from=builder /app/public ./public
COPY --from=builder --chown=nextjs:nodejs /app/.next/standalone ./
COPY --from=builder --chown=nextjs:nodejs /app/.next/static ./.next/static

USER nextjs

EXPOSE 3000
ENV PORT 3000

CMD ["node", "server.js"]
```

## Docker Compose Template

```yaml
version: '3.8'

services:
  backend:
    build:
      context: ./phase_3/backend
      dockerfile: Dockerfile
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=${DATABASE_URL}
      - OPENAI_API_KEY=${OPENAI_API_KEY}
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/api/health"]
      interval: 30s
      timeout: 10s
      retries: 3

  frontend:
    build:
      context: ./phase_3/frontend
      dockerfile: Dockerfile
    ports:
      - "3000:3000"
    environment:
      - NEXT_PUBLIC_API_URL=http://backend:8000
    depends_on:
      - backend
```

## .dockerignore Template

```
# Git
.git
.gitignore

# Python
__pycache__
*.py[cod]
*$py.class
.Python
*.egg-info
.eggs
*.egg
venv/
.venv/

# Node
node_modules
.next
.npm

# IDE
.idea
.vscode
*.swp
*.swo

# Testing
.pytest_cache
.coverage
htmlcov/

# Misc
*.md
!README.md
.env*
docker-compose*.yml
Dockerfile*
```

## Build Commands

```bash
# Build backend image
docker build -t todo-backend:latest ./phase_3/backend

# Build frontend image
docker build -t todo-frontend:latest ./phase_3/frontend

# Build with docker-compose
docker-compose build

# Run with docker-compose
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

## Image Optimization Tips

| Technique | Impact |
|-----------|--------|
| Multi-stage builds | 50-80% size reduction |
| Alpine base images | 60-70% size reduction |
| .dockerignore | Faster builds, smaller context |
| Layer caching | Faster rebuilds |
| COPY vs ADD | Prefer COPY (simpler, faster) |
