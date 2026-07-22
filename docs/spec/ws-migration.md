---
status: Approved
last_updated: 2026-07-21
requires:
  - REQ-WS-021
  - REQ-WS-022
  - REQ-WS-023
---

# v3 → v4 Migration

## Context

v4 relocates flat execution artifacts under `docs/ws/default/` while leaving the
requirements/spec/research/traceability corpus shared (`ws-layout.md`). Existing v3
repos adopt v4 through a one-time `sdd-migrate` step. RS-007 Q3 established the safe
step order: because a v3 skill invoked while the marker still reads `3` must still find
the flat files, the flat layout must stay valid across the whole `3` window — so the
migration **copies** (not moves) and writes the version marker **last**.

This spec extends the existing `sdd-migrate` design (`migration.md`) with the v3→v4
step and resolves the requirements-stage carried-forward decision on `kickoff.md`
placement (REQ-WS-021). It covers REQ-WS-021..023.

## Design

### `.sdd-version` Is the Sole Layout Gate (REQ-WS-023)

`docs/.sdd-version` is the single switch selecting which layout every skill's step-0
reads:

| Marker | Authoritative execution layout |
|--------|-------------------------------|
| `3` | flat: `docs/plan.md`, `docs/verification.md`, `docs/plan-history/`, flat `docs/handoff/kickoff.md` |
| `4` | per-workstream: `docs/ws/<id>/{kickoff,plan,verification}.md`, `docs/ws/<id>/plan-history/`, default ws `default`; `requirements/`, `spec/`, `research/`, traceability shared |

- A v3 skill must **never** read `docs/ws/`.
- A v4 skill must **never** read flat execution paths.
- A v4-aware skill invoked while the marker still reads `3` sees "not yet migrated" and
  suggests `sdd-migrate` (existing behavior).

**Why one marker gates the layout**: a single switch guarantees no skill misdetects
phase during or after migration — the on-disk layout and the marker are only ever read
together.

### Version-Routing Extension

`sdd-migrate`'s version routing (see `migration.md` § Version Routing) gains a `3`→`4`
arm:

```
elif version == 3:
    migrate_v3_to_v4()      # this spec
elif version == 4:
    inform("already at v4, nothing to do")
```

For missing/`2` markers, the existing v1→v2→v3 chain runs first, then v3→v4 composes on
the end (the marker is written `4` last, once).

### Decision: kickoff.md Absorbed Per-Workstream; No Flat `docs/handoff/` in v4 (REQ-WS-021)

**Adopted**: `kickoff.md` lives at `docs/ws/<id>/kickoff.md` (per-workstream). The flat
`docs/handoff/` directory is **NOT retained** in v4 — the v3→v4 migration moves a flat
`docs/handoff/kickoff.md` (if present) to `docs/ws/default/kickoff.md`.

**Rationale**: kickoff is a workstream-scoped handoff (it seeds one cycle), so it
belongs with the other workstream-owned execution artifacts under `docs/ws/<id>/`.
Retaining a flat `docs/handoff/` would reintroduce a repo-global singleton — exactly the
collision the v4 layout removes — and split kickoff state across two locations. A single
per-workstream home keeps phase detection uniform: `sdd-orchestrate`'s picker and every
skill's step-0 read `docs/ws/<id>/kickoff.md`, never a flat path (see `ws-orchestration.md`).

**Phase-detection & orchestrate impact**: `sdd-orchestrate` reads each workstream's
description/phase from `docs/ws/<id>/kickoff.md` (REQ-WS-029). No skill reads
`docs/handoff/` under marker `4`.

### v3 → v4 Migration: Copy-Verify-Flip-Cleanup (REQ-WS-021, REQ-WS-022)

The migration **copies** execution artifacts into `docs/ws/default/`, **verifies** them
byte-identical, writes the marker **last**, then deletes the flat originals as
idempotent cleanup.

**Safe step order**:

1. **Precondition**: `docs/.sdd-version` == `3`. Create `docs/ws/default/` and
   `docs/ws/default/plan-history/`.
2. **Copy** (not move), preserving content verbatim:
   - `docs/plan.md` → `docs/ws/default/plan.md`
   - `docs/verification.md` → `docs/ws/default/verification.md`
   - `docs/plan-history/*` → `docs/ws/default/plan-history/`
   - `docs/handoff/kickoff.md` (if present) → `docs/ws/default/kickoff.md`
   Preserve task `[x]`/`[ ]` status and pass/fail verdicts **verbatim**.
3. **Verify** each copy is **byte-identical** to its source.
4. Leave the shared corpus in place — `docs/requirements/`, `docs/spec/`,
   `docs/research/`, `docs/requirements/traceability.md` are NOT moved.
5. **Write `docs/.sdd-version` = `4`** — the single atomic layout flip, written **LAST**.
6. **Cleanup** (idempotent): delete the now-orphaned flat `docs/plan.md`,
   `docs/verification.md`, `docs/plan-history/`, and flat `docs/handoff/kickoff.md`
   (and the empty `docs/handoff/`).

**Interrupted-migration invariant (REQ-WS-022)**:

- Interrupted **before** the flip (step 5): the marker still reads `3`, the flat files
  are intact → a working v3 repo. Re-running restarts copy-verify (copy is idempotent).
- Interrupted **after** the flip: the marker reads `4`, v4 skills already ignore the
  flat paths → a working v4 repo. Re-running detects marker `4` and re-does cleanup
  idempotently.

**Why copy-then-delete rather than move** (the one deviation from prior move-based
migrations): while the marker still reads `3`, v3 skills must still find the flat files,
so the flat layout must remain valid for the entire `3` window. Duplicates under
`docs/ws/default/` are invisible to v3 skills. Moving would break the flat layout the
instant it ran, before the marker flips — violating the "version marker written last"
invariant that makes interrupted migrations safe.

## Deferred work

**`docs/spec/overview.md` must be updated to v4 during the implement phase** — recorded
here so `sdd-plan` emits an explicit overview.md-update task rather than silently
carrying the v2/v3 contradiction forward. Two edits are deferred:

- **§Version Marker** — add `4` as a valid version-marker value (the section currently
  lists only `2` and `3`, contradicted by v4 / REQ-WS-023).
- **§ID Namespaces** — add the `<WS>` workstream segment to the RS / REQ / Q-IMPL ID
  formats (the section currently documents the un-prefixed v2 formats, superseded by
  `ws-ids.md` / REQ-WS-009).

This is a deliberate deferral: `overview.md` is Approved and is not edited in the specs
pass, but the update is mandatory before v4 ships. `sdd-plan` MUST pick this note up and
emit a dedicated `overview.md`-update implement task.

## Verification

### Automated
- Verify `sdd-migrate` routes `version == 3` to the v3→v4 step and `version == 4` to a
  clean exit.
- Verify the v3→v4 step copies (does not move) before the flip, verifies byte-identity,
  writes the marker last, and deletes flat originals only after the flip.
- Verify no v4 skill reads flat execution paths and no v3 skill reads `docs/ws/`.

### Manual
- Run v3→v4 on a v3 repo; confirm `docs/ws/default/` holds the former flat artifacts,
  `.sdd-version` == `4`, and no flat `docs/plan.md` / `docs/verification.md` /
  `docs/handoff/` remain.
- Interrupt before the flip; confirm a working v3 repo (flat files intact, marker `3`)
  and that re-running completes.
- Interrupt after the flip; confirm a working v4 repo and that re-running completes
  cleanup idempotently.
- Confirm task `[x]`/`[ ]` status and pass/fail verdicts are preserved verbatim in the
  copied artifacts.

### Acceptance Criteria
- [ ] `sdd-migrate` gains a v3→v4 step moving flat execution artifacts (plan,
      verification, plan-history, flat kickoff if present) into `docs/ws/default/`,
      leaving the shared corpus in place, and setting `.sdd-version` = `4` (REQ-WS-021)
- [ ] kickoff.md is absorbed to `docs/ws/<id>/kickoff.md`; flat `docs/handoff/` is not
      retained in v4 (REQ-WS-021)
- [ ] Migration is copy-verify-flip-cleanup: copy (not move), verify byte-identical,
      write marker last, delete flat originals as idempotent cleanup (REQ-WS-022)
- [ ] Task status and pass/fail verdicts preserved verbatim (REQ-WS-022)
- [ ] Interrupt before flip → working v3 repo; interrupt after flip → working v4 repo;
      re-run is safe (REQ-WS-022)
- [ ] `.sdd-version` is the sole layout gate: `3` = flat authoritative, `4` =
      per-workstream authoritative; v3 skills never read `ws/`, v4 skills never read
      flat paths (REQ-WS-023)
- [ ] Markdown well-formed; frontmatter valid
