---
name: sdd-plan
description: >
  Reads approved design specs from docs/spec/ and creates a concrete
  implementation plan with ordered tasks, dependencies, and milestones.
  Tasks are typed (implement, spike, verify). Plan includes replan triggers.
  Use after specs are approved and before writing code.
---

# SDD: Implementation Planning

You are creating an implementation plan from approved design specs. Your input is `docs/spec/*.md` (status: Approved). Your output is an ordered, actionable plan with typed tasks.

## Phase Detection

Before starting, check project state. **Compare `last_updated` dates** to detect stale downstream artifacts:

1. If no `docs/requirements.md` or status is `Draft` → use `sdd-requirements`
2. If `docs/spec/*.md` are missing or any has `status: Draft` → use `sdd-specs`
3. **Staleness check**: if `docs/plan.md` exists, compare its modification date against `last_updated` in each `docs/spec/*.md`. If any spec is newer than the plan, the plan is **stale** — it was written against older specs and needs updating. Proceed to rewrite/update the plan regardless of task completion status
4. If `docs/plan.md` exists with incomplete tasks **and is not stale** (per check 3) → use `sdd-implement`
5. If `docs/verification.md` exists with failures → use `sdd-replan`
6. If all specs are `Approved` and plan is missing or stale → you're in the right place

Tell the user which phase you detected, including any stale artifacts found, and confirm before proceeding.

## Your Role

- Break approved specs into implementable tasks
- Order tasks by dependencies (what must exist before what)
- Type each task: `implement`, `spike`, or `verify`
- Identify milestones where the system is testable end-to-end
- Define replan triggers — conditions that mean the plan is no longer valid
- Flag risks and unknowns that could block implementation
- Do NOT start implementing — this skill produces a plan only

## Process

### Step 1: Read Approved Specs

1. Read all files in `docs/spec/` — only plan from specs with `status: Approved`
2. If any spec is still `Draft` or `Under Review`, tell the user and ask whether to proceed without it or wait
3. Read `docs/requirements.md` for context on priorities
4. Read `docs/research/*.md` for context on what's been explored
5. Read `CLAUDE.md` for project conventions and technical constraints

### Step 2: Identify Implementation Units

Break each spec into implementation units. An implementation unit is:

- Small enough to implement and test in one session
- Large enough to be meaningful (not "add an import")
- Has clear inputs (what it depends on) and outputs (what it produces)
- Has a definition of done from the spec's acceptance criteria

### Step 3: Type Each Task

Every task gets one of three types:

- **`implement`** — produce working code + tests for a spec section
- **`spike`** — time-boxed research to resolve a `[high-uncertainty]` section from specs. Produces findings, may cause replan. Budget: state explicitly (e.g., "30 min max")
- **`verify`** — dedicated verification task (integration test, manual check, performance benchmark). Goes beyond "run pytest" — validates behavior from user perspective

### Step 4: Order by Dependencies

Build a dependency graph:

1. **Foundation first**: models, configuration, utilities
2. **Core interfaces next**: the contracts other code depends on
3. **Implementations**: concrete classes/functions that fulfill contracts
4. **Integration**: wiring components together
5. **Verification**: holistic checks

Place `spike` tasks early — their findings may invalidate later tasks.

### Step 5: Define Milestones

Group tasks into milestones. Each milestone should produce a **testable system** — not just a pile of code. Good milestones:

- M1: Project skeleton — builds, lints, type-checks with zero functionality
- M2: Core models + first working feature end-to-end
- M3..N: Feature groups that build on each other
- Final: Full feature set, all acceptance criteria pass

### Step 6: Define Replan Triggers

For each spike task and any high-risk implement task, define the condition that would invalidate the current plan:

```markdown
## Replan Triggers
- If spike "OAuth2 feasibility" finds the API doesn't support refresh tokens → redesign auth section
- If performance benchmark exceeds 500ms p99 → reconsider caching strategy
- If TA-Lib C library is unavailable on target → switch to pure-Python fallback approach
```

### Step 7: Write the Plan

Save the plan to `docs/plan.md`. Present to the user in this format:

```markdown
# Implementation Plan: [Project Name]

## Overview
One paragraph: what we're implementing and the approach.

## Conventions
- **Tests alongside implementation**: every milestone includes tests.
- **Task types**: [implement] produces code, [spike] produces findings, [verify] validates behavior.
- **Parallelization**: note which milestones/tasks can run in parallel.

## Milestones

### M1: [Name] — [one-line description]
**Goal**: What's testable after this milestone.
**Tasks**:
1. [implement] [Task description] — traces to [spec.md]
2. [spike] [Research question, budget: 30min] — traces to [spec.md §section]
3. [verify] [What to validate] — traces to [spec.md acceptance criteria]
**Verify**: How to confirm this milestone is done.

### M2: [Name] — [one-line description]
**Depends on**: M1
**Goal**: ...
**Tasks**: ...
**Verify**: ...

## Replan Triggers
- [Condition] → [what changes in the plan]

## Risks
- [Risk]: [Impact and mitigation]

## Open Questions
- Questions that surfaced during planning
```

### Planning Rules

- **Every task traces to a spec**: if you can't point to which spec a task implements, it's unplanned work — flag it
- **No task should take more than ~2 hours**: if it feels bigger, break it down
- **Tests are tasks, not afterthoughts**: "write tests for X" is a task with its own place in the order
- **Spikes go early**: place spike tasks before the implement tasks that depend on their findings
- **Don't over-plan**: if the order between two independent tasks doesn't matter, say so — let the implementor parallelize
- **Flag unknowns**: if a task depends on something you're not sure about, mark it as a risk
- **Verify tasks are explicit**: don't rely on "tests pass" — include specific verification tasks for complex features

### Step 8: Review

Present the plan to the user. Ask:

- "Does the milestone ordering make sense?"
- "Are any tasks missing?"
- "Are the replan triggers right?"
- "Do you want to adjust scope for any milestone?"

Iterate until approved.

## Re-planning

When invoked for an existing plan (e.g., after `sdd-replan` triggers):

1. Note which tasks are done, in-progress, or blocked
2. Identify what changed (spike findings, spec update, discovered blocker)
3. Adjust remaining tasks and milestones
4. Present the updated plan — don't silently change it

## Transition

When approved, recommend `sdd-implement` as the next step.
