---
status: Approved
last_updated: 2026-04-28
research_refs:
  - docs/research/sdd-artifact-structure.md
---

# Requirements: SDD Artifact Structure v2

## Overview

The SDD (Spec-Driven Development) workflow uses file-based artifacts to track
state across phases: research, requirements, specs, plan, implementation, and
verification. The current artifact structure has three problems: plan files grow
unboundedly across cycles, research files lack traceability, and requirements
live in a single monolithic file that doesn't scale. This project restructures
all SDD artifacts for bounded file sizes, traceable cross-references, and
AI-context-friendly document sizes, then updates all seven SDD skills to use the
new structure.

## Stakeholders

- **Pankaj Jangid** — creator and primary user of the SDD skills
- **Downstream users** — anyone using the SDD skills in their own projects

## Functional Requirements

### Research Structure

#### REQ-RS-001: Research directory convention
Each research spike must produce artifacts in a directory named
`docs/research/RS-NNN-{topic}/` where `NNN` is a zero-padded sequential number
and `{topic}` is kebab-case. The main findings file must be named `findings.md`.
Supporting files (prototypes, API responses, screenshots) may live alongside it
in the same directory.

#### REQ-RS-002: Research index
The `sdd-research` skill must auto-maintain a `docs/research/index.md` file.
Each entry must be one line containing: RS ID, topic, date, status, and a
one-sentence summary. The index must be updated every time a research spike is
created or its status changes.

#### REQ-RS-003: Research ID assignment
The skill must determine the next RS number by scanning existing
`docs/research/RS-*` directories and incrementing. If no research exists, start
at RS-001.

### Requirements Structure

#### REQ-REQ-001: Requirements directory layout
Requirements must be organized into `docs/requirements/` with the following
subdirectories:
- `functional/` — one file per feature domain (e.g., `auth.md`, `billing.md`)
- `non-functional/` — one file per concern (e.g., `performance.md`, `security.md`)
- `integration/` — one file per external system (e.g., `stripe-api.md`)
- `configuration/` — one file per configuration area (e.g., `env-config.md`)

#### REQ-REQ-002: Requirements index with versioning
`docs/requirements/index.md` must contain:
- YAML frontmatter with `version` (semver `major.minor`), `status`
  (Draft/Approved), and `last_updated` fields
- A listing of all requirement files with their status and requirement count
- A reference to `docs/requirements/traceability.md`

The version must be bumped on every change:
- Major bump when requirements are added, removed, or fundamentally changed
- Minor bump for clarifications, rewording, or priority changes

#### REQ-REQ-003: Requirement ID scheme
Requirements must use the ID format `REQ-{DOMAIN}-{NNN}` where `{DOMAIN}` is an
uppercase short name matching the file's topic (e.g., `AUTH`, `PERF`, `STRIPE`)
and `{NNN}` is a zero-padded sequential number within that domain. IDs must be
unique across the entire requirements set.

#### REQ-REQ-004: Per-file metadata
Each requirements category file must have YAML frontmatter containing:
- `domain` — the domain prefix used in IDs (e.g., `AUTH`)
- `last_updated` — date of last modification
- `status` — Draft or Approved

#### REQ-REQ-005: File size limit
Each requirements category file should stay under 300 lines. When a file
approaches this limit, the skill should recommend splitting it into more
specific domain files.

#### REQ-REQ-006: Auto-maintained index
The `sdd-requirements` skill must update `docs/requirements/index.md`
automatically whenever requirements are created, updated, or removed. The user
should not need to manually edit the index.

#### REQ-REQ-007: Traceability matrix
A separate `docs/requirements/traceability.md` file must maintain a matrix
mapping requirement IDs to spec files, test files, and implementation status.
The format must be a markdown table. This file must be referenced from
`index.md` and updated by `sdd-specs` (when specs are written), `sdd-implement`
(when tests/code are written), and `sdd-verify` (when verification completes).

### Plan Management

#### REQ-PLAN-001: Active plan size bound
`docs/plan.md` must contain only current and future milestones with their tasks.
Completed milestones must be summarized to a single line each (milestone name,
completion date, task count) in a `## Completed` section at the bottom of the
active plan.

#### REQ-PLAN-002: Plan archival
When `sdd-plan` rewrites a plan (due to staleness or new cycle) or `sdd-replan`
makes significant changes, the previous plan must be archived to
`docs/plan-history/{YYYY-MM-DD}-{reason}.md` before modification.

#### REQ-PLAN-003: Changelog in archive only
Replan changelogs must be written to the archived plan file, not appended to the
active `docs/plan.md`. The active plan must not contain a changelog section.

#### REQ-PLAN-004: Removed tasks cleanup
When tasks are invalidated during replanning, they must be moved to the archive
file. The active plan must not contain `[removed: ...]` markers.

### Staleness Detection

#### REQ-STALE-001: Index-based staleness
Staleness detection across all skills must compare against the `last_updated`
field in `docs/requirements/index.md` rather than a single `requirements.md`
file. When any category file is updated, `index.md`'s `last_updated` must also
be bumped.

#### REQ-STALE-002: Research-to-requirements staleness
When new research is completed (a `findings.md` with `status: Complete`), the
`sdd-requirements` skill should detect that research is newer than the
requirements version and inform the user that requirements may need updating.

### Migration

#### REQ-MIG-001: Standalone migration skill
A new `sdd-migrate` skill must handle migration between SDD artifact structure
versions. The skill must be versioned, with the current migration being to v2.

#### REQ-MIG-002: Version detection
The migration skill must detect the current artifact version:
- v1: flat `docs/research/{topic}.md` files, monolithic `docs/requirements.md`,
  plan with accumulated changelogs
- v2: the structure defined in this requirements document
If artifacts are already at the target version, inform the user and exit.

#### REQ-MIG-003: Research migration
The skill must move existing `docs/research/{topic}.md` files into
`docs/research/RS-NNN-{topic}/findings.md` directories, assigning sequential RS
numbers by file date. It must create `docs/research/index.md`.

#### REQ-MIG-004: Requirements migration
The skill must:
1. Split `docs/requirements.md` into category files under `docs/requirements/`
2. Remap IDs from `REQ-{TYPE}-{NNN}` to `REQ-{DOMAIN}-{NNN}`
3. Perform in-place replacement of old IDs across all docs files (specs, plan,
   verification)
4. Create `docs/requirements/index.md` with version `2.0`
5. Create `docs/requirements/traceability.md` seeded from existing spec
   `requires` fields
6. Delete the old `docs/requirements.md`

#### REQ-MIG-005: Plan migration
The skill must:
1. Move `docs/plan.md` to `docs/plan-history/{date}-pre-v2-migration.md`
2. Create a new `docs/plan.md` with only active/future tasks
3. Summarize completed milestones to one line each
4. Strip all changelogs and `[removed: ...]` markers from the active plan

#### REQ-MIG-006: Skill version tracking
The `sdd-migrate` skill must track the current artifact structure version (e.g.,
in a `docs/.sdd-version` file or similar marker) so future migrations can detect
the current version and apply the appropriate transformation.

#### REQ-MIG-007: Safe migration
The migration must not delete any files until replacements are verified to exist.
Each step (research, requirements, plan) must be independently runnable so
partial migrations can be resumed.

#### REQ-MIG-008: Mid-cycle migration
The migration skill must handle projects mid-cycle — where specs, plans, or
implementation are in progress. It must remap IDs in all existing artifacts
(specs, plan, verification) and preserve task completion status. After migration,
the relevant SDD skill must be able to resume from the detected phase.

## Non-Functional Requirements

#### REQ-CTX-001: AI context budget
No single artifact file consumed by an SDD skill during a phase should exceed
300 lines. Index files and traceability matrices are exempt from this limit but
should be kept as concise as possible.

#### REQ-CTX-002: Self-contained files
Each requirements category file must be readable in isolation — it must not
require reading other category files to understand its requirements. Cross-domain
dependencies must use explicit requirement IDs, not prose references.

#### REQ-COMPAT-001: Git-friendly format
All artifacts must be plain Markdown with YAML frontmatter. No binary files, no
tool-specific formats. Diffs must be human-readable.

## Integration Requirements

#### REQ-SKILL-001: Skill update scope
All seven existing SDD skills must be updated to read/write the v2 artifact
structure. Path references, phase detection logic, and staleness checks must
reflect the new layout.

#### REQ-SKILL-002: sdd-research updates
`sdd-research` must write to `docs/research/RS-NNN-{topic}/findings.md` and
auto-maintain `docs/research/index.md`.

#### REQ-SKILL-003: sdd-requirements updates
`sdd-requirements` must read/write per-domain files in
`docs/requirements/{category}/`, auto-maintain `index.md` with versioning, and
detect the old monolithic format (offering migration via `sdd-migrate`).

#### REQ-SKILL-004: sdd-specs updates
`sdd-specs` must read requirements from `docs/requirements/{category}/*.md`,
use the new `REQ-{DOMAIN}-{NNN}` IDs in `requires` frontmatter, and update
`docs/requirements/traceability.md` when mapping specs to requirements.

#### REQ-SKILL-005: sdd-plan updates
`sdd-plan` must implement the archive pattern (REQ-PLAN-002), keep the active
plan lean (REQ-PLAN-001), and read staleness from
`docs/requirements/index.md` (REQ-STALE-001).

#### REQ-SKILL-006: sdd-implement updates
`sdd-implement` must read requirements from the new paths, reference RS-* IDs
for spike tasks, and update `docs/requirements/traceability.md` when
tests/implementation are created.

#### REQ-SKILL-007: sdd-verify updates
`sdd-verify` must read requirements from the new paths, verify traceability
across split files using `traceability.md`, and update the traceability matrix
with verification results.

#### REQ-SKILL-008: sdd-replan updates
`sdd-replan` must write changelogs to the archive file (REQ-PLAN-003) and move
removed tasks to the archive (REQ-PLAN-004) instead of marking them in the
active plan.

## Configuration Requirements

#### REQ-CFG-001: Version marker location
The SDD artifact structure version must be stored in `docs/.sdd-version` as a
plain text file containing the version number (e.g., `2`). All skills may read
this to determine which artifact layout to expect.

## Out of Scope

- Changes to the spec document format (beyond updating path references and IDs)
- Changes to the verification report format (beyond updating path references)
- New skills beyond `sdd-migrate`
- Automated tooling outside of the skill definitions (no CLI scripts, no CI checks)
- Database-backed or non-Markdown requirements formats
- Per-requirement files (Doorstop model) — ruled out in research

## Open Questions

- Should `sdd-migrate` support rollback (v2 → v1), or is migration one-way?

## Resolved Questions

- **In-progress implementations during migration**: Migration does not require
  completing the current SDD cycle first. The `sdd-migrate` skill must handle
  mid-cycle migration — remapping IDs in partially-complete plans, specs, and
  implementation artifacts. Skills resume from the detected phase after migration.

## Glossary

- **SDD**: Spec-Driven Development — the cyclic, phase-based workflow defined by
  the seven sdd-* skills
- **Artifact**: A Markdown file produced by an SDD phase (research findings,
  requirements, specs, plan, verification report)
- **Staleness**: When a downstream artifact's `last_updated` is older than its
  upstream input, indicating it was written against outdated information
- **Domain prefix**: The uppercase short name in a requirement ID that maps to
  the topic of the file containing it (e.g., `AUTH`, `PERF`)
- **RTM**: Requirements Traceability Matrix — a table mapping requirements to
  specs, tests, and implementation status
