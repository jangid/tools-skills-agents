---
status: Draft
last_updated: 2026-05-25
requires:
  - REQ-QIMPL-001
  - REQ-QIMPL-002
  - REQ-QIMPL-003
---

# Q-IMPL Deviation Protocol

## Context

During implementation, developers encounter situations the spec didn't
anticipate. In the rubric M1 cycle, ~9 Q-IMPL entries were created across
specs — each capturing a real decision the spec hadn't addressed. Without a
protocol, these become silent interpretations that downstream chunks inherit
without awareness.

The current `sdd-implement` skill says "trigger replan when assumptions
break" — that's the heavy-weight escape valve. In practice, most deviations
are lighter than a replan: a spec ambiguity that needs documenting, or an
internal implementation choice that needs no documentation at all.

This spec defines a three-tier classification that matches deviation severity
to response effort.

## Design

### Tier Classification

#### Tier 1: Implementation Choice

Internal decisions that don't affect the spec's public contract.

**Examples**: helper function naming, internal data structure selection,
import organization, private method decomposition.

**Protocol**: No documentation required. Commit normally.

**Why no protocol**: These decisions are routine engineering judgment.
Documenting them would create noise that obscures real deviations.

#### Tier 2: Spec Ambiguity

The spec didn't anticipate the situation. The implementation must make a
decision, but the decision doesn't change the spec's public interface.

**Examples**: spec says "match positions" but doesn't specify the matching
key; spec defines a type but doesn't cover an edge case in its behavior;
spec is silent on error handling for a specific scenario.

**Protocol**:
1. Add a Q-IMPL entry to the relevant spec's `## Implementation Questions`
   section (format below)
2. Continue implementing with the chosen approach
3. The Q-IMPL entry captures the decision for future reference and chunk
   close review

**Why continue rather than stop**: Tier 2 deviations are ambiguities, not
contradictions. The implementer has enough context to make a reasonable
choice. Stopping for every ambiguity would make implementation sessions
unworkably slow.

#### Tier 3: Contract Change

The spec's public interface must change — a type needs renaming, a field
needs adding, an API contract needs revision.

**Examples**: spec defines `BreadthAssessment` but `BreadthAnalysis` is
more accurate; spec omits a field that downstream consumers require; spec's
algorithm produces incorrect results for a discovered edge case.

**Protocol**:
1. Stop implementation of the current task
2. Escalate to the operator
3. The operator decides: edit the spec via `sdd-specs` and get re-approved,
   or trigger `sdd-replan` at Level 2 (spec gap)

**Relationship to replan**: Q-IMPL Tier 3 is a structured trigger for
`sdd-replan` Level 2 ("spec gap"). The Q-IMPL protocol classifies the
deviation; replan handles the response. They are complementary vocabularies,
not duplicates.

**Why stop**: Contract changes ripple across chunks. A renamed type affects
every file that references it. Continuing with a contract change and
documenting it after the fact creates exactly the drift that chunk-close
review (see chunk-close-review.md) is designed to catch — but catching it
earlier is cheaper.

### Q-IMPL Entry Format

Entries live in an `## Implementation Questions` section at the bottom of
the relevant spec file:

```markdown
## Implementation Questions

### Q-IMPL-001: Position matching key
**Tier**: 2 (spec ambiguity)
**Spec reference**: §Reconciliation Engine, "match positions"
**Decision**: Match by `contract_id` rather than `symbol` because
contract_id is unique per instrument while symbol can be shared across
exchanges.
**Impact**: Downstream consumers must include contract_id in position
snapshots.

### Q-IMPL-002: VIX data source fallback
**Tier**: 2 (spec ambiguity)
**Decision**: Return None when VIX data is unavailable rather than raising.
**Rationale**: Callers already handle None for optional indicators.
```

**Required fields**: question ID, tier, decision, and rationale (or impact
for tier 2+ entries).

### Numbering

- Global sequential: `Q-IMPL-001`, `Q-IMPL-002`, ... across all specs in
  the project
- The implementer scans all spec files' `## Implementation Questions`
  sections to find the highest existing number and increments
- Numbering is append-only: retired entries remain in their spec with a
  `[superseded by Q-IMPL-NNN]` status note rather than being deleted or
  renumbered
- No separate index file — entries live in the specs they relate to

**Why global numbering**: A project-wide sequence makes Q-IMPL IDs
unambiguous in conversation ("Q-IMPL-007" refers to exactly one entry).
Per-spec numbering would require qualifying with the spec name.

**Why no index file**: The rubric M1 cycle produced ~9 entries across 4
specs. At this volume, an index adds maintenance overhead without
discoverability benefit. The chunk close Q-IMPL audit (Check 4 in
chunk-close-review.md) already scans all specs.

### Discovery on Task Start

When starting an implementation task, `sdd-implement` should instruct the
implementer to read the relevant spec's existing Q-IMPL entries. This
provides context on how prior ambiguities were resolved and prevents
contradictory decisions.

This is advisory — it informs implementation decisions but does not block
task start. A task may reference a spec with no Q-IMPL entries, and that's
normal.

### Interaction with Chunk Close Review

The Q-IMPL audit (Check 4 in chunk-close-review.md) runs at chunk
boundaries. It verifies that implementation decisions deviating from spec
have corresponding Q-IMPL entries. Undocumented deviations are flagged as
advisory findings — the operator may override if the deviation is trivially
obvious.

This creates a safety net: even if the implementer forgets to add a Q-IMPL
entry during implementation, the chunk close catches it.

## Verification

### Automated
- Verify `sdd-implement` SKILL.md documents the three-tier protocol
- Verify tier descriptions match: Tier 1 (no protocol), Tier 2 (Q-IMPL
  entry, continue), Tier 3 (stop, escalate)
- Verify Q-IMPL entry format includes ID, tier, decision, rationale fields
- Verify global sequential numbering is documented

### Manual
- Run `sdd-implement` against a spec with ambiguities
- Create a Tier 2 Q-IMPL entry; verify format compliance
- Trigger a Tier 3 deviation; verify implementation stops and escalates
- At chunk close, verify Q-IMPL audit detects undocumented deviations

### Acceptance Criteria
- [ ] Three-tier protocol documented in sdd-implement (REQ-QIMPL-001)
- [ ] Tier 1 requires no documentation (REQ-QIMPL-001)
- [ ] Tier 2 adds Q-IMPL entry and continues (REQ-QIMPL-001)
- [ ] Tier 3 stops and escalates; references sdd-replan Level 2 (REQ-QIMPL-001)
- [ ] Q-IMPL entries use global sequential numbering (REQ-QIMPL-002)
- [ ] Entries placed in spec's Implementation Questions section (REQ-QIMPL-002)
- [ ] Each entry includes ID, tier, decision, rationale (REQ-QIMPL-002)
- [ ] Numbering is append-only with superseded notes (REQ-QIMPL-002)
- [ ] Task start includes advisory read of existing Q-IMPL entries (REQ-QIMPL-003)
