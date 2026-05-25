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

0. **Version check**: If `docs/.sdd-version` is missing, suggest running `sdd-migrate` before proceeding
1. If no `docs/requirements/index.md` or status is `Draft` → use `sdd-requirements`
2. If `docs/spec/*.md` are missing or any has `status: Draft` → use `sdd-specs`
3. **Staleness check**: if `docs/plan.md` exists, check for upstream changes:
   - **Single-milestone plan**: compare `docs/plan.md`'s modification date against `last_updated` in each `docs/spec/*.md` and `docs/requirements/index.md`. If any upstream artifact is newer, the plan is **stale**
   - **Multi-milestone plan** (index + per-milestone files): apply milestone-scoped staleness — for each milestone plan file, compare its `last_updated` only against specs and requirement category files traced by that milestone's tasks (task → spec → `requires:` → requirement IDs → category file dates). A change to unrelated requirements does not make the milestone plan stale
   - Stale plans need updating. Proceed to rewrite/update regardless of task completion status
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
3. Read `docs/requirements/index.md` for overview and priorities, then read `docs/requirements/{category}/*.md` for detail (use `index.md` to discover files)
4. Read `docs/research/RS-*/findings.md` for context on what's been explored
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

### Step 5: Group into Chunks and Milestones

Group tasks into **chunks** — contiguous work units of ~5-15 hours each, marked by `### Chunk N: <name>` headers. Each chunk should have clear entry/exit criteria.

Decide whether to use per-milestone plan files:

- **Default: single-milestone.** Write all chunks directly to `docs/plan.md` with `### Chunk N:` headers. No `milestone:` frontmatter needed. Use this for projects with one delivery scope.

- **Per-milestone activation.** Use per-milestone files when:
  - The plan or specs explicitly define multiple delivery milestones (M1, M2, M3...), OR
  - The total chunk count exceeds ~10, or the plan would exceed ~300 lines, or work spans multiple distinct delivery scopes

When activating per-milestone structure:
1. Create `docs/plan.md` as the index (milestone table format — see Step 7)
2. Create `docs/plan-{milestone-id}.md` for each active milestone
3. Add `milestone:`, `last_updated:`, and `status: planned` frontmatter to each milestone plan

Each delivery milestone should produce a **testable system** — not just a pile of code. Good milestones:

- M1: Project skeleton — builds, lints, type-checks with zero functionality
- M2: Core models + first working feature end-to-end
- M3..N: Feature groups that build on each other
- Final: Full feature set, all acceptance criteria pass

**Milestone lifecycle** (per-milestone plans only):

Each milestone plan file's `status:` frontmatter transitions through:

1. **planned**: `sdd-plan` creates the file. Tasks defined but not started.
2. **active**: `sdd-implement` sets when work begins on the milestone's first task.
3. **complete**: `sdd-implement` (or `sdd-verify`) sets when all tasks are done and verified.
4. **archived**: The completed plan moves to `docs/plan-history/{date}-{milestone-id}-complete.md` and the index table is updated with the archive link.

### Step 6: Define Replan Triggers

For each spike task and any high-risk implement task, define the condition that would invalidate the current plan:

```markdown
## Replan Triggers
- If spike "OAuth2 feasibility" finds the API doesn't support refresh tokens → redesign auth section
- If performance benchmark exceeds 500ms p99 → reconsider caching strategy
- If TA-Lib C library is unavailable on target → switch to pure-Python fallback approach
```

### Step 7: Archive and Write the Plan

**Archival**: If `docs/plan.md` already exists, archive it before writing the new plan:

1. Create `docs/plan-history/` directory if it doesn't exist
2. Copy current `docs/plan.md` to `docs/plan-history/{date}-{reason}.md` (e.g., `2026-04-27-rewrite-after-spec-update.md`)
3. Then write the new plan

Save the plan to `docs/plan.md` (single-milestone) or create the index + per-milestone files (multi-milestone).

**Single-milestone plan format (default):**

```markdown
# Implementation Plan: [Project Name]

## Overview
One paragraph: what we're implementing and the approach.

## Conventions
- **Task types**: [implement] produces code, [spike] produces findings, [verify] validates behavior.
- **Chunk headers**: `### Chunk N: <name>` per work unit.

## Chunks

### Chunk 0: [Name]
**Goal**: What's testable after this chunk.
**Tasks**:
1. [implement] [Task description] — traces to [spec.md]
2. [spike] [Research question, budget: 30min] — traces to [spec.md §section]
3. [verify] [What to validate] — traces to [spec.md acceptance criteria]
**Entry criteria**: None (first chunk).
**Exit criteria**: [conditions].

### Chunk 1: [Name]
**Tasks**: ...
**Entry criteria**: Chunk 0 complete.
**Exit criteria**: ...

## Replan Triggers
- [Condition] → [what changes in the plan]

## Completed
- [chunk/milestone name]: [description] (YYYY-MM-DD, N tasks)

## Risks
- [Risk]: [Impact and mitigation]
```

**Multi-milestone index format** (`docs/plan.md` when per-milestone files exist):

```markdown
# Implementation Plan: [Project Name]

## Overview
One paragraph: project scope and approach.

## Milestones

| ID | Name | Plan File | Status |
|----|------|-----------|--------|
| M1 | [name] | [archived](plan-history/2026-04-20-m1-complete.md) | Complete |
| M2 | [name] | plan-m2.md | Active |
| M3 | [name] | plan-m3.md | Planned |
```

Each `docs/plan-{id}.md` follows the single-milestone format above (with `### Chunk N:` headers) plus `milestone:`, `last_updated:`, and `status:` frontmatter.

**Active plan format rules**:
- Only include current and future chunks in the active plan
- Completed chunks/milestones are summarized as one line each in the `## Completed` section
- Do NOT include a `## Plan Changelog` section in the active plan — changelog entries belong in archive files

### Planning Rules

- **Every task traces to a spec**: if you can't point to which spec a task implements, it's unplanned work — flag it
- **No task should take more than ~2 hours**: if it feels bigger, break it down
- **Tests are tasks, not afterthoughts**: "write tests for X" is a task with its own place in the order
- **Spikes go early**: place spike tasks before the implement tasks that depend on their findings
- **Don't over-plan**: if the order between two independent tasks doesn't matter, say so — let the implementor parallelize
- **Flag unknowns**: if a task depends on something you're not sure about, mark it as a risk
- **Verify tasks are explicit**: don't rely on "tests pass" — include specific verification tasks for complex features
- **Chunks not milestones for work units**: use `### Chunk N: <name>` headers for implementation work units (~5-15 hours each). Reserve "milestone" for delivery groupings (M1, M2, etc.) in multi-milestone projects

### Step 8: Review

Present the plan to the user. Ask:

- "Does the chunk ordering make sense?"
- "Are any tasks missing?"
- "Are the replan triggers right?"
- "Do you want to adjust scope for any chunk or milestone?"

Iterate until approved.

## Re-planning

When invoked for an existing plan (e.g., after `sdd-replan` triggers):

1. Note which tasks are done, in-progress, or blocked
2. Identify what changed (spike findings, spec update, discovered blocker)
3. Adjust remaining tasks, chunks, and milestones
4. Present the updated plan — don't silently change it

## Transition

When approved, recommend `sdd-implement` as the next step.
