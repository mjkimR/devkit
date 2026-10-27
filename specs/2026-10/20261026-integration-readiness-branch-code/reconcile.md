---
reconcile_id: REC-integration-readiness-branch-code
spec: SPEC-integration-readiness-branch-code
status: resolved
targets:
  - file: docs/capabilities/integration/CAP-INT-mcp-services.md
    resolution: modified
  - file: docs/capabilities/governance/CAP-GOV-evaluation-lifecycle.md
    resolution: modified
  - file: docs/usecases/delivery/UC-drive-development-to-integration.md
    resolution: modified
  - file: docs/development/reference/integration.md
    resolution: modified
---

# [REC-integration-readiness-branch-code] Reconcile: Integration names a branch rule that needs the branch's code

## Living Spec changes

- `CAP-INT-mcp-services`: a paragraph after the readiness binding states that readiness runs with the invoking
  runtime's installed code, the EARS rule that a synchronized rule module of the source (or the result at a build)
  importing a module or name of an installed top-level package the runtime lacks refuses with
  `INTEGRATION_RULE_RUNTIME_MISMATCH` before the provider, that the check parses and resolves without executing
  source code, which failures stay with the provider, and that integration never builds or selects a source runtime
  itself, and that it follows `INTEGRATION_RUNTIME_IN_WORKTREE` and `INTEGRATION_RECEIPT_READER_CHANGED`; the stable
  code table gains the code and its directive.
- `CAP-GOV-evaluation-lifecycle` section 6 (managed rule copies in snapshots): the receipt pins rule files, not the
  package code they import; a snapshot's rules import the evaluating process's code, so a missing implementation module
  is `RULES_LOAD_FAILED`, and integration names the case first with its own code.
- `UC-drive-development-to-integration`: extension 7h (after 7f and 7g) and Scenario 21 for the refusal and the separately authorized
  source-built runtime recovery.
- `docs/development/reference/integration.md`: the code table row.

- No change: `CAP-GOV-rule-authoring` and `CAP-GOV-rules-engine` (rule loading and `RULES_LOAD_FAILED` are unchanged);
  `CAP-ADV-agent-advisory-protocol` (the new code follows the existing conventions); no bundled guide or skill names
  the integration codes, so no consumer-facing mirror changes. Entrypoints: `CAP-INT-mcp-services` already owns
  `packages/devkit/src/devkit_agt/features/integration/`.

## Source feedback

- `FB-integration-readiness-loads-new-rule-with-base-code`: resolved by `SPEC-integration-readiness-branch-code`, the
  suggestion's second alternative (its own code and directive); the disposition is appended to the feedback file.
  The first alternative (evaluating with the source's environment automatically) is Non-Goal 1, because the source
  would then be judged by its own rule engine and provider and a build's result tree is in neither environment.
