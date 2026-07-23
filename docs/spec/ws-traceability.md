---
status: Approved
last_updated: 2026-07-21
requires:
  - REQ-WS-007
  - REQ-WS-008
---

# Multi-Workstream Traceability Join

## Context

With requirements and specs shared (`ws-layout.md`) and execution artifacts
per-workstream, traceability is the only structure that records **which workstream
cares about which shared input** — the coverage/derivation join across
`REQ → SPEC → workstream → verification`. RS-007 Q1 empirically proved that a single
hand-appended shared traceability table conflicts on **every** concurrent append
(every workstream appends rows, all at the EOF boundary). So traceability must be
restructured so each workstream owns its own rows.

This spec resolves the requirements-stage carried-forward decision on the concrete
traceability shape (REQ-WS-008 offered two options) and pins how the join relates to
staleness. It covers REQ-WS-007 and REQ-WS-008.

## Design

### Decision: Separate Per-Workstream Files, Aggregated (REQ-WS-008)

**Adopted shape**: option (a) — each workstream owns a **separate file**
`docs/ws/<id>/traceability.md`; a shared `docs/requirements/traceability.md` is a
**derived aggregate** regenerated deterministically from all per-workstream files
(plus the pre-existing shipped rows). A workstream only ever edits its own
`docs/ws/<id>/traceability.md`.

**Rejected**: option (b) — delimited per-ws sections
(`<!-- ws:<id> -->…<!-- /ws:<id> -->`) inside the shared file. Within-section edits
merge cleanly (RS-007 S6), but **creating a brand-new section for a new workstream is
still an EOF-boundary edit** and two concurrent new-workstream creations conflict
(RS-007 S7). Separate files never conflict on creation (S8). Since opening a
workstream is exactly when a new section/file appears, the separate-file shape is the
one that survives concurrent workstream creation.

**Why aggregate at all**: the shared matrix stays useful as a single product-wide
view (the shipped `REQ-*` rows and every workstream's coverage in one place). Because
it is **derived**, it is never hand-merged — regeneration replaces it wholesale, so it
cannot merge-conflict (RS-007 S8).

### Per-Workstream File Shape

`docs/ws/<id>/traceability.md` — owned by workstream `<id>`, holds only that
workstream's rows:

```markdown
---
workstream: <id>
last_updated: YYYY-MM-DD
---

# Traceability — <id>

| Requirement | Spec | Workstream | Test | Implementation | Verified |
|-------------|------|------------|------|----------------|----------|
| REQ-AUTH-ISSUE42-001 | auth-login.md | ISSUE-42 | | | |
| REQ-AUTH-001         | auth-login.md | ISSUE-42 | | | |
```

- Rows record, for each shared REQ/SPEC the workstream delivers, the coverage through
  to that workstream's verification. Both **new ws-prefixed requirements** and
  **pre-existing shared requirements the workstream re-uses** may appear as rows owned
  by this workstream.
- The `Workstream` column is redundant with the file location but is retained so a row
  is self-describing once aggregated into the shared matrix.
- A workstream MUST NOT write rows into any other workstream's file or into the shared
  aggregate directly.

**Why a `Workstream` column added to the historical 5-column matrix**: the shipped
matrix is `| Requirement | Spec | Test | Implementation | Verified |`. Aggregating
per-ws rows into one view needs a workstream axis so rows from different files stay
attributable. The shipped rows (no workstream) aggregate under a `default` / blank
workstream value, preserving them unchanged.

**The `Workstream` column (the 3rd column) does not disturb the REQ-WS-012
unchanged-parsers guarantee**: traceability/requirements row parsing keys off the first
`Requirement` column (opaque-string / `REQ-*` prefix-glob, per `ws-ids.md`), so column
position is irrelevant — the parser is unaffected regardless of where the `Workstream`
column sits.

### Aggregation Contract

The shared `docs/requirements/traceability.md` is **regenerated**, not appended:

```
regenerate_shared_traceability():
    rows  = shipped legacy rows (workstream = blank/default)
    rows += concat( parse(docs/ws/<id>/traceability.md) for each <id> )
    sort rows by (Requirement id)          # deterministic order
    write docs/requirements/traceability.md   # wholesale replacement
```

- Regeneration is deterministic (stable sort by requirement id) so the output is
  reproducible and diffs are minimal.
- Because the shared file is replaced wholesale from owned inputs, two workstreams
  regenerating on their own branches never produce a git merge conflict on the
  per-ws inputs; if the derived aggregate itself is committed on both branches, it is
  re-derived on merge rather than hand-reconciled.
- The aggregate is a convenience view. It is **not** read by staleness (see below).

### Traceability Is the Recorded Join; Staleness Computes Live (REQ-WS-007)

Traceability is the **load-bearing recorded** join: for each workstream it records
which shared REQ and SPEC it depends on, through to its verification. This is the
coverage/derivation join that logically defines a workstream's shared-input set.

The staleness **computation**, however, MUST NOT read any traceability file. It
derives the same scoped set **live** by walking the workstream's plan
`task → spec requires: → requirement` chain (specified in `ws-staleness.md`,
REQ-WS-026). The two must coincide: the live plan-walk set equals the coverage set the
traceability join records for that workstream.

**Why compute live rather than read the join**: RS-007 Q2 chose Option A (compute-live,
no new traceability schema column) as lowest-cost — the existing milestone traversal
generalizes verbatim. Making staleness read traceability would couple it to the
aggregate file (a merge-risk artifact) and add a schema dependency for no benefit. The
recorded join documents coverage for humans and review; the live walk drives staleness.
Consequently no traceability **column** is added for staleness scope — the `Workstream`
column above exists only to attribute aggregated rows, not to feed staleness.

## Verification

### Automated
- Verify workstream tooling writes only `docs/ws/<id>/traceability.md` and never edits
  another workstream's file or the shared aggregate in place.
- Verify the aggregate regeneration is deterministic (same inputs → byte-identical
  output) and sorted by requirement id.
- Verify the staleness code path performs no read of any `traceability.md`.

### Manual
- Two concurrent workstreams each append their traceability rows to their own files;
  confirm the branches 3-way-merge with no conflict.
- Regenerate the shared matrix on each branch; confirm it is derived (no hand-merge)
  and merging re-derives rather than conflicts.
- For a workstream, confirm the shared REQ/SPEC set derived live by the plan-walk
  (per ws-staleness.md) coincides with the coverage set its traceability file records.

### Acceptance Criteria
- [ ] Traceability records, per workstream, the REQ→SPEC→workstream→verification
      coverage join (REQ-WS-007)
- [ ] Staleness scope is derived live by the plan-walk with NO traceability-file read,
      and coincides with the recorded coverage set (REQ-WS-007)
- [ ] Each workstream owns its rows via a separate `docs/ws/<id>/traceability.md`
      (REQ-WS-008)
- [ ] The shared matrix is a deterministically regenerated aggregate, never hand-merged
      (REQ-WS-008)
- [ ] A workstream only ever edits its own traceability rows (REQ-WS-008)
- [ ] Two concurrent workstreams' traceability additions 3-way-merge with no conflict
      (REQ-WS-008)
- [ ] Markdown well-formed; frontmatter valid

## Implementation Questions

### Q-IMPL-011: Which skills regenerate the shared aggregate, and when
**Tier**: 2 (spec ambiguity)
**Spec reference**: §Aggregation Contract ("regenerated … wholesale replacement")
**Decision**: Every skill that writes a per-ws traceability row under marker `4`
(`sdd-requirements` adding a new row, `sdd-specs` filling **Spec**, `sdd-implement`
filling **Test**/**Implementation** and at chunk-close Check 2, `sdd-verify` filling
**Verified**) regenerates `docs/requirements/traceability.md` **immediately after** its
per-ws write, using the `regenerate_shared_traceability()` contract (shipped legacy rows
+ concat of every `docs/ws/<id>/traceability.md`, stable-sorted by requirement id,
wholesale replacement). The spec pins the aggregate as derived/deterministic but does not
name a single regenerator; making each writer regenerate keeps the aggregate live after
every owned-row change while remaining conflict-free (each branch only edits its own per-ws
file; the aggregate re-derives on merge).
**Rationale**: A per-ws write leaves the aggregate stale until regenerated; co-locating
regeneration with each write is the least-surprising place and needs no separate trigger
skill. Marker `3` behavior is untouched — the single shared file is still written directly.

### Q-IMPL-012: sdd-requirements (a shared-corpus skill) writes into a per-ws file
**Tier**: 2 (spec ambiguity)
**Spec reference**: §Per-Workstream File Shape ("both new ws-prefixed requirements and
pre-existing shared requirements the workstream re-uses may appear as rows owned by this
workstream")
**Decision**: Under marker `4`, when `sdd-requirements` adds a new
`REQ-<DOMAIN>-<WS>-NNN`, the requirement **text** is added to the shared category file
(merge-safe, per `ws-ids.md`), but the traceability **row** is written into the active
workstream's OWN `docs/ws/<ws>/traceability.md` — not the shared aggregate — then the
aggregate is regenerated. This keeps the "a workstream only ever edits its own rows"
invariant even though requirements themselves are shared.
**Rationale**: The row records *which workstream delivers* the REQ, which is
workstream-owned state; only the requirement definition is shared. Splitting text (shared,
merge-safe append) from row (per-ws owned) satisfies both REQ-WS-004 (shared corpus) and
REQ-WS-008 (per-ws-owned rows) without a shared write point.
