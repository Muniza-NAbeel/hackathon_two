---
name: helm-chart-generation
description: Generate Kubernetes Helm charts for frontend and backend services with configurable deployments, services, ConfigMaps, and resources. Use when creating infrastructure-as-code, Helm chart structure, Kubernetes deployment manifests, or preparing for Phase IV Minikube deployment.
allowed-tools: Write, Read, Bash(helm:*), Bash(kubectl:*), Bash(cat:*), Glob, Grep
---

# Helm Chart Generation Skill

## Purpose

I help you create production-ready Helm charts for your Todo application microservices. Helm charts use templates and values files to make Kubernetes deployments reusable across environments (dev, staging, production).

## When to Use This Skill

Ask me to help with:
- Creating Helm charts from scratch
- Designing chart structure and templates
- Writing values.yaml for environment configuration
- Creating ConfigMaps and Secrets management
- Setting up resource limits and requests
- Configuring health checks and probes
- Phase IV Minikube deployment preparation

## Helm Chart Structure

Standard structure I create:

```
helm/
├── backend/
│   ├── Chart.yaml
│   ├── values.yaml
│   ├── values-dev.yaml
│   ├── values-prod.yaml
│   └── templates/
│       ├── _helpers.tpl
│       ├── deployment.yaml
│       ├── service.yaml
│       ├── configmap.yaml
│       └── hpa.yaml
└── frontend/
    ├── Chart.yaml
    ├── values.yaml
    └── templates/
        ├── _helpers.tpl
        ├── deployment.yaml
        └── service.yaml
```

## Key Principles

1. **One chart per service** - backend, frontend separately
2. **Template all variables** - anything that changes per environment
3. **Use values.yaml** - single source of truth for configuration
4. **Document all values** - with comments in values.yaml
5. **Resource limits** - prevent runaway containers
6. **Health checks** - ensure reliable deployments
7. **Labels** - consistent labeling for management

## Backend Chart Templates

### Chart.yaml

```yaml
apiVersion: v2
name: todo-backend
description: FastAPI backend for Todo AI Chatbot application
type: application
version: 0.1.0
appVersion: "1.0.0"
keywords:
  - todo
  - fastapi
  - backend
  - api
maintainers:
  - name: Developer
```

### values.yaml

```yaml
# Replica configuration
replicaCount: 1

# Image configuration
image:
  repository: todo-backend
  tag: "latest"
  pullPolicy: IfNotPresent

# Service configuration
service:
  type: ClusterIP
  port: 8000
  targetPort: 8000

# Resource limits
resources:
  requests:
    cpu: 100m
    memory: 128Mi
  limits:
    cpu: 500m
    memory: 512Mi

# Environment variables
env:
  DATABASE_URL: ""
  OPENAI_API_KEY: ""
  BETTER_AUTH_SECRET: ""
  LOG_LEVEL: "info"
  ENVIRONMENT: "development"

# Health checks
livenessProbe:
  enabled: true
  path: /api/health
  initialDelaySeconds: 10
  periodSeconds: 10

readinessProbe:
  enabled: true
  path: /api/health
  initialDelaySeconds: 5
  periodSeconds: 5

# Autoscaling (optional)
autoscaling:
  enabled: false
  minReplicas: 1
  maxReplicas: 5
  targetCPUUtilizationPercentage: 80
```

### templates/_helpers.tpl

```yaml
{{/*
Expand the name of the chart.
*/}}
{{- define "todo-backend.name" -}}
{{- default .Chart.Name .Values.nameOverride | trunc 63 | trimSuffix "-" }}
{{- end }}

{{/*
Create a default fully qualified app name.
*/}}
{{- define "todo-backend.fullname" -}}
{{- if .Values.fullnameOverride }}
{{- .Values.fullnameOverride | trunc 63 | trimSuffix "-" }}
{{- else }}
{{- $name := default .Chart.Name .Values.nameOverride }}
{{- printf "%s-%s" .Release.Name $name | trunc 63 | trimSuffix "-" }}
{{- end }}
{{- end }}

{{/*
Common labels
*/}}
{{- define "todo-backend.labels" -}}
helm.sh/chart: {{ .Chart.Name }}-{{ .Chart.Version }}
app.kubernetes.io/name: {{ include "todo-backend.name" . }}
app.kubernetes.io/instance: {{ .Release.Name }}
app.kubernetes.io/version: {{ .Chart.AppVersion | quote }}
app.kubernetes.io/managed-by: {{ .Release.Service }}
{{- end }}

{{/*
Selector labels
*/}}
{{- define "todo-backend.selectorLabels" -}}
app.kubernetes.io/name: {{ include "todo-backend.name" . }}
app.kubernetes.io/instance: {{ .Release.Name }}
{{- end }}
```

### templates/deployment.yaml

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: {{ include "todo-backend.fullname" . }}
  labels:
    {{- include "todo-backend.labels" . | nindent 4 }}
spec:
  replicas: {{ .Values.replicaCount }}
  selector:
    matchLabels:
      {{- include "todo-backend.selectorLabels" . | nindent 6 }}
  template:
    metadata:
      labels:
        {{- include "todo-backend.selectorLabels" . | nindent 8 }}
    spec:
      containers:
        - name: {{ .Chart.Name }}
          image: "{{ .Values.image.repository }}:{{ .Values.image.tag }}"
          imagePullPolicy: {{ .Values.image.pullPolicy }}
          ports:
            - name: http
              containerPort: {{ .Values.service.targetPort }}
              protocol: TCP
          env:
            {{- range $key, $value := .Values.env }}
            - name: {{ $key }}
              value: {{ $value | quote }}
            {{- end }}
          {{- if .Values.livenessProbe.enabled }}
          livenessProbe:
            httpGet:
              path: {{ .Values.livenessProbe.path }}
              port: http
            initialDelaySeconds: {{ .Values.livenessProbe.initialDelaySeconds }}
            periodSeconds: {{ .Values.livenessProbe.periodSeconds }}
          {{- end }}
          {{- if .Values.readinessProbe.enabled }}
          readinessProbe:
            httpGet:
              path: {{ .Values.readinessProbe.path }}
              port: http
            initialDelaySeconds: {{ .Values.readinessProbe.initialDelaySeconds }}
            periodSeconds: {{ .Values.readinessProbe.periodSeconds }}
          {{- end }}
          resources:
            {{- toYaml .Values.resources | nindent 12 }}
```

### templates/service.yaml

```yaml
apiVersion: v1
kind: Service
metadata:
  name: {{ include "todo-backend.fullname" . }}
  labels:
    {{- include "todo-backend.labels" . | nindent 4 }}
spec:
  type: {{ .Values.service.type }}
  ports:
    - port: {{ .Values.service.port }}
      targetPort: {{ .Values.service.targetPort }}
      protocol: TCP
      name: http
  selector:
    {{- include "todo-backend.selectorLabels" . | nindent 4 }}
```

## Helm Commands Reference

```bash
# Lint chart
helm lint ./helm/backend

# Template (dry-run)
helm template todo-backend ./helm/backend

# Install
helm install todo-backend ./helm/backend

# Install with custom values
helm install todo-backend ./helm/backend -f values-prod.yaml

# Upgrade
helm upgrade todo-backend ./helm/backend

# Upgrade with set
helm upgrade todo-backend ./helm/backend --set replicaCount=3

# Rollback
helm rollback todo-backend 1

# Uninstall
helm uninstall todo-backend

# List releases
helm list

# Get values
helm get values todo-backend
```

## Process

1. Ask about your services (backend/frontend)
2. Review application requirements
3. Generate Chart.yaml with metadata
4. Create values.yaml with configurations
5. Generate deployment, service, configmap templates
6. Provide helm install/upgrade commands
