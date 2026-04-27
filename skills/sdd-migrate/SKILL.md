---
name: sdd-migrate
description: >
  Migrates SDD artifact structures between versions (currently v1 to v2).
  Handles research directory restructuring, requirements splitting with ID
  remapping, and plan archival. Use when other SDD skills detect old-format
  artifacts or when upgrading a project to the latest SDD conventions. Skip
  if docs/.sdd-version already shows the target version.
---

# SDD: Migrate

You are migrating a project's SDD artifacts from one structure version to another. This is a one-time operation per version transition. Each step is independent and idempotent — you can re-run safely after interruption.

## Version Detection

Before anything else, determine the current artifact version:

1. If no `docs/` directory exists at all, inform the user there is nothing to migrate and exit.
2. Read `docs/.sdd-version`:
   - **File missing** → v1 detected. Offer migration to v2.
   - **Contains `2`** → already at v2. Inform the user and exit.
   - **Contains any other value** → unknown version. Warn the user and exit without changes.

Tell the user which version you detected and what will happen. Get confirmation before proceeding.

## Migration Pipeline Overview

The v1-to-v2 migration has three independent steps:

```
Step 1: Research    (docs/research/*.md    -> docs/research/RS-NNN-{topic}/)
Step 2: Requirements (docs/requirements.md -> docs/requirements/{category}/)
Step 3: Plan        (docs/plan.md          -> docs/plan-history/ + lean plan)
```

Each step checks its own preconditions. If research is already migrated but requirements are not, Step 2 runs without Step 1. This supports partial migrations and resumption after interruption.

**Ask the user for confirmation before each step.** Present what will change and wait for approval.

## Step 1: Research Migration

### Precondition

`docs/research/*.md` files exist at the root level (not already inside `RS-NNN-*` directories). If no flat research files exist, skip this step and tell the user.

### Process

1. Collect all `docs/research/*.md` files, excluding `index.md` if present.
2. Sort by file modification date (oldest first).
3. For each file, assign the next `RS-NNN` number starting from 001:
   - Derive `{topic}` from the original filename in kebab-case (strip `.md`, lowercase, hyphens for spaces/underscores).
   - Create directory `docs/research/RS-NNN-{topic}/`.
   - Move the file to `docs/research/RS-NNN-{topic}/findings.md`.
   - Add `id: RS-NNN` to the file's YAML frontmatter if not already present.
   - If the file has `status: In-Progress`, preserve it as-is (do not force to Complete).
4. Present the proposed mapping to the user before executing moves:
   ```
   oauth-flow.md       -> RS-001-oauth-flow/findings.md
   rate-limiting.md    -> RS-002-rate-limiting/findings.md
   ```
5. After all files are moved, generate `docs/research/index.md` listing all research entries with their IDs, topics, and statuses.

### Idempotency

If `RS-NNN-*` directories already exist alongside flat files, only migrate the flat files. Start numbering after the highest existing RS number. Existing directories are not touched.

## Step 2: Requirements Migration

### Precondition

`docs/requirements.md` exists in monolithic v1 format. If the file does not exist or `docs/requirements/` directory already contains category files, skip this step and tell the user.

### Process

1. Read `docs/requirements.md` fully.
2. Parse all requirement IDs and their sections.
3. Group requirements by their type prefix:
   - `REQ-F-*` -> `functional/` (further grouped by domain from section headings)
   - `REQ-NF-*` -> `non-functional/`
   - `REQ-I-*` -> `integration/`
   - `REQ-C-*` -> `configuration/`

#### Domain Prefix Inference

4. For functional requirements, inspect section headings in the v1 file (e.g., `### Authentication`, `### Data Pipeline`).
5. Propose a short uppercase prefix for each domain:
   ```
   ### Authentication   -> AUTH
   ### Data Pipeline    -> DATAPIPE
   ### User Management  -> USERMGMT
   ```
6. **Present the proposed prefixes to the user and wait for confirmation or overrides.** Do not proceed until the user approves the mapping.

#### File Creation and ID Remapping

7. Create category directories under `docs/requirements/`:
   ```
   docs/requirements/functional/auth.md
   docs/requirements/functional/datapipe.md
   docs/requirements/non-functional/performance.md
   docs/requirements/integration/external-apis.md
   docs/requirements/configuration/settings.md
   ```
8. Write each category file with proper YAML frontmatter (status, last_updated, category).
9. Remap IDs: `REQ-F-001` becomes `REQ-{DOMAIN}-001`. Renumber within each domain starting from 001.
10. Log the full ID mapping (old -> new) so the user can review:
    ```
    REQ-F-001 -> REQ-AUTH-001
    REQ-F-002 -> REQ-AUTH-002
    REQ-F-003 -> REQ-DATAPIPE-001
    ```

#### Cross-File ID Replacement

11. Perform in-place replacement of old IDs across all files in `docs/`:
    - `docs/spec/*.md` — frontmatter `requires` lists and prose references
    - `docs/plan.md` — task traces and requirement references
    - `docs/verification.md` — acceptance criteria tables
    - Any other `.md` files under `docs/`
12. **Do not modify files outside `docs/`** — code references (comments, test names) are intentionally left as-is. The traceability matrix provides the mapping for developers to update manually.

#### Index and Traceability

13. Create `docs/requirements/index.md` with `version: 2.0` in frontmatter, listing all requirement files and their categories.
14. Create `docs/requirements/traceability.md` seeded from spec `requires` fields (if specs exist). Format: table mapping requirement IDs to spec files.

#### Verification and Cleanup

15. Grep all files under `docs/` for any remaining old-format IDs (`REQ-F-*`, `REQ-NF-*`, `REQ-I-*`, `REQ-C-*`). Report any found — these indicate incomplete replacement.
16. Only after verifying all replacements succeeded, delete `docs/requirements.md`.

### ID Remapping Safety

- Before deleting the old file, verify every old ID has a corresponding new ID.
- Old IDs are unique strings (e.g., `REQ-F-001`) that won't match non-ID text, making in-place replacement safe.
- If any replacement fails verification, stop and report the problem. Do not delete the original file.

## Step 3: Plan Migration

### Precondition

`docs/plan.md` exists. If it does not exist, skip this step and tell the user.

### Process

1. Read `docs/plan.md`.
2. Create `docs/plan-history/` directory if it does not exist.
3. Copy the full plan to `docs/plan-history/{YYYY-MM-DD}-pre-v2-migration.md` (using today's date).
4. Verify the archived file is identical to the original before modifying.
5. Parse the plan to identify:
   - **Completed milestones**: all tasks marked done
   - **Active/future milestones**: tasks pending or in-progress
   - **Changelog sections** (`## Plan Changelog` or similar)
   - **`[removed: ...]` markers**
6. Rewrite `docs/plan.md`:
   - **Keep**: Overview, Conventions, active/future milestones (with full task detail), Replan Triggers, Risks
   - **Summarize**: completed milestones become one line each in a `## Completed` section (milestone name + date completed + number of tasks)
   - **Remove**: `## Plan Changelog` sections, `[removed: ...]` markers
7. **Preserve task completion status** — any task marked `[x]` stays marked `[x]`. Do not reset progress.
8. Present the before/after summary to the user:
   ```
   Archived: docs/plan-history/2026-04-27-pre-v2-migration.md
   Completed milestones summarized: 3 (M1, M2, M3)
   Active milestones preserved: 2 (M4, M5)
   Removed: changelog (47 lines), 5 [removed:] markers
   ```

## Finalization

After all three steps complete (or are skipped because already done):

1. Write `docs/.sdd-version` containing `2` (single line, no trailing content).
2. Present a migration summary to the user:
   ```
   Migration v1 -> v2 complete.
   - Research: N files migrated to RS-NNN directories
   - Requirements: N requirements remapped across M files
   - Plan: archived to plan-history/, N completed milestones summarized
   - ID mapping: [list of old -> new ID changes]
   - Version: docs/.sdd-version set to 2
   ```

## Mid-Cycle Handling

The migration must preserve the current SDD phase state. Be aware of these scenarios:

| Current phase | What to preserve |
|--------------|-----------------|
| Research in progress | Migrate files with `status: In-Progress` intact; do not force completion |
| Requirements draft | Split into category files preserving current status |
| Specs in progress | Update ID references in spec `requires` lists |
| Plan in progress | Remap IDs in task traces; preserve task completion status (`[x]` / `[ ]`) |
| Implementation active | Remap IDs in docs only; do NOT touch code files |
| Verification | Remap IDs in verification tables |

After migration, the project should be able to resume its current SDD phase using the updated v2 skills without any manual fixup.

## Future Migrations

This skill is structured to support future version transitions. When v3 is defined:

1. Add a new section `## v2 to v3 Migration` with its own steps.
2. Update version detection to handle `2` -> offer v3, `3` -> already done.
3. Each migration is self-contained — v2-to-v3 does not re-run v1-to-v2 logic.

The version detection block at the top routes to the correct migration path:

```
version missing  -> run v1-to-v2
version == 2     -> check if v3 migration exists; if so, offer it; otherwise exit
version == 3     -> already current, exit
unknown          -> warn and exit
```

## Rules

- **Confirm before each step**: never modify files without user approval
- **Idempotent steps**: each step checks preconditions and skips if already done
- **No data loss**: archive before modifying, verify before deleting
- **Docs only**: never modify files outside `docs/` during migration
- **Preserve phase state**: task completion, draft statuses, in-progress research all survive migration
- **Log everything**: print the ID mapping, file moves, and changes so the user has a full audit trail
- **Stop on error**: if any verification check fails (missing ID mapping, failed replacement), halt and report rather than continuing with partial state
- **Domain prefixes are user-approved**: always propose and wait for confirmation before remapping IDs
