---
name: memory.load
description: Load conversation history from the database
arguments:
  - name: session_id
    description: Session ID to load
    required: false
  - name: user_id
    description: Load most recent for user
    required: false
  - name: limit
    description: Number of messages to load (default all)
    required: false
agent: conversation-memory-manager
---

# Memory Load Skill

Retrieve conversation history from persistent storage.

## Load Options

### By Session ID
Load specific conversation by its unique identifier.

### By User ID
Load most recent conversation for a user.

### With Pagination
Load subset of messages for large conversations.

## Load Process

1. **Query** database for matching records
2. **Validate** conversation exists
3. **Deserialize** message content
4. **Reconstruct** conversation state
5. **Apply** to current context

## Output

```
CONVERSATION LOADED
===================
Session ID: [uuid]
Title: "[title]"
Created: [timestamp]
Last Updated: [timestamp]

Messages Loaded: [count] of [total]

Conversation Preview:
---------------------
[First few exchanges summarized]

Context restored. You can continue from where you left off.
```
