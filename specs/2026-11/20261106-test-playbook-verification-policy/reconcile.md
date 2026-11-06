---
reconcile_id: REC-test-playbook-verification-policy
status: resolved
targets:
  - file: docs/capabilities/delivery/CAP-DLV-test-management.md
    resolution: modified
  - file: docs/usecases/delivery/UC-assess-test-management.md
    resolution: modified
---

# Reconciliation: SPEC-test-playbook-verification-policy

CAP-DLV-test-management reflects repository-first consultation, missing-preference clarification, concrete
recommendation and one change-decision round (AC-06/12); inventory and independent-group criteria with native
required checks (AC-01/03/04/11); local exact-revision pending coverage and accepted-risk cloud repair examples
(AC-02/07/08); conditional self-contained optional execution (AC-09/10); and comparable evidence limits (AC-05).
UC-assess-test-management reflects that flow through evidence, aims, safe execution, recommendation, decision,
routing and report, with extension scenarios for absent invocation, unclear groups, pending/failed observation,
cloud nightly repair and inconclusive tuning.

No runtime/API, architecture, dependency, glossary term or general completion-policy change is introduced. No
waiver, deferred required work or source feedback retirement is needed. Existing entrypoints remain the main
router for both documents; derived helpers/tests are not doorways. Fresh code review PASS at bb156395 covers all twelve
criteria; separate reconcile verification follows this implementer-authored reflection.
