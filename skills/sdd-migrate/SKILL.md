---
name: sdd-migrate
description: >
  Migrates SDD artifact structures between versions (v1→v2→v3). Handles
  research directory restructuring, requirements splitting with ID remapping,
  plan archival, plan vocabulary rename, and v3 convention adoption. Use when
  other SDD skills detect old-format artifacts or when upgrading a project to
  the latest SDD conventions. Skip if docs/.sdd-version already shows `3`.
---

# SDD: Migrate

You are migrating a project's SDD artifacts from one structure version to another. This is a one-time operation per version transition. Each step is independent and idempotent — you can re-run safely after interruption.

## Version Detection

Before anything else, determine the current artifact version:

1. If no `docs/` directory exists at all, inform the user there is nothing to migrate and exit.
2. Read `docs/.sdd-version`:

| Disk state | Version | Action |
|------------|---------|--------|
| File missing | v1 | Run v1→v2 then v2→v3 in one invocation |
| Contains `2` | v2 | Offer v2→v3 migration |
| Contains `3` | v3 | Already current — inform user and exit |
| Other value | Unknown | Warn and exit without changes |

**Routing logic:**

1. If v3 → "Already at v3, nothing to migrate." Exit.
2. If v2 → run v2→v3 migration (see § v2 to v3 Migration below).
3. If v1 → run v1→v2 first (Steps 1-3 + Finalization below), then continue directly to v2→v3 without writing the intermediate version marker. The composition is sequential within a single invocation (see § v1 to v3 Composition).

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

## v1→v2 Finalization

After all three steps complete (or are skipped because already done):

1. **If running standalone (v1→v2 only):** Write `docs/.sdd-version` containing `2`.
2. **If running as part of v1→v3 composition:** Do NOT write the version marker here — continue directly to § v2 to v3 Migration. The marker is written by v2→v3 Finalization as `3`.
3. Present a v1→v2 migration summary:
   ```
   v1 -> v2 migration complete.
   - Research: N files migrated to RS-NNN directories
   - Requirements: N requirements remapped across M files
   - Plan: archived to plan-history/, N completed milestones summarized
   - ID mapping: [list of old -> new ID changes]
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

## v2 to v3 Migration

v3 adds behavioral conventions (chunk-close review, Q-IMPL protocol, per-milestone plans, cross-spec consistency) on top of the v2 artifact layout. The only artifact change is plan vocabulary — work-unit headers shift from `### M N:` to `### Chunk N:`. Migration is opt-in; v2 projects work without it.

### Backward Compatibility

v2 projects that have not run v2→v3 migration continue to work:

- **Chunk-close review** is inactive when plan headers don't use `### Chunk N:` format.
- **Per-milestone logic** activates only when per-milestone files (`docs/plan-{id}.md`) exist.
- **Q-IMPL entries** accumulate on demand — specs without `## Implementation Questions` are fine.

### Step 1: Plan Vocabulary Rename

**Skip this step if:**
- `docs/plan.md` does not exist
- The plan already uses `### Chunk N:` headers (no `### M\d+:` matches found)
- The plan is complete with no active work

**Process:**

1. Read `docs/plan.md`.
2. Scan for lines matching the regex `### M\d+:` (M followed by one or more digits, then a colon). This matches `### M1:`, `### M12:`, etc. It does NOT match `### Migration`, `### Models`, or other section headers starting with M.
3. Present proposed renames to the operator, preserving original numbering:
   ```
   ### M1: Foundation    →  ### Chunk 1: Foundation
   ### M2: Core Models   →  ### Chunk 2: Core Models
   ```
   Numbering is preserved (M1 → Chunk 1, not Chunk 0) — chunk-close triggers on `### Chunk N:` regardless of N's value, and renumbering would break external references for no functional benefit.
4. **Wait for operator confirmation before applying.** Do not rename automatically.
5. Apply renames in `docs/plan.md` only. Archive files in `docs/plan-history/` are historical snapshots — do not modify them.

**Edge cases:**
- **Mixed headers** (`### M1:` as delivery milestone alongside `### Chunk N:` as work units): Present the mixed state for operator confirmation; do not auto-rename delivery milestone headers.
- **Completed entries in `## Completed`**: Leave as-is — these are one-line summaries without `###` headers.

### Step 2: Multi-Milestone Split (Optional)

**Precondition:** `docs/plan.md` contains multiple delivery milestone groupings with distinct chunks under each.

1. Offer to split into per-milestone plan files (`docs/plan-{id}.md`) with `docs/plan.md` converted to an index. Each per-milestone file gets `milestone:`, `last_updated:`, and `status:` frontmatter.
2. **Operator confirms or declines. Declining is the default** — single-file plans are valid in v3.
3. If accepted, archive the pre-split plan to `docs/plan-history/` before splitting.

### Step 3: Capability Report

After completing required steps, report new v3 capabilities to the operator:

- **Chunk-close review**: Structured 4-check checklist at each `### Chunk N:` boundary during `sdd-implement`.
- **Q-IMPL deviation protocol**: Three-tier classification for implementation decisions diverging from spec.
- **Per-milestone plan support**: Optional structure for multi-milestone projects with milestone-scoped staleness.
- **Cross-spec consistency pass**: Type reference validation between specs during `sdd-specs`.

The report is informational — no operator action required. These mechanisms activate automatically during their respective skill phases.

### Step 4: Finalization

1. Write `3` to `docs/.sdd-version` (overwriting `2`).
2. Present a migration summary:
   - Plan vocabulary: N headers renamed (or "skipped — already using Chunk format")
   - Multi-milestone split: applied / declined / not applicable
   - New capabilities: listed in the capability report above

**Version marker is written last.** If any prior step fails or is interrupted, `.sdd-version` still contains `2`. Re-running `sdd-migrate` detects v2 and resumes the v2→v3 migration.

## v1 to v3 Composition

For v1 projects (`.sdd-version` missing), `sdd-migrate` runs v1→v2 (Steps 1-3 above) then v2→v3 (Steps 1-4 above) in a single invocation.

- **Intermediate state**: v1→v2 completes but does NOT write `.sdd-version` in the composition path — only the v2→v3 Finalization writes `3`.
- **Resumability**: If interrupted at any point, `.sdd-version` is still missing. Re-running `sdd-migrate` detects v1, re-runs v1→v2 (idempotent — each step checks preconditions and skips if already done), then continues to v2→v3.
- **v1→v2 logic unchanged**: The Step 1-3 sections above are not modified. v2→v3 is a new section. Composition is routing logic only.

## Rules

- **Confirm before each step**: never modify files without user approval
- **Idempotent steps**: each step checks preconditions and skips if already done
- **No data loss**: archive before modifying, verify before deleting
- **Docs only**: never modify files outside `docs/` during migration
- **Preserve phase state**: task completion, draft statuses, in-progress research all survive migration
- **Log everything**: print the ID mapping, file moves, and changes so the user has a full audit trail
- **Stop on error**: if any verification check fails (missing ID mapping, failed replacement), halt and report rather than continuing with partial state
- **Domain prefixes are user-approved**: always propose and wait for confirmation before remapping IDs
