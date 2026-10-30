---
id: FB-feedback-lifecycle-confirmation-names-wrong-rule
title: The feedback lifecycle ADR confirms source-feedback resolution with a rule that does not check it
scope: repo
kind: friction
category: docs-mismatch
target: ADR-feedback-lifecycle
origin: agent
severity: noise
recurring: false
status: open
created_at: 2026-10-30
---

# [FB-feedback-lifecycle-confirmation-names-wrong-rule] The feedback lifecycle ADR confirms source-feedback resolution with a rule that does not check it

## 1. Friction / Question (friction, question)

- **Context**: Planning of `PROP-feedback-dedup-and-compaction` traced how terminal feedback references are checked
  before deciding that compaction may retire FB IDs.
- **Expectation**: `ADR-feedback-lifecycle` §6 says `RULE-reconcile-contract` and its tests check source-feedback
  resolution at completion, so a reader expects a mechanical check of FB outcomes in `reconcile.md`.
- **Actual**: `RULE-reconcile-contract` checks only the form of `reconcile.md` (`reconcile_id`, `status`, `targets`)
  and the diff evidence of `modified` targets; no code or test of the rule reads feedback IDs or statuses.
- **Workaround (or Interpretation Chosen)**: treated source-feedback resolution as review-only and relied on
  `RULE-document-reference` for FB ID resolution.
- **Suggestion**: correct the Confirmation line to "Review only" for source-feedback resolution (an editable-record
  wording repair), or name the check that actually covers it.

## Diagnostic Details

- **Reproduction**: read `ADR-feedback-lifecycle` §6, then the rule's module docstring and tests.
- **Expected / Actual**: expected a feedback check in the rule; found none.
- **Versions**: base `95b8228c`.
- **Conditions**: not applicable.
- **Workarounds Attempted**: not attempted.
- **Related Assets**: `ADR-feedback-lifecycle`, `RULE-reconcile-contract`,
  `packages/devkit-spec/src/devkit_spec/features/governance/usecases/reconcile_contract.py`.

## Evidence

```text
docs/decisions/2026-10/20261022-feedback-lifecycle.md:89  - `RULE-reconcile-contract` and its tests check source-feedback resolution at completion.
reconcile_contract.py:1-17  docstring: frontmatter reconcile_id/status/targets, waiver rationale, diff evidence of modified targets; no feedback
rg -n "feedback" packages/devkit-spec/src/devkit_spec/bundles/spec/bundle/rules/reconcile_contract/  -> no feedback assertions
```
