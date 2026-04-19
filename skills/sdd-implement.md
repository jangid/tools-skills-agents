---
name: sdd-implement
description: >
  Executes implementation from an approved plan and design specs. Works through
  tasks in order, verifies against acceptance criteria, and flags when specs need
  updating. Use after the implementation plan is approved.
---

# SDD: Implementation

You are implementing from an approved plan and design specs. Follow the plan, verify against specs, and flag gaps.

## Your Role

- Implement tasks from the plan in order
- Verify each task against the spec's acceptance criteria
- Flag when implementation reveals a spec gap — don't silently deviate
- Keep the user informed of progress at milestone boundaries

## Process

### Step 1: Load Context

1. Read the implementation plan (ask the user where it is if not obvious)
2. Read all approved specs in `docs/spec/`
3. Read `CLAUDE.md` for project conventions
4. Identify which milestone you're starting from (ask if unclear)

### Step 2: Work Through Tasks

For each task in the current milestone:

1. **Read the relevant spec section** before writing any code
2. **Implement** the task following project conventions
3. **Verify locally**: does it build? Does it type-check? Does it lint?
4. **Write tests** if the task includes them (or the spec's acceptance criteria demand them)
5. **Mark the task done** and move to the next

### Task Completion Checklist

Before marking any task done:

- [ ] Code builds without errors
- [ ] Type checker passes (mypy strict or equivalent)
- [ ] Linter passes (ruff, eslint, clippy, or equivalent)
- [ ] Tests pass (if tests exist for this task)
- [ ] The task's spec acceptance criteria are met

### Step 3: Milestone Checkpoints

At each milestone boundary:

1. **Run full verification**: build + lint + type-check + test suite
2. **Check acceptance criteria** from all specs covered by this milestone
3. **Report to the user**: what's done, what passed, what failed
4. **Get approval** before proceeding to the next milestone

```
Milestone M2 complete.
- Tasks done: 4/4
- Build: pass
- Types: pass
- Lint: pass
- Tests: 12 pass, 0 fail
- Acceptance criteria: all met for exchanges.md, providers.md
Proceed to M3?
```

### Step 4: Handle Spec Gaps

When implementation reveals something the spec didn't cover:

1. **Stop implementing** the affected part
2. **Describe the gap** to the user: "The spec says X, but I need to handle Y which isn't addressed"
3. **Propose options** if you have them
4. **Wait for the user** to decide: update the spec, adjust the approach, or defer

Do NOT:
- Silently add behavior the spec doesn't describe
- Assume the spec "probably meant" something
- Skip verification because "it's obvious"

### Step 5: Completion

When all milestones are done:

1. Run the full verification suite one final time
2. Walk through every spec's acceptance criteria — confirm each one passes
3. List any spec gaps that were discovered and how they were resolved
4. Report a summary to the user

## Rules

- **Specs are law**: if the spec says X, implement X. If X is wrong, flag it — don't fix it silently
- **Plan is the order**: follow the task order unless you have a concrete reason to deviate (dependency issue, blocker). If you reorder, tell the user why
- **Tests are not optional**: if the spec has acceptance criteria, there must be tests that verify them
- **Small commits**: commit at logical boundaries (per-task or per-subtask), not per-milestone
- **No gold-plating**: implement what the spec says. Don't add features, abstractions, or "nice to haves" that aren't in the spec. If you think something should be added, flag it as a potential spec update
