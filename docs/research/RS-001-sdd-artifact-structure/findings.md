---
id: RS-001
status: Complete
date: 2026-04-27
questions:
  - "Why does docs/plan.md grow unboundedly across SDD cycles?"
  - "What naming/numbering convention should research artifacts use?"
  - "How should requirements be split, categorized, and versioned?"
  - "What do RE practitioners recommend for file-based requirements systems?"
  - "How should existing SDD projects migrate to the new structure?"
budget: "1 hour"
---

# Research: SDD Artifact Structure Improvements

## Questions

1. Why does `docs/plan.md` grow on every SDD cycle, and how to fix it?
2. What structure should research artifacts use for traceability?
3. How should requirements be split, versioned, and categorized?
4. What does the requirements engineering domain recommend?
5. How do existing projects migrate?

## Findings

### Q1: Plan Bloat — Root Causes and Fix

**Answer**: Three mechanisms cause monotonic growth of `plan.md`.

**Evidence** (from current skill definitions):

1. **sdd-replan appends changelogs** (sdd-replan/SKILL.md:86-97) — every replan
   adds a `## Plan Changelog` section. These never get pruned.
2. **Removed tasks are marked, not deleted** (sdd-replan/SKILL.md:83) — `[removed:
   reason]` annotations accumulate. Same in requirements (sdd-requirements/SKILL.md:155).
3. **Completed tasks are preserved** — "preserve done tasks" rule means old milestones
   stay in the document even across full rewrites.

**Proposed fix — archive pattern**:
- Active plan stays in `docs/plan.md` — contains only current/future milestones and tasks.
- When a plan is rewritten or a cycle completes, move the old plan to
  `docs/plan-history/{date}-{reason}.md`.
- Changelogs live in the history file, not the active plan.
- Completed milestones can optionally be summarized (one line each) rather than
  preserved in full.

**Confidence**: High — the bloat sources are directly visible in the skill definitions.

### Q2: Research Folder Structure

**Answer**: Use ID-prefixed directories with a sequential counter.

**Proposed convention**:
```
docs/research/
  RS-001-{topic}/
    findings.md       # Main research document (current format)
    prototype/        # Optional: throwaway code, API responses, screenshots
  RS-002-{topic}/
    findings.md
  index.md            # Lists all research with ID, date, status, summary
```

**Naming rules**:
- `RS-NNN` prefix provides stable, referenceable IDs
- `{topic}` is kebab-case, descriptive (e.g., `RS-001-oauth2-feasibility`)
- `findings.md` is always the main file (standardized name for tooling)
- Supporting files go in the same folder (not scattered)
- `index.md` is auto-maintained — one line per research entry

**Why not date-prefixed**: Dates make paths long and don't help with references.
Research IDs (`RS-001`) are shorter and more stable for cross-referencing from
requirements and specs.

**Confidence**: High — this follows the same pattern as requirement IDs (REQ-*) and
is consistent with how the existing skills reference research.

### Q3: Requirements Splitting, Versioning, and Categories

**Answer**: Split by feature domain with a lightweight index. Use document-level
versioning tied to the SDD cycle.

**Evidence** (from domain research — see Q4):
- StrictDoc evolved away from Doorstop's one-file-per-requirement model because it
  fragments narrative coherence. Per-feature-domain files are the consensus best practice.
- AI context windows make file size a real constraint — each file should be loadable
  alongside specs and code in a single session (~300 lines max).

**Proposed structure**:
```
docs/requirements/
  index.md                    # Overview, version, cross-reference matrix
  functional/
    {domain}.md               # e.g., auth.md, billing.md, data-pipeline.md
  non-functional/
    {concern}.md              # e.g., performance.md, security.md
  integration/
    {system}.md               # e.g., stripe-api.md, oauth-provider.md
  configuration/
    {area}.md                 # e.g., env-config.md, feature-flags.md
```

**Versioning scheme**:
- `index.md` carries a `version` field in frontmatter (semver: `major.minor`).
- Major bump: requirements added/removed/fundamentally changed (triggers spec update).
- Minor bump: clarifications, rewording, priority changes (may not trigger spec update).
- Each category file has its own `last_updated` date for staleness detection.
- Research that creates/updates requirements bumps the version in `index.md`.

**Requirement ID scheme** (updated):
- `REQ-{DOMAIN}-{NNN}` instead of `REQ-{TYPE}-{NNN}`
- Examples: `REQ-AUTH-001`, `REQ-PERF-001`, `REQ-STRIPE-001`
- Domain prefix is more discoverable than type prefix — you know where to find
  `REQ-AUTH-001` (it's in `functional/auth.md` or `integration/auth.md`)
- Type (must/should/may) is conveyed by the requirement text, not the ID prefix

**Why not per-requirement files**: Too many tiny files. A requirement like "the system
must authenticate users via OAuth2" needs context — the surrounding requirements in
the same domain give it meaning. Isolated files lose that narrative.

**Why not monolithic**: Files grow unbounded. A 500-line requirements doc is hard to
navigate and consumes too much AI context when only one domain is relevant.

**Confidence**: High — validated by both domain research and practical AI workflow constraints.

### Q4: Requirements Engineering Domain Findings

**Answer**: The RE domain strongly validates splitting by domain, using explicit IDs,
and keeping files under review-friendly sizes.

**Key findings from forums and tools**:

1. **File organization consensus** (StrictDoc, Sphinx-Needs): Split by document/domain,
   not per-requirement. Doorstop's per-requirement YAML model is considered a
   predecessor pattern — fragmented and hard to review holistically.

2. **Traceability**: IEEE-standard Requirements Traceability Matrix (RTM) maps
   requirements → specs → tests → code. For file-based systems, explicit IDs with
   cross-references work better than separate spreadsheets.

3. **Versioning**: Tools that colocate requirements with code (git-based) let git
   history serve as the version log. In-document version metadata (`last_updated`,
   `status`) handles lifecycle; git handles change history.

4. **AI context constraints** (Factory.ai research, arXiv "Requirements are All You
   Need"): LLMs produce better output when given detailed, focused requirements —
   not entire project documentation. Self-contained per-domain files with ID-based
   cross-references are ideal.

5. **Bloat prevention**: "One problem per requirement" rule. Use status fields
   (Draft/Approved/Deprecated) to manage lifecycle without deleting history.
   Multiple smaller targeted documents beat one large monolith. Documents over
   ~100 pages cause stakeholder burnout — same applies to AI context.

6. **Tool landscape**: StrictDoc (active, document-centric), Sphinx-Needs (active,
   RST-based), Doorstop (barely maintained, per-requirement YAML). All three
   validate text-based, git-collocated requirements over database-backed tools.

**Confidence**: High — multiple independent sources converge on the same recommendations.

### Q5: Migration Strategy

**Answer**: A three-step migration that existing projects can run incrementally.

**Proposed migration plan**:

#### Step 1: Research migration
- Create `docs/research/index.md`
- Move each existing `docs/research/{topic}.md` into `docs/research/RS-NNN-{topic}/findings.md`
- Assign sequential RS numbers based on file date
- Update any cross-references in requirements/specs

#### Step 2: Requirements migration
- Create `docs/requirements/index.md` with version `1.0` and metadata
- Split existing `docs/requirements.md` by category:
  - Group `REQ-F-*` by domain → `docs/requirements/functional/{domain}.md`
  - Move `REQ-NF-*` → `docs/requirements/non-functional/{concern}.md`
  - Move `REQ-I-*` → `docs/requirements/integration/{system}.md`
  - Move `REQ-C-*` → `docs/requirements/configuration/{area}.md`
- Remap old IDs: `REQ-F-001` → `REQ-AUTH-001` (with a mapping table in index.md
  for one cycle, then remove)
- Delete old `docs/requirements.md`

#### Step 3: Plan archival
- Move current `docs/plan.md` to `docs/plan-history/{date}-initial.md`
- Create fresh `docs/plan.md` with only active/future tasks
- Strip changelogs and completed milestones from the active plan

**Migration skill**: Consider a `sdd-migrate` one-time skill or a migration checklist
in the updated `sdd-requirements` skill that detects the old format and offers to migrate.

**Confidence**: Medium — the structure is sound, but ID remapping could have edge cases
with in-progress implementations that reference old IDs.

## Implications for Design

### Changes needed in each SDD skill

| Skill | Change needed |
|-------|--------------|
| `sdd-research` | Write to `RS-NNN-{topic}/findings.md`, maintain `index.md` |
| `sdd-requirements` | Read/write per-domain files, maintain `index.md` with version, detect old format |
| `sdd-specs` | Read from `docs/requirements/{category}/*.md`, update `requires` refs to new IDs |
| `sdd-plan` | Archive old plan before rewrite, keep active plan lean |
| `sdd-implement` | Read requirements from new paths, reference RS-* IDs for spikes |
| `sdd-verify` | Read requirements from new paths, verify traceability across split files |
| `sdd-replan` | Write changelogs to history file, not active plan |

### Staleness detection update
- Currently compares `last_updated` across single files
- Needs to compare against the `version` in `docs/requirements/index.md` and
  `last_updated` across multiple category files
- Simplest approach: staleness checks compare against `index.md`'s `last_updated`
  (which gets bumped whenever any category file changes)

### Approaches ruled out
- **Per-requirement files** (Doorstop model) — too fragmented, loses narrative coherence
- **Database-backed tools** — incompatible with git-collocated, text-based workflow
- **In-document version suffixes** (e.g., `REQ-AUTH-001_v2`) — git handles versioning;
  in-ID versions create reference instability

## Open Questions

- Should the migration skill be a standalone `sdd-migrate` or integrated into each
  skill's phase detection?
- Should `index.md` files be auto-generated or manually curated?
- How should the plan reference requirements when IDs change during migration?
  (mapping table vs. one-time bulk rename)
- Should `docs/requirements/index.md` include a traceability matrix (requirements →
  specs → tests) or should that live in a separate artifact?
