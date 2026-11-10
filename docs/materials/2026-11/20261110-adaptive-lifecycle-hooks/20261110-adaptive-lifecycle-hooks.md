---
id: MAT-adaptive-lifecycle-hooks
created_at: 2026-11-10
summary: "Retained Planning evidence for Stop, SubagentStop and SessionStart hook gates over the adaptive assignment ledger: host capabilities, devkit gaps with sized work items, gate behavior, measurement criteria and live probe procedures. The proposal was rejected without delivery."
---

# [MAT-adaptive-lifecycle-hooks] Lifecycle hook gates for adaptive delegation

## Outcome

The proposal for lifecycle hook gates over the adaptive assignment ledger was rejected after its first Planning
turn, with no delivery. The user's reason: the gates would not help much in their usage pattern.

The evidence behind that choice:

- **The Host loop already covers most of the gate's work.** In adaptive development a Host session orchestrates
  subagents and the user stays in the conversation. A worker always ends with its assignment `open`, because the
  Host records the return after the worker stops, so a `SubagentStop` gate has no status to block on. A Host `Stop`
  gate is left with one failure: the Host ending a turn with outstanding assignments it does not name, which the
  user sees at that turn end.
- **The cost falls on the host in use.** devkit registers hooks on Codex only. A Claude Code gate first needs a
  host adapter (size M with a registration the user installs, L with one devkit manages). Antigravity documents
  another contract and no subagent event.
- **No effect was measured.** No host ran a hook in Planning; the host facts come from vendor documentation.

A later proposal is warranted when the failures F1 (ending with unnamed outstanding assignments) or F2 (acting
before reading the ledger on resume) recur in real adaptive runs.

## Files

| File | Content |
| --- | --- |
| `host-capability-matrix.md` | What each host documents for the three events, classed `documented`, `code` or `probe` |
| `host-documentation-extraction.md` | The per-host extraction from vendor documentation fetched on 2026-11-10 |
| `devkit-gaps-and-work-breakdown.md` | Gaps G1 to G16, work items W1 to W10 with sizes, and delivery options (a) to (e) |
| `gate-behavior-and-measurement.md` | Ledger needs, gate decision tables, failures F1 to F3 and the measurement criteria |
| `live-probes.md` | Procedures for the host observations documentation cannot settle |

The files keep their Planning wording. Section references such as "§3.1" point within the same file or to the
assignment proposal they name. The proposal, its envelopes and its open questions remain in Git history at commit
`ad3d2ba3`.
