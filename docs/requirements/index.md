---
version: "11.0"
last_updated: 2026-07-21
traceability: traceability.md
---

# Requirements Index

## Summary

Requirements for SDD (Spec-Driven Development) skill improvements in the
tools-skills-agents repository. Covers three scopes:

1. **v2 artifact structure** (RS-001): Research structure, requirements
   splitting, plan management, staleness detection, migration, and per-skill
   updates for the v2 layout.
2. **Workflow improvements** (RS-002): Chunk-close review, Q-IMPL deviation
   protocol, multi-milestone plan iteration, cross-spec consistency, and
   per-skill updates for workflow changes.
3. **v3 migration** (RS-003): Migration path from v2 to v3 — plan vocabulary
   rename, version marker update, backward compatibility, documentation
   consistency.
4. **External review** (RS-004): Formal sdd-review skill for structured
   out-of-session review at phase boundaries — phase detection, report
   format, session isolation, scope-completeness checking.
5. **Orchestration driver** (RS-005): `sdd-orchestrate` driver skill running
   the nine SDD skills as a single-operator loop with per-stage subagent
   review — DISCUSS/KICKOFF/LOOP/DONE phases, dispatch-time isolation,
   non-interactivity contract, human gates, resume via phase detection.
6. **Multi-workstream SDD** (RS-007): concurrent SDD cycles in one repo via a
   v4 layout — execution artifacts under `docs/ws/<id>/`, requirements/specs a
   shared corpus, workstream-prefixed IDs, merge-safe shared writes,
   workstream-scoped staleness, branch-per-workstream → PR integration, v3→v4
   migration, and a ceremony-free implicit `default` workstream for solo use.

## Stakeholders

- **Pankaj Jangid** — skills owner and operator. Used all SDD skills across
  the rubric M1 cycle (7 chunks, ~46h). Provided friction observations.

## Files

| Category | File | Domain | Requirements | Status | Last Updated |
|----------|------|--------|-------------|--------|--------------|
| functional | [research-structure.md](functional/research-structure.md) | RS | REQ-RS-001..003 | Approved | 2026-04-28 |
| functional | [requirements-structure.md](functional/requirements-structure.md) | REQ | REQ-REQ-001..007 | Approved | 2026-04-28 |
| functional | [plan-management.md](functional/plan-management.md) | PLAN | REQ-PLAN-001..004 | Approved | 2026-04-28 |
| functional | [staleness-detection.md](functional/staleness-detection.md) | STALE | REQ-STALE-001..003 | Approved | 2026-05-25 |
| functional | [migration.md](functional/migration.md) | MIG | REQ-MIG-001..015 | Approved | 2026-05-25 |
| functional | [chunk-close.md](functional/chunk-close.md) | CHKC | REQ-CHKC-001..008 | Approved | 2026-05-25 |
| functional | [deviation-protocol.md](functional/deviation-protocol.md) | QIMPL | REQ-QIMPL-001..003 | Approved | 2026-05-25 |
| functional | [milestone-plans.md](functional/milestone-plans.md) | MPLAN | REQ-MPLAN-001..004 | Approved | 2026-05-25 |
| functional | [cross-spec-consistency.md](functional/cross-spec-consistency.md) | XSPEC | REQ-XSPEC-001..002 | Approved | 2026-05-25 |
| functional | [review.md](functional/review.md) | REV | REQ-REV-001..008 | Approved | 2026-05-25 |
| functional | [orchestration.md](functional/orchestration.md) | ORCH | REQ-ORCH-001..033 | Approved | 2026-06-06 |
| functional | [multi-workstream.md](functional/multi-workstream.md) | WS | REQ-WS-001..029 | Approved | 2026-07-21 |
| non-functional | [context-and-compatibility.md](non-functional/context-and-compatibility.md) | CTX, COMPAT | REQ-CTX-001..002, REQ-COMPAT-001..002 | Approved | 2026-05-25 |
| integration | [skill-updates.md](integration/skill-updates.md) | SKILL | REQ-SKILL-001..018 | Approved | 2026-05-25 |
| configuration | [version-marker.md](configuration/version-marker.md) | CFG | REQ-CFG-001 | Approved | 2026-05-25 |

> **ORCH delta note:** The ORCH domain mixes shipped requirements (REQ-ORCH-001..015,
> 017..021, all traced and `pass`) with a freshly-added implement-fan-out delta —
> REQ-ORCH-016 (promoted) and REQ-ORCH-022..028. That delta was added at the
> requirements phase and is **not yet specced or implemented**; its traceability
> Spec/Impl/Verified columns are intentionally blank pending the specs and implement
> phases. The specs phase should treat REQ-ORCH-016 and REQ-ORCH-022..028 as the
> new work to design.

> **WS delta note:** The `WS` domain (REQ-WS-001..029, RS-007) is the
> multi-workstream v4 feature, added at `status: Draft` (authored by a
> non-interactive pipeline subagent; operator approval is pending at the
> orchestration gate). It is not yet specced or implemented — its traceability
> Spec/Impl/Verified columns are intentionally blank pending the specs and
> implement phases. This supersedes the earlier "Forward planning to v4" /
> "Formal 4 → migration" out-of-scope note below, which applied to the RS-002/003
> cycle: v4 is now the in-scope work for this cycle.

## Domain Prefixes

| Prefix | Domain | File |
|--------|--------|------|
| RS | Research Structure | functional/research-structure.md |
| REQ | Requirements Structure | functional/requirements-structure.md |
| PLAN | Plan Management | functional/plan-management.md |
| STALE | Staleness Detection | functional/staleness-detection.md |
| MIG | Migration | functional/migration.md |
| CHKC | Chunk-Close Review | functional/chunk-close.md |
| QIMPL | Q-IMPL Deviation Protocol | functional/deviation-protocol.md |
| MPLAN | Milestone Plan Iteration | functional/milestone-plans.md |
| XSPEC | Cross-Spec Consistency | functional/cross-spec-consistency.md |
| REV | External Review | functional/review.md |
| ORCH | SDD Orchestration Driver | functional/orchestration.md |
| WS | Multi-Workstream SDD | functional/multi-workstream.md |
| CTX | AI Context Budget | non-functional/context-and-compatibility.md |
| COMPAT | Git Compatibility | non-functional/context-and-compatibility.md |
| SKILL | Skill Updates | integration/skill-updates.md |
| CFG | Configuration | configuration/version-marker.md |

## Q-REQ Resolutions

Resolved during requirements gathering for RS-006 (implement-stage fan-out):

- **Q-REQ-A** (fan-out feasibility / design): Implement-stage fan-out is now
  **supported** (REQ-ORCH-016 promoted from `may`/deferred to `must`), built as
  **Design B — orchestrator-owned fan-out, one level deep** (REQ-ORCH-022). RS-006
  Q1 proved a dispatched subagent has no subagent-dispatch tool, so the nested
  Design A (implement subagent owns its own fan-out) is infeasible; the
  orchestrator must dispatch the parallel implement subagents itself.
- **Q-REQ-B** (fan-out boundaries & worktrees): Fan out along the plan's
  independent chunk-dependency branches, one git worktree per concurrently-runnable
  chunk-group (REQ-ORCH-016, REQ-ORCH-023).
- **Q-REQ-C** (opt-in vs default): Fan-out is opt-in at the implement gate
  (REQ-ORCH-024); sequential execution remains the default (REQ-ORCH-015 updated).
- **Q-REQ-D** (merge & conflict policy): Worktree branches merge sequentially into
  `main` before the implement-stage review (REQ-ORCH-025); conflicts are resolved
  automatically, with `git merge --abort` + redo-at-orchestrator as the fallback,
  never corrupting already-merged work (REQ-ORCH-026). RS-006 Q3 proved this safe.
- **Q-REQ-E** (subagent git identity): Fan-out subagents commit with inline
  `git -c user.email=... -c user.name=...` flags because the subagent sandbox
  blocks shared `.git/config` writes (REQ-ORCH-027; RS-006 Q2 caveat).
- **Q-REQ-F** (dispatch concurrency): Whether N parallel subagents run truly
  concurrently vs serialized is **unverified** and carried as a `[needs-spike]`
  requirement (REQ-ORCH-028) to resolve at spec/implementation time. The design
  holds either way; only wall-clock speedup is at stake (RS-006 Open Questions).
- **Q-REQ-G** (worktree ownership): **Decision — the orchestrator provisions the
  worktrees** (REQ-ORCH-023), not the fan-out subagents. RS-006 Q2 showed BOTH
  approaches work — an orchestrator-pre-created worktree and a subagent-created
  worktree both succeed — and permitted either; orchestrator ownership was merely
  noted as "cleaner." We harden that preference into a requirement so worktree
  lifecycle and cleanup belong to a single owner (the orchestrator), which keeps
  provisioning and teardown symmetric and avoids orphaned subagent-created
  worktrees. RS-006 permitted either approach; this entry records the deliberate
  narrowing to orchestrator-provisioned.

Resolved during requirements gathering for RS-005:

- **Q-REQ-A** (entry points): Research-entry only for v1 (REQ-ORCH-005). The
  kickoff writer emits a research kickoff and the loop starts at research.
  Mid-pipeline entry deferred — keeps the driver's phase logic minimal and
  matches the dogfooding path.
- **Q-REQ-B** (fan-out scope): Deferred from v1 (REQ-ORCH-015). v1 runs every
  stage sequentially in the main workspace; parallel implement-stage fan-out is
  a follow-on feature. Gets the loop working before adding worktree merge
  complexity that RS-005 flagged as reasoned-not-prototyped.
- **Q-REQ-C** (fan-out boundary rule): _(superseded — see RS-006 Q-REQ-A)_ Pinned
  now even though deferred (REQ-ORCH-016, priority may). Fan out along independent
  branches of the plan's chunk dependency graph; one worktree per
  concurrently-runnable chunk-group; merge sequentially to main before the
  implement-stage review. Documents a settled rule so the later feature inherits a
  design, not a [needs-spike].
- **Q-REQ-D** (resume marker): No new marker, no authoritative loop log
  (REQ-ORCH-014). Resume relies on existing phase detection + staleness; reviews
  are reproduced by re-dispatch. Preserves D5 (kickoff.md the only new artifact).

Resolved during requirements gathering for RS-004:

- **Q-REQ-A** (scope-completeness placement): Separate requirement
  (REQ-REV-008). F2's root-cause finding is cross-cutting — folding it
  into phase checklists risks the lesson being lost. Dedicated requirement
  makes the concern visible.
- **Q-REQ-B** (review persistence): Locked down as non-persistent.
  Reviews are transient working artifacts; decisions land in the artifacts
  themselves (commits, Q-IMPL entries, replan triggers). No `docs/reviews/`
  directory.
- **Q-REQ-C** (session isolation enforcement): Combined approach. Skill
  includes confirmation prompt as opening step; actual isolation is operator
  responsibility. Claude cannot reliably detect its own context
  contamination.

Resolved during requirements gathering for RS-003:

- **Q-REQ-A** (renumbering policy): Preserve original numbering during
  vocabulary rename (M1 → Chunk 1, not Chunk 0). Chunk-close doesn't care
  about N's value; renumbering breaks external references for no functional
  benefit.
- **Q-REQ-B** (version marker semantics): Marker tracks SDD process version,
  not just artifact layout. "3" means v3 conventions available.
- **Q-REQ-C** (overview.md update scope): Promoted into scope. Documentation
  and version marker must be consistent at the moment of version bump.

Resolved during requirements gathering for RS-002:

- **Q-REQ-A** (milestone scoping): Requirements are milestone-agnostic.
  Milestones are a planning concern — plans scope themselves to milestones
  via task tracing to specs and requirements. No milestone field in
  requirements.
- **Q-REQ-B** (chunk-close enforcement): Tiered. Type-name mismatches and
  missing traceability hard-block. Q-IMPL audit and test coverage are
  advisory with operator override.
- **Q-REQ-C** (Q-IMPL vs replan): Keep 3 tiers as self-contained protocol.
  Tier 3 cross-references `sdd-replan` Level 2 but doesn't collapse into it.
- **Q-REQ-D** (external review): Not formalized. Strengthen P1 chunk-close
  checklist instead. External review remains ad-hoc — its value comes from
  being outside the implementing session's context window.

## Out of Scope

- Code changes to skills (implementation phase)
- Redesigning the broader SDD methodology
- New skills not derived from RS-002, RS-003, or RS-004
- Forward planning to v4
- Cross-project review (sdd-review operates on one SDD project at a time)
- Review automation or auto-triggering
- Review of sdd-review's own output (recursive case deferred)
- Non-research orchestrator entry points / starting the loop mid-pipeline (v1)
- Nested subagent fan-out (Design A) — infeasible: a dispatched subagent has no
  subagent-dispatch tool (RS-006 Q1). Fan-out is orchestrator-owned, one level deep
- Fan-out of any stage other than implement; changes to `sdd-implement` itself
- Persisting review verdicts to disk (no docs/reviews/ — reaffirmed for the driver)
- Two literal human terminal sessions (superseded by the orchestrator + subagent model)

## Open Questions

- **Subagent nesting (fan-out):** RESOLVED by RS-006 Q1 — a dispatched subagent
  has no subagent-dispatch tool, so nesting is impossible. Fan-out is therefore
  orchestrator-owned, one level deep (Design B; REQ-ORCH-022).
- **Fan-out dispatch concurrency [needs-spike]:** whether the orchestrator can run
  multiple implement subagents truly concurrently (vs. issued-together-but-serialized)
  is unverified (REQ-ORCH-028). The fan-out design is correct either way — only
  wall-clock speedup depends on it. Resolve at spec/implementation time before
  claiming a speedup guarantee. (RS-006 Open Questions; see also RS-005 Q4)

All other Q-REQ items resolved.

## Research References

- [RS-001: SDD Artifact Structure](../research/RS-001-sdd-artifact-structure/findings.md)
- [RS-002: SDD Skill Improvements](../research/RS-002-skill-improvements/findings.md)
- [RS-003: v3 Migration Path](../research/RS-003-v3-migration/findings.md)
- [RS-004: sdd-review Skill Design](../research/RS-004-sdd-review/findings.md)
- [RS-005: sdd-orchestrate Feasibility](../research/RS-005-sdd-orchestrate-feasibility/findings.md)
- [RS-006: Subagent Nesting & Worktrees (implement-stage fan-out)](../research/RS-006-subagent-nesting-worktrees/findings.md)
- [RS-007: Multi-Workstream SDD (concurrent cycles in one repo)](../research/RS-007-multi-workstream/findings.md)

## See Also

- [Traceability Matrix](traceability.md)
