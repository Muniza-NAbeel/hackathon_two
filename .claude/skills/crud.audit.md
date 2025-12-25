---
name: crud.audit
description: Audit task operations and generate compliance reports
arguments:
  - name: period
    description: Audit period (today|week|month|custom)
    required: false
  - name: user
    description: Filter by user (optional)
    required: false
  - name: operation
    description: Filter by operation type (create|read|update|delete)
    required: false
agent: todo-crud-orchestrator
---

# CRUD Audit Skill

Generate audit reports for task operations.

## Audit Capabilities

### Operation Tracking
- All CRUD operations with timestamps
- User/actor identification
- Before/after state snapshots
- Interface of origin

### Compliance Reporting
- Data access patterns
- Modification history
- Deletion audit trail
- Permission checks

## Audit Report Sections

### Operation Summary
```
CRUD AUDIT REPORT
Period: {{period}}
=================

Operations by Type:
- Create: [count]
- Read: [count]
- Update: [count]
- Delete: [count]

Operations by Interface:
- Console: [count]
- Web: [count]
- Chatbot: [count]
```

### Detailed Log
```
[Timestamp] [User] [Interface] [Operation] [Task ID] [Details]
2024-01-15 10:30 user@email Console CREATE task-123 "New task title"
2024-01-15 11:45 user@email Web UPDATE task-123 status: pending → complete
```

### Anomaly Detection
- Unusual deletion patterns
- High-frequency modifications
- Access outside normal hours
- Failed operations

## Output

```
AUDIT REPORT: {{period}}
========================

Executive Summary:
- Total Operations: [count]
- Unique Users: [count]
- Most Active Interface: [interface]

Top Modified Tasks:
1. [Task ID] - [modification count]
2. ...

Anomalies Detected: [count]
[List of anomalies if any]

Full log exported to: [file path]
```
