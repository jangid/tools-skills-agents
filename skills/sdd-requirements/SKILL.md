---
name: sdd-requirements
description: >
  Guides requirements gathering for a new project or feature using Spec-Driven
  Development (SDD). Produces structured requirements in docs/requirements/
  (split by domain) through iterative Q&A with the user. Use at the start of
  any new project or when adding significant new functionality. Can reference
  prior research from docs/research/.
---

# SDD: Requirements Gathering

You are guiding the user through requirements gathering for a Spec-Driven Development workflow. Your output is a structured set of requirement files under `docs/requirements/`.

## Phase Detection

Requirements gathering is always valid — the user may be starting a new cycle or updating existing requirements. Before starting, check project state:

1. **Version check**: Read `docs/.sdd-version`. If missing, assume v1 — check for v1 vs v2 format below.
2. **Format detection**: Check which format exists:
   - If `docs/requirements/index.md` exists → v2 format, proceed normally
   - If `docs/requirements.md` exists (v1 monolithic format) → suggest running `sdd-migrate` to convert to v2 structure before proceeding. Do not attempt to read/write the v1 format
   - If neither exists → start fresh with v2 format
3. If `docs/requirements/index.md` exists with `status: Draft` → resume requirements gathering
4. If `docs/requirements/index.md` exists with `status: Approved` → inform the user. They can either:
   - Update the existing requirements (proceed here, downstream artifacts will become stale)
   - Move to the next phase (`sdd-specs` if specs are missing/stale, `sdd-plan` if specs are done)
5. If downstream artifacts exist (`docs/spec/`, `docs/plan.md`, `docs/verification.md`) → note them. If requirements are being rewritten or significantly updated, these will become stale and need updating in subsequent phases — that's the intended workflow
6. **Research staleness check**: Read `docs/research/index.md` if it exists. Find the newest research date (latest `Date` column entry with `status: Complete`). Compare against `docs/requirements/index.md`'s `last_updated`. If research is newer, inform the user: "Research RS-NNN completed on {date} — requirements may need updating to reflect new findings." This is advisory, not blocking.

Tell the user what artifacts exist and confirm how to proceed.

## Your Role

- Ask questions to clarify scope, constraints, and expected behavior
- Identify gaps and ambiguities in what the user describes
- Organize requirements into domain-specific files with unique IDs
- Reference research findings when available (by RS-NNN ID)
- Do NOT design solutions — requirements describe WHAT, not HOW

## Process

### Step 1: Understand Context

Before asking questions, understand what exists:

1. Read `docs/requirements/index.md` — check the Files table for existing category files and their status
2. Read existing category files under `docs/requirements/` — you may be adding to them, not starting fresh
3. Read `docs/research/index.md` and relevant `docs/research/RS-*/findings.md` — prior spikes inform what's feasible and what constraints exist
4. Read `CLAUDE.md` or `README` for project context
5. Ask the user: "What are we building and why?" if not already clear

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
2. Assign requirement IDs (using the domain-based scheme)
3. Flag any conflicts with existing requirements
4. Ask clarifying questions about ambiguities

### Step 4: Write Requirements

Write requirements to the appropriate category files based on domain. The directory structure is:

```
docs/requirements/
  index.md                      # Versioned index (auto-maintained)
  traceability.md               # RTM: requirement -> spec -> test -> status
  functional/
    {domain}.md                 # One file per feature domain
  non-functional/
    {concern}.md                # One file per quality concern
  integration/
    {system}.md                 # One file per external system
  configuration/
    {area}.md                   # One file per config area
```

#### Category File Format

Each category file follows this structure:

```markdown
---
domain: AUTH
last_updated: YYYY-MM-DD
status: Draft
---

# Requirements: Authentication

## Overview
Brief context for this domain — what it covers and why.

## Requirements

### REQ-AUTH-001: User login via OAuth2
The system must authenticate users through OAuth2 providers.
[Priority: must]

### REQ-AUTH-002: Session expiry
User sessions should expire after 30 minutes of inactivity.
[Priority: should]

### REQ-AUTH-003: Remember me option
The system may offer a "remember me" checkbox extending sessions to 30 days.
[Priority: may]
```

**Conventions**:
- `domain` in frontmatter is the uppercase prefix used in IDs for this file (2-8 chars)
- Each requirement is an h3 heading: `### REQ-{DOMAIN}-{NNN}: {title}`
- Priority (must/should/may) is stated in the requirement text
- One requirement per heading — no bundling multiple behaviors
- Requirements are testable statements — if you can't write a verification, rewrite

#### ID Assignment

Use `REQ-{DOMAIN}-{NNN}` format:
- `{DOMAIN}` is an uppercase short name matching the file's `domain` frontmatter
- `{NNN}` is a zero-padded 3-digit number, sequential within the domain
- Scan the target file for the highest existing NNN and increment
- New files start at 001
- IDs are globally unique — the domain prefix prevents collisions
- When creating a new category file, choose a domain prefix that doesn't collide with existing prefixes (check `index.md` Domain Prefixes table)
- Never reuse IDs, even for removed requirements

#### Index File Format

`docs/requirements/index.md` is auto-maintained:

```markdown
---
version: 1.0
status: Draft
last_updated: YYYY-MM-DD
---

# Requirements Index

## Summary
One paragraph: what the project is and what this requirements set covers.

## Stakeholders
Who provided requirements and their role/perspective.

## Files

| Category | File | Domain | Status | Count | Last Updated |
|----------|------|--------|--------|-------|--------------|
| Functional | functional/auth.md | AUTH | Approved | 12 | 2026-04-28 |

## Domain Prefixes

Reserved prefixes to prevent collisions:

| Prefix | File | Description |
|--------|------|-------------|
| AUTH | functional/auth.md | Authentication and authorization |

## Out of Scope
- Explicit list of what this project does NOT do

## Open Questions
- Unresolved items that need answers before specs can be written
- Items marked [needs-spike] that require research

## Glossary
Domain-specific terms used in these requirements.

## See Also
- [Traceability Matrix](traceability.md)
```

#### Traceability File Format

`docs/requirements/traceability.md` maps requirements through the lifecycle:

```markdown
---
last_updated: YYYY-MM-DD
---

# Traceability Matrix

| Requirement | Spec | Test | Implementation | Verified |
|-------------|------|------|----------------|----------|
| REQ-AUTH-001 | | | | |
| REQ-AUTH-002 | | | | |
```

When adding new requirements, add rows with the Spec/Test/Implementation/Verified columns blank. Other SDD skills fill those columns later:
- `sdd-specs` fills the Spec column
- `sdd-implement` fills Test and Implementation columns
- `sdd-verify` fills the Verified column

### Requirement Rules

- Every requirement gets a unique ID: `REQ-{DOMAIN}-{NNN}` where DOMAIN matches the file's frontmatter
- Requirements must be **testable** — if you can't write a verification for it, rewrite it
- Requirements describe behavior, not implementation ("the system must support multiple exchanges" not "use a factory pattern for exchanges")
- One requirement per ID — don't bundle multiple behaviors
- Use "must" for mandatory, "should" for preferred, "may" for optional
- Mark uncertain requirements with `[needs-spike]` — these may bounce back to `sdd-research`

### Step 5: Auto-Maintain Index and Traceability

After every write to a category file, perform these maintenance steps:

1. **Update category file frontmatter**: Bump `last_updated` to today
2. **Update index.md**:
   - Bump `version`: major bump for requirements added/removed/fundamentally changed; minor bump for clarifications, rewording, priority changes
   - Bump `last_updated` to today
   - Update the Files table row for the changed file (count, status, last_updated)
   - Add new rows to Files table and Domain Prefixes table if a new category file was created
3. **Update traceability.md**:
   - Add rows for new requirements (all columns except Requirement are blank)
   - For removed requirements: delete from category file, mark `[Deprecated]` in the traceability Requirement column. Never reuse the ID
   - Bump `last_updated` to today

### Step 6: File Size Monitoring

After writing to any category file, check its line count. If the file exceeds 300 lines:
- Inform the user: "{file} is at {N} lines — recommend splitting"
- Propose a split (e.g., `auth.md` -> `auth-login.md` + `auth-permissions.md`)
- If approved: create the new files, move requirements, assign new domain prefixes, update index.md

### Step 7: Review

Present the requirements to the user. Ask:
- "Are any requirements missing?"
- "Are any requirements wrong or unclear?"
- "Are the priorities right?" (must vs should vs may)
- "Are there open questions we need to resolve before proceeding to design?"
- "Do any [needs-spike] items need research before we proceed?"

Iterate until the user approves. Set `status: Approved` in both the category file frontmatter and `index.md` when approved.

If `[needs-spike]` items remain, recommend invoking `sdd-research` before proceeding to specs. The user may choose to proceed anyway and resolve them during implementation.

## Updating Existing Requirements

When category files already exist under `docs/requirements/`:

1. Read the current files via `index.md`'s Files table
2. Identify where new requirements fit in the existing structure
3. Use the next available ID number in each domain (don't reuse deleted IDs)
4. If a requirement changes, update in place and add a `[Updated: YYYY-MM-DD]` tag
5. If a requirement is removed: delete it from the category file and mark `[Deprecated]` in `traceability.md` — never reuse the ID
6. Present a diff summary to the user for approval
7. Run the auto-maintenance steps (Step 5) after every change

## Transition

When approved, recommend the next step:
- If `[needs-spike]` items remain unresolved → suggest `sdd-research`
- Otherwise → suggest `sdd-specs`
