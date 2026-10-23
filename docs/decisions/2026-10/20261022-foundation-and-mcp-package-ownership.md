---
id: ADR-foundation-and-mcp-package-ownership
title: Foundation in devkit-core, the mcp extra on devkit-agt
summary: "For package ownership, we keep the shared foundation in devkit-core, the devkit executable and standalone distribution in devkit-dist, and the mcp extra on devkit-agt requiring devkit-mcp, to keep the foundation free of application and transport code, accepting one more wheel in lockstep."
status: accepted
created_at: 2026-10-22
supersedes:
  - ADR-dist-foundation-ownership
---

# [ADR-foundation-and-mcp-package-ownership] Foundation in devkit-core, the mcp extra on devkit-agt

- **Status**: Accepted
- **Date**: 2026-10-22
- **Deciders**: @minjae
- **Involved Components/Capabilities**: `packages/devkit-core/`, `packages/devkit-dist/`, `packages/devkit/`,
  `packages/devkit-mcp/`, `architecture/` (`ARCH-05-1-containers`, `ARCH-07-deployment`), `capabilities/distribution/`
  (`CAP-DIST-content-packages`)

---

## 1. Context & Problem Statement

`ADR-dist-foundation-ownership` gave `devkit-dist` the shared foundation needed for a standalone distribution. The
foundation now ships as its own wheel: `devkit-core` owns the `devkit_core` package (`base` for shared errors and
SDK-free MCP contracts, `core` for generic filesystem, Git, parsing, plugin, logging and extension-dispatch
primitives), depends only on `devkit-advisory` and PyYAML, and is a dependency of `devkit-dist`, `devkit-agt` and
`devkit-mcp`. The MCP transport is the `devkit-mcp` wheel, reached through the `mcp` extra of `devkit-agt`;
`devkit-dist` declares no `mcp` extra. No decision records either placement, so the in-effect ADR states an owner the
code does not have.

---

## 2. Decision Drivers

- Installing `devkit-dist` alone provides distribution without the harness engines.
- One package owns the `devkit` executable when distribution and harness are installed together.
- Dependency direction follows the foundation-to-engine layering, and the foundation imports no application or
  transport code.
- An optional transport stays out of the wheels that do not need it.

---

## 3. Considered Options

### Option 1: Foundation in `devkit-core`, `mcp` extra on `devkit-agt` (Selected)
- **Overview**: record the current layout: `devkit-core` owns the foundation, `devkit-dist` owns the executable and
  standalone distribution, `devkit-agt[mcp]` requires `devkit-mcp`.
- **Pros**: the foundation cannot import an application wheel or the MCP SDK; `devkit-dist` stays free of the SDK.
- **Cons**: one more wheel released in lockstep.

### Option 2: Keep the foundation in `devkit-dist` (`ADR-dist-foundation-ownership`)
- **Cons**: `devkit-mcp` and other providers would depend on the distribution wheel for generic primitives, and the
  decision would keep contradicting the code.

---

## 4. Decision Outcome

We adopt **Option 1**. It replaces `ADR-dist-foundation-ownership` as a whole; its standalone-scope, executable and
dependency-direction rules are carried over unchanged.

- **Standalone distribution** (carried over): installing `devkit-dist` alone MUST provide distribution commands,
  native hook support, context loading and playbook functionality without installing `devkit-agt`.
- **Executable** (carried over): `devkit-dist` MUST own the sole `devkit` console entry point.
- **Harness** (carried over): `devkit-agt` MUST depend on `devkit-dist` and supply the higher-level harness engines.
  `devkit-dist` MUST NOT depend on `devkit-agt`.
- **Foundation**: `devkit-core` MUST own the shared foundation as the `devkit_core` package, with `base` (shared
  errors and SDK-free MCP contracts, never importing `core`) and `core` (generic implementations). It depends only on
  `devkit-advisory` and PyYAML and MUST NOT import application packages or the MCP SDK. `devkit-dist`, `devkit-agt`
  and `devkit-mcp` depend on it at the same version. This replaces the foundation clause of
  `ADR-dist-foundation-ownership`.
- **MCP runtime**: the MCP transport ships as `devkit-mcp`, which depends on `devkit-core`, `devkit-dist` and the MCP
  SDK. `devkit-agt` declares the `mcp` extra requiring `devkit-mcp` at the same version for agt-only installs.
  `devkit-spec` requires `devkit-mcp` at the same version because its native handoff tools are part of the Spec
  package's default capability. `devkit-dist` declares no `mcp` extra and never imports `devkit_agt` or the MCP SDK.
- Project configuration, receipts and execution binding stay in the distribution's project feature, and the
  namespace, module split and `search` extra stay as `ADR-package-split-and-namespaces` decides.

---

## 5. Consequences

- **Positive**: the in-effect decision matches the wheels; a reader finds the foundation owner and the MCP extra in
  one record.
- **Negative / Risks**: a project that wants the MCP transport without the harness has no `devkit-dist` extra and
  requires `devkit-mcp` directly.
- **Follow-ups**: none.

---

## 6. Confirmation

- `packages/devkit-core/tests/integration/test_package.py` (the foundation imports only its own code, advisory, YAML
  and the standard library; no application or transport module loads).
- `packages/devkit-dist/tests/unit/architecture/test_layering.py` (`test_distribution_never_imports_the_harness`) and
  `just test-dist`.
- `packages/devkit/tests/integration/package/test_lockstep.py` (`test_devkit_agt_extras_pass_through_to_devkit_dist`,
  the version pins between the wheels).
