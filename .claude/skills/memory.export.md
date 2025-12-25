---
name: memory.export
description: Export conversation history to file
arguments:
  - name: session_id
    description: Specific session to export (or "all")
    required: true
  - name: format
    description: Export format (json|markdown|csv)
    required: false
agent: conversation-memory-manager
---

# Memory Export Skill

Export conversation history to external files.

## Export Formats

### JSON Export
```json
{
  "session": {
    "id": "uuid",
    "title": "string",
    "created_at": "timestamp"
  },
  "messages": [
    {
      "role": "user",
      "content": "string",
      "timestamp": "timestamp"
    }
  ]
}
```

### Markdown Export
```markdown
# Conversation: [Title]
Date: [created_at]

## User
[message content]

## Assistant
[message content]
```

### CSV Export
```csv
timestamp,role,content
2024-01-15T10:30:00Z,user,"message content"
2024-01-15T10:30:15Z,assistant,"response content"
```

## Export Process

1. **Load** conversation data
2. **Transform** to target format
3. **Write** to file
4. **Verify** export integrity
5. **Report** export location

## Output

```
EXPORT COMPLETE
===============
Session: [session_id]
Format: {{format}}
Messages: [count]

Exported to: [file path]
File Size: [size]

Checksum: [hash for verification]
```
