---
name: spec.phase
description: Check if specifications are ready for the next development phase
arguments:
  - name: feature
    description: Feature name to check
    required: true
  - name: target_phase
    description: Target phase (plan|tasks|implement|test|deploy)
    required: true
agent: spec-analyst
---

# Spec Phase Readiness Skill

Evaluate if specifications are ready to advance to the next development phase.

## Phase Requirements

### Ready for Planning (spec.md complete)
- [ ] Problem statement clear
- [ ] User needs documented
- [ ] Acceptance criteria defined
- [ ] Scope boundaries set
- [ ] Non-functional requirements listed

### Ready for Task Generation (plan.md complete)
- [ ] Architecture decisions finalized
- [ ] API contracts defined
- [ ] Data models specified
- [ ] Integration points mapped
- [ ] Risks identified

### Ready for Implementation (tasks.md complete)
- [ ] All tasks atomic and testable
- [ ] Dependencies ordered correctly
- [ ] Test cases defined for each task
- [ ] Acceptance criteria verifiable
- [ ] No blocking unknowns

### Ready for Testing
- [ ] All implementation tasks complete
- [ ] Unit tests passing
- [ ] Integration points tested
- [ ] Edge cases covered

### Ready for Deployment
- [ ] All tests passing
- [ ] Documentation complete
- [ ] Deployment plan created
- [ ] Rollback strategy defined

## Output

```
PHASE READINESS CHECK: {{feature}}
Target Phase: {{target_phase}}
================================

PREREQUISITES:
[x] Requirement 1 - Met
[ ] Requirement 2 - NOT MET: [reason]
[x] Requirement 3 - Met

BLOCKING ISSUES:
1. [Issue description and remediation]

STATUS: [READY / NOT READY]

NEXT STEPS:
1. [Action needed]
```
