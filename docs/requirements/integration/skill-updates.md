---
domain: SKILL
last_updated: 2026-05-25
status: Approved
research_refs: [RS-003, RS-004]
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

### REQ-SKILL-009: sdd-implement chunk-close checklist
`sdd-implement` must add the structured chunk close review checklist
(REQ-CHKC-001 through REQ-CHKC-008) to its implementation process. The
current "Step 4: Milestone Checkpoints" must be renamed to distinguish
chunk-level checkpoints (chunk close review) from milestone-level
checkpoints (delivery approval). Chunk close runs at each `### Chunk N`
boundary; milestone checkpoints run at delivery milestone boundaries.
[Priority: must]

### REQ-SKILL-010: sdd-implement Q-IMPL protocol
`sdd-implement` must document the three-tier deviation protocol
(REQ-QIMPL-001 through REQ-QIMPL-003) in its implementation process,
including tier classification guidance and Q-IMPL entry format.
[Priority: must]

### REQ-SKILL-011: sdd-implement spike code separation
`sdd-implement` must add a rule for `[spike]` tasks: spike code is throwaway
and must be written in a scratch location. Spike findings go to
`docs/spikes/{topic}.md`, throwaway code goes to `scripts/spike_*`. Production
code for the same functionality must be written fresh against the spec, not
adapted from spike code.
[Priority: should]

### REQ-SKILL-012: sdd-implement CLAUDE.md convention reading
`sdd-implement` must instruct the implementer to read `CLAUDE.md` as the
first item in its context loading step. Project conventions from `CLAUDE.md`
take precedence over generic patterns when choosing libraries, coding
patterns, and project structure.
[Priority: must]

### REQ-SKILL-013: sdd-specs cross-spec consistency
`sdd-specs` must add the cross-spec consistency reading pass (REQ-XSPEC-001,
REQ-XSPEC-002) after writing all specs and before the final coverage check.
[Priority: must]

### REQ-SKILL-014: sdd-plan milestone support
`sdd-plan` must support per-milestone plan files (REQ-MPLAN-001 through
REQ-MPLAN-004) when the project defines multiple milestones. For single-
milestone projects, the existing single-file behavior must be preserved.
[Priority: must]

### REQ-SKILL-015: sdd-replan milestone support
`sdd-replan` must work with per-milestone plan files, archiving and revising
the correct milestone's plan file based on which milestone's tasks are
affected.
[Priority: must]

### REQ-SKILL-016: Milestone-scoped staleness in plan skills
`sdd-plan` and `sdd-implement` must implement milestone-scoped staleness
detection (REQ-STALE-003) when reading per-milestone plan files, comparing
only against requirements and specs traced by that milestone's tasks.
[Priority: must]

### REQ-SKILL-017: sdd-migrate v2→v3 support
`sdd-migrate` must implement v2→v3 migration steps (REQ-MIG-009 through
REQ-MIG-014): version detection for v3, plan vocabulary rename, optional
multi-milestone split, capability report, v1→v3 sequential composition, and
finalization. The existing v1→v2 logic must remain unchanged.
(see RS-003)
[Priority: must]

### REQ-SKILL-018: sdd-review skill
A new `sdd-review` skill must be created at `skills/sdd-review/SKILL.md`
implementing the external review requirements (REQ-REV-001 through
REQ-REV-008): phase detection with phase-specific checklists, structured
report format, required inputs specification, bias disclosure, trigger
classification, scope boundaries against chunk-close/XSPEC/sdd-verify,
session-isolation confirmation, and scope-completeness checking.
(see RS-004)
[Priority: must]
