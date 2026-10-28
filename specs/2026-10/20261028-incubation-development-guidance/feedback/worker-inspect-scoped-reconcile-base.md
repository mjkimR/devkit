---
id: FB-worker-inspect-scoped-reconcile-base
title: Worker inspection conflates turn and feature comparison bases
scope: repo
kind: friction
category: tool-error
target: packages/devkit-spec/src/devkit_spec/features/worker/usecases/inspect.py
origin: agent
severity: workaround
recurring: false
status: open
created_at: 2026-10-28
---

# [FB-worker-inspect-scoped-reconcile-base] Worker inspection conflates turn and feature comparison bases

## 1. Friction / Question

- **Context**: A multi-turn feature created a capability in an earlier accepted turn and finalized reconciliation in its last turn.
- **Expectation**: Audit writes against the last accepted turn head while checking resolved contract targets against the cumulative feature comparison.
- **Actual**: Worker inspection passed the last accepted turn head to CI rules. RULE-reconcile-contract rejected a correctly modified cumulative target absent from only that final turn's diff.
- **Workaround**: Preserve the exact scoped write audit, ancestry, cleanliness and envelope checks; independently run the required cumulative governance against main and the returned-head affected tests. These passed. Do not report the composite scoped rules result as a pass or add a document no-op.
- **Suggestion**: Model a separate governance comparison base, retaining the last accepted head for write-scope auditing and showing both identities.

## Diagnostic Details

- **Reproduction**: Inspect the guidance final head62bf1887 against accepted43a12db6.
- **Expected / Actual**: Expected cumulative target evidence; actual SPEC_WORKER_RULES_FAILED because CAP-DLV-idea-incubation was unchanged in the final turn.
- **Versions**: devkit-spec0.1.4.
- **Conditions**: Multiple committed, accepted Development turns; earlier capability creation remains in the branch's full feature diff.
- **Workarounds Attempted**: Cumulative rules against main2ee13ec1 passed with errors0/warnings0; scoped writes stayed authorized and affected44 passed on the returned head.
- **Related Assets**: Worker inspector runner invocation; RULE-reconcile-contract; spec-delegate worker validation.

## Evidence

```text
inspect --base43a12db6 --head62bf1887: ancestry/head/scope/worktree/envelopes/workflow PASS; rules FAIL
rules check --ci --base main: errors0 warnings0
just test-affected --base43a12db6: 44 passed
CAP-DLV-idea-incubation exists in the full feature diff but not in the final scoped-turn diff
```
