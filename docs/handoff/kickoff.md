# Kickoff: RS-006 — Subagent nesting & worktrees (→ implement-stage fan-out)

Run `/sdd-research`. This spike de-risks the **parallel implement-stage fan-out**
feature for `sdd-orchestrate` (REQ-ORCH-016, currently deferred). Its result picks
between two fan-out designs, so it must run before requirements/specs for fan-out.

Driven by `sdd-orchestrate` (dogfooding). Cycle: this research spike → then
requirements → specs → plan → implement → verify for the fan-out feature.

## Research questions

1. **Nested dispatch** — Can a subagent dispatched via the Agent tool itself
   dispatch sub-subagents (nested Agent calls)? Is there a depth limit or a
   harness policy that blocks it? Prove with a minimal real nested dispatch.
2. **Worktree creation by a subagent** — Can a dispatched subagent create and work
   inside a git worktree (or use `isolation: worktree`), or must worktrees be
   created/owned by the orchestrator? What fails if a subagent tries?
3. **Merge-back + conflict handling** — When parallel worktree branches return,
   what is the mechanism to merge them sequentially to `main`, and how are
   conflicts surfaced? (Decided policy: resolve automatically; worst case the
   orchestrator takes the subagent's returned output and redoes the merge at the
   orchestrator level — verify this fallback is workable.)
4. **Decisive outcome** — Does nesting work (→ a pipeline implement subagent can
   own the fan-out) or not (→ **fallback**: the orchestrator owns fan-out
   directly, dispatching parallel implement subagents itself, nesting one level
   deep)? State which design the evidence selects.

## Success criteria

Each question has an evidence-based finding (proven with a real dispatch where
feasible) and a concrete recommendation. Enough certainty to write requirements
for implement-stage fan-out without guessing which design (nested vs
orchestrator-owned) to build.

## Budget

~1 hour. Prototype questions 1–2 (the riskiest — nested dispatch and subagent
worktree creation). A negative result on Q1 is not a blocker — it selects the
orchestrator-owned fallback design, which is already the documented Plan B.

## Downstream feature scope (informs requirements after the spike)

- **In scope**: implement-stage fan-out along the plan's **independent chunk
  dependency branches**; one worktree per concurrently-runnable chunk-group;
  **sequential merge to `main` before** the implement-stage review; **opt-in** at
  the implement gate (not automatic); **automatic** conflict resolution with the
  redo-at-orchestrator-level fallback.
- **Out of scope**: non-research entry points (separate feature); fan-out of any
  stage other than implement; changing `sdd-implement` itself.

## Out of scope (for the spike)

Writing the fan-out feature; modifying `sdd-implement`; requirements/specs (later
stages of this cycle).
