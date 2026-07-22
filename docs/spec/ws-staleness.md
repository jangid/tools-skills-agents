---
status: Approved
last_updated: 2026-07-21
requires:
  - REQ-WS-026
  - REQ-WS-027
  - REQ-WS-028
---

# Workstream-Scoped Staleness

## Context

v3 staleness has a milestone-scoped traversal in `sdd-plan`, `sdd-implement`, and
`sdd-replan` (canonical in `milestone-plans.md` § Milestone-Scoped Staleness): read a
plan's tasks → each task's `traces to` spec → the spec's `requires:` requirement IDs →
compare dates against those specs and the category files. RS-007 Q2 showed this
traversal generalizes verbatim to a **workstream** key with no schema change, and
identified two skills — `sdd-specs` and `sdd-verify` — that today have **no** scoped
branch and need **new** per-workstream logic because specs are now shared and plans are
per-workstream.

This spec generalizes the traversal to workstream scope, adds the two new branches, and
pins that requirements-corpus staleness stays workstream-independent. It covers
REQ-WS-026..028.

## Design

### Generalize Milestone-Scoped Staleness to Workstream Scope (REQ-WS-026)

The existing traversal in `sdd-plan`, `sdd-implement`, and `sdd-replan` is generalized
by swapping two inputs and keeping the chain identical:

| Element | v3 (milestone-scoped) | v4 (workstream-scoped) |
|---------|----------------------|------------------------|
| plan path | `docs/plan.md` (or `docs/plan-{id}.md`) | `docs/ws/<id>/plan.md` |
| scope key | milestone | workstream |
| chain | `task → spec requires: → requirement IDs → category-file dates` | **unchanged** |

**Compute-live, no schema column** (RS-007 Q2 Option A): the scoped set of shared
inputs is derived **live** from the workstream's plan — walk its tasks' `traces to`
specs, collect each spec's `requires:` requirement IDs, and compare the plan's
`last_updated` against those specs' `last_updated` and against `requirements/index.md`
only if a collected requirement ID belongs to a category file updated more recently
than the plan. **No** traceability-file read; **no** new traceability schema column
(consistent with `ws-traceability.md`).

```
stale_inputs(<id>):
    plan = docs/ws/<id>/plan.md
    specs = { task.traces_to for task in plan.tasks }
    reqs  = ∪ { spec.requires for spec in specs }
    stale_specs = { s for s in specs if s.last_updated        > plan.last_updated }
    stale_reqs  = { r for r in reqs  if category_file(r).last_updated > plan.last_updated }
    return stale_specs ∪ stale_reqs
```

**Result**: `sdd-plan`/`sdd-implement`/`sdd-replan` in `ISSUE-42` scope staleness to the
specs/requirements `ISSUE-42`'s plan traces, ignoring updates to shared inputs no
`ISSUE-42` task references.

**Per-skill step-0 notes** (RS-007 Q2):
- **sdd-plan / sdd-implement**: the multi-milestone branch generalizes verbatim; the
  single-plan branch becomes the `default` workstream case.
- **sdd-implement**: the v3 caveat "the index-level `docs/plan.md` is not subject to
  this check" is dropped — there is no plan index in v4; workstreams are selected via
  the orchestrate picker (`ws-orchestration.md`), not a `plan.md` table.
- **sdd-replan**: references milestone-scoped staleness **by name only**, so re-pointing
  that reference at this workstream-scoped definition suffices; no new traversal.

**Why generalize rather than rewrite**: RS-007 Q2 showed the milestone traversal is the
same chain with a different scope key; reusing it keeps three skills' step-0 logic
identical in structure and avoids divergent staleness definitions.

### New Per-Workstream Staleness Branches for sdd-specs and sdd-verify (REQ-WS-027)

`sdd-specs` and `sdd-verify` have no scoped branch today and gain new per-workstream
logic, using the milestone traversal as the template:

- **sdd-verify**: gains a **new** workstream-scoped branch comparing a workstream's
  `docs/ws/<id>/plan.md` / `docs/ws/<id>/verification.md` **only** against the shared
  specs/requirements that workstream traces (via the same live plan-walk as REQ-WS-026).
  It must not report staleness from shared-input changes outside that workstream's
  traced set.
- **sdd-specs**: must **stop treating the flat plan as a monolith**. Under v4, specs are
  shared and there are N per-workstream plans, so `sdd-specs` no longer compares against
  a global `docs/plan.md`. It either **defers plan staleness to `sdd-plan`** (the
  recommended, lowest-cost resolution) or gains a per-workstream branch. This spec
  adopts **deferral**: `sdd-specs` checks only requirements→spec staleness (shared
  corpus) and leaves plan staleness to `sdd-plan`'s per-workstream branch.

**Why these two need new logic**: RS-007 Q2 identified them as the only skills whose
staleness assumptions break under v4 — specs became shared (so a per-spec vs. global
plan comparison is meaningless) and plans became per-workstream (so verify must scope to
one workstream's traced set). The other three already had a scoped branch to generalize.

### Requirements-Corpus Staleness Stays Workstream-Independent (REQ-WS-028)

The research→requirements staleness check (REQ-STALE-002) remains on the **shared
corpus** and is **NOT** scoped by workstream. Only the research ID pattern changes if
research becomes workstream-prefixed (`RS-<WS>-NNN`, per `ws-ids.md`).

**Why keep it shared**: requirements are a product-wide corpus, so "did research change
under requirements" is a product-level question, not a per-workstream one. Scoping it by
workstream would be incorrect — a shared requirement can be stale relative to shared
research regardless of which workstream is active.

## Verification

### Automated
- Verify `sdd-plan`/`sdd-implement`/`sdd-replan` staleness reads `docs/ws/<id>/plan.md`
  and scopes by workstream key, with the `task → spec requires: → requirement →
  category-file dates` chain unchanged and no traceability-file read.
- Verify `sdd-verify` has a workstream-scoped branch comparing only the workstream's
  traced shared inputs.
- Verify `sdd-specs` no longer compares against a global `docs/plan.md`.
- Verify `sdd-requirements` research→requirements staleness applies no workstream key.

### Manual
- Update a shared spec/requirement no `ISSUE-42` task traces; confirm `sdd-plan`/
  `sdd-implement`/`sdd-replan`/`sdd-verify` for `ISSUE-42` do not flag staleness.
- Update a shared input `ISSUE-42` does trace; confirm staleness is detected.
- Update shared research; confirm the shared requirements staleness check fires
  independent of any workstream.

### Acceptance Criteria
- [ ] Milestone-scoped staleness generalized to workstream scope in sdd-plan/
      sdd-implement/sdd-replan by swapping plan path and scope key; chain unchanged
      (REQ-WS-026)
- [ ] Staleness scope computed live from the workstream's plan, no new traceability
      column, no traceability-file read (REQ-WS-026)
- [ ] `sdd-verify` gains a workstream-scoped branch comparing only the workstream's
      traced shared inputs (REQ-WS-027)
- [ ] `sdd-specs` stops treating the flat plan as a monolith (defers plan staleness to
      sdd-plan) (REQ-WS-027)
- [ ] research→requirements staleness stays shared/workstream-independent; only the
      research ID pattern changes (REQ-WS-028)
- [ ] Markdown well-formed; frontmatter valid
