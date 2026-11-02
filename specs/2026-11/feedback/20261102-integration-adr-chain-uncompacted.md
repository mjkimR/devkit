---
id: FB-integration-adr-chain-uncompacted
title: The integration ADR supersession chain was left out of compaction
scope: repo
kind: suggestion
category: other
target: docs/decisions/
origin: agent
severity: noise
recurring: false
status: open
created_at: 2026-11-02
---

# [FB-integration-adr-chain-uncompacted] The integration ADR supersession chain was left out of compaction

Category note: decision ledger size.

## 2. Suggestion / Change Request (suggestion, change-request)

- **Current Procedure**: The 2026-11-02 `adr-compaction` run compacted 77 ADRs into 20 replacements and left one
  supersession component of 13 ADRs untouched. Supersession closure forbids splitting it, and as one replacement it
  would be a mega-ADR with about 30 aliases and five unrelated clause families. The 13 ADRs:
  `ADR-configuration-language-and-rendering`, `ADR-delivery-decision-boundaries`,
  `ADR-local-and-pull-request-integration`, `ADR-orchestration-workers`, `ADR-host-cli-lifecycle-authority`,
  `ADR-subagent-level-projection`, `ADR-five-subagent-levels`, `ADR-lean-subagent-level`,
  `ADR-reusable-lifecycle-resource-manager`, `ADR-drop-the-base-checkout-equality-from-worker-validation`,
  `ADR-moved-target-merge`, `ADR-generated-conflicts-in-prepared-merge`,
  `ADR-retire-stale-integration-approval-clauses`.
- **Proposed Procedure**: Untangle the chain first. Where a later ADR replaced a whole topic, state the replacement
  per topic so the component splits into coherent groups (gates and authority, merge routes, workers and subagent
  levels, configuration and rendering). Then compact each group. Fold in `FB-native-approval-adrs-without-pointers`.
- **Expected Benefit**: The ledger shrinks from 47 to about 38 records, and each integration topic can be looked up
  as one decision.
- **Cost & Risk**: Restating supersession per topic risks changing a decision; the step needs a fidelity review
  like the compaction itself.
- **Attempted**: The grouping analysis was done in the compaction run; the split was not.

## Diagnostic Details

- **Reproduction**: Compute the supersession closure of `ADR-retire-stale-integration-approval-clauses`.
- **Expected / Actual**: Expected topic-sized groups; observed one component of 13.
- **Versions**: base `27987dd7`.
- **Conditions**: not applicable.
- **Workarounds Attempted**: Deferred by user decision.
- **Related Assets**: `adr-compaction` playbook, `ADR-decision-ledger`.

## Evidence

```text
retire-stale-integration-approval-clauses supersedes local-and-pull-request-integration and
configuration-language-and-rendering; reusable-lifecycle-resource-manager supersedes host-cli-lifecycle-authority,
orchestration-workers and five-subagent-levels; subagent-level-projection supersedes an orchestration-workers alias.
```
