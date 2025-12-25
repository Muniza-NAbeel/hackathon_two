---
name: deploy.rollback
description: Rollback a deployment to previous version
arguments:
  - name: name
    description: Deployment name
    required: true
  - name: revision
    description: Target revision (default previous)
    required: false
  - name: namespace
    description: Kubernetes namespace
    required: false
agent: cloud-native-deployer
---

# Deploy Rollback Skill

Rollback deployments to previous versions.

## Rollback Options

### Kubernetes Deployment
```bash
kubectl rollout undo deployment/{{name}} -n {{namespace}}
kubectl rollout undo deployment/{{name}} --to-revision={{revision}}
```

### Helm Release
```bash
helm rollback {{name}} {{revision}}
helm history {{name}}
```

## Rollback Process

1. **Identify** current and target revision
2. **Validate** target revision exists
3. **Preview** changes (diff)
4. **Execute** rollback
5. **Verify** rollback success
6. **Monitor** pod health

## Output

```
ROLLBACK EXECUTION
==================
Deployment: {{name}}
Namespace: {{namespace | "default"}}
Current Revision: [n]
Target Revision: {{revision | "n-1"}}

Changes:
- Image: [current] → [previous]
- Config: [diff summary]

Rolling back...
[████████████████████] 100%

Status: SUCCESS

Verification:
- Pods Ready: [x/y]
- Health Checks: PASSING
- Error Rate: [0%]

Rollback Details:
- Time: [duration]
- Previous Image: [tag]
- Pods Restarted: [count]

To undo this rollback:
kubectl rollout undo deployment/{{name}} --to-revision=[n]
```
