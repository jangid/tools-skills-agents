---
domain: CTX,COMPAT
last_updated: 2026-05-25
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

### REQ-COMPAT-002: v3 backward compatibility
v2 projects that have not run the v2→v3 migration must continue to work with
v3-era skills. All v3 behavioral additions (chunk-close review, Q-IMPL protocol,
cross-spec consistency, per-milestone plans) must degrade gracefully: the
chunk-close mechanism is inactive when plan headers don't use `### Chunk N:`
format; per-milestone logic activates only when per-milestone files exist;
Q-IMPL sections accumulate on demand. Migration must be opt-in.
[Priority: must]
