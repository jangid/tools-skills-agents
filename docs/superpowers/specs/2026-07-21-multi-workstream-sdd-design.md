# Design: Multi-Workstream SDD (teams, many concurrent issues)

**Date:** 2026-07-21
**Status:** Approved (brainstorming) — feeds the research kickoff for this cycle
**Author:** converged with operator via `sdd-orchestrate` DISCUSS

## Problem

Every SDD skill assumes **one operator working one feature at a time**. All
artifacts except `docs/research/RS-*/` live at **fixed, feature-independent
paths** (`docs/plan.md`, `docs/verification.md`, `docs/requirements/index.md`,
`docs/handoff/kickoff.md`, `docs/traceability.md`). "The current phase" is a pure
function of the shared repo. IDs are allocated by "scan the tree, take max, +1."
Staleness is broadcast globally from one `requirements/index.md` clock.

The consequence, already visible in this repo: `docs/verification.md` coexists
with hand-suffixed `verification-rs002.md`, `-rs004.md`, `-rs005.md`,
`-rs006-fanout.md` — a manual workaround for the singleton path, under merely
*sequential* single-person use. No skill reads those suffixed files.

Under real multi-person / multi-issue use the failures are hard:

- Concurrent planning **archives and overwrites** an in-flight `plan.md`
  (`sdd-plan` Step 7), so one person's `sdd-implement` resumes against another's
  tasks.
- One global `verification.md` pass/fail routes *unrelated* sessions into
  `sdd-replan`.
- Any edit to `requirements/index.md` bumps its clock, marking **every**
  downstream artifact of **every** workstream stale — and skills respond by
  *rewriting*, not warning.
- Scan-and-increment ID allocation races across `RS-NNN`, `REQ-{DOMAIN}-NNN`,
  `Q-IMPL-NNN`.
- `sdd-orchestrate` resolves its done-vs-new-cycle ambiguity by appealing to a
  *single operator's intent* — undefined when two operators share the repo.

## Goal

Let a team run several SDD cycles concurrently in one repo, each on its own
branch/issue, without artifact collisions, false staleness, ID races, or
cross-workstream phase confusion — while keeping requirements and specs as a
single shared product corpus, and keeping solo use ceremony-free.

## Decisions (from DISCUSS)

1. **Isolation boundary: branch-per-issue, `docs/` scoped by workstream.** Each
   issue is a branch; execution artifacts move under `docs/ws/<id>/`. Concurrency
   becomes structural (git handles it), not conventional (discipline).
2. **Requirements and specs are a single COMMON corpus.** Not per-workstream.
   One product requirement set, one product spec set. New work *adds* to them; it
   never forks them. A **workstream is an execution unit**, not a copy of the docs.
3. **A workstream owns only execution:** `kickoff.md`, `plan.md`,
   `verification.md`. It *references* a subset of the shared req/spec through
   traceability.
4. **Traceability is the load-bearing join:** `REQ → SPEC → workstream →
   verification`. It records which shared req/specs each workstream depends on,
   which also scopes that workstream's staleness.
5. **IDs are workstream-prefixed** so concurrent allocation cannot collide:
   `RS-ISSUE42-001`, `Q-IMPL-ISSUE42-003`. New requirements append under a
   **claimed domain prefix** (`AUTH → ISSUE-42`); requirement text stays
   product-wide. New specs are **new files**, never edits to existing ones.
6. **Shared-corpus writes are append-mostly** (new files, appended rows) so two
   concurrent workstreams 3-way-merge cleanly. Modifying an *existing* shared
   requirement remains a human PR-conflict to resolve — not automated (YAGNI).
7. **Integration: branch-per-ws → PR to `main`.** Fan-out worktrees branch from
   **the workstream branch**, not `main`, and merge back to it. This removes the
   fan-out lifecycle's exclusive ownership of `main` and the false
   "conflict-after-re-derivation = boundary error" inference.
8. **Approval stays a bare `status` flag, scoped per-workstream.** No approver
   identity, no quorum (YAGNI).
9. **Compatibility: migrate once (v3→v4); solo = implicit `default` workstream.**
   `sdd-migrate` moves flat `plan.md`/`verification.md` into `ws/default/`. Solo
   use feels unchanged.
10. **Every new workstream starts at research** for uniformity. The research
    stage early-exits fast when the shared corpus already covers the work.

## Target layout (v4)

```
docs/
  .sdd-version                 # 4  (repo-global version — fine, it's a version)
  requirements/                # COMMON — one product requirement set
    index.md                   #   domain-prefix registry + ID claims (AUTH→ISSUE-42)
    functional/auth.md         #   REQ-AUTH-001..007  (product-wide text)
  spec/                        # COMMON — one product spec set
    auth.md                    #   product-wide design specs (new work = new file)
  research/
    index.md                   # COMMON — RS registry (workstream-prefixed rows)
    RS-ISSUE42-001-oauth/      #   findings, prototypes
  traceability.md              # COMMON — REQ → SPEC → workstream → verification
  ws/
    ISSUE-42/
      kickoff.md               # scope + description (shown in the picker)
      plan.md                  # THIS ws's ordered tasks / chunks / milestones
      plan-history/            # THIS ws's archives
      verification.md          # THIS ws's pass/fail
    ISSUE-57/
      ...
    default/                   # implicit workstream for solo / migrated repos
```

Phase becomes a function of **`(repo, workstream)`**, not `repo`. Every skill's
step-0 detection takes a workstream argument, defaulting to `default`.

## What changes, by file

| Skill / file | Change |
|---|---|
| **all 9 `sdd-*`** | Step-0 phase detection takes a **workstream arg** (default `default`); plan/verification read/write `ws/<id>/`, req/spec/research read/write shared paths |
| `sdd-orchestrate` | New **workstream picker** at entry (list existing ws + description + phase → select or create); per-ws kickoff & phase; fan-out branches from the ws branch not `main`; done-vs-new-cycle ambiguity resolved per-ws |
| `sdd-research` | ws-prefixed `RS-ISSUE42-NNN`; append rows to shared `research/index.md` |
| `sdd-requirements` | Writes to **shared** `requirements/`; append-only new IDs under a claimed prefix; status/clock product-wide but **staleness reads the per-ws-traced subset** |
| `sdd-specs` | New specs = **new files** in shared `spec/`; never rewrite existing; filename claimed in registry |
| `sdd-plan` | Writes `ws/<id>/plan.md`; **staleness scoped to the specs this ws traces** (generalize the existing milestone-scoping); no global archive-on-rewrite of other workstreams' plans |
| `sdd-implement` | `Q-IMPL-ISSUE42-NNN`; reads `ws/<id>/plan.md`; task cursor per-ws |
| `sdd-verify` | Writes `ws/<id>/verification.md`; regression diff base = the **ws branch point**, not `main` |
| `sdd-replan` | Operates on `ws/<id>/plan.md`; a ws's verify-fail no longer routes other workstreams into replan |
| `sdd-migrate` | New **v3→v4** migration; `.sdd-version` → 4 |
| `sdd-review` | Mostly intact (already input-driven, phase-agnostic); reviews scoped to a ws's artifacts |
| `CLAUDE.md` | Document the `ws/` + shared layout, the workstream lifecycle, updated phase-detection & staleness tables, updated commit/branch conventions |
| **traceability** | Load-bearing `REQ → SPEC → workstream → verification`; `sdd-implement`/`sdd-verify` append their ws's rows |

## In scope

Layout change; workstream-aware phase detection & staleness scoping; ws-prefixed
IDs; append-only shared writes; the entry picker; v3→v4 migration; the git/PR
integration model; documentation updates.

## Out of scope (YAGNI)

- Approver identity / quorum — approval stays a bare per-ws status flag.
- Any locking daemon or server — git is the coordination substrate.
- Dual-layout support forever — migrate once (v3→v4), then v4 only.
- Automating merges of **modifications to existing** shared requirements —
  append-only sidesteps the common case; same-requirement edits stay a human PR
  conflict.

## Open questions for the research stage

1. **Append-only merge reality.** Does append-only + 3-way merge actually stay
   clean for `requirements/index.md` and `traceability.md` under two concurrent
   workstreams, or do table edits conflict in practice? (Spike: two branches,
   real merge.)
2. **Staleness generalization.** Does the existing `task → spec → requirement`
   trace machinery cover workstream-scoped staleness, or is new traversal needed?
3. **Migration safety.** Can v3→v4 move `plan.md`/`verification.md` into
   `ws/default/` without breaking any skill's phase detection mid-migration?
4. **ID-format blast radius.** Does the workstream-prefixed ID format break any
   existing parser — fan-out's `Depends on: Chunk N`, traceability row parsing,
   `sdd-review`'s Q-REQ checks?

## Success criteria

A team can open two issues, run two `sdd-orchestrate` sessions on two branches,
carry both through research→verify, and merge both to `main` via PR — with no
artifact collision, no false staleness, no ID race, and no cross-workstream phase
confusion. Solo use in the `default` workstream is unchanged in feel.
