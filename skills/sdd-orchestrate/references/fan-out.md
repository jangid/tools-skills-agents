# Implement-Stage Fan-out Procedure (Design B)

The full, bulky procedure for **orchestrator-owned, one-level-deep** implement-stage
fan-out. `../SKILL.md` (§Execution Model) describes this behavior in concise prose
and points here for the dispatch template and the exact command sequence. The
contract is defined by `docs/spec/orchestration.md` §"Sequential Execution and
Implement-Stage Fan-out" (REQ-ORCH-015/016, REQ-ORCH-022..028).

Fan-out is the orchestrator's job, never a subagent's: a dispatched subagent has
**no subagent-dispatch tool** in its toolset (RS-006 Q1), so each fan-out implement
subagent is a **leaf** that runs `sdd-implement` on its chunk-group and cannot fan
out further (REQ-ORCH-022). Design A (a pipeline subagent owning nested fan-out) is
ruled out infeasible; Design B (this procedure) is the spec.

---

## 1. Boundary derivation (which chunks run in parallel)

Fan-out occurs along the **independent branches of the plan's chunk dependency
graph** — not per-milestone (too coarse; milestones are sequential) and not
per-task (too fine) (REQ-ORCH-016).

Derive the parallel groups by **reading `docs/plan.md`**, never by modifying
`sdd-implement` (REQ-ORCH-001, REQ-ORCH-016):

- The canonical signal is each chunk's `**Depends on**: Chunk N` field (defined in
  `docs/spec/plan-management.md`). The live plan may instead express the same
  relation as chunk-level prose — `Entry criteria: Chunk N complete` — which you
  treat as the equivalent of that field.
- These are **chunk-level** declarations. Do **not** use the coarser
  milestone-level Entry/Exit criteria from milestone-plans to derive chunk fan-out.
- Two chunks are **independent** (concurrently runnable) when neither (transitively)
  depends on the other. A maximal set of mutually-independent chunks is a
  **chunk-group** that can run in its own worktree.

**Degrade-to-sequential conditions** (never guess a boundary):

- The plan does **not** express parseable chunk-level dependencies in either form, OR
- The dependency graph is a **single chain** (every chunk depends on the previous —
  no ≥2 independent branches exist).

In either case, run the implement stage sequentially in the main workspace even if
the operator opted into fan-out, and tell the operator at the gate (see SKILL.md
§Execution Model).

---

## 2. Per-group implement dispatch template

One dispatch per chunk-group, pinned to that group's orchestrator-provisioned
worktree/branch. The non-interactivity contract (REQ-ORCH-007) and central ID
assignment (REQ-ORCH-008) apply exactly as for any pipeline dispatch (see
`dispatch-templates.md` §PIPELINE). The fan-out-specific additions are the
**worktree pin**, the **leaf clause**, and the **inline git identity**.

```
You are a non-interactive pipeline subagent executing ONE stage of an SDD
pipeline. Do NOT ask questions — you have no user to answer them.

Working directory (absolute): {worktree_path}
Stage skill to invoke: sdd-implement
Assigned IDs (use these verbatim, do not scan/guess): {ids_if_any}
Success criterion: the chunk-group's tasks are implemented and committed on
  branch {branch} within this worktree.
Budget: {budget}
Deliverable contract: implement these chunks only — {chunk_group_tasks}.

Worktree pin (HARD boundary):
  - Operate ONLY within this worktree ({worktree_path}) and ONLY on its branch
    ({branch}). Do not touch the main workspace, other worktrees, or other
    branches.

Leaf clause:
  - You are a LEAF subagent. Do NOT dispatch any sub-subagent and do NOT fan out
    further — run sdd-implement directly on your chunk-group. (You have no
    subagent-dispatch tool; this is enforced by the harness as well.)

Commit identity (sandbox-safe):
  - Commit with inline identity flags, NEVER by writing .git/config:
      git -c user.email={git_email} -c user.name={git_name} commit ...
    Writing the main repo's .git/config is blocked by the sandbox
    ("Operation not permitted"); the inline -c flags let commits, merges, and
    branch ops succeed.

Precedence: where sdd-implement tells you to scan for the next ID or choose an
output path, THESE dispatch instructions override it.

Task:
  1. Invoke sdd-implement via the Skill tool and follow it on your chunk-group.
  2. Where the skill instructs "ask the user", use the inputs above; record any
     genuinely missing decision under Open Questions/Assumptions with a stated
     default and proceed — NEVER fabricate operator consent.
  3. Commit your work on {branch} using the inline git identity above.
  4. Return: the list of files written + commits made + a one-paragraph summary.
     If a write is blocked, return the file's full content with the target path
     labeled so the orchestrator can persist it.

Do not perform any stage other than sdd-implement.
```

### Slot contract (fan-out dispatch)
- `{worktree_path}` — absolute path of this group's worktree (orchestrator pins cwd).
- `{branch}` — this group's branch, created by the orchestrator in step 1 below.
- `{chunk_group_tasks}` — the chunk(s)/tasks this leaf owns; nothing outside them.
- `{ids_if_any}` — IDs the orchestrator assigned centrally (REQ-ORCH-008).
- `{git_email}` / `{git_name}` — identity for the inline `-c` flags (REQ-ORCH-027).
- `{budget}` — explicit bound (REQ-ORCH-007).

**Concurrency note (RS-006 spike, 2026-06-05):** issuing all per-group dispatches
**in a single batch** was **observed to run them concurrently** on this harness —
medium confidence, since the spike's ~4s probe workload inside a ~426s agent lifetime
is latency-dominated (`docs/spikes/dispatch-concurrency.md`, REQ-ORCH-028). Where it
holds, that is a wall-clock speedup, not merely worktree isolation. **Correctness does
not depend on it** — the design is correct whether dispatches run concurrently or
serialized; only the speedup depends on concurrency.

---

## 3. Orchestrator command sequence (provision → await → merge → teardown)

The orchestrator (not any subagent) owns worktree provisioning, merging, and
teardown — a single owner keeps lifecycle symmetric and avoids orphaned worktrees
(Q-REQ-G).

### 3a. Provision one worktree/branch per group (REQ-ORCH-023)

```bash
# base = main (or the current tip the implement stage builds on)
git worktree add -b <branch> <worktree_path> <base>
```

Then dispatch one leaf implement subagent per group (§2), **all in one batch** so
they run concurrently. Await **all** returns before merging (REQ-ORCH-022/023).

### 3b. Sequential merge to main (REQ-ORCH-025)

Merge the branches **one at a time** into `main`; complete **all** merges **before**
the implement-stage review runs (the review sees the merged state, never an unmerged
branch). For each branch in turn:

```bash
git merge --no-edit <branch>
#   exit 0  -> merged cleanly (fast-forward or auto-merge); go to teardown (3d)
#   exit !=0 -> conflict; go to conflict handling (3c)
```

Because merges are one-at-a-time, each branch's merge is either fully applied or
fully unwound — partial-merge corruption across branches cannot occur.

### 3c. Merge-conflict handling (REQ-ORCH-026, Q-IMPL-1)

On a non-zero `git merge` exit:

1. **(Optional) best-effort auto-resolve.** You MAY first attempt automatic
   resolution. This is best-effort and never the only path. A conflict that
   auto-resolves cleanly (no abort) is a normal success — the merge completes,
   continue to teardown (3d) as for a clean `exit 0`.
2. **Guaranteed fallback — abort and redo by re-derivation.** If auto-resolve is not
   attempted or does not cleanly succeed:

   ```bash
   git merge --abort                                   # restores the last good state
   git worktree add -b <branch>-redo <redo_path> main  # re-branch from UPDATED main
   ```

   Re-dispatch a **leaf** implement subagent (§2 template, pinned to `<redo_path>` /
   `<branch>-redo`) to **re-run `sdd-implement`** for that chunk-group in the fresh
   worktree. Because the work is re-derived against the updated `main` (which already
   contains the branches merged so far), the already-merged changes are integrated by
   re-derivation — **never replay the stale returned patch**, which would reproduce
   the identical conflict. Then re-attempt:

   ```bash
   git merge --no-edit <branch>-redo
   ```

3. **Convergence / guaranteed termination.** If the chunk-group **still** conflicts
   after re-derivation against the updated `main`, that proves the groups were **not
   truly independent** — a fan-out boundary-selection error (genuinely independent
   branches cannot conflict after re-derivation against a `main` already containing
   the other branch). **Fall back to running the affected chunk-groups sequentially**
   (one implement run re-branched from `main`, merged, then the next), which cannot
   conflict by construction. This guarantees termination: each round either merges
   cleanly or proves non-independence and collapses to the always-terminating
   sequential path.
4. **No-corruption invariant.** The abort-and-redo path must **never** corrupt or
   unwind already-merged work. A `git merge --abort` unwinds only the single failing
   merge (RS-006 Q3 proved clean restoration with no loss of prior merges); the redo
   worktree re-branches from that intact `main`, inheriting — never undoing — the
   already-merged branches.

Conflict detection relies on the `git merge` exit code as the contract signal
(`git status --porcelain` `AA` markers and `<<<<<<<` file markers corroborate it,
RS-006 Q3).

### 3d. Teardown after each successful merge

Once a branch is merged into `main`, remove its worktree and delete its branch so
the review sees a clean repo with only `main` (REQ-ORCH-023, Q-REQ-G):

```bash
git worktree remove <worktree_path>
git branch -d <branch>
```

Redo worktrees (`<branch>-redo`) are torn down the same way after their merge. All
teardown happens **before** the implement-stage review.

---

## 4. Invariants checklist

- [ ] Boundary derived from `**Depends on**`/`Entry criteria: Chunk N` prose, not
      milestone Entry/Exit; degrade to sequential if unparseable or single-chain.
- [ ] One orchestrator-provisioned worktree/branch per concurrently-runnable group.
- [ ] Each fan-out subagent is a leaf (no sub-dispatch), pinned to its worktree.
- [ ] Subagents commit with inline `git -c user.email=… -c user.name=…` (no
      `.git/config` write).
- [ ] All subagents return before any merge; merges are sequential into `main`,
      completed before the implement-stage review.
- [ ] Conflicts: optional auto-resolve → else `git merge --abort` → redo by
      re-derivation in a worktree re-branched from updated `main` → sequential
      fallback on repeat conflict (guaranteed termination); never corrupt merged work.
- [ ] Each merged worktree/branch is torn down before review.
