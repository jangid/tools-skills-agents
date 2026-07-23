# `sdd-orchestrate` — Operator Guide

This is the **human-facing** guide to the `sdd-orchestrate` driver. The companion
[`SKILL.md`](SKILL.md) is the Claude-facing operational instruction; this file
explains how *you*, the operator, drive a cycle and what to expect at each step.

---

## 1. What it is

`sdd-orchestrate` runs the nine SDD phase skills (research → requirements →
specs → plan → implement → verify, plus replan/migrate/review) as a **single
operator-driven loop with built-in external review**. You stay in one session.
For each stage the driver dispatches two *separate, context-isolated* subagents —
one that does the work, one that reviews it — and then stops at a **gate** so you
can decide whether to proceed.

It is a **driver**, not a tenth phase skill: it composes the existing skills and
never reimplements them.

### When to use it
- You want to take an idea through a whole SDD cycle end-to-end.
- You want each stage independently reviewed by a reviewer that has **not** seen
  the working session's reasoning (catches scope/coherence gaps in-session checks
  miss).

### When **not** to use it
- You only need one phase → invoke that `sdd-*` skill directly.
- You only want to review one finished artifact → use `sdd-review`.

---

## 2. Installation

Claude Code discovers skills from `~/.claude/skills/`. This project keeps the
source of truth in the repo and **symlinks** each skill into that directory, so
edits to the repo are immediately live.

Install (or re-install) every SDD skill, including this one:

```bash
REPO="$HOME/work/github/jangid/tools-skills-agents"   # adjust to your checkout
for d in "$REPO"/skills/*/; do
  name="$(basename "$d")"
  ln -sfn "$d" "$HOME/.claude/skills/$name"
done
ls -l ~/.claude/skills/        # each entry should point back into the repo
```

To install just this skill:

```bash
ln -sfn "$HOME/work/github/jangid/tools-skills-agents/skills/sdd-orchestrate" \
        "$HOME/.claude/skills/sdd-orchestrate"
```

Notes:
- `ln -sfn` is idempotent — safe to re-run when you add a new skill or move the
  checkout. Re-run it whenever a **new skill** is added to `skills/` so its link
  appears in `~/.claude/skills/`.
- Skills are loaded at **session start**. After adding a link, start a new
  Claude Code session for the skill to become invocable.
- Verify with `ls -l ~/.claude/skills/` — every `sdd-*` entry should be a symlink
  back into `…/tools-skills-agents/skills/<name>`.

---

## 3. Invoking and driving the loop

You invoke the driver **once** and then mostly just talk to it. You do **not**
invoke each `sdd-*` skill yourself — the orchestrator does that for you.

### Start it

In a Claude Code session, either run the slash command:

```
/sdd-orchestrate
```

or ask in plain language:

> Use sdd-orchestrate to take "<your idea>" through a full SDD cycle.

Either way, Claude loads the driver and becomes the **orchestrator** for the rest
of the session.

### Then: discuss (DISCUSS)

The orchestrator opens by brainstorming the idea with you. Just talk — answer its
clarifying questions, push back, refine scope. Nothing is written to disk yet.
When you and it share an understanding of the scope and the open questions, DISCUSS
is done.

### Then: it picks up the loop on its own

Once you've converged, the orchestrator runs the rest **autonomously**, pausing
only at the gates:

1. It writes the kickoff (KICKOFF): `docs/handoff/kickoff.md` under marker `3`,
   or `docs/ws/<id>/kickoff.md` for the selected workstream under marker `4`.
2. For each stage (research → requirements → specs → plan → implement → verify) it
   dispatches the **pipeline** subagent, then the **review** subagent, handling
   skill invocation, ID assignment, paths, and isolation for you.
3. It **stops at each gate**, shows you the review verdict, and waits for your
   one-word decision: **proceed**, **loop-back-to-fix**, or **stop**.

So after DISCUSS your job shrinks to making gate decisions. You are not copy-
pasting between sessions or remembering which skill comes next — the orchestrator
sequences the whole loop and only ever hands control back at a gate.

### A typical exchange (abridged)

```
you  > /sdd-orchestrate
      Idea: add a --dry-run flag to the deploy tool.
orch > A few questions before I write a kickoff:
       - dry-run prints the plan only, or a diff?  - exit-code contract? ...
you  > plan + diff; non-zero exit if drift. partial applies are out of scope.
orch > Good — we're aligned. Writing docs/handoff/kickoff.md and starting research.
       [dispatches research pipeline → research review]
orch > GATE (research): reviewer says Approve. proceed / loop-back / stop?
you  > proceed
orch > [requirements pipeline → review]
       GATE (requirements): Approve with fixes — REQ-DRY-003 not testable. ...?
you  > loop-back-to-fix
orch > [re-dispatch with that finding → re-review] Approve now. proceed?
you  > proceed
       ... specs, plan, implement, verify, each with a gate ...
orch > DONE — verify passed review. Recommend committing the cycle.
```

### Coming back later (resume)

If you stop partway and return in a **new** session, just invoke
`/sdd-orchestrate` again. It reads the existing artifacts on disk, detects which
stage you're at (no hidden marker file), and continues the loop from there — re-
running the current stage's review if needed.

---

## 4. The four phases

```
DISCUSS ──▶ KICKOFF ──▶ LOOP ──▶ DONE
                          │
            ┌─────────────┴───────────────────────────┐
            │ per stage: pipeline ▶ review ▶ GATE      │
            └──────────────────────────────────────────┘
```

### DISCUSS
You and the orchestrator brainstorm the idea until you share an understanding of
scope and the open questions worth researching. It reuses the brainstorming
process — expect to be asked clarifying questions. Nothing is written yet.

### KICKOFF
The orchestrator writes the kickoff (`docs/handoff/kickoff.md`; marker `4`:
`docs/ws/<id>/kickoff.md`) — a **research kickoff** stating
the questions, success criteria, a budget, and what's out of scope. This is the
only new artifact type the driver introduces, and it's committed with the cycle.

### LOOP
For each stage in order, three things happen:
1. **Pipeline subagent** — a fresh subagent invokes the stage skill
   (`sdd-research`, `sdd-requirements`, …) and writes the normal SDD artifact(s).
2. **Review subagent** — a *separate* fresh subagent is given **only** the
   artifact paths and told to invoke `sdd-review`. It returns a tiered verdict.
3. **Gate** — the orchestrator shows you the verdict and waits. You choose:
   - **proceed** → next stage,
   - **loop-back-to-fix** → re-run the pipeline with just the review findings,
     then re-review,
   - **stop** → halt.

### DONE
Reached when the verify stage passes review **and** you approve. Commit the
cycle's artifacts (including the kickoff — `docs/handoff/kickoff.md`, or
`docs/ws/<id>/kickoff.md` under marker `4`).

---

## 4b. Workstreams (marker `4`)

If `docs/.sdd-version` reads `4`, the driver opens with a **workstream picker**:
it lists every `docs/ws/<id>/` workstream with its description and detected
phase, and you select one or create a new one. Several workstreams can be live
at once, each at its own phase, each on its own git branch, integrating via a
PR to `main` when complete.

- **Solo use stays ceremony-free** — a repo whose only workstream is `default`
  collapses to a picker of one; you never name anything.
- **New workstreams always start at research** — cheap when the shared corpus
  already covers the need, because research records a fast "covered by shared
  corpus" early-exit and moves on.
- **Execution artifacts move; the corpus doesn't** — kickoff/plan/verification
  live under `docs/ws/<id>/`; requirements, specs, and research stay shared at
  top level.
- **Fan-out and verification re-anchor** — implement-stage fan-out branches from
  and merges back into the *workstream branch* (`main` is untouched until the
  PR), and `sdd-verify` diffs against the workstream's branch point, not `main`
  HEAD.

Under marker `3` none of this appears — the driver runs the single flat cycle
exactly as described above.

---

## 5. A complete worked example

Idea: *"Add a `--dry-run` flag to our deploy tool."*

1. **DISCUSS.** Orchestrator: "What should `--dry-run` print — the plan only, or a
   diff? Any exit-code contract?" You converge: print the plan + non-zero exit if
   drift detected; out of scope: partial applies.
2. **KICKOFF.** Orchestrator writes `docs/handoff/kickoff.md` with the research
   questions ("does the deploy SDK expose a plan-only mode?"), a 1-hour budget,
   and scope boundaries.
3. **LOOP — research.** Pipeline subagent runs `sdd-research`, writes
   `docs/research/RS-007-dry-run/findings.md`. Review subagent (paths only) returns
   *Approve*. Gate → you say **proceed**.
4. **LOOP — requirements.** Pipeline writes the requirements; review returns
   *Approve with fixes* ("REQ-DRY-003 isn't testable"). Gate → you say
   **loop-back-to-fix**. Orchestrator re-dispatches the pipeline with just that
   finding; re-review returns *Approve*. Gate → **proceed**.
5. **LOOP — specs / plan / implement / verify.** Same rhythm. At implement, the
   pipeline runs `sdd-implement`; at verify, `sdd-verify` writes
   `docs/verification.md`. Each stage is reviewed and gated.
6. **DONE.** Verify passes review, you approve, the orchestrator recommends
   committing the cycle.

You made a decision at six gates; the reviewer never saw your reasoning, only the
artifacts on disk.

---

## 6. Isolation — why two subagents

The review subagent is dispatched with **only**: the repo root, the deliverable
path(s), and (for non-research stages) the upstream artifact path. It never
receives your conversation, the pipeline subagent's reasoning, kickoff prose, or
drafts. Because a freshly dispatched subagent starts with an empty context
window, there is *nothing to leak through* — a stronger guarantee than two human
terminals. (Caveat: the subagent still reads repo-level context like `CLAUDE.md`;
what's excluded is the working session's reasoning, not repo docs.) This is what
lets the review catch framing/scope problems an in-session check would
rationalize away.

(The research stage is special: the review dispatch omits the kickoff path,
because `sdd-review` forbids kickoff prompts as input. The reviewer reads the
research questions from the findings file's own frontmatter.)

---

## 7. Troubleshooting

| Symptom | Cause | What to do |
|---------|-------|------------|
| A pipeline subagent reports "could not write file — returning content inline" | The harness can block a subagent's disk write (especially report-style files or non-conventional paths). Observed live in RS-005. | This is expected and handled: the dispatch template's **labeled-content fallback** returns the file body; the **orchestrator persists it**. No action needed beyond confirming the artifact landed. |
| Pipeline subagent asks a question / stalls | A stage skill's "ask the user" step wasn't front-loaded. | The orchestrator must front-load the stage's question, success criterion, budget, and deliverable contract, plus a non-interactivity clause. Re-dispatch with those filled in. |
| Two artifacts collide on the same ID | A subagent picked its own ID. | The orchestrator assigns IDs centrally and passes them verbatim — never let the subagent scan-and-guess. |
| Review verdict seems to know your reasoning | Isolation leak — prohibited input slipped into the review dispatch. | Reconstruct the review dispatch from paths only (see `references/dispatch-templates.md`). |
| Review returns *Reject* with no actionable findings | Genuine reviewer uncertainty. | The driver pauses; you decide: re-dispatch, override, or stop. |
| A stage triggers a replan | Stuck detection / spike invalidation / verify failure. | It surfaces at the gate as a replan event; you may route back via `sdd-replan`. |

---

## 8. Sequential default and fan-out

### Sequential by default; implement-stage fan-out is opt-in
Every stage runs **single-threaded in the main workspace by default**. The
**implement stage** is the one exception: you can **opt into fan-out** at the
implement gate to run independent chunk-groups in parallel.

When you opt in, the orchestrator:
- derives the independent chunk-groups from the plan's chunk dependency graph
  (the `**Depends on**: Chunk N` field, or its `Entry criteria: Chunk N complete`
  prose equivalent — not milestone-level Entry/Exit),
- provisions one git worktree/branch per group and dispatches one **leaf**
  implement subagent per group (each runs `sdd-implement` and cannot fan out
  further),
- then merges the branches **sequentially** back into the integration anchor —
  `main` under marker `3`, the **workstream branch** under marker `4` (`main`
  stays untouched until the workstream PR) — completing all merges **before**
  the implement-stage review runs on the merged state, tearing down each
  worktree as it merges.

Dispatched as a single batch, the per-group subagents run concurrently (measured in
the RS-006 spike), so fan-out delivers a genuine wall-clock speedup on top of
worktree isolation.

**Single-chain degrade-to-sequential.** If the plan's chunk graph is a single
chain (or has no parseable chunk-level dependencies), there is nothing to
parallelize. The orchestrator tells you this **at the gate** and runs the implement
stage sequentially even if you opted in — an expected outcome, not a failure.

On a merge conflict, the orchestrator runs `git merge --abort` and **redoes** the
offending group by re-running `sdd-implement` in a worktree re-branched from the
updated integration anchor (`main`, or the workstream branch under marker `4`;
best-effort auto-resolve may be tried first). If a group conflicts
*again*, that proves the groups weren't truly independent, and the orchestrator
falls back to running them sequentially — so the run always terminates and
already-merged work is never corrupted.

### Starting mid-pipeline (non-research entry)

Research is the **default** entry, but you don't have to start there. When approved
upstream artifacts already exist, you can start the loop at **requirements, specs,
plan, or implement** — e.g. you already have approved requirements and want the
gated loop for specs onward. (Verify is not an entry point — to just verify an
existing project, run `sdd-verify` directly.)

How it works: the driver **auto-detects** the furthest-complete approved artifact,
**proposes** the entry stage, and **confirms** with you (you can override to an
earlier stage); it **validates** the upstream is actually approved and otherwise
routes you to the earliest incomplete stage. KICKOFF then writes an **entry
kickoff** (scope + entry stage + assumed-approved upstream) instead of a research
kickoff. This is different from *resume* (§3): resume continues a cycle this driver
started; non-research entry begins a loop over artifacts you produced elsewhere.

### By design (not limitations)
- **Reviews are ephemeral** — verdicts are shown inline and never written to disk;
  there is no `docs/reviews/`. Decisions live in the artifacts (commits, spec
  edits, Q-IMPL entries, replan triggers). Permanent by design.

All originally-deferred features — parallel implement-stage fan-out and
non-research entry — are now built.

---

## 9. See also

- [`SKILL.md`](SKILL.md) — the driver's operational instructions
- [`references/dispatch-templates.md`](references/dispatch-templates.md) — the
  copy-ready pipeline and review dispatch prompts
- [`references/fan-out.md`](references/fan-out.md) — the implement-stage fan-out
  procedure (boundary derivation, per-group dispatch, sequential merge, teardown,
  conflict redo-by-re-derivation)
- `docs/spec/orchestration.md` — the design spec
- `docs/research/RS-005-sdd-orchestrate-feasibility/findings.md` — the feasibility
  evidence behind the isolation and non-interactivity guarantees
