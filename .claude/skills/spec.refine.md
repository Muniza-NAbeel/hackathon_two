---
name: spec.refine
description: Suggest specific refinements to improve specification quality
arguments:
  - name: feature
    description: Feature name to refine
    required: true
  - name: focus
    description: Focus area (requirements|architecture|tasks|all)
    required: false
agent: spec-analyst
---

# Spec Refine Skill

Analyze specifications and provide actionable refinement suggestions.

## Refinement Process

1. **Read Current Specs**: Load all specification documents
2. **Identify Gaps**: Find missing or weak areas
3. **Generate Suggestions**: Create specific, actionable improvements
4. **Prioritize**: Rank suggestions by impact and effort

## Refinement Categories

### Requirements Refinements
- Clarify vague acceptance criteria
- Add missing error scenarios
- Specify performance requirements
- Define security requirements
- Add data validation rules

### Architecture Refinements
- Strengthen decision rationale
- Add missing trade-off analysis
- Define clearer API contracts
- Improve data model clarity
- Add integration details

### Task Refinements
- Break down oversized tasks
- Add missing test cases
- Clarify acceptance criteria
- Add dependency links
- Improve task descriptions

## Output Format

```markdown
# Refinement Suggestions: {{feature}}

## High Priority Refinements

### 1. [Document]: [Section]
**Current**: [What exists now]
**Issue**: [What's wrong/missing]
**Suggestion**: [Specific improvement]
**Example**:
```
[Concrete example of the improvement]
```

## Medium Priority Refinements
...

## Low Priority Refinements
...

## Quick Wins
[List of simple improvements that can be done immediately]
```
