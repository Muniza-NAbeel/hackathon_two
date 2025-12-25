---
name: event.schema
description: Manage event schemas and versioning
arguments:
  - name: action
    description: Action (register|get|evolve|validate|list)
    required: true
  - name: schema_name
    description: Schema name for register/get/evolve
    required: false
  - name: schema_file
    description: Path to schema file (Avro/JSON Schema)
    required: false
agent: event-notification-agent
---

# Event Schema Management Skill

Manage event schemas for the notification system.

## Schema Actions

### Register Schema
Add a new schema to the registry.

### Get Schema
Retrieve current schema version.

### Evolve Schema
Update schema with compatibility check.

### Validate
Validate an event against its schema.

### List Schemas
List all registered schemas.

## Schema Definition (JSON Schema)

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "$id": "reminder.triggered.v1",
  "type": "object",
  "required": ["eventId", "eventType", "timestamp", "payload"],
  "properties": {
    "eventId": { "type": "string", "format": "uuid" },
    "eventType": { "type": "string", "enum": ["reminder.triggered"] },
    "timestamp": { "type": "string", "format": "date-time" },
    "payload": { "$ref": "#/definitions/ReminderPayload" }
  }
}
```

## Compatibility Rules

- **BACKWARD**: New schema can read old data
- **FORWARD**: Old schema can read new data
- **FULL**: Both directions compatible

## Output

### Register
```
SCHEMA REGISTERED
=================
Name: {{schema_name}}
Version: [n]
Compatibility: [BACKWARD|FORWARD|FULL]

Schema ID: [registry id]
```

### Evolve
```
SCHEMA EVOLUTION
================
Name: {{schema_name}}
Previous Version: [n-1]
New Version: [n]

Changes:
+ Added field: [field_name]
~ Modified field: [field_name]
- Removed field: [field_name] (deprecated)

Compatibility Check: [PASS/FAIL]
```
