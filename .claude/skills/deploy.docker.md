---
name: deploy.docker
description: Generate optimized Dockerfiles for applications
arguments:
  - name: app_type
    description: Application type (node|python|go|java|dotnet)
    required: true
  - name: path
    description: Application path
    required: false
  - name: multi_stage
    description: Use multi-stage build (default true)
    required: false
agent: cloud-native-deployer
---

# Deploy Docker Skill

Generate production-ready Dockerfiles.

## Best Practices Applied

### Security
- Non-root user execution
- Minimal base images (alpine/distroless)
- No secrets in image layers
- Read-only filesystem where possible

### Optimization
- Multi-stage builds for smaller images
- Layer caching optimization
- .dockerignore generation
- Dependency caching

### Configuration
- Health check endpoints
- Environment variable support
- Proper signal handling

## Generated Files

### Dockerfile
```dockerfile
# Build stage
FROM node:20-alpine AS builder
WORKDIR /app
COPY package*.json ./
RUN npm ci --only=production

# Production stage
FROM node:20-alpine
RUN addgroup -g 1001 appgroup && adduser -u 1001 -G appgroup -D appuser
WORKDIR /app
COPY --from=builder /app/node_modules ./node_modules
COPY . .
USER appuser
EXPOSE 3000
HEALTHCHECK CMD wget -q --spider http://localhost:3000/health
CMD ["node", "server.js"]
```

### .dockerignore
```
node_modules
.git
.env
*.md
tests
coverage
```

## Output

```
DOCKERFILE GENERATED
====================
Application: {{app_type}}
Path: {{path}}
Multi-stage: {{multi_stage}}

Files Created:
- Dockerfile
- .dockerignore

Image Characteristics:
- Base: [base image]
- Estimated Size: [size]
- Security: Non-root, minimal base

Build Command:
docker build -t [app-name]:latest .

Test Command:
docker run --rm -p 3000:3000 [app-name]:latest
```
