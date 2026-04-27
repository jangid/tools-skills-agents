---
status: Approved
last_updated: 2026-04-28
requires:
  - REQ-MIG-001
  - REQ-MIG-002
  - REQ-MIG-003
  - REQ-MIG-004
  - REQ-MIG-005
  - REQ-MIG-006
  - REQ-MIG-007
  - REQ-MIG-008
  - REQ-CFG-001
---

# Migration (sdd-migrate)

## Context

The SDD artifact structure is changing from v1 (flat files, monolithic
requirements, accumulating plans) to v2 (ID-prefixed research directories,
split requirements with versioned index, lean plans with archival). Existing
projects using SDD skills need a migration path that handles mid-cycle
projects safely.

This spec defines a new `sdd-migrate` skill that performs the migration and
supports future version transitions.

## Design

### Skill Identity

- **Skill name**: `sdd-migrate`
- **Location**: `skills/sdd-migrate/SKILL.md`
- **Purpose**: One-time migration between SDD artifact structure versions
- **Invocation**: User runs `/sdd-migrate` or the skill is suggested by other
  skills when they detect an old format

### Version Detection

On entry, the skill reads `docs/.sdd-version`:

| File state | Detected version | Action |
|------------|-----------------|--------|
| Missing | v1 | Offer migration to v2 |
| Contains `2` | v2 | Inform user, exit |
| Contains unknown value | Unknown | Warn and exit |

If no `docs/` directory exists at all, there's nothing to migrate — inform
the user and exit.

### Migration Pipeline

The migration runs in three independent steps. Each step is idempotent — it
can be re-run safely if interrupted.

```
Step 1: Research    (docs/research/*.md → docs/research/RS-NNN-{topic}/)
Step 2: Requirements (docs/requirements.md → docs/requirements/{category}/)
Step 3: Plan        (docs/plan.md → docs/plan-history/ + lean plan.md)
```

**Independence**: Each step checks its own preconditions. If research is
already migrated but requirements aren't, Step 2 runs without Step 1. This
supports partial migrations and resumption after interruption.

### Step 1: Research Migration

**Precondition**: `docs/research/*.md` files exist at the root level (not
inside `RS-NNN-*` directories).

**Process**:
1. Collect all `docs/research/*.md` files (excluding `index.md` if it exists).
2. Sort by file modification date (oldest first).
3. For each file, assign the next `RS-NNN` number starting from 001.
4. Create `docs/research/RS-NNN-{topic}/` directory where `{topic}` is derived
   from the original filename (kebab-case).
5. Move the file to `docs/research/RS-NNN-{topic}/findings.md`.
6. Add `id: RS-NNN` to the file's frontmatter if not already present.
7. After all files are moved, generate `docs/research/index.md`.

**Idempotency**: If `RS-NNN-*` directories already exist alongside flat files,
only migrate the flat files. Existing directories are not touched.

### Step 2: Requirements Migration

**Precondition**: `docs/requirements.md` exists (monolithic v1 format).

**Process**:
1. Read `docs/requirements.md` fully.
2. Parse all requirement IDs and their sections.
3. Group requirements by category:
   - `REQ-F-*` → `functional/` (further grouped by domain if detectable from
     section headings)
   - `REQ-NF-*` → `non-functional/`
   - `REQ-I-*` → `integration/`
   - `REQ-C-*` → `configuration/`
4. For each group, determine the domain prefix:
   - Use the section heading as a hint (e.g., "### Authentication" → `AUTH`).
   - If ambiguous, prompt the user to choose a prefix.
5. Create category files with proper frontmatter.
6. Remap IDs: `REQ-F-001` → `REQ-{DOMAIN}-001` (renumber within each domain
   starting from 001).
7. Perform in-place replacement of old IDs across all files in `docs/`:
   - `docs/spec/*.md` (frontmatter `requires` lists and prose references)
   - `docs/plan.md` (task traces)
   - `docs/verification.md` (acceptance criteria tables)
8. Create `docs/requirements/index.md` with `version: 2.0`.
9. Create `docs/requirements/traceability.md` seeded from spec `requires`
   fields (if specs exist).
10. Verify all replacements succeeded (grep for any remaining `REQ-F-*`,
    `REQ-NF-*`, `REQ-I-*`, `REQ-C-*` patterns in `docs/`).
11. Delete `docs/requirements.md`.

**ID Remapping Safety**:
- Before deleting the old file, verify every old ID has a corresponding new ID.
- Log the full mapping (old → new) to stdout so the user can review.
- Old IDs are unique strings (e.g., `REQ-F-001`) that won't match non-ID text,
  making in-place replacement safe.

**Domain prefix inference**: The skill inspects category headings in the v1
file (e.g., `### Authentication`, `### Data Pipeline`). It proposes a short
uppercase prefix for each (e.g., `AUTH`, `DATAPIPE`). The user confirms or
overrides before the remap happens.

### Step 3: Plan Migration

**Precondition**: `docs/plan.md` exists.

**Process**:
1. Read `docs/plan.md`.
2. Create `docs/plan-history/` directory.
3. Copy the full plan to `docs/plan-history/{date}-pre-v2-migration.md`.
4. Parse the plan to identify:
   - Completed milestones (tasks all marked done)
   - Active/future milestones (tasks pending or in-progress)
   - Changelog sections
   - `[removed: ...]` markers
5. Rewrite `docs/plan.md`:
   - Keep: Overview, Conventions, active/future milestones, Replan Triggers,
     Risks.
   - Summarize: completed milestones → one line each in `## Completed`.
   - Remove: `## Plan Changelog`, `[removed: ...]` markers.
6. Verify the archived file is identical to the original before modifying.

### Finalization

After all steps complete:
1. Write `docs/.sdd-version` containing `2`.
2. Present a summary to the user:
   - Research: N files migrated to RS-NNN directories
   - Requirements: N requirements remapped across M files
   - Plan: archived to `plan-history/`, N completed milestones summarized
   - ID mapping: list of old → new ID changes

### Mid-Cycle Handling

The migration must preserve the current SDD phase state:

| Current phase | What to preserve |
|--------------|-----------------|
| Research in progress | Don't migrate the in-progress spike; let it finish first or migrate it with `status: In-Progress` |
| Requirements draft | Migrate the draft; split into category files with `status: Approved` |
| Specs in progress | Update ID references in spec `requires` lists |
| Plan in progress | Remap IDs in task traces; preserve task completion status |
| Implementation | Remap IDs; code references (comments, test names) are NOT migrated — only docs/ files |
| Verification | Remap IDs in verification tables |

**Why not migrate code references**: Code files may use requirement IDs in
comments or test names, but these are implementation details. Migrating them
risks breaking code. The traceability matrix provides the mapping; developers
update code references as they encounter them.

### Future Migrations

The skill is structured to support future versions:

```
if version == missing:
    migrate_v1_to_v2()
elif version == 2:
    if target == 3:
        migrate_v2_to_v3()
    else:
        inform("already at v2")
```

Each migration is a self-contained function. The skill version and migration
logic are defined in `SKILL.md`, not in external scripts.

## Verification

### Manual
- Run migration on a v1 project and verify:
  - All research files moved to RS-NNN directories
  - All requirement IDs remapped consistently
  - Plan archived and active plan is lean
  - `docs/.sdd-version` contains `2`
  - No orphaned old-format files remain
- Run migration on a v2 project and verify it exits cleanly
- Run migration on a mid-cycle project and verify phase can resume

### Acceptance Criteria
- [ ] `sdd-migrate` skill exists at `skills/sdd-migrate/SKILL.md` (REQ-MIG-001)
- [ ] Detects v1 (no version file) and v2 (version file = 2) (REQ-MIG-002)
- [ ] Research files moved to `RS-NNN-{topic}/findings.md` (REQ-MIG-003)
- [ ] RS numbers assigned by file date (REQ-MIG-003)
- [ ] `docs/research/index.md` created (REQ-MIG-003)
- [ ] Requirements split into category files (REQ-MIG-004)
- [ ] IDs remapped from `REQ-{TYPE}-{NNN}` to `REQ-{DOMAIN}-{NNN}` (REQ-MIG-004)
- [ ] Old IDs replaced in all docs/ files (REQ-MIG-004)
- [ ] `requirements/index.md` created with version 2.0 (REQ-MIG-004)
- [ ] `traceability.md` seeded from existing specs (REQ-MIG-004)
- [ ] Plan archived to `plan-history/` (REQ-MIG-005)
- [ ] Active plan contains only current/future work (REQ-MIG-005)
- [ ] `docs/.sdd-version` written with value `2` (REQ-MIG-006)
- [ ] No files deleted until replacements verified (REQ-MIG-007)
- [ ] Each step independently runnable and idempotent (REQ-MIG-007)
- [ ] Mid-cycle projects: IDs remapped, phase state preserved (REQ-MIG-008)
- [ ] Version marker at `docs/.sdd-version` (REQ-CFG-001)
