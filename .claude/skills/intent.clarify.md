---
name: intent.clarify
description: Generate targeted clarification questions for ambiguous intents
arguments:
  - name: message
    description: Ambiguous user message
    required: true
  - name: ambiguities
    description: List of unclear elements
    required: false
agent: chat-intent-resolver
---

# Intent Clarify Skill

Generate clarification questions for ambiguous requests.

## Clarification Triggers

### Missing Information
- Task title unclear
- Date/time not specified
- Priority not indicated
- Target task ambiguous

### Multiple Interpretations
- "Delete it" - which task?
- "Move to tomorrow" - which task?
- "The important one" - by priority or context?

### Conflicting Signals
- "Do it later but it's urgent"
- "Add to project X and project Y"

## Question Templates

### Entity Clarification
```
I want to make sure I understand correctly.
When you say "[ambiguous term]", do you mean:
1. [Option A]
2. [Option B]
3. Something else?
```

### Scope Clarification
```
Should I apply this to:
1. Just "[specific item]"
2. All [category] items
3. Items matching [criteria]?
```

### Action Clarification
```
I can help with that. Would you like me to:
1. [Action A] - [brief description]
2. [Action B] - [brief description]
3. [Action C] - [brief description]
```

## Output

```
CLARIFICATION NEEDED
====================
Original: "{{message}}"

Ambiguity Detected: [description]

Clarifying Question:
[Generated question with options]

Once clarified, I'll:
[Describe intended action]
```
