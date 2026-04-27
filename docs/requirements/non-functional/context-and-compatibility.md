---
domain: CTX,COMPAT
last_updated: 2026-04-28
status: Approved
---

# Requirements: Context Budget and Compatibility

## Overview

Constraints on artifact file sizes for AI context windows and format
requirements for git-friendly workflows.

## Requirements

### REQ-CTX-001: AI context budget
No single artifact file consumed by an SDD skill during a phase should exceed
300 lines. Index files and traceability matrices are exempt from this limit but
should be kept as concise as possible.
[Priority: must]

### REQ-CTX-002: Self-contained files
Each requirements category file must be readable in isolation — it must not
require reading other category files to understand its requirements. Cross-domain
dependencies must use explicit requirement IDs, not prose references.
[Priority: must]

### REQ-COMPAT-001: Git-friendly format
All artifacts must be plain Markdown with YAML frontmatter. No binary files, no
tool-specific formats. Diffs must be human-readable.
[Priority: must]
