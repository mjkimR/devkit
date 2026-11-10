---
reconcile_id: REC-verification-execution-ownership
status: pending
targets:
  - file: docs/capabilities/harness/CAP-HARN-agent-guidance.md
    resolution: modified
  - file: docs/capabilities/delivery/CAP-DLV-delivery-workflows.md
    resolution: modified
  - file: docs/capabilities/delivery/CAP-DLV-test-management.md
    resolution: modified
  - file: docs/decisions/2026-11/20261110-verification-execution-ownership.md
    resolution: modified
---

# Reconciliation

All four targets reflect worker-native synchronous verification and Host-owned postlanding asynchronous execution.
The executor runtime and the original executor decision remain unchanged. The new decision records the operational
ownership boundary across bundles without inventing supersession. No use-case flow or architecture edge changes.
The client guide and installation entry links preserve native commands, optional tooling, combined suites and
manual ownership outside the managed block. Tests verify rendered guidance rather than live agent compliance.
No required work is deferred and no source feedback was named as a direct-fix input.
