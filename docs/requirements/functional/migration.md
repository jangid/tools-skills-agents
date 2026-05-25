---
domain: MIG
last_updated: 2026-05-25
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
  plan with accumulated changelogs (`.sdd-version` missing)
- v2: split requirements, RS-NNN research directories, lean plans
  (`.sdd-version` contains `2`)
- v3: v2 layout plus v3 conventions — plan vocabulary uses `### Chunk N:`,
  Q-IMPL protocol, chunk-close review, per-milestone support
  (`.sdd-version` contains `3`)
If artifacts are already at the highest supported version, inform the user and
exit. If a version upgrade is available, offer it.
[Priority: must] [Updated: 2026-05-25]

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

### REQ-MIG-009: v3 version detection
The migration skill must recognize `.sdd-version` value `3` as current and exit
without changes. When `.sdd-version` contains `2`, the skill must offer v2→v3
migration. When `.sdd-version` is missing (v1), the skill must run v1→v2 then
v2→v3 sequentially (see REQ-MIG-013).
[Priority: must]

### REQ-MIG-010: v2→v3 plan vocabulary rename
The migration skill must detect `### M` followed by a digit in `docs/plan.md`
headers that serve as work-unit groupings. It must propose renaming each to
`### Chunk N:` format, preserving the original numbering (M1 → Chunk 1, M2 →
Chunk 2). The operator must confirm before the rename is applied. The skill must
skip this step if: (a) the plan already uses `### Chunk N:` headers, (b) no
`docs/plan.md` exists, or (c) the plan is complete with no active work.
(see RS-003 §F2)
[Priority: must]

### REQ-MIG-011: v2→v3 multi-milestone split offer
If `docs/plan.md` contains multiple delivery milestone groupings, the migration
skill should offer to split into per-milestone plan files (`docs/plan-{id}.md`)
with `docs/plan.md` as an index. This is operator-confirmed, not automatic.
Single-file plans are valid in v3 — splitting must not be required.
(see RS-003 §F2)
[Priority: should]

### REQ-MIG-012: v2→v3 capability report
After completing v2→v3 migration, the skill must report new v3 capabilities
available to the operator: chunk-close review, Q-IMPL deviation protocol,
cross-spec consistency pass, and per-milestone plan support. The report is
informational — no operator action required.
(see RS-003 §F2)
[Priority: must]

### REQ-MIG-013: v1→v3 sequential composition
For v1 projects (`.sdd-version` missing), the migration skill must run v1→v2
migration (REQ-MIG-003 through REQ-MIG-005) then v2→v3 migration (REQ-MIG-010
through REQ-MIG-012) in a single invocation. The existing v1→v2 logic must not
be modified. The intermediate version state (`2`) exists only during execution;
the finalization writes `3` to `.sdd-version`.
(see RS-003 §F3)
[Priority: must]

### REQ-MIG-014: v2→v3 finalization
After all v2→v3 steps complete, the migration skill must write `3` to
`docs/.sdd-version`. The version marker must be written last — after all other
migration steps succeed — so partial migrations are detectable and resumable.
[Priority: must]

### REQ-MIG-015: v3 overview documentation
The SDD overview documentation must be updated when v3 is formalized to describe:
(a) the plan vocabulary convention (`### Chunk N:` for work units, "milestone"
reserved for delivery groupings), (b) the version marker semantics (tracks SDD
process version, not just artifact layout), and (c) v3 behavioral additions
(chunk-close, Q-IMPL, cross-spec, per-milestone support). The overview and
version marker must be consistent at the point of version bump.
[Priority: must]
