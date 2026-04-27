---
status: Approved
last_updated: 2026-04-28
requires:
  - REQ-SKILL-001
  - REQ-SKILL-002
  - REQ-SKILL-003
  - REQ-SKILL-004
  - REQ-SKILL-005
  - REQ-SKILL-006
  - REQ-SKILL-007
  - REQ-SKILL-008
  - REQ-STALE-001
---

# Skill Updates

## Context

All seven existing SDD skills reference v1 artifact paths and conventions.
Each skill needs targeted updates to its phase detection logic, read/write
paths, and staleness checks. The changes are mechanical — the skill workflows
themselves don't change, only the paths and formats they operate on.

This spec documents the changes needed in each skill, organized by skill.

## Design

### Shared Changes (All Skills)

Every SDD skill's phase detection section must be updated:

1. **Read version**: Check `docs/.sdd-version` on entry. If missing, suggest
   `sdd-migrate`.
2. **Requirements path**: Replace `docs/requirements.md` with
   `docs/requirements/index.md` for existence/staleness checks.
3. **Staleness comparison**: Compare against `docs/requirements/index.md`'s
   `last_updated` instead of `docs/requirements.md`'s `last_updated`.

**Why suggest migration instead of silently handling both formats**: Dual-format
support in every skill creates complexity and bugs. A clean migration followed
by single-format skills is simpler and more maintainable.

### sdd-research

**Current behavior**: Writes to `docs/research/{topic}.md`.

**Changes**:
1. **ID assignment**: Scan `docs/research/RS-*` directories to find the next
   sequential number. Start at RS-001 if none exist.
2. **Output path**: Write to `docs/research/RS-NNN-{topic}/findings.md`
   instead of `docs/research/{topic}.md`.
3. **Frontmatter**: Add `id: RS-NNN` field to findings frontmatter.
4. **Index maintenance**: After writing findings, update
   `docs/research/index.md` — add or update the row for this RS ID.
5. **Phase detection**: When checking for existing research on a topic, scan
   `RS-*` directories and read their `findings.md` files (not flat files).

**Unchanged**: The findings document format, research process, budget
enforcement, and recommendation logic remain the same.

### sdd-requirements

**Current behavior**: Reads/writes a single `docs/requirements.md`.

**Changes**:
1. **Format detection**: On entry, check whether `docs/requirements.md` (v1)
   or `docs/requirements/index.md` (v2) exists. If v1 is found, suggest
   running `sdd-migrate` before proceeding.
2. **Read path**: Read all category files under `docs/requirements/` by
   scanning subdirectories. Use `index.md` for the overview and file listing.
3. **Write path**: Write requirements to the appropriate category file based
   on domain. Create new category files and directories as needed.
4. **ID generation**: Use `REQ-{DOMAIN}-{NNN}` scheme. Determine domain from
   target file's frontmatter. Assign next sequential number within that domain.
5. **Index maintenance**: After any change, update `docs/requirements/index.md`:
   bump version (major or minor per rules), bump `last_updated`, update the
   Files table.
6. **Traceability**: After adding a new requirement, add a row to
   `docs/requirements/traceability.md` with the Spec/Test/Implementation/
   Verified columns blank.
7. **Removed requirements**: Instead of `[Removed: date — reason]` inline
   markers, remove the requirement from the category file and mark it
   `[Deprecated]` in `traceability.md`. Never reuse the ID.
8. **Research staleness**: On entry, compare newest research date (from
   `docs/research/index.md`) against `docs/requirements/index.md`'s
   `last_updated`. If research is newer, inform the user.
9. **File size monitoring**: After writing, check if the target file exceeds
   300 lines. If approaching, recommend splitting.

**Unchanged**: The elicitation process, question categories, requirement rules
(testable, one-per-ID, must/should/may), and review cycle.

### sdd-specs

**Current behavior**: Reads `docs/requirements.md`, writes `docs/spec/`.

**Changes**:
1. **Read path**: Read requirements from `docs/requirements/index.md` (for
   overview) and `docs/requirements/{category}/*.md` (for detail). The index
   tells the skill which files exist.
2. **Requires field**: Use `REQ-{DOMAIN}-{NNN}` IDs in spec frontmatter
   `requires` lists.
3. **Traceability update**: After writing or updating a spec, update
   `docs/requirements/traceability.md` — fill the Spec column for each
   requirement the spec addresses.
4. **Staleness check**: Compare `docs/requirements/index.md`'s `last_updated`
   against each spec's `last_updated`.
5. **Coverage check**: During the traceability summary (Step 5), read
   `traceability.md` to verify all requirements have spec coverage. Report
   uncovered requirements from the matrix rather than scanning requirement
   files directly.

**Unchanged**: The spec format, review cycle, and spec rules.

### sdd-plan

**Current behavior**: Reads specs, writes `docs/plan.md`. Appends changelogs
on rewrite.

**Changes**:
1. **Archival on rewrite**: Before writing a new plan (due to staleness or
   fresh creation when a plan exists), archive the current `docs/plan.md` to
   `docs/plan-history/{date}-{reason}.md`.
2. **Active plan format**: Write only current/future milestones. Completed
   milestones go in a `## Completed` section as one-line summaries.
3. **No changelog section**: Do not write a `## Plan Changelog` section in
   the active plan.
4. **Staleness check**: Compare against `docs/requirements/index.md`'s
   `last_updated` (not `docs/requirements.md`).
5. **Requirements reading**: Read from `docs/requirements/{category}/*.md`
   for priority context. Use `index.md` to discover which files exist.
6. **Research reading**: Read from `docs/research/RS-*/findings.md` instead
   of `docs/research/*.md`.

**Unchanged**: The planning process, task typing (implement/spike/verify),
milestone structure, dependency ordering, and replan trigger definition.

### sdd-implement

**Current behavior**: Reads plan and specs, implements tasks.

**Changes**:
1. **Requirements path**: Read from `docs/requirements/{category}/*.md` when
   needing requirement context (e.g., to understand priority or scope).
2. **Staleness check**: Compare `docs/requirements/index.md`'s `last_updated`
   against specs and plan.
3. **Spike tasks**: When a spike task produces findings, ensure they go to
   `docs/research/RS-NNN-{topic}/findings.md` (following the research
   artifact convention) and update `docs/research/index.md`.
4. **Traceability update**: When implementing a task:
   - After writing tests: update `traceability.md`'s Test column for the
     relevant requirements.
   - After writing code: update `traceability.md`'s Implementation column.
5. **Research reading**: Read from `docs/research/RS-*/findings.md`.

**Unchanged**: The TDD inner loop, stuck detection, milestone checkpoints,
spec gap handling, and task completion checklist.

### sdd-verify

**Current behavior**: Reads all artifacts, writes `docs/verification.md`.

**Changes**:
1. **Requirements path**: Read from `docs/requirements/{category}/*.md` to
   collect acceptance criteria.
2. **Traceability verification**: Read `docs/requirements/traceability.md`
   and verify:
   - Every requirement has a spec (Spec column filled)
   - Every implemented requirement has tests (Test column filled)
   - Flag gaps in the verification report.
3. **Traceability update**: After verification, update `traceability.md`'s
   Verified column with pass/fail for each requirement.
4. **Staleness check**: Compare `docs/requirements/index.md`'s `last_updated`
   against plan date.
5. **Plan archival on cycle complete**: After successful verification, the
   plan may be archived. Note this in the recommendation: "Cycle complete —
   plan can be archived with `sdd-plan` on next invocation."

**Unchanged**: The verification process, quality gates, acceptance criteria
walkthrough, user-perspective validation, regression check, and report format.

### sdd-replan

**Current behavior**: Revises plan, appends changelog, marks removed tasks.

**Changes**:
1. **Archival on significant replan**: Before making significant changes
   (adding/removing milestones), archive the current plan to
   `docs/plan-history/{date}-replan-{reason}.md`.
2. **Changelog destination**: Write the changelog entry to the archived plan
   file, not to the active plan.
3. **Removed tasks**: Move invalidated tasks to the archive file. Do not
   write `[removed: reason]` markers in the active plan.
4. **Requirements path**: Read from `docs/requirements/{category}/*.md`.
5. **Staleness check**: Check `docs/requirements/index.md` and spec dates
   as part of situation assessment.

**Unchanged**: The replan process, issue classification (Level 1-4), routing
logic, and rules (minimize disruption, preserve history, cascade awareness).

## Verification

### Automated
- For each skill SKILL.md file, verify it references v2 paths:
  - `docs/research/RS-*/findings.md` (not `docs/research/*.md`)
  - `docs/requirements/index.md` (not `docs/requirements.md`)
  - `docs/requirements/{category}/*.md` for reading requirements
  - `docs/plan-history/` for archival
- Verify no skill references the v1 monolithic `docs/requirements.md` as a
  write target
- Verify `sdd-replan` does not mention appending changelogs to the active plan
- Verify `sdd-requirements` includes format detection logic

### Manual
- Run each skill against a v2 project structure and confirm correct path usage
- Run `sdd-requirements` against a v1 project and confirm migration suggestion
- Run `sdd-replan` and confirm changelog goes to archive, not active plan

### Acceptance Criteria
- [ ] All 7 skills updated for v2 paths (REQ-SKILL-001)
- [ ] `sdd-research` writes to `RS-NNN-{topic}/findings.md` and maintains index (REQ-SKILL-002)
- [ ] `sdd-requirements` reads/writes split files, maintains index with versioning (REQ-SKILL-003)
- [ ] `sdd-requirements` detects v1 format and suggests migration (REQ-SKILL-003)
- [ ] `sdd-specs` reads from split requirements, updates traceability (REQ-SKILL-004)
- [ ] `sdd-plan` archives before rewrite, keeps active plan lean (REQ-SKILL-005)
- [ ] `sdd-implement` updates traceability when writing tests/code (REQ-SKILL-006)
- [ ] `sdd-verify` verifies traceability matrix, updates Verified column (REQ-SKILL-007)
- [ ] `sdd-replan` writes changelogs/removed tasks to archive only (REQ-SKILL-008)
- [ ] All skills use `index.md` for staleness detection (REQ-STALE-001)
