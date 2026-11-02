---
id: PLAN-adr-ledger-cleanup
spec: SPEC-adr-ledger-cleanup
---

# Technical Plan: `SPEC-adr-ledger-cleanup` Topic compaction groups and retired stale ADR clauses

## 1. Constitution & Invariant Review

Two decisions change, so each gets a new ADR with `supersedes`: the compaction closure rule and the stale clauses.
The closure rule lived only in `ADR-decision-ledger`. Its replacement is now restated in `CAP-DOCS-document-model`.

## 2. Architecture Overview & Impact

| Component | Change | Serves |
| --- | --- | --- |
| `ADR-group-compaction-by-topic` (new) | Topic groups and cross-group partial supersession | AC-01 |
| `ADR-decision-ledger` | Pointer lines | AC-01 |
| `CAP-DOCS-document-model` §Decision supersession | Compaction groups rule (MUST) | AC-01 |
| `adr-compaction` playbook and `test_playbook_discovery_guidance.py` | Step 1 grouping, Step 2 crossing pairs, Step 3 kept `supersedes` | AC-01 |
| `ADR-retire-native-approval-and-moved-ownership-clauses` (new) | Retires the stale clauses | AC-02 |
| The four target ADRs | Pointer lines | AC-02 |
| Two feedback files | Resolved with Disposition | AC-03 |

## 3. Verification & Test Plan

- `just test devkit-spec tests/integration/bundles/spec/test_playbook_discovery_guidance.py`
- `uv run devkit rules check`, `--phase hygiene` on the playbook, and `just test-affected`
