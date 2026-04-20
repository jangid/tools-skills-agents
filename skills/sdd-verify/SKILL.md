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

## Phase Detection

Before starting, check project state. **Compare dates** to detect stale artifacts:

1. If no `docs/plan.md` → use `sdd-plan`
2. **Staleness check**: compare `last_updated` in specs against `docs/plan.md` modification date. If specs are newer than the plan, the plan is stale → use `sdd-plan` to update before verifying
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
4. Read `docs/requirements.md` — understand the original intent

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

### Step 6: Write Verification Report

Save to `docs/verification.md`:

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

- **All pass, no issues** → tell the user "verification complete, ready to ship"
- **Minor issues only** → ask user: "fix now or ship and track as follow-up?"
- **Critical issues** → recommend `sdd-replan` with the failure context

## Rules

- **Evidence over assertion**: never write "pass" without running the actual check
- **Run, don't read**: execute commands, don't just read test files and assume they pass
- **User perspective matters**: a passing test suite with a broken UX is a fail
- **Be specific about failures**: "test_foo failed" is useless. Include the error, the expected vs actual, and which spec criterion it maps to
- **Don't fix during verify**: your job is to report, not fix. If you find issues, document them and recommend replan. Fixing during verification muddies the report
