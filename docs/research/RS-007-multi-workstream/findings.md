---
id: RS-007
topic: multi-workstream
status: Complete
date: 2026-07-21
last_updated: 2026-07-21
questions:
  - "Q1: Does append-mostly + git 3-way merge stay clean for the shared table artifacts (requirements/index.md, traceability.md) when two workstreams append distinct rows concurrently? If it conflicts, what row/table structure merges cleanly?"
  - "Q2: Can the existing milestone-scoped staleness machinery (task -> spec -> requires: -> requirement IDs -> category-file dates, REQ-STALE-003) be generalized to workstream-scoped staleness, or is new traversal logic needed? Which skills' step-0 checks change and how?"
  - "Q3: Can sdd-migrate move flat docs/plan.md and docs/verification.md into docs/ws/default/ (leaving requirements/spec/research/traceability shared) without any skill misdetecting phase mid-migration? Safe step order and what .sdd-version gates?"
  - "Q4: Does the workstream-prefixed ID format (RS-ISSUE42-NNN, Q-IMPL-ISSUE42-NNN) break any existing parser? Which parsers are touched and must the format change?"
budget: "~1.5h; Q1 first (empirical git spike), Q2-Q4 ~20min each analysis"
research_refs: [RS-002, RS-003, RS-005, RS-006]
---

# Research: Multi-Workstream SDD (concurrent cycles in one repo)

## Questions

De-risk reshaping the nine `sdd-*` skills so a team can run several SDD cycles
concurrently in one repo (branch/issue per workstream), with requirements+specs a
shared corpus and execution artifacts per-workstream under `docs/ws/<id>/`. Four
front-loaded questions, below. Full design context:
`docs/superpowers/specs/2026-07-21-multi-workstream-sdd-design.md` and
`docs/handoff/kickoff.md`.

## Findings

### Q1 - Append-only merge reality (EMPIRICAL git spike)

**Answer**: Plain append to a shared markdown table does **NOT** 3-way-merge
cleanly under concurrency - it **conflicts**. Git conflicts whenever both
branches edit the *same location*, and "append to the end" is the same location
(the EOF boundary) for both branches, regardless of row content. Clean auto-merge
happens **only when the two insertions land at distinct positions separated by >=1
unchanged line**. Two structures are provably merge-safe: **sorted-by-ID
insertion when the new IDs sort into different regions**, and **per-workstream
owned regions / separate per-ws files**.

**Evidence** (7 scenarios, isolated throwaway repo; `merge-spike.md` shows the
literal command sequence and observed merge output for S1 — the CONFLICT proof —
and for the three CLEAN scenarios that justify the recommendations, S3/S6/S8.
The remaining CONFLICT cases S2/S4/S5/S7 follow deductively from the S1-proven
governing rule — position, not row content, determines the conflict — and are
summarized in the table below):

| Structure / edit | Result |
|---|---|
| Both append a distinct row at EOF | **CONFLICT** |
| Both insert a row at the same interior point | **CONFLICT** |
| Sorted-by-ID insertion, IDs sort to **distinct** regions (>=1 line apart) | **CLEAN** |
| Sorted-by-ID insertion, IDs sort **adjacent** | **CONFLICT** |
| Both insert immediately before a trailing sentinel line | **CONFLICT** |
| Each workstream edits **within its own delimited section** | **CLEAN** |
| Two new workstreams each append a **new section at EOF** | **CONFLICT** |
| **Separate per-workstream files** (shared file untouched) | **CLEAN** |

Key negative results: a trailing sentinel row does **not** rescue append (both
still target the same pre-sentinel point); appending a whole new per-ws *section*
at EOF still conflicts because it is still an EOF-boundary edit.

**Confidence**: High. Directly demonstrated with real `git merge` on the exact
table shapes used by `docs/requirements/index.md` and
`docs/requirements/traceability.md`.

**Recommendation** (becomes requirements):

1. **`traceability.md` (highest risk - every workstream appends rows):** do NOT
   keep it as a single hand-appended shared table. Make **each workstream own its
   traceability rows**, via either (a) a **per-ws file**
   (`docs/ws/<id>/traceability.md`) that a shared matrix aggregates/regenerates
   deterministically (S8 - trivially conflict-free, rebuild is derived so it never
   merge-conflicts), or (b) a **delimited per-ws section** in the shared file
   (`<!-- ws:<id> -->...<!-- /ws:<id> -->`) seeded at workstream-creation time so a
   workstream only ever edits inside its own block (S6 - clean). Prefer (a):
   section creation for a brand-new workstream still conflicts if two new
   workstreams do it concurrently (S7), whereas separate files never do.

2. **`requirements/index.md` Files table + new requirement rows within a category
   file:** use **one-row-per-line, ID-sorted (domain-grouped) insertion**, never
   raw EOF append. **Precondition (input assumption, not established by Q1):** the
   clean-merge guarantee here holds *only if each concurrent workstream owns a
   distinct claimed domain prefix* (e.g. AUTH->ISSUE-42), so their new IDs sort into
   *distinct, non-adjacent regions*. That distinct-prefix assignment comes from the
   design, not from this spike; Q1 only proves that *given* distinct sort regions the
   merge is clean (S3) and that *same/adjacent* regions conflict (S4). Under the
   precondition, concurrent workstreams append under different prefixes -> different
   regions -> **clean merge** (S3). The residual conflict case is two workstreams
   appending under the **same domain** concurrently (S4, i.e. the precondition does
   not hold) - that degrades to an ordinary human PR conflict, which the design
   already accepts (decision #6, "modifying an existing shared requirement stays a
   human PR conflict"). To keep the sort deterministic, insert into the correct
   sorted position rather than at EOF, and keep the table one row per line.

3. **General rule to encode:** "append-mostly" must mean **sorted insertion into
   distinct regions or per-workstream-owned regions**, NOT tail-append. State this
   explicitly so skills don't naively append at EOF.

### Q2 - Staleness generalization

**Answer**: The existing milestone-scoped traversal **generalizes directly** to
workstream-scoping for the 3 skills that already have a milestone-scoped branch
(`sdd-plan`, `sdd-implement`, `sdd-replan`) - swap the plan path
(`docs/plan-{id}.md` -> `docs/ws/<id>/plan.md`) and the "milestone" key for
"workstream"; the `task -> spec requires: -> requirement IDs -> category-file dates`
chain is unchanged. **New logic is required** for 2 skills (`sdd-specs`,
`sdd-verify`) that today have **no** scoped branch. `sdd-requirements` staleness
(research->requirements, REQ-STALE-002) is on the shared corpus and does **not**
scope by workstream.

**Evidence** (canonical definitions):
- REQ-STALE-003 canonical text: `docs/requirements/functional/staleness-detection.md:29-36`.
- Canonical traversal: `docs/spec/milestone-plans.md:148-158` - (1) read the plan's
  tasks; (2) each task's `traces to` -> spec file; (3) spec `requires:` frontmatter ->
  requirement IDs; (4) compare plan `last_updated` against each referenced spec's
  `last_updated` and against `index.md`'s `last_updated` *only if* a collected
  requirement ID belongs to a **category file updated more recently than the plan**.
  The anchor itself states the rule in terms of the "category file" date, not a named
  column; the concrete mechanism it resolves through — the `index.md` **Files table**
  and its **`Last Updated`** column — is specified in
  `docs/spec/requirements-artifacts.md:131,159` (Files-table schema and rationale)
  and instantiated at `docs/requirements/index.md:38`.

Per-skill step-0 impact:
- **sdd-plan** (`SKILL.md:22-24`): multi-milestone branch generalizes verbatim;
  single-milestone branch becomes the `default` workstream case. *No new traversal.*
- **sdd-implement** (`SKILL.md:23-24`): same generalization; the caveat "the
  index-level `docs/plan.md` is not subject to this check" must be restated -
  there is no plan index in v4 (workstreams are selected via the entry picker, not
  a plan.md table). *No new traversal.*
- **sdd-replan** (`SKILL.md:24-26`): references "milestone-scoped staleness" **by
  name only**, so it inherits whatever the canonical definition says; re-point that
  reference at a workstream-scoped definition. *No new traversal.*
- **sdd-specs** (`SKILL.md:21`): **no scoped branch today** - compares coarse
  requirements `index.md` -> specs -> plan as one monolith. Under v4, specs are
  shared and there are N per-ws plans; this clause should **stop touching plans**
  (defer plan staleness to sdd-plan) or gain a new per-ws branch. *New logic.*
- **sdd-verify** (`SKILL.md:24`): **no scoped branch today** - coarse
  `index.md`-vs-`docs/plan.md`. Needs a **new** workstream-scoped branch comparing
  `docs/ws/<id>/plan.md`/verification only against the shared specs/reqs that
  workstream traces. *New logic (milestone traversal is the template).*
- **sdd-requirements** (`SKILL.md:29`, REQ-STALE-002): research->requirements on the
  shared corpus; **unchanged** (only the RS ID pattern changes if research becomes
  ws-prefixed).

**Does traceability.md already record the ws->spec->req linkage?** **No.** It is a
5-column matrix `| Requirement | Spec | Test | Implementation | Verified |`
(`docs/requirements/traceability.md:7-8`) with **no workstream axis**. Crucially,
the *current* staleness algorithm does **not read traceability.md at all** - scope
is computed live from the plan file's tasks' `traces to` -> spec `requires:` ->
IDs -> `index.md` dates. So two implementation options:
- **Option A (recommended, lowest cost):** keep computing scope live from
  `docs/ws/<id>/plan.md`. Works with **no traceability schema change**; the
  milestone traversal generalizes as-is.
- **Option B:** honor the kickoff's `REQ -> SPEC -> workstream -> verification`
  framing by adding a **workstream column** to traceability.md. Records the linkage
  but is *not present today* and adds a concurrently-appended column to the very
  file flagged as a merge risk in Q1 - so if chosen, it must adopt the Q1
  per-ws-owned-rows structure.

**Confidence**: High (direct reads of the canonical spec + all six skills' step-0).

**Recommendation**: Generalize the existing milestone traversal to a workstream key
for plan/implement/replan (Option A, compute-live, no schema change). Add new per-ws
staleness branches to verify and specs (or remove specs' plan-staleness clause). Do
not make staleness depend on a new traceability column.

### Q3 - Migration safety (v3->v4)

**Answer**: Yes, safe - provided the migration **copies (not moves) execution
artifacts into `docs/ws/default/`, verifies, then flips `.sdd-version` to `4`
LAST, then deletes the flat originals as idempotent cleanup**. This preserves the
existing "version marker written last" interrupted-migration invariant
(`sdd-migrate/SKILL.md:272`: "If any prior step fails or is interrupted,
`.sdd-version` still contains [the old value]. Re-running detects [it] and
resumes.").

**Evidence / mechanism**: `.sdd-version` is the single switch that selects which
layout a skill's step-0 reads. The one dangerous window is any moment when the
on-disk layout disagrees with what the marker claims:
- While marker = `3`: v3 skills read flat `docs/plan.md` / `docs/verification.md`
  and MUST find them. So flat files must remain valid for the entire `3` window ->
  **copy, don't move**. Duplicates in `docs/ws/default/` are invisible to v3 skills.
- The instant marker = `4`: v4 skills read `docs/ws/<id>/...` and MUST find them ->
  `docs/ws/default/plan.md` + `verification.md` must be fully in place and verified
  **before** the flip.
- A v4-aware skill invoked while marker still = `3` sees "not yet migrated" and
  suggests `sdd-migrate` (existing behavior, `SKILL.md:26`) - no misdetection.

**Recommended safe step order (v3->v4):**
1. Precondition: `.sdd-version` = `3`. Create `docs/ws/default/` and
   `docs/ws/default/plan-history/`.
2. **Copy** `docs/plan.md` -> `docs/ws/default/plan.md`, `docs/verification.md` ->
   `docs/ws/default/verification.md`, `docs/plan-history/*` ->
   `docs/ws/default/plan-history/`, and (if present) `docs/handoff/kickoff.md` ->
   `docs/ws/default/kickoff.md`. Preserve task `[x]`/`[ ]` status and pass/fail
   verdicts verbatim. **Verify byte-identical.**
3. Leave the shared corpus in place: `docs/requirements/`, `docs/spec/`,
   `docs/research/`, `docs/requirements/traceability.md` are NOT moved.
4. **Write `docs/.sdd-version` = `4`** (atomic single-file flip - the LAST
   meaningful gate).
5. **Cleanup:** delete the now-orphaned flat `docs/plan.md`,
   `docs/verification.md`, `docs/plan-history/` (and flat `kickoff.md`). Idempotent
   - if interrupted, v4 skills already ignore flat paths; re-running detects
   marker = `4` and re-does cleanup.

**What `.sdd-version` gates**: the layout contract. `3` = flat execution artifacts
authoritative (`docs/plan.md`, `docs/verification.md`); `4` = per-workstream
execution artifacts authoritative (`docs/ws/<id>/{plan,verification,kickoff}.md`,
default ws = `default`) with `requirements/`, `spec/`, `research/`, `traceability`
as the shared corpus. Every skill's step-0 branches on it, guaranteeing a v3 skill
never reads `ws/` and a v4 skill never reads flat paths.

**Confidence**: High. The copy-verify-flip-cleanup pattern is the same invariant
sdd-migrate already relies on (`SKILL.md:264-280`); note the one deviation from
existing steps - v1->v2/v3 *moved* files, but v3->v4 must **copy-then-delete** so
the flat layout stays valid across the whole `3` window.

### Q4 - ID-format blast radius

**Answer**: The workstream-prefixed format inserts a middle token
(`RS-ISSUE42-NNN`, `Q-IMPL-ISSUE42-NNN`, `REQ-AUTH-ISSUE42-NNN`). It breaks **every
"scan tree -> highest numeric NNN -> +1 -> zero-pad-3" ID generator** and **one
convention-validation check**. It does **NOT** break fan-out's `Depends on: Chunk
N` derivation, traceability row parsing, or the Q-REQ/Q-SPEC checks. There is **no
compiled `RS-\d+` / `Q-IMPL-\d+` regex anywhere** - the breakage is in the described
*algorithms*, not in grep patterns.

**Parsers that BREAK (need format/algorithm change):**

| File:line | What breaks | Minimal change |
|---|---|---|
| `sdd-research/SKILL.md:48-51` | `RS-NNN-*` dir scan + highest-NNN extract + zero-pad | Pattern `RS-{WS}-NNN-*`; parse NNN after WS token; scope max per-workstream |
| `sdd-requirements/SKILL.md:134-138` | `REQ-{DOMAIN}-{NNN}` template + highest-NNN scan | `REQ-{DOMAIN}-{WS}-{NNN}`; scan max per domain+workstream |
| `sdd-implement/SKILL.md:261-262` | `Q-IMPL-NNN` "global sequential, increment from highest" | `Q-IMPL-{WS}-NNN`; scan per-workstream |
| `sdd-migrate/SKILL.md:61,76,116` | RS/REQ remap target templates + "start after highest" | Add `{WS}` slot; renumber within domain+workstream |
| `sdd-review/SKILL.md:98` | Convention check literally states `REQ-{DOMAIN}-{NNN}` -> would flag ws IDs as violations (advisory false-positive) | State convention as `REQ-{DOMAIN}-{WS}-{NNN}` / optional WS segment |

**Parsers that DO NOT break (no change):**
- **Fan-out `Depends on: Chunk N`** (`sdd-orchestrate/references/fan-out.md:26-29,213`):
  parses **chunk ordinals** from `### Chunk N:` headers - a separate namespace from
  RS/Q/REQ artifact IDs. Artifact IDs appear only as inert prose. Unaffected.
- **Traceability / requirements row parsing** (`sdd-requirements/SKILL.md:201-204`,
  `sdd-specs/SKILL.md:187` uses a `REQ-*` prefix-glob, `sdd-implement/SKILL.md:144`):
  opaque-string / prefix-glob matching; tolerates an inserted WS segment.
- **sdd-review Q-REQ / Q-IMPL / Q-SPEC content checks** (`SKILL.md:99,137,233`): no
  numeric-suffix assumption. Q-REQ/Q-SPEC already use letter suffixes in practice
  (`Q-REQ-G`, `Q-IMPL-1`), so nothing assumes zero-padded numerics for them.
- **`### M\d+:` milestone regex** (`sdd-migrate/SKILL.md:225,231,237`): matches
  milestone headers, not artifact IDs. Unaffected.

**Confidence**: High (exhaustive grep + read across all `sdd-*` skills and
references).

**Recommendation**: Adopt `RS-{WS}-NNN`, `REQ-{DOMAIN}-{WS}-NNN`, `Q-IMPL-{WS}-NNN`.
Change the 4 generators to parse NNN *after* the WS token and scope the max-scan
per-workstream (this also removes the original scan-and-increment race, since each
workstream's counter is independent). Update the sdd-review convention string. No
other parser needs touching.

## Implications for Design (feeds requirements)

- **Merge-safe writes are a hard requirement, not a convention.** "Append-mostly"
  must be specified as **sorted-insertion-into-distinct-regions** or
  **per-workstream-owned rows/files** - never tail-append. `traceability.md` should
  become per-workstream-owned (separate `docs/ws/<id>/traceability.md` aggregated,
  or delimited per-ws sections). `requirements/index.md` new rows use ID-sorted
  insertion; distinct-domain concurrency merges clean, same-domain concurrency is an
  accepted human PR conflict.
- **Staleness**: generalize the milestone traversal to a workstream key for
  plan/implement/replan (no schema change, compute-live); add new per-ws staleness
  branches to verify and specs. Keep research->requirements staleness workstream-
  independent.
- **Migration**: v3->v4 is **copy-verify-flip-cleanup** with `.sdd-version` flipped
  last; the marker is the sole layout gate; copy-not-move is the one deviation from
  existing migrate steps.
- **IDs**: 4 generators + 1 review convention string change; fan-out, traceability
  parsing, and Q-REQ/Q-SPEC checks are untouched. Per-workstream counters also
  eliminate the allocation race.

## Prototype (Q1)

- Isolated throwaway git repo at `$TMPDIR/rs007-merge-spike` (deleted after the
  spike). No branches created in the real repo. Full commands, all 7 scenarios,
  and the verbatim conflict output are in `merge-spike.md` (this directory).
- Demonstrates: concurrent 3-way merge behavior on the exact table shapes of
  `requirements/index.md` and `traceability.md`. Does not prove behavior under
  non-default merge drivers (e.g. a custom `.gitattributes` union merge) - see
  Open Questions.

## Open Questions / Assumptions

- **Assumption (Q1):** default git recursive merge, no `.gitattributes` overrides.
  A `merge=union` driver on the table files would auto-union concurrent appends
  (no conflict) - a possible *alternative* mitigation not spiked here. Default: do
  NOT rely on `union` (it can interleave rows unsorted); prefer the structural fix.
  Flagged for the design to consider as an optional belt-and-suspenders.
- **Assumption (Q2):** chose Option A (compute-live staleness, no new traceability
  column) as the recommendation because it needs zero schema change; if the design
  wants the recorded `REQ -> SPEC -> workstream` linkage for other reasons, it must
  adopt the Q1 per-ws-owned-rows structure for the new column.
- **Assumption (Q3):** `docs/handoff/kickoff.md` (if present at migration time) maps
  to `docs/ws/default/kickoff.md`; the design's target layout puts kickoff under
  `ws/<id>/`. Confirm whether a flat `docs/handoff/` is retained for the
  orchestrator's active-cycle handoff or fully absorbed per-ws.

## Recommended Next Step

**Proceed to requirements.** All four uncertainties are resolved with enough
certainty to write requirements without guessing: the merge-safe structure (Q1),
the staleness-scoping mechanism (Q2 Option A + new branches for verify/specs), the
migration step order (Q3 copy-verify-flip-cleanup), and the exact parser changes
(Q4: 4 generators + 1 convention string).
