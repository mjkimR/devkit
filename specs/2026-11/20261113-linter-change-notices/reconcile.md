---
reconcile_id: REC-linter-change-notices
status: pending
targets:
  - file: docs/capabilities/governance/CAP-GOV-rules-engine.md
    resolution: modified
  - file: docs/capabilities/governance/CAP-GOV-evaluation-lifecycle.md
    resolution: modified
  - file: docs/capabilities/governance/CAP-GOV-rule-authoring.md
    resolution: modified
  - file: docs/capabilities/gate/CAP-GATE-commit-gates.md
    resolution: modified
  - file: docs/development/reference/rules.md
    resolution: modified
  - file: docs/decisions/2026-11/20261113-change-scoped-rule-notices.md
    resolution: modified
  - file: packages/devkit/README.md
    resolution: modified
---

# Reconciliation: `SPEC-linter-change-notices`

## Contract agreement

- `CAP-GOV-rules-engine`: NOTICE/INFO compatibility, consider status, no repair/promotion obligations, explicit bounded read context and transient suppression/error semantics agree with CLI, evaluator and context/memo implementation.
- `CAP-GOV-evaluation-lifecycle`: independent change_scope/hygiene rules, exact working/staged/CI pairs, semantic/deletion ranges, capture omissions and fresh autofix rechecks match the source; directory-only deletions preserve ordinary empty selections.
- `CAP-GOV-rule-authoring`: exported immutable ChangeSpan/FileChange helpers and matching/metadata validation describe the implemented rule API. No production reminder catalog is shipped.
- `CAP-GATE-commit-gates`: NOTICE findings pass as GATE_RULES_NOTICES independently of warning and error behavior, including strict mode.
- Rules reference and owning package README restate the command/API and output contracts. The accepted ADR traces the delivered decisions and states empirical limits.

## Review and verification

High code review ran three independent rounds. Initial outside-target-fix and nested-workspace failures were fixed and confirmed by fresh rounds. Canonical input handling was corrected in the existing owner. The last exact one-line helper correction met all minor-fix conditions with two Red-to-Green original-blob/false-reminder regressions and unchanged outside rejection.

The original draft incorrectly described warning-finding strict promotion. Host selected preservation of the actual current contract: warning/INFO stdout findings remain nonblocking in strict CLI checks. The compatibility regression confirms that behavior; advisory warnings retain their own strict semantics.

## Entrypoints

Keep existing doorway files; add the explicit read-context use case to the rules-engine capability. Reject broad rules directories, model/helper files and tests as new doorway candidates. Lifecycle, authoring and gate entrypoints already route readers to their owning operations.

## Remaining scope

Every accepted AC-01 through AC-10 is implemented and verified. No required implementation or concrete follow-up is deferred. Native file-read interception and production reminder catalogs remain excluded by the accepted scope. Live model receipt and host use remain best-effort limits, with no model-obedience, comparative quality or timing claim.
