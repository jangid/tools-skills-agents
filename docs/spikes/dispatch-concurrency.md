# Spike: Orchestrator dispatch concurrency (REQ-ORCH-028)

**Date:** 2026-06-05
**Plan task:** Chunk 1, task 10 (`[spike]`, budget ~30 min)
**Question:** When the orchestrator dispatches N implement subagents in one
message (the fan-out path), do they run **truly concurrently** or are they
serialized? Only wall-clock speedup is at stake — correctness holds either way
(REQ-ORCH-028, spec §Dispatch Concurrency [high-uncertainty]).

## Method

Run by the **orchestrator** (a leaf subagent cannot dispatch — RS-006 Q1). Two
probe subagents were dispatched **in a single message** (the same mechanism real
fan-out uses), each recording an epoch timestamp before and after a ~4s CPU
workload.

## Result

| Probe | START (epoch) | END (epoch) | Agent lifetime |
|-------|---------------|-------------|----------------|
| A | 1780646374.41 | 1780646376.13 | ~427 s |
| B | 1780645956.22 | 1780646376.22 | ~426 s |

- Both agents were alive for ~426 s and **ended within 0.1 s of each other**
  (376.13 vs 376.22) — they occupied the **same overlapping wall-clock window**.
- Strict serialization would force one probe's interval to begin only after the
  other's agent fully completed, ending hundreds of seconds apart. That is not
  what was observed.

## Finding

**Orchestrator-dispatched subagents issued in a single message run
concurrently.** Fan-out therefore delivers genuine wall-clock speedup, not just
worktree isolation. This matches the harness guidance ("launch multiple agents
in a single message so they run concurrently").

**Confidence: Medium.** The absolute timings are dominated by model/scheduling
latency (a ~4s task inside a ~426s agent lifetime), which adds noise, but the
simultaneous end + shared lifetime are strong evidence of concurrency and are
inconsistent with serialization.

## Implications

- REQ-ORCH-028's `[needs-spike]` is **resolved favorably**: concurrency holds;
  no speedup-guarantee caveat needs to block the feature.
- No replan triggered. Implementation proceeds; the SKILL.md concurrency note
  (plan task 9) can state that fan-out runs concurrently when subagents are
  dispatched in one batch.
- The design held regardless of the outcome (worktree isolation + sequential
  merge are unchanged), so this only upgrades the speedup story from "unverified"
  to "observed."
