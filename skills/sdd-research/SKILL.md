---
name: sdd-research
description: >
  Time-boxed exploration to reduce uncertainty before committing to requirements
  or design. Produces structured findings in docs/research/RS-NNN-{topic}/.
  Use when facing unfamiliar APIs, unknown libraries, architectural unknowns,
  or feasibility questions. Skip when the domain is well-understood.
---

# SDD: Research

You are conducting a time-boxed research spike to reduce uncertainty. Your output is structured findings — not code, not requirements, not design.

## Phase Detection

Research is always a valid entry point — new exploration doesn't require a clean slate. Before starting, check what exists so you can inform the user:

1. **Version check**: Read `docs/.sdd-version`. If missing, assume v1 — suggest running `sdd-migrate` to upgrade to v2 artifact structure before proceeding. If present and contains `2`, use v2 paths below.
2. If `docs/verification.md` exists with failures → mention it; user may want `sdd-replan` instead, but research is valid if they're exploring a new direction
3. If downstream artifacts exist (`docs/requirements/index.md`, `docs/spec/`, `docs/plan.md`) → note them. These may become stale after new research — that's expected. Downstream phases will detect staleness and update them
4. If existing `docs/research/RS-*` directories cover this topic → you may be extending prior research. Read their `findings.md` files first to avoid duplicating work. Check the `docs/research/index.md` table for a quick scan of existing spikes and their statuses
5. Proceed with research

Tell the user what artifacts exist and confirm the research direction before proceeding.

## Your Role

- Explore unknowns through reading docs, trying APIs, and prototyping
- Prove or disprove feasibility of approaches
- Produce findings that inform requirements and design decisions
- Stay within a time/scope budget — research expands to fill available time if unconstrained

## Process

### Step 1: Define the Research Question

Ask the user:
- "What are we trying to learn?" — the specific question(s) this spike should answer
- "What would success look like?" — how will we know when we have enough information
- "What's the budget?" — suggest a scope limit (e.g., "explore 3 approaches, max 1 hour")

If the user doesn't specify a budget, propose one based on the question complexity.

### Step 2: Assign Research ID

Before starting exploration, assign an ID for this spike:

1. Scan `docs/research/` for directories matching `RS-NNN-*`
2. Extract the highest `NNN` value from existing directories
3. Increment by 1 and zero-pad to 3 digits (e.g., `RS-002` if `RS-001` exists)
4. If no `RS-*` directories exist, start at `RS-001`
5. Choose a kebab-case topic slug (e.g., `oauth2-feasibility`, `plan-bloat-analysis`)

The new spike directory will be: `docs/research/RS-NNN-{topic}/`

**Edge case**: If a directory exists but its `findings.md` is missing or has `status: Abandoned`, the number is still consumed — IDs are never reused.

### Step 3: Explore

For each research question:

1. **Survey** — read docs, search for prior art, check existing libraries
2. **Prototype** (if needed) — minimal throwaway code in a scratch branch to prove feasibility
3. **Document as you go** — capture findings immediately, don't rely on memory

Exploration approaches by uncertainty type:
- **API unknown**: make real calls, inspect responses, document shapes
- **Library unknown**: read docs, try the happy path, check edge cases
- **Architecture unknown**: sketch 2-3 approaches, identify trade-offs
- **Feasibility unknown**: build the riskiest part first in isolation

### Step 4: Budget Enforcement

Track your progress against the budget. When you've consumed ~80% of the budget:
- Summarize what you've learned so far
- Ask the user: "extend budget, narrow scope, or stop here?"

Do NOT continue open-ended exploration past the budget.

### Step 5: Write Findings

Save to `docs/research/RS-NNN-{topic}/findings.md`:

```markdown
---
id: RS-NNN
status: Complete
date: YYYY-MM-DD
questions:
  - "The specific question we were answering"
budget: "What was allocated"
---

# Research: [Topic]

## Questions
What we set out to learn.

## Findings

### [Question 1]
**Answer**: [Clear, actionable answer]
**Evidence**: [What we observed/tested]
**Confidence**: [High/Medium/Low — and why]

### [Question 2]
...

## Implications for Design
- What this means for requirements/specs
- Approaches that are viable vs ruled out
- Constraints discovered

## Prototype (if any)
- Branch: `research/{topic}` (throwaway — do not merge)
- What it demonstrates
- What it doesn't prove

## Open Questions
- Things we still don't know (may need another spike)
```

The `id` field in frontmatter must match the directory prefix (e.g., `RS-001` for directory `RS-001-oauth2`). This allows validation and makes the ID visible when reading the file without inspecting the path.

Supporting files (prototype code, API response samples, screenshots) go in subdirectories within the spike directory:
- `docs/research/RS-NNN-{topic}/prototype/` — throwaway code
- `docs/research/RS-NNN-{topic}/responses/` — API response samples, screenshots
- `docs/research/RS-NNN-{topic}/notes.md` — raw notes, scratchpad

### Step 6: Update Research Index

After writing findings, update `docs/research/index.md`. If the index doesn't exist yet, create it.

**Index format**:

```markdown
---
last_updated: YYYY-MM-DD
---

# Research Index

| ID | Topic | Date | Status | Summary |
|----|-------|------|--------|---------|
| RS-001 | OAuth2 feasibility | 2026-03-15 | Complete | OAuth2 refresh tokens supported; proceed with auth design |
| RS-002 | Plan bloat analysis | 2026-04-27 | Complete | Three bloat sources identified; archive pattern proposed |
```

- Add a new row for a new spike, or update the existing row if revising a spike
- One row per research spike, sorted by ID (chronological by creation)
- Bump `last_updated` in frontmatter to today's date
- Summary should be a single sentence capturing the key finding or outcome

### Step 7: Recommend Next Step

Based on findings, recommend one of:
- **Proceed to requirements** — "We know enough to define what to build"
- **Another spike** — "Question X needs more exploration"
- **Pivot** — "This approach won't work because Y. Consider Z instead"
- **Stop** — "This isn't worth building because..."

## Cross-Referencing

Other artifacts reference research spikes by their RS-NNN ID:
- **Requirements**: `research_refs: [RS-001, RS-002]` in frontmatter, or inline `(see RS-001)` in prose
- **Specs**: `(see RS-001 §Findings)` in design rationale sections
- **Plan**: spike tasks reference `RS-NNN` when extending prior research

Always use the RS-NNN ID for cross-references, not file paths — IDs are stable even if directory structure changes.

## Rules

- **Budget is real**: don't exceed it. Partial findings are better than exhaustive ones delivered late
- **Findings over code**: prototypes are evidence, not deliverables. They live on throwaway branches
- **Concrete over abstract**: "the API returns X in Y format" beats "the API seems flexible"
- **Negative results are valuable**: "this won't work because X" saves weeks of implementation
- **One spike per uncertainty**: don't bundle unrelated questions into one research session
- **IDs are permanent**: never reuse an RS-NNN number, even if the spike was abandoned
