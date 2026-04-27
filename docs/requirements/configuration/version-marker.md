---
domain: CFG
last_updated: 2026-04-28
status: Approved
---

# Requirements: Version Marker

## Overview

How the SDD artifact structure version is tracked on disk.

## Requirements

### REQ-CFG-001: Version marker location
The SDD artifact structure version must be stored in `docs/.sdd-version` as a
plain text file containing the version number (e.g., `2`). All skills may read
this to determine which artifact layout to expect.
[Priority: must]
