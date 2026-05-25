---
id: RS-003
status: Complete
date: 2026-05-25
questions:
  - "What semantic differences between v2 and v3 justify a version bump?"
  - "How should sdd-migrate detect and execute v2→v3 migration?"
  - "How should sdd-migrate handle v1→v3 transitions?"
budget: "30-45 minutes"
---

# Research: v3 Migration Path

## Summary

The RS-002 skill improvements introduced one migration-required change
(plan vocabulary: `### M N:` → `### Chunk N:`), several migration-optional
patterns (per-milestone files, Q-IMPL sections), and many no-migration
behavioral changes. The v2→v3 migration is lightweight — primarily a
vocabulary rename in `docs/plan.md` plus a version bump. The recommended
v1→v3 strategy is sequential composition: run v1→v2 then v2→v3.

## Findings

### F1: v3 vs v2 semantic differences

**Confidence: High** — based on direct reading of all 5 modified SKILL.md
files, 10 specs, and the rubric M1 plan as evidence.

| Change | Classification | Rationale |
|--------|---------------|-----------|
| Plan vocabulary: `### Chunk N:` for work units | **Migration-required** | sdd-implement Step 4 triggers chunk-close review at `### Chunk N:` boundaries. Plans using `### M N:` as work-unit headers won't trigger chunk-close at the right boundaries. Functional impact, not cosmetic. |
| `## Implementation Questions` sections in specs | Migration-optional | Accumulate naturally during implementation via Q-IMPL protocol. No sections needed in existing specs until a deviation is recorded. |
| Per-milestone plan files (`docs/plan-{id}.md`) | Migration-optional | Single-milestone fallback (REQ-MPLAN-004) preserves existing behavior. Splitting is opt-in and only valuable for multi-milestone projects. |
| Milestone lifecycle frontmatter (`milestone:`, `status:`) | Migration-optional | Only applies to per-milestone plan files. Single-milestone plans don't use it. |
| Chunk-close review (4-check structured checklist) | No-migration-needed | Purely behavioral — the skill performs it during sdd-implement. No file format changes to existing artifacts. |
| Q-IMPL deviation protocol (3 tiers) | No-migration-needed | Behavioral. Protocol is in skill instructions; entries go into specs during implementation. |
| Cross-spec consistency pass | No-migration-needed | Behavioral — runs during sdd-specs. No changes to spec file format. |
| Milestone-scoped staleness | No-migration-needed | Behavioral — activates only when per-milestone files exist. Irrelevant to single-file plans. |
| Research-to-requirements staleness | No-migration-needed | Behavioral — sdd-requirements checks on entry. No artifact changes. |
| CLAUDE.md reading on context load | No-migration-needed | CLAUDE.md may or may not exist. The skill reads it if present. |
| Spike code separation | No-migration-needed | Behavioral convention in sdd-implement. Existing spike artifacts are fine. |

**Key insight:** Only one change is migration-required (the plan vocabulary),
and even that only affects projects with active or in-progress plans that use
`### M N:` as work-unit headers. Projects whose plans are complete (all tasks
done) or already use `### Chunk N:` headers need only the version bump.

**Evidence from rubric project:** The rubric project (v2, `docs/.sdd-version`
= 2) already uses `### Chunk N:` headers — the convention originated there
during M1 planning. Its v2→v3 migration would be version-bump only.

### F2: v2→v3 migration procedure

**Confidence: High** — procedure directly follows from F1's classification.

#### Detection

Primary signal: `docs/.sdd-version` contains `2`.

No secondary heuristics needed. The version marker is authoritative. Plans
without `### Chunk N:` headers don't break the v2→v3 migration — they just
need the vocabulary rename step.

#### Step 1: Plan Vocabulary Rename

**Precondition**: `docs/plan.md` exists and contains `### M` headers that
serve as work-unit groupings.

**Process:**

1. Read `docs/plan.md`.
2. Identify `### M N:` headers (pattern: `### M` followed by a digit).
3. **Disambiguation**: Not all `### M N:` headers are work-unit chunks.
   In a project with delivery milestones (M1, M2), the same pattern might
   mean a delivery grouping. The operator must confirm which are work units
   vs delivery milestones.
4. Present the proposed renames:
   ```
   ### M1: Foundation    →  ### Chunk 0: Foundation
   ### M2: Core Models   →  ### Chunk 1: Core Models
   ```
   Note: renumbering from M1-based to 0-based aligns with the `### Chunk N:`
   convention in sdd-plan.
5. After operator approval, apply the renames in `docs/plan.md`.
6. If the plan has already-completed `### M N:` entries in `## Completed`,
   leave them as-is — completed sections are historical references.
7. Also update any `docs/plan-history/*.md` files? **No** — archive files
   are historical snapshots. Leave them untouched.

**Edge cases:**

- **Plan already uses `### Chunk N:`**: Skip step entirely. Some v2 projects
  (like rubric) adopted the convention before v3 was formalized.
- **Mixed headers** (`### M1:` for delivery milestone + `### Chunk N:` for
  work units within): Already v3-compatible. Skip rename, but confirm with
  operator.
- **No plan exists** (`docs/plan.md` missing): Skip step.
- **Plan complete** (all tasks done, no active work): Skip rename. The
  vocabulary shift only matters for active plans that sdd-implement will
  read.

#### Step 2: Per-Milestone Split (Optional)

**Precondition**: `docs/plan.md` contains multiple top-level delivery
milestone headers (e.g., `## M1`, `## M2` or equivalent groupings) with
distinct chunks under each.

**Process:**

1. Detect multi-milestone structure in `docs/plan.md`.
2. Offer to split into per-milestone files per milestone-plans.md spec.
3. This is opt-in — operator can decline and keep the single-file plan.
4. If accepted:
   - Create `docs/plan-{id}.md` for each active/future milestone
   - Convert `docs/plan.md` to index format
   - Add `milestone:`, `last_updated:`, `status:` frontmatter to each file
5. Archive the pre-split plan to `docs/plan-history/`.

**This step is advisory, not migration-required.** Single-file plans work
fine in v3. The offer informs the operator about the new capability.

#### Step 3: Report Migration-Optional Features

After completing required migration, inform the operator about new v3
capabilities they can adopt:

```
v3 migration complete. New capabilities available:
- Q-IMPL deviation protocol: spec deviations during implementation are
  classified and documented in specs' Implementation Questions sections.
  No action needed — entries accumulate naturally.
- Per-milestone plan files: if your project spans multiple delivery
  milestones, you can split docs/plan.md into per-milestone files.
  Use sdd-plan to create the structure.
- Chunk-close review: sdd-implement now runs a 4-check structured
  review at each ### Chunk N: boundary.
- Cross-spec consistency: sdd-specs now validates type references
  between specs before the coverage check.
```

#### Step 4: Finalization

1. Write `3` to `docs/.sdd-version`.
2. Present migration summary.

#### Operator Confirmation Flow

The v2→v3 migration follows the same confirmation pattern as v1→v2:
confirm before each step, present before/after, stop on error. The
migration is shorter (1 required step vs 3) but uses the same safety
conventions.

### F3: v1→v3 strategy

**Confidence: High** — validated against the existing v1→v2 code path.

**Recommendation: Option A — Sequential composition.**

Run v1→v2 (existing logic, unchanged), then v2→v3 (new logic) in
sequence within a single `sdd-migrate` invocation.

**Rationale:**

1. The v1→v2 migration is already tested and verified (RS-001 cycle,
   rubric M1 migration, verification report 2026-04-28).
2. The v2→v3 migration is lightweight (1 required step + advisory).
3. Composing them adds no complexity — the routing is already
   scaffolded in sdd-migrate's "Future Migrations" section:
   ```
   version missing  → run v1→v2, then offer v2→v3
   version == 2     → offer v2→v3
   version == 3     → already current, exit
   ```
4. Option B (direct v1→v3) would duplicate v1→v2 logic with v3
   vocabulary applied — more code, more testing, for no benefit.
5. Option C (two separate invocations) is safe but unnecessary
   friction for the operator. The tool can compose transparently.

**Implementation detail:** After v1→v2 completes (writing `2` to
`.sdd-version`), the skill immediately proceeds to v2→v3 detection.
The intermediate state (`version == 2`) exists only briefly. The
finalization writes `3`, not `2`.

**Edge case:** If v1→v2 is interrupted, the operator re-runs
`sdd-migrate`. Idempotency means v1→v2 resumes from where it stopped,
then v2→v3 runs. The version marker is written last, so partial state
is detectable.

## Out-of-Scope Observations

1. **Traceability Implementation column gap.** The RS-002 verification
   report flagged 34 v2-era requirements with empty Implementation
   columns. A future cycle could backfill these, but it's not a
   migration concern — the work exists, the matrix is incomplete.

2. **v3 overview spec.** The current overview.md describes v2. If v3
   is formalized, overview.md should be updated to reflect the plan
   vocabulary convention and per-milestone file pattern. This is a
   spec update, not a migration task.

3. **`docs/plan-history/` vocabulary in archives.** Archived v2 plans
   may contain `### M N:` headers. These are historical records and
   should not be renamed. But a future reader might be confused by
   the vocabulary mismatch. A note in the migration summary ("archived
   plans retain their original vocabulary") would help.

4. **Version marker semantics.** The version marker currently means
   "artifact layout version." v3 doesn't change the layout — it adds
   behavioral conventions and one vocabulary change. Should the
   version track layout, conventions, or both? This is a design
   question for the specs phase, not a research finding.

## Recommendation

Proceed to `/sdd-requirements` to translate these findings into
requirements. The scope is narrow:

- **REQ-MIG-v3 requirements** for the v2→v3 migration steps (detection,
  vocabulary rename, optional split, finalization)
- **REQ-MIG-compose requirement** for v1→v3 sequential composition
- **Update REQ-MIG-002** to include v3 detection (version == 2 → offer v3,
  version == 3 → exit)
- **Update REQ-CFG-001** to note version 3 as a valid value

The implementation phase should be a single chunk: extend
`sdd-migrate/SKILL.md` with a `## v2 to v3 Migration` section and
update version detection routing. Estimated effort: ~2-3 hours.
