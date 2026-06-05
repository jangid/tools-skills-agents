---
domain: ORCH
last_updated: 2026-06-05
status: Approved
research_refs: [RS-005]
---

# Requirements: SDD Orchestration Driver

## Overview

A driver skill (`sdd-orchestrate`) that runs the existing nine `sdd-*` skills as
a single-operator orchestration loop with per-stage external review. One human
session (the orchestrator) drives; each pipeline stage and each review run as
**separate subagents** with fresh context windows, giving isolation by
construction. After every stage the operator gates on the review verdict
(proceed │ loop-back-to-fix │ stop). Derived from the settled dual-session design
(D1–D7) and RS-005 feasibility findings, which proved subagent skill-invocation
and dispatch-time review isolation with live dispatches. (see RS-005)

Scope note: the loop is **research-entry**, with **sequential execution as the
default**. Mid-pipeline entry points remain deferred. Parallel implement-stage
fan-out is **supported** as an opt-in mode (REQ-ORCH-016,
REQ-ORCH-022..028, where 028 is the [needs-spike] dispatch-concurrency item),
built as **Design B (orchestrator-owned fan-out, one level deep)** per the RS-006
spike, which proved subagent dispatch cannot nest and that orchestrator-owned
worktree creation + sequential merge with conflict-abort fallback all work.
(see RS-006)

## Requirements

### REQ-ORCH-001: Driver composes, never reimplements
The skill must act as a driver that composes the nine existing `sdd-*` skills.
It must not modify, rewrite, or reimplement the logic of any `sdd-*` skill;
stage work is performed by dispatching the corresponding skill. Staleness and
phase detection remain the stage skills' responsibility — the driver relays
their output, it does not duplicate that logic.
[Priority: must]

### REQ-ORCH-002: Four driver phases
The driver must implement four phases in order: (a) DISCUSS — converge operator
and orchestrator on scope and questions; (b) KICKOFF — write the kickoff prompt;
(c) LOOP — per-stage pipeline → review → gate; (d) DONE — reached when the verify
stage passes review and the operator approves.
[Priority: must]

### REQ-ORCH-003: DISCUSS borrows brainstorming
The DISCUSS phase must reach a shared understanding of the idea (scope and open
questions) before writing the kickoff, reusing the brainstorming process rather
than jumping directly to a kickoff or to implementation.
[Priority: must]

### REQ-ORCH-004: Kickoff is the only new on-disk artifact
The KICKOFF phase must write `docs/handoff/kickoff.md`, and this must be the only
new on-disk artifact type the driver introduces. It must be git-trackable. All
other stage outputs are the normal SDD artifacts, which serve as the message bus
between pipeline and review subagents.
[Priority: must]

### REQ-ORCH-005: Research-entry only (v1)
For v1, the kickoff writer must emit a research kickoff, and the LOOP must begin
at the research stage. Non-research entry points (starting the loop mid-pipeline
when upstream artifacts already exist) are out of scope for v1.
[Priority: must]

### REQ-ORCH-006: Two separate subagents per stage
For each stage in [research, requirements, specs, plan, implement, verify], the
driver must dispatch the pipeline work and the review as two separate subagents,
each with a fresh context. The pipeline and review must never share a single
dispatch.
[Priority: must]

### REQ-ORCH-007: Pipeline non-interactivity contract
Each pipeline dispatch prompt must front-load every decision the stage skill
would otherwise ask a human for: the stage's question/scope, the success
criterion, an explicit budget, and the exact deliverable contract (files to
write and their frontmatter). The prompt must include a non-interactivity clause
instructing the subagent not to ask questions and not to fabricate operator
consent; genuinely missing information must be recorded under an Open
Questions / Assumptions section with a stated default. Evidence: RS-005 Q1 found
the only real hazard of subagent skill execution is the interactive-skill /
non-interactive-dispatch gap, fully solved by front-loading.
[Priority: must]

### REQ-ORCH-008: Central ID assignment
The orchestrator must assign artifact IDs (e.g. `RS-NNN`) centrally and pass them
verbatim to pipeline subagents, rather than letting subagents scan existing
artifacts and pick the next ID themselves. This prevents ID collisions,
especially under any future parallel dispatch.
[Priority: must]

### REQ-ORCH-009: Review dispatch carries paths only
Each review dispatch prompt must carry only: the repository root, the
deliverable artifact path(s), the upstream artifact path (where applicable —
see REQ-ORCH-010), and the instruction to invoke `sdd-review`. It must not
include the orchestrator's conversation or reasoning, the pipeline subagent's
reasoning or "here's what I was thinking" framing, kickoff prose beyond the
artifact itself, or any draft/intermediate states. This enforces `sdd-review`
Step 2's prohibited-inputs list at dispatch time rather than relying on operator
vigilance. Verified by RS-005 Q2: a paths-only review dispatch produced a correct
verdict with an audited zero-leakage input set.
[Priority: must]

### REQ-ORCH-010: Research-stage review omits the upstream path
For the research stage specifically, the review dispatch must omit the upstream
(kickoff) path, because `sdd-review` prohibits kickoff prompts as a contaminating
input. The reviewer instead reads the research questions from the deliverable's
own frontmatter. For all later stages, the upstream SDD artifact (requirements,
specs, plan, …) is a permitted, non-leaking input and must be supplied.
[Priority: must]

### REQ-ORCH-011: Human gate at every stage
After the pipeline → review sequence for a stage, the driver must surface the
review verdict to the operator and wait for an explicit decision: proceed,
loop-back-to-fix, or stop. The driver must not auto-advance to the next stage
without an operator decision.
[Priority: must]

### REQ-ORCH-012: Fix loop passes findings and paths only
On a loop-back-to-fix decision, the driver must re-dispatch the pipeline subagent
with only the review findings plus the relevant artifact paths — not a
re-litigation of the reviewer's reasoning or chain-of-thought — and must then
re-run the review for that stage.
[Priority: must]

### REQ-ORCH-013: Reviews are ephemeral
A review verdict is the review subagent's return text, surfaced to the operator
inline. The driver must not write review verdicts to disk as a project artifact
and must not create a `docs/reviews/` directory. Decisions land in the artifacts
themselves (commits, Q-IMPL entries, replan triggers).
[Priority: must]

### REQ-ORCH-014: Resume via existing phase detection
On re-entry in a new orchestrator session, the driver must derive loop position
from the existing SDD artifacts (existence, status, and staleness), reusing the
stage skills' phase detection. The driver must not introduce a dedicated
loop-position marker file, and `docs/handoff/kickoff.md` must not carry an
authoritative loop log. A pending or prior review is reproduced by re-dispatching
the review subagent against the current artifacts. Evidence: RS-005 Q3.
[Priority: must]

### REQ-ORCH-015: Sequential execution is the default
By default, all stages must run single-threaded in the main workspace. Sequential
execution is the baseline behavior; parallel implement-stage fan-out
(REQ-ORCH-016, REQ-ORCH-022..028, where 028 is the [needs-spike]
concurrency item) is an opt-in mode selected at the implement
gate. When fan-out is not selected, the implement stage runs single-threaded in
the main workspace exactly as every other stage does.
[Priority: must] [Updated: 2026-06-04]

### REQ-ORCH-016: Implement fan-out boundary rule
The orchestrator must support parallel implement-stage fan-out. Fan-out must occur
along the independent branches of the plan's **chunk** dependency graph — not
per-milestone (too coarse, milestones are sequential) and not per-task (too
fine). The orchestrator must derive the parallel groups by reading the plan's
dependency graph, without modifying `sdd-implement`. Fan-out applies only when the
dependency graph actually contains independent chunk branches; otherwise execution
stays sequential even when fan-out is selected. (chunk-boundary rule: RS-005;
orchestrator-owned design selection: RS-006 Q4)
[Priority: must] [Updated: 2026-06-04]

> Note: REQ-ORCH-022..028 extend the implement-fan-out cluster begun at
> REQ-ORCH-015/016 (IDs are non-monotonic in this file).

### REQ-ORCH-022: Orchestrator-owned fan-out, one level deep (Design B)
_(added 2026-06-04, RS-006)_
The orchestrator must own the fan-out directly, dispatching the parallel implement
subagents itself, nesting exactly one level deep. A dispatched implement subagent
must not itself dispatch sub-subagents — each fan-out subagent is a leaf. This is
required because a dispatched subagent has no subagent-dispatch tool in its
toolset, making a nested implement-owns-fan-out design (Design A) infeasible in
this harness. (see RS-006 Q1, Q4)
[Priority: must]

### REQ-ORCH-023: One worktree per concurrently-runnable chunk-group
For each concurrently-runnable chunk-group, the orchestrator must provision one
git worktree on its own branch and pin the corresponding implement subagent to
it, so that parallel work is isolated per worktree. The orchestrator (not the
subagent) must provision these worktrees, giving it cleaner lifecycle and
cleanup ownership (per RS-006 Q2; decision: see Q-REQ-G). Each fan-out subagent
must operate only within its assigned worktree/branch.
[Priority: must]

### REQ-ORCH-024: Fan-out is opt-in at the implement gate
The operator must explicitly choose fan-out at the implement gate; the orchestrator
must not enable fan-out automatically. When the operator does not opt in, the
implement stage runs sequentially per REQ-ORCH-015.
[Priority: must]

### REQ-ORCH-025: Sequential merge to main before the implement-stage review
After the fan-out subagents return, the orchestrator must merge the worktree
branches **sequentially** into `main` and complete all merges **before** the
implement-stage review runs. The review must therefore operate on the merged
state, not on individual unmerged branches.
[Priority: must]

### REQ-ORCH-026: Merge-conflict abort-and-redo (with optional best-effort resolution)
On detecting a merge conflict — a non-zero exit from `git merge` — the orchestrator
must `git merge --abort` and redo the offending chunk-group by **re-deriving** its
implement work in a worktree re-branched from the updated `main` (not by replaying
the prior subagent output), then re-attempt the merge.
This abort-and-redo fallback is the guaranteed contract and must never corrupt or
unwind already-merged work; because merges are sequential, an abort only unwinds
the single failing merge. As an explicit BEST-EFFORT optional step, the orchestrator
may first attempt automatic resolution of the conflict before falling back to
abort-and-redo; auto-resolution is not guaranteed and the abort-and-redo path is
always available as the verifiable fallback. (see RS-006 Q3)
[Priority: must] [Updated: 2026-06-04]

### REQ-ORCH-027: Subagents commit with inline git identity flags
Each fan-out implement subagent must commit using inline
`git -c user.email=... -c user.name=...` identity flags rather than writing a
shared `.git/config`, because a dispatched subagent's command sandbox blocks
writes to the main repo's `.git/config`. Commits, merges, and branch operations
must still succeed under this constraint. (see RS-006 Q2)
[Priority: must]

### REQ-ORCH-028: Concurrent dispatch of fan-out subagents [needs-spike]
The orchestrator should dispatch the fan-out implement subagents so they execute
truly concurrently rather than serialized, to obtain wall-clock speedup. Whether
the harness runs a batch of dispatches concurrently or serializes them is
**unverified** and must be resolved at spec/implementation time. This question
only matters when ≥2 chunk-groups are concurrently runnable; with a single
runnable group it is moot. The fan-out design (worktree isolation + sequential
merge) holds correctly either way; only the wall-clock speedup is at stake if
dispatch is serialized. [needs-spike]
(see RS-006 Open Questions, RS-005 Q4)
[Priority: should]

### REQ-ORCH-017: Replan surfaces as a gate event
When a pipeline subagent triggers a replan (stuck detection, spike invalidation,
or a verification failure), the driver must surface it to the operator as a gate
event. The loop may then route back to an earlier stage via `sdd-replan`,
consistent with the cyclic SDD model. The driver must not silently absorb or
auto-resolve a replan trigger.
[Priority: must]

### REQ-ORCH-018: Reject verdict with no actionable findings pauses
If a review returns a reject/fail verdict with no actionable findings, the driver
must pause and let the operator decide whether to re-dispatch, override, or stop.
It must not auto-loop the pipeline in this case.
[Priority: must]

### REQ-ORCH-019: Single-skill packaging
The driver must be a single skill at `skills/sdd-orchestrate/SKILL.md`, kept under
the project's ~500-line guideline. The kickoff-writer must not be a separate
skill. The dispatch prompt templates (pipeline and review) may live in a
`skills/sdd-orchestrate/references/` file to keep the body lean.
[Priority: should]

### REQ-ORCH-020: Extensive operator user documentation
The skill must ship with extensive end-user (operator) documentation, distinct
from the `SKILL.md` (which is Claude-facing instructions). The documentation must
cover, at minimum: what the driver is and when to use vs. skip it; each of the
four phases (DISCUSS, KICKOFF, LOOP, DONE) explained for a human operator; a
complete worked example walking one idea from DISCUSS through a per-stage
pipeline→review→gate to DONE; the isolation guarantees and why they matter;
**installation** instructions, including linking the skill into the Claude skills
directory (`~/.claude/skills/<name>` → repo `skills/<name>`) as the project does
for every SDD skill; troubleshooting (including the blocked-subagent-write
labeled-content fallback); the execution model (sequential by default, with
implement-stage fan-out available as an opt-in mode — including its single-chain
degrade-to-sequential behavior); and the remaining v1 limitation
(**research-entry-only**: no non-research / mid-pipeline entry). It must live at a
discoverable path under `skills/sdd-orchestrate/`.
[Priority: must] [Updated: 2026-06-05]

### REQ-ORCH-021: Project README introduces the driver and links the docs
The project README must be updated to introduce `sdd-orchestrate` (and the SDD
skill suite it drives) and link to the operator documentation (REQ-ORCH-020) and
the skills directory. Installation guidance in the README must describe the
`~/.claude/skills/` symlink convention so a new adopter can install the skills.
[Priority: must]
