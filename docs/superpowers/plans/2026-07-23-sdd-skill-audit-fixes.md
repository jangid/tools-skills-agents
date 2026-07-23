# SDD Skill-Suite Audit Fixes Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Fix all 28 findings from the 2026-07-23 audit of the ten `sdd-*` skills (10 correctness contradictions, 10 medium gaps, 8 polish items).

**Architecture:** All changes are surgical Markdown edits to `skills/*/SKILL.md`, `skills/sdd-orchestrate/references/*.md`, and `skills/sdd-orchestrate/USAGE.md`, executed as one atomic commit per finding (or per tightly-coupled finding group) on branch `fix/sdd-skill-audit`. `~/.claude/skills/*` are symlinks into this repo, so edits are live immediately — no install step.

**Tech Stack:** Markdown, git, grep (verification).

## Global Constraints

- Commit format: `type(scope): description`, imperative mood, **no** Co-Authored-By and **no** "Generated with Claude Code" lines (user's global CLAUDE.md).
- One logical change per commit (atomic commits).
- Never edit files under `~/.claude/skills/` directly — they are symlinks; edit the repo copies.
- Every `old_string` below was verified against the files as of commit `97740de`. If an exact match fails, re-read the file and re-anchor — do not skip the edit.
- Verification greps must be run from the repo root: `/Users/pankaj/work/github/jangid/tools-skills-agents`.
- The repo itself runs at SDD marker `3` (`docs/.sdd-version` = `3`); nothing in this plan changes that file.

---

### Task 0: Create the working branch

**Files:** none (git only)

- [ ] **Step 1: Branch from main**

```bash
git checkout -b fix/sdd-skill-audit main
```

Expected: `Switched to a new branch 'fix/sdd-skill-audit'`

---

### Task 1 (F1): Unify spike findings/code destinations — sdd-implement

`skills/sdd-implement/SKILL.md` says spike findings go to `docs/research/RS-NNN-{topic}/findings.md` (step 4 of the `[spike]` list) but the "Spike code separation" block seven lines later says they go to `docs/spikes/{topic}.md` and code to `scripts/spike_*`. Canonical: everything lives in the research spike directory, matching `sdd-research`.

**Files:**
- Modify: `skills/sdd-implement/SKILL.md` (§`[spike] tasks`)

- [ ] **Step 1: Replace the contradictory block**

Old:

```markdown
**Spike code separation:**

- Spike findings (decisions, learnings, recommendations) go to `docs/spikes/{topic}.md`.
- Throwaway spike code (proofs of concept, exploratory scripts) goes to `scripts/spike_*` with a docstring noting it is throwaway.
```

New:

```markdown
**Spike code separation:**

- Spike findings (decisions, learnings, recommendations) go to `docs/research/RS-NNN-{topic}/findings.md` — the same destination as step 4 above and as `sdd-research` spikes. Do not create a separate `docs/spikes/` tree.
- Throwaway spike code (proofs of concept, exploratory scripts) goes to `docs/research/RS-NNN-{topic}/prototype/` with a docstring noting it is throwaway (per `sdd-research` §Step 5 supporting files).
```

- [ ] **Step 2: Verify**

```bash
grep -n "docs/spikes" skills/sdd-implement/SKILL.md
```

Expected: no output.

- [ ] **Step 3: Commit**

```bash
git add skills/sdd-implement/SKILL.md
git commit -m "fix(sdd-implement): unify spike findings and code under docs/research/RS-*"
```

---

### Task 2 (F2): Give the single-milestone plan frontmatter; fix staleness references

The single-milestone plan template has no frontmatter, but `sdd-implement` compares against the plan's `last_updated`, `sdd-plan`/`sdd-verify` fall back to fragile file mtime, and the v4 gate asserts the plan carries `status`.

**Files:**
- Modify: `skills/sdd-plan/SKILL.md` (template + phase detection step 3)
- Modify: `skills/sdd-verify/SKILL.md` (phase detection step 2)
- Modify: `skills/sdd-replan/SKILL.md` (staleness check step 5)

- [ ] **Step 1: Add frontmatter to the single-milestone template in sdd-plan**

Old:

```markdown
**Single-milestone plan format (default):**

```markdown
# Implementation Plan: [Project Name]
```

New:

```markdown
**Single-milestone plan format (default):**

```markdown
---
last_updated: YYYY-MM-DD
status: planned   # planned → active (first task starts) → complete
---

# Implementation Plan: [Project Name]
```

(The `last_updated:` field is what every staleness check compares; bump it on every rewrite/update. `status:` follows the same lifecycle vocabulary as per-milestone plans.)

- [ ] **Step 2: Fix sdd-plan phase-detection step 3 mtime reference**

Old:

```markdown
   - **Single-milestone plan**: compare `docs/plan.md`'s modification date against `last_updated` in each `docs/spec/*.md` and `docs/requirements/index.md`. If any upstream artifact is newer, the plan is **stale**
```

New:

```markdown
   - **Single-milestone plan**: compare `docs/plan.md`'s `last_updated` frontmatter against `last_updated` in each `docs/spec/*.md` and `docs/requirements/index.md`. If any upstream artifact is newer, the plan is **stale**. (Legacy plans without frontmatter: fall back to file modification date — unreliable after a fresh clone — and add the frontmatter while updating)
```

- [ ] **Step 3: Fix sdd-verify phase-detection step 2 mtime reference**

Old:

```markdown
2. **Staleness check**: compare `last_updated` in `docs/requirements/index.md` and specs against `docs/plan.md` modification date. If upstream artifacts are newer than the plan, the plan is stale → use `sdd-plan` to update before verifying
```

New:

```markdown
2. **Staleness check**: compare `last_updated` in `docs/requirements/index.md` and specs against `docs/plan.md`'s `last_updated` frontmatter (legacy plans without frontmatter: file modification date as fallback). If upstream artifacts are newer than the plan, the plan is stale → use `sdd-plan` to update before verifying
```

- [ ] **Step 4: Clarify sdd-replan's compare basis**

Old:

```markdown
   - **Single-milestone plan**: compare `docs/requirements/index.md` and specs against `docs/plan.md`
```

New:

```markdown
   - **Single-milestone plan**: compare `docs/requirements/index.md` and specs against `docs/plan.md`'s `last_updated` frontmatter (mtime fallback for legacy plans)
```

- [ ] **Step 5: Verify**

```bash
grep -n "modification date" skills/sdd-plan/SKILL.md skills/sdd-verify/SKILL.md
```

Expected: only fallback-context mentions ("fall back to file modification date", "file modification date as fallback"); no primary-mechanism uses. Also:

```bash
grep -n "last_updated: YYYY-MM-DD" skills/sdd-plan/SKILL.md
```

Expected: at least one hit inside the single-milestone template.

- [ ] **Step 6: Commit**

```bash
git add skills/sdd-plan/SKILL.md skills/sdd-verify/SKILL.md skills/sdd-replan/SKILL.md
git commit -m "fix(sdd-plan): add frontmatter to single-milestone plans; stop keying staleness off mtime"
```

---

### Task 3 (F3): Requirements file-split must not remap IDs — sdd-requirements

Step 6 currently says a >300-line split "assigns new domain prefixes", which silently remaps permanent IDs with no cross-reference update.

**Files:**
- Modify: `skills/sdd-requirements/SKILL.md` (Step 6 + ID Assignment)

- [ ] **Step 1: Rewrite the split instructions**

Old:

```markdown
After writing to any category file, check its line count. If the file exceeds 300 lines:
- Inform the user: "{file} is at {N} lines — recommend splitting"
- Propose a split (e.g., `auth.md` -> `auth-login.md` + `auth-permissions.md`)
- If approved: create the new files, move requirements, assign new domain prefixes, update index.md
```

New:

```markdown
After writing to any category file, check its line count. If the file exceeds 300 lines:
- Inform the user: "{file} is at {N} lines — recommend splitting"
- Propose a split (e.g., `auth.md` -> `auth-login.md` + `auth-permissions.md`)
- If approved: create the new files and move requirements **verbatim — IDs are permanent** (`REQ-AUTH-007` stays `REQ-AUTH-007`; never renumber or assign a new domain prefix on a split)
- The split files **share the original domain prefix**: each keeps `domain: AUTH` in frontmatter, the Domain Prefixes table lists all files carrying the prefix, and the next-ID scan covers every file sharing the domain (see ID Assignment)
- Update index.md: one Files-table row per new file; update the Domain Prefixes table row to list all the prefix's files
```

- [ ] **Step 2: Update the ID-scan rule to cover shared prefixes**

Old:

```markdown
- Scan the target file for the highest existing NNN and increment
```

New:

```markdown
- Scan **all category files sharing the domain prefix** (a prefix can span multiple files after a split — check the Domain Prefixes table) for the highest existing NNN and increment
```

- [ ] **Step 3: Verify**

```bash
grep -n "assign new domain prefixes" skills/sdd-requirements/SKILL.md
```

Expected: no output.

- [ ] **Step 4: Commit**

```bash
git add skills/sdd-requirements/SKILL.md
git commit -m "fix(sdd-requirements): keep requirement IDs permanent across file splits"
```

---

### Task 4 (F4): Greenfield init — sdd-migrate

Fresh projects ping-pong: skills say "marker missing → run sdd-migrate", migrate says "no docs/ → nothing to migrate, exit". Nobody ever writes the marker.

**Files:**
- Modify: `skills/sdd-migrate/SKILL.md` (Version Detection step 1)

- [ ] **Step 1: Replace the no-docs exit with greenfield initialization**

Old:

```markdown
1. If no `docs/` directory exists at all, inform the user there is nothing to migrate and exit.
```

New:

```markdown
1. **Greenfield check**: if there are no SDD artifacts to migrate — no `docs/` directory at all, or a `docs/` containing none of `requirements.md`, `requirements/`, `research/`, `spec/`, `plan.md` — there is nothing to *migrate*. Offer to **initialize** instead: create `docs/` (if absent) and write `docs/.sdd-version` containing `4` (the latest supported version), so other SDD skills stop detecting a pre-versioning layout and route correctly. Get confirmation, write the marker, report "initialized at v4 (greenfield — no artifacts migrated)", and exit. A "missing marker" therefore means *v1 legacy layout* only when legacy artifacts actually exist.
```

- [ ] **Step 2: Verify**

```bash
grep -n "Greenfield check" skills/sdd-migrate/SKILL.md
```

Expected: one hit.

- [ ] **Step 3: Commit**

```bash
git add skills/sdd-migrate/SKILL.md
git commit -m "fix(sdd-migrate): initialize greenfield projects instead of exiting with nothing to migrate"
```

---

### Task 5 (F5): Q-IMPL ID race under fan-out — reserved number blocks

Two parallel fan-out leaves in the same workstream can both scan-and-mint the same next `Q-IMPL-[<WS>-]NNN` in different spec files; the merge won't conflict and the duplicate survives.

**Files:**
- Modify: `skills/sdd-orchestrate/references/fan-out.md` (§2 template + slot contract)
- Modify: `skills/sdd-implement/SKILL.md` (§Numbering Rules)

- [ ] **Step 1: Add the Q-IMPL block line to the fan-out dispatch template**

In `fan-out.md` §2, old:

```
Assigned IDs (use these verbatim, do not scan/guess): {ids_if_any}
Success criterion: the chunk-group's tasks are implemented and committed on
```

New:

```
Assigned IDs (use these verbatim, do not scan/guess): {ids_if_any}
Q-IMPL number block (allocate sequentially from the start of this block; do
  NOT scan for the next number): {qimpl_block}
Success criterion: the chunk-group's tasks are implemented and committed on
```

- [ ] **Step 2: Add the slot to the fan-out slot contract**

Old:

```markdown
- `{ids_if_any}` — IDs the orchestrator assigned centrally (REQ-ORCH-008).
```

New:

```markdown
- `{ids_if_any}` — IDs the orchestrator assigned centrally (REQ-ORCH-008).
- `{qimpl_block}` — a **disjoint** Q-IMPL number range per leaf (e.g. group 1:
  `011–030`, group 2: `031–050`), allocated by the orchestrator above the current
  scanned max. Q-IMPL entries arise dynamically mid-implementation, so they cannot
  be pre-assigned individually — but two parallel leaves scanning globally would
  mint the same next number. Unused block numbers stay unused forever (IDs are
  append-only and never reused; gaps are fine).
```

- [ ] **Step 3: Add the parallel-dispatch exception to sdd-implement's numbering rules**

Old:

```markdown
- Global sequential across all specs in the project: `Q-IMPL-001`, `Q-IMPL-002`, ...
- To find the next number, scan all spec files' `## Implementation Questions` sections and increment from the highest existing.
```

New:

```markdown
- Global sequential across all specs in the project: `Q-IMPL-001`, `Q-IMPL-002`, ...
- To find the next number, scan all spec files' `## Implementation Questions` sections and increment from the highest existing.
- **Parallel-dispatch exception**: when running as a fan-out leaf with an assigned Q-IMPL number block in your dispatch, allocate from that block instead of scanning — parallel leaves scanning globally would mint colliding numbers. Gaps left by unused block numbers are permanent and acceptable.
```

- [ ] **Step 4: Verify**

```bash
grep -n "qimpl_block" skills/sdd-orchestrate/references/fan-out.md
grep -n "Parallel-dispatch exception" skills/sdd-implement/SKILL.md
```

Expected: 2 hits in fan-out.md, 1 in sdd-implement.

- [ ] **Step 5: Commit**

```bash
git add skills/sdd-orchestrate/references/fan-out.md skills/sdd-implement/SKILL.md
git commit -m "fix(sdd-orchestrate): reserve disjoint Q-IMPL number blocks per fan-out leaf"
```

---

### Task 6 (F6): Fan-out leaves must not write shared plan/traceability

Every leaf marks `[x]` in the same plan and fills the same traceability rows, so any two "independent" groups conflict on docs — first merge conflicts force redos and, under marker 3, misdiagnose as boundary errors.

**Files:**
- Modify: `skills/sdd-orchestrate/references/fan-out.md` (§2 worktree pin, new §3e, §3c note, §4 checklist)

- [ ] **Step 1: Extend the worktree pin in the §2 template**

Old:

```
Worktree pin (HARD boundary):
  - Operate ONLY within this worktree ({worktree_path}) and ONLY on its branch
    ({branch}). Do not touch the main workspace, other worktrees, or other
    branches.
```

New:

```
Worktree pin (HARD boundary):
  - Operate ONLY within this worktree ({worktree_path}) and ONLY on its branch
    ({branch}). Do not touch the main workspace, other worktrees, or other
    branches.
  - Do NOT edit the shared plan or traceability files (docs/plan.md /
    docs/ws/<ws>/plan.md; docs/requirements/traceability.md /
    docs/ws/<ws>/traceability.md): every fan-out leaf writes them, so any two
    groups would conflict on merge regardless of code independence. Where
    sdd-implement says to mark tasks [x] or fill traceability columns
    (including chunk-close Check 2), instead RECORD the completed task list
    and the column fills in your return; the orchestrator applies them once
    after all merges (§3e).
```

- [ ] **Step 2: Add §3e after §3d (post-merge bookkeeping)**

Insert after the §3d block (after "All teardown happens **before** the implement-stage review."):

```markdown
### 3e. Post-merge bookkeeping (orchestrator-owned)

After all merges and teardowns, before the implement-stage review, the
orchestrator applies the shared-doc updates the leaves were barred from making
(§2 worktree pin):

1. Mark each returned completed task `[x]` in the plan (`docs/plan.md`, or
   `docs/ws/<ws>/plan.md` under marker `4`) and bump its `last_updated`.
2. Apply the returned traceability Test/Implementation fills per the active
   marker's contract (marker `3`: the single shared
   `docs/requirements/traceability.md`; marker `4`: the workstream's own
   `docs/ws/<ws>/traceability.md`, then regenerate the shared aggregate).
3. Re-run any chunk-close Check 2 that a leaf deferred, now that the columns
   are filled.

Only then dispatch the implement-stage review, which sees the fully merged,
fully book-kept state.
```

- [ ] **Step 3: Strengthen the §3c boundary-error inference note**

Old:

```markdown
   (genuinely independent branches cannot conflict after re-derivation against a
   `main` already containing the other branch). **Fall back to running the affected chunk-groups sequentially**
```

New:

```markdown
   (genuinely independent branches cannot conflict after re-derivation against a
   `main` already containing the other branch — and with the shared
   plan/traceability writes excluded from leaves per §2, a conflict genuinely
   indicates overlapping *code* changes, not bookkeeping collisions).
   **Fall back to running the affected chunk-groups sequentially**
```

- [ ] **Step 4: Add the invariant to §4**

Old:

```markdown
- [ ] Each merged worktree/branch is torn down before review.
```

New:

```markdown
- [ ] Leaves never edit the shared plan/traceability files; the orchestrator
      applies returned completions and fills after all merges (§3e), before the
      review.
- [ ] Each merged worktree/branch is torn down before review.
```

- [ ] **Step 5: Verify**

```bash
grep -n "3e" skills/sdd-orchestrate/references/fan-out.md | head
```

Expected: §3e heading plus references from §2 and §4.

- [ ] **Step 6: Commit**

```bash
git add skills/sdd-orchestrate/references/fan-out.md
git commit -m "fix(sdd-orchestrate): keep fan-out leaves out of shared plan/traceability; orchestrator books after merge"
```

---

### Task 7 (F7): Teach the canonical `**Depends on**` field — sdd-plan

`fan-out.md` calls `**Depends on**: Chunk N` canonical, but sdd-plan's template only emits the `Entry criteria:` fallback.

**Files:**
- Modify: `skills/sdd-plan/SKILL.md` (template chunks + Planning Rules)

- [ ] **Step 1: Add the field to both template chunks**

Old:

```markdown
### Chunk 0: [Name]
**Goal**: What's testable after this chunk.
**Tasks**:
1. [implement] [Task description] — traces to [spec.md]
2. [spike] [Research question, budget: 30min] — traces to [spec.md §section]
3. [verify] [What to validate] — traces to [spec.md acceptance criteria]
**Entry criteria**: None (first chunk).
**Exit criteria**: [conditions].

### Chunk 1: [Name]
**Tasks**: ...
**Entry criteria**: Chunk 0 complete.
**Exit criteria**: ...
```

New:

```markdown
### Chunk 0: [Name]
**Goal**: What's testable after this chunk.
**Depends on**: None.
**Tasks**:
1. [implement] [Task description] — traces to [spec.md]
2. [spike] [Research question, budget: 30min] — traces to [spec.md §section]
3. [verify] [What to validate] — traces to [spec.md acceptance criteria]
**Entry criteria**: None (first chunk).
**Exit criteria**: [conditions].

### Chunk 1: [Name]
**Depends on**: Chunk 0.
**Tasks**: ...
**Entry criteria**: Chunk 0 complete.
**Exit criteria**: ...
```

- [ ] **Step 2: Add the Planning Rule**

Old:

```markdown
- **Chunks not milestones for work units**: use `### Chunk N: <name>` headers for implementation work units (~5-15 hours each). Reserve "milestone" for delivery groupings (M1, M2, etc.) in multi-milestone projects
```

New:

```markdown
- **Chunks not milestones for work units**: use `### Chunk N: <name>` headers for implementation work units (~5-15 hours each). Reserve "milestone" for delivery groupings (M1, M2, etc.) in multi-milestone projects
- **Declare chunk dependencies**: every chunk carries a `**Depends on**: Chunk N` field (`None` for roots; comma-separate multiple). This is the canonical machine-readable signal implement-stage fan-out parses to find independent chunk-groups — `Entry criteria:` prose is a tolerated fallback, not the canonical form
```

- [ ] **Step 3: Verify**

```bash
grep -n "Depends on" skills/sdd-plan/SKILL.md
```

Expected: 3 hits (two template fields, one rule).

- [ ] **Step 4: Commit**

```bash
git add skills/sdd-plan/SKILL.md
git commit -m "fix(sdd-plan): emit the canonical Depends-on chunk field fan-out parses"
```

---

### Task 8 (F8): Entry-kickoff-aware phase detection — sdd-orchestrate

Resuming a mid-pipeline-entry cycle misdetects position as "research" because the table only looks at artifacts.

**Files:**
- Modify: `skills/sdd-orchestrate/SKILL.md` (§Phase Detection, right after the table)

- [ ] **Step 1: Insert after the phase-detection table**

Old (the paragraph immediately following the table):

```markdown
Tell the operator the detected position and confirm before proceeding.
```

New:

```markdown
**Entry kickoffs shift the table's origin.** If the kickoff on disk is an
**entry kickoff** (§Entry Points — it records an entry stage and which upstream
is assumed approved), the stages before its entry stage are *intentionally
absent*: do not derive "at the research stage" from missing research artifacts.
Read the kickoff's recorded entry stage and derive loop position from that stage
onward only.

Tell the operator the detected position and confirm before proceeding.
```

- [ ] **Step 2: Verify**

```bash
grep -n "Entry kickoffs shift" skills/sdd-orchestrate/SKILL.md
```

Expected: one hit.

- [ ] **Step 3: Commit**

```bash
git add skills/sdd-orchestrate/SKILL.md
git commit -m "fix(sdd-orchestrate): derive resume position from the entry kickoff's recorded stage"
```

---

### Task 9 (F9): Research checklist must read questions from findings frontmatter — sdd-review

The research checklist tells the reviewer to check questions "stated in the kickoff" — an input Step 2 prohibits.

**Files:**
- Modify: `skills/sdd-review/SKILL.md` (§Research checklist)

- [ ] **Step 1: Edit the checklist line**

Old:

```markdown
- Check that every research question stated in the kickoff has a finding (even if "inconclusive")
```

New:

```markdown
- Check that every research question stated in the deliverable's own `questions:` frontmatter has a finding (even if "inconclusive") — the kickoff is a prohibited input (Step 2); the findings file's frontmatter is the authoritative question list
```

- [ ] **Step 2: Verify**

```bash
grep -n "stated in the kickoff" skills/sdd-review/SKILL.md
```

Expected: no output.

- [ ] **Step 3: Commit**

```bash
git add skills/sdd-review/SKILL.md
git commit -m "fix(sdd-review): source research questions from findings frontmatter, not the prohibited kickoff"
```

---

### Task 10 (F10): Cycle-scoped research detection via kickoff `research_id` — sdd-orchestrate

Prior cycles' completed `RS-*` findings make a new cycle's research stage look done.

**Files:**
- Modify: `skills/sdd-orchestrate/SKILL.md` (§Phase Detection table row, §KICKOFF, §Workstream Picker lifecycle item 2)

- [ ] **Step 1: Fix the table row**

Old:

```markdown
| kickoff exists, no `docs/research/RS-*/findings.md` | at the research stage |
```

New:

```markdown
| kickoff exists, its `research_id` spike has no Complete findings | at the research stage |
```

- [ ] **Step 2: Add the research_id contract to §KICKOFF**

Old:

```markdown
**By default** the kickoff is a **research kickoff**: it states the research
questions, success criteria, a budget, and what is out of scope, and the LOOP
begins at the research stage.
```

New:

```markdown
**By default** the kickoff is a **research kickoff**: it states the research
questions, success criteria, a budget, and what is out of scope, and the LOOP
begins at the research stage. Assign the cycle's research ID at KICKOFF — the
next `RS-NNN` (marker `4`: `RS-<WS>-NNN`), allocated centrally per §Pipeline
subagent dispatch — and record it in the kickoff frontmatter as `research_id:`.
Phase detection checks **that spike's** findings, never "any `RS-*`", so a prior
cycle's completed research can never mask the new cycle's research stage.
(Kickoffs predating this field: fall back to comparing findings dates against
the kickoff's write date.)
```

- [ ] **Step 3: Fix the picker lifecycle's research-complete rule**

Old:

```markdown
2. **positions its loop at research** (§Phase Detection: `docs/ws/<id>/kickoff.md`
   exists and research is **not yet complete for `<id>`** → the research stage).
   Research is complete for workstream `<id>` when a shared
   `docs/research/RS-<id>-*/findings.md` exists with `status: Complete` (an
   explicit early-exit finding counts as Complete).
```

New:

```markdown
2. **positions its loop at research** (§Phase Detection: `docs/ws/<id>/kickoff.md`
   exists and research is **not yet complete for `<id>`** → the research stage).
   Research is complete for this cycle when the kickoff's recorded `research_id`
   spike (`docs/research/RS-<id>-NNN-*/findings.md`) exists with
   `status: Complete` (an explicit early-exit finding counts as Complete) —
   scoped to the kickoff's spike, not "any `RS-<id>-*`", so a prior cycle in the
   same workstream never masks a new cycle's research stage.
```

- [ ] **Step 4: Verify**

```bash
grep -n "research_id" skills/sdd-orchestrate/SKILL.md
```

Expected: ≥3 hits.

- [ ] **Step 5: Commit**

```bash
git add skills/sdd-orchestrate/SKILL.md
git commit -m "fix(sdd-orchestrate): scope research-stage detection to the kickoff's assigned research_id"
```

---

### Task 11 (F11+F12): Generalize sdd-review's phase-detection inputs; define the implement-stage review deliverable

The Implementation row hardcodes this repo's `skills/*/SKILL.md`; plan/verification rows aren't v4-aware; orchestrate never says what paths an implement-stage review dispatch carries.

**Files:**
- Modify: `skills/sdd-review/SKILL.md` (phase-detection table)
- Modify: `skills/sdd-orchestrate/SKILL.md` (§Review subagent dispatch)

- [ ] **Step 1: Rewrite the three table rows in sdd-review**

Old:

```markdown
| `docs/plan.md` (or `docs/plan-*.md`) | Plan | §Plan |
| `skills/*/SKILL.md` + chunk context | Implementation | §Implementation |
| `docs/verification.md` | Verification | §Verification |
```

New:

```markdown
| `docs/plan.md` / `docs/plan-*.md` (marker `4`: `docs/ws/<id>/plan.md`) | Plan | §Plan |
| changed source/test files (the implementation diff) + plan/chunk context | Implementation | §Implementation |
| `docs/verification.md` (marker `4`: `docs/ws/<id>/verification.md`) | Verification | §Verification |
```

- [ ] **Step 2: Define the implement-stage deliverable in orchestrate's review dispatch section**

In `skills/sdd-orchestrate/SKILL.md`, old:

```markdown
**The review dispatch MUST carry ONLY:**
- the repository root,
- the deliverable artifact path(s),
```

New:

```markdown
**The review dispatch MUST carry ONLY:**
- the repository root,
- the deliverable artifact path(s) — for the **implement stage**, where there is
  no single artifact file, this means the plan path plus the source/test files
  changed during the stage (e.g. `git diff --name-only` against the
  stage-start commit),
```

- [ ] **Step 3: Verify**

```bash
grep -n "skills/\*/SKILL.md" skills/sdd-review/SKILL.md
```

Expected: no output.

- [ ] **Step 4: Commit**

```bash
git add skills/sdd-review/SKILL.md skills/sdd-orchestrate/SKILL.md
git commit -m "fix(sdd-review): generalize phase-detection inputs; define implement-stage review deliverable"
```

---

### Task 12 (F13): Modernize sdd-research's version-check text

Step 1 still says "upgrade to v2" and only knows markers up to `2`.

**Files:**
- Modify: `skills/sdd-research/SKILL.md` (Phase Detection step 1)

- [ ] **Step 1: Replace the stale step**

Old:

```markdown
1. **Version check**: Read `docs/.sdd-version`. If missing, assume v1 — suggest running `sdd-migrate` to upgrade to v2 artifact structure before proceeding. If present and contains `2`, use v2 paths below.
```

New:

```markdown
1. **Version check**: Read `docs/.sdd-version`. If missing, suggest running `sdd-migrate` before proceeding — it migrates pre-versioning layouts and initializes greenfield projects. If present but below the latest supported version, note that `sdd-migrate` can upgrade (advisory, not blocking).
```

- [ ] **Step 2: Verify**

```bash
grep -n "upgrade to v2" skills/sdd-research/SKILL.md
```

Expected: no output.

- [ ] **Step 3: Commit**

```bash
git add skills/sdd-research/SKILL.md
git commit -m "fix(sdd-research): modernize version-check wording beyond v2"
```

---

### Task 13 (F14): v4 refresh of the operator guide — USAGE.md

USAGE.md predates v4: kickoff path, merge-to-main, no workstream picker, stale §8 heading.

**Files:**
- Modify: `skills/sdd-orchestrate/USAGE.md`

- [ ] **Step 1: Gate the kickoff path in §3**

Old:

```markdown
1. It writes `docs/handoff/kickoff.md` (KICKOFF).
```

New:

```markdown
1. It writes the kickoff (KICKOFF): `docs/handoff/kickoff.md` under marker `3`,
   or `docs/ws/<id>/kickoff.md` for the selected workstream under marker `4`.
```

- [ ] **Step 2: Gate the kickoff path in §4 KICKOFF**

Old:

```markdown
### KICKOFF
The orchestrator writes `docs/handoff/kickoff.md` — a **research kickoff** stating
```

New:

```markdown
### KICKOFF
The orchestrator writes the kickoff (`docs/handoff/kickoff.md`; marker `4`:
`docs/ws/<id>/kickoff.md`) — a **research kickoff** stating
```

- [ ] **Step 3: Add a workstreams section after §4**

Insert immediately before the `## 5. A complete worked example` heading:

```markdown
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
```

- [ ] **Step 4: Fix the §8 heading and gate the merge language**

Old:

```markdown
## 8. Sequential default, fan-out, and v1 limitations
```

New:

```markdown
## 8. Sequential default and fan-out
```

Old:

```markdown
- then merges the branches **sequentially** back into `main` — completing all
  merges **before** the implement-stage review runs on the merged state — tearing
  down each worktree as it merges.
```

New:

```markdown
- then merges the branches **sequentially** back into the integration anchor —
  `main` under marker `3`, the **workstream branch** under marker `4` (`main`
  stays untouched until the workstream PR) — completing all merges **before**
  the implement-stage review runs on the merged state, tearing down each
  worktree as it merges.
```

Old:

```markdown
On a merge conflict, the orchestrator runs `git merge --abort` and **redoes** the
offending group by re-running `sdd-implement` in a worktree re-branched from the
updated `main` (best-effort auto-resolve may be tried first).
```

New:

```markdown
On a merge conflict, the orchestrator runs `git merge --abort` and **redoes** the
offending group by re-running `sdd-implement` in a worktree re-branched from the
updated integration anchor (`main`, or the workstream branch under marker `4`;
best-effort auto-resolve may be tried first).
```

- [ ] **Step 5: Verify**

```bash
grep -n "v1 limitations" skills/sdd-orchestrate/USAGE.md
grep -cn "marker" skills/sdd-orchestrate/USAGE.md
```

Expected: no "v1 limitations" hit; several "marker" hits.

- [ ] **Step 6: Commit**

```bash
git add skills/sdd-orchestrate/USAGE.md
git commit -m "docs(sdd-orchestrate): refresh operator guide for the v4 workstream layout"
```

---

### Task 14 (F15): Non-interactivity clause in the review dispatch template

A literal reviewer subagent could stall on sdd-review Step 2's "request inputs from the operator".

**Files:**
- Modify: `skills/sdd-orchestrate/references/dispatch-templates.md` (REVIEW template)

- [ ] **Step 1: Add the clause to the template**

Old:

```
Invoke the sdd-review skill and follow it to produce a tiered verdict on the
deliverable. Obtain any context you need by reading files from the repository
yourself — none is provided in this prompt by design.
```

New:

```
You are non-interactive — do NOT ask questions; you have no operator to answer
them. Where sdd-review Step 2 says to request inputs from the operator, use the
paths above instead and read everything else from the repository.

Invoke the sdd-review skill and follow it to produce a tiered verdict on the
deliverable. Obtain any context you need by reading files from the repository
yourself — none is provided in this prompt by design.
```

- [ ] **Step 2: Verify**

```bash
grep -n "non-interactive" skills/sdd-orchestrate/references/dispatch-templates.md
```

Expected: hits in both the pipeline and review templates.

- [ ] **Step 3: Commit**

```bash
git add skills/sdd-orchestrate/references/dispatch-templates.md
git commit -m "fix(sdd-orchestrate): add non-interactivity clause to the review dispatch template"
```

---

### Task 15 (F16): Multi-language type extraction — XSPEC and chunk-close Check 1

Both checks list only Python declaration patterns, silently no-oping (reading as "pass") on TS/Rust/Move projects the suite claims to support.

**Files:**
- Modify: `skills/sdd-specs/SKILL.md` (Step 4b item 1)
- Modify: `skills/sdd-implement/SKILL.md` (Check 1)

- [ ] **Step 1: Replace sdd-specs Step 4b item 1**

Old:

```markdown
1. **Extract type definitions** from each spec's code blocks:
   - Class declarations: `class Foo` or `class Foo(Base)`
   - Enum declarations: `class Foo(Enum)` or `class Foo(StrEnum)`
   - Type alias patterns: `Foo: TypeAlias = Bar` or `Foo = NewType("Foo", Bar)` only — bare `Foo = ...` is excluded to avoid noise on TypeVar/generic declarations
```

New:

```markdown
1. **Extract type definitions** from each spec's code blocks, using the pattern set matching each block's language:
   - Python: `class Foo` / `class Foo(Base)`; enums `class Foo(Enum)` / `class Foo(StrEnum)`; aliases `Foo: TypeAlias = Bar` / `Foo = NewType("Foo", Bar)` only — bare `Foo = ...` is excluded to avoid noise on TypeVar/generic declarations
   - TypeScript: `interface Foo`, `class Foo`, `enum Foo`, `type Foo = ...`
   - Rust: `struct Foo`, `enum Foo`, `trait Foo`, `type Foo = ...;`
   - Move: `struct Foo` (incl. `public struct Foo`)
   - If a spec's code blocks match **no** pattern for their language, report "no extractable type definitions in {spec}" as an explicit result — a silent no-op reads as a clean pass and hides the gap
```

- [ ] **Step 2: Add the language note to sdd-implement Check 1**

Old:

```markdown
For each spec referenced by the chunk's tasks, extract from code blocks:
- (a) Class names — `class Foo` or `class Foo(Base)` declarations
- (b) Field names — `field_name: Type` lines within class bodies
- (c) Enum value lists — `VALUE = "literal"` lines in enum classes
```

New:

```markdown
For each spec referenced by the chunk's tasks, extract from code blocks:
- (a) Class names — `class Foo` or `class Foo(Base)` declarations
- (b) Field names — `field_name: Type` lines within class bodies
- (c) Enum value lists — `VALUE = "literal"` lines in enum classes

(a)–(c) show the Python forms; for TypeScript, Rust, or Move use the equivalent declarations (`interface`/`struct`/`trait`/`enum`, their field declarations, and enum variants). If a spec's code blocks match no pattern for their language, report "no extractable types" as a finding-free but explicit result — never silently pass.
```

- [ ] **Step 3: Verify**

```bash
grep -n "TypeScript" skills/sdd-specs/SKILL.md skills/sdd-implement/SKILL.md
```

Expected: ≥1 hit in each file.

- [ ] **Step 4: Commit**

```bash
git add skills/sdd-specs/SKILL.md skills/sdd-implement/SKILL.md
git commit -m "fix(sdd-specs,sdd-implement): make type-extraction checks language-aware, never silent"
```

---

### Task 16 (F17): Define per-milestone plans under marker 4

sdd-implement says "there is no plan index in v4" while sdd-plan/sdd-replan still offer ungated `docs/plan-{id}.md`.

**Files:**
- Modify: `skills/sdd-plan/SKILL.md` (Step 5 activation)
- Modify: `skills/sdd-implement/SKILL.md` (marker-4 staleness bullet)
- Modify: `skills/sdd-replan/SKILL.md` (§Per-Milestone Replans)

- [ ] **Step 1: Gate the activation paths in sdd-plan**

Old:

```markdown
When activating per-milestone structure:
1. Create `docs/plan.md` as the index (milestone table format — see Step 7)
2. Create `docs/plan-{milestone-id}.md` for each active milestone
3. Add `milestone:`, `last_updated:`, and `status: planned` frontmatter to each milestone plan
```

New:

```markdown
When activating per-milestone structure:
1. Create `docs/plan.md` as the index (milestone table format — see Step 7)
2. Create `docs/plan-{milestone-id}.md` for each active milestone
3. Add `milestone:`, `last_updated:`, and `status: planned` frontmatter to each milestone plan

**Marker `4`**: the same structure lives inside the workstream — `docs/ws/<ws>/plan.md` is the index and `docs/ws/<ws>/plan-{milestone-id}.md` the milestone plans, archiving to `docs/ws/<ws>/plan-history/`. Per-milestone activation is per-workstream; it never creates flat `docs/plan-*.md` files.
```

- [ ] **Step 2: Fix sdd-implement's "no plan index in v4" claim**

Old (within the marker-4 staleness bullet):

```markdown
The v3 caveat "the index-level `docs/plan.md` is not subject to this check" is **dropped** — there is no plan index in v4; workstreams are selected via the `sdd-orchestrate` picker (`docs/spec/ws-orchestration.md`), not a `plan.md` table.
```

New:

```markdown
The v3 caveat generalizes rather than drops: when the workstream uses per-milestone files, the index-level `docs/ws/<ws>/plan.md` is not subject to this check. (Workstream *selection* happens via the `sdd-orchestrate` picker — `docs/spec/ws-orchestration.md` — never via a repo-global plan index.)
```

- [ ] **Step 3: Add the marker-4 line to sdd-replan**

Old:

```markdown
Single-file plans continue to use the existing archival pattern above. Per-milestone logic activates only when per-milestone files exist.
```

New:

```markdown
Single-file plans continue to use the existing archival pattern above. Per-milestone logic activates only when per-milestone files exist. Under marker `4` the same logic runs within the workstream: index and milestone files at `docs/ws/<ws>/plan.md` / `docs/ws/<ws>/plan-{id}.md`, archives to `docs/ws/<ws>/plan-history/`.
```

- [ ] **Step 4: Verify**

```bash
grep -n "no plan index in v4" skills/sdd-implement/SKILL.md
```

Expected: no output.

- [ ] **Step 5: Commit**

```bash
git add skills/sdd-plan/SKILL.md skills/sdd-implement/SKILL.md skills/sdd-replan/SKILL.md
git commit -m "fix(sdd-plan): define per-milestone plan paths under the v4 workstream layout"
```

---

### Task 17 (F18): Reconcile "Approve with fixes" semantics — sdd-orchestrate

sdd-review defines Approve-with-fixes as "fix, then proceed **without** re-review"; orchestrate's loop always re-reviews.

**Files:**
- Modify: `skills/sdd-orchestrate/SKILL.md` (§The gate, after the decision table)

- [ ] **Step 1: Insert after the gate decision table**

Old (paragraph following the gate table):

```markdown
### Edge cases routed through the gate
```

New:

```markdown
**Approve-with-fixes shortcut.** `sdd-review` defines *Approve with fixes* as
"fix the named findings, then proceed without re-review". When that is the
verdict and the operator chooses **loop-back-to-fix**, offer both readings at
the gate: re-dispatch the pipeline with the findings and then either re-review
(the default loop) or skip the re-review per the verdict's own definition — the
operator picks. For *Reject* verdicts the re-review is never skipped.

### Edge cases routed through the gate
```

- [ ] **Step 2: Verify**

```bash
grep -n "Approve-with-fixes shortcut" skills/sdd-orchestrate/SKILL.md
```

Expected: one hit.

- [ ] **Step 3: Commit**

```bash
git add skills/sdd-orchestrate/SKILL.md
git commit -m "fix(sdd-orchestrate): honor Approve-with-fixes' no-re-review semantics at the gate"
```

---

### Task 18 (F19): sdd-verify small gaps — plan_ref gate, last_updated, generic paths

**Files:**
- Modify: `skills/sdd-verify/SKILL.md` (report template + quality gates)

- [ ] **Step 1: Gate the report frontmatter and rename date**

Old:

```markdown
```markdown
---
date: YYYY-MM-DD
status: pass | fail
plan_ref: docs/plan.md
---
```

New:

```markdown
```markdown
---
last_updated: YYYY-MM-DD
status: pass | fail
plan_ref: docs/plan.md   # marker 4: docs/ws/<ws>/plan.md
---
```

- [ ] **Step 2: Add the legacy-field note after the template**

Old (first line after the closing code fence of the report template):

```markdown
### Step 7: Decide Next Step
```

New:

```markdown
(`last_updated:` matches every other SDD artifact's staleness field; older reports may carry `date:` instead — treat the two as equivalent when reading.)

### Step 7: Decide Next Step
```

- [ ] **Step 3: Genericize the hardcoded src/ paths**

Old:

```markdown
**Language-specific gates:**

Python:
```

New:

```markdown
**Language-specific gates** (paths below are examples — substitute the project's actual source layout, e.g. `ruff check .` or the package directory):

Python:
```

- [ ] **Step 4: Verify**

```bash
grep -n "^date:" skills/sdd-verify/SKILL.md
```

Expected: no output.

- [ ] **Step 5: Commit**

```bash
git add skills/sdd-verify/SKILL.md
git commit -m "fix(sdd-verify): gate plan_ref for v4, align staleness field name, genericize gate paths"
```

---

### Task 19 (F20): De-overload the requirements index `version:` — sdd-migrate

Migrate writes `version: 2.0` as a *format* signal; sdd-requirements bumps the same field for *content* changes. Format is `docs/.sdd-version`'s job.

**Files:**
- Modify: `skills/sdd-migrate/SKILL.md` (Step 2, item 13)

- [ ] **Step 1: Edit item 13**

Old:

```markdown
13. Create `docs/requirements/index.md` with `version: 2.0` in frontmatter, listing all requirement files and their categories.
```

New:

```markdown
13. Create `docs/requirements/index.md` with `version: 1.0` in frontmatter, listing all requirement files and their categories. (The index `version:` tracks requirements-*content* revisions and is bumped by `sdd-requirements`; the artifact-*format* version is tracked solely by `docs/.sdd-version`.)
```

- [ ] **Step 2: Verify**

```bash
grep -n "version: 2.0" skills/sdd-migrate/SKILL.md
```

Expected: no output.

- [ ] **Step 3: Commit**

```bash
git add skills/sdd-migrate/SKILL.md
git commit -m "fix(sdd-migrate): stop overloading the requirements index version field as a format signal"
```

---

### Task 20 (P1): Dedupe the v4 ownership boilerplate across 7 skills

The identical ~10-line "Under marker `4` a workstream **owns only** …" paragraph is copy-pasted into 7 skills — the suite's biggest drift risk (F13 was an instance of exactly this rot).

**Files:**
- Modify: `skills/sdd-research/SKILL.md`, `skills/sdd-requirements/SKILL.md`, `skills/sdd-specs/SKILL.md`, `skills/sdd-plan/SKILL.md`, `skills/sdd-implement/SKILL.md`, `skills/sdd-verify/SKILL.md`, `skills/sdd-replan/SKILL.md`

- [ ] **Step 1: In each of the 7 files, replace the shared paragraph**

Each file contains this paragraph verbatim (sdd-research's begins "Under marker `4` a workstream **owns only** `kickoff.md`, `plan.md`," — the six others are identical; in sdd-replan it directly follows the gate bullet ending "never another workstream's plan/verification."):

Old (identical in all 7 files):

```markdown
Under marker `4` a workstream **owns only** `kickoff.md`, `plan.md`,
`plan-history/`, `verification.md`, and its own `docs/ws/<ws>/traceability.md`. It
never creates `docs/ws/<ws>/requirements/` or `docs/ws/<ws>/spec/` (requirements,
specs, research and the aggregated traceability are shared — ADD to them, never
fork per workstream) and never touches flat `docs/plan.md` / `docs/verification.md`.
Omitting the argument resolves the implicit `default` workstream, so solo use needs
no naming and lands all execution artifacts under `docs/ws/default/`. Approval is a
bare `status` flag — owned `plan.md`/`verification.md` carry their own `status`;
shared `requirements/*` / `spec/*` carry one product-wide `status`; no approver
identity or quorum. Full contract: `docs/spec/ws-layout.md`.
```

New (identical in all 7 files):

```markdown
Ownership, sharing, solo-`default`, and approval semantics under marker `4`
follow the common v4 contract — see `docs/spec/ws-layout.md`. In short: a
workstream owns only its `docs/ws/<ws>/` execution artifacts and per-ws
`traceability.md`; requirements/specs/research and the aggregated traceability
are shared (ADD, never fork); omitting the argument resolves `default`.
```

Note for sdd-research: its variant of this paragraph starts identically — verify with grep before editing; if any file's paragraph differs by a word, preserve that file's extra sentence and still collapse the common body.

- [ ] **Step 2: Verify**

```bash
grep -c "owns only" skills/sdd-*/SKILL.md
```

Expected: `owns only` appears at most once per file (inside the short summary), and

```bash
grep -c "common v4 contract" skills/sdd-*/SKILL.md | grep -v ":0"
```

Expected: 7 files with 1 hit each.

- [ ] **Step 3: Commit**

```bash
git add skills/sdd-research/SKILL.md skills/sdd-requirements/SKILL.md skills/sdd-specs/SKILL.md skills/sdd-plan/SKILL.md skills/sdd-implement/SKILL.md skills/sdd-verify/SKILL.md skills/sdd-replan/SKILL.md
git commit -m "refactor(skills): collapse duplicated v4 ownership boilerplate to a pointer"
```

---

### Task 21 (P2): Add when-NOT-to-use clauses to six skill descriptions

The repo's own quality check requires descriptions to "state when to use AND when not to use"; six skills don't.

**Files:**
- Modify: frontmatter `description:` of `skills/sdd-requirements/SKILL.md`, `skills/sdd-specs/SKILL.md`, `skills/sdd-plan/SKILL.md`, `skills/sdd-implement/SKILL.md`, `skills/sdd-verify/SKILL.md`, `skills/sdd-replan/SKILL.md`

- [ ] **Step 1: Append one sentence to each description (inside the existing YAML `>` block)**

- sdd-requirements — after "Can reference prior research from docs/research/." add:
  `Skip for bug fixes and small tweaks that don't change what the system should do.`
- sdd-specs — after "Use after requirements are approved and before implementation begins." add:
  `Skip while requirements are still Draft, or for changes too small to need a design spec.`
- sdd-plan — after "Use after specs are approved and before writing code." add:
  `Skip while specs are unapproved, or for single-task changes that need no ordered plan.`
- sdd-implement — after "Use after the implementation plan is approved." add:
  `Do not use without an approved plan — run sdd-plan first.`
- sdd-verify — after "Use after all plan tasks are complete." add:
  `Skip while tasks remain incomplete; not a substitute for per-task testing.`
- sdd-replan — after "Use when the current plan is no longer valid." add:
  `Skip for routine progress — invoke only when a replan trigger actually fires.`

- [ ] **Step 2: Verify**

```bash
grep -A6 "^description" skills/sdd-requirements/SKILL.md skills/sdd-specs/SKILL.md skills/sdd-plan/SKILL.md skills/sdd-implement/SKILL.md skills/sdd-verify/SKILL.md skills/sdd-replan/SKILL.md | grep -c "Skip\|Do not use"
```

Expected: 6.

- [ ] **Step 3: Commit**

```bash
git add skills/sdd-requirements/SKILL.md skills/sdd-specs/SKILL.md skills/sdd-plan/SKILL.md skills/sdd-implement/SKILL.md skills/sdd-verify/SKILL.md skills/sdd-replan/SKILL.md
git commit -m "docs(skills): add when-not-to-use clauses to six skill descriptions"
```

---

### Task 22 (P3): Budgets in observable units, not wall-clock

Agents can't track wall-clock time; budgets should bind on countable units.

**Files:**
- Modify: `skills/sdd-research/SKILL.md` (Step 1)
- Modify: `skills/sdd-plan/SKILL.md` (Step 3 spike type)
- Modify: `skills/sdd-implement/SKILL.md` (spike step 1)

- [ ] **Step 1: sdd-research Step 1 budget bullet**

Old:

```markdown
- "What's the budget?" — suggest a scope limit (e.g., "explore 3 approaches, max 1 hour")
```

New:

```markdown
- "What's the budget?" — suggest a scope limit in **observable units** an agent can actually track — N approaches, N documents/APIs tried, N prototype iterations (e.g., "explore 3 approaches, ~20 tool calls"); wall-clock time is a secondary hint at best
```

- [ ] **Step 2: sdd-plan spike task type**

Old:

```markdown
- **`spike`** — time-boxed research to resolve a `[high-uncertainty]` section from specs. Produces findings, may cause replan. Budget: state explicitly (e.g., "30 min max")
```

New:

```markdown
- **`spike`** — time-boxed research to resolve a `[high-uncertainty]` section from specs. Produces findings, may cause replan. Budget: state explicitly, in observable units (e.g., "2 approaches, ~15 tool calls")
```

- [ ] **Step 3: sdd-implement spike step 1**

Old:

```markdown
1. **Note the budget** from the plan (e.g., "30 min max")
```

New:

```markdown
1. **Note the budget** from the plan (e.g., "2 approaches, ~15 tool calls")
```

- [ ] **Step 4: Commit**

```bash
git add skills/sdd-research/SKILL.md skills/sdd-plan/SKILL.md skills/sdd-implement/SKILL.md
git commit -m "docs(skills): express spike budgets in observable units instead of wall-clock time"
```

---

### Task 23 (P4): Make DISCUSS's brainstorming dependency optional — sdd-orchestrate

**Files:**
- Modify: `skills/sdd-orchestrate/SKILL.md` (§DISCUSS)

- [ ] **Step 1: Edit the DISCUSS opening**

Old:

```markdown
Before writing any kickoff, reach a shared understanding of the idea with the
operator. **Reuse the brainstorming process** (invoke the brainstorming skill):
explore intent, surface scope boundaries, and capture the open questions the
research stage should answer.
```

New:

```markdown
Before writing any kickoff, reach a shared understanding of the idea with the
operator. **Reuse the brainstorming process** — invoke a brainstorming skill if
one is available in the session; otherwise run the equivalent inline:
explore intent, challenge assumptions, surface scope boundaries, and capture the
open questions the research stage should answer.
```

- [ ] **Step 2: Commit**

```bash
git add skills/sdd-orchestrate/SKILL.md
git commit -m "docs(sdd-orchestrate): make the brainstorming-skill dependency optional in DISCUSS"
```

---

### Task 24 (P5): Honest isolation caveat — sdd-orchestrate + USAGE

**Files:**
- Modify: `skills/sdd-orchestrate/SKILL.md` (§What This Is)
- Modify: `skills/sdd-orchestrate/USAGE.md` (§6)

- [ ] **Step 1: SKILL.md caveat**

Old:

```markdown
Isolation is **by construction**. Each pipeline stage and each review run as a
**separate subagent** with a fresh context window. A freshly dispatched subagent
has no shared window through which your reasoning could leak — a stronger
guarantee than two human terminal sessions.
```

New:

```markdown
Isolation is **by construction**. Each pipeline stage and each review run as a
**separate subagent** with a fresh context window. A freshly dispatched subagent
has no shared window through which your reasoning could leak — a stronger
guarantee than two human terminal sessions. (Honest caveat: a fresh subagent
still inherits repo-level context — `CLAUDE.md`, project memory. The guarantee
covers the working session's reasoning and drafts, not repo documentation.)
```

- [ ] **Step 2: USAGE.md §6 caveat**

Old:

```markdown
window, there is *nothing to leak through* — a stronger guarantee than two human
terminals. This is what lets the review catch framing/scope problems an
in-session check would rationalize away.
```

New:

```markdown
window, there is *nothing to leak through* — a stronger guarantee than two human
terminals. (Caveat: the subagent still reads repo-level context like `CLAUDE.md`;
what's excluded is the working session's reasoning, not repo docs.) This is what
lets the review catch framing/scope problems an in-session check would
rationalize away.
```

- [ ] **Step 3: Commit**

```bash
git add skills/sdd-orchestrate/SKILL.md skills/sdd-orchestrate/USAGE.md
git commit -m "docs(sdd-orchestrate): state the repo-context caveat on subagent isolation"
```

---

### Task 25 (P6): Gloss "shipped legacy rows" at first use in four skills

**Files:**
- Modify: `skills/sdd-requirements/SKILL.md`, `skills/sdd-specs/SKILL.md`, `skills/sdd-implement/SKILL.md`, `skills/sdd-verify/SKILL.md`

- [ ] **Step 1: Insert the gloss at the first "shipped legacy rows" occurrence in each file**

In each file, extend the first occurrence of the phrase with a parenthetical. The occurrences (one per file, inside the regenerate-the-aggregate sentence) all read `shipped legacy rows` — replace the first occurrence in each file:

Old (first occurrence per file): `shipped legacy rows`

New: `shipped legacy rows (rows predating the v4 migration, attributed to the blank/default workstream)`

If a file's occurrence already sits inside a parenthetical, adapt punctuation so the sentence stays well-formed (em-dash instead of nested parens).

- [ ] **Step 2: Verify**

```bash
grep -l "predating the v4 migration" skills/sdd-requirements/SKILL.md skills/sdd-specs/SKILL.md skills/sdd-implement/SKILL.md skills/sdd-verify/SKILL.md | wc -l
```

Expected: 4.

- [ ] **Step 3: Commit**

```bash
git add skills/sdd-requirements/SKILL.md skills/sdd-specs/SKILL.md skills/sdd-implement/SKILL.md skills/sdd-verify/SKILL.md
git commit -m "docs(skills): define 'shipped legacy rows' at first use"
```

---

### Task 26 (P7): One canonical priority encoding — sdd-requirements

Template shows both an RFC keyword in the sentence and a `[Priority: x]` tag. Canonical: the modal verb in the requirement text.

**Files:**
- Modify: `skills/sdd-requirements/SKILL.md` (category file template + conventions)

- [ ] **Step 1: Remove the tags from the template**

Old:

```markdown
### REQ-AUTH-001: User login via OAuth2
The system must authenticate users through OAuth2 providers.
[Priority: must]

### REQ-AUTH-002: Session expiry
User sessions should expire after 30 minutes of inactivity.
[Priority: should]

### REQ-AUTH-003: Remember me option
The system may offer a "remember me" checkbox extending sessions to 30 days.
[Priority: may]
```

New:

```markdown
### REQ-AUTH-001: User login via OAuth2
The system must authenticate users through OAuth2 providers.

### REQ-AUTH-002: Session expiry
User sessions should expire after 30 minutes of inactivity.

### REQ-AUTH-003: Remember me option
The system may offer a "remember me" checkbox extending sessions to 30 days.
```

- [ ] **Step 2: Sharpen the convention bullet**

Old:

```markdown
- Priority (must/should/may) is stated in the requirement text
```

New:

```markdown
- Priority is expressed solely by the requirement's modal verb — must (mandatory), should (preferred), may (optional); no separate `[Priority:]` tag
```

- [ ] **Step 3: Verify**

```bash
grep -n "\[Priority:" skills/sdd-requirements/SKILL.md
```

Expected: at most the convention bullet's negative mention; no template tags.

- [ ] **Step 4: Commit**

```bash
git add skills/sdd-requirements/SKILL.md
git commit -m "docs(sdd-requirements): make the modal verb the single priority encoding"
```

---

### Task 27 (P8): Marker-4 annotations in the fan-out invariants checklist

§0 defines the substitution but the checklist — the part actually executed — still says `main` unqualified.

**Files:**
- Modify: `skills/sdd-orchestrate/references/fan-out.md` (§4)

- [ ] **Step 1: Annotate the two checklist items**

Old:

```markdown
- [ ] All subagents return before any merge; merges are sequential into `main`,
      completed before the implement-stage review.
```

New:

```markdown
- [ ] All subagents return before any merge; merges are sequential into `main`
      (marker `4`: the workstream branch — §0), completed before the
      implement-stage review.
```

Old:

```markdown
- [ ] Conflicts: optional auto-resolve → else `git merge --abort` → redo by
      re-derivation in a worktree re-branched from updated `main` → sequential
      fallback on repeat conflict (guaranteed termination); never corrupt merged work.
```

New:

```markdown
- [ ] Conflicts: optional auto-resolve → else `git merge --abort` → redo by
      re-derivation in a worktree re-branched from updated `main` (marker `4`:
      the workstream branch — §0) → sequential fallback on repeat conflict
      (guaranteed termination); never corrupt merged work.
```

- [ ] **Step 2: Commit**

```bash
git add skills/sdd-orchestrate/references/fan-out.md
git commit -m "docs(sdd-orchestrate): annotate fan-out invariants checklist with marker-4 anchors"
```

---

### Task 28: Final consistency sweep and merge

**Files:** none new (verification + merge)

- [ ] **Step 1: Run the full drift-check sweep**

```bash
grep -rn "docs/spikes" skills/ ; \
grep -rn "assign new domain prefixes" skills/ ; \
grep -rn "upgrade to v2" skills/ ; \
grep -rn "skills/\*/SKILL.md" skills/sdd-review/ ; \
grep -rn "v1 limitations" skills/ ; \
grep -rn "\[Priority:" skills/sdd-requirements/SKILL.md ; \
grep -rn "no plan index in v4" skills/
```

Expected: no output from any grep (except possibly the convention bullet's negative `[Priority:]` mention).

- [ ] **Step 2: Confirm installed skills still resolve (symlinks intact)**

```bash
ls -l ~/.claude/skills/ | grep sdd- | grep -c tools-skills-agents
```

Expected: 10.

- [ ] **Step 3: Review the branch diff as a whole**

```bash
git log --oneline main..fix/sdd-skill-audit
git diff main...fix/sdd-skill-audit --stat
```

Expected: ~28 commits; only files under `skills/` and this plan file changed.

- [ ] **Step 4: Merge (user preference: merge, not rebase)**

```bash
git checkout main
git merge --no-ff fix/sdd-skill-audit -m "merge: fix/sdd-skill-audit — 28 audit findings across the SDD skill suite"
git branch -d fix/sdd-skill-audit
```

Expected: clean merge, branch deleted.

---

## Finding → Task map (coverage check)

| Finding | Task | | Finding | Task |
|---|---|---|---|---|
| F1 spike destinations | 1 | | F15 review non-interactivity | 14 |
| F2 plan frontmatter/mtime | 2 | | F16 multi-language XSPEC | 15 |
| F3 split ID remap | 3 | | F17 v4 per-milestone | 16 |
| F4 greenfield init | 4 | | F18 approve-with-fixes | 17 |
| F5 Q-IMPL race | 5 | | F19 verify small gaps | 18 |
| F6 fan-out shared docs | 6 | | F20 index version overload | 19 |
| F7 Depends-on field | 7 | | P1 boilerplate dedupe | 20 |
| F8 entry-kickoff resume | 8 | | P2 descriptions | 21 |
| F9 review kickoff questions | 9 | | P3 budget units | 22 |
| F10 new-cycle research | 10 | | P4 brainstorm dependency | 23 |
| F11 implement deliverable | 11 | | P5 isolation caveat | 24 |
| F12 review v4 paths | 11 | | P6 jargon gloss | 25 |
| F13 research version text | 12 | | P7 priority encoding | 26 |
| F14 USAGE v4 refresh | 13 | | P8 fan-out checklist | 27 |
