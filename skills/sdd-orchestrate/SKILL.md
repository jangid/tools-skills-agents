---
name: sdd-orchestrate
description: >
  Driver skill that runs the nine SDD phase skills as a single-operator
  orchestration loop with per-stage external review. Drives DISCUSS → KICKOFF →
  LOOP → DONE: brainstorm an idea to shared understanding, write a research
  kickoff, then for each stage dispatch an isolated pipeline subagent and an
  isolated review subagent, gating with the operator after every stage. Use when
  you want to run a whole SDD cycle end-to-end with built-in external review. Do
  NOT use to run a single phase (invoke that sdd-* skill directly) or to review
  an artifact in isolation (use sdd-review).
---

# SDD: Orchestration Driver

You are the **orchestrator**. You drive the full SDD cycle from a single human
session, dispatching each pipeline stage and each review as separate subagents,
and gating with the operator after every stage.

## What This Is

`sdd-orchestrate` is a **driver**, not a tenth phase skill. It composes the nine
existing `sdd-*` skills (research, requirements, specs, plan, implement, verify,
replan, migrate, review) and **never reimplements their logic**. Stage work —
including each skill's own phase detection and staleness handling — is performed
by dispatching the corresponding `sdd-*` skill; you relay that output rather than
duplicating it. You own only orchestration: sequencing stages, constructing
isolated dispatches, and mediating operator gates.

Isolation is **by construction**. Each pipeline stage and each review run as a
**separate subagent** with a fresh context window. A freshly dispatched subagent
has no shared window through which your reasoning could leak — a stronger
guarantee than two human terminal sessions.

**Scope**: research-entry; sequential by default. The kickoff is always a research
kickoff and the loop starts at research — mid-pipeline entry remains out of scope.
Implement-stage **fan-out is active** as an opt-in mode at the implement gate (see
§Execution Model); every other stage is always sequential.

## Phase Detection

The driver introduces **no loop-position marker**. On entry — including re-entry
in a fresh session mid-loop — derive the current loop position from the existing
SDD artifacts, reusing the stage skills' own phase detection:

| On disk | Loop position |
|---------|---------------|
| no `docs/handoff/kickoff.md` | before KICKOFF — run DISCUSS |
| kickoff exists, no `docs/research/RS-*/findings.md` | at the research stage |
| research done, requirements `Draft`/missing | at the requirements stage |
| requirements `Approved`, specs missing/stale | at the specs stage |
| specs `Approved`, no `docs/plan.md` (or stale) | at the plan stage |
| plan has incomplete tasks | at the implement stage |
| plan complete, no/failing `docs/verification.md` | at the verify stage |
| `docs/verification.md` status pass | at DONE (pending operator approval) |

Tell the operator the detected position and confirm before proceeding. A pending
or prior review leaves no on-disk trace by design — it is **reproduced** by
re-dispatching the review subagent against the current artifacts (reviews are
read-only and idempotent).

## The Four Phases

```
DISCUSS  — converge with the operator on the idea (scope + open questions)
   ↓
KICKOFF  — write docs/handoff/kickoff.md (a research kickoff for v1)
   ↓
LOOP     — for each stage in [research, requirements, specs, plan, implement, verify]:
             1. PIPELINE subagent → invokes sdd-<stage>, writes artifact(s) to disk
             2. REVIEW subagent   → fed artifact paths only; invokes sdd-review;
                                     returns a tiered verdict
             3. GATE (operator)   → surface the verdict; wait:
                                     proceed │ loop-back-to-fix │ stop
             4. if fix → re-dispatch PIPELINE with findings + paths only; goto 2
   ↓
DONE     — the verify stage passes review AND the operator approves
```

## DISCUSS

Before writing any kickoff, reach a shared understanding of the idea with the
operator. **Reuse the brainstorming process** (invoke the brainstorming skill):
explore intent, surface scope boundaries, and capture the open questions the
research stage should answer. Do not jump straight to a kickoff or to
implementation — converge first.

Exit DISCUSS when the operator and you agree on: what the idea is, what is in and
out of scope, and the concrete questions worth researching.

## KICKOFF

Write the converged discussion into `docs/handoff/kickoff.md`. This is the
**only** new on-disk artifact type the driver introduces; every other stage
output is a normal SDD artifact. It must be git-trackable (a real file under
`docs/handoff/`, committed alongside the cycle's work).

For v1 the kickoff is a **research kickoff**: it states the research questions,
success criteria, a budget, and what is out of scope, and the LOOP begins at the
research stage. Non-research entry points (starting mid-pipeline when upstream
artifacts already exist) are **out of scope for v1** — do not emit a non-research
kickoff or skip the research stage.

The kickoff carries **no loop log**. It is written once at KICKOFF and is not the
source of truth for resume — the SDD artifacts are (see Phase Detection).

## LOOP

For each stage in order — research, requirements, specs, plan, implement, verify
— run pipeline → review → gate.

### Per-stage dispatch model

Issue **two separate subagent dispatches** per stage — never a single combined
one. Run the **pipeline** dispatch to completion (artifacts on disk) **before**
constructing the **review** dispatch, because the review's only inputs are the
paths the pipeline produced.

### Pipeline subagent dispatch

The pipeline subagent invokes `sdd-<stage>` and writes the stage's SDD
artifact(s). A subagent is **non-interactive** — it has no operator to answer the
questions an `sdd-*` skill would normally ask. You MUST neutralize this in the
dispatch prompt. The full template is in
[`references/dispatch-templates.md`](references/dispatch-templates.md); its slots
MUST satisfy this contract:

- **Front-load every decision** the stage skill would ask a human for: the
  stage's question/scope, the success criterion, an explicit budget, and the
  exact deliverable contract (files to write + their frontmatter).
- **Assign IDs centrally.** You (the orchestrator) pick the artifact IDs (e.g.
  the next `RS-NNN`) and pass them verbatim. Subagents must not scan existing
  artifacts and choose IDs themselves — that collides under any future parallel
  dispatch.
- **Pin the absolute working directory** (phase detection reads
  `docs/.sdd-version` and artifacts relative to cwd; a wrong cwd silently
  misdetects).
- **Include a non-interactivity clause**: do not ask questions; do not fabricate
  operator consent; record genuinely missing information under an
  Open Questions / Assumptions section with a stated default, and proceed.
- **Include the labeled-content fallback**: if a file cannot be written, return
  its full content with the target path labeled.

### Review subagent dispatch

The review subagent invokes `sdd-review` against the pipeline's output. This
dispatch enforces `sdd-review`'s prohibited-inputs list **at dispatch time** —
isolation does not depend on operator vigilance. The template is in
[`references/dispatch-templates.md`](references/dispatch-templates.md).

**The review dispatch MUST carry ONLY:**
- the repository root,
- the deliverable artifact path(s),
- the upstream artifact path — **except for the research stage** (see below),
- the instruction to invoke `sdd-review`.

**It MUST NOT carry:**
- your conversation or reasoning,
- the pipeline subagent's reasoning or "here's what I was thinking" framing,
- kickoff prose beyond the artifact itself,
- any draft or intermediate states.

The reviewer obtains all other context (frontmatter, commit history, the
traceability matrix) by reading repository files itself.

**Research-stage exception**: for the research stage, **omit the upstream
(kickoff) path** — `sdd-review` prohibits kickoff prompts as a contaminating
input, so the reviewer reads the research questions from the deliverable's own
frontmatter instead. For every later stage, supply the upstream SDD artifact
(requirements when reviewing specs, specs when reviewing the plan, …) — it is a
permitted, non-leaking input.

### The gate

After review, surface the verdict (the review subagent's return text) to the
operator and **wait** for an explicit decision. Never auto-advance.

| Decision | Action |
|----------|--------|
| **proceed** | Advance to the next stage. |
| **loop-back-to-fix** | Re-dispatch the pipeline subagent with **only** the review findings + the relevant artifact paths — not a re-litigation of the reviewer's reasoning — then re-run the review for this stage. |
| **stop** | Halt the loop; leave artifacts as-is. |

### Edge cases routed through the gate

- **Replan trigger**: if a pipeline subagent triggers a replan (stuck detection,
  spike invalidation, or a verification failure), surface it to the operator as a
  gate event. The loop may then route back to an earlier stage via `sdd-replan`,
  consistent with the cyclic SDD model. Do not silently absorb or auto-resolve a
  replan trigger.
- **Reject with no actionable findings**: if a review returns a reject/fail
  verdict carrying no actionable findings, **pause** and let the operator decide
  (re-dispatch, override, or stop). Do not auto-loop the pipeline.

## Reviews Are Ephemeral

A review verdict is the review subagent's return text, surfaced inline. Do
**not** write verdicts to disk as a project artifact, and do **not** create a
`docs/reviews/` directory. Decisions land in the artifacts themselves — commits,
spec edits, Q-IMPL entries, replan triggers.

## Execution Model

**Sequential is the default.** Every stage runs single-threaded in the main
workspace unless the operator explicitly opts into fan-out at the implement gate.
Fan-out is **only** ever available at the implement stage; no other stage fans out.

**Implement-stage fan-out (Design B — active, opt-in).** Fan-out is
**orchestrator-owned and one level deep**: you derive independent chunk-groups from
the plan, provision a worktree per group, dispatch one **leaf** implement subagent
per group, then merge the branches sequentially into `main` before the
implement-stage review. The full procedure (dispatch template + command sequence)
lives in [`references/fan-out.md`](references/fan-out.md); the contract below is its
summary.

Design A (a pipeline subagent owning nested fan-out) is **ruled out infeasible** — a
dispatched subagent has no subagent-dispatch tool (RS-006 Q1) — so Design B is the
only viable design and the spec.

### Boundary derivation

Fan out along the **independent branches of the plan's chunk dependency graph** —
not per-milestone (too coarse; milestones are sequential) and not per-task (too
fine). Derive the groups by **reading `docs/plan.md`**, never by modifying
`sdd-implement`: parse each chunk's `**Depends on**: Chunk N` field (canonical, per
plan-management.md) or its chunk-level prose equivalent `Entry criteria: Chunk N
complete`. Do **not** use milestone-level Entry/Exit criteria for this. Two chunks
are independent when neither (transitively) depends on the other.

**Degrade to sequential** (never guess a boundary) when the plan has no parseable
chunk-level dependencies, or when the graph is a **single chain** (no ≥2 independent
branches).

### Opt-in gate

Fan-out is **opt-in at the implement gate** and never automatic. At that gate,
present fan-out as an explicit operator choice; you may surface how many independent
chunk-groups the plan yields so the operator can judge whether it is worthwhile.
Absent an opt-in, the implement stage runs sequentially.

When the plan yields only a **single chain** (or has no parseable chunk-level
dependencies), tell the operator **at the gate** that fan-out will degrade to
sequential for this plan — so an opt-in that then runs sequentially is expected, not
surprising.

### Lifecycle (provision → dispatch → merge → teardown)

When the operator opts in and the graph has ≥2 independent branches:

1. **Provision** one worktree/branch per group yourself:
   `git worktree add -b <branch> <path> <base>`. Worktree ownership is the
   orchestrator's (Q-REQ-G) — a single owner keeps provisioning and teardown
   symmetric and avoids orphaned worktrees.
2. **Dispatch** one implement subagent per group, pinned to its worktree/branch,
   carrying that group's chunks. Each is a **leaf** — it runs `sdd-implement` and
   must not (and cannot) sub-dispatch (REQ-ORCH-022). The non-interactivity contract
   and central ID assignment apply. **Issue all per-group dispatches in one batch**
   so they run concurrently (see Concurrency note), then **await all returns** before
   merging.
3. **Subagent git identity:** instruct each subagent to commit with inline
   `git -c user.email=<id> -c user.name=<name> commit ...` — never by writing
   `.git/config`, which the subagent sandbox blocks (RS-006 Q2). Do not instruct a
   subagent to write `.git/config`.
4. **Sequential merge to main:** after all returns, merge branches one at a time
   (`git merge --no-edit <branch>`), completing **all** merges **before** the
   implement-stage review (the review sees the merged state, never an unmerged
   branch). One-at-a-time merging means partial-merge corruption cannot occur.
5. **Teardown:** after each clean merge, remove the worktree
   (`git worktree remove <path>`) and delete its branch (`git branch -d <branch>`),
   leaving only `main` for the review.

### Conflict handling (redo by re-derivation)

On a non-zero `git merge` exit: an **optional** best-effort auto-resolve may be tried
first (a clean auto-resolve = PASS, no abort). Otherwise run `git merge --abort`,
then **redo the chunk-group by re-derivation** — provision a fresh worktree
re-branched from the updated `main` (`git worktree add -b <branch>-redo <path>
main`) and re-dispatch a leaf implement subagent to re-run `sdd-implement` there.
**Never replay the stale returned patch** (it would reproduce the same conflict);
re-derivation integrates the already-merged changes. If the group **still** conflicts
after re-derivation, that proves the groups were not truly independent (a boundary
error) → **fall back to running the affected groups sequentially**, which cannot
conflict by construction and guarantees termination. `git merge --abort` unwinds only
the single failing merge — already-merged work is never corrupted. Full command
sequence: [`references/fan-out.md`](references/fan-out.md) §3c (Q-IMPL-1).

### Concurrency note

Fan-out implement subagents dispatched in a single batch were **observed to run
concurrently** on this harness — medium confidence, per the RS-006
dispatch-concurrency spike (`docs/spikes/dispatch-concurrency.md`), whose ~4s probe
workload inside a ~426s agent lifetime is latency-dominated. Where it holds, fan-out
delivers wall-clock speedup, not merely worktree isolation (REQ-ORCH-028).
**Correctness does not depend on it:** the design (per-worktree isolation +
sequential conflict-aborting merge) is correct whether dispatches run concurrently or
serialized; only the speedup depends on concurrency.

## Isolation Discipline (normative)

The driver MUST:

1. Dispatch the pipeline and the review as **two separate subagents** per stage.
2. Construct the review dispatch from **artifact paths only** (plus the repo root
   and, for non-research stages, the upstream path). Never include your
   conversation, the pipeline subagent's reasoning, kickoff prose beyond the
   artifact, or draft/intermediate states.
3. On a fix loop, pass the pipeline subagent **only** the review findings plus
   artifact paths — not a re-litigation of the reviewer's reasoning.

These mirror `sdd-review` Step 2's "Do NOT accept as inputs" list, enforced at
dispatch time rather than relying on operator vigilance.

## Rules

- **Compose, never reimplement**: stage logic lives in the nine `sdd-*` skills.
  Dispatch them; do not duplicate or modify them.
- **Two dispatches per stage, always**: pipeline and review are never combined.
- **Paths only to the reviewer**: if you are tempted to "give the reviewer some
  helpful context," stop — that is the leak the design exists to prevent.
- **Human gate at every stage**: never auto-advance past a gate.
- **Reviews are ephemeral**: no `docs/reviews/`, no verdicts on disk.
- **Artifacts are the source of truth for resume**: no loop-position marker, no
  authoritative loop log.
- **Sequential by default**: only the implement stage may fan out, only when the
  operator opts in and the plan has ≥2 independent chunk branches; no non-research
  entry.

## Transition

When the verify stage passes review and the operator approves, the cycle is
DONE. Recommend committing the cycle's artifacts (including
`docs/handoff/kickoff.md`).
