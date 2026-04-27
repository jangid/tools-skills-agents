---
domain: SKILL
last_updated: 2026-04-28
status: Approved
---

# Requirements: Skill Updates

## Overview

Changes required across all existing SDD skills to support the v2 artifact
structure.

## Requirements

### REQ-SKILL-001: Skill update scope
All seven existing SDD skills must be updated to read/write the v2 artifact
structure. Path references, phase detection logic, and staleness checks must
reflect the new layout.
[Priority: must]

### REQ-SKILL-002: sdd-research updates
`sdd-research` must write to `docs/research/RS-NNN-{topic}/findings.md` and
auto-maintain `docs/research/index.md`.
[Priority: must]

### REQ-SKILL-003: sdd-requirements updates
`sdd-requirements` must read/write per-domain files in
`docs/requirements/{category}/`, auto-maintain `index.md` with versioning, and
detect the old monolithic format (offering migration via `sdd-migrate`).
[Priority: must]

### REQ-SKILL-004: sdd-specs updates
`sdd-specs` must read requirements from `docs/requirements/{category}/*.md`,
use the new `REQ-{DOMAIN}-{NNN}` IDs in `requires` frontmatter, and update
`docs/requirements/traceability.md` when mapping specs to requirements.
[Priority: must]

### REQ-SKILL-005: sdd-plan updates
`sdd-plan` must implement the archive pattern (REQ-PLAN-002), keep the active
plan lean (REQ-PLAN-001), and read staleness from
`docs/requirements/index.md` (REQ-STALE-001).
[Priority: must]

### REQ-SKILL-006: sdd-implement updates
`sdd-implement` must read requirements from the new paths, reference RS-* IDs
for spike tasks, and update `docs/requirements/traceability.md` when
tests/implementation are created.
[Priority: must]

### REQ-SKILL-007: sdd-verify updates
`sdd-verify` must read requirements from the new paths, verify traceability
across split files using `traceability.md`, and update the traceability matrix
with verification results.
[Priority: must]

### REQ-SKILL-008: sdd-replan updates
`sdd-replan` must write changelogs to the archive file (REQ-PLAN-003) and move
removed tasks to the archive (REQ-PLAN-004) instead of marking them in the
active plan.
[Priority: must]
