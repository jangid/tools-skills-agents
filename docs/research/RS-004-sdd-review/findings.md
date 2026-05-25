---
id: RS-004
status: Complete
date: 2026-05-25
questions:
  - "What did external review actually catch across two projects?"
  - "What did external review miss?"
  - "What review-report structure emerged consistently?"
  - "What does sdd-review need that other skills don't?"
  - "When should sdd-review run? Trigger points."
  - "What does the skill NOT do?"
budget: "45-60 minutes"
reviewer_bias_disclosure: >
  This research is conducted by the same Claude instance that performed
  external review across both projects. See §Reviewer Bias Disclosure.
---

# Research: sdd-review Skill Design

## Reviewer Bias Disclosure

This research is conducted by the same Claude instance that has performed
external review across rubric M1 (7 chunks, ~46h) and the skills repo's
three research cycles (RS-001 through RS-003). The research design
therefore risks encoding self-justifying patterns — the reviewer is
designing the reviewer skill.

Mitigations attempted: catalog misses as rigorously as hits (F2 is as
long as F1); draw boundaries by reference to what other skills already
cover (F6); resist framing review as universally valuable when historical
evidence shows mixed results at different phase boundaries (F5). The
operator should weight these findings knowing the structural bias exists.

## Summary

External review has caught critical issues at 4 of 7 phase boundaries
where it was applied, with the highest hit rate at requirements→specs
and specs→plan transitions. Three systematic misses trace to a common
root cause: the reviewer didn't have a checklist for "what should have
changed but didn't." The skill design is bounded: ~7 requirements
covering phase detection, report format, required inputs, bias
disclosure, trigger classification, and scope boundaries against the
three existing verification layers.

## Findings

### F1: Review's catch-zone (Q1)

Evidence drawn from git history (commits `19c7ac5`, `489c79b`, `dde2337`)
and conversation-level review events across both projects.

#### Critical catches (prevented multi-hour rework)

1. **Milestone/chunk terminology overload** (requirements review, RS-002).
   The initial requirements used "milestone" for both implementation work
   units and delivery groupings. Review caught this before specs were
   written. Without the fix, every spec would have inherited the ambiguity,
   and sdd-implement's chunk-close mechanism would have triggered at
   delivery milestone boundaries instead of work-unit boundaries. Commit
   `19c7ac5`: 6 files changed, terminology systematically corrected, new
   REQ-CHKC-008 added to anchor chunk identification.

2. **Plan-management.md vocabulary inconsistency** (specs review, RS-002).
   The spec's example plan used `### M3:`, `### M4:` headers and
   `## Milestones` section heading while the requirements specified
   `### Chunk N:` vocabulary. Review caught the mismatch before the plan
   phase. Commit `489c79b`: 48 lines changed in plan-management.md,
   examples updated to use `### Chunk N:` format throughout.

3. **v2→v3 migration gap** (post-RS-002 review). After RS-002 shipped
   (chunk-close, Q-IMPL, per-milestone, cross-spec), the operator
   observed that sdd-migrate hadn't been updated and `.sdd-version`
   still said `2`. This spawned the entire RS-003 cycle. Without this
   observation, downstream operators running sdd-migrate on v2 projects
   would have received no v3 migration path. Note: this catch came from
   the operator, not the formal reviewer — see F2 for why.

4. **Type alias detection scope** (specs review, RS-002). Cross-spec
   consistency spec initially extracted bare `Foo = ...` assignments as
   type aliases, which would match TypeVar declarations, generic params,
   and module-level constants. Review tightened to `TypeAlias`/`NewType`
   patterns only. Without the fix, XSPEC would have produced false
   positives on every real project.

5. **REQ-STALE-001/002 missing from spec coverage** (specs review,
   RS-002). Two staleness requirements had no spec tracing them. Review
   flagged the gap; specs were updated to cover both. Without the fix,
   staleness detection would have been implemented without spec
   acceptance criteria — no way to verify it worked correctly.

#### Material catches (prevented downstream confusion)

6. **REQ-CHKC-002 acceptance criteria granularity** (specs review,
   RS-002). Original had a single criterion for "type alignment check."
   Review split into (a) class names, (b) field names, (c) enum values
   — making each independently verifiable. Commit `489c79b`: criterion
   split visible in chunk-close-review.md.

7. **REQ-CHKC-003 traceability trace chain** (requirements review,
   RS-002). Original specified traceability check using structural
   frontmatter parsing. Review changed to prose spec references +
   `requires:` extraction — matching how the skill actually reads specs.

8. **REQ-SKILL-012 priority bump** (requirements review, RS-002).
   CLAUDE.md reading was "should" priority. Review bumped to "must"
   with rationale: CLAUDE.md is load-bearing for project conventions,
   not optional context. Commit `19c7ac5`.

9. **Q-IMPL append-only numbering** (requirements review, RS-002).
   Original numbering scheme didn't address what happens when entries
   are superseded. Review added explicit append-only policy with
   `[superseded by Q-IMPL-NNN]` status notes.

10. **XSPEC flag-only policy** (requirements review, RS-002). Original
    didn't specify whether cross-spec findings were auto-fixed or
    flagged. Review made it explicitly flag-only, preserving operator
    judgment on resolution.

#### Minor catches (polish-level)

11. **Spec status management** — specs set to Approved after content
    changes needed status reset to Draft/Under Review.
12. **Cross-spec consistency spec scope limits** — added "no transitive
    checking" and "code blocks only" clarifications.
13. **RS-003 spec polish** — overview.md directory tree comment updated
    from `"2"` to `"2" or "3"`, migration.md gained multi-path framing
    note. Both in commit `dde2337`.

### F2: Review's miss-zone (Q2)

#### Miss 1: v2→v3 migration scope (RS-002 cycle completion)

**What happened**: RS-002 shipped with all 5 chunks verified, all
acceptance criteria passing. Neither the working session nor the
reviewer flagged that sdd-migrate still only knew about v1→v2, or that
`.sdd-version` should become `3`. The operator caught it.

**Root cause**: The reviewer checked whether the delivered work matched
the plan and specs. The question "what *should* have been in scope but
wasn't" is a different kind of check — it requires stepping back from
the deliverables and asking "is the project complete from an operator's
perspective?" The in-session verification (sdd-verify) also missed it
because sdd-verify walks acceptance criteria from specs, and the specs
didn't include migration or version bump requirements.

**Would a checklist have caught it?** Yes — a phase-boundary question
like "After this project ships, what changes for downstream operators?
Are there migration paths, version markers, or documentation that need
updating?" would have surfaced the gap. This is a *scope completeness*
check, distinct from *spec compliance* checks.

#### Miss 2: Approved-status-with-content-changes (RS-002 specs phase)

**What happened**: Specs were marked Approved, then content was changed
to fix review findings. The status should have been reset to
Draft/Under Review during the edit, then re-Approved. This was caught
on a subsequent review pass, not on the first.

**Root cause**: The review focused on content correctness, not process
compliance. Status field management is a mechanical check.

**Would a checklist have caught it?** Yes — a simple "verify all spec
frontmatter `status` fields match their actual review state" would
catch it. This is the kind of check that's easy to miss ad-hoc but
trivial on a checklist.

#### Miss 3: Plan template vocabulary in plan-management.md (RS-002 specs phase)

**What happened**: plan-management.md used `### M3:` / `### M4:` in its
example plan template. This was caught during a pre-approval review
pass, but only after the spec had been under review for a cycle.

**Root cause**: The reviewer read the spec's prose and design sections
carefully but skimmed the example code blocks. Examples are where
vocabulary inconsistencies hide because they're concrete instances of
abstract rules.

**Would a checklist have caught it?** Partially — "verify all code
blocks and examples use the vocabulary defined in the spec's own
terminology" is a useful checklist item. More broadly, examples should
be treated as first-class content during review.

#### Miss 4: REQ-STALE-001 traceability gap

**What happened**: REQ-STALE-001 had no spec coverage. This was caught
during the specs review, but should have been caught during the
requirements→specs transition check — a simple coverage scan of
traceability.md would have flagged it.

**Root cause**: The reviewer focused on the content of new specs rather
than checking coverage of existing requirements. The traceability
matrix was updated as a side-effect, not as a primary review input.

**Would a checklist have caught it?** Yes — "read traceability.md and
flag any requirement with an empty Spec column that should have been
covered by this phase's work" is a concrete checklist item.

#### Pattern analysis

Three of four misses share a root cause: **the reviewer checked whether
delivered content was correct, but not whether the right content was
delivered.** This maps to two distinct review modes:

- **Content review**: "Is what's here correct?" (catches: terminology,
  type definitions, acceptance criteria granularity, scope limits)
- **Scope review**: "Is what should be here actually here?" (misses:
  migration gap, coverage gaps, status field hygiene)

The skill should make both modes explicit in its checklist structure.

### F3: Review report structure (Q3)

The review reports produced across both projects followed a consistent
structure that emerged through practice:

```
1. Verdict (Approve / Approve with fixes / Reject)
2. Strengths (brief)
3. Critical findings (must fix before next phase)
4. Material findings (should fix, can proceed)
5. Minor findings (polish, defer if needed)
6. Recommendation (concrete next action)
```

#### Structure evaluation

**Verdict states**: Three states (Approve / Approve with fixes / Reject)
are sufficient. "Conditional Approve" would be semantically identical to
"Approve with fixes" — the condition IS the fixes. Keep three states.

- **Approve**: Proceed to next phase. No blocking findings.
- **Approve with fixes**: Proceed after addressing critical findings.
  Material findings may be carried forward with documentation.
- **Reject**: Significant rework needed. Return to current or earlier
  phase. Invoke sdd-replan.

**Strengths section**: Keep as required but brief (2-4 bullet points
max). Its value is calibration — the reviewer demonstrates they read
the work carefully, not just hunted for flaws. Without it, operators
can't distinguish "the reviewer found nothing good" from "the reviewer
didn't read thoroughly." However, it must be substantive: "good work"
is padding; "the staleness detection chain correctly handles the
multi-milestone case" is useful.

**Findings classification**: The three-tier severity (Critical /
Material / Minor) maps cleanly to action:

| Severity | Action | Blocking? |
|----------|--------|-----------|
| Critical | Must fix before next phase | Yes |
| Material | Should fix; can proceed with carry-forward note | No |
| Minor | Fix if convenient; defer without documentation | No |

Each finding should cite: (a) what's wrong, (b) where (file + section),
(c) which requirement or spec criterion is affected, (d) suggested fix.
Generic findings ("some inconsistencies exist") are not actionable and
should be avoided.

**Recommendation**: Must be concrete. "Proceed to sdd-plan" is better
than "looks good." When fixes are needed, list them explicitly:
"Fix findings C1 and C2, then approve. M1 can be carried forward."

#### Persistence question

Should reviews be persisted to `docs/reviews/`?

**Recommendation: No.** Reviews are transient — their value is consumed
at the phase boundary. The durable artifacts are the fixes applied to
specs/requirements/plan, not the review itself. Persisting reviews
creates files that nobody reads after the first session. The RS-002
verification report (`docs/verification-rs002.md`) captures the
equivalent information in a more useful form — what was verified, not
what was reviewed.

Exception: if a review produces findings that are deferred (material
findings carried forward), those should be tracked in the project's
plan or issues, not in a review artifact.

### F4: Skill mechanics (Q4)

#### Phase detection

sdd-review is phase-agnostic — it can review artifacts from any SDD
phase. Phase detection determines which checklist to apply:

| Artifact being reviewed | Detected phase | Checklist focus |
|------------------------|----------------|-----------------|
| `docs/research/RS-*/findings.md` | Research | Completeness, evidence quality, scope boundaries |
| `docs/requirements/**/*.md` | Requirements | Testability, terminology, coverage, priority |
| `docs/spec/*.md` | Specs | Design coherence, vocabulary consistency, acceptance criteria quality, coverage |
| `docs/plan.md` | Plan | Task ordering, trace completeness, risk identification, scope alignment |
| Chunk close output (in-session) | Implementation | Content vs scope review (see F2 pattern analysis) |
| `docs/verification.md` | Verification | Evidence quality, criteria coverage, recommendation alignment |

Detection logic: read the artifacts the operator points to (or the
most recently modified phase artifacts). The reviewer doesn't need to
detect the project's current phase — they review what they're given.

#### Required inputs

The reviewer needs:

1. **The deliverable** — the artifact(s) being reviewed
2. **Prior phase output** — the upstream artifact that the deliverable
   was produced from (e.g., requirements when reviewing specs)
3. **The kickoff/brief** — if available, the instructions that initiated
   the phase. This provides intent context: what was the phase trying
   to accomplish?
4. **Traceability matrix** — `docs/requirements/traceability.md` for
   coverage checks

The reviewer does NOT need:

- The working session's internal deliberation or conversation history
- Draft versions or intermediate states
- The implementer's commit history (git log is available but not
  required input)

The separation is important: the reviewer's value comes from reading
the deliverable fresh, without the working session's sunk-cost bias.

#### Bias disclosure

When the reviewer has prior involvement in the project (reviewed
earlier phases, provided requirements, wrote the kickoff), the review
report should include a bias disclosure section:

```markdown
## Reviewer Context
- Prior involvement: [e.g., "Reviewed RS-002 requirements and specs"]
- Potential bias: [e.g., "May under-scrutinize requirements I previously
  approved"]
```

This is informational — the operator decides how to weight findings
given the disclosed bias. For projects where the reviewer has no prior
involvement, this section is omitted.

#### Recursion

How does sdd-review review its own output? In v1 of the skill: it
doesn't. Self-review is out of scope. The review skill produces a
report; the operator decides whether to act on findings. If the
operator wants a second opinion on the review itself, they run another
review session — the skill supports this naturally since each
invocation is a fresh session.

### F5: Trigger points (Q5)

Ranking phase boundaries by historical hit rate across both projects:

| Boundary | Reviews done | Catches | Hit rate | Classification |
|----------|-------------|---------|----------|----------------|
| Requirements → Specs | 2 | 8 (2 critical, 4 material, 2 minor) | High | **Mandatory** |
| Specs → Plan | 2 | 5 (2 critical, 2 material, 1 minor) | High | **Mandatory** |
| Plan → Implement | 1 | 2 (1 material, 1 minor) | Medium | Recommended |
| Research → Requirements | 1 | 1 (1 minor) | Low | Optional |
| Chunk close | 0 (handled by in-session chunk-close) | N/A | N/A | **Skip** |
| Post-verification | 1 | 1 (the v3 migration gap — operator catch) | Special | Recommended |

#### Classification rationale

**Mandatory** (requirements→specs, specs→plan): These transitions
translate between abstraction levels — requirements to design,
design to execution plan. Translation errors compound: a terminology
error in requirements becomes a vocabulary inconsistency in specs,
which becomes wrong trigger conditions in the plan. Historical data
shows the highest catch rate here.

**Recommended** (plan→implement, post-verification): Useful but
lower hit rate. Plan→implement review catches scope alignment issues.
Post-verification review catches the "is the project complete from an
operator's perspective" question (the miss that spawned RS-003).

**Optional** (research→requirements): Research findings are
exploratory; requirements formalize them. The translation is usually
straightforward. Review is valuable when research scope is contested
or when multiple approaches were considered.

**Skip** (chunk close during implementation): Already covered by the
in-session chunk-close mechanism (sdd-implement Step 4). Adding
external review at every chunk boundary would be excessive ceremony.
Exception: for critical chunks where rework cost is high, the
operator can invoke sdd-review ad-hoc.

#### Trigger point recommendation

The skill should define three trigger classes:

1. **Mandatory**: review before proceeding. Requirements→specs and
   specs→plan boundaries.
2. **Recommended**: review is valuable but operator judgment on whether
   to invoke. Plan→implement and post-verification boundaries.
3. **Ad-hoc**: operator invokes when they want a second opinion on any
   artifact. No trigger — on demand.

The skill should NOT enforce mandatory triggers — it has no mechanism
to block phase transitions. It documents which boundaries are
highest-value so operators know where to invest review time.

### F6: Scope boundaries (Q6)

Four verification layers, each with a distinct catch-zone:

| Layer | Session | Timing | Catches | Misses |
|-------|---------|--------|---------|--------|
| **Chunk-close** | In-session | Per-chunk | Type drift, traceability gaps, undocumented deviations, test coverage | Scope gaps, cross-phase coherence, external readability |
| **XSPEC** | In-session | During sdd-specs | Type reference mismatches between specs | Prose inconsistencies, vocabulary drift, scope gaps |
| **sdd-verify** | In-session | End of project | Acceptance criteria compliance, quality gates, traceability completeness | Design coherence, scope completeness, operator perspective |
| **sdd-review** | Out-of-session | Phase boundaries | Design coherence, scope completeness, vocabulary consistency, external readability, missing scope | Mechanical drift (types, traceability), deep implementation bugs |

#### What sdd-review does

1. **Semantic coherence**: Do the artifacts make sense as a whole? Is
   the terminology consistent? Do the design decisions follow from the
   requirements?
2. **Scope completeness**: Is everything that should be here actually
   here? Are there gaps between what the project claims to deliver and
   what the artifacts cover?
3. **External readability**: Would an operator outside the working
   session understand these artifacts? Are assumptions explained? Are
   cross-references accurate?
4. **Translation fidelity**: When artifacts translate between
   abstraction levels (requirements→specs, specs→plan), does the
   translation preserve intent without losing or adding scope?

#### What sdd-review does NOT do

1. **Mechanical drift detection** — chunk-close handles type/field
   name matching between specs and implementation.
2. **Type cross-reference validation** — XSPEC handles structural
   consistency between specs during the specs phase.
3. **Acceptance criteria walkthrough** — sdd-verify does holistic
   criterion-by-criterion verification against implementation.
4. **Auto-fix** — review is read-only. It produces findings; fixes
   happen in the working session. The reviewer never edits project
   artifacts.
5. **Dispute arbitration** — the reviewer produces findings with
   rationale. The operator decides whether to act on them. The
   reviewer is not the authority.
6. **In-session invocation** — sdd-review must run in a separate
   Claude session. The bias-isolation property (fresh context, no
   sunk-cost bias) is the skill's core value proposition. Any design
   that allows in-session invocation defeats this purpose.

#### Overlap management

The content review / scope review distinction (F2) maps to the
layer boundaries:

- **Content review** partially overlaps with chunk-close (both check
  whether what exists is correct). Difference: chunk-close checks
  mechanically (grep for type names); sdd-review checks semantically
  (does the design make sense).
- **Scope review** has no overlap with other layers. This is
  sdd-review's unique contribution — asking "what's missing" rather
  than "what's wrong with what's here."

## Out-of-Scope Observations

1. **Review as a gate vs review as advice.** The current design treats
   review as advisory — findings inform the operator but don't block
   phase transitions. An alternative design would make mandatory
   reviews actual gates (phase can't proceed without review approval).
   This requires tooling changes (phase detection that checks for a
   review artifact) and adds significant ceremony. Not recommended for
   v1 but worth revisiting if review-skipping causes problems.

2. **Multi-reviewer scenarios.** When multiple reviewers review the
   same artifact, their findings may conflict. The current design
   doesn't address reconciliation. In practice, the operator is the
   arbiter. Not in scope for v1.

3. **Review of non-SDD artifacts.** The skill is designed for SDD
   phase artifacts (research, requirements, specs, plan, verification).
   Reviewing code directly (PR review) is a different workflow with
   different checklists. Could be a separate skill or a mode of
   sdd-review, but out of scope for this cycle.

4. **Metrics and tracking.** Counting catches, tracking hit rates,
   measuring review effectiveness over time — all useful for process
   improvement but not in scope for the skill itself. The operator can
   derive this from review reports and git history.

## Recommendation

Proceed to `/sdd-requirements` with ~7 requirements:

1. **REQ-REV-001**: Phase detection — sdd-review detects which SDD
   phase artifacts are being reviewed and applies appropriate checklist
2. **REQ-REV-002**: Report format — structured report with verdict,
   strengths, tiered findings, recommendation
3. **REQ-REV-003**: Required inputs — deliverable, prior phase output,
   traceability matrix; NOT working session history
4. **REQ-REV-004**: Bias disclosure — reviewer discloses prior
   involvement when applicable
5. **REQ-REV-005**: Trigger classification — mandatory, recommended,
   and ad-hoc boundaries defined with rationale
6. **REQ-REV-006**: Scope boundaries — explicit boundaries against
   chunk-close, XSPEC, and sdd-verify
7. **REQ-REV-007**: Session isolation — review must run in a separate
   session; in-session invocation is prohibited

One skill file (`skills/sdd-review/SKILL.md`) is sufficient. Phase-
specific checklists are sections within the skill, not separate skills.
The skill is comparable in size to sdd-verify (~200-250 lines).

The RS-002 finding that recommended against sdd-review ("core value
requires session boundary, not skill invocation") was correct about
the mechanism but wrong about the conclusion. A skill can define
structure and checklists for an out-of-session reviewer without being
invoked in-session. The skill provides the *what to check* and *how
to report*; the session boundary provides the *fresh perspective*.
Both are necessary.
