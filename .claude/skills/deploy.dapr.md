---
name: deploy.dapr
description: Configure Dapr components and annotations
arguments:
  - name: component
    description: Dapr component type (pubsub|statestore|binding|secret)
    required: true
  - name: name
    description: Component name
    required: true
  - name: provider
    description: Backend provider (redis|kafka|postgres|azure)
    required: false
agent: cloud-native-deployer
---

# Deploy Dapr Skill

Configure Dapr components for microservices.

## Component Types

### Pub/Sub
```yaml
apiVersion: dapr.io/v1alpha1
kind: Component
metadata:
  name: {{name}}
spec:
  type: pubsub.redis
  version: v1
  metadata:
  - name: redisHost
    value: "redis:6379"
  - name: redisPassword
    secretKeyRef:
      name: redis-secret
      key: password
```

### State Store
```yaml
apiVersion: dapr.io/v1alpha1
kind: Component
metadata:
  name: {{name}}
spec:
  type: state.redis
  version: v1
  metadata:
  - name: redisHost
    value: "redis:6379"
```

### Secret Store
```yaml
apiVersion: dapr.io/v1alpha1
kind: Component
metadata:
  name: {{name}}
spec:
  type: secretstores.kubernetes
  version: v1
```

## Service Annotations

```yaml
annotations:
  dapr.io/enabled: "true"
  dapr.io/app-id: "{{app_name}}"
  dapr.io/app-port: "8080"
  dapr.io/config: "dapr-config"
```

## Output

```
DAPR COMPONENT CONFIGURED
=========================
Type: {{component}}
Name: {{name}}
Provider: {{provider}}

Files Created:
- dapr/components/{{name}}.yaml
- dapr/config.yaml (if needed)

Service Annotations Added:
[List of annotations to add to deployment]

Test Commands:
# Publish to pub/sub
dapr publish --pubsub {{name}} --topic test --data '{"msg":"hello"}'

# Invoke service
dapr invoke --app-id {{app_name}} --method mymethod
```
