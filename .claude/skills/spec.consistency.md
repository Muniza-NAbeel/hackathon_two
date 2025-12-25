---
name: spec.consistency
description: Check cross-document consistency between spec.md, plan.md, and tasks.md
arguments:
  - name: feature
    description: Feature name to check
    required: true
agent: spec-analyst
---

# Spec Consistency Check Skill

Verify that all specification documents are aligned and consistent.

## Consistency Checks

### Spec → Plan Alignment
- All requirements in spec.md addressed in plan.md
- Architecture supports all specified features
- Non-functional requirements have architectural solutions
- Dependencies are acknowledged in plan

### Plan → Tasks Alignment
- All architectural components have implementation tasks
- API contracts have corresponding tasks
- Data models have migration/creation tasks
- Integration points have setup tasks

### Spec → Tasks Traceability
- Every requirement has at least one task
- Every task traces back to a requirement
- Acceptance criteria in tasks match spec
- Test cases cover all requirements

### Terminology Consistency
- Same terms used across all documents
- No conflicting definitions
- Consistent naming conventions

### Scope Consistency
- Tasks don't exceed spec scope
- No spec requirements missing from tasks
- Out-of-scope items truly excluded

## Output Format

```markdown
# Consistency Report: {{feature}}

## Cross-Reference Matrix

| Requirement | Plan Section | Tasks | Status |
|-------------|--------------|-------|--------|
| REQ-001     | 3.1          | T-001 | ✅     |
| REQ-002     | -            | -     | ❌     |

## Inconsistencies Found

### Critical
1. **[Type]**: [Description]
   - In spec.md: [reference]
   - In plan.md: [reference]
   - Resolution: [suggested fix]

### Warnings
...

## Orphaned Items
- **Tasks without requirements**: [list]
- **Requirements without tasks**: [list]
- **Plan sections without implementation**: [list]

## Consistency Score: [X/100]
```
