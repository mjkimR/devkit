---
reconcile_id: REC-mcp-onboarding
feature: SPEC-mcp-onboarding
status: pending
targets:
  - file: docs/capabilities/host/CAP-HOST-lifecycle-observation.md
    resolution: modified
  - file: docs/capabilities/integration/CAP-INT-mcp-services.md
    resolution: modified
  - file: docs/development/reference/host.md
    resolution: modified
---

# Reconciliation

Host owns explicit user registration, conflict handling, retained-runtime checks and registration-only diagnostics.
Integration setup guidance now leads to those commands without changing authorization or execution behavior.
The host quick reference and installation routes describe the commands, scope, failure recovery and separate
connection/UI verification. No architectural layering, approval policy, distribution transaction or story changes
are required. Sync remains independent; there is no selected MCP setting or automatic registration obligation.

Entrypoint candidates are restricted to the host implementation for the host capability. The integration capability
only changes setup guidance and does not own the host implementation paths. No concrete deferred work is retained.
