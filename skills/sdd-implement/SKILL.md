---
name: sdd-implement
description: >
  Executes implementation from an approved plan and design specs. Works through
  tasks in order, uses TDD inner loop, detects stuck states, and executes spike
  tasks. Triggers replan when assumptions break. Use after the implementation
  plan is approved.
---

# SDD: Implementation

You are implementing from an approved plan and design specs. Follow the plan, use TDD, detect when you're stuck, and trigger replanning when needed.

## Phase Detection

Before starting, check project state. **Compare `last_updated` dates** to detect stale upstream artifacts:

0. **Version check**: If `docs/.sdd-version` is missing, suggest running `sdd-migrate` before proceeding
1. If no `docs/requirements/index.md` or status is `Draft` → use `sdd-requirements`
2. If `docs/spec/*.md` are missing or have `status: Draft` → use `sdd-specs`
3. If no `docs/plan.md` → use `sdd-plan`
4. **Staleness check**: compare `last_updated` in `docs/requirements/index.md` against `last_updated` in specs, and specs against `docs/plan.md` modification date. If the plan is older than its specs, or specs are older than requirements, upstream artifacts have changed since the plan was written → use `sdd-plan` to update the plan before implementing
5. If `docs/verification.md` exists with failures → use `sdd-replan`
6. If `docs/plan.md` exists with incomplete tasks **and is not stale** (per check 4) → you're in the right place, resume

Tell the user which phase you detected. If resuming, identify the next incomplete task and confirm before proceeding.

## Your Role

- Implement tasks from the plan in order
- Use TDD: write test → see it fail → implement → see it pass → refactor
- Execute spike tasks as time-boxed research
- Detect when you're stuck and trigger replanning
- Verify each task against the spec's acceptance criteria
- Keep the user informed of progress at milestone boundaries

## Process

### Step 1: Load Context

1. Read `docs/plan.md` — identify the current milestone and next task
2. Read the relevant spec sections for the current task
3. Read `docs/requirements/{category}/*.md` for requirement context when needed
4. Read `CLAUDE.md` for project conventions
5. Identify which milestone you're starting from (ask if unclear)

### Step 2: Work Through Tasks

For each task, follow the process based on its type:

#### [implement] tasks — TDD Inner Loop

1. **Read the relevant spec section** before writing any code
2. **Write a failing test** that captures what the spec requires
3. **Run the test** — confirm it fails (red)
4. **Write minimal code** to make the test pass
5. **Run the test** — confirm it passes (green)
6. **Refactor** if needed — tests must still pass
7. **Run full verification**: build + lint + type-check + tests
8. **Mark the task done**

#### [spike] tasks — Time-Boxed Research

1. **Note the budget** from the plan (e.g., "30 min max")
2. **Explore** the unknown: read docs, try APIs, prototype in a scratch branch
3. **Read prior research** from `docs/research/RS-*/findings.md` to avoid duplicating work
4. **Document findings** — write to `docs/research/RS-NNN-{topic}/findings.md` and update `docs/research/index.md`
5. **Check replan triggers** — did findings invalidate any plan assumptions?
6. If replan triggered → stop implementation, invoke `sdd-replan`
7. If no replan needed → mark done, proceed to next task

#### [verify] tasks — Beyond Unit Tests

1. **Read the acceptance criteria** from the spec
2. **Run the specified verification** (integration test, manual check, benchmark)
3. **Document results** — what passed, what failed
4. If failures → assess severity. Minor: fix inline. Major: trigger replan

### Task Completion Checklist

Before marking any task done:

- [ ] Code builds without errors
- [ ] Type checker passes (mypy strict or equivalent)
- [ ] Linter passes (ruff, eslint, clippy, or equivalent)
- [ ] Tests pass (including the new test written for this task)
- [ ] The task's spec acceptance criteria are met
- [ ] Update `docs/requirements/traceability.md`: fill **Test** column after writing tests, fill **Implementation** column after writing code

### Step 3: Stuck Detection

You are **stuck** if any of these are true:

- Same test has failed 3+ times with different attempted fixes
- You've spent more than 2x the expected effort on a single task
- You've discovered something that contradicts the spec or plan
- A dependency you expected to exist doesn't work as documented

When stuck:

1. **Stop** — don't keep trying the same approach
2. **Document** what you tried and why it failed
3. **Assess**: is this a spec gap, a plan ordering issue, or a research question?
4. **Recommend**: invoke `sdd-replan` with the stuck context

### Step 4: Milestone Checkpoints

At each milestone boundary:

1. **Run full verification**: build + lint + type-check + test suite
2. **Check acceptance criteria** from all specs covered by this milestone
3. **Report to the user**: what's done, what passed, what failed
4. **Get approval** before proceeding to the next milestone

```
Milestone M2 complete.
- Tasks done: 4/4 (3 implement, 1 spike)
- Build: pass
- Types: pass
- Lint: pass
- Tests: 12 pass, 0 fail
- Spike findings: OAuth2 works as expected, no replan needed
- Acceptance criteria: all met for exchanges.md, providers.md
Proceed to M3?
```

### Step 5: Handle Spec Gaps

When implementation reveals something the spec didn't cover:

1. **Stop implementing** the affected part
2. **Describe the gap** to the user: "The spec says X, but I need to handle Y which isn't addressed"
3. **Propose options** if you have them
4. **Wait for the user** to decide: update the spec, adjust the approach, or defer

Do NOT:
- Silently add behavior the spec doesn't describe
- Assume the spec "probably meant" something
- Skip verification because "it's obvious"

### Step 6: Completion

When all milestones are done:

1. Run the full verification suite one final time
2. Walk through every spec's acceptance criteria — confirm each one passes
3. List any spec gaps that were discovered and how they were resolved
4. Recommend invoking `sdd-verify` for holistic validation

## Rules

- **Specs are law**: if the spec says X, implement X. If X is wrong, flag it — don't fix it silently
- **Plan is the order**: follow the task order unless you have a concrete reason to deviate (dependency issue, blocker). If you reorder, tell the user why
- **TDD is not optional**: write the test first. If you catch yourself writing implementation before a test, stop and write the test
- **Tests are not optional**: if the spec has acceptance criteria, there must be tests that verify them
- **Small commits**: commit at logical boundaries (per-task or per-subtask), not per-milestone
- **No gold-plating**: implement what the spec says. Don't add features, abstractions, or "nice to haves" that aren't in the spec
- **Stuck means stop**: if you're stuck, replan. Don't burn cycles on a broken approach
- **Spike budget is real**: when a spike task exceeds its budget, stop and report findings so far

## Transition

When all tasks complete, recommend `sdd-verify` as the next step.
