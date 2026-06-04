# Dual-Session SDD Orchestration — Design

**Date:** 2026-06-03
**Status:** Draft (brainstorming output, pending RS-005 research cycle)
**Author:** Pankaj Jangid (with Claude)

## Problem

The SDD skill set (9 skills) is run today as an ad-hoc manual flow: the operator
invokes each `sdd-*` skill in turn, and occasionally invokes `sdd-review` in a
separate session for an external read. There is no defined workflow for the
pattern the operator actually wants:

1. Evolve an idea collaboratively with the AI until both share an understanding.
2. Emit a kickoff prompt that starts the SDD pipeline.
3. Run the pipeline.
4. After **each** stage, have a fresh, context-isolated reviewer check the
   stage's output via `sdd-review`, with back-and-forth until the stage is sound.

The missing surface area is a **driver** that ties the existing skills into this
loop, plus the **isolation discipline** and **handoff conventions** that make the
per-stage external review trustworthy.

## Non-Goals

- Replacing or rewriting any existing `sdd-*` skill. The driver dispatches them.
- Two literal human-driven terminal sessions. Superseded by the orchestrator +
  subagent model below.
- Persisting review reports to disk (preserves the existing Q-REQ-B decision:
  no `docs/reviews/`).
- Review automation/auto-triggering of the pipeline without a human gate.

## Key Decisions

| # | Decision | Rationale |
|---|----------|-----------|
| D1 | Single human session (the **orchestrator**) drives; pipeline stages and reviews run as **subagents**, not as a second human session. | Eliminates copy-paste between terminals; gives isolation by construction (see D2). Chosen over disk-relay and copy-paste handoff models. |
| D2 | The **review subagent** receives only: path(s) to the deliverable, path to the upstream artifact, and "invoke `sdd-review`." Never the orchestrator's reasoning or the pipeline subagent's chain-of-thought. Pipeline and review are always **separate dispatches**. | A subagent starts with a fresh context window — there is no shared window to leak through, a *stronger* guarantee than two human sessions. Directly satisfies Q-REQ-C (Claude cannot self-detect context contamination). |
| D3 | Human gates **every** stage: after `pipeline → review`, the orchestrator shows the verdict and waits for `proceed │ loop-back-to-fix │ stop`. | Operator's explicit choice ("you at every gate"); matches the "back and forth" intent. |
| D4 | Reviews are **ephemeral** — the verdict is the review subagent's return text, surfaced to the operator, not written to disk. | Preserves Q-REQ-B. Decisions land in the artifacts themselves (commits, Q-IMPL entries, replan triggers). |
| D5 | `docs/handoff/kickoff.md` is the **only** new on-disk artifact. Stage outputs are the normal SDD artifacts, which already serve as the message bus between pipeline and review. | Minimal new convention; git-trackable; traceable. |
| D6 | **Worktree isolation** is used only when the implement stage fans out into **multiple parallel** pipeline subagents. Sequential stages (all doc stages, and single-threaded implementation) run in the main workspace. Review subagents are read-only and never need a worktree. | Worktrees add merge overhead; only justified when concurrent writers would conflict. |
| D7 | This feature is built by **dogfooding** the workflow itself: the terminal of this brainstorming is an RS-005 research kickoff prompt, not a jump to `writing-plans`. | The operator invoked `/sdd-research`; the project's own SDD methodology inserts research → requirements → specs → plan before implementation. User instructions override the brainstorming skill's default terminal. |

## Architecture

A new skill, working name **`sdd-orchestrate`**, at
`skills/sdd-orchestrate/SKILL.md`. It is a **driver**, not a phase skill — it
composes the existing nine.

### Phases of the driver

```
DISCUSS  — orchestrator + operator brainstorm the idea to a shared understanding
           (borrows the brainstorming process; converges on scope and questions)
   ↓
KICKOFF  — orchestrator writes docs/handoff/kickoff.md: the research kickoff prompt
           that the pipeline will start from
   ↓
LOOP     — for each stage in [research, requirements, specs, plan, implement, verify]:
             1. PIPELINE subagent  → fresh ctx; invokes sdd-<stage>; writes the
                                      stage's SDD artifact(s) to disk
             2. REVIEW subagent    → fresh ctx; fed ONLY {deliverable path,
                                      upstream artifact path, "invoke sdd-review"};
                                      returns a tiered verdict
             3. GATE (operator)    → orchestrator surfaces the verdict and waits:
                                      proceed │ loop-back-to-fix │ stop
             4. if fix → re-dispatch PIPELINE subagent with the review findings
                         (and only the findings + artifact paths); back to step 2
   ↓
DONE     — verify stage passes review AND operator approves
```

### Components

| Unit | Purpose | Inputs | Outputs |
|------|---------|--------|---------|
| Orchestrator (the skill body) | Drive the loop, enforce isolation discipline, mediate gates | Operator dialogue | Subagent dispatches, gate prompts |
| Kickoff writer | Turn the converged discussion into a research kickoff prompt | Discussion outcome | `docs/handoff/kickoff.md` |
| Pipeline subagent | Execute one SDD stage | Stage skill name + kickoff or prior artifacts + (on fix) review findings | SDD artifact(s) on disk |
| Review subagent | Externally review one stage's output | Deliverable path + upstream artifact path | Ephemeral tiered verdict (return text) |

### Data flow

```
operator ⇄ orchestrator
                │ writes
                ▼
        docs/handoff/kickoff.md ──► pipeline subagent ──► docs/<sdd artifact>
                                                               │
                                          (paths only) ────────┤
                                                               ▼
                                                      review subagent
                                                               │ return text
                                                               ▼
                                                    orchestrator → operator (gate)
```

## Isolation Discipline (normative)

The driver MUST:

1. Dispatch the pipeline and the review as **two separate subagents** per stage.
2. Construct the review subagent prompt from **artifact paths only**. It MUST NOT
   include: the orchestrator's conversation, the pipeline subagent's reasoning,
   kickoff prose beyond the artifact itself, draft/intermediate states, or any
   "here's what I was thinking" framing.
3. On a fix loop, pass the pipeline subagent **only** the review findings plus
   artifact paths — not a re-litigation of the reviewer's reasoning.

These mirror `sdd-review`'s Step 2 "Do NOT accept as inputs" list, enforced at
dispatch time by the driver rather than relying on operator vigilance.

## Error Handling / Edge Cases

- **Review raises FAIL with no actionable findings** → orchestrator pauses; the
  operator decides whether to re-dispatch, override, or stop.
- **Pipeline subagent triggers a replan** (stuck detection, spike invalidation) →
  surfaces to the operator as a gate event; loop may route back to an earlier
  stage via `sdd-replan`, consistent with the cyclic SDD model.
- **Stage produces a stale downstream artifact** → the stage skills already
  detect staleness; the driver does not duplicate that logic, it relays the
  skill's output.
- **Implement stage fans out** → only then are worktree subagents used; the
  driver merges their branches before the implement-stage review.

## Open Questions (for RS-005 to resolve)

- Q1: Is `sdd-orchestrate` one skill, or a skill plus a thin "kickoff-writer"
  sub-skill? (Lean: one skill, under the ~500-line guideline.)
- Q2: Does the driver need its own phase-detection/resume (operator re-enters
  mid-loop in a new session)? If so, what on-disk marker records loop position?
- Q3: How does the implement-stage parallel fan-out decide *how many* subagents
  and along what boundaries (per-milestone? per-task?) before worktrees apply.
- Q4: Should the kickoff writer support non-research entry points (e.g. operator
  already has requirements and wants to start the loop mid-pipeline)?

## Verification Criteria

- A driver skill exists and, given an idea, runs DISCUSS → KICKOFF → per-stage
  LOOP with a human gate at each stage.
- The review subagent provably receives only artifact paths (inspect the dispatch
  prompt).
- No `docs/reviews/` directory is created; reviews remain ephemeral.
- `docs/handoff/kickoff.md` is produced and git-tracked.
- Worktrees appear only for parallel implement-stage fan-out.
- Existing `sdd-*` skills are unmodified except where RS-005 requirements say
  otherwise.
