---
name: deploy.helm
description: Create or update Helm charts for applications
arguments:
  - name: name
    description: Chart name
    required: true
  - name: action
    description: Action (create|update|lint|template)
    required: false
  - name: values
    description: Custom values file to use
    required: false
agent: cloud-native-deployer
---

# Deploy Helm Skill

Create and manage Helm charts.

## Chart Structure Generated

```
{{name}}/
├── Chart.yaml
├── values.yaml
├── values-staging.yaml
├── values-production.yaml
├── templates/
│   ├── _helpers.tpl
│   ├── deployment.yaml
│   ├── service.yaml
│   ├── ingress.yaml
│   ├── configmap.yaml
│   ├── secret.yaml
│   ├── hpa.yaml
│   ├── pdb.yaml
│   └── NOTES.txt
└── .helmignore
```

## Values Configuration

```yaml
# values.yaml
replicaCount: 1

image:
  repository: myapp
  tag: latest
  pullPolicy: IfNotPresent

service:
  type: ClusterIP
  port: 80

ingress:
  enabled: false
  className: nginx
  hosts: []

resources:
  limits:
    cpu: 500m
    memory: 512Mi
  requests:
    cpu: 100m
    memory: 128Mi

autoscaling:
  enabled: false
  minReplicas: 1
  maxReplicas: 10
```

## Output

```
HELM CHART {{action | "CREATED"}}
=================================
Name: {{name}}
Version: [chart version]
App Version: [app version]

Files Created/Updated:
- Chart.yaml
- values.yaml
- templates/*.yaml

Validation:
helm lint {{name}} ... [PASSED]

Install Command:
helm install {{name}} ./{{name}} -f values-staging.yaml

Upgrade Command:
helm upgrade {{name}} ./{{name}} -f values-production.yaml
```
