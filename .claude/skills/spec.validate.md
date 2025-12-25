---
name: spec.validate
description: Validate specification documents against quality gates and SDD standards
arguments:
  - name: feature
    description: Feature name to validate
    required: true
  - name: strict
    description: Enable strict validation mode (fail on warnings)
    required: false
agent: spec-analyst
---

# Spec Validate Skill

Validate specifications against Spec-Driven Development quality gates.

## Validation Checklist

### spec.md Quality Gates
- [ ] Clear problem statement defined
- [ ] User personas/stakeholders identified
- [ ] In-scope items explicitly listed
- [ ] Out-of-scope items explicitly listed
- [ ] Acceptance criteria are measurable
- [ ] Error cases documented
- [ ] Edge cases covered
- [ ] Non-functional requirements specified
- [ ] Dependencies identified
- [ ] No ambiguous language (should/might/could without specifics)

### plan.md Quality Gates
- [ ] Architectural decisions documented
- [ ] Rationale provided for each decision
- [ ] Trade-offs explicitly stated
- [ ] API contracts defined
- [ ] Data models specified
- [ ] Integration points described
- [ ] Risk analysis included
- [ ] Aligns with constitution.md principles

### tasks.md Quality Gates
- [ ] Tasks are atomic (< 4 hours)
- [ ] Each task has acceptance criteria
- [ ] Test cases are specific
- [ ] Dependencies between tasks explicit
- [ ] Tasks trace to spec requirements
- [ ] No task is too vague

## Output

```
VALIDATION REPORT: {{feature}}
================================

spec.md:  [PASS/FAIL] - [X/Y checks passed]
plan.md:  [PASS/FAIL] - [X/Y checks passed]
tasks.md: [PASS/FAIL] - [X/Y checks passed]

ISSUES FOUND:
-------------
[Severity] [Document] [Issue description]

OVERALL: [READY FOR IMPLEMENTATION / NEEDS REVISION]
```
