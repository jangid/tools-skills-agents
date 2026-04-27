---
status: Approved
last_updated: 2026-04-28
requires:
  - REQ-CTX-001
  - REQ-CTX-002
  - REQ-COMPAT-001
  - REQ-CFG-001
---

# Overview: SDD Artifact Structure v2

## Context

The SDD workflow produces artifacts across seven phases. In v1, these artifacts
live in flat structures that grow unboundedly: a single `requirements.md`, flat
research files, and plan files that accumulate changelogs and removed-task
markers. v2 restructures all artifacts for bounded file sizes, traceable
cross-references, and AI-context-friendly document sizes.

This spec establishes the shared principles and directory layout that all other
specs build on.

## Design

### Directory Layout

```
docs/
  .sdd-version                    # Plain text: "2"
  research/
    index.md                      # Auto-maintained research index
    RS-001-{topic}/
      findings.md                 # Main research document
      prototype/                  # Optional supporting files
    RS-002-{topic}/
      findings.md
  requirements/
    index.md                      # Versioned requirements index
    traceability.md               # RTM: requirements → specs → tests → status
    functional/
      {domain}.md                 # e.g., auth.md, billing.md
    non-functional/
      {concern}.md                # e.g., performance.md, security.md
    integration/
      {system}.md                 # e.g., stripe-api.md
    configuration/
      {area}.md                   # e.g., env-config.md
  spec/
    overview.md                   # This file (unchanged from v1)
    {feature}.md                  # Feature specs (unchanged from v1)
  plan.md                         # Active plan — lean, no history
  plan-history/
    {YYYY-MM-DD}-{reason}.md      # Archived plans with changelogs
  verification.md                 # Verification report (unchanged from v1)
```

### Version Marker

`docs/.sdd-version` is a plain text file containing a single integer (e.g.,
`2`). All SDD skills read this file on phase detection to determine which
artifact layout to expect.

- If the file is missing, assume v1 (backward compatible).
- If the file contains `2`, use v2 paths and conventions.
- Future versions increment this number and add migration logic to `sdd-migrate`.

**Why a separate file instead of frontmatter in an existing artifact**: The
version marker must be detectable before reading any specific artifact. A
standalone file avoids chicken-and-egg problems (which file do you read to find
the version?).

### Shared Conventions

#### File Size Budget

No single artifact file should exceed 300 lines. This ensures any file can be
loaded into an AI session alongside specs and code without consuming excessive
context. Exceptions:
- Index files and `traceability.md` are exempt but should be kept concise.
- `docs/plan.md` is naturally bounded by the archive pattern (completed
  milestones are summarized, not preserved in full).

**Why 300 lines**: Research found that LLMs produce better output with focused,
detailed documents rather than large dumps. 300 lines is ~10KB of markdown —
comfortably fits within a single context window alongside implementation code.

#### Self-Contained Files

Each artifact file must be understandable in isolation. Cross-references use
explicit IDs (`REQ-AUTH-001`, `RS-003`) rather than prose like "see the auth
section in requirements." This allows skills to load only the files relevant to
the current task.

#### Format

All artifacts are plain Markdown with YAML frontmatter. No binary files, no
tool-specific formats. This ensures:
- Git diffs are human-readable
- Any text editor can open them
- AI assistants can read/write them without special tooling

#### Frontmatter Fields

Every artifact file must include at minimum:
- `status` — lifecycle state (Draft, Approved, Complete, etc.)
- `last_updated` — ISO date (YYYY-MM-DD), used for staleness detection

Additional fields are spec-specific (e.g., `version` in requirements index,
`requires` in spec files).

### Staleness Detection Model

v2 changes staleness detection from comparing individual files to comparing
against index files:

```
research/index.md → requirements/index.md → spec/*.md → plan.md → verification.md
         (last_updated)    (last_updated)
```

The key change: `requirements/index.md`'s `last_updated` is bumped whenever any
category file changes. Downstream skills compare against this single date rather
than scanning all category files.

**Why index-based**: In v1, staleness compares one file against one file. With
split requirements, comparing against N files adds complexity. The index acts as
a single source of truth for "when did requirements last change?"

### ID Namespaces

v2 uses three ID namespaces:

| Namespace | Format | Example | Scope |
|-----------|--------|---------|-------|
| Research | `RS-NNN` | `RS-001` | Global across project |
| Requirements | `REQ-{DOMAIN}-{NNN}` | `REQ-AUTH-001` | Unique per domain, globally unique |
| Specs | filename-based | `auth-flow.md` | `docs/spec/` directory |

**Why domain-based requirement IDs instead of type-based**: `REQ-AUTH-001` tells
you both what it's about and where to find it (`functional/auth.md` or similar).
`REQ-F-001` tells you only the type, requiring a search to locate it.

## Verification

### Manual
- Inspect the directory layout after migration or fresh project setup
- Confirm `docs/.sdd-version` contains `2`
- Confirm each artifact file has the required frontmatter fields

### Acceptance Criteria
- [ ] All artifact files use plain Markdown with YAML frontmatter (REQ-COMPAT-001)
- [ ] No artifact file exceeds 300 lines except index/traceability (REQ-CTX-001)
- [ ] Each file is self-contained with ID-based cross-references (REQ-CTX-002)
- [ ] `docs/.sdd-version` exists and contains the version number (REQ-CFG-001)
- [ ] Staleness detection uses `index.md` dates, not individual file scans
