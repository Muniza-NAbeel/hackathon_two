# Phase 5 Research: Technology Decisions

**Date**: 2026-01-18
**Feature**: 005-Advanced-Cloud-Deployment
**Status**: Complete

## Research Areas

This document captures technology research and decisions for Phase 5 event-driven architecture.

---

## 1. Event Streaming Platform

### Decision: Redpanda

### Rationale
- **Kafka API Compatible**: Drop-in replacement, same client libraries work
- **Simpler Operations**: No ZooKeeper dependency, single binary deployment
- **Better Performance**: Lower latency, higher throughput in benchmarks
- **Managed Cloud Option**: Redpanda Cloud for production
- **Minikube Friendly**: Single pod deployment for local development

### Alternatives Considered

| Option | Pros | Cons | Rejected Because |
|--------|------|------|------------------|
| Apache Kafka | Industry standard, mature | Complex (ZooKeeper), heavy resources | Operational complexity |
| AWS Kinesis | Managed, AWS native | AWS lock-in, different API | Vendor lock-in |
| Azure Event Hubs | Kafka compatible, Azure native | Azure lock-in | Vendor lock-in |
| NATS JetStream | Lightweight, simple | Less mature, different patterns | Ecosystem maturity |

### Implementation Notes
- Local: Deploy Redpanda in Minikube via Helm chart
- Cloud: Use Redpanda Cloud Serverless (free tier available)
- Topics: `task-events`, `reminders`, `task-updates`

---

## 2. Microservice Runtime

### Decision: Dapr 1.12.0+

### Rationale
- **Building Block Abstractions**: Pub/Sub, State, Bindings, Secrets standardized
- **Multi-Cloud Portable**: Same code works on any cloud
- **mTLS Built-in**: Secure service-to-service communication
- **Kubernetes Native**: First-class K8s support with sidecars
- **Active Community**: Strong ecosystem, good documentation

### Alternatives Considered

| Option | Pros | Cons | Rejected Because |
|--------|------|------|------------------|
| Direct Kafka SDK | Full control, no abstraction overhead | Vendor lock-in, boilerplate | No portability |
| Istio Service Mesh | Mature, enterprise features | Complex, resource heavy | Overkill for this use case |
| Linkerd | Lightweight service mesh | No pub/sub abstraction | Missing building blocks |
| Spring Cloud | Java ecosystem | Not Python | Wrong language |

### Implementation Notes
- Install Dapr on Kubernetes via CLI: `dapr init -k --runtime-version 1.12.0`
- Each service annotated for Dapr sidecar injection
- Components configured per environment (local/cloud)

---

## 3. State Store for Idempotency

### Decision: Redis (Local) / PostgreSQL (Cloud)

### Rationale
- **Local Development**: Redis is fast, simple, perfect for TTL-based deduplication
- **Cloud Production**: Reuse existing Neon PostgreSQL, avoid new service
- **Dapr Abstraction**: Same code works with both backends
- **TTL Support**: Both support automatic expiry for 24h deduplication window

### Alternatives Considered

| Option | Pros | Cons | Rejected Because |
|--------|------|------|------------------|
| Redis only | Simple, fast | Additional cloud service cost | Extra infrastructure |
| In-memory | No dependencies | Lost on restart | Unreliable |
| DynamoDB | Managed, scalable | AWS lock-in | Vendor lock-in |

### Implementation Notes
- Key pattern: `{service}:processed:{event_id}`
- TTL: 86400 seconds (24 hours)
- Check before processing, set after successful processing

---

## 4. Event Schema Format

### Decision: CloudEvents v1.0

### Rationale
- **Industry Standard**: CNCF specification, wide adoption
- **Extensible**: Custom attributes via extensions
- **Interoperable**: Works across languages and platforms
- **Dapr Native**: Dapr Pub/Sub uses CloudEvents by default

### Schema Design

```json
{
  "specversion": "1.0",
  "type": "com.todo.task.completed",
  "source": "/services/chat-backend",
  "id": "uuid-v4",
  "time": "2026-01-18T10:00:00Z",
  "datacontenttype": "application/json",
  "data": {
    "task_id": 123,
    "user_id": "uuid",
    "task_data": {...}
  }
}
```

### Event Types
- `com.todo.task.created`
- `com.todo.task.updated`
- `com.todo.task.completed`
- `com.todo.task.deleted`
- `com.todo.reminder.due`

---

## 5. Cron Scheduling for Reminders

### Decision: Dapr Cron Binding

### Rationale
- **Kubernetes Native**: Works in K8s without external scheduler
- **Dapr Integrated**: Same configuration pattern as other components
- **Simple**: Just a YAML configuration, no custom scheduler code
- **Scoped**: Can limit which service receives triggers

### Alternatives Considered

| Option | Pros | Cons | Rejected Because |
|--------|------|------|------------------|
| Kubernetes CronJob | Native K8s | New pod per trigger, cold starts | Inefficient |
| Celery Beat | Python native, flexible | Additional infrastructure (Redis/RabbitMQ) | Complexity |
| APScheduler | In-process | Not distributed, lost on restart | Unreliable |
| External cron service | Managed | Extra cost, external dependency | Unnecessary |

### Implementation Notes
- Schedule: `*/5 * * * *` (every 5 minutes)
- Target: Backend `/reminder-cron` endpoint
- Scoped to `chat-backend` service only

---

## 6. Service-to-Service Communication

### Decision: Dapr Service Invocation

### Rationale
- **Service Discovery**: Automatic via Kubernetes DNS
- **Load Balancing**: Built-in across replicas
- **Retries**: Automatic retry with backoff
- **mTLS**: Encrypted without code changes

### Use Cases
- Recurring Task Service → Backend: Create new task
- Notification Service → Backend: Mark reminder sent (future)

### Implementation Notes
```python
# Call backend from recurring task service
resp = await httpx.post(
    "http://localhost:3500/v1.0/invoke/chat-backend/method/api/internal/tasks",
    json=task_data
)
```

---

## 7. Local Development Environment

### Decision: Minikube with Helm

### Rationale
- **Production Parity**: Same Kubernetes environment as cloud
- **Resource Efficient**: Single-node cluster, minimal overhead
- **Dapr Support**: Full Dapr functionality
- **Docker Integration**: Direct image building with `minikube docker-env`

### Local Stack
| Component | Implementation |
|-----------|---------------|
| Kubernetes | Minikube |
| Kafka | Redpanda (single node) |
| State Store | Redis |
| Database | Neon PostgreSQL (cloud, same as Phase 3/4) |
| Secrets | Kubernetes Secrets |

---

## 8. Cloud Deployment Target

### Decision: DOKS (DigitalOcean Kubernetes Service) - Primary

### Rationale
- **Cost Effective**: Lower cost than GKE/AKS for small clusters
- **Simple**: Easy setup, good documentation
- **Managed Kubernetes**: No control plane management
- **DigitalOcean Ecosystem**: Easy integration with DOCR, Spaces

### Alternatives
- GKE: More features, but higher cost and complexity
- AKS: Good for Azure users, but Azure-centric
- EKS: AWS native, but most complex

### Cloud Stack
| Component | Implementation |
|-----------|---------------|
| Kubernetes | DOKS 1.28+ |
| Kafka | Redpanda Cloud Serverless |
| State Store | Neon PostgreSQL (Dapr state) |
| Database | Neon PostgreSQL (existing) |
| Secrets | Kubernetes Secrets + External Secrets Operator |
| Ingress | NGINX Ingress + cert-manager |
| Registry | DOCR (DigitalOcean Container Registry) |

---

## 9. CI/CD Platform

### Decision: GitHub Actions

### Rationale
- **GitHub Native**: Repository already on GitHub
- **Free Tier**: Sufficient for this project
- **Marketplace**: Rich ecosystem of actions
- **Matrix Builds**: Easy parallel testing

### Pipeline Structure
1. **CI (on PR)**: Lint → Test → Build
2. **Deploy Staging (on merge)**: Build → Push → Deploy to staging
3. **Deploy Production (manual)**: Approval → Deploy to production
4. **Rollback (manual)**: Revert to previous version

---

## 10. Observability Strategy

### Decision: Structured Logging + Dapr Observability

### Rationale
- **Phase 5 Scope**: Full observability stack (Prometheus/Grafana) is out of scope
- **Structured Logs**: JSON logs with correlation IDs for tracing
- **Dapr Metrics**: Built-in Prometheus metrics from Dapr sidecars
- **Future Ready**: Can add Prometheus/Grafana in Bonus Phase

### Implementation Notes
- Python `structlog` for structured JSON logging
- Include `event_id`, `user_id`, `trace_id` in all logs
- Dapr exposes metrics on `:9090/metrics`

---

## Summary of Decisions

| Area | Decision | Confidence |
|------|----------|------------|
| Event Streaming | Redpanda | High |
| Runtime | Dapr 1.12.0+ | High |
| State Store | Redis (local) / PostgreSQL (cloud) | High |
| Event Format | CloudEvents v1.0 | High |
| Cron Scheduling | Dapr Cron Binding | High |
| Service Invocation | Dapr Service Invocation | High |
| Local Dev | Minikube + Helm | High |
| Cloud Target | DOKS | Medium (user preference) |
| CI/CD | GitHub Actions | High |
| Observability | Structured Logging | High |

---

## Open Questions (Resolved)

1. **Q**: Should we use separate Kafka clusters for local and cloud?
   **A**: Yes - Redpanda local, Redpanda Cloud for production

2. **Q**: How to handle event ordering across partitions?
   **A**: Partition by `user_id` to ensure per-user ordering

3. **Q**: How to prevent duplicate notifications?
   **A**: Idempotency via Dapr State Store with 24h TTL

4. **Q**: How to handle service failures during event processing?
   **A**: Retry 3 times with exponential backoff, then DLQ

---

## References

- [Dapr Documentation](https://docs.dapr.io/)
- [Redpanda Documentation](https://docs.redpanda.com/)
- [CloudEvents Specification](https://cloudevents.io/)
- [Kubernetes Documentation](https://kubernetes.io/docs/)
- [GitHub Actions Documentation](https://docs.github.com/en/actions)
