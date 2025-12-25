---
name: memory.save
description: Persist current conversation to the database
arguments:
  - name: session_id
    description: Session identifier (auto-generated if omitted)
    required: false
  - name: metadata
    description: Additional metadata to store (JSON)
    required: false
agent: conversation-memory-manager
---

# Memory Save Skill

Persist conversation state to the database.

## Data Persisted

### Conversation Record
```json
{
  "session_id": "uuid",
  "user_id": "string",
  "title": "auto-generated or provided",
  "created_at": "ISO timestamp",
  "updated_at": "ISO timestamp",
  "message_count": "integer",
  "metadata": {}
}
```

### Message Records
```json
{
  "message_id": "uuid",
  "session_id": "uuid",
  "role": "user|assistant|system",
  "content": "string",
  "timestamp": "ISO timestamp",
  "tool_calls": [],
  "metadata": {}
}
```

## Save Process

1. **Validate** conversation state
2. **Generate** session ID if needed
3. **Extract** conversation title from content
4. **Serialize** all messages
5. **Write** to database in transaction
6. **Confirm** persistence

## Output

```
CONVERSATION SAVED
==================
Session ID: [uuid]
Title: "[auto-generated title]"
Messages: [count]
Size: [bytes]

Storage Location: [database/table]
Timestamp: [ISO timestamp]

To resume this conversation:
> memory.load session_id={{session_id}}
```
