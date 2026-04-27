---
status: Approved
last_updated: 2026-04-28
requires:
  - REQ-REQ-001
  - REQ-REQ-002
  - REQ-REQ-003
  - REQ-REQ-004
  - REQ-REQ-005
  - REQ-REQ-006
  - REQ-REQ-007
  - REQ-STALE-001
  - REQ-STALE-002
  - REQ-SKILL-003
---

# Requirements Artifacts

## Context

In v1, all requirements live in a single `docs/requirements.md`. This file
grows unboundedly as projects evolve — requirements accumulate, removed ones
get `[Removed: ...]` markers, and the file consumes excessive AI context even
when only one domain is relevant.

v2 splits requirements by domain into category directories, adds a versioned
index for staleness detection, and introduces a separate traceability matrix.

## Design

### Directory Layout

```
docs/requirements/
  index.md                      # Versioned index (auto-maintained)
  traceability.md               # RTM: requirement → spec → test → status
  functional/
    {domain}.md                 # One file per feature domain
  non-functional/
    {concern}.md                # One file per quality concern
  integration/
    {system}.md                 # One file per external system
  configuration/
    {area}.md                   # One file per config area
```

**Why four subdirectories instead of flat**: The subdirectory names act as type
tags. When the `sdd-specs` skill needs to find performance constraints, it
knows to look in `non-functional/`. When `sdd-implement` needs API integration
details, it looks in `integration/`. This avoids scanning all files.

**Why not deeper nesting** (e.g., `functional/auth/login.md`): One level of
nesting is enough. If a domain file approaches 300 lines, split it into
sibling files (`auth-login.md`, `auth-permissions.md`), not deeper directories.
Flat within each category keeps paths short and predictable.

### Category File Format

Each category file follows this structure:

```markdown
---
domain: AUTH
last_updated: YYYY-MM-DD
status: Approved | Approved
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
- `domain` in frontmatter is the uppercase prefix used in IDs for this file.
- Each requirement is an h3 heading with format `### REQ-{DOMAIN}-{NNN}: {title}`.
- Priority (must/should/may) is stated in the requirement text, not the ID.
- One requirement per heading — no bundling multiple behaviors.
- Requirements are testable statements — if you can't write a verification, rewrite.

### Requirement ID Scheme

Format: `REQ-{DOMAIN}-{NNN}`

- `{DOMAIN}` is an uppercase short name (2-8 chars) matching the file's topic.
  Examples: `AUTH`, `PERF`, `STRIPE`, `ENVCFG`.
- `{NNN}` is a zero-padded 3-digit number, sequential within the domain.
- IDs must be globally unique — no two domains may produce the same full ID.
  The domain prefix naturally prevents collisions.

**Domain prefix selection**: When creating a new category file, the skill
chooses the domain prefix based on the topic and checks that it doesn't collide
with existing prefixes. The prefix must be listed in `index.md`.

**ID assignment**: The skill scans the target file for the highest existing
`NNN` and increments. New files start at `001`.

### Requirements Index

`docs/requirements/index.md` is the single source of truth for requirements
metadata and staleness detection:

```markdown
---
version: 1.0
status: Approved | Approved
last_updated: YYYY-MM-DD
---

# Requirements Index

## Summary
One paragraph: what the project is and what this requirements set covers.

## Files

| Category | File | Domain | Status | Count | Last Updated |
|----------|------|--------|--------|-------|--------------|
| Functional | functional/auth.md | AUTH | Approved | 12 | 2026-04-28 |
| Functional | functional/billing.md | BILL | Draft | 5 | 2026-04-28 |
| Non-functional | non-functional/performance.md | PERF | Approved | 3 | 2026-04-25 |
| Integration | integration/stripe-api.md | STRIPE | Approved | 8 | 2026-04-20 |

## Domain Prefixes

Reserved prefixes to prevent collisions:

| Prefix | File | Description |
|--------|------|-------------|
| AUTH | functional/auth.md | Authentication and authorization |
| BILL | functional/billing.md | Billing and payments |
| PERF | non-functional/performance.md | Performance constraints |
| STRIPE | integration/stripe-api.md | Stripe API integration |

## See Also
- [Traceability Matrix](traceability.md)
```

**Versioning rules**:
- `version` uses semver `major.minor`.
- Major bump: requirements added, removed, or fundamentally changed.
- Minor bump: clarifications, rewording, priority changes.
- The skill bumps the version and `last_updated` on every change.

**Why a Files table**: It gives any skill a quick scan of all requirement
files without traversing the directory tree. The Count column helps detect
files approaching the 300-line limit.

### Traceability Matrix

`docs/requirements/traceability.md` maps requirements through the full
lifecycle:

```markdown
---
last_updated: YYYY-MM-DD
---

# Traceability Matrix

| Requirement | Spec | Test | Implementation | Verified |
|-------------|------|------|----------------|----------|
| REQ-AUTH-001 | spec/auth-flow.md | tests/test_auth.py | src/auth.py | pass |
| REQ-AUTH-002 | spec/auth-flow.md | tests/test_session.py | src/session.py | pass |
| REQ-PERF-001 | spec/overview.md | tests/test_perf.py | — | fail |
| REQ-STRIPE-001 | spec/payments.md | — | — | — |
```

**Update responsibilities**:
- `sdd-specs` fills the Spec column when writing specs.
- `sdd-implement` fills Test and Implementation columns when writing code.
- `sdd-verify` fills the Verified column during verification.
- `sdd-requirements` creates the initial rows (Requirement column only, rest
  blank).

**Why a separate file instead of embedding in index.md**: The traceability
matrix grows with every requirement and gets updated by four different skills.
Keeping it separate prevents index.md churn and keeps concerns separated.

### Auto-Maintenance Behavior

When the `sdd-requirements` skill creates, updates, or removes requirements:

1. Write the change to the appropriate category file.
2. Update the category file's `last_updated` in frontmatter.
3. Update `index.md`: bump version, bump `last_updated`, update the Files
   table (count, status, date).
4. Update `traceability.md`: add rows for new requirements, mark removed
   requirements as `[Deprecated]`.

**Removed requirements**: In v2, removed requirements get `status: Deprecated`
in the traceability matrix and are removed from the category file. The ID is
never reused. This replaces v1's `[Removed: date — reason]` inline markers
that caused bloat.

**Why not just delete**: The traceability matrix preserves the record that the
requirement once existed and was deprecated. This is important when specs or
tests reference it — the reference becomes traceable to a deliberate removal
rather than a mysterious broken link.

### Staleness Detection

#### Index-based (REQ-STALE-001)

All downstream skills compare against `index.md`'s `last_updated`:
- If `index.md` is newer than `docs/spec/*.md` → specs are stale.
- If `index.md` is newer than `docs/plan.md` → plan is stale.

This replaces comparing against a single `requirements.md`.

#### Research-to-requirements (REQ-STALE-002)

When `sdd-requirements` starts, it checks:
1. Scan `docs/research/index.md` for entries with `status: Complete`.
2. Compare the newest research date against `requirements/index.md`'s
   `last_updated`.
3. If research is newer → inform the user: "Research RS-NNN completed on
   {date} — requirements may need updating."

This is advisory, not blocking. The user decides whether the new research
affects requirements.

### File Size Management

When a category file approaches 300 lines, the skill should:
1. Inform the user: "{file} is at {N} lines — recommend splitting."
2. Propose a split (e.g., `auth.md` → `auth-login.md` + `auth-permissions.md`).
3. If approved: create the new files, move requirements, assign new domain
   prefixes if needed, update `index.md`.

## Verification

### Automated
- Validate that `index.md` lists every category file that exists on disk
- Validate that every requirement ID matches its file's `domain` frontmatter
- Validate no duplicate requirement IDs across all files
- Validate no category file exceeds 300 lines
- Validate `traceability.md` has a row for every requirement ID

### Acceptance Criteria
- [ ] Requirements organized into `docs/requirements/` with subdirectories (REQ-REQ-001)
- [ ] `index.md` has version, status, last_updated, and file listing (REQ-REQ-002)
- [ ] Version bumps follow major/minor rules (REQ-REQ-002)
- [ ] IDs use `REQ-{DOMAIN}-{NNN}` format (REQ-REQ-003)
- [ ] Category files have domain, last_updated, status frontmatter (REQ-REQ-004)
- [ ] No category file exceeds 300 lines (REQ-REQ-005)
- [ ] Index is auto-maintained on every change (REQ-REQ-006)
- [ ] `traceability.md` maps requirements to specs/tests/status (REQ-REQ-007)
- [ ] Staleness compares against `index.md` last_updated (REQ-STALE-001)
- [ ] Research-to-requirements staleness is detected and reported (REQ-STALE-002)
- [ ] `sdd-requirements` reads/writes the new structure (REQ-SKILL-003)
- [ ] Old monolithic format is detected with migration offer (REQ-SKILL-003)
