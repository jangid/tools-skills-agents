---
domain: MPLAN
last_updated: 2026-05-25
status: Approved
---

# Requirements: Milestone Plan Iteration

## Overview

Support for multi-milestone projects where a single `docs/plan.md` grows
unboundedly. Introduces per-milestone plan files with a lightweight index.
Requirements are milestone-agnostic — milestones are a planning concern,
and plans scope themselves to milestones via task tracing to specs and
requirements. Derived from RS-002 finding P3. (see RS-002)

## Requirements

### REQ-MPLAN-001: Per-milestone plan files
For projects with multiple milestones, each milestone must have its own
plan file: `docs/plan-{milestone-id}.md` (e.g., `docs/plan-m1.md`,
`docs/plan-m2.md`). `docs/plan.md` serves as a lightweight index listing
all milestone plans, their status, and which is currently active.
[Priority: must]

### REQ-MPLAN-002: Milestone plan frontmatter
Each per-milestone plan file must include a `milestone:` field in its YAML
frontmatter identifying which milestone it covers. The index file
`docs/plan.md` must list all known milestones with their plan file paths
and status (planned/active/complete/archived).
[Priority: must]

### REQ-MPLAN-003: Milestone lifecycle
Completed milestone plans must be archived to `docs/plan-history/` per
REQ-PLAN-002. The index file `docs/plan.md` must be updated to reflect the
milestone's completed status and archive path. In-progress milestone plans
remain at their top-level path until completion.
[Priority: must]

### REQ-MPLAN-004: Single-milestone fallback
For projects with only one milestone (or no explicit milestone structure),
`docs/plan.md` remains the single plan file with no `milestone:` frontmatter
required. The per-milestone convention activates only when the plan or specs
explicitly define multiple milestones.
[Priority: must]
