---
name: sdd-plan
description: >
  Reads approved design specs from docs/spec/ and creates a concrete
  implementation plan with ordered tasks, dependencies, and milestones.
  Use after specs are approved and before writing code.
---

# SDD: Implementation Planning

You are creating an implementation plan from approved design specs. Your input is `docs/spec/*.md` (status: Approved). Your output is an ordered, actionable plan.

## Your Role

- Break approved specs into implementable tasks
- Order tasks by dependencies (what must exist before what)
- Identify milestones where the system is testable end-to-end
- Flag risks and unknowns that could block implementation
- Do NOT start implementing — this skill produces a plan only

## Process

### Step 1: Read Approved Specs

1. Read all files in `docs/spec/` — only plan from specs with `status: Approved`
2. If any spec is still `Draft` or `Under Review`, tell the user and ask whether to proceed without it or wait
3. Read `docs/requirements.md` for context on priorities
4. Read `CLAUDE.md` for project conventions and technical constraints

### Step 2: Identify Implementation Units

Break each spec into implementation units. An implementation unit is:

- Small enough to implement and test in one session
- Large enough to be meaningful (not "add an import")
- Has clear inputs (what it depends on) and outputs (what it produces)
- Has a definition of done from the spec's acceptance criteria

### Step 3: Order by Dependencies

Build a dependency graph:

1. **Foundation first**: models, configuration, utilities
2. **Core interfaces next**: the contracts other code depends on
3. **Implementations**: concrete classes/functions that fulfill contracts
4. **Integration**: wiring components together
5. **Verification**: tests and manual checks

### Step 4: Define Milestones

Group tasks into milestones. Each milestone should produce a **testable system** — not just a pile of code. Good milestones:

- M1: Project skeleton — builds, lints, type-checks with zero functionality
- M2: Core models + first working feature end-to-end
- M3..N: Feature groups that build on each other
- Final: Full feature set, all acceptance criteria pass

### Step 5: Write the Plan

Present the plan to the user in this format:

```markdown
# Implementation Plan: [Project Name]

## Overview
One paragraph: what we're implementing and the approach.

## Milestones

### M1: [Name] — [one-line description]
**Goal**: What's testable after this milestone.
**Tasks**:
1. [Task description] — traces to [spec.md]
2. [Task description] — traces to [spec.md]
**Verification**: How to confirm this milestone is done.

### M2: [Name] — [one-line description]
**Depends on**: M1
**Goal**: ...
**Tasks**: ...
**Verification**: ...

## Risks
- [Risk]: [Impact and mitigation]

## Open Questions
- Questions that surfaced during planning
```

### Planning Rules

- **Every task traces to a spec**: if you can't point to which spec a task implements, it's unplanned work — flag it
- **No task should take more than ~2 hours**: if it feels bigger, break it down
- **Tests are tasks, not afterthoughts**: "write tests for X" is a task with its own place in the order, usually right after implementing X
- **Don't over-plan**: if the order between two independent tasks doesn't matter, say so — let the implementor parallelize
- **Flag unknowns**: if a task depends on something you're not sure about (an API behavior, a library capability), mark it as a risk

### Step 6: Review

Present the plan to the user. Ask:

- "Does the milestone ordering make sense?"
- "Are any tasks missing?"
- "Are the risk items right?"
- "Do you want to adjust scope for any milestone?"

Iterate until approved.

## Re-planning

When the plan needs updating mid-implementation:

1. Note which tasks are done, in-progress, or blocked
2. Identify what changed (new requirement, spec update, discovered blocker)
3. Adjust remaining tasks and milestones
4. Present the updated plan — don't silently change it
