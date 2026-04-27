---
domain: PLAN
last_updated: 2026-04-28
status: Approved
---

# Requirements: Plan Management

## Overview

How the implementation plan stays lean across SDD cycles through archival
and summarization of completed work.

## Requirements

### REQ-PLAN-001: Active plan size bound
`docs/plan.md` must contain only current and future milestones with their tasks.
Completed milestones must be summarized to a single line each (milestone name,
completion date, task count) in a `## Completed` section at the bottom of the
active plan.
[Priority: must]

### REQ-PLAN-002: Plan archival
When `sdd-plan` rewrites a plan (due to staleness or new cycle) or `sdd-replan`
makes significant changes, the previous plan must be archived to
`docs/plan-history/{YYYY-MM-DD}-{reason}.md` before modification.
[Priority: must]

### REQ-PLAN-003: Changelog in archive only
Replan changelogs must be written to the archived plan file, not appended to the
active `docs/plan.md`. The active plan must not contain a changelog section.
[Priority: must]

### REQ-PLAN-004: Removed tasks cleanup
When tasks are invalidated during replanning, they must be moved to the archive
file. The active plan must not contain `[removed: ...]` markers.
[Priority: must]
