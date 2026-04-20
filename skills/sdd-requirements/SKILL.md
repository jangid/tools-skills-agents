---
name: sdd-requirements
description: >
  Guides requirements gathering for a new project or feature using Spec-Driven
  Development (SDD). Produces a structured docs/requirements.md through iterative
  Q&A with the user. Use at the start of any new project or when adding significant
  new functionality. Can reference prior research from docs/research/.
---

# SDD: Requirements Gathering

You are guiding the user through requirements gathering for a Spec-Driven Development workflow. Your output is a structured `docs/requirements.md` in the project directory.

## Phase Detection

Requirements gathering is always valid — the user may be starting a new cycle or updating existing requirements. Before starting, check project state:

1. If `docs/requirements.md` exists with `status: Draft` → resume requirements gathering
2. If `docs/requirements.md` exists with `status: Approved` → inform the user. They can either:
   - Update the existing requirements (proceed here, downstream artifacts will become stale)
   - Move to the next phase (`sdd-specs` if specs are missing/stale, `sdd-plan` if specs are done)
3. If downstream artifacts exist (`docs/spec/`, `docs/plan.md`, `docs/verification.md`) → note them. If requirements are being rewritten or significantly updated, these will become stale and need updating in subsequent phases — that's the intended workflow
4. Otherwise → start fresh

Tell the user what artifacts exist and confirm how to proceed.

## Your Role

- Ask questions to clarify scope, constraints, and expected behavior
- Identify gaps and ambiguities in what the user describes
- Organize requirements into a structured document with unique IDs
- Reference research findings when available
- Do NOT design solutions — requirements describe WHAT, not HOW

## Process

### Step 1: Understand Context

Before asking questions, understand what exists:

1. Read any existing `docs/requirements.md` — you may be adding to it, not starting fresh
2. Read `docs/research/*.md` — prior spikes inform what's feasible and what constraints exist
3. Read `CLAUDE.md` or `README` for project context
4. Ask the user: "What are we building and why?" if not already clear

### Step 2: Elicit Requirements

Ask questions in these categories (skip what's already clear):

- **Functional**: What must the system do? What are the inputs/outputs?
- **Non-functional**: Performance, security, reliability, scalability constraints?
- **Integration**: What does this connect to? What protocols/APIs?
- **Configuration**: What must be configurable? What are sensible defaults?
- **Scope boundaries**: What is explicitly out of scope?

Don't ask all questions at once. Go category by category. Listen for implicit requirements in the user's answers — things they assume but don't state.

When a requirement depends on an unresolved uncertainty, mark it with `[needs-spike]` and note what research is needed.

### Step 3: Capture External Input

The user may bring in requirements from other parties (stakeholders, docs, tickets). When they paste or describe external requirements:

1. Restate them in your own words to confirm understanding
2. Assign requirement IDs
3. Flag any conflicts with existing requirements
4. Ask clarifying questions about ambiguities

### Step 4: Write Requirements Document

When the user is satisfied with the Q&A, produce `docs/requirements.md`:

```markdown
---
status: Draft
last_updated: YYYY-MM-DD
research_refs:
  - docs/research/topic.md
---

# Requirements: [Project Name]

## Overview
One paragraph: what the project is and why it exists.

## Stakeholders
Who provided requirements and their role/perspective.

## Functional Requirements

### [Category Name]

#### REQ-F-001: [Short title]
[Clear, testable statement of what the system must do.]

#### REQ-F-002: [Short title] [needs-spike]
[Statement with uncertainty noted. Spike needed to resolve X.]

## Non-Functional Requirements

#### REQ-NF-001: [Short title]
[Clear, measurable constraint.]

## Integration Requirements

#### REQ-I-001: [Short title]
[What the system connects to and how.]

## Configuration Requirements

#### REQ-C-001: [Short title]
[What must be configurable.]

## Out of Scope
- Explicit list of what this project does NOT do

## Open Questions
- Unresolved items that need answers before specs can be written
- Items marked [needs-spike] that require research

## Glossary
Domain-specific terms used in this document.
```

### Requirement Rules

- Every requirement gets a unique ID: `REQ-{type}-{number}` where type is F (functional), NF (non-functional), I (integration), C (configuration)
- Requirements must be **testable** — if you can't write a verification for it, rewrite it
- Requirements describe behavior, not implementation ("the system must support multiple exchanges" not "use a factory pattern for exchanges")
- One requirement per ID — don't bundle multiple behaviors
- Use "must" for mandatory, "should" for preferred, "may" for optional
- Mark uncertain requirements with `[needs-spike]` — these may bounce back to `sdd-research`

### Step 5: Review

Present the document to the user. Ask:
- "Are any requirements missing?"
- "Are any requirements wrong or unclear?"
- "Are the priorities right?" (must vs should vs may)
- "Are there open questions we need to resolve before proceeding to design?"
- "Do any [needs-spike] items need research before we proceed?"

Iterate until the user approves. Set `status: Approved` when approved.

If `[needs-spike]` items remain, recommend invoking `sdd-research` before proceeding to specs. The user may choose to proceed anyway and resolve them during implementation.

## Updating Existing Requirements

When `docs/requirements.md` already exists:

1. Read the current document fully
2. Identify where new requirements fit in the existing structure
3. Use the next available ID number in each category (don't reuse deleted IDs)
4. If a requirement changes, update in place and add a `[Updated: YYYY-MM-DD]` tag
5. If a requirement is removed, mark it `[Removed: YYYY-MM-DD — reason]` — don't delete the ID
6. Present a diff summary to the user for approval

## Transition

When approved, recommend the next step:
- If `[needs-spike]` items remain unresolved → suggest `sdd-research`
- Otherwise → suggest `sdd-specs`
