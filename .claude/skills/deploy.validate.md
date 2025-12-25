---
name: deploy.validate
description: Validate deployment artifacts before applying
arguments:
  - name: path
    description: Path to deployment files
    required: true
  - name: type
    description: Validation type (docker|helm|k8s|all)
    required: false
agent: cloud-native-deployer
---

# Deploy Validate Skill

Validate deployment artifacts.

## Validation Checks

### Docker Validation
- [ ] Dockerfile syntax valid
- [ ] Base image exists and is pinned
- [ ] Non-root user configured
- [ ] Health check defined
- [ ] No secrets in build args
- [ ] .dockerignore present

### Helm Validation
- [ ] Chart.yaml valid
- [ ] values.yaml valid YAML
- [ ] Templates render without errors
- [ ] No deprecated APIs
- [ ] Resources have limits defined
- [ ] Labels follow convention

### Kubernetes Validation
- [ ] Valid YAML syntax
- [ ] API versions current
- [ ] Resource limits defined
- [ ] Security context set
- [ ] Probes configured
- [ ] Labels and selectors match

## Output

```
DEPLOYMENT VALIDATION
=====================
Path: {{path}}
Type: {{type | "all"}}

Docker Validation:
✅ Dockerfile syntax: VALID
✅ Non-root user: CONFIGURED
✅ Health check: DEFINED
⚠️ Base image: Not pinned (using :latest)

Helm Validation:
✅ helm lint: PASSED
✅ helm template: SUCCESS
❌ Deprecated API: extensions/v1beta1/Ingress

Kubernetes Validation:
✅ Syntax: VALID
✅ API versions: CURRENT
⚠️ Resource limits: Missing on 1 container

Summary:
- Errors: [count]
- Warnings: [count]
- Status: [PASS/FAIL]

{{errors > 0 ? "Fix errors before deploying" : "Ready for deployment"}}
```
