---
name: spec.analyze
description: Perform deep analysis of specification documents (spec.md, plan.md, tasks.md) for a feature
arguments:
  - name: feature
    description: Feature name (directory under specs/)
    required: true
agent: spec-analyst
---

# Spec Analyze Skill

Analyze the specification documents for the given feature and produce a comprehensive analysis report.

## Task

1. Read all specification documents from `specs/{{feature}}/`:
   - `spec.md` - Feature requirements
   - `plan.md` - Architectural decisions
   - `tasks.md` - Implementation tasks

2. Analyze each document for:
   - Completeness of requirements
   - Clarity of acceptance criteria
   - Testability of each requirement
   - Identified risks and gaps

3. Generate an analysis report including:
   - Summary of feature scope
   - Strengths of current specification
   - Areas needing improvement
   - Risk assessment
   - Recommended next steps

## Output Format

```markdown
# Specification Analysis: {{feature}}

## Summary
- **Status**: [Ready/Needs Work/Critical Issues]
- **Documents Found**: [list]
- **Completeness Score**: [0-100%]

## Document Analysis

### spec.md
[Analysis of requirements document]

### plan.md
[Analysis of architectural plan]

### tasks.md
[Analysis of task breakdown]

## Key Findings
1. [Finding 1]
2. [Finding 2]
...

## Recommendations
1. [Priority] [Recommendation]
...
```
