---
domain: XSPEC
last_updated: 2026-05-25
status: Draft
---

# Requirements: Cross-Spec Consistency

## Overview

Lightweight validation that types referenced across multiple specs are
consistent — catching the failure mode where one spec references a type
defined in another spec, but the type definition doesn't include the
expected fields. Derived from RS-002 finding P6. (see RS-002)

## Requirements

### REQ-XSPEC-001: Cross-spec reading pass
After all specs are written and before the final coverage check (Step 5),
`sdd-specs` must perform a reading pass that identifies cross-spec type
references — types mentioned in one spec that are defined in another spec.
[Priority: must]

### REQ-XSPEC-002: Reference validation
For each cross-spec type reference identified in REQ-XSPEC-001, the reading
pass must verify that the referenced type exists in the target spec with the
expected fields. Mismatches (missing type, missing field, field name
discrepancy) must be flagged to the operator before specs are marked
Approved. Flag only — no auto-fix. Cross-spec mismatches typically have
multiple valid resolutions and require operator judgment.
[Priority: must]
