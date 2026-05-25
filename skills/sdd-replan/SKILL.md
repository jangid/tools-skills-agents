---
name: sdd-replan
description: >
  Structured replanning when assumptions break during implementation. Triggered
  by stuck detection, spike findings that invalidate the plan, verification
  failures, or user-requested scope changes. Reads current state, identifies
  what changed, and produces a revised plan. Use when the current plan is no
  longer valid.
---

# SDD: Replan

You are adjusting an existing implementation plan because something changed. The current plan is no longer valid — your job is to understand why, decide what to adjust, and produce a revised plan.

## Phase Detection

Before starting, check what triggered the replan:

0. **Version check**: If `docs/.sdd-version` is missing, suggest running `sdd-migrate` before proceeding
1. If `docs/verification.md` exists with `status: fail` → replan from verification failures
2. If a spike task produced findings that contradict the plan → replan from new knowledge
3. If the user explicitly requested changes → replan from scope change
4. If implementation is stuck (documented in conversation) → replan from blocked state
5. **Staleness check**: if upstream artifacts are newer than the plan, the plan is stale → replan to align:
   - **Single-milestone plan**: compare `docs/requirements/index.md` and specs against `docs/plan.md`
   - **Multi-milestone plan**: apply milestone-scoped staleness — compare only against requirements and specs traced by the affected milestone's tasks

Tell the user what triggered the replan and confirm before proceeding.

## Your Role

- Understand what changed and why the current plan is invalid
- Assess impact: is this a minor task reordering or a fundamental redesign?
- Produce a revised plan that accounts for the new information
- Route to the appropriate phase if the issue is deeper than task ordering

## Process

### Step 1: Assess the Situation

Read the current state:

1. `docs/plan.md` — which tasks are done, in-progress, blocked?
2. `docs/verification.md` (if exists) — what failed?
3. `docs/research/RS-*/findings.md` — any new findings that changed assumptions?
4. `docs/spec/*.md` — are specs still valid given new information?
5. `docs/requirements/{category}/*.md` — current requirements for context
6. Recent conversation context — what was the stuck state or trigger?

### Step 2: Classify the Issue

Determine the depth of the problem:

**Level 1: Task adjustment** — plan ordering or task breakdown is wrong, but specs are fine
- Example: "Task 5 depends on something from Task 8, need to reorder"
- Action: revise `docs/plan.md`

**Level 2: Spec gap** — the design doesn't cover something we discovered during implementation
- Example: "The spec assumes the API returns JSON but it returns XML"
- Action: update the affected spec, then revise the plan

**Level 3: Requirements change** — what we're building needs to change
- Example: "Verification showed the approach won't meet performance requirements"
- Action: update requirements, then cascade through specs and plan

**Level 4: Pivot needed** — fundamental assumptions are wrong, need research
- Example: "The library we planned to use doesn't support our use case at all"
- Action: invoke `sdd-research` for a spike, then cascade

### Step 3: Route Based on Level

- **Level 1** → revise plan directly (Step 4 below)
- **Level 2** → tell user "this needs a spec update" and either:
  - Make the spec change inline (if small and obvious)
  - Recommend invoking `sdd-specs` for the affected spec
  - Then revise the plan
- **Level 3** → recommend invoking `sdd-requirements` to capture the change, then cascade
- **Level 4** → recommend invoking `sdd-research` for the unknown, then cascade

### Step 4: Revise the Plan (Level 1 and 2)

First, determine if this is a **significant** or **minor** replan:

- **Significant** = adds/removes milestones or changes the overall approach
- **Minor** = task reordering within a milestone, small task edits

**For significant replans**: archive the current plan before modifying it:

1. Create `docs/plan-history/` directory if it doesn't exist
2. Copy `docs/plan.md` to `docs/plan-history/{date}-replan-{reason}.md`
3. Write the changelog and removed tasks to the **archive file**, not the active plan

**For minor replans**: edit `docs/plan.md` in place. No archive needed.

When revising `docs/plan.md`:

1. **Preserve done tasks** — never undo completed work unless explicitly reverting
2. **Mark blocked tasks** — note why they're blocked and what unblocks them
3. **Add new tasks** if the replan introduces new work
4. **Remove invalidated tasks** — move them to the archive file (for significant replans). Do NOT write `[removed: reason]` in the active plan
5. **Reorder** remaining tasks based on new dependencies
6. **Update replan triggers** — the old ones may no longer apply

**Archive file format** (for significant replans — written to `docs/plan-history/{date}-replan-{reason}.md`):

```markdown
# Plan Archive: Replan — [reason]

## Changelog
- **Date**: YYYY-MM-DD
- **Trigger**: [what caused the replan]
- **Impact**: [what changed]
- **Added**: [new tasks]
- **Removed**: [invalidated tasks and why]
- **Reordered**: [what moved and why]

## Previous Plan Snapshot
[Full content of plan.md at time of archive]
```

#### Per-Milestone Replans

When the project uses per-milestone plan files (`docs/plan-{id}.md`):

**Single-milestone replan** (most common):
1. Identify which milestone's plan file is affected by the replan trigger
2. Archive only that milestone's plan file to `docs/plan-history/{date}-m{N}-replan-{reason}.md`
3. Revise the affected milestone plan
4. Update `docs/plan.md` index table if milestone status changes

**Cross-milestone replan** (tasks moving between milestones):
1. Archive both affected milestone plans before changes
2. Update both milestone plan files with the task movement
3. Update the index table to reflect current status

Single-file plans continue to use the existing archival pattern above. Per-milestone logic activates only when per-milestone files exist.

### Step 5: Present and Confirm

Present the revised plan to the user:

1. Summarize what triggered the replan
2. Show what changed (added/removed/reordered tasks)
3. Highlight any cascading impacts (spec changes, new risks)
4. Ask for approval before resuming implementation

### Step 6: Transition

After the revised plan is approved:
- If implementation should resume → recommend `sdd-implement`
- If a spec needs updating first → recommend `sdd-specs`
- If research is needed → recommend `sdd-research`
- If re-verification is needed → recommend `sdd-verify`

## Rules

- **Don't panic**: a replan is normal, not a failure. The goal is to adjust efficiently, not to blame or justify
- **Minimize disruption**: change only what's necessary. If 3 tasks out of 20 need adjustment, don't rewrite the whole plan
- **Preserve history**: never silently delete tasks or change what's already done. Use the archive file for significant changes
- **Cascade awareness**: a spec change may invalidate multiple tasks. Check downstream effects
- **User decides scope**: if the replan could go multiple directions (cut scope vs extend timeline vs change approach), present options and let the user choose
- **Don't implement during replan**: produce the revised plan, not code. Implementation happens in `sdd-implement`
