---
id: FB-classification-maintenance-playbook-case
title: Classification criteria name no maintenance-playbook refactor case
scope: repo
kind: change-request
category: instruction-conflict
target: packages/devkit-spec (spec skill references/classification.md)
origin: agent
severity: workaround
recurring: false
status: open
created_at: 2026-10-26
---

# [FB-classification-maintenance-playbook-case] Classification criteria name no maintenance-playbook refactor case

## 2. Suggestion / Change Request (suggestion, change-request)

- **Current Procedure**: the `spec` bundle's classification criteria give `overall-refactor` to a behavior-free
  structural change across the project whose direction settles during the work, and keep a refactor inside one
  feature or module on the feature workflows. They name no case for a maintenance playbook run whose decision round
  has already agreed the changes. `ADR-apply-behavior-preserving-batches-as-direct-mode-refactors` refines
  `ADR-overall-refactor-workflow`: a review-refactor batch's multi-module work item is overall-refactor work in
  direct mode, and a single-module one follows the feature workflow at its own depth.
- **Proposed Procedure**: add one line to the classification criteria stating that a behavior-preserving work item
  agreed in a maintenance playbook's decision round (review-refactor) classifies as `overall-refactor` when its
  edited source files span more than one feature or module, and as `feature` at its own depth otherwise.
- **Expected Benefit**: an agent classifying a review-refactor work item without reading the playbook does not
  route agreed refactors to `spec` depth feature work.
- **Cost & Risk**: one line in the `spec` bundle; none to behavior.
- **Attempted**: not edited: `packages/devkit-spec/` is outside this Unit's write scope (spec §3 non-goal 5). The
  playbook states the route itself (`references/applying.md` §1). Restart on the next change to the classification
  reference; done when it names the case.

## Evidence

```text
spec skill references/classification.md: overall-refactor = structural change across the project, no new behavior, direction settles during the work.
ADR-apply-behavior-preserving-batches-as-direct-mode-refactors §4: refines the applicability of ADR-overall-refactor-workflow for review-refactor runs.
```
