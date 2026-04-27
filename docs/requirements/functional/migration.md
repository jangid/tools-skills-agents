---
domain: MIG
last_updated: 2026-04-28
status: Approved
---

# Requirements: Migration

## Overview

How projects migrate between SDD artifact structure versions safely,
including mid-cycle migration support.

## Requirements

### REQ-MIG-001: Standalone migration skill
A new `sdd-migrate` skill must handle migration between SDD artifact structure
versions. The skill must be versioned, with the current migration being to v2.
[Priority: must]

### REQ-MIG-002: Version detection
The migration skill must detect the current artifact version:
- v1: flat `docs/research/{topic}.md` files, monolithic `docs/requirements.md`,
  plan with accumulated changelogs
- v2: the structure defined in this requirements document
If artifacts are already at the target version, inform the user and exit.
[Priority: must]

### REQ-MIG-003: Research migration
The skill must move existing `docs/research/{topic}.md` files into
`docs/research/RS-NNN-{topic}/findings.md` directories, assigning sequential RS
numbers by file date. It must create `docs/research/index.md`.
[Priority: must]

### REQ-MIG-004: Requirements migration
The skill must:
1. Split `docs/requirements.md` into category files under `docs/requirements/`
2. Remap IDs from `REQ-{TYPE}-{NNN}` to `REQ-{DOMAIN}-{NNN}`
3. Perform in-place replacement of old IDs across all docs files (specs, plan,
   verification)
4. Create `docs/requirements/index.md` with version `2.0`
5. Create `docs/requirements/traceability.md` seeded from existing spec
   `requires` fields
6. Delete the old `docs/requirements.md`
[Priority: must]

### REQ-MIG-005: Plan migration
The skill must:
1. Move `docs/plan.md` to `docs/plan-history/{date}-pre-v2-migration.md`
2. Create a new `docs/plan.md` with only active/future tasks
3. Summarize completed milestones to one line each
4. Strip all changelogs and `[removed: ...]` markers from the active plan
[Priority: must]

### REQ-MIG-006: Skill version tracking
The `sdd-migrate` skill must track the current artifact structure version (e.g.,
in a `docs/.sdd-version` file or similar marker) so future migrations can detect
the current version and apply the appropriate transformation.
[Priority: must]

### REQ-MIG-007: Safe migration
The migration must not delete any files until replacements are verified to exist.
Each step (research, requirements, plan) must be independently runnable so
partial migrations can be resumed.
[Priority: must]

### REQ-MIG-008: Mid-cycle migration
The migration skill must handle projects mid-cycle — where specs, plans, or
implementation are in progress. It must remap IDs in all existing artifacts
(specs, plan, verification) and preserve task completion status. After migration,
the relevant SDD skill must be able to resume from the detected phase.
[Priority: must]
