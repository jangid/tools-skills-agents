---
status: Draft
last_updated: 2026-05-25
requires:
  - REQ-CTX-001
  - REQ-CTX-002
  - REQ-COMPAT-001
  - REQ-COMPAT-002
  - REQ-CFG-001
  - REQ-MIG-015
  - REQ-STALE-001
---

# Overview: SDD Artifact Structure

## Context

The SDD workflow produces artifacts across seven phases. In v1, these artifacts
live in flat structures that grow unboundedly: a single `requirements.md`, flat
research files, and plan files that accumulate changelogs and removed-task
markers. v2 restructures all artifacts for bounded file sizes, traceable
cross-references, and AI-context-friendly document sizes. v3 adds behavioral
conventions — chunk-close review, Q-IMPL deviation protocol, per-milestone plan
support, and cross-spec consistency — without changing the artifact layout.

This spec establishes the shared principles, directory layout, and version
conventions that all other specs build on.

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

`docs/.sdd-version` is a plain text file containing a single integer
indicating the SDD process version. Current valid values:

- `2` — v2 artifact layout (split requirements, RS-NNN research, archive
  pattern, traceability matrix)
- `3` — v2 layout plus v3 process conventions (chunk-close review, Q-IMPL
  deviation protocol, per-milestone plan support, cross-spec consistency
  pass, plan vocabulary using `### Chunk N:` headers for work units)

If the file is missing, assume v1 (backward compatible). All SDD skills read
this file on phase detection to determine which conventions apply.

The marker tracks SDD process version — not just artifact layout — because v3
introduces behavioral conventions (not layout changes) that operators need to
know about. Skills read this file to determine which mechanisms are active.

v3 is backward compatible with v2: projects on v2 continue to work without
migration. v3 mechanisms gracefully degrade when v3 conventions aren't present
(chunk-close is inactive without `### Chunk N:` headers; per-milestone logic
activates only when per-milestone files exist; Q-IMPL entries accumulate on
demand).

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

### Plan Vocabulary

v3 distinguishes **chunks** (implementation work units, ~5-15 hours) from
**delivery milestones** (M1, M2, etc., delivery groupings). Single-milestone
plans use `### Chunk N:` headers under a `## Chunks` section. Multi-milestone
projects use per-milestone plan files (see milestone-plans.md) where each
per-milestone file contains chunks.

v2 plans using `### M N:` as work-unit headers are still readable but won't
activate chunk-close review (which triggers on `### Chunk N:` boundaries). The
v2→v3 migration renames these to chunk format, preserving original numbering
(M1 → Chunk 1, M2 → Chunk 2).

### v3 Behavioral Additions

Beyond the v2 artifact layout, v3 adds:

- **Chunk-close review** — structured 4-check checklist at chunk boundaries
  during implementation (see chunk-close-review.md)
- **Q-IMPL deviation protocol** — three-tier classification for implementation
  decisions diverging from spec (see deviation-protocol.md)
- **Per-milestone plan support** — optional structure for multi-milestone
  projects (see milestone-plans.md)
- **Cross-spec consistency pass** — type reference validation between specs
  (see cross-spec-consistency.md)

These are documented in their own specs. The overview lists them as the answer
to "what does v3 add" without restating their designs.

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
- Confirm `docs/.sdd-version` contains the current version (`2` or `3`)
- Confirm each artifact file has the required frontmatter fields
- Confirm v3 projects use `### Chunk N:` plan vocabulary

### Acceptance Criteria
- [ ] All artifact files use plain Markdown with YAML frontmatter (REQ-COMPAT-001)
- [ ] No artifact file exceeds 300 lines except index/traceability (REQ-CTX-001)
- [ ] Each file is self-contained with ID-based cross-references (REQ-CTX-002)
- [ ] `docs/.sdd-version` exists and contains the version number (REQ-CFG-001)
- [ ] Version marker valid values are `2` and `3` (REQ-CFG-001)
- [ ] Staleness detection uses `index.md` dates, not individual file scans (REQ-STALE-001)
- [ ] v2 projects work without migration; v3 mechanisms degrade gracefully (REQ-COMPAT-002)
- [ ] Overview documents plan vocabulary convention (REQ-MIG-015)
- [ ] Overview documents version marker semantics as process version (REQ-MIG-015)
- [ ] Overview lists v3 behavioral additions (REQ-MIG-015)
