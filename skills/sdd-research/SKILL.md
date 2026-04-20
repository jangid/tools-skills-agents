---
name: sdd-research
description: >
  Time-boxed exploration to reduce uncertainty before committing to requirements
  or design. Produces structured findings in docs/research/. Use when facing
  unfamiliar APIs, unknown libraries, architectural unknowns, or feasibility
  questions. Skip when the domain is well-understood.
---

# SDD: Research

You are conducting a time-boxed research spike to reduce uncertainty. Your output is structured findings — not code, not requirements, not design.

## Phase Detection

Research is always a valid entry point — new exploration doesn't require a clean slate. Before starting, check what exists so you can inform the user:

1. If `docs/verification.md` exists with failures → mention it; user may want `sdd-replan` instead, but research is valid if they're exploring a new direction
2. If downstream artifacts exist (`docs/requirements.md`, `docs/spec/`, `docs/plan.md`) → note them. These may become stale after new research — that's expected. Downstream phases will detect staleness and update them
3. If `docs/research/*.md` already cover this topic → you may be extending prior research. Read existing findings first to avoid duplicating work
4. Proceed with research

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

### Step 2: Explore

For each research question:

1. **Survey** — read docs, search for prior art, check existing libraries
2. **Prototype** (if needed) — minimal throwaway code in a scratch branch to prove feasibility
3. **Document as you go** — capture findings immediately, don't rely on memory

Exploration approaches by uncertainty type:
- **API unknown**: make real calls, inspect responses, document shapes
- **Library unknown**: read docs, try the happy path, check edge cases
- **Architecture unknown**: sketch 2-3 approaches, identify trade-offs
- **Feasibility unknown**: build the riskiest part first in isolation

### Step 3: Budget Enforcement

Track your progress against the budget. When you've consumed ~80% of the budget:
- Summarize what you've learned so far
- Ask the user: "extend budget, narrow scope, or stop here?"

Do NOT continue open-ended exploration past the budget.

### Step 4: Write Findings

Save to `docs/research/{topic}.md`:

```markdown
---
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

### Step 5: Recommend Next Step

Based on findings, recommend one of:
- **Proceed to requirements** — "We know enough to define what to build"
- **Another spike** — "Question X needs more exploration"
- **Pivot** — "This approach won't work because Y. Consider Z instead"
- **Stop** — "This isn't worth building because..."

## Rules

- **Budget is real**: don't exceed it. Partial findings are better than exhaustive ones delivered late
- **Findings over code**: prototypes are evidence, not deliverables. They live on throwaway branches
- **Concrete over abstract**: "the API returns X in Y format" beats "the API seems flexible"
- **Negative results are valuable**: "this won't work because X" saves weeks of implementation
- **One spike per uncertainty**: don't bundle unrelated questions into one research session
