# Sources: RS-002 SDD Skill Improvements

## Primary Sources (fully read)

### SDD Skills (this repo)

| File | Lines | Relevance |
|------|-------|-----------|
| `skills/sdd-implement/SKILL.md` | 164 | Core skill under investigation — Step 4 milestone checkpoints, Step 2 task types, stuck detection |
| `skills/sdd-verify/SKILL.md` | 193 | Traceability check (Step 3b), verification report format |
| `skills/sdd-specs/SKILL.md` | 186 | Step 5 coverage check, cross-spec consistency gap |
| `skills/sdd-plan/SKILL.md` | 185 | Step 7 plan format, milestone structure, archive pattern |
| `skills/sdd-replan/SKILL.md` | 143 | Level 1-4 classification, archive format |
| `skills/sdd-requirements/SKILL.md` | 273 | Traceability file format, ID scheme, index maintenance |
| `skills/sdd-research/SKILL.md` | 179 | RS-NNN convention, research process |
| `skills/sdd-migrate/SKILL.md` | ~225 | v1→v2 migration (read for completeness, not directly relevant) |

### Rubric M1 Evidence

| File | Relevance |
|------|-----------|
| `rubric/docs/plan.md` (1212 lines) | Chunk definitions (0-6), Completed section with rework notes, Q-PLAN entries, effort actuals |
| `rubric/docs/requirements/traceability.md` (206 lines) | Traceability matrix state — `last_updated: 2026-05-24` vs Chunk 5-6 completion on 2026-05-25 |
| `rubric/docs/spec/phase0.md` lines 260-274 | Q-IMPL-001: rolling 5-day P&L approximation |
| `rubric/docs/spec/phase1.md` lines 290-327 | Q-IMPL-002 through Q-IMPL-005: breadth fallback, config param, Warning rename, DXY field |
| `rubric/docs/spec/phase2.md` line 221 | Q-IMPL-006: expiry-today EntryBlock reason |
| `rubric/docs/spec/output.md` lines 267-275 | Q-IMPL-007, Q-IMPL-008: latency measurement, permission mapping |
| `rubric/docs/spec/cli.md` line 205 | Q-IMPL-009: bootstrap JSON shape |

### This Repo's Existing Artifacts

| File | Relevance |
|------|-----------|
| `docs/research/RS-001-sdd-artifact-structure/findings.md` | Prior research — plan bloat, research structure, requirements splitting. All implemented. |
| `docs/research/index.md` | Research index with RS-001 entry |
| `docs/requirements/index.md` | v2 requirements from RS-001 cycle |
| `docs/plan.md` | Completed plan from RS-001 cycle |
| `docs/verification.md` | Passed verification from RS-001 cycle |
| `CLAUDE.md` | Project conventions, SDD phase detection table |

## Secondary Sources (sampled)

| Source | Method | Finding |
|--------|--------|---------|
| Cursor rules documentation | Prior knowledge from training data | Static linting rules, no milestone-boundary review concept |
| GitHub Copilot Workspace | Prior knowledge | Plan → implement → PR review flow; review is manual, not structured checklist |
| ADR (Architecture Decision Records) | Prior knowledge | Heavier than Q-IMPL: separate files, status lifecycle, supersedes chains. Q-IMPL is inline and ephemeral. |
| Scrum Definition of Done | Prior knowledge | Closest analogue to chunk-close checklist: gating list checked before marking work item complete |
| StrictDoc, Sphinx-Needs | Referenced from RS-001 findings | Document-centric requirements, not per-requirement files — validates SDD's approach |

## Not Consulted

- OpenAI Assistants API docs (no "stop and review" concept found in prior knowledge)
- BDD/SDD methodology academic references (vocabulary alignment not needed for this research)
- `factory.ai` research papers (already covered in RS-001)
