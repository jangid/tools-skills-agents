---
version: "3.0"
last_updated: 2026-05-25
traceability: traceability.md
---

# Requirements Index

## Summary

Requirements for SDD (Spec-Driven Development) skill improvements in the
tools-skills-agents repository. Covers two scopes:

1. **v2 artifact structure** (RS-001): Research structure, requirements
   splitting, plan management, staleness detection, migration, and per-skill
   updates for the v2 layout.
2. **Workflow improvements** (RS-002): Chunk-close review, Q-IMPL deviation
   protocol, multi-milestone plan iteration, cross-spec consistency, and
   per-skill updates for workflow changes.

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
| functional | [migration.md](functional/migration.md) | MIG | REQ-MIG-001..008 | Approved | 2026-04-28 |
| functional | [chunk-close.md](functional/chunk-close.md) | CHKC | REQ-CHKC-001..008 | Approved | 2026-05-25 |
| functional | [deviation-protocol.md](functional/deviation-protocol.md) | QIMPL | REQ-QIMPL-001..003 | Approved | 2026-05-25 |
| functional | [milestone-plans.md](functional/milestone-plans.md) | MPLAN | REQ-MPLAN-001..004 | Approved | 2026-05-25 |
| functional | [cross-spec-consistency.md](functional/cross-spec-consistency.md) | XSPEC | REQ-XSPEC-001..002 | Approved | 2026-05-25 |
| non-functional | [context-and-compatibility.md](non-functional/context-and-compatibility.md) | CTX, COMPAT | REQ-CTX-001..002, REQ-COMPAT-001 | Approved | 2026-04-28 |
| integration | [skill-updates.md](integration/skill-updates.md) | SKILL | REQ-SKILL-001..016 | Approved | 2026-05-25 |
| configuration | [version-marker.md](configuration/version-marker.md) | CFG | REQ-CFG-001 | Approved | 2026-04-28 |

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
| CTX | AI Context Budget | non-functional/context-and-compatibility.md |
| COMPAT | Git Compatibility | non-functional/context-and-compatibility.md |
| SKILL | Skill Updates | integration/skill-updates.md |
| CFG | Configuration | configuration/version-marker.md |

## Q-REQ Resolutions

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
- New skills not derived from RS-002
- v2→v3 artifact migration (changes are backward compatible with v2)
- External review as a formal skill (`sdd-review`)

## Open Questions

None — all Q-REQ items resolved.

## Research References

- [RS-001: SDD Artifact Structure](../research/RS-001-sdd-artifact-structure/findings.md)
- [RS-002: SDD Skill Improvements](../research/RS-002-skill-improvements/findings.md)

## See Also

- [Traceability Matrix](traceability.md)
