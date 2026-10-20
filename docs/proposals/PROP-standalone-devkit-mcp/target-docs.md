---
id: PROP-standalone-devkit-mcp-target
title: Standalone MCP Living Spec targets
summary: "Maps the standalone MCP runtime, registration and approval contracts to their Development reconciliation targets."
status: draft
proposal: PROP-standalone-devkit-mcp
created_at: 2026-10-20
targets:
  - file: docs/architecture/ARCH-05-1-containers.md
  - file: docs/architecture/ARCH-05-2-components.md
  - file: docs/architecture/ARCH-05-3-command-plugins.md
  - file: docs/architecture/ARCH-05-4-distribution-components.md
  - file: docs/architecture/ARCH-07-deployment.md
  - file: docs/capabilities/host/CAP-HOST-lifecycle-observation.md
  - file: docs/capabilities/integration/CAP-INT-mcp-services.md
  - file: docs/development/reference/host.md
  - file: docs/development/reference/integration.md
---

# Living Spec targets

- `ARCH-05-1-containers`: optional runtime wheel, dependency graph and lockstep release.
- `ARCH-05-2-components`: core contracts, runtime/service inversion and host registration ownership.
- `ARCH-05-3-command-plugins`: devkit mcp mount; executable remains owned by dist.
- `ARCH-05-4-distribution-components`: local registration planning, ledger and transactions.
- `ARCH-07-deployment`: package combinations and retained runtime lifetime.
- `CAP-HOST-lifecycle-observation`: extract MCP behavior, preserve hook ownership and narrowly authorize project registration.
- `CAP-INT-mcp-services`: Host-owned approval, cloud/resume guards and environment origin.
- `ADR-dist-module-split` and `ADR-dist-command-composition`: narrowly superseded MCP clauses via promoted PADR.
- Relevant handoff/worktree capability discovered during Development: configuration identity and unchanged exact-scope handoff authority.
- Package READMEs, docs/development/reference/host.md, integration reference, release/install guides and AGENTS.md package overview.

Existing accepted ADR bodies remain append-only; promote the PADR with explicit supersession rather than editing
historical decisions. The config proposal owns its own core effective-config contract and worktree-copy documentation.
