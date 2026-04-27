---
status: Approved
last_updated: 2026-04-28
requires:
  - REQ-PLAN-001
  - REQ-PLAN-002
  - REQ-PLAN-003
  - REQ-PLAN-004
  - REQ-SKILL-005
  - REQ-SKILL-008
---

# Plan Management

## Context

In v1, `docs/plan.md` grows monotonically across SDD cycles. Three mechanisms
cause this: replan changelogs are appended, removed tasks are marked with
`[removed: reason]` instead of deleted, and completed milestones are preserved
in full. After several cycles, the plan file consumes excessive AI context and
becomes hard to navigate.

v2 introduces an archive pattern: the active plan stays lean, and history moves
to `docs/plan-history/`.

## Design

### Active Plan Structure

`docs/plan.md` contains only actionable content:

```markdown
# Implementation Plan: [Project Name]

## Overview
One paragraph: what we're implementing and the approach.

## Conventions
...

## Milestones

### M3: [Name] — [one-line description]
**Goal**: ...
**Tasks**:
1. [implement] ... — traces to [spec.md]
2. [verify] ... — traces to [spec.md]
**Verify**: ...

### M4: [Name] — [one-line description]
**Depends on**: M3
...

## Replan Triggers
- [Condition] → [what changes in the plan]

## Risks
- [Risk]: [Impact and mitigation]

## Completed
- M1: Project skeleton (2026-04-20, 3 tasks)
- M2: Core models + first feature (2026-04-25, 5 tasks)
```

**Key differences from v1**:
- The `## Completed` section contains one-line summaries, not full milestone
  details. Format: `- {name}: {description} ({date}, {task count})`.
- No `## Plan Changelog` section — changelogs live in archive files.
- No `[removed: reason]` markers — removed tasks are moved to the archive.

**Why summarize instead of remove entirely**: The one-line summaries provide
context for milestone dependencies ("M3 depends on M1" is meaningful only if
you can see what M1 was). A single line per milestone adds negligible size.

### Plan History

```
docs/plan-history/
  2026-04-20-initial.md
  2026-04-25-replan-api-change.md
  2026-04-28-pre-v2-migration.md
```

Archive files are complete snapshots of the plan at the time of archival,
including:
- All milestones (completed and pending at that time)
- Task completion status
- The changelog entry that triggered the archival

**Naming convention**: `{YYYY-MM-DD}-{reason}.md` where reason is kebab-case,
describing why the plan was archived (e.g., `replan-api-change`, `cycle-complete`,
`pre-v2-migration`).

### Archival Triggers

The active plan is archived before these operations:

1. **Plan rewrite** (`sdd-plan`): When the plan is stale and needs rewriting
   from updated specs, archive the current plan as
   `{date}-stale-rewrite.md` before creating the new one.

2. **Significant replan** (`sdd-replan`): When replanning changes more than
   task reordering — adding/removing milestones, changing approach. Archive as
   `{date}-replan-{reason}.md`. Minor replans (reordering tasks within a
   milestone) do not trigger archival.

3. **Cycle completion** (`sdd-verify`): When verification passes and the cycle
   is complete, the plan becomes historical. Archive as
   `{date}-cycle-complete.md`.

**What counts as "significant"**: If the replan adds or removes milestones, or
changes the approach described in the Overview section, it's significant.
Task-level changes within existing milestones are minor.

### Replan Behavior Changes

When `sdd-replan` revises the plan:

1. If significant (per above): archive current plan, then write the revised
   plan fresh.
2. If minor: edit the plan in place.
3. In both cases:
   - Removed tasks go to the archive file, not marked inline.
   - Changelog entries go to the archive file, not appended to the active plan.
   - Completed milestone summaries are preserved in the `## Completed` section.

### Interaction with Staleness Detection

`sdd-plan` reads staleness from `docs/requirements/index.md` (per overview
spec). When the plan is stale:

1. Archive the current plan.
2. Re-read all approved specs.
3. Produce a new plan, carrying forward the `## Completed` section from the
   archived plan.

## Verification

### Automated
- Validate `docs/plan.md` contains no `## Plan Changelog` section
- Validate `docs/plan.md` contains no `[removed: ...]` markers
- Validate completed milestones are single-line summaries
- Validate `docs/plan-history/` files follow the naming convention

### Manual
- After a replan, confirm the archived file contains the full pre-replan state
- After a cycle, confirm the archive captures the final plan state

### Acceptance Criteria
- [ ] Active plan contains only current/future milestones (REQ-PLAN-001)
- [ ] Completed milestones are one-line summaries (REQ-PLAN-001)
- [ ] Plan is archived before rewrite or significant replan (REQ-PLAN-002)
- [ ] Archive files use `{YYYY-MM-DD}-{reason}.md` naming (REQ-PLAN-002)
- [ ] Changelogs are written to archive only (REQ-PLAN-003)
- [ ] Active plan never contains a changelog section (REQ-PLAN-003)
- [ ] Removed tasks are moved to archive, not marked inline (REQ-PLAN-004)
- [ ] `sdd-plan` reads staleness from `requirements/index.md` (REQ-SKILL-005)
- [ ] `sdd-replan` writes changelogs and removed tasks to archive (REQ-SKILL-008)
