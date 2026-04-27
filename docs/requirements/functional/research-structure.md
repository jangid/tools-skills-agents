---
domain: RS
last_updated: 2026-04-28
status: Approved
---

# Requirements: Research Structure

## Overview

How research spikes produce and organize their artifacts for traceability
and discoverability.

## Requirements

### REQ-RS-001: Research directory convention
Each research spike must produce artifacts in a directory named
`docs/research/RS-NNN-{topic}/` where `NNN` is a zero-padded sequential number
and `{topic}` is kebab-case. The main findings file must be named `findings.md`.
Supporting files (prototypes, API responses, screenshots) may live alongside it
in the same directory.
[Priority: must]

### REQ-RS-002: Research index
The `sdd-research` skill must auto-maintain a `docs/research/index.md` file.
Each entry must be one line containing: RS ID, topic, date, status, and a
one-sentence summary. The index must be updated every time a research spike is
created or its status changes.
[Priority: must]

### REQ-RS-003: Research ID assignment
The skill must determine the next RS number by scanning existing
`docs/research/RS-*` directories and incrementing. If no research exists, start
at RS-001.
[Priority: must]
