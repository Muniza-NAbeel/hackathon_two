---
name: deploy.k8s
description: Generate Kubernetes manifests
arguments:
  - name: name
    description: Application name
    required: true
  - name: type
    description: Resource type (deployment|service|ingress|configmap|all)
    required: false
  - name: namespace
    description: Target namespace
    required: false
agent: cloud-native-deployer
---

# Deploy K8s Skill

Generate Kubernetes manifests.

## Resource Templates

### Deployment
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: {{name}}
  labels:
    app: {{name}}
spec:
  replicas: 1
  selector:
    matchLabels:
      app: {{name}}
  template:
    metadata:
      labels:
        app: {{name}}
    spec:
      securityContext:
        runAsNonRoot: true
        runAsUser: 1001
      containers:
      - name: {{name}}
        image: {{name}}:latest
        ports:
        - containerPort: 8080
        resources:
          requests:
            memory: "128Mi"
            cpu: "100m"
          limits:
            memory: "512Mi"
            cpu: "500m"
        livenessProbe:
          httpGet:
            path: /health
            port: 8080
        readinessProbe:
          httpGet:
            path: /ready
            port: 8080
```

### Service
```yaml
apiVersion: v1
kind: Service
metadata:
  name: {{name}}
spec:
  selector:
    app: {{name}}
  ports:
  - port: 80
    targetPort: 8080
```

## Output

```
KUBERNETES MANIFESTS GENERATED
==============================
Application: {{name}}
Namespace: {{namespace | "default"}}
Resources: {{type | "all"}}

Files Created:
- k8s/{{name}}/deployment.yaml
- k8s/{{name}}/service.yaml
- k8s/{{name}}/ingress.yaml
- k8s/{{name}}/configmap.yaml

Validation:
kubectl apply --dry-run=client -f k8s/{{name}}/ ... [VALID]

Apply Command:
kubectl apply -f k8s/{{name}}/ -n {{namespace}}
```
