---
id: RS-005
status: Complete
date: 2026-06-04
questions:
  - "Can a subagent reliably invoke an sdd-* skill and execute a full stage (write artifacts to disk)? Failure modes?"
  - "What is the concrete review-subagent prompt template that carries only artifact paths, and does it prevent leakage?"
  - "On mid-loop re-entry, what on-disk marker records loop position — is docs/handoff/ + SDD staleness enough?"
  - "What determines parallel implement fan-out boundaries (per-milestone vs per-task) and the merge strategy?"
  - "Can one SKILL.md hold the whole driver under ~500 lines, or does the kickoff-writer belong in a sub-skill?"
budget: "~1 hour; prototype only Q1 and Q2 (riskiest). Negative Q1 = pivot signal."
research_refs: [RS-004]
---

# Research: `sdd-orchestrate` Feasibility (Dual-Session SDD Orchestration)

Inputs: the settled design `docs/superpowers/specs/2026-06-03-dual-session-sdd-orchestration-design.md`
(decisions D1–D7 are fixed). This spike resolves the design's four Open Questions
(Q1–Q4 there) plus the two riskiest feasibility unknowns via real subagent
dispatches.

## Questions

1. Subagent skill invocation (feasibility — riskiest, pivot trigger).
2. Isolation enforcement at dispatch (concrete template + leakage proof).
3. Loop resume / phase detection (design Q2).
4. Parallel implement fan-out + worktrees (design Q3).
5. Driver vs. sub-skill packaging (design Q1).

## Findings

### Q1 — Subagent skill invocation: **FEASIBLE**
**Answer**: A subagent dispatched via the Agent tool can reliably (a) access the
`Skill` tool, (b) load an `sdd-*` skill's body into context, and (c) write SDD
artifacts to disk. **No pivot needed.** The one real hazard is *interactivity*,
not invocation — and it is fully solvable at dispatch time.

**Evidence**: A real `general-purpose` subagent dispatch:
- Confirmed `Skill` tool present in its toolset (surfaced via the available-skills system-reminder).
- Invoked `sdd-research`; the full SKILL.md body loaded synchronously (proof quote: *"You are conducting a time-boxed research spike to reduce uncertainty."*). The Skill tool returns immediately — it injects instructional text, it does not block.
- Wrote a valid artifact to `prototype/q1-probe-artifact.md` ("File created successfully").

**The core hazard — interactivity deadlock**: `sdd-*` skills are written for an
*interactive* operator (they say "Ask the user: …"). A non-interactive subagent
has no user to ask, producing one of two bad outcomes: (1) **stall** — emits
questions and ends its turn waiting forever; or (2) **hallucinated consent** —
invents answers and produces artifacts the operator never sanctioned. This is
*behavioral*, not mechanical — nothing blocks at the tool layer.

**Mitigation (must be encoded in the driver's dispatch prompt)**:
- Front-load every Step-1 decision the skill will ask for (question, success
  criterion, explicit budget, deliverable contract).
- Pin all IDs and the absolute working directory in the prompt (phase detection
  reads `docs/.sdd-version` and artifacts relative to cwd; wrong cwd → silent
  misdetection; parallel subagents scanning for the next `RS-NNN` will collide —
  the orchestrator must assign IDs centrally).
- Add a non-interactivity clause: *"Do not ask questions. If information is
  missing, record it under Open Questions and proceed with a stated default —
  never invent requirements."*
- Always include the labeled-content fallback for write-scope denials.

**Confidence**: **High** — proven end-to-end with a live dispatch.

### Q2 — Isolation enforcement at dispatch: **HOLDS BY CONSTRUCTION**
**Answer**: A review subagent fed *only* `{repo_root, deliverable_path,
"invoke sdd-review"}` produces a complete, correct tiered verdict, and an input
audit confirms **zero leakage** of orchestrator/pipeline reasoning. Isolation is
a *stronger* guarantee than two human sessions (D2): a freshly dispatched
subagent has **no shared context window to leak through**.

**Evidence**: A real review-subagent dispatch reviewed `RS-004/findings.md` given
only its path + repo root. It:
- Produced a proper sdd-review verdict (Approve, with M1/m1/m2 tiered findings —
  it even independently caught a real "4 of 7 phase boundaries" inconsistency and
  a kickoff-as-input contradiction).
- Obtained all context (research questions, commit history, the shipped skill) by
  **reading files itself**, not from the prompt.
- Self-audited "INPUTS RECEIVED": **No** to every prohibited category
  (conversation history, kickoff/planning notes, drafts, author reasoning,
  anything beyond paths).

**Concrete templates**: see `prototype/dispatch-templates.md` (PIPELINE and
REVIEW). Key nuance discovered: **for the research stage, OMIT the upstream
path** — the upstream is the kickoff, which `sdd-review` Step 2 explicitly
prohibits as a contaminating input. The reviewer instead reads the research
questions from the deliverable's own frontmatter. For later stages the upstream
SDD artifact (requirements/specs) *is* a permitted, non-leaking input.

**Confidence**: **High** — proven with a live dispatch + explicit leakage audit.

### Q3 — Loop resume / phase detection: **NO NEW MARKER NEEDED**
**Answer**: `docs/handoff/kickoff.md` + existing SDD artifact staleness is
**sufficient** to resume mid-loop. No new on-disk loop-position marker is
required for correctness.

**Reasoning**: Loop position is already fully encoded on disk. Every `sdd-*`
skill performs phase detection from artifact existence + status + staleness
(verified in CLAUDE.md's phase table and in each skill's "Phase Detection"
section). The orchestrator derives the same position by the same means. The only
thing *not* on disk is the per-stage **review verdict** and the **gate decision**
— but those are ephemeral by design (D4) and **reproducible**: reviews are
read-only, idempotent, and cheap, so on re-entry the orchestrator simply
re-dispatches the review subagent against the current artifacts to re-derive the
verdict, then re-presents the gate. Nothing is lost.

**Recommendation**: Do not add a loop-state file. *Optionally*, append a
human-facing one-line "loop log" to `kickoff.md` (`- specs: pipeline ✓, review
looped 1x, gate: proceed (2026-06-04)`) purely for operator convenience — but the
driver MUST treat artifacts as the source of truth, never the log. This keeps D5
intact (kickoff.md the only new artifact).

**Confidence**: **High** for "no marker needed" (follows directly from the
existing, already-shipped phase-detection mechanism); Medium on whether the
optional loop-log earns its keep (decide in requirements).

### Q4 — Parallel implement fan-out + worktrees: **fan out along independent plan chunks; merge sequentially**
**Answer**: Boundaries are **neither blindly per-milestone nor per-task** —
they are the **independent branches of the plan's dependency graph**, which the
plan already expresses as **chunks** (`### Chunk N:` work units of ~5–15h) within
delivery milestones.

**Evidence (from inspecting the shipped plan/implement skills)**:
- `sdd-plan` Step 4 builds an explicit dependency graph and Step 5 groups tasks
  into **chunks** and **delivery milestones**. Milestones are sequential by
  intent (each yields a testable system built on the prior) → too coarse and
  usually dependent. Tasks are too fine (TDD inner loop + intra-chunk ordering is
  sequential). **Chunks** are the right granularity: declared, dependency-aware,
  sized for a single subagent.
- `sdd-implement` has **no existing parallel/fan-out concept** — it is sequential
  by default. So the **orchestrator owns the fan-out decision externally**: it
  reads the plan's dependency graph, finds chunk-groups with no cross-dependency,
  and dispatches one worktree subagent per concurrently-runnable group. This
  reads artifacts only — it does **not** modify `sdd-implement` (respects the
  design's non-goal).

**Merge strategy**: One worktree per parallel chunk-group (D6 — worktrees *only*
here). Merge branches back to `main` **sequentially** before the implement-stage
review (project CLAUDE.md mandates merge over rebase; the orchestrator resolves
conflicts at merge time). The implement-stage review subagent then reviews the
**merged** state on main — never per-worktree partials.

**Default stays sequential**: fan-out triggers only when the dependency graph
*actually* has independent chunk branches; otherwise single-threaded in the main
workspace (D6).

**Confidence**: **Medium-High** — grounded in the shipped plan/implement
conventions; not prototyped (parallel fan-out wasn't in the Q1–Q2 budget). The
exact "independent chunk-group" detection rule should be pinned in specs.

### Q5 — Driver vs. sub-skill packaging: **one SKILL.md, templates in a `references/` file**
**Answer**: One `SKILL.md` can hold the whole driver under the ~500-line
guideline. The kickoff-writer does **not** warrant a separate skill.

**Evidence**: Existing `sdd-*` skills run 162–291 lines (largest: `sdd-migrate`
291). The driver's body — DISCUSS/KICKOFF/LOOP/DONE phases, the normative
isolation discipline, the gate protocol, error/edge handling — is comparable in
scope to `sdd-implement` (267) or `sdd-requirements` (272), call it ~300–400
lines. The two dispatch prompt templates (~60 lines) are the bulkiest single
component; moving them to `skills/sdd-orchestrate/references/dispatch-templates.md`
keeps the body lean and well under 500. The kickoff-writer (DISCUSS→KICKOFF) is a
small, contained sub-task (~50–80 lines, borrows the brainstorming process and
writes one file) and is **not independently reusable**, so a separate skill would
add a discovery surface for no reuse benefit — a `references/` split is the right
tool, not a sub-skill.

**Confidence**: **High** for "fits in one skill"; the `references/` split is a
recommendation to confirm during implementation if the body approaches the limit.

## Implications for Design

- **Greenlight `sdd-orchestrate`.** The two riskiest unknowns (subagent skill
  execution, dispatch isolation) are proven positive with live dispatches. No
  pivot.
- **Requirements must mandate a non-interactivity contract** for pipeline
  dispatches (front-loaded decisions + "don't ask, don't fabricate" clause +
  central ID assignment + absolute cwd). This is the single highest-risk surface.
- **Research-stage review is a special case**: the review dispatch omits the
  upstream (kickoff) path; the reviewer reads questions from the findings
  frontmatter. Encode this per-stage variation, don't use one flat template.
- **No new resume marker** — rely on existing phase detection; keep `kickoff.md`
  as the only new artifact (D5 preserved). Optional ephemeral loop-log is a
  convenience, not a mechanism.
- **Fan-out boundary = independent plan chunks**, orchestrator-driven, merged
  sequentially to main before the implement-stage review; `sdd-implement`
  unmodified.
- **Package as one skill** + a `references/dispatch-templates.md`.

### Viable vs. ruled out
- **Viable**: single-orchestrator + per-stage pipeline/review subagent dispatch
  (D1/D2); artifacts-as-message-bus (D5); ephemeral reproducible reviews (D4).
- **Ruled out**: relying on operator vigilance for isolation (unnecessary —
  isolation is structural); a dedicated loop-position state file (redundant with
  phase detection); fanning out per-milestone (too coarse) or per-task (too fine).

## Prototype

Two **live subagent dispatches** (not throwaway-branch code):
- **Q1 probe** — a `general-purpose` subagent invoked `sdd-research` and wrote
  `prototype/q1-probe-artifact.md`. Demonstrates: Skill-tool access, skill
  loading, disk write. Does not prove a *full interactive* stage runs unattended
  — that's exactly why the non-interactivity contract is required.
- **Q2 probe** — a review subagent fed only paths reviewed `RS-004/findings.md`,
  produced a correct tiered verdict, and self-audited zero input leakage.
  Demonstrates dispatch-time isolation. Templates captured in
  `prototype/dispatch-templates.md`.

## Open Questions

- **Q4 fan-out is reasoned, not prototyped** — the precise "independent
  chunk-group" detection + sequential-merge-conflict handling should be pinned in
  specs (and ideally a small spike during implementation) before the parallel
  path ships.
- **Optional loop-log in kickoff.md** — decide in requirements whether the
  human-facing convenience justifies the (tiny) convention.
- **Pipeline subagent depth limits** — a stage that itself triggers `sdd-replan`
  or its own sub-dispatches wasn't exercised; confirm nesting behavior when the
  implement stage internally fans out (subagent-spawning-subagent).
