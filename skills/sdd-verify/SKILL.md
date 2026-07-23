---
name: sdd-verify
description: >
  Holistic validation after implementation — goes beyond "tests pass" to verify
  quality gates, acceptance criteria, user-perspective behavior, and regressions.
  Produces docs/verification.md. Use after all plan tasks are complete. Triggers
  sdd-replan if critical failures are found.
---

# SDD: Verification

You are performing holistic verification of a completed implementation. Your job is to confirm that the system works correctly from every angle — not just that tests pass.

## Verification Layers

`sdd-verify` is one of four verification layers in the SDD workflow. The others are: chunk-close (mechanical, in-session, per-chunk), XSPEC (structural, in-session, during sdd-specs), and sdd-review (semantic, out-of-session, at phase boundaries). sdd-verify is the holistic in-session pass at end of project. If you find this skill's scope crossing into another layer's territory, refer to that layer's skill or spec.

## Phase Detection

Before starting, check project state. **Compare dates** to detect stale artifacts:

**Workstream & version gate (v4).** This skill accepts an optional `workstream`
argument that defaults to `default`. Read `docs/.sdd-version` first — it is the
**sole** layout gate:

- **Marker is not `4` (v3 or earlier): behavior UNCHANGED.** Ignore the workstream
  argument and run exactly the numbered detection below against flat
  `docs/plan.md` / `docs/verification.md`; never read or write `docs/ws/`. The v3
  path is unaffected.
- **Marker is `4` (workstream-aware layout).** Resolve `ws` = the workstream
  argument (default `default`), set `base = docs/ws/<ws>/`, and run the same
  detection below but root every **execution artifact** (`plan.md`,
  `verification.md`, `kickoff.md`, `plan-history/`) at `base` — never at flat
  `docs/`. The **shared corpus** stays at its top-level paths and is used as-is:
  `docs/research/`, `docs/requirements/` (index, category files, aggregated
  `traceability.md`), `docs/spec/`.

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

0. **Version check**: If `docs/.sdd-version` is missing, suggest running `sdd-migrate` before proceeding
1. If no `docs/plan.md` → use `sdd-plan`
2. **Staleness check**: compare `last_updated` in `docs/requirements/index.md` and specs against `docs/plan.md` modification date. If upstream artifacts are newer than the plan, the plan is stale → use `sdd-plan` to update before verifying
   - **Workstream-scoped (marker `4` only)**: `docs/.sdd-version` is the sole gate. Under marker `3` (or earlier) run the whole-plan compare above — flat `docs/plan.md` vs all specs/requirements — **unchanged**. Under marker `4` `sdd-verify` gains a **new** workstream-scoped branch (it had no scoped branch before): compare the active workstream's `docs/ws/<ws>/plan.md` / `docs/ws/<ws>/verification.md` **only** against the shared specs/requirements that workstream traces, using the **same live plan-walk** as `sdd-plan`/`sdd-implement` (walk `<ws>`'s tasks' `traces to` specs → each spec's `requires:` requirement IDs → those specs' and requirement category files' `last_updated`; task → spec `requires:` → requirement IDs → category-file dates). It must **not** report staleness from shared-input changes outside `<ws>`'s traced set. This reads **no traceability file** and adds no traceability schema column — the scope is derived live (REQ-WS-027). See `docs/spec/ws-staleness.md`
3. If `docs/plan.md` has incomplete tasks → use `sdd-implement`
4. If all plan tasks are done (or user explicitly requests verification) → you're in the right place
5. If `docs/verification.md` already exists → you're re-verifying (after fixes or replan)

Tell the user which phase you detected and confirm before proceeding.

## Your Role

- Run all quality gates and report results
- Walk through every acceptance criterion in every spec
- Verify user-perspective behavior (not just unit test pass/fail)
- Check for regressions
- Produce a structured verification report
- Trigger replan if critical failures are found

## Process

### Step 1: Load Context

1. Read `docs/plan.md` — confirm all tasks marked done
2. Read all `docs/spec/*.md` — collect every acceptance criterion
3. Read `CLAUDE.md` — identify the project's quality gates
4. Read `docs/requirements/index.md` and `docs/requirements/{category}/*.md` — understand the original intent
5. Read `docs/requirements/traceability.md` — understand current coverage state

### Step 2: Quality Gates

Run all automated quality checks. Report each as pass/fail:

**Language-specific gates:**

Python:
- `ruff check src/` — zero violations
- `ruff format --check src/` — zero reformats needed
- `mypy src/ --strict` — zero errors
- `pytest` — all pass, note duration

Rust:
- `cargo fmt --check` — clean
- `cargo clippy -- -D warnings` — zero warnings
- `cargo test` — all pass

TypeScript:
- `eslint .` — zero violations
- `prettier --check .` — formatted
- `tsc --noEmit` — zero errors
- `npm test` — all pass

Sui Move:
- `sui move build` — zero warnings
- `sui move test` — all pass

Also check:
- Build succeeds (`uv build`, `cargo build --release`, `npm run build`)
- Package is installable/publishable (if applicable)

### Step 3: Acceptance Criteria Walkthrough

For each spec in `docs/spec/`:

1. Read its acceptance criteria section
2. For each criterion:
   - Determine how to verify it (test exists? manual check needed?)
   - Execute the verification
   - Record: pass, fail, or unable-to-verify
3. If a criterion fails: note what's wrong and severity (critical/minor)

### Step 3b: Traceability Verification

Read `docs/requirements/traceability.md` and verify:

1. **Every requirement has a spec** — Spec column is non-empty for all rows
2. **Every implemented requirement has tests** — Test column is non-empty for requirements with Implementation filled
3. **Flag gaps** — list any requirements missing spec, test, or implementation coverage

After verification, update the **Verified** column with pass/fail for each requirement.

**Per-workstream traceability (marker `4` only).** `docs/.sdd-version` is the sole gate.
Under marker `3` or earlier, read and write the single shared
`docs/requirements/traceability.md` directly, as above (unchanged). Under marker `4`,
the aggregate `docs/requirements/traceability.md` remains a convenient read-only
**coverage view** for the checks above, but write the **Verified** column into the
active workstream's OWN file `docs/ws/<ws>/traceability.md` (per-workstream-owned rows,
6-column matrix with the appended `Workstream` column) — never another ws's file and
never the shared aggregate in place — then **regenerate** the shared aggregate wholesale
(shipped legacy rows + concat of every `docs/ws/<id>/traceability.md`, stable-sorted by
requirement id; never hand-merged). See `docs/spec/ws-traceability.md` (REQ-WS-007,
REQ-WS-008).

### Step 4: User-Perspective Validation

Go beyond unit tests. Ask:

- **Does the feature actually work end-to-end?** Start the system, use it as a user would
- **Are error messages helpful?** Trigger common error paths, check the output
- **Is configuration intuitive?** Try setting up from scratch with only the docs
- **Are edge cases handled?** Try unusual inputs, boundary values, empty states

For CLI tools: run them. For servers: start them and make requests. For libraries: write a minimal usage example.

### Step 5: Regression Check

- Run the full test suite (not just new tests)
- If there's a pre-existing test suite, confirm nothing regressed
- Check git diff against the base branch — are there unintended changes?
- **Regression base (marker `4`)**: under `docs/.sdd-version` == `4` the regression base is the **workstream branch point**, `merge-base(<ws>, main)` — diff `<ws>` HEAD against that base, not `main` HEAD, so verification reflects only this workstream's delta. The full re-anchored regression-base contract is specified in Chunk 4 / `docs/spec/ws-integration.md` (REQ-WS-018); under marker `3` diff against the base branch exactly as above, unchanged.

### Step 6: Write Verification Report

**Workstream scoping (marker `4`)**: under `docs/.sdd-version` == `4`, write the
report to the active workstream's `docs/ws/<ws>/verification.md` (default
`default`) — **never** the flat `docs/verification.md` and never another
workstream's file. Under marker `3` (or earlier) save to `docs/verification.md`
exactly as below, unchanged.

Save to `docs/verification.md` (or `docs/ws/<ws>/verification.md` under marker `4`):

```markdown
---
date: YYYY-MM-DD
status: pass | fail
plan_ref: docs/plan.md
---

# Verification Report

## Summary
[One paragraph: overall status — pass or fail with how many issues]

## Quality Gates

| Gate | Status | Notes |
|------|--------|-------|
| Lint | pass/fail | details |
| Format | pass/fail | details |
| Type check | pass/fail | details |
| Unit tests | pass/fail | X pass, Y fail, Zs duration |
| Build | pass/fail | details |

## Acceptance Criteria

### [spec-name.md]

| Criterion | Status | Evidence |
|-----------|--------|----------|
| [criterion text] | pass/fail/unable | [how verified] |
| ... | ... | ... |

### [another-spec.md]
...

## User-Perspective Validation

| Scenario | Status | Notes |
|----------|--------|-------|
| [end-to-end usage] | pass/fail | what happened |
| [error handling] | pass/fail | what happened |
| ... | ... | ... |

## Regressions
- [None found / List of regressions]

## Issues Found

### Critical (blocks release)
- [issue description — what's wrong, where]

### Minor (can ship, fix later)
- [issue description]

## Recommendation
- [ ] Ship as-is
- [ ] Fix critical issues then ship (invoke sdd-replan)
- [ ] Significant rework needed (invoke sdd-replan)
```

### Step 7: Decide Next Step

Based on the report:

- **All pass, no issues** → tell the user "verification complete, ready to ship". Note that the active plan can now be archived to `docs/plan-history/` if desired
- **Minor issues only** → ask user: "fix now or ship and track as follow-up?"
- **Critical issues** → recommend `sdd-replan` with the failure context. Under
  marker `4`, route **only** the active workstream `<ws>` into replan — never
  another workstream's plan/verification

## Rules

- **Evidence over assertion**: never write "pass" without running the actual check
- **Run, don't read**: execute commands, don't just read test files and assume they pass
- **User perspective matters**: a passing test suite with a broken UX is a fail
- **Be specific about failures**: "test_foo failed" is useless. Include the error, the expected vs actual, and which spec criterion it maps to
- **Don't fix during verify**: your job is to report, not fix. If you find issues, document them and recommend replan. Fixing during verification muddies the report
