---
reconcile_id: REC-handoff-rewrite-overlap-scheduling
status: resolved
targets:
  - file: docs/capabilities/harness/CAP-HARN-agent-guidance.md
    resolution: modified
formal_docs:
  design: "none: a Host reading rule for existing scope evidence; no component, mechanism or interface shape changes"
  domain: "none: horizon, source and observed keep their meaning; no term or identity is introduced"
  operations: "none: no command, configuration, runbook or symptom changes"
---

# Reconciliation: `SPEC-handoff-rewrite-overlap-scheduling`

## Contract comparison

- `CAP-HARN-agent-guidance` "Host scope observation" (AC-01, AC-02, AC-03): now states that `current` overlap on a
  path with `observed`-only evidence for both units, changed by each unit's handoff commit and by no later commit of
  that unit, is integration-conflict evidence resolved in overlap order and named in no payload as a write target.
  This matches the scheduling bullet of the spec-orchestrate skill source.
- `CAP-COLL-work-scope-registry`: unaffected; `scope collect` code and output are unchanged (non-goal).
- `CAP-DLV-proposal-lifecycle` §4.8 (AC-04): unaffected; it already describes the widened
  `SPEC_PROPOSAL_REFS_REWRITTEN` trigger, which the `ProposalReferencesRewrittenNotice` docstring now matches.
- Use cases, architecture and glossary: unaffected; `UC-run-parallel-work-safely` already has the Host use
  overlaps, horizon and provenance.

## Source feedback

- `FB-handoff-reference-overlap-serializes-workers`: resolved; resolution appended to its file.
- `FB-refs-rewritten-notice-docstring`: resolved by the Host-authorized extension; disposition appended to its file.
