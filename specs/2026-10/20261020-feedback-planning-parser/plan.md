---
id: PLAN-feedback-planning-parser
spec: SPEC-feedback-planning-parser
---

# Technical Plan: `SPEC-feedback-planning-parser`

## Constitution and invariant review

None. Preserve worker commit-only authority and `CAP-DLV-delivery-workflows`; preserve reconciliation grammar from
`CAP-TRACE-code-entrypoints`. No dependencies, schema changes or ADR required.

## Components and interface

- Planning reference: require context refresh through the Host when newer IDs or CLI features are necessary.
- Planning worker contract and delegation payload: assigned-worktree instructions and CLI; explicit ignored probe
  path inside existing allowed scope, cleanup and evidence retention. Sandbox permission is separate.
- entrypoints/bundle.py: rename _targets to parse_targets(text: str, relative: str) -> tuple[Target, ...], document
  the existing text-only interface. Update disk and committed consumers without changing its body.
- Corresponding capability statements and four linked open source feedback dispositions.

## Verification

Review guidance against the three Planning scenarios, including unavailable ignored probe space and stale CLI.
Direct parser tests cover ordered/default targets and malformed input with diagnostic paths; existing entrypoint
and worker tests cover callers. Run just lint-check spec, just check spec, just test-affected --base main and
cumulative governance rules. Independent medium code review and reconciliation verification precede completion.
