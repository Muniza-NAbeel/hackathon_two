---
name: memory.search
description: Search across conversation history
arguments:
  - name: query
    description: Search query (text or semantic)
    required: true
  - name: user_id
    description: Limit to specific user
    required: false
  - name: date_range
    description: Date range filter (e.g., "last 7 days")
    required: false
agent: conversation-memory-manager
---

# Memory Search Skill

Search across stored conversation history.

## Search Capabilities

### Text Search
- Full-text search across message content
- Exact phrase matching
- Wildcard support

### Semantic Search
- Meaning-based search (if vector store available)
- Find similar conversations
- Context-aware matching

### Filtered Search
- By user
- By date range
- By conversation metadata
- By message role

## Search Process

1. **Parse** search query and filters
2. **Execute** against search index
3. **Rank** results by relevance
4. **Extract** matching snippets
5. **Return** paginated results

## Output

```
SEARCH RESULTS
==============
Query: "{{query}}"
Filters: {{filters}}
Results: [count] found

1. [Session Title] - [date]
   Score: [relevance %]
   Match: "...[highlighted match]..."

2. [Session Title] - [date]
   Score: [relevance %]
   Match: "...[highlighted match]..."

...

To load a conversation:
> memory.load session_id=[session_id]
```
