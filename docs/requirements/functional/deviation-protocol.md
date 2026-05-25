---
domain: QIMPL
last_updated: 2026-05-25
status: Draft
---

# Requirements: Q-IMPL Deviation Protocol

## Overview

Protocol for handling implementation deviations from spec during
`sdd-implement`. Provides a three-tier classification: silent implementation
choices, documented spec ambiguities (Q-IMPL entries), and escalated
contract changes. Derived from RS-002 finding P2. (see RS-002)

## Requirements

### REQ-QIMPL-001: Three-tier deviation classification
`sdd-implement` must document a three-tier protocol for implementation
deviations from spec:
- **Tier 1** (implementation choice): Internal decisions (helper naming,
  data structure selection) that don't affect the spec's public contract.
  No documentation required.
- **Tier 2** (spec ambiguity): The spec didn't anticipate the situation.
  Add a Q-IMPL entry to the relevant spec's "Implementation Questions"
  section. Continue implementing.
- **Tier 3** (contract change): The spec's public interface must change.
  Stop implementation, escalate to the operator. This typically triggers
  `sdd-replan` at Level 2 (spec gap), but the Q-IMPL protocol and replan
  vocabulary are complementary — Q-IMPL classifies the deviation, replan
  handles the response.
[Priority: must]

### REQ-QIMPL-002: Q-IMPL entry format
Q-IMPL entries must use global sequential numbering (`Q-IMPL-001`,
`Q-IMPL-002`, ... across all specs in the project) and be placed in an
`## Implementation Questions` section at the bottom of the relevant spec
file. Each entry must include: the question ID, a description of the
deviation, and the rationale for the implementation choice. Numbering is
append-only; retired entries remain in their spec with a
`[superseded by Q-IMPL-NNN]` status note.
[Priority: must]

### REQ-QIMPL-003: Q-IMPL discovery on task start
When starting an implementation task, the implementer should read the
relevant spec's existing Q-IMPL entries to understand how prior ambiguities
were resolved. This is advisory — it informs implementation decisions but
does not block.
[Priority: should]
