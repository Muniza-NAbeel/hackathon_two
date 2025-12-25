---
name: crud.migrate
description: Migrate task data between storage backends or versions
arguments:
  - name: source
    description: Source storage (json|sqlite|postgres|api)
    required: true
  - name: target
    description: Target storage (json|sqlite|postgres|api)
    required: true
  - name: dry_run
    description: Preview migration without executing
    required: false
agent: todo-crud-orchestrator
---

# CRUD Migration Skill

Migrate task data between storage backends.

## Migration Process

### Pre-Migration
1. **Validate** source connection
2. **Validate** target connection
3. **Analyze** data volume and structure
4. **Check** schema compatibility
5. **Estimate** migration time

### Migration Execution
1. **Export** data from source
2. **Transform** to target format
3. **Validate** data integrity
4. **Import** to target
5. **Verify** record counts match

### Post-Migration
1. **Run** integrity checks
2. **Compare** source and target
3. **Generate** migration report
4. **Archive** source (optional)

## Schema Mapping

```
Source Field → Target Field [Transformation]
task_id → id [UUID conversion]
due → due_date [ISO format]
done → status [boolean to enum]
```

## Output

```
MIGRATION: {{source}} → {{target}}
===================================
Mode: {{dry_run ? "DRY RUN" : "LIVE"}}

Pre-Check:
- Source records: [count]
- Target (before): [count]
- Schema compatible: [Yes/No]

Migration Progress:
[████████████░░░░░░░░] 60% - 600/1000 tasks

Results:
- Migrated: [count]
- Skipped: [count]
- Failed: [count]

Verification:
- Source count: [count]
- Target count: [count]
- Integrity check: [PASS/FAIL]

{{dry_run ? "Run without --dry_run to execute" : "Migration complete!"}}
```
