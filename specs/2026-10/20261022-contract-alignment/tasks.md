---
id: TASKS-contract-alignment
spec: SPEC-contract-alignment
plan: PLAN-contract-alignment
---

# Task Breakdown: `SPEC-contract-alignment` Align ADRs and alias wording with the shipped contracts

## Phase 1: Implementation

- [ ] **Task 1.1**: Foundation and `mcp` extra ownership ADR superseding `ADR-dist-foundation-ownership`, with link repair
  - **_Boundary**: `docs/decisions/2026-10/20261022-foundation-and-mcp-package-ownership.md`, `docs/decisions/2026-10/20261019-dist-foundation-ownership.md`, `docs/architecture/ARCH-05-1-containers.md`, `docs/capabilities/distribution/CAP-DIST-content-packages.md`, `docs/decisions/2026-10/20261022-configuration-language-and-rendering.md`, `docs/decisions/2026-10/20261022-package-split-and-namespaces.md`
  - _Requirements: AC-01, AC-05_
  - **Verification**: `uv run devkit rules check`
- [ ] **Task 1.2**: Host-owned review loop recovery ADR superseding `ADR-bounded-high-effort-review-loop`, `CAP-DLV-delivery-workflows` aligned, with link repair
  - **_Boundary**: `docs/decisions/2026-10/20261022-host-owned-review-loop-recovery.md`, `docs/decisions/2026-10/20261019-bounded-high-effort-review-loop.md`, `docs/capabilities/delivery/CAP-DLV-delivery-workflows.md`, `docs/architecture/ARCH-04-delivery-strategy.md`, `docs/decisions/2026-10/20261022-review-and-reconcile-verification.md`
  - _Requirements: AC-02, AC-03, AC-05_
  - **Verification**: `uv run devkit rules check`
- [ ] **Task 1.3**: Alias wording in the contracts, the `consumption` instruction and the glossary
  - **_Boundary**: `docs/capabilities/delivery/CAP-DLV-spec-bundles.md`, `docs/capabilities/traceability/CAP-TRACE-code-entrypoints.md`, `docs/capabilities/distribution/CAP-DIST-manifest-spec.md`, `packages/devkit-dist/src/devkit_dist/bundles/devkit/bundle/instructions/consumption.md`, `docs/glossary.md`, `.devkit/managed/devkit/`, `.devkit/installation.json`
  - _Requirements: AC-04, AC-05_
  - **Verification**: `uv run devkit sync --check`, `just test-affected`, `uv run devkit rules check`
