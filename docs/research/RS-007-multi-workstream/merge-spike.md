# RS-007 Q1 — Git merge spike (raw commands + observed output)

Ran in an **isolated throwaway git repo** under `$TMPDIR/rs007-merge-spike`
(identical 3-way-merge semantics to the real repo, fully isolated from
`feat/multi-workstream-sdd`). Repo deleted after the spike; no branches were
created in the real repo. `merge.conflictstyle = merge`, git default merge
strategy (`ort`).

Evidence detail: S1 (the CONFLICT case) and the three CLEAN cases that justify
the recommendations — S3 (sorted-into-distinct-regions), S6 (per-ws delimited
section), S8 (separate per-ws files) — are shown below with the literal command
sequence and observed merge output. S2, S4, S5, S7 are CONFLICT cases that
follow deductively from the same governing rule proven by S1 (position, not row
content, determines the conflict) and are summarized in the results table
rather than pasted verbatim.

## Method

For each scenario: branch A and branch B off a common base, each applies one
distinct edit to the SAME shared markdown table file, commit, then
`git merge A` into B and observe whether it auto-merges or conflicts.

## Scenarios and results

| # | Structure / edit pattern | Result |
|---|--------------------------|--------|
| S1 | Table ends at EOF; both branches **append a distinct row at the end** | **CONFLICT** (1 hunk) |
| S2 | Table has trailing prose; both **insert a distinct row at the same point** (after the last data row) | **CONFLICT** (1 hunk) |
| S3 | One-row-per-line, **sorted-by-ID insertion at DISTINCT interior positions** (new rows sort to different regions, ≥1 unchanged line between them) | **CLEAN** |
| S4 | Sorted insertion where both new IDs **sort to the same/adjacent position** (`REQ-ABC-001` vs `REQ-ABD-001`) | **CONFLICT** (1 hunk) |
| S5 | Trailing sentinel comment line; both **insert immediately before the sentinel** (same insertion point) | **CONFLICT** (1 hunk) |
| S6 | Shared file, **each workstream owns a delimited section** (`<!-- ws:ISSUE-42 -->…<!-- /ws:ISSUE-42 -->`); each edits WITHIN its own section (separated regions) | **CLEAN** |
| S7 | Two **new** workstreams each **append a new section block at EOF** concurrently | **CONFLICT** (1 hunk) |
| S8 | **Separate per-workstream files** (each ws writes its own new file; shared file untouched) | **CLEAN** |

## The actual S1 conflict (proof)

Base table (ends at EOF):

```
| Requirement | Spec | Verified |
|-------------|------|----------|
| REQ-RS-001 | research.md | pass |
| REQ-RS-002 | research.md | pass |
```

Branch A appended `| REQ-AUTH-100 | auth.md | pass |`; branch B appended
`| REQ-PAY-200 | pay.md | pass |`. `git merge` produced:

```
| REQ-RS-001 | research.md | pass |
| REQ-RS-002 | research.md | pass |
<<<<<<< HEAD
| REQ-PAY-200 | pay.md | pass |
=======
| REQ-AUTH-100 | auth.md | pass |
>>>>>>> A_x
```

## The clean scenarios (proof)

Each was run with the literal sequence below (`git init`, `git config
user.*`, `merge.conflictstyle=merge` set once in the repo). Two branches diverge
from a common base, each makes one edit, then `git merge --no-edit` the second
into the first.

### S3 — sorted-by-ID insertion into DISTINCT regions → CLEAN

Base table (one row per line, ID-sorted):

```
| Requirement | Spec | Verified |
|-------------|------|----------|
| REQ-AAA-001 | a.md | pass |
| REQ-MMM-001 | m.md | pass |
| REQ-ZZZ-001 | z.md | pass |
```

Branch A inserts `| REQ-AUTH-001 | auth.md | pass |` into its sorted slot
(between AAA and MMM); branch B inserts `| REQ-PAY-001 | pay.md | pass |` into
its sorted slot (between MMM and ZZZ). Commands and output:

```
$ git checkout -b s3-A base && <edit: insert AUTH row in sorted region> && git commit -am "A"
$ git checkout -b s3-B base && <edit: insert PAY row in sorted region>  && git commit -am "B"
$ git checkout s3-A
$ git merge --no-edit s3-B
Auto-merging table.md
Merge made by the 'ort' strategy.
 table.md | 1 +
 1 file changed, 1 insertion(+)
```

Merged result (both rows land in their own sorted regions, no conflict):

```
| Requirement | Spec | Verified |
|-------------|------|----------|
| REQ-AAA-001 | a.md | pass |
| REQ-AUTH-001 | auth.md | pass |
| REQ-MMM-001 | m.md | pass |
| REQ-PAY-001 | pay.md | pass |
| REQ-ZZZ-001 | z.md | pass |
```

### S6 — each workstream owns a delimited section → CLEAN

Base file seeds one empty delimited block per workstream:

```
# Traceability

<!-- ws:ISSUE-42 -->
<!-- /ws:ISSUE-42 -->

<!-- ws:ISSUE-99 -->
<!-- /ws:ISSUE-99 -->
```

Branch A appends `| REQ-AUTH-42-001 | auth.md | pass |` inside `ws:ISSUE-42`;
branch B appends `| REQ-PAY-99-001 | pay.md | pass |` inside `ws:ISSUE-99`.
Output:

```
$ git checkout s6-A
$ git merge --no-edit s6-B
Auto-merging trace.md
Merge made by the 'ort' strategy.
 trace.md | 1 +
 1 file changed, 1 insertion(+)
```

Merged result (each edit stays inside its own separated region):

```
# Traceability

<!-- ws:ISSUE-42 -->
| REQ-AUTH-42-001 | auth.md | pass |
<!-- /ws:ISSUE-42 -->

<!-- ws:ISSUE-99 -->
| REQ-PAY-99-001 | pay.md | pass |
<!-- /ws:ISSUE-99 -->
```

### S8 — separate per-workstream files → CLEAN

Shared `trace.md` is untouched; each workstream creates its own new file.
Branch A adds `ws-ISSUE-42-traceability.md`, branch B adds
`ws-ISSUE-99-traceability.md`. Output:

```
$ git checkout s8-A
$ git merge --no-edit s8-B
Merge made by the 'ort' strategy.
 ws-ISSUE-99-traceability.md | 1 +
 1 file changed, 1 insertion(+)
 create mode 100644 ws-ISSUE-99-traceability.md
```

After merge both per-ws files are present and the shared `trace.md` is
byte-unchanged from base — the two branches never touch the same lines.

## Governing rule (derived from the seven scenarios)

Git's 3-way merge conflicts **whenever both branches edit the same location** —
and "append to the end of a file/table" is the same location (the EOF boundary)
for both branches. It auto-merges cleanly **only when the two insertions land at
distinct positions separated by at least one unchanged line**. Content
distinctness is irrelevant; position is everything.

Consequences:
- Plain append to a shared table (S1, S2, S5, S7) **always conflicts** under
  concurrency. A trailing sentinel does NOT help when both target the same
  pre-sentinel point (S5).
- Sorted-by-ID insertion is clean **iff** the new IDs sort into different
  regions (S3); two rows that sort adjacent still conflict (S4).
- Per-workstream **owned regions** (S6) and **separate per-ws files** (S8) are
  robustly clean because the two branches never touch the same lines.
