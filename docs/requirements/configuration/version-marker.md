---
domain: CFG
last_updated: 2026-05-25
status: Approved
---

# Requirements: Version Marker

## Overview

How the SDD process version is tracked on disk. The version marker indicates
which SDD conventions and mechanisms are available in the project.

## Requirements

### REQ-CFG-001: Version marker location and semantics
The SDD process version must be stored in `docs/.sdd-version` as a plain text
file containing a single integer. Valid values: `2` (v2 artifact layout), `3`
(v2 layout plus v3 process conventions). The marker tracks SDD process version
— not just artifact layout — so operators can determine which mechanisms (e.g.,
chunk-close, Q-IMPL protocol) are available. All skills must read this file to
determine which conventions to apply.
[Priority: must] [Updated: 2026-05-25]
