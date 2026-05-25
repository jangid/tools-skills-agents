---
domain: CHKC
last_updated: 2026-05-25
status: Draft
---

# Requirements: Chunk-Close Review

## Overview

Structured review checklist at milestone boundaries during implementation.
Catches spec-implementation drift, missing traceability updates, and
undocumented deviations before they ripple into downstream chunks.
Derived from RS-002 finding P1 (chunk-close review), P4 (drift detection),
and P5 (traceability enforcement). (see RS-002)

## Requirements

### REQ-CHKC-001: Milestone close checkpoint
After completing all tasks in a milestone, `sdd-implement` must execute a
structured review checklist before reporting the milestone as complete. The
checklist runs at the milestone boundary defined in the plan (Step 4:
Milestone Checkpoints in current skill).
[Priority: must]

### REQ-CHKC-002: Spec-implementation type alignment check
The milestone close checklist must extract data type definitions (class
names and field names) from spec code blocks referenced by the milestone's
tasks, and grep the implementation for matching definitions. Mismatches in
class names or field names must be reported as findings.
[Priority: must]

### REQ-CHKC-003: Traceability matrix update check
The milestone close checklist must verify that the Test and Implementation
columns in `docs/requirements/traceability.md` are populated for all
requirements covered by the milestone's tasks (identified via task → spec
`requires:` → requirement IDs). If any column is empty, the implementer
must fill it before the milestone is marked complete.
[Priority: must]

### REQ-CHKC-004: Test coverage per spec check
The milestone close checklist must verify that each spec referenced by the
milestone's tasks has at least one corresponding test file that imports
from the implementation module. Specs with zero test coverage must be
flagged as findings.
[Priority: must]

### REQ-CHKC-005: Q-IMPL audit
The milestone close checklist must identify any implementation decisions
that deviated from spec but are not documented as Q-IMPL entries (see
REQ-QIMPL-001). Undocumented deviations must be flagged as findings.
[Priority: must]

### REQ-CHKC-006: Tiered enforcement
Checklist findings must be classified by severity:
- **Blocking**: Type-name mismatches (REQ-CHKC-002) and missing
  traceability entries (REQ-CHKC-003) hard-block the milestone close.
  The implementer must fix them before proceeding.
- **Advisory**: Q-IMPL audit findings (REQ-CHKC-005) and test coverage
  gaps (REQ-CHKC-004) are advisory. The operator may override each with
  a written rationale that gets documented in the milestone close report.
[Priority: must]

### REQ-CHKC-007: Milestone close report
The milestone close checklist must produce a structured findings report
listing each check, its status (pass/block/advisory), and any remediation
needed or override rationale provided. The report is presented to the
operator before the milestone is closed.
[Priority: must]
