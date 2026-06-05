---
id: RS-006
status: Complete
date: 2026-06-04
questions:
  - "Nested dispatch: can a subagent dispatched via the Agent tool itself dispatch sub-subagents? Is there a depth limit or harness policy blocking it?"
  - "Worktree creation by a subagent: can a dispatched subagent create and work inside a git worktree, or must worktrees be orchestrator-owned?"
  - "Merge-back + conflict handling: what is the concrete mechanism to merge parallel worktree branches sequentially to main, and is automatic-resolution-with-redo-at-orchestrator a workable fallback?"
  - "Decisive outcome: does nesting work (pipeline subagent owns fan-out) or not (orchestrator owns fan-out, one level deep), and which design does the evidence select?"
budget: "~1 hour; prototype Q1-Q2"
---

# Research: Subagent nesting & worktrees (→ implement-stage fan-out)

## Questions

This spike de-risks the **parallel implement-stage fan-out** feature for
`sdd-orchestrate` (REQ-ORCH-016, deferred). The result picks between two fan-out
designs, so it must run before requirements/specs for fan-out:

- **Design A (nested):** a pipeline implement subagent itself owns the fan-out,
  spawning one sub-subagent per concurrently-runnable chunk-group (nesting two
  levels deep below the operator).
- **Design B (orchestrator-owned fallback):** the orchestrator owns the fan-out
  directly, dispatching parallel implement subagents itself (nesting one level
  deep). This is the documented Plan B.

Four questions:

1. **Nested dispatch** — Can a dispatched subagent itself dispatch sub-subagents?
   Depth limit or harness policy?
2. **Worktree creation by a subagent** — Can a subagent create and work inside a
   git worktree, or must worktrees be orchestrator-owned?
3. **Merge-back + conflict handling** — Mechanism to merge parallel worktree
   branches sequentially to `main`; is automatic-resolution-with-redo-at-orchestrator
   a workable fallback?
4. **Decisive outcome** — Which design does the evidence select?

## Scope

Per the kickoff, this is a **de-risking spike only**. It does **not** write the
parallel implement-stage fan-out feature (REQ-ORCH-016) and does **not** modify
`sdd-implement` (or any other shipping skill). Its deliverable is the design
selection and supporting evidence below; the fan-out requirements, specs, and
implementation are out of scope and follow in their own SDD phases.

## Findings

### Q1 — Nested dispatch

**Answer**: A dispatched pipeline subagent **cannot** dispatch sub-subagents. The
subagent-dispatch tool (the Agent / Task-dispatch capability the orchestrator
used to spawn this subagent) **is not provisioned into a subagent's toolset**.
Nesting is blocked by tool availability, not by a runtime depth counter.

**Evidence**: Running as a real dispatched pipeline subagent, I enumerated my own
toolset via `ToolSearch` with several queries targeting any dispatch capability
(`select:Task,TaskCreate`, `+agent dispatch subagent`, `+task spawn launch
parallel agent run`, `dispatch subagent isolation worktree parallel fan-out`).
The only "Task"-named tools surfaced are the **todo-list** tools —
`TaskCreate`, `TaskList`, `TaskGet`, `TaskUpdate`, `TaskStop` — whose schemas
describe a session todo list ("create a structured task list for your current
coding session... track progress"), not subagent dispatch. No `Agent` tool, no
sub-agent / sub-task dispatch tool, and no parallel-agent tool appears anywhere
in the deferred-tool catalog available to me. Because the dispatch tool is absent
from the schema, there is nothing to call: a real nested dispatch attempt cannot
even be issued (the tool name does not exist to invoke). This is the
"blocked-by-harness-policy" outcome — the policy is implemented as
tool-provisioning: dispatch is an orchestrator-only capability.

Note on the prototype: the kickoff asked to "actually call the Agent tool to
spawn a trivial sub-subagent." That call is not constructible because no such
tool is exposed to this subagent — which is itself the decisive negative result,
equivalent to a blocked attempt with the message "no dispatch tool available in
this agent's toolset."

**Confidence**: High. Determined by direct inspection of the live subagent's own
tool catalog (the authoritative source), not by inference. The negative is the
expected, design-selecting outcome per the kickoff.

### Q2 — Worktree creation by a subagent

**Answer**: A dispatched subagent **can** create a git worktree, write files in
it, and commit on its branch — via plain `git worktree add` to a scratch path
under `/tmp/claude`. Worktrees do **not** have to be orchestrator-owned.

**Evidence**: Real attempt from inside this subagent:

- `git worktree add -b research/rs006-scratch /tmp/claude/rs006-wt-test HEAD` →
  `Preparing worktree (new branch 'research/rs006-scratch')`, exit `0`.
- `git worktree list` then showed the new worktree on its own branch alongside
  the main checkout.
- Inside the worktree I wrote `scratch.txt`, `git add`, and committed
  (`git -C ... commit`) → commit `6fa24db` created successfully on the branch.
- Cleanup: `git worktree remove --force` for every scratch worktree and
  `git branch -D` for every branch all succeeded; final `git worktree list`
  shows only the original checkout, no `rs006*` branches remain.

Caveat (sandbox-specific, not a worktree limitation): writes to the **main
repo's `.git/config`** are blocked by the command sandbox
("Operation not permitted"), so `git -C <wt> config user.email ...` fails and
`git branch -D` prints a cosmetic config-update warning. Worktree creation,
file writes, commits (using inline `-c user.email=... -c user.name=...`), merges,
and branch deletion all still complete. The orchestrator (running with the
operator's normal git identity, not under this restriction) will not hit the
config write block; a subagent can sidestep it with inline `-c` identity flags.

**Confidence**: High. Proven end-to-end with real `git worktree` commands and
verified cleanup.

### Q3 — Merge-back + conflict handling

**Answer**: The concrete mechanism is: each fan-out worktree commits on its own
branch; the owner (per Q4, the orchestrator) merges those branches **sequentially**
into an integration branch / `main` with `git merge --no-edit <branch>` one at a
time. Clean merges (different files) fast-forward or auto-merge silently;
conflicts surface deterministically and are easy to detect. The
**automatic-resolution-with-redo-at-orchestrator-level fallback is workable.**

**Evidence**: Real simulation of three parallel fan-out branches off one base:

- Branch A adds `fileA.txt`, Branch B adds `fileB.txt` (disjoint), Branch C adds
  a **divergent** `fileA.txt` (overlaps A).
- Sequential merge into an integration branch:
  - merge A → `Fast-forward`, exit `0` (clean).
  - merge B → `Merge made by the 'ort' strategy`, exit `0` (clean, disjoint file).
  - merge C → `CONFLICT (add/add): Merge conflict in fileA.txt`,
    `Automatic merge failed`, exit `1`.
- Conflict is **detectable four ways**: non-zero exit code (1), the
  `CONFLICT (...)` stderr message, `git status --porcelain` showing `AA fileA.txt`,
  and `<<<<<<< HEAD ... ======= ... >>>>>>> rs006-branchC` markers in the file.
- Redo fallback: `git merge --abort` cleanly restored the tree
  ("abort ok; tree restored", clean porcelain status afterward).

So the orchestrator's loop is: merge branches one at a time; on exit code 0
continue; on exit code 1, either auto-resolve (e.g. re-run / regenerate the
losing chunk) or `git merge --abort` and hand the conflicting chunk back for a
redo at orchestrator level. Because merges are sequential and each conflict is
isolated to a single `git merge` invocation, abort/redo never corrupts already-merged
work — the fallback is clean and bounded.

**Confidence**: High. Proven with a real conflicting/non-conflicting merge
sequence and a successful abort.

### Q4 — Decisive outcome

**Answer**: **Nesting does not work → the orchestrator owns the fan-out, one
level deep (Design B, the documented fallback).** The evidence selects
**Design B (orchestrator-owned fan-out).**

**Evidence**: Q1 establishes that a dispatched subagent has no dispatch tool, so
a pipeline implement subagent **cannot** spawn the per-chunk sub-subagents that
Design A requires. Q2 and Q3 establish that the pieces Design B needs — worktree
creation and sequential merge with a clean conflict-abort fallback — all work and
can be driven by the orchestrator (and even by a single agent directly). The only
viable design is therefore the orchestrator dispatching parallel implement
subagents itself, one level deep, then merging their branches sequentially.

**Confidence**: High. Q1 is the decisive constraint; Q2/Q3 confirm the fallback
is fully implementable.

## Implications for Design

- **Selected design: B — orchestrator-owned fan-out, one level deep.** Write the
  REQ-ORCH-016 fan-out requirements against this design. Do **not** spec a nested
  implement-subagent-owns-fan-out path; it is infeasible in this harness.
- **Fan-out topology:** the orchestrator (operator session driving
  `sdd-orchestrate`) reads the plan's independent chunk-dependency branches and
  dispatches **one implement subagent per concurrently-runnable chunk-group**,
  each pinned to its own worktree/branch. Subagents are leaves; they do not
  themselves fan out.
- **Worktree ownership:** either the orchestrator pre-creates one worktree per
  chunk-group and pins each subagent to it, or each subagent creates its own
  worktree under a scratch path. Q2 shows both work; orchestrator-pre-created is
  cleaner for lifecycle/cleanup ownership. Subagents should use inline
  `git -c user.email=... -c user.name=...` to avoid touching shared `.git/config`.
- **Merge policy:** orchestrator merges branches **sequentially into `main`
  before** the implement-stage review (matches kickoff in-scope policy). Detect
  conflict via `git merge` exit code; on conflict, attempt automatic resolution,
  else `git merge --abort` and redo the offending chunk at orchestrator level.
  This is proven safe because earlier sequential merges are already committed and
  an abort only unwinds the single failing merge.
- **Opt-in gate:** fan-out stays opt-in at the implement gate (not automatic),
  per kickoff scope.
- **Ruled out:** Design A (nested subagent fan-out). No tooling exists for it.

## Prototype

All prototypes were **real** and run from inside this live dispatched subagent;
no throwaway branch was merged to `main`; all scratch artifacts were removed.

- **Q1 (negative, by tool inspection):** enumerated the subagent's own tool
  catalog via `ToolSearch`; confirmed no `Agent`/dispatch tool exists — only the
  todo-list `Task*` tools. A nested dispatch call is not constructible.
- **Q2 (positive):** `git worktree add -b research/rs006-scratch
  /tmp/claude/rs006-wt-test HEAD` (exit 0); wrote + committed `scratch.txt`
  (commit `6fa24db`) on the worktree branch; verified in `git worktree list`.
- **Q3 (positive):** created 3 parallel branches off one base in scratch
  worktrees; sequential `git merge` of two disjoint-file branches (clean,
  fast-forward + ort) and one overlapping branch (`CONFLICT (add/add)`, exit 1,
  `AA` status, conflict markers); `git merge --abort` cleanly restored the tree.
- **Cleanup:** `git worktree remove --force` for all 5 scratch worktrees +
  `git branch -D` for all 5 branches; final `git worktree list` shows only the
  original checkout and no `rs006*` branches remain.

## Open Questions

- **Parallel subagent dispatch from the orchestrator:** Q1 proves subagents can't
  dispatch, and RS-005 already proved the orchestrator can dispatch subagents.
  Whether the orchestrator can run **multiple** implement subagents truly
  concurrently (vs. issued-together-but-serialized) was not re-measured here.
  Default assumption for requirements: treat orchestrator-driven fan-out as
  *issued in one batch*; if the harness serializes execution, the design still
  holds (worktree isolation + sequential merge are unchanged) — only wall-clock
  speedup varies. Confirm during specs/implementation if speedup is a hard
  requirement. *(Forward pointer: RS-005 already characterized the
  orchestrator's fan-out boundaries — see RS-005 for the dispatch-concurrency
  envelope; this spike does not re-open that territory.)*
- **Sandbox `.git/config` write block:** observed in this subagent's command
  sandbox. The operator/orchestrator session is not expected to have this
  restriction; if a future subagent-driven git step needs config writes, prefer
  inline `-c` flags. Not a blocker for Design B.
