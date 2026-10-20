---
id: ADR-independent-mcp-runtime-with-project-registration-and-environment-guards
title: Independent MCP runtime with project registration and environment guards
summary: "Place MCP transport in an optional devkit-mcp wheel, keep service contracts in core and domain execution in agt/spec, and reconcile owned project registrations through sync while enforcing cloud restrictions at runtime."
proposal: SPEC-standalone-devkit-mcp
status: accepted
created_at: 2026-10-20
---

# [ADR-independent-mcp-runtime-with-project-registration-and-environment-guards] Independent MCP runtime with project registration and environment guards

- **Status**: Accepted
- **Date**: 2026-10-20

---

## 1. Context & Problem Statement

`ADR-dist-module-split` moved host whole into dist; `ADR-dist-command-composition` made the server version follow
dist. The selected independent-runtime direction requires a narrow revision of those MCP clauses. Existing hooks,
CLI executable ownership and portable installation receipts retain their current owners. Existing services import
SDK-free contracts, which must remain available without installing a transport package.

## 2. Decision Drivers

Keep runtime installation optional, avoid cyclic dependencies and duplicate wheel paths, make project registration
converge even after runtime removal, and preserve exact native approval authority. Configuration location must not
be confused with the retained executable required by worktree cleanup. Sync must never approve host trust.

## 3. Considered Options

| Option | Benefit | Cost / decision |
| --- | --- | --- |
| Leave MCP in dist | Fewest moves | Does not satisfy the selected independent runtime direction. |
| Put contracts and registration exclusively in runtime | One apparent owner | Forces optional-runtime imports in domain services and leaves no cleanup after uninstall. |
| Runtime wheel, lower contracts and dist file reconciliation | Optional SDK, acyclic imports, reversible owned registration | Selected; requires explicit provider and local ownership boundaries. |
| User-scoped global setup as default | Existing implementation | Binds one repository/runtime globally and does not meet project sync selection. |

## 4. Decision Outcome

Create `devkit_mcp` in the optional, foundation-lockstep `devkit-mcp` wheel. It depends on dist and SDK/runtime
libraries, serves `devkit.host.services`, and mounts `devkit mcp`. SDK-free service contracts move to `devkit.core.mcp`;
agt/spec own their services. Dist's host/distribution layer owns a narrow desired-registration provider contract,
project host-file transactions and ignored machine-local ownership ledger. The runtime provider owns launch
selection and requirements. Dist-only operations neither import nor require the runtime.

Default sync registration targets selected Codex CLI/Claude Code project files with `[mcp] register=true`. It
preserves foreign entries and refuses collisions rather than modifying global host configuration or trust.
Automatic writes require an untracked ignored destination: newly created files receive narrow clone-local exclude
entries, while tracked or visible foreign untracked files are left unchanged with explicit registration-unavailable
and CLI/PR fallback guidance. This limitation preserves native handoff/integration clean-state requirements;
setup never bypasses it. No tracked ignore-file edits or Git clean-state bypass is introduced. Removal
requires exact ownership, including after package uninstall. The committed installation receipt remains portable.

Retained executable, retained domain executor and owning config workspace are separate identities. Configuration
uses the independent copied local file contract of `SPEC-local-config-execution-environment`; no live parent
inheritance is introduced here. Cloud auto-registration exposes the read-only service subset. Both runtime and
domain mutation boundaries refuse cloud interactive approval and resumed mutation; no missing UI grants authority.

Direct/local-orchestrated approvals belong to the Host. Native confirmation is the normal route when connected;
explicit existing CLI/PR authorization is recovery. No extra conversational approval is required after the exact
native confirmation, and no host permission prompt is suppressed.

On promotion, this decision supersedes only `ADR-dist-module-split`'s whole-host MCP placement and
`ADR-dist-command-composition`'s MCP server-version owner, not their other contracts. It also authorizes the narrow
project-registration exception that Development must reflect in `CAP-HOST-lifecycle-observation`. The proposal
contains the detailed acceptance evidence and failure semantics.

## 5. Consequences

A new release wheel, command path and testing matrix are required. No external consumers require a migration
shim; previous user-scoped entries get explicit conflict/recovery instructions rather than automatic conversion.
Machine-local registration ownership must survive normal sync and detect edits. Consumers that track native
project config cannot receive automatic machine-specific registration in that file; an existing host-managed
registration or the explicit CLI/PR route remains available. Exclusions created for new files are narrowly owned
and retained as clone-local setup, with explicit cleanup guidance; creating them must not hide existing foreign
untracked host files in another registered worktree. Generated absolute paths are local setup. Runtime registration cannot
prove actual host discovery, trust or form UI. Those require separate implementation evidence.

The configuration proposal is an integration-order dependency, not an assumed accepted contract. This proposal
can be accepted independently, but dependent Development cannot proceed against missing APIs or invent a resolver.
