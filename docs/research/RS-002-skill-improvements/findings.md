---
id: RS-002
status: Complete
date: 2026-05-25
questions:
  - "How should chunk-close review work to catch spec-implementation drift between milestones?"
  - "Should Q-IMPL deviation protocol be a first-class SDD artifact?"
  - "How should SDD skills handle multi-milestone iteration?"
  - "Is structural drift detection between specs and implementation feasible?"
  - "Where should traceability matrix enforcement happen in the workflow?"
  - "Is cross-spec consistency checking tractable from a workflow skill?"
budget: "4-6 hours"
---

# Research: SDD Skill Improvements from M1 Friction

## Questions

These questions arose from the rubric M1 cycle (7 chunks + spike, ~46h,
101 requirements, 474 tests). The M1 cycle exercised every SDD skill
against a real project and surfaced systematic friction patterns.

1. How should chunk-close review work to catch spec-implementation drift?
2. Should Q-IMPL deviation protocol be a first-class artifact?
3. How should SDD handle multi-milestone iteration?
4. Is structural drift detection feasible from skill instructions?
5. Where should traceability enforcement happen?
6. Is cross-spec consistency checking tractable?

## Findings

### P1: Chunk-Close Review

**Answer**: Add a structured review checklist to `sdd-implement`'s milestone
checkpoint (Step 4), not a separate sub-skill. The checklist catches the 5
failure modes observed in M1 through targeted grep-style checks.

**Evidence**:

*Current skill state*: `sdd-implement` has no concept of "chunk." The rubric
plan introduced "chunks" as plan-level work units — the skill calls them
"milestones" (Step 4: Milestone Checkpoints). The existing checkpoint does:
run full verification, check acceptance criteria, report to user, get approval.
It does NOT check spec-implementation fidelity, traceability updates, or
contract alignment.

*Sub-skill feasibility*: Claude Code skills cannot invoke other skills
programmatically. Skills reference other skills via text ("recommend invoking
`sdd-replan`"), which tells the user to run the command. A `sdd-chunk-close`
sub-skill would require the user to manually invoke it at each milestone
boundary — adding ceremony without enforcement. Inline checklist in
`sdd-implement` is the pragmatic choice.

*M1 failure modes and their minimal checks*:

| Failure Mode | M1 Example | Minimal Check |
|-------------|------------|---------------|
| Model-name drift | `BreadthAssessment` in spec vs `BreadthAnalysis` in impl | Grep spec code blocks for type names; grep impl for same names; flag mismatches |
| Silent stubbing | VIX futures stubbed to return empty | Check each spec requirement has a corresponding test that exercises real behavior |
| Wrong matching field | Position matched by `symbol` instead of `contract_id` | Read spec's interface contracts; verify impl uses same field names/semantics |
| Missing logic | Exclusion-merge logic absent in reconcile | Walk spec's algorithm steps; verify each has impl counterpart |
| Dead code | Unreachable halt path | Grep for functions defined but never called in the module |

*Proposed checklist* (added to Step 4: Milestone Checkpoints):

1. **Spec-impl type alignment**: For each spec referenced by tasks in this
   milestone, extract data type definitions from spec code blocks. Grep the
   implementation for matching class/field names. Flag any class that exists
   in spec but not impl, or vice versa. Flag any field name mismatch.

2. **Traceability update**: Read `docs/requirements/traceability.md`. For
   each requirement covered by this milestone's tasks, verify the Test and
   Implementation columns are populated. If empty, fill them before
   proceeding.

3. **Test coverage per spec**: For each spec referenced by this milestone,
   verify at least one test file exists that imports from the corresponding
   implementation module. Flag specs with zero test coverage.

4. **Q-IMPL audit**: List any implementation decisions that deviated from
   spec (see P2 below). If any exist and aren't documented as Q-IMPL
   entries, add them before proceeding.

*Failure handling*: The checklist produces findings, not hard blocks. The
operator sees the findings and decides whether to fix before proceeding or
carry forward. This matches M1's actual workflow — some findings were fixed
inline, others became carry-forwards to the next chunk.

*Prior art*: No direct equivalent found in Cursor rules, GitHub Copilot
Workspace, or OpenAI assistants documentation. Cursor rules are static
linting guidance. Copilot Workspace has "plan → implement → review" but
the review is manual PR review, not structured checklist. The closest
analogue is DoD (Definition of Done) checklists in Scrum — a gating list
checked before marking a sprint item complete.

**Confidence**: High — the failure modes are concrete, the checks are
grep-level operations that Claude can perform, and the checklist pattern
fits naturally into the existing Step 4.

**Decision-relevance**: This directly answers "what should chunk-close
review look like" and provides the specific checklist items for the
requirements phase.

---

### P2: Q-IMPL Deviation Protocol

**Answer**: Elevate Q-IMPL to a documented convention in `sdd-implement`,
not a separate artifact type. Keep entries per-spec in "Implementation
Questions" sections. Add a numbering scheme and discovery mechanism.

**Evidence**:

*M1 data*: 9 Q-IMPL entries across 5 spec files:
- `phase0.md`: Q-IMPL-001 (rolling 5-day P&L approximation)
- `phase1.md`: Q-IMPL-002 through Q-IMPL-005 (breadth fallback, config
  param, Warning rename, DXY display field)
- `phase2.md`: Q-IMPL-006 (expiry-today EntryBlock reason)
- `output.md`: Q-IMPL-007, Q-IMPL-008 (latency measurement, permission
  level mapping)
- `cli.md`: Q-IMPL-009 (bootstrap JSON shape)

*Pattern analysis*: All 9 entries follow the same structure:
- Located in an "## Implementation Questions" section at the bottom of
  each spec
- Format: `**Q-IMPL-NNN**: [description of deviation with rationale]`
- Each documents a decision the spec didn't anticipate
- None required full replan — they were all Tier 2 (spec ambiguity,
  keep going)

*Three-tier protocol observed in M1*:
1. **Implementation choice** (no protocol): internal helper naming,
   data structure selection. Not documented.
2. **Spec ambiguity** (Q-IMPL): spec didn't anticipate the situation.
   Add entry, keep implementing. All 9 M1 entries fall here.
3. **Spec contract change** (escalate): spec's public interface must
   change. Stop, edit spec, get re-approved, resume. M1 had 2 of these
   (SPEC-LOG contract_id field, SPEC-IBKR Execution type) — but those
   were caught by external review, not by Q-IMPL protocol.

*Design recommendation*:
- **Location**: Per-spec, in "## Implementation Questions" section. This
  is where M1 put them and it works — questions are co-located with the
  design they refer to.
- **Numbering**: Global sequential (`Q-IMPL-001` through `Q-IMPL-NNN`
  across all specs), not per-spec. Global numbering makes them
  referenceable from plan and traceability without spec context.
- **Discovery**: `sdd-implement` should instruct the implementer to check
  for existing Q-IMPL entries before starting a task (they inform how
  prior ambiguities were resolved). At chunk-close, audit for
  undocumented deviations.
- **Index**: No separate `docs/q-impl.md` index file. Overhead exceeds
  value — Q-IMPL entries are findable by `grep -rn "Q-IMPL" docs/spec/`.
  Cross-spec questions are rare enough to not warrant infrastructure.

*Comparison with ADRs*: Architecture Decision Records (ADRs) serve a
similar purpose — documenting decisions with context and rationale. But
ADRs are heavier (separate files, status lifecycle, supersedes chains).
Q-IMPL entries are inline, ephemeral, and spec-scoped. They're closer
to margin notes than formal records. The rubric project already has ADRs
(`docs/adr/ADR-001` through `ADR-006`) for architectural decisions;
Q-IMPL captures implementation-level decisions that don't rise to
architecture.

**Confidence**: High — pattern is validated by 9 real entries across a
real project. The per-spec location survived the full M1 cycle without
needing reorganization.

**Decision-relevance**: Q-IMPL should be documented as a convention in
`sdd-implement`, with the three-tier protocol explicitly stated. The
chunk-close checklist (P1) includes Q-IMPL audit as item 4.

---

### P3: Milestone Iteration

**Answer**: Option B — separate plan files per milestone — with a thin
index at `docs/plan.md`. Staleness detection needs a `milestone` field
in plan frontmatter.

**Evidence**:

*Current state*: `sdd-plan` produces a single `docs/plan.md`. The rubric
plan.md is 1212 lines covering M1 only. M2-M4 would each add similar
volume. Even with the archive pattern from RS-001 (completed milestones
summarized to one line), the plan grows because each milestone adds
new tasks, dependencies, and deliverables.

*Option analysis*:

**Option A** (frontmatter `milestone:` field, `## Milestones` section):
- Keeps one file but structures it
- Problem: the file still grows. At M4, the Milestones section has 4
  milestone entries each with their task lists. Even summarized, this
  exceeds useful context-window size.
- Problem: staleness detection becomes complex — need to distinguish
  "M1 plan stale" from "M2 plan stale" within the same file.

**Option B** (separate files: `docs/plan-m1.md`, `docs/plan-m2.md`, index
at `docs/plan.md`):
- Each milestone plan is self-contained: ~200-500 lines for tasks,
  dependencies, replan triggers.
- `docs/plan.md` becomes a lightweight index: lists milestones, their
  status, and which plan file is active.
- Staleness is per-file: M1 plan doesn't become stale when M2
  requirements are added, because they're different files.
- Archive pattern still applies: when M1 completes, its plan file
  moves to `docs/plan-history/`.
- Trade-off: slightly more files, but each file is focused and fits in
  context window.

**Option C** (monolithic + filtered views):
- Requires tooling outside the skill (a script or Claude instruction to
  filter by milestone tag).
- Doesn't solve the staleness problem.
- Adds complexity without reducing file size.

*Staleness interaction*: The key insight is that milestones should have
independent staleness chains. M1's plan was written against M1's
requirements subset. If M2 adds new requirements to `index.md` (bumping
`last_updated`), M1's plan is NOT stale — it was never meant to cover
M2 requirements. This requires:
- Plan frontmatter includes `milestone: M1` (or whatever the identifier is)
- Requirements tracked per-milestone (e.g., `index.md` lists which
  requirements belong to which milestone, or milestone-scoped requirement
  subsets)
- Staleness check compares plan's `last_updated` against only the
  requirements/specs relevant to that milestone

*Q-REQ for requirements phase*: The exact mechanism for milestone-scoping
requirements needs design. Options: (a) tag requirements with `milestone:`
in their text, (b) add a milestone mapping table to `index.md`, (c) use
spec-level milestone grouping (specs already list `requires:` which maps
to requirements). This decision belongs in `sdd-requirements` and
`sdd-plan` specs, not here.

**Confidence**: Medium — Option B is sound architecturally, but the
staleness-per-milestone mechanism needs design work in the specs phase.

**Decision-relevance**: Recommend Option B for requirements. The staleness
mechanism is a Q-REQ for the requirements phase.

---

### P4: Silent Drift Between Specs and Implementation

**Answer**: Grep-based structural drift detection is feasible and belongs
in the chunk-close checklist (P1 item 1), not as a separate skill.

**Evidence**:

*Feasibility test*: Spec data types in rubric live in markdown code blocks
under `###` headings. Example from `phase1.md`:

```python
class RegimeAssessment(BaseModel):
    regime_tag: RegimeTag
    spy_trend: SpyTrend
    ...
```

Claude can: (1) extract class names and field names from these code blocks,
(2) grep the implementation for matching class definitions, (3) compare
field names. This is a grep-level operation, not AST parsing.

*What it catches*: The Chunk 4 Phase 1 rework (BreadthAssessment →
BreadthAnalysis, missing `regime_tag` field name, wrong `sector_rs` vs
`sector_relative_strength`) would all be caught by name-matching grep.

*What it misses*: Semantic drift (field exists but has wrong type or
different meaning), logic drift (algorithm differs from spec but types
match), silent stubbing (function exists but returns dummy data). These
require deeper analysis — test execution catches them if tests are
spec-aligned.

*Lock files rejected*: The `docs/spec/_locks/phase1.lock.md` idea adds
a generated artifact that must be maintained. If the lock gets stale,
it's worse than no lock — false confidence. The grep-based check runs
fresh every time and doesn't create maintenance burden.

*Separate skill rejected*: `sdd-drift-check` as a standalone skill would
require the user to remember to invoke it. Embedding it in chunk-close
(P1) ensures it runs automatically at milestone boundaries.

*Trade-off spectrum*:
- Grep-based (recommended): low precision, high robustness, zero
  maintenance cost. Catches name-level drift. Misses semantic drift.
- AST-based: medium precision, language-dependent, needs tooling per
  language. Overkill for a workflow skill.
- Full type comparison: high precision, requires running the type checker
  against spec-generated interfaces. Beyond what a skill can instruct.

**Confidence**: High for the grep-based approach. The check is simple,
catches the most common failure mode (name drift), and has zero false
negative cost (worst case: it doesn't flag a drift that tests would
catch anyway).

**Decision-relevance**: This merges into P1's chunk-close checklist as
item 1 (spec-impl type alignment). No separate skill needed.

---

### P5: Traceability Matrix Enforcement

**Answer**: Enforce at chunk-close (P1 checklist item 2). `sdd-verify`
is a backup check, not the primary enforcement point.

**Evidence**:

*M1 data*: The traceability matrix was forgotten at chunk close 4 out of
7 times. The matrix's `last_updated` is 2026-05-24, but Chunks 5 and 6
completed on 2026-05-25 — confirming the enforcement gap.

*Current skill state*: `sdd-implement` Step 2's Task Completion Checklist
already includes: "Update `docs/requirements/traceability.md`: fill Test
column after writing tests, fill Implementation column after writing code."
But this is a per-task checklist item, and in practice it gets skipped when
focus is on making tests pass. `sdd-verify` (Step 3b) also checks
traceability, but by then bugs have rippled downstream.

*Enforcement point*: The chunk-close checklist (P1) is the right place.
It's a mandatory stop-and-check at milestone boundaries — exactly when
traceability should be verified. The check is:
1. Read `docs/requirements/traceability.md`
2. For each requirement covered by this milestone's tasks (identified via
   plan task → spec `requires:` → requirement IDs), verify Test and
   Implementation columns are populated
3. If empty: fill them before marking the milestone complete

*Authoritative source*: The matrix is hand-edited markdown. This is
correct for the SDD workflow — generating it from spec frontmatter would
require parsing all specs and cross-referencing, which is fragile. Hand-
edited with enforcement-at-boundaries is the right balance.

*`sdd-verify` role*: Keep the traceability check in `sdd-verify` (Step
3b) as a final validation — it catches anything that slipped through
chunk-close. But the primary enforcement is at chunk-close, which is
earlier and cheaper to fix.

**Confidence**: High — the failure mode (forgotten matrix updates) and
the fix (check at milestone boundary) are both well-understood.

**Decision-relevance**: This is P1 checklist item 2. No separate
mechanism needed.

---

### P6: Cross-Spec Consistency

**Answer**: Add a lightweight cross-spec reading pass to `sdd-specs`
(Step 5 expansion), not a separate skill. Accept that this catches
reference-level inconsistencies only, not semantic ones.

**Evidence**:

*M1 example*: SPEC-RECON specified "match by contract_id," but SPEC-LOG's
PositionSnapshot didn't include `contract_id`. Both specs were Approved.
The inconsistency was caught during implementation (Chunk 3 rework),
not during spec review.

*Tractability*: Full structural cross-spec checking (parse all type
definitions, build a type graph, find inconsistencies) is not tractable
from a workflow skill. It would require language-specific parsing and a
type unification algorithm — too complex for markdown-based instructions.

*Lightweight version*: When `sdd-specs` finishes writing all specs (Step
5: Coverage Check), add a cross-reference pass:

1. For each spec, extract external type references — types mentioned in
   the spec that are defined in another spec (identified by `SPEC-*`
   prefix references or cross-spec `###` type headings)
2. For each reference, verify the referenced type exists in the target
   spec with the expected fields
3. Flag mismatches: "SPEC-RECON references `PositionSnapshot.contract_id`
   from SPEC-LOG, but SPEC-LOG's PositionSnapshot doesn't define
   `contract_id`"

This is a reading pass, not a parsing pass — Claude reads both specs and
checks for consistency by name matching. It catches the exact M1 failure
mode.

*Alternative — catch at `sdd-plan`*: The planning phase reads all specs
together for the first time. It could surface inconsistencies during
dependency mapping. But this is too late — specs are already Approved,
and changing them requires going back to spec review. Better to catch
during spec writing.

**Confidence**: Medium — the lightweight reading pass is feasible but
depends on specs having clear type definitions in code blocks. If specs
use prose descriptions instead of code blocks, the check degrades to
"does the other spec mention this concept" which is less precise.

**Decision-relevance**: Recommend adding to `sdd-specs` Step 5. This is
a Q-REQ for the requirements phase — the exact mechanism needs design.

---

## Medium-Priority Threads

### Spike Protocol Formalization

**Finding**: `sdd-implement` already handles spike tasks (Step 2, `[spike]`
type) with time-boxing and findings output. What it lacks is explicit
guidance on code separation: spike code must be throwaway, production code
must be written fresh against the spec.

The rubric M1 spike (`docs/spikes/ib-async-prototype.md`) followed this
pattern correctly: throwaway code in `scripts/spike_ib_async.py` with a
docstring marking it as a spike, production code in Chunk 2 written fresh.
But this wasn't skill-enforced — it was operator discipline.

**Recommendation**: Add a rule to `sdd-implement`'s `[spike]` task section:
"Spike code is throwaway. Write it in a scratch location (`scripts/spike_*`
or a feature branch). Production code for the same functionality must be
written fresh against the spec, not adapted from spike code."

**Confidence**: High. This codifies existing good practice.

### Reviewer Mode

**Finding**: External chunk review caught bugs that the skills missed. The
value came from the reviewer being *outside the implementing session's
context window* — a fresh read of spec + impl without the implementation
history biasing interpretation.

A `sdd-review` skill could provide structured prompts for a reviewer, but
the core value (fresh context) requires a separate Claude session, not just
a skill invocation. The skill can't provide the fresh perspective — only the
session boundary can.

**Recommendation**: Don't build a `sdd-review` skill. Instead, document
the practice: "For critical milestones, run a separate Claude session with
the spec + implementation files and ask for a focused review. The reviewer
should check: spec-impl type alignment, missing logic, dead code, test
coverage of spec requirements." This goes in `CLAUDE.md` as project
conventions, not in a skill.

**Confidence**: Medium. A review skill might still add value for structured
prompts, but the session-boundary benefit can't be replicated within the
implementing session.

### CLAUDE.md as Project Conventions

**Finding**: Skills don't read `CLAUDE.md`. In rubric, the operator had
`alpha-mcp` patterns to reuse (httpx client pattern, structlog setup,
pydantic-settings config); the skills had no way to know.

`sdd-implement` Step 1 (Load Context) already says "Read CLAUDE.md for
project conventions" — but this is an instruction to the implementer, not
a mechanism. The implementer reads it if they remember.

**Recommendation**: Make "Read CLAUDE.md" the first item in Step 1 for all
skills that produce artifacts (`sdd-implement`, `sdd-specs`, `sdd-plan`).
For `sdd-implement`, add a rule: "Project conventions from CLAUDE.md take
precedence over generic patterns — use the project's established libraries,
patterns, and style before introducing new ones."

**Confidence**: High. This is a documentation fix, not a mechanism change.

### Rework Prompts as Artifacts

**Finding**: M1 generated ~6 rework prompts (one per chunk that needed
rework). These lived in conversation history and are lost when the session
ends.

**Recommendation**: Don't formalize rework prompts as artifacts. They are
session-specific instructions that lose value once the rework is complete.
The *findings* from rework are what matter — and those are captured in the
chunk-close checklist (P1) and Q-IMPL entries (P2). Committing rework
prompts to `docs/reworks/` creates files that nobody reads after the first
session.

**Confidence**: High. The cost (more files to maintain) exceeds the value
(archaeological interest).

## Implications for Design

### Changes needed in SDD skills

| Skill | Change | Priority |
|-------|--------|----------|
| `sdd-implement` | Add chunk-close review checklist to Step 4 | P1 |
| `sdd-implement` | Document Q-IMPL three-tier protocol | P2 |
| `sdd-implement` | Add spike code separation rule | Medium |
| `sdd-implement` | Strengthen "Read CLAUDE.md" in Step 1 | Medium |
| `sdd-plan` | Support per-milestone plan files with index | P3 |
| `sdd-plan` | Add `milestone:` frontmatter to plan files | P3 |
| `sdd-specs` | Add cross-spec consistency reading pass (Step 5) | P6 |
| `sdd-verify` | Keep traceability check as backup validation | P5 |
| `sdd-requirements` | Consider milestone-scoping mechanism | P3 |
| `sdd-replan` | Work with per-milestone plan files | P3 |
| CLAUDE.md | Document reviewer mode practice | Medium |

### Approaches ruled out

- **`sdd-chunk-close` as separate skill**: Skills can't invoke sub-skills.
  The user would have to remember to invoke it manually. Inline checklist
  is more reliable.
- **`sdd-drift-check` as separate skill**: Same problem. Drift detection
  belongs in chunk-close checklist.
- **`sdd-review` skill**: Core value (fresh context) requires session
  boundary, not skill invocation.
- **Q-IMPL index file**: Overhead exceeds value. Per-spec location with
  global numbering is sufficient.
- **Spec lock files**: Generated artifacts that go stale. Grep-based
  checks are fresher and maintenance-free.
- **Full AST-based drift detection**: Too complex for a workflow skill.
  Grep-based name matching catches the most common failure mode.
- **Rework prompt artifacts**: Files nobody reads after the first session.

### Key design decisions deferred to specs phase

1. Exact chunk-close checklist wording and integration into Step 4
2. Q-IMPL numbering scheme details (global counter, reset per milestone?)
3. Per-milestone plan file naming convention and index format
4. Milestone-scoping mechanism for requirements and staleness detection
5. Cross-spec reading pass: exact instructions for type reference extraction

## Open Questions

- **Q-REQ-001**: Should milestone-scoped plans reference only milestone-
  scoped requirements, or can they reference any requirement? The rubric
  plan.md Chunk 3 references REQ-RECON-001 through REQ-RECON-013 — some
  of which are M2+ requirements. Need a clear scoping rule.

- **Q-REQ-002**: Should the chunk-close checklist be mandatory (hard
  block) or advisory (findings report)? M1 used advisory (external
  reviewer findings were carry-forwards). But 5/7 chunks needed rework —
  suggesting advisory isn't strong enough. The answer may depend on
  project maturity: new projects need stricter enforcement.

- **Q-REQ-003**: How does the three-tier Q-IMPL protocol interact with
  replan? Currently, Tier 3 (spec contract change) says "stop, escalate,
  edit spec." But `sdd-replan` classifies issues as Level 1-4 based on
  depth. Tier 3 is probably Level 2 (spec gap) in replan terms. Need to
  align the vocabularies.
