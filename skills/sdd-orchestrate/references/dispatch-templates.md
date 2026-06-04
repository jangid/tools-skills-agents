# Dispatch Prompt Templates

Copy-ready templates the `sdd-orchestrate` driver fills in at dispatch time.
`{...}` are orchestrator-filled slots. The contract these templates satisfy is
defined in `../SKILL.md` (§Pipeline subagent dispatch, §Review subagent
dispatch). Both were validated by live subagent dispatches in RS-005.

---

## PIPELINE subagent template

Front-loads every decision so the non-interactive subagent never needs to ask
the operator a question. The `{on_fix_only}` block is included only when
re-dispatching after a loop-back-to-fix gate.

```
You are a non-interactive pipeline subagent executing ONE stage of an SDD
pipeline. Do NOT ask questions — you have no user to answer them.

Working directory (absolute): {repo_root}
Stage skill to invoke: sdd-{stage}
Assigned IDs (use these verbatim, do not scan/guess): {ids_if_any}
Success criterion: {success_criterion}
Budget: {budget}
Deliverable contract (exact files + frontmatter to produce): {deliverable_contract}

Inputs you have been given:
  - Kickoff / upstream artifact path(s): {input_paths}
  {on_fix_only}- Review findings to address (paths-only; no reviewer reasoning
    beyond the findings themselves): {review_findings}

Precedence: where the sdd-{stage} skill tells you to scan for the next ID,
update an index, or choose an output path, THESE dispatch instructions override
it — use the assigned IDs, the deliverable contract's paths, and (if told) do not
touch index files. The skill's other guidance still applies.

Task:
  1. Invoke the sdd-{stage} skill via the Skill tool and follow it.
  2. Where the skill instructs you to "ask the user", instead use the inputs
     above. If a required decision is genuinely missing, record it under an
     "Open Questions" / "Assumptions" section in the artifact and proceed with
     a stated default — NEVER invent requirements or fabricate operator consent.
  3. Write the stage's SDD artifact(s) to disk per the deliverable contract.
  4. Return: the list of files written + a one-paragraph summary of what the
     stage produced. If a write is blocked, return the file's full content with
     the target path labeled so the orchestrator can persist it.

Do not perform any stage other than sdd-{stage}.
```

### Slot contract (pipeline)
- `{repo_root}` — absolute path; pins cwd so phase detection reads the right tree.
- `{stage}` — one of research, requirements, specs, plan, implement, verify.
- `{ids_if_any}` — IDs the orchestrator assigned centrally (e.g. `RS-006`). Never
  let the subagent pick its own ID.
- `{success_criterion}` — how the stage knows it is done (mandated by REQ-ORCH-007).
- `{budget}` — explicit scope/time bound for the stage (mandated by REQ-ORCH-007).
- `{deliverable_contract}` — the exact files to write and their frontmatter
  (mandated by REQ-ORCH-007). Also pins output paths, which the Precedence note
  uses to override the skill's default path/index behavior.
- `{input_paths}` — kickoff path (research stage) or prior SDD artifact paths.
- `{on_fix_only}` / `{review_findings}` — present only on a fix re-dispatch;
  carries the review findings + artifact paths, nothing of the reviewer's
  chain-of-thought.

**Disk-write reality (validated live):** a dispatched subagent's write can be
blocked by harness policy (e.g. writing a report-style file to a non-conventional
path). The labeled-content fallback in step 4 is therefore load-bearing, not
decorative — the orchestrator MUST be ready to persist returned content itself
when a subagent reports a blocked write.

---

## REVIEW subagent template (isolation-critical)

Carries only artifact paths + the repo root + "invoke sdd-review". Nothing else.
This is the dispatch-time enforcement of `sdd-review` Step 2's prohibited-inputs
list.

```
You are an external reviewer for an SDD artifact. Review the deliverable below.

Repository root: {repo_root}
Deliverable to review: {deliverable_path}
{upstream_path_line}      # e.g. "Upstream artifact: docs/requirements/index.md"
                          # OMIT this line for the research stage — sdd-review
                          # prohibits kickoff prompts as input; the reviewer
                          # reads the research questions from the deliverable's
                          # own frontmatter.

Invoke the sdd-review skill and follow it to produce a tiered verdict on the
deliverable. Obtain any context you need by reading files from the repository
yourself — none is provided in this prompt by design.
```

### Slot contract (review)
- `{repo_root}` — absolute repository path.
- `{deliverable_path}` — the artifact(s) the pipeline just wrote.
- `{upstream_path_line}` — the upstream SDD artifact for the stage. **Omit
  entirely for the research stage.** For later stages supply requirements (for a
  specs review), specs (for a plan review), etc.

### What the review template MUST NOT contain
(verified absent in the RS-005 dispatch; mirrors `sdd-review` Step 2)
- the orchestrator's conversation history or chain-of-thought
- the pipeline subagent's reasoning / "here's what I was thinking" framing
- a kickoff prompt or internal planning notes
- draft / intermediate versions of the artifact
- the author's out-of-band rationale for design choices

Isolation holds **by construction**: a freshly dispatched subagent has no shared
context window to leak through.
