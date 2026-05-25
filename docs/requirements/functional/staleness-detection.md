---
domain: STALE
last_updated: 2026-05-25
status: Draft
---

# Requirements: Staleness Detection

## Overview

How SDD skills detect when downstream artifacts are outdated relative to
their upstream inputs.

## Requirements

### REQ-STALE-001: Index-based staleness
Staleness detection across all skills must compare against the `last_updated`
field in `docs/requirements/index.md` rather than a single `requirements.md`
file. When any category file is updated, `index.md`'s `last_updated` must also
be bumped.
[Priority: must]

### REQ-STALE-002: Research-to-requirements staleness
When new research is completed (a `findings.md` with `status: Complete`), the
`sdd-requirements` skill should detect that research is newer than the
requirements version and inform the user that requirements may need updating.
[Priority: should]

### REQ-STALE-003: Milestone-scoped plan staleness
When a project uses per-milestone plan files (REQ-MPLAN-001), staleness
detection for a plan file must compare only against the requirements and
specs that are relevant to that milestone (identified via the plan's task →
spec `requires:` → requirement IDs). Changes to requirements or specs not
traced by the milestone's tasks must not trigger staleness for that
milestone's plan.
[Priority: must]
