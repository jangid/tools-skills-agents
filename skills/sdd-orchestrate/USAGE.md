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

## 3. The four phases

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
The orchestrator writes `docs/handoff/kickoff.md` — a **research kickoff** stating
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
cycle's artifacts (including `docs/handoff/kickoff.md`).

---

## 4. A complete worked example

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

## 5. Isolation — why two subagents

The review subagent is dispatched with **only**: the repo root, the deliverable
path(s), and (for non-research stages) the upstream artifact path. It never
receives your conversation, the pipeline subagent's reasoning, kickoff prose, or
drafts. Because a freshly dispatched subagent starts with an empty context
window, there is *nothing to leak through* — a stronger guarantee than two human
terminals. This is what lets the review catch framing/scope problems an
in-session check would rationalize away.

(The research stage is special: the review dispatch omits the kickoff path,
because `sdd-review` forbids kickoff prompts as input. The reviewer reads the
research questions from the findings file's own frontmatter.)

---

## 6. Troubleshooting

| Symptom | Cause | What to do |
|---------|-------|------------|
| A pipeline subagent reports "could not write file — returning content inline" | The harness can block a subagent's disk write (especially report-style files or non-conventional paths). Observed live in RS-005. | This is expected and handled: the dispatch template's **labeled-content fallback** returns the file body; the **orchestrator persists it**. No action needed beyond confirming the artifact landed. |
| Pipeline subagent asks a question / stalls | A stage skill's "ask the user" step wasn't front-loaded. | The orchestrator must front-load the stage's question, success criterion, budget, and deliverable contract, plus a non-interactivity clause. Re-dispatch with those filled in. |
| Two artifacts collide on the same ID | A subagent picked its own ID. | The orchestrator assigns IDs centrally and passes them verbatim — never let the subagent scan-and-guess. |
| Review verdict seems to know your reasoning | Isolation leak — prohibited input slipped into the review dispatch. | Reconstruct the review dispatch from paths only (see `references/dispatch-templates.md`). |
| Review returns *Reject* with no actionable findings | Genuine reviewer uncertainty. | The driver pauses; you decide: re-dispatch, override, or stop. |
| A stage triggers a replan | Stuck detection / spike invalidation / verify failure. | It surfaces at the gate as a replan event; you may route back via `sdd-replan`. |

---

## 7. v1 limitations

- **Research-entry only** — a cycle always starts from a research kickoff. You
  cannot yet start mid-pipeline with pre-existing requirements.
- **Sequential** — every stage runs single-threaded in the main workspace. There
  is no parallel implement-stage fan-out and no worktrees in v1. (The fan-out
  boundary rule is documented in the spec for a future version.)
- **Reviews are ephemeral** — verdicts are shown inline and never written to
  disk; there is no `docs/reviews/`. Decisions live in the artifacts (commits,
  spec edits, Q-IMPL entries, replan triggers).

---

## 8. See also

- [`SKILL.md`](SKILL.md) — the driver's operational instructions
- [`references/dispatch-templates.md`](references/dispatch-templates.md) — the
  copy-ready pipeline and review dispatch prompts
- `docs/spec/orchestration.md` — the design spec
- `docs/research/RS-005-sdd-orchestrate-feasibility/findings.md` — the feasibility
  evidence behind the isolation and non-interactivity guarantees
