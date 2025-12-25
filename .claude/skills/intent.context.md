---
name: intent.context
description: Load and analyze conversation context for reference resolution
arguments:
  - name: reference
    description: Reference to resolve (it, that, this, etc.)
    required: true
  - name: depth
    description: How many conversation turns to analyze (default 5)
    required: false
agent: chat-intent-resolver
---

# Intent Context Skill

Resolve contextual references using conversation history.

## Reference Types

### Pronoun References
- "it" → last mentioned entity
- "that" → previously discussed item
- "this" → current topic
- "them" → plural entities

### Implicit References
- "again" → repeat last action
- "same" → same parameters as before
- "also" → add to previous action
- "instead" → replace previous action

### Temporal References
- "earlier" → previous conversation segment
- "before" → prior to specific event
- "the last one" → most recent of type

## Resolution Process

1. **Scan** recent conversation turns
2. **Identify** candidate referents
3. **Score** candidates by relevance
4. **Select** highest confidence match
5. **Validate** context fit

## Output

```
CONTEXT RESOLUTION
==================
Reference: "{{reference}}"
Search Depth: {{depth}} turns

Candidates Found:
1. [Entity] - Confidence: [%] - From: "[context]"
2. [Entity] - Confidence: [%] - From: "[context]"

Resolution:
"{{reference}}" → "[resolved entity]"

Context Used:
[Turn N]: "[relevant message excerpt]"
[Turn M]: "[relevant message excerpt]"

Confidence: [high|medium|low]
{{low confidence ? "Recommend asking for clarification" : ""}}
```
