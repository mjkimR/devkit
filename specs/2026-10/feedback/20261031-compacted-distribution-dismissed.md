---
id: FB-compacted-distribution-dismissed
title: Distribution feedback, dismissed
summary: Bundle asset synchronization, presets, and package distribution.
target: docs/capabilities/distribution/
status: dismissed
created_at: 2026-10-31
aliases:
  - FB-common-exclusion-policy-helper
  - FB-maintenance-companion-playbooks
  - FB-parallel-pruning-cuts-both-owners
  - FB-presentation-fallback-field-unused
---

# [FB-compacted-distribution-dismissed] Distribution feedback, dismissed

## FB-common-exclusion-policy-helper

- **Symptom**: Centralize common exclusion policy for independent local services
- **Response**: dismissed. A speculative refactor with no observed failure
- **Reason**: only two services share the `devkit-mcp.lock` literal. Record new feedback when a third service joins the common exclusion.

## FB-maintenance-companion-playbooks

- **Symptom**: Track the independent maintenance review-refactor companion
- **Response**: Dismissed outcome
- **Reason**: dismissed. `MS-maintenance-operations` owns the `review-refactor` playbook of the `maintenance` bundle, so the roadmap already tracks this delivery.

## FB-parallel-pruning-cuts-both-owners

- **Symptom**: Parallel pruning deletes a rule from both files that point to each other
- **Response**: dismissed by the user's decision
- **Reason**: the failure needs parallel ownership-based pruning across files that point to each other, too narrow a case for standing guidance in `agent-asset-writing`; an independent review of the whole diff caught it in the observed run.

## FB-presentation-fallback-field-unused

- **Symptom**: The presentation language fallback field is now always false
- **Response**: Dismissed outcome
- **Reason**: Dismissed as moot. Under the user decision recorded with the return to build-verify (`decisions/02-return-build-verify.yaml`), an unsupported `[presentation] language` again resolves to `en` with `fallback=true`, and `language_notices` reads that field to return the `PRESENTATION_LANGUAGE_UNSUPPORTED` warning from `devkit sync`, `devkit status` and `devkit config show`. The field is no longer constant or unused.
