# Phase 0 Research: Todo In-Memory Console Application

**Feature**: Phase I Todo Console App
**Date**: 2025-12-24
**Status**: Complete

---

## Research Summary

This document consolidates all Phase 0 research findings for the Phase I Todo Console Application. All initial NEEDS CLARIFICATION items have been resolved.

---

## 1. CLI Interaction Pattern

**Decision**: Interactive menu-driven interface

**Rationale**:
- User Story 6 explicitly describes a main menu with numbered options
- Better UX for learning/demonstration purposes (Phase I goal)
- Aligns with spec's acceptance scenarios describing menu navigation

**Alternatives Considered**:
| Alternative | Why Rejected |
|-------------|--------------|
| Command-line arguments (`python todo.py add "Task"`) | Less intuitive for new users; spec describes menu navigation |
| Hybrid (both menu and CLI args) | Over-engineering for Phase I scope |

---

## 2. Output Formatting Strategy

**Decision**: Plain text with ASCII status indicators

**Rationale**:
- No external dependencies (Constitution constraint)
- Python stdlib provides adequate formatting
- Status indicators `[ ]` and `[x]` are universal and clear
- Sufficient for Phase I console experience

**Alternatives Considered**:
| Alternative | Why Rejected |
|-------------|--------------|
| `rich` library | External dependency; violates Phase I constraints |
| `tabulate` library | External dependency |
| JSON output mode | Out of scope; deferred to Phase II API |

---

## 3. Data Storage Pattern

**Decision**: Python dictionary (`dict[int, Task]`)

**Rationale**:
- O(1) lookup by task ID for update/delete/toggle operations
- Simple, stdlib-only implementation
- Easy to replace with persistent storage in Phase II

**Alternatives Considered**:
| Alternative | Why Rejected |
|-------------|--------------|
| List of Tasks | O(n) lookup by ID; less efficient |
| SQLite in-memory | External setup; overkill for Phase I |

---

## 4. Task Model Implementation

**Decision**: Python dataclass

**Rationale**:
- Built-in since Python 3.7
- Automatic `__init__`, `__repr__`, `__eq__`
- Clean, readable syntax
- Easy serialization with `asdict()`

**Alternatives Considered**:
| Alternative | Why Rejected |
|-------------|--------------|
| Plain class | More boilerplate code |
| NamedTuple | Immutable; tasks need state changes |
| Pydantic model | External dependency |

---

## 5. ID Generation Strategy

**Decision**: Auto-increment integer, never reused

**Rationale**:
- Simple and predictable
- Matches spec requirement (FR-002)
- Prevents ID collision issues
- Easy to implement with counter variable

**Alternatives Considered**:
| Alternative | Why Rejected |
|-------------|--------------|
| UUID | Overkill; harder to type for users |
| Reusing deleted IDs | Spec explicitly states IDs never reused |

---

## 6. Input Validation Approach

**Decision**: Validate at menu.py layer, raise exceptions for business rules

**Rationale**:
- Separation of concerns: UI handles format validation
- Business layer (task_manager) handles domain rules
- Clear error messages at point of validation

**Validation Matrix**:
| Input | Validation Layer | Rule |
|-------|-----------------|------|
| Menu choice | menu.py | Must be 1-6 |
| Task ID format | menu.py | Must be positive integer |
| Task ID exists | task_manager.py | Must exist in storage |
| Title empty | task_manager.py | Cannot be empty after trim |
| Title length | task_manager.py | Max 100 chars |
| Description length | task_manager.py | Max 500 chars |

---

## 7. Error Handling Pattern

**Decision**: User-friendly messages with retry capability

**Rationale**:
- FR-009 requires graceful handling with clear messages
- Users should be able to recover from errors without restarting
- No stack traces or technical errors shown to user

**Error Response Pattern**:
```
1. Display [ERROR] prefix with descriptive message
2. Explain what went wrong
3. Suggest corrective action
4. Allow retry or return to menu
```

---

## 8. Timestamp Handling

**Decision**: Use `datetime.now()` at creation time

**Rationale**:
- Spec states "creation timestamp when a new task is added" (FR-004)
- No timezone conversion required (per assumptions)
- Display format: `YYYY-MM-DD HH:MM`

**Alternatives Considered**:
| Alternative | Why Rejected |
|-------------|--------------|
| UTC timestamps | Spec says no timezone conversion needed |
| Unix timestamps | Less readable for users |

---

## 9. Testing Strategy

**Decision**: Manual testing with documented scenarios

**Rationale**:
- Phase I is a basic console app
- 39 test scenarios mapped to 15 functional requirements
- No pytest setup needed (deferred to Phase II)
- Acceptance scenarios in spec are comprehensive

**Test Coverage Target**:
- 100% of functional requirements (FR-001 to FR-015)
- All edge cases documented in spec

---

## 10. Future Extensibility Patterns

### Storage Interface

Design TaskStorage as replaceable interface:
- Same method signatures
- Different implementations (JSON, SQLite, PostgreSQL)
- Factory pattern for storage selection

### Serialization

Prepare for JSON export:
- Use `dataclasses.asdict()` for conversion
- Handle datetime with `.isoformat()`
- Reconstruct with `datetime.fromisoformat()`

### Potential Fields

Document potential future fields (not implemented):
- `due_at: Optional[datetime]`
- `priority: int`
- `category: str`

---

## Dependencies Research

### Python Stdlib Modules Required

| Module | Purpose | Python Version |
|--------|---------|----------------|
| dataclasses | Task model | 3.7+ |
| datetime | Timestamps | 2.x+ |
| typing | Type hints | 3.5+ |

### External Dependencies

**None required** for Phase I.

---

## Best Practices Applied

### From Python Community

1. **PEP 8**: Code style guidelines (snake_case, etc.)
2. **PEP 484**: Type hints for all functions
3. **Dataclasses**: Modern data structure pattern
4. **Dependency Injection**: Pass storage as parameter

### From Clean Code Principles

1. **Single Responsibility**: One purpose per function
2. **No Global State**: Pass dependencies explicitly
3. **Clear Naming**: Verb-first for functions
4. **Early Returns**: For validation failures

---

## Conclusion

All research items have been resolved. The plan is ready for implementation with:
- Clear architectural decisions
- No external dependencies
- Comprehensive test scenarios
- Future extensibility patterns documented

**Next Step**: Proceed to implementation (`/sp.implement`)
