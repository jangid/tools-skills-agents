---
name: sdd-specs
description: >
  Reads approved requirements from docs/requirements.md and produces feature
  design specs in docs/spec/. Each spec defines contracts, interfaces, and
  verification criteria — not implementation code. Use after requirements are
  approved and before implementation begins.
---

# SDD: Design Specs

You are writing design specs for a Spec-Driven Development workflow. Your input is an approved `docs/requirements.md`. Your output is feature specs in `docs/spec/`.

## Phase Detection

Before starting, check project state. **Compare `last_updated` dates** to detect stale downstream artifacts:

1. If no `docs/requirements.md` or status is `Draft` → use `sdd-requirements` first
2. **Staleness check**: compare `last_updated` in `docs/requirements.md` against `last_updated` in each `docs/spec/*.md` and `docs/plan.md` (if they exist). If requirements are newer than existing specs or plan, those downstream artifacts are **stale** — they were written against older requirements and need updating. Proceed to write/update specs regardless of their current status
3. If `docs/spec/*.md` all have `status: Approved` **and are not stale** (per check 2) → use `sdd-plan`
4. If `docs/plan.md` exists with incomplete tasks **and is not stale** (per check 2) → use `sdd-implement`
5. If `docs/verification.md` exists with failures → use `sdd-replan`
6. If `docs/requirements.md` has `status: Approved` and specs are missing, `Draft`, or stale → you're in the right place

Tell the user which phase you detected, including any stale artifacts found, and confirm before proceeding.

## Your Role

- Translate requirements into concrete design decisions
- Define contracts, interfaces, data shapes, and behavior
- Document rationale for design choices (why X not Y)
- Include verification criteria so reviewers can assess testability
- Mark sections with high uncertainty that may need spikes during implementation
- Do NOT write implementation code — specs define WHAT the system looks like, not the code

## Process

### Step 1: Read Requirements

1. Read `docs/requirements.md` — this is your source of truth
2. Read `docs/research/*.md` — prior research informs design decisions
3. Read `CLAUDE.md` or `README` for project context and technical constraints
4. Read any existing specs in `docs/spec/` — you may be adding or updating
5. Flag any requirements that are ambiguous or conflicting — ask the user before proceeding

### Step 2: Plan Spec Structure

Propose a list of spec files to the user. Each spec should cover a cohesive feature area. Example:

```
docs/spec/
  overview.md          # Architecture, principles, package structure
  feature-a.md         # One feature area
  feature-b.md         # Another feature area
  testing.md           # Testing strategy
```

Get approval on the structure before writing. The user may merge or split areas.

### Step 3: Write Specs

Start with `overview.md` — get it approved before writing other specs. The overview establishes architecture and principles that other specs depend on.

Each spec follows this format:

```markdown
---
status: Draft
last_updated: YYYY-MM-DD
requires: [REQ-F-001, REQ-F-002, REQ-NF-003]
---

# Feature Name

## Context
Why this feature exists and what problem it solves.
Reference the requirements it fulfills.

## Design

### [Sub-section as needed]
Contracts, interfaces, data shapes, behavior.
Decisions with rationale (why X not Y).

### [Sub-section] [high-uncertainty]
Mark sections where the design depends on unverified assumptions.
Note what spike would resolve it and what the fallback is.

Keep this section focused on:
- Public interfaces and their contracts
- Data models and their invariants
- Behavior under normal and error conditions
- Interaction with other features/specs

Do NOT include:
- Line-by-line implementation instructions
- File paths or directory structures (except in overview.md)
- Code snippets longer than 10 lines (use pseudocode for contracts)

## Verification

### Automated
- Key test scenarios with descriptive names
- Cover: happy path, edge cases, failure modes, boundary conditions

### Manual (if any)
- Steps to verify interactively (only when automated testing isn't sufficient)

### Acceptance Criteria
- [ ] Checkable conditions that define "done"
- [ ] Each must be independently verifiable
- [ ] Must include: type checking passes, linting clean
- [ ] Must trace to at least one requirement
```

### Spec Rules

- **Trace everything**: every spec must list which requirements it addresses in the `requires` frontmatter. If you're writing something no requirement covers, flag it to the user — don't invent requirements.
- **One cohesive area per spec**: a spec should be readable in isolation. Cross-references to other specs are fine but shouldn't be required to understand the core design.
- **Keep specs short**: ~500 lines max. If a spec is growing beyond that, split it.
- **Decisions need rationale**: every non-obvious design choice should have a "why" — a sentence or two explaining the tradeoff. Future readers need to know if the context has changed enough to revisit the decision.
- **Verification is design**: the verification section is reviewed alongside the design, not added as an afterthought. If you can't write verification criteria, the design isn't concrete enough.
- **Mark uncertainty**: sections marked `[high-uncertainty]` become spike tasks in the plan. They must include: what assumption is unverified, what spike would resolve it, and what the fallback design is if the assumption is wrong.

### Step 4: Review Cycle

Present each spec to the user for review. The lifecycle is:

```
Draft → Under Review → Approved
```

- **Draft**: you've written it, not yet presented
- **Under Review**: presented to user, awaiting feedback
- **Approved**: user has signed off, ready for implementation

When the user requests changes:
1. Update the spec in place
2. Update `last_updated`
3. Keep status as `Under Review` until the user approves

### Step 5: Coverage Check

After all specs are written, verify:

1. **Every requirement is covered** — each REQ-* ID appears in at least one spec's `requires` list
2. **No orphan specs** — every spec traces to at least one requirement
3. **No contradictions** — specs don't make conflicting design decisions
4. **Uncertainty inventory** — list all `[high-uncertainty]` sections and confirm the user is aware

Present a traceability summary:

```
REQ-F-001 → overview.md, exchanges.md
REQ-F-002 → exchanges.md
REQ-NF-001 → testing.md
...
[Uncovered]: REQ-F-015 (no spec addresses this yet)
[High-uncertainty]: exchanges.md §OAuth2 flow, testing.md §TA-Lib fallback
```

## Updating Existing Specs

When updating specs after code exists:

1. Read the current spec and the current code
2. Update the spec to reflect the proposed change
3. Bump `last_updated`, set status back to `Under Review`
4. In the design section, note what changed and why: `[Changed YYYY-MM-DD: switched from X to Y because Z]`
5. Update verification/acceptance criteria to cover the change
6. Present the diff to the user for approval

## Transition

When all specs are approved, recommend `sdd-plan` as the next step.
