---
status: Approved
last_updated: 2026-06-04
requires:
  - REQ-ORCH-001
  - REQ-ORCH-002
  - REQ-ORCH-003
  - REQ-ORCH-004
  - REQ-ORCH-005
  - REQ-ORCH-006
  - REQ-ORCH-007
  - REQ-ORCH-008
  - REQ-ORCH-009
  - REQ-ORCH-010
  - REQ-ORCH-011
  - REQ-ORCH-012
  - REQ-ORCH-013
  - REQ-ORCH-014
  - REQ-ORCH-015
  - REQ-ORCH-016
  - REQ-ORCH-017
  - REQ-ORCH-018
  - REQ-ORCH-019
  - REQ-ORCH-020
  - REQ-ORCH-021
---

# SDD Orchestration Driver

## Context

SDD's nine skills are run today as an ad-hoc manual flow: the operator invokes
each `sdd-*` skill in turn and occasionally invokes `sdd-review` separately for
an external read. There is no defined workflow for the loop the operator wants:
evolve an idea to shared understanding, emit a kickoff, run the pipeline, and
after **each** stage have a fresh, context-isolated reviewer check the output
with back-and-forth until the stage is sound.

`sdd-orchestrate` is the **driver** that ties the existing skills into that loop.
It adds the isolation discipline and handoff conventions that make per-stage
external review trustworthy. RS-005 proved the two load-bearing mechanisms with
live subagent dispatches: a subagent can reliably invoke an `sdd-*` skill and
write artifacts (Q1), and a review subagent fed only artifact paths produces a
correct verdict with audited zero leakage (Q2). This spec defines the driver's
phases, its dispatch contracts, its gate protocol, and what it explicitly does
not do. Design decisions D1–D7 from the dual-session design are settled inputs.

## Design

### Driver Positioning

`sdd-orchestrate` is a **driver**, not a tenth phase skill. It composes the nine
existing skills and never reimplements their logic (REQ-ORCH-001). Stage work —
including each skill's own phase detection and staleness handling — is performed
by dispatching the corresponding `sdd-*` skill; the driver relays that output
rather than duplicating it. The driver owns only orchestration concerns:
sequencing stages, constructing isolated dispatches, and mediating operator
gates.

A single human session (the **orchestrator**) drives. Each pipeline stage and
each review run as **separate subagents** with fresh context windows (D1). This
gives isolation by construction — a freshly dispatched subagent has no shared
context window through which the orchestrator's reasoning could leak (D2),
a stronger guarantee than two human terminal sessions.

### Driver Phases

The driver runs four phases in order (REQ-ORCH-002):

```
DISCUSS  — orchestrator + operator brainstorm the idea to shared understanding
           (scope + open questions); reuses the brainstorming process
   ↓
KICKOFF  — orchestrator writes docs/handoff/kickoff.md (a research kickoff for v1)
   ↓
LOOP     — for each stage in [research, requirements, specs, plan, implement, verify]:
             1. PIPELINE subagent → invokes sdd-<stage>, writes the SDD artifact(s)
             2. REVIEW subagent   → fed artifact paths only; invokes sdd-review;
                                     returns a tiered verdict (return text)
             3. GATE (operator)   → orchestrator surfaces the verdict and waits:
                                     proceed │ loop-back-to-fix │ stop
             4. if fix → re-dispatch PIPELINE with review findings + paths only;
                         back to step 2
   ↓
DONE     — the verify stage passes review AND the operator approves
```

DISCUSS must reach a shared understanding before KICKOFF, reusing the
brainstorming process rather than jumping straight to a kickoff or to
implementation (REQ-ORCH-003).

### Kickoff Artifact

KICKOFF writes `docs/handoff/kickoff.md`, the **only** new on-disk artifact type
the driver introduces (REQ-ORCH-004). It is git-trackable. Every other stage
output is a normal SDD artifact; those artifacts are the message bus between
pipeline and review subagents (D5).

For v1 the kickoff writer emits a **research kickoff**, and the LOOP begins at
the research stage (REQ-ORCH-005). Non-research entry points (starting mid-
pipeline when upstream artifacts already exist) are out of scope for v1.

### Per-Stage Dispatch Model

For each stage the driver issues **two separate subagent dispatches** — never a
single combined one (REQ-ORCH-006):

| Dispatch | Fresh ctx | Purpose | Carries |
|----------|-----------|---------|---------|
| Pipeline | yes | Execute one SDD stage | Stage skill name, front-loaded decisions, IDs, cwd, (on fix) review findings |
| Review | yes | Externally review the stage output | Repo root + deliverable path(s) + (non-research) upstream path + "invoke sdd-review" |

The pipeline dispatch always runs to completion (artifacts on disk) before the
review dispatch is constructed, because the review's only inputs are the paths
the pipeline produced.

### Pipeline Subagent Contract

A subagent is non-interactive — it has no operator to answer questions. RS-005 Q1
found this is the single real hazard of subagent skill execution: an interactive
`sdd-*` skill that says "ask the user" will otherwise stall or fabricate consent.
The contract neutralizes this (REQ-ORCH-007):

**The pipeline dispatch prompt MUST:**
- Front-load every decision the stage skill would ask a human for: the stage's
  question/scope, the success criterion, an explicit budget, and the exact
  deliverable contract (files to write + their frontmatter).
- Pin all artifact IDs and the absolute working directory. IDs are assigned
  **centrally by the orchestrator** and passed verbatim — subagents must not scan
  existing artifacts and pick the next ID themselves, which would collide under
  any future parallel dispatch (REQ-ORCH-008).
- Include a **non-interactivity clause**: do not ask questions; do not fabricate
  operator consent; record genuinely missing information under an
  Open Questions / Assumptions section with a stated default and proceed.
- Include the labeled-content fallback (if a file cannot be written, return its
  full content with the target path labeled).

The full prompt template lives in the skill's `references/` file (REQ-ORCH-019);
this spec defines the contract its slots must satisfy. Illustrative shape:

```
You are a non-interactive pipeline subagent executing ONE SDD stage.
Working directory (absolute): {repo_root}
Stage skill: sdd-{stage}    Assigned IDs (verbatim): {ids}
Inputs (paths): {input_paths}    [on fix] Review findings: {findings}
Do NOT ask questions; do NOT fabricate consent. Missing info → record under
Open Questions with a default and proceed. Write {deliverable_contract}.
```

### Review Subagent Contract

The review dispatch enforces `sdd-review` Step 2's prohibited-inputs list **at
dispatch time**, rather than relying on operator vigilance (REQ-ORCH-009). RS-005
Q2 verified a paths-only dispatch yields a correct verdict with an audited
zero-leakage input set.

**The review dispatch prompt MUST carry ONLY:**
- the repository root,
- the deliverable artifact path(s),
- the upstream artifact path — **except for the research stage** (see below),
- the instruction to invoke `sdd-review`.

**It MUST NOT carry:**
- the orchestrator's conversation or reasoning,
- the pipeline subagent's reasoning or "here's what I was thinking" framing,
- kickoff prose beyond the artifact itself,
- any draft or intermediate states.

The reviewer obtains all other context (frontmatter, commit history, the
traceability matrix) by reading repository files itself.

**Research-stage exception** (REQ-ORCH-010): for the research stage the dispatch
**omits the upstream path**, because the upstream is the kickoff and `sdd-review`
prohibits kickoff prompts as a contaminating input. The reviewer reads the
research questions from the deliverable's own frontmatter. For all later stages
the upstream SDD artifact (requirements, specs, plan, …) is a permitted,
non-leaking input and MUST be supplied.

### Gate Protocol

After pipeline → review, the orchestrator surfaces the verdict and waits for an
explicit operator decision — it never auto-advances (REQ-ORCH-011):

| Decision | Driver action |
|----------|---------------|
| **proceed** | Advance to the next stage. |
| **loop-back-to-fix** | Re-dispatch the pipeline subagent with **only** the review findings + relevant artifact paths (not a re-litigation of the reviewer's reasoning), then re-run the review for that stage (REQ-ORCH-012). |
| **stop** | Halt the loop; leave artifacts as-is. |

Two non-standard events route through the gate as well:

- **Replan trigger** (REQ-ORCH-017): when a pipeline subagent triggers a replan
  (stuck detection, spike invalidation, or a verification failure), the driver
  surfaces it to the operator as a gate event. The loop may then route back to an
  earlier stage via `sdd-replan`, consistent with the cyclic SDD model. The
  driver must not silently absorb or auto-resolve a replan trigger.
- **Reject with no actionable findings** (REQ-ORCH-018): if a review returns a
  reject/fail verdict carrying no actionable findings, the driver pauses and lets
  the operator decide (re-dispatch, override, or stop). It must not auto-loop the
  pipeline in this case.

### Ephemeral Reviews

A review verdict is the review subagent's return text, surfaced inline to the
operator. The driver must not write verdicts to disk as a project artifact and
must not create a `docs/reviews/` directory (REQ-ORCH-013, preserving the
project's prior Q-REQ-B decision). Decisions land in the artifacts themselves —
commits, spec edits, Q-IMPL entries, replan triggers.

### Resume and Phase Detection

On re-entry in a new orchestrator session, the driver derives loop position from
the existing SDD artifacts (existence, status, staleness), reusing the stage
skills' own phase detection (REQ-ORCH-014). RS-005 Q3 established this is
sufficient: loop position is already fully encoded on disk, and the only
non-persisted state — the per-stage review verdict — is **reproducible** by
re-dispatching the (read-only, idempotent) review subagent against the current
artifacts.

Therefore the driver introduces **no** dedicated loop-position marker file, and
`docs/handoff/kickoff.md` carries **no** authoritative loop log. The artifacts
are the single source of truth for resume.

### Sequential Execution and Deferred Fan-out

For v1 every stage runs single-threaded in the main workspace (REQ-ORCH-015).
Parallel implement-stage fan-out and worktree isolation are out of scope for v1.

When fan-out is later introduced (REQ-ORCH-016, deferred), the settled rule is:
fan out along the **independent branches of the plan's chunk dependency graph** —
not per-milestone (too coarse; milestones are sequential) and not per-task (too
fine). Use one worktree per concurrently-runnable chunk-group and merge branches
**sequentially** back to `main` before the implement-stage review runs on the
merged state. The orchestrator derives the parallel groups by reading the plan's
dependency graph, without modifying `sdd-implement`. Fan-out applies only when
the graph actually contains independent chunk branches; otherwise execution stays
sequential.

#### Subagent nesting [high-uncertainty]
The deferred fan-out implies a pipeline subagent that itself spawns worktree
subagents (subagent-spawning-subagent). RS-005 did not exercise this nesting.
**Unverified assumption:** a dispatched subagent can itself dispatch subagents and
merge their branches. **Spike to resolve:** a minimal nested-dispatch probe
before the fan-out feature ships. **Fallback if false:** the orchestrator (not a
pipeline subagent) owns the fan-out — it dispatches the parallel implement
subagents directly and performs the merges itself, keeping nesting one level
deep. This uncertainty does **not** affect v1, which is sequential (REQ-ORCH-015).

### Packaging

The driver is a single skill at `skills/sdd-orchestrate/SKILL.md`, kept under the
project's ~500-line guideline (REQ-ORCH-019). The kickoff-writer is not a separate
skill — it is a contained, non-reusable sub-task of the driver. The two dispatch
prompt templates (pipeline and review) live in
`skills/sdd-orchestrate/references/dispatch-templates.md` to keep the body lean;
moving the bulkiest component out is what makes the ~500-line target comfortable
(RS-005 Q5; existing skills run 162–291 lines).

### User Documentation

`SKILL.md` is Claude-facing operational instruction. Operators also need a
human-facing guide (REQ-ORCH-020), shipped at
`skills/sdd-orchestrate/USAGE.md`. It must cover: what the driver is and when to
use vs. skip; each phase explained for an operator; a complete worked example
(one idea → DISCUSS → KICKOFF → per-stage pipeline→review→gate → DONE); the
isolation guarantees and why they matter; **installation** via the
`~/.claude/skills/<name>` → repo `skills/<name>` symlink convention this project
uses for every SDD skill; troubleshooting, including the blocked-subagent-write
labeled-content fallback observed live in RS-005; and the v1 limitations
(research-entry, sequential, no fan-out).

The project README (`README.org`) introduces the driver and the SDD suite, links
the operator guide, and documents the `~/.claude/skills/` symlink install
convention so a new adopter can install the skills (REQ-ORCH-021).

## Verification

### Manual
- Confirm the skill body implements DISCUSS → KICKOFF → LOOP → DONE in order.
- Inspect a constructed review dispatch prompt and confirm it contains only the
  permitted inputs (repo root, deliverable path, non-research upstream path,
  "invoke sdd-review") and none of the prohibited inputs.
- Inspect a constructed research-stage review dispatch and confirm the upstream
  path is omitted.
- Inspect a constructed pipeline dispatch and confirm the non-interactivity
  clause, front-loaded decisions, pinned IDs, and absolute cwd are present.
- Run the driver end-to-end on a small idea and confirm a gate appears after each
  stage with proceed │ loop-back-to-fix │ stop options.
- Confirm no `docs/reviews/` directory is created and `docs/handoff/kickoff.md`
  is git-tracked.

### Acceptance Criteria
- [ ] Skill is a driver that dispatches `sdd-*` skills and modifies none of them (REQ-ORCH-001)
- [ ] Skill body implements four ordered phases DISCUSS/KICKOFF/LOOP/DONE (REQ-ORCH-002)
- [ ] DISCUSS reuses the brainstorming process before KICKOFF (REQ-ORCH-003)
- [ ] KICKOFF writes `docs/handoff/kickoff.md` as the only new on-disk artifact type, git-trackable (REQ-ORCH-004)
- [ ] v1 emits a research kickoff and starts the loop at research; non-research entry is excluded (REQ-ORCH-005)
- [ ] Each stage issues two separate subagent dispatches (pipeline, review) (REQ-ORCH-006)
- [ ] Pipeline dispatch front-loads decisions and includes a non-interactivity clause forbidding questions and fabricated consent (REQ-ORCH-007)
- [ ] Orchestrator assigns IDs centrally and passes them verbatim to pipeline subagents (REQ-ORCH-008)
- [ ] Review dispatch carries only the permitted paths-only input set and excludes all prohibited inputs (REQ-ORCH-009)
- [ ] Research-stage review dispatch omits the upstream/kickoff path; later stages supply it (REQ-ORCH-010)
- [ ] A human gate follows every stage with proceed │ loop-back-to-fix │ stop; no auto-advance (REQ-ORCH-011)
- [ ] Fix loop re-dispatches the pipeline with only findings + artifact paths, then re-reviews (REQ-ORCH-012)
- [ ] Review verdicts are never written to disk; no `docs/reviews/` directory (REQ-ORCH-013)
- [ ] Resume derives loop position from existing phase detection; no marker file, no authoritative loop log (REQ-ORCH-014)
- [ ] v1 runs all stages sequentially in the main workspace (REQ-ORCH-015)
- [ ] Deferred fan-out rule documented: independent plan chunks, one worktree per group, sequential merge to main (REQ-ORCH-016)
- [ ] Replan triggers surface to the operator as gate events, not silently absorbed (REQ-ORCH-017)
- [ ] A reject verdict with no actionable findings pauses for an operator decision (REQ-ORCH-018)
- [ ] Skill is a single `SKILL.md` under ~500 lines with templates in `references/` (REQ-ORCH-019)
- [ ] Operator guide `skills/sdd-orchestrate/USAGE.md` exists covering when-to-use, the four phases, a complete worked example, isolation, installation via `~/.claude/skills/` symlink, troubleshooting (write fallback), and v1 limitations (REQ-ORCH-020)
- [ ] README introduces `sdd-orchestrate`, links the operator guide, and documents the `~/.claude/skills/` symlink install convention (REQ-ORCH-021)
- [ ] Markdown well-formed; frontmatter valid; kebab-case skill name (project quality checks)
