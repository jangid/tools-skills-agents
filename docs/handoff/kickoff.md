# Kickoff: RS-005 — Dual-session SDD orchestration (`sdd-orchestrate`)

Run `/sdd-research`. This spike explores how to build a **driver skill** that
runs the existing 9 SDD skills as a single-operator orchestration loop with
per-stage external review.

**Background design:**
`docs/superpowers/specs/2026-06-03-dual-session-sdd-orchestration-design.md`
(read it; decisions D1–D7 there are settled inputs, not open questions).

## Research questions

1. **Subagent skill invocation** — Can a subagent dispatched via the Agent tool
   reliably invoke an `sdd-*` skill and execute a full stage (write artifacts to
   disk)? What are the failure modes (skill not loading, missing tools, context
   limits)? Prove with a minimal real dispatch.
2. **Isolation enforcement at dispatch** — What is the concrete prompt template
   for a review subagent that carries *only* artifact paths? Verify by inspection
   that no orchestrator/pipeline reasoning leaks in. Compare against `sdd-review`
   Step 2's "Do NOT accept" list.
3. **Loop resume / phase detection** (design Q2) — If the operator re-enters
   mid-loop in a new orchestrator session, what on-disk marker (if any) records
   loop position? Is `docs/handoff/` + existing SDD artifact staleness
   sufficient, or is a new marker needed?
4. **Parallel implement fan-out + worktrees** (design Q3) — When the implement
   stage fans out into multiple subagents, what determines the boundaries
   (per-milestone vs per-task) and the merge strategy back to main before the
   implement-stage review?
5. **Driver vs. sub-skill packaging** (design Q1) — Can one `SKILL.md` hold the
   whole driver under the ~500-line project guideline, or does the
   kickoff-writer belong in a sub-skill?

## Success criteria

Each question has an evidence-based finding (proven with a real subagent dispatch
where feasible) and a concrete recommendation; enough certainty to write
requirements for `sdd-orchestrate` without guessing.

## Budget

~1 hour / explore the 5 questions; prototype only questions 1–2 (the riskiest —
subagent skill execution and isolation). A negative result on Q1 (subagents
can't reliably run skills) is a pivot signal — surface it immediately.

## Out of scope

Writing the skill itself, modifying other `sdd-*` skills, requirements/specs
(later phases).
