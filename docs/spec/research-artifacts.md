---
status: Approved
last_updated: 2026-05-25
requires:
  - REQ-RS-001
  - REQ-RS-002
  - REQ-RS-003
  - REQ-SKILL-002
---

# Research Artifacts

## Context

In v1, research spikes produce flat files at `docs/research/{topic}.md`. There
is no index, no numbering, no way to cross-reference a specific spike from
requirements or specs. Supporting files (prototypes, API responses) have no
designated location.

v2 introduces ID-prefixed directories, a standardized main file name, and an
auto-maintained index for discoverability and traceability.

## Design

### Directory Convention

Each research spike lives in its own directory:

```
docs/research/RS-NNN-{topic}/
  findings.md       # Main research document (required)
  prototype/        # Optional: throwaway code
  responses/        # Optional: API response samples, screenshots
  notes.md          # Optional: raw notes, scratchpad
```

- `NNN` is a zero-padded 3-digit sequential number (e.g., `001`, `002`).
- `{topic}` is kebab-case, descriptive of the research question (e.g.,
  `oauth2-feasibility`, `plan-bloat-analysis`).
- `findings.md` is always the main document — the skill writes here, other
  skills reference here.

**Why directories instead of flat files**: Research spikes often produce
supporting artifacts (prototype code, API response dumps, screenshots). A
directory provides a natural home for these without cluttering the research
root.

**Why `findings.md` instead of `{topic}.md`**: A standardized name means any
tool or skill can find the main document without parsing the directory name.

### findings.md Format

The format is unchanged from v1, with one addition — an `id` field in
frontmatter:

```markdown
---
id: RS-001
status: Complete
date: YYYY-MM-DD
questions:
  - "The specific question we were answering"
budget: "What was allocated"
---

# Research: [Topic]
...
```

The `id` field must match the directory prefix. This allows validation and
makes the ID visible when reading the file without inspecting the path.

### Research Index

`docs/research/index.md` is auto-maintained by the `sdd-research` skill:

```markdown
---
last_updated: YYYY-MM-DD
---

# Research Index

| ID | Topic | Date | Status | Summary |
|----|-------|------|--------|---------|
| RS-001 | OAuth2 feasibility | 2026-03-15 | Complete | OAuth2 refresh tokens supported; proceed with auth design |
| RS-002 | Plan bloat analysis | 2026-04-27 | Complete | Three bloat sources identified; archive pattern proposed |
```

- One row per research spike.
- Updated every time a spike is created or its status changes.
- Sorted by ID (chronological by creation).

**Why a markdown table instead of a list**: Tables are scannable and
machine-parseable. Skills can grep for a specific RS ID and get all metadata
in one line.

### ID Assignment

When creating a new research spike, the skill must:

1. Scan `docs/research/` for directories matching `RS-NNN-*`
2. Extract the highest `NNN` value
3. Increment by 1, zero-pad to 3 digits
4. If no `RS-*` directories exist, start at `001`

**Edge case**: If a directory exists but `findings.md` is missing or has
`status: Abandoned`, it still counts — the number is consumed. IDs are never
reused.

### Cross-Referencing

Other artifacts reference research by ID:
- Requirements: `research_refs: [RS-001, RS-002]` in frontmatter, or inline
  `(see RS-001)` in prose
- Specs: `(see RS-001 §Findings)` in design rationale
- Plan: spike tasks reference `RS-NNN` when extending prior research

## Verification

### Automated
- Validate that every `RS-NNN-*` directory contains a `findings.md`
- Validate that `findings.md` frontmatter contains `id` matching directory prefix
- Validate that `index.md` has an entry for every `RS-NNN-*` directory
- Validate no duplicate RS numbers exist

### Acceptance Criteria
- [ ] Research spikes create directories at `docs/research/RS-NNN-{topic}/` (REQ-RS-001)
- [ ] Main findings file is always named `findings.md` (REQ-RS-001)
- [ ] `docs/research/index.md` is auto-maintained with one row per spike (REQ-RS-002)
- [ ] Index is updated on spike creation and status change (REQ-RS-002)
- [ ] RS numbers are assigned by scanning existing directories (REQ-RS-003)
- [ ] Numbering starts at RS-001 when no research exists (REQ-RS-003)
- [ ] `sdd-research` skill writes to the new paths (REQ-SKILL-002)
