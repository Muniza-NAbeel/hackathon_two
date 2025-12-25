---
name: event.monitor
description: Monitor Kafka cluster health and event metrics
arguments:
  - name: scope
    description: Monitoring scope (cluster|topic|consumer)
    required: false
  - name: topic
    description: Specific topic to monitor
    required: false
  - name: group
    description: Consumer group to monitor
    required: false
agent: event-notification-agent
---

# Event Monitor Skill

Monitor Kafka cluster health and event metrics.

## Monitoring Scopes

### Cluster Health
- Broker status
- Partition distribution
- Replication factor
- Under-replicated partitions

### Topic Metrics
- Message rate (in/out)
- Partition lag
- Retention status
- Size on disk

### Consumer Metrics
- Consumer lag per partition
- Processing rate
- Commit frequency
- Rebalance events

## Output

```
KAFKA MONITORING DASHBOARD
==========================
Cluster: {{cluster_name}}
Brokers: [active]/[total]
Status: [HEALTHY|DEGRADED|CRITICAL]

Topic Metrics:
┌──────────────────────┬───────────┬─────────┬──────────┐
│ Topic                │ Messages  │ Rate    │ Lag      │
├──────────────────────┼───────────┼─────────┼──────────┤
│ reminders.notify     │ 1.2M      │ 50/s    │ 0        │
│ tasks.recurring      │ 500K      │ 10/s    │ 12       │
│ audit.logs           │ 5M        │ 100/s   │ 0        │
└──────────────────────┴───────────┴─────────┴──────────┘

Consumer Groups:
┌──────────────────────┬───────────┬──────────┬──────────┐
│ Group                │ Members   │ Lag      │ Status   │
├──────────────────────┼───────────┼──────────┼──────────┤
│ reminder-processor   │ 3         │ 0        │ ACTIVE   │
│ audit-writer         │ 2         │ 45       │ ACTIVE   │
└──────────────────────┴───────────┴──────────┴──────────┘

Alerts:
⚠️ Consumer lag > threshold on audit.logs
```
