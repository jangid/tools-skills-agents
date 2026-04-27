---
domain: REQ
last_updated: 2026-04-28
status: Approved
---

# Requirements: Requirements Structure

## Overview

How requirements are organized, versioned, and traced across the SDD lifecycle.

## Requirements

### REQ-REQ-001: Requirements directory layout
Requirements must be organized into `docs/requirements/` with the following
subdirectories:
- `functional/` — one file per feature domain (e.g., `auth.md`, `billing.md`)
- `non-functional/` — one file per concern (e.g., `performance.md`, `security.md`)
- `integration/` — one file per external system (e.g., `stripe-api.md`)
- `configuration/` — one file per configuration area (e.g., `env-config.md`)
[Priority: must]

### REQ-REQ-002: Requirements index with versioning
`docs/requirements/index.md` must contain:
- YAML frontmatter with `version` (semver `major.minor`), `status`
  (Draft/Approved), and `last_updated` fields
- A listing of all requirement files with their status and requirement count
- A reference to `docs/requirements/traceability.md`

The version must be bumped on every change:
- Major bump when requirements are added, removed, or fundamentally changed
- Minor bump for clarifications, rewording, or priority changes
[Priority: must]

### REQ-REQ-003: Requirement ID scheme
Requirements must use the ID format `REQ-{DOMAIN}-{NNN}` where `{DOMAIN}` is an
uppercase short name matching the file's topic (e.g., `AUTH`, `PERF`, `STRIPE`)
and `{NNN}` is a zero-padded sequential number within that domain. IDs must be
unique across the entire requirements set.
[Priority: must]

### REQ-REQ-004: Per-file metadata
Each requirements category file must have YAML frontmatter containing:
- `domain` — the domain prefix used in IDs (e.g., `AUTH`)
- `last_updated` — date of last modification
- `status` — Draft or Approved
[Priority: must]

### REQ-REQ-005: File size limit
Each requirements category file should stay under 300 lines. When a file
approaches this limit, the skill should recommend splitting it into more
specific domain files.
[Priority: should]

### REQ-REQ-006: Auto-maintained index
The `sdd-requirements` skill must update `docs/requirements/index.md`
automatically whenever requirements are created, updated, or removed. The user
should not need to manually edit the index.
[Priority: must]

### REQ-REQ-007: Traceability matrix
A separate `docs/requirements/traceability.md` file must maintain a matrix
mapping requirement IDs to spec files, test files, and implementation status.
The format must be a markdown table. This file must be referenced from
`index.md` and updated by `sdd-specs` (when specs are written), `sdd-implement`
(when tests/code are written), and `sdd-verify` (when verification completes).
[Priority: must]
