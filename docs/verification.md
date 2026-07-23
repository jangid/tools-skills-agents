---
date: 2026-07-23
status: pass
plan_ref: docs/plan.md
scope: Multi-Workstream SDD (v4) — REQ-WS-001..029, specs ws-layout/ws-ids/ws-traceability/ws-staleness/ws-integration/ws-migration/ws-orchestration, the ten sdd-* skills + fan-out.md, overview.md, CLAUDE.md
---

# Verification Report

## Summary

**PASS.** The Multi-Workstream SDD (v4) feature is verified holistically: all nine
plan chunks (0–8) are CLOSED with every task complete, all 29 REQ-WS acceptance
criteria are met (high-value merge/isolation/migration/integration behaviors backed
by throwaway git-fixture evidence, the rest by contract inspection), the ten
`sdd-*` skills + `fan-out.md` + `overview.md` + `CLAUDE.md` present one consistent v4
contract, and the `main..HEAD` diff contains only the intended feature. The
**critical v3-solo-safety gate PASSES**: this repo remains at `.sdd-version = 3`, has
no `docs/ws/`, and every skill gates the entire v4 behavior behind a "marker not `4`
⇒ behavior UNCHANGED" branch — so nothing about the live marker-3 solo cycle changes.
No critical or minor issues found. Recommend ship-as-is.

## Quality Gates

This is a docs/skills meta-feature (no compiled code — the "code" is the skills'
described algorithms), so the gates are markdown well-formedness, frontmatter
validity, and behavioral fixtures rather than compilers/unit tests.

| Gate | Status | Notes |
|------|--------|-------|
| Frontmatter (7 new specs) | pass | each `docs/spec/ws-*.md` opens with `---` |
| Frontmatter (10 skills) | pass | all `skills/sdd-*/SKILL.md` retain valid `---` name/description block |
| Markdown well-formed | pass | plan/specs/requirements/overview/CLAUDE parse; tables one-row-per-line |
| Plan completeness | pass | chunks 0–8 all `Status: CLOSED`; only `[ ]` occurrences are literal prose ("preserving `[x]`/`[ ]`"), no open tasks |
| Behavioral fixtures | pass | 4 throwaway git fixtures (merge-safety, owned-files, migration, regression base) all behaved as specified; see below |
| Repo cleanliness | pass | live tree clean; no fixtures leaked (`$TMPDIR` swept, 0 remaining) |

## Acceptance Criteria

### ws-layout.md (REQ-WS-001..006, 019, 020)

| Criterion | Status | Evidence |
|-----------|--------|----------|
| v4 per-ws execution layout; shared corpus stays top-level (001) | pass | Shared-vs-owned table in ws-layout.md; every skill step-0 roots execution artifacts at `docs/ws/<ws>/`, corpus at `docs/{research,requirements,spec}/` |
| Branch-per-issue isolation (002) | pass | ws-integration.md + fan-out.md §0: workstream = its own branch, isolation via git + `docs/ws/<id>/` |
| Phase detection is fn(repo, workstream) (003) | pass | All 10 skills carry a marker-`4` step-0 branch taking a `workstream` arg defaulting to `default` |
| Requirements/specs single shared corpus; no per-ws fork (004) | pass | ws-layout.md forbids `docs/ws/<id>/requirements|spec/`; skills ADD new IDs/files only |
| Workstream references a shared subset via traceability (005) | pass | ws-layout.md + ws-traceability.md: reference model, no ownership marker on requirement text |
| Workstream owns only its execution artifacts (006) | pass | Owned set = kickoff/plan/plan-history/verification/per-ws traceability; plan archive & verify are per-ws |
| Approval is a per-ws bare status flag (019) | pass | Owned plan/verification carry own `status`; shared requirements/specs one product-wide status; no approver/quorum |
| Solo = implicit ceremony-free `default` ws (020) | pass | `workstream` defaults to `default` throughout; omitting it needs no naming |

### ws-ids.md (REQ-WS-009..015)

| Criterion | Status | Evidence |
|-----------|--------|----------|
| IDs carry ws segment, NNN parsed after WS (009) | pass | `RS-<WS>-NNN`, `Q-IMPL-<WS>-NNN`, `REQ-<DOMAIN>-<WS>-NNN` consistent across sdd-research/implement/requirements/migrate + ws-ids.md + overview.md |
| New reqs append under claimed prefix; new specs new files; no shared-body rewrite (010) | pass | sdd-requirements/specs prose; ws-ids.md write model |
| Per-ws (per domain+ws) counters replace global scan (011) | pass | ws-ids.md generator table; four generators scope max-scan per workstream |
| Exactly 4 generators + sdd-review string change; parsers untouched (012) | pass | sdd-review accepts `<WS>` as opaque/prefix-glob (lines 100-103, 145-146); Chunk-N and Q-*/row parsers unchanged |
| Shared-table writes sorted-insertion/owned, no EOF append (013) | pass | **Fixture A**: distinct-prefix sorted insertion 3-way merges CLEAN; adjacent EOF append CONFLICTS |
| Clean index merge conditional on distinct prefixes; same-domain = human PR conflict (014) | pass | **Fixture A/A2** demonstrates the distinct-vs-adjacent divide; tooling does not auto-union |
| index.md ID-sorted one-row-per-line insertion (015) | pass | Fixture A rows inserted at sorted position, one per line |

### ws-traceability.md (REQ-WS-007, 008)

| Criterion | Status | Evidence |
|-----------|--------|----------|
| Traceability is recorded join; staleness computes live (no file read) (007) | pass | ws-traceability.md + ws-staleness.md: live plan-walk `task → spec requires: → requirement`, no traceability read; sets coincide |
| Per-ws-owned rows, merge-safe; aggregate regenerated not hand-merged (008) | pass | **Fixture B**: two ws own separate `docs/ws/<id>/traceability.md` files → merge CLEAN; aggregation contract is wholesale regenerate + stable sort by req id; `Workstream` = 3rd column of 6-col matrix, consistent in sdd-implement/sdd-verify |

### ws-staleness.md (REQ-WS-026..028)

| Criterion | Status | Evidence |
|-----------|--------|----------|
| Milestone→workstream scope by swapping plan path + key; chain unchanged (026) | pass | sdd-implement/sdd-plan/sdd-replan marker-`4` branch: `docs/plan.md`→`docs/ws/<ws>/plan.md`, milestone key→ws key, chain identical, no traceability read/column |
| sdd-verify gains ws-scoped branch on traced inputs only (027) | pass | sdd-verify.md L52 marker-`4` branch compares ws plan/verification only vs traced shared inputs |
| sdd-specs stops treating flat plan as monolith (defers to sdd-plan) (027) | pass | ws-staleness.md adopts deferral; sdd-specs checks only requirements→spec staleness |
| research→requirements staleness stays shared/ws-independent (028) | pass | sdd-requirements.md L58: same under marker 3 and 4, no ws key; only research ID pattern may change |

### ws-integration.md (REQ-WS-016..018)

| Criterion | Status | Evidence |
|-----------|--------|----------|
| Branch-per-ws → PR to main; concurrent open PRs (016) | pass | ws-integration.md; fan-out.md §0 |
| Fan-out worktrees branch from ws branch, merge back; no exclusive main (017) | pass | fan-out.md §0/§3a-c: base = ws branch HEAD, merge back into ws branch |
| main-ownership "conflict = boundary error" inference removed (017) | pass | fan-out.md §3c: inference explicitly REMOVED |
| sdd-verify regression base = ws branch point, not main (018) | pass | **Fixture D**: `merge-base(ISSUE-42,main)` == branch point; diff vs merge-base shows only ISSUE-42's delta while diff vs main HEAD falsely folds in unrelated ISSUE-57 |
| Verification independent of other ws merged to main meanwhile (018) | pass | Fixture D: merging unrelated ISSUE-57 to main does not affect ISSUE-42's branch-point diff |

### ws-migration.md (REQ-WS-021..023)

| Criterion | Status | Evidence |
|-----------|--------|----------|
| sdd-migrate gains v3→v4 step; flat exec artifacts → docs/ws/default/, corpus in place, marker→4 (021) | pass | sdd-migrate.md v3→v4 arm; version-routing extension |
| Copy-verify-flip-cleanup, marker written last, idempotent, interrupt-safe (022) | pass | **Fixture C**: copy byte-identical (`[x]`/`[ ]` + pass verdict verbatim); interrupt-before-flip leaves working v3 (marker 3, flat intact); after flip+cleanup marker 4, flat gone, ws/default present; cleanup re-run idempotent |
| .sdd-version is sole layout gate; v3 never reads ws/, v4 never reads flat (023) | pass | ws-migration.md gate table; "sole gate" phrasing in all 9 step-0 skills + overview.md |

### ws-orchestration.md (REQ-WS-024, 025, 029)

| Criterion | Status | Evidence |
|-----------|--------|----------|
| Workstream picker (id, description from kickoff.md, phase) select-or-create (029) | pass | sdd-orchestrate.md marker-`4` branch enumerates `docs/ws/<id>/`, reads kickoff description + detected phase |
| done-vs-new-cycle resolved per workstream, not global intent (029) | pass | ws-orchestration.md: DONE read from per-ws `verification.md`; new cycle overwrites that ws's kickoff |
| Every new ws begins at research; no mid-pipeline entry variant (024) | pass | sdd-orchestrate positions new ws at research |
| Research early-exits fast when corpus already covers (025) | pass | sdd-research recorded early-exit path distinct from full spike |

## User-Perspective Validation

| Scenario | Status | Notes |
|----------|--------|-------|
| Two concurrent workstreams (ISSUE-42 impl, ISSUE-57 plan) | pass | Separate `docs/ws/<id>/` execution trees, independent per-ws ID counters, per-ws staleness scope, per-ws-owned traceability files that 3-way-merge clean (Fixture B), branch-point regression base independent of the other's merges (Fixture D). Concurrency is structural, not conventional. |
| Solo operator, unchanged experience | pass | Live repo at marker 3 behaves byte-for-byte as before (v3 path untouched). Under a future marker 4, the implicit `default` workstream needs no naming; all artifacts land under `docs/ws/default/`. |
| Concurrent requirement additions merge | pass | Distinct claimed domain prefixes → clean 3-way merge (Fixture A); same-domain surfaces an honest human PR conflict, no silent union (accepted degradation per REQ-WS-014). |
| Migration adoption path | pass | Copy-verify-flip-cleanup is interrupt-safe at every step (Fixture C): before flip = working v3, after flip = working v4, cleanup idempotent. |
| Error/edge honesty | pass | Same-domain concurrency and in-place shared-edit conflicts are deliberately left as human PR conflicts rather than mis-auto-merged — the design surfaces them instead of hiding them. |

## Regressions

- **None.** `git diff --name-status main..HEAD` (base = `03268f2`, the current `main`
  HEAD and the branch's merge-base) contains only in-scope changes: the ten
  `skills/sdd-*` skill bodies + `fan-out.md` (v4 gating), the 7 new `docs/spec/ws-*.md`,
  `docs/requirements/functional/multi-workstream.md`, `docs/spec/overview.md` (v4),
  `CLAUDE.md` (v4 section), and bookkeeping (`requirements/index.md`,
  `requirements/traceability.md`, `research/index.md` + RS-007 research, `plan.md`,
  `plan-history/` archive, the superpowers design doc, `docs/handoff/kickoff.md`).
  No out-of-scope or unrelated file touched. No source code exists to regress.
- **v3-solo-safety (critical gate): no regression.** `.sdd-version` is still `3`,
  `docs/ws/` is absent, and all ten skills gate the v4 layout behind "marker not `4`
  ⇒ UNCHANGED". CLAUDE.md explicitly states "Both markers are supported; this repo
  currently runs at marker `3`." The feature is inert on the live marker-3 cycle.

## Issues Found

### Critical (blocks release)
- None.

### Minor (can ship, fix later)
- None. (Observation, not a defect: `sdd-review` shows the lowest ws/marker-4 mention
  count of the ten skills — expected, since its only required change per REQ-WS-012 is
  the convention string accepting the `<WS>` segment; verified present and correct.)

## Assumptions

- Treated this as a prose/algorithm meta-feature: "run the code" is inapplicable, so
  behavioral verification used throwaway git fixtures to reconfirm the empirical
  merge/migration/integration claims (which RS-007 originally established) plus
  contract inspection across skills/specs/overview/CLAUDE for the layout, ID,
  staleness, approval, and orchestration prose. Default: fixtures for empirical
  behaviors, inspection for contract-shape behaviors.
- Verification ran under marker `3` by design and did **not** flip `.sdd-version`; the
  marker-`4` behaviors were validated via fixtures and prose rather than by mutating
  the live repo's layout.

## Recommendation
- [x] Ship as-is
- [ ] Fix critical issues then ship (invoke sdd-replan)
- [ ] Significant rework needed (invoke sdd-replan)

The active `docs/plan.md` may now be archived to `docs/plan-history/` if desired.
