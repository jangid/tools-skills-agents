# Kickoff: RS-007 — Multi-workstream SDD (teams, many concurrent issues)

Run `/sdd-research`. This spike de-risks reshaping the nine `sdd-*` skills so a
**team can run several SDD cycles concurrently** in one repo — each on its own
branch/issue — without artifact collisions, false staleness, ID races, or
cross-workstream phase confusion. Its findings must land before requirements/specs
for the multi-workstream feature.

Driven by `sdd-orchestrate` (dogfooding). Cycle: this research spike → then
requirements → specs → plan → implement → verify for the multi-workstream feature.

Converged design (approved, in DISCUSS):
`docs/superpowers/specs/2026-07-21-multi-workstream-sdd-design.md`. That doc holds
the full decision set — read it first; the questions below only de-risk the parts
still uncertain.

## Design in one paragraph (context for the spike)

Requirements and specs stay a **single shared product corpus**
(`docs/requirements/`, `docs/spec/`). Only **execution** artifacts become
per-workstream under `docs/ws/<id>/` (`kickoff.md`, `plan.md`,
`verification.md`). A **workstream is an execution unit** that references a subset
of the shared corpus via **traceability** (`REQ → SPEC → workstream →
verification`). IDs are **workstream-prefixed** (`RS-ISSUE42-001`,
`Q-IMPL-ISSUE42-003`); new requirements append under a claimed domain prefix; new
specs are new files. Shared-corpus writes are **append-mostly** so concurrent
branches 3-way-merge cleanly. Integration is **branch-per-ws → PR to `main`**;
fan-out worktrees branch from the ws branch, not `main`. `sdd-migrate` gains a
**v3→v4** step; solo use runs in an implicit `default` workstream. Phase detection
becomes a function of `(repo, workstream)`.

## Research questions

1. **Append-only merge reality** — Does append-mostly + git 3-way merge actually
   stay clean for the shared table artifacts (`docs/requirements/index.md`,
   `docs/traceability.md`) when two workstreams append rows concurrently? Prove
   with a real spike: two branches each appending distinct rows to the same table
   file, then merge — does it auto-merge, or conflict on adjacent lines? If it
   conflicts, what table/row structure (e.g. one-row-per-line, trailing sentinel,
   sorted-by-id) merges cleanly?

2. **Staleness generalization** — Can the existing milestone-scoped staleness
   machinery (`task → spec → requires: → requirement IDs → category-file dates`,
   REQ-STALE-003) be generalized to **workstream-scoped** staleness — a ws plan is
   stale only if the specific shared specs/requirements *it traces* changed — or is
   new traversal logic required? Identify exactly which skills' step-0 checks
   change and how.

3. **Migration safety (v3→v4)** — Can `sdd-migrate` move flat `docs/plan.md` and
   `docs/verification.md` into `docs/ws/default/`, and leave `requirements/`,
   `spec/`, `research/`, `traceability.md` as the shared corpus, **without any
   skill misdetecting phase mid-migration** (the interrupted-migration invariant)?
   What is the safe step order, and what does `.sdd-version` gate?

4. **ID-format blast radius** — Does the workstream-prefixed ID format
   (`RS-ISSUE42-NNN`, `Q-IMPL-ISSUE42-NNN`) break any existing parser? Concretely
   check: fan-out's `**Depends on**: Chunk N` derivation, traceability row
   parsing, `sdd-review`'s Q-REQ / Q-IMPL checks, and any regex that assumes
   `RS-\d+` or `Q-IMPL-\d+`. List each parser touched and whether the format needs
   adjusting.

## Success criteria

Each question has an evidence-based finding (proven with a real git spike where
feasible — especially Q1) and a concrete recommendation. Enough certainty to write
requirements for the multi-workstream feature without guessing: the merge-safe
table structure (Q1), the staleness-scoping mechanism (Q2), the migration step
order (Q3), and the exact parser changes the ID format forces (Q4).

## Budget

~1.5 hours. Prototype Q1 first (the riskiest and most empirical — real concurrent
merges of table artifacts). Q2–Q4 are largely analysis over existing skill files;
time-box each to ~20 min. A messy result on Q1 is not a blocker — it selects a
merge-safe row structure, which becomes a requirement.

## Downstream feature scope (informs requirements after the spike)

- **In scope**: per-workstream execution artifacts under `docs/ws/<id>/`;
  workstream-aware phase detection & staleness scoping; workstream-prefixed IDs;
  append-only shared req/spec/research writes; the `sdd-orchestrate` entry picker
  (list workstreams → select/create); the v3→v4 migration; the branch-per-ws → PR
  integration model with fan-out branching from the ws branch; doc updates to
  `CLAUDE.md`.
- **Out of scope**: approver identity / quorum (approval stays a bare per-ws
  status flag); any locking daemon or server (git is the coordination substrate);
  dual-layout support forever (migrate once, then v4 only); automating merges of
  modifications to *existing* shared requirements (append-only sidesteps it;
  same-requirement edits stay a human PR conflict).

## Out of scope (for the spike)

Writing the feature; modifying any `sdd-*` skill; requirements/specs (later stages
of this cycle).
