---
status: Approved
last_updated: 2026-07-21
requires:
  - REQ-WS-024
  - REQ-WS-025
  - REQ-WS-029
---

# Multi-Workstream Orchestration Entry & Research Lifecycle

## Context

Under v4, phase is a function of `(repo, workstream)` (`ws-layout.md`), so
`sdd-orchestrate` can no longer infer a single active cycle from the repo — it must ask
which workstream the operator is driving. Separately, the workstream lifecycle needs a
uniform entry point: RS-007 and the design fixed every workstream to begin at research,
with a fast early-exit so uniform research-entry stays cheap.

This spec covers the orchestrate workstream picker (REQ-WS-029) and the uniform
research-entry lifecycle with early-exit (REQ-WS-024, REQ-WS-025).

## Design

### Workstream Picker at Orchestration Entry (REQ-WS-029)

`sdd-orchestrate` presents a **workstream picker** at entry that lists existing
workstreams and lets the operator select one or create a new one.

For each existing workstream (one `docs/ws/<id>/` directory each), the picker shows:

| Field | Source |
|-------|--------|
| id | the `docs/ws/<id>/` directory name |
| description | from `docs/ws/<id>/kickoff.md` (per `ws-migration.md` decision, kickoff is per-workstream) |
| detected phase | phase detection for that workstream (`ws-layout.md` REQ-WS-003) |

Behavior:
- The operator selects an existing workstream **or** creates a new one.
- The **done-vs-new-cycle ambiguity is resolved per workstream**, not by appealing to a
  single operator's global intent. Selecting a workstream whose detected phase is DONE
  (verified/shipped) vs. bringing a new idea is disambiguated **within that
  workstream's context** — a DONE workstream offers "start a new cycle in this
  workstream" while a new idea creates a new workstream id.

**Why an explicit picker**: with phase now `(repo, workstream)`, the driver cannot infer
a single active cycle from the repo — several may be live at once. An explicit picker
surfaces each workstream with its phase so the operator names the one they are driving,
rather than the driver guessing. This is the orchestration-level counterpart to
threading the workstream argument through each skill's step-0.

**Interaction with solo use**: in a repo with only `default`, the picker degenerates to
that single workstream (no naming ceremony — consistent with REQ-WS-020). It is a picker
of one, not a prompt the solo operator must answer.

### Uniform Research-Entry Lifecycle (REQ-WS-024)

Every new workstream **begins at the research stage**, regardless of how much shared
corpus already exists. There is no per-workstream mid-pipeline entry variant to select
at creation.

- Creating a new workstream positions its loop at research and seeds
  `docs/ws/<id>/kickoff.md`.
- The workstream id is conventionally the branch/issue key; the branch is created/used
  per `ws-integration.md`.

**Why a single uniform entry point**: it keeps the workstream lifecycle simple and
predictable — one shape for every workstream — rather than a matrix of entry variants
the operator must choose among at creation.

### Research Early-Exit When the Shared Corpus Already Covers the Work (REQ-WS-025)

The research stage **early-exits quickly** when the shared corpus already covers the
workstream's needs, so uniform research-entry (REQ-WS-024) imposes minimal overhead when
little or no new exploration is required.

Contract:
- On entry at research for a workstream whose needs are already covered by existing
  shared requirements/specs/research, the stage records a **fast, explicit early-exit**
  (a recorded finding of "covered by shared corpus — no new spike") rather than
  performing a full spike.
- The early-exit is recorded (so the workstream's research state is auditable), then the
  loop advances to the next stage.

**Why the early-exit is `should`, not `must`**: uniform research-entry must not become
busy-work. The fast early-exit is what makes uniformity cheap. It is a `should` because a
workstream is always free to run a real spike; the early-exit is the optimization that
keeps the common "already covered" case near-zero-cost, not a hard gate.

**Interaction with staleness**: whether the shared corpus "covers" the work is a
judgment recorded at the research early-exit; ongoing staleness of the shared inputs a
workstream traces is handled separately and live (`ws-staleness.md`).

## Verification

### Automated
- Verify `sdd-orchestrate` enumerates `docs/ws/<id>/` directories and, for each, reads
  the description from `docs/ws/<id>/kickoff.md` and computes detected phase.
- Verify new-workstream creation positions the loop at research and seeds
  `docs/ws/<id>/kickoff.md`.
- Verify the research stage supports a recorded early-exit path distinct from a full
  spike.

### Manual
- With `ISSUE-42` at implement and `ISSUE-57` at plan, enter `sdd-orchestrate`; confirm
  the picker lists both with id, description, and phase, and lets the operator pick or
  create.
- Select a DONE workstream vs. bring a new idea; confirm the done-vs-new-cycle choice is
  resolved within the selected workstream's context, not globally.
- Create a workstream whose needs the shared corpus already covers; confirm research
  early-exits fast with a recorded exit rather than a full spike.
- In a `default`-only repo, confirm the picker does not impose naming ceremony.

### Acceptance Criteria
- [ ] `sdd-orchestrate` presents a workstream picker listing existing workstreams (id,
      description from kickoff.md, detected phase) with select-or-create (REQ-WS-029)
- [ ] done-vs-new-cycle ambiguity resolved per workstream, not by global operator intent
      (REQ-WS-029)
- [ ] Every new workstream begins at research; no per-workstream mid-pipeline entry
      variant (REQ-WS-024)
- [ ] Research early-exits fast with a recorded exit when the shared corpus already
      covers the work (REQ-WS-025)
- [ ] Markdown well-formed; frontmatter valid
