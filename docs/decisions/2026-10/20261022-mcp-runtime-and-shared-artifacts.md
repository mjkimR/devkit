---
id: ADR-mcp-runtime-and-shared-artifacts
title: Independent MCP runtime, immutable shared artifacts and revision-bound reports
summary: "For optional MCP access and regenerable reports, we put MCP transport in an optional devkit-mcp wheel with guarded project registration and keep reports as immutable artifacts apart from scope and publication records, to keep authority separate, accepting new wheels and records."
status: accepted
created_at: 2026-10-22
aliases:
  - ADR-independent-mcp-runtime-with-project-registration-and-environment-guards
  - ADR-separate-shared-artifacts-from-scope
  - ADR-weekly-report-evidence-and-publication
---

# [ADR-mcp-runtime-and-shared-artifacts] Independent MCP runtime, immutable shared artifacts and revision-bound reports

- **Status**: Accepted
- **Date**: 2026-10-22
- **Deciders**: @minjae
- **Involved Components/Capabilities**: `packages/devkit-mcp/`, `packages/devkit-dist/` (shared artifacts, host
  registration), `packages/devkit-core/`, `CAP-HOST-lifecycle-observation`, `CAP-COLL-work-scope-registry`, the
  maintenance bundle's reporting playbook, `MS-maintenance-operations`

---

## 1. Context & Problem Statement

The package split moved host whole into dist and made the MCP server version follow dist. The selected
independent-runtime direction (`SPEC-standalone-devkit-mcp`) requires a narrow revision of those MCP clauses. Existing
hooks, CLI executable ownership and portable installation receipts retain their current owners. Existing services
import SDK-free contracts, which must remain available without installing a transport package.

`CAP-COLL-work-scope-registry` records authoritative owner tokens and optimistic revisions, while proposal review
reports are regenerable presentation artifacts. Applying TTL and generic CRUD to both would violate the registry's
non-expiring storage and read-only query contract in `ADR-worktrees-branches-and-scope`
(`SPEC-worker-shared-state-mcp`).

`MS-maintenance-operations` needs a manually useful weekly report before a scheduler or durable history
backend exists (`SPEC-weekly-report`). Commits, accepted proposals and current check results alone cannot prove weekly
delivery or resolution, and an external publication can fail independently from successful evidence collection.

---

## 2. Decision Drivers

- Keep runtime installation optional, avoid cyclic dependencies and duplicate wheel paths.
- Make project registration converge even after runtime removal; sync must never approve host trust.
- Preserve exact native approval authority; add no new approval authority.
- Configuration location must not be confused with the retained executable required by worktree cleanup.
- Bounded report sharing across linked worktrees with immutable commit binding.
- SDD-agnostic package ownership; independent CLI access; optional retained local MCP transport; read-only viewers and
  queries.
- Preserve source revision, observation interval and limitations behind each report claim.
- Keep report generation useful without maintenance sweeps, external accounts or publication authority.
- Make retries and same-period reruns distinguishable without a new runtime or database.
- Fit the independently invocable maintenance playbooks in `SPEC-periodic-drift-reconciliation`.

---

## 3. Considered Options

### MCP runtime

- **Leave MCP in dist** (rejected by `ADR-independent-mcp-runtime-with-project-registration-and-environment-guards`):
  fewest moves, but does not satisfy the selected independent runtime direction.
- **Put contracts and registration exclusively in runtime** (rejected by
  `ADR-independent-mcp-runtime-with-project-registration-and-environment-guards`): forces optional-runtime imports in
  domain services and leaves no cleanup after uninstall.
- **Runtime wheel, lower contracts and dist file reconciliation** (selected by
  `ADR-independent-mcp-runtime-with-project-registration-and-environment-guards`): optional SDK, acyclic imports,
  reversible owned registration; requires explicit provider and local ownership boundaries.
- **User-scoped global setup as default** (rejected by
  `ADR-independent-mcp-runtime-with-project-registration-and-environment-guards`): binds one repository/runtime
  globally and does not meet project sync selection.

### Shared artifacts

- **A common mutable record/artifact backend** (rejected by `ADR-separate-shared-artifacts-from-scope`): couples
  unrelated authority and expiry semantics.
- **Immutable local artifacts with an adapter seam** (selected by `ADR-separate-shared-artifacts-from-scope`): meets
  the immediate report consumer.
- **A production remote artifact adapter** (deferred by `ADR-separate-shared-artifacts-from-scope`): viable but
  requires a provider/authentication/deployment decision; deferred to `FB-remote-shared-adapter-follow-up`.

### Weekly reports

- **Replace one report per calendar week and embed its mutable publication result** (rejected by
  `ADR-weekly-report-evidence-and-publication`): destroys earlier evidence and changes the report after publication.
- **Immutable run-specific local reports with publication outcomes in a companion record** (selected by
  `ADR-weekly-report-evidence-and-publication`): stable evidence, same-period reruns, ordinary files and existing
  connectors.
- **A history backend and automatic maintenance sweeps with reporting** (rejected by
  `ADR-weekly-report-evidence-and-publication`): dependencies and external mutations beyond the manual reporting
  milestone; durable history storage belongs to `MS-maintenance-operations`.

---

## 4. Decision Outcome

### MCP runtime and project registration

- Create `devkit_mcp` in the optional, foundation-lockstep `devkit-mcp` wheel. It depends on dist and SDK/runtime
  libraries, serves `devkit.host.services`, and mounts `devkit mcp`. SDK-free service contracts move to the core
  foundation (`devkit.core.mcp` when decided; `devkit_core.base` under `ADR-package-split-and-namespaces`); agt/spec
  own their services. (ADR-independent-mcp-runtime-with-project-registration-and-environment-guards)
- Dist's host/distribution layer owns a narrow desired-registration provider contract, project host-file transactions
  and an ignored machine-local ownership ledger. The runtime provider owns launch selection and requirements.
  Dist-only operations neither import nor require the runtime.
  (ADR-independent-mcp-runtime-with-project-registration-and-environment-guards)
- Default sync registration targets selected Codex CLI/Claude Code project files with `[mcp] register=true`. It
  preserves foreign entries and refuses collisions rather than modifying global host configuration or trust.
  (ADR-independent-mcp-runtime-with-project-registration-and-environment-guards)
- Automatic writes require an untracked ignored destination: newly created files receive narrow clone-local exclude
  entries, while tracked or visible foreign untracked files are left unchanged with explicit registration-unavailable
  and CLI/PR fallback guidance. Setup never bypasses this; no tracked ignore-file edits or Git clean-state bypass is
  introduced. Removal requires exact ownership, including after package uninstall. The committed installation receipt
  remains portable. (ADR-independent-mcp-runtime-with-project-registration-and-environment-guards)
- Retained executable, retained domain executor and owning config workspace are separate identities. Configuration
  uses the independent copied local file contract of `SPEC-local-config-execution-environment`; no live parent
  inheritance is introduced. (ADR-independent-mcp-runtime-with-project-registration-and-environment-guards)
- Cloud auto-registration exposes the read-only service subset. Both runtime and domain mutation boundaries refuse
  cloud interactive approval and resumed mutation; no missing UI grants authority.
  (ADR-independent-mcp-runtime-with-project-registration-and-environment-guards)
- Direct/local-orchestrated approvals belong to the Host. Native confirmation is the normal route when connected;
  explicit existing CLI/PR authorization is recovery. No extra conversational approval is required after the exact
  native confirmation, and no host permission prompt is suppressed.
  (ADR-independent-mcp-runtime-with-project-registration-and-environment-guards)
- This replaces only the package split's whole-host MCP placement and its MCP server-version owner, not their other
  contracts, and authorizes the narrow project-registration exception reflected in `CAP-HOST-lifecycle-observation`.
  The proposal contains the detailed acceptance evidence and failure semantics.
  (ADR-independent-mcp-runtime-with-project-registration-and-environment-guards)

### Shared artifacts

- `devkit.shared` in devkit-dist (the shared feature of `devkit_dist`) holds immutable content-addressed artifacts,
  separate from existing scope records. Equivalent CLI and optional MCP methods share validation, bounded payloads,
  expiry, locking and errors. (ADR-separate-shared-artifacts-from-scope)
- Read/list never sweep; MCP sweep-plan and sweep-apply are separate tools. Identical live content is idempotent,
  while expiration permits a fresh generation with a new URI and never revives the old URI. Local bounded-write MCP
  calls do not elicit forms and remain prohibited in cloud mode. (ADR-separate-shared-artifacts-from-scope)
- The proposal defines concrete keys, metadata, seven-day logical expiry, exclusion checks and acceptance fixtures.
  (ADR-separate-shared-artifacts-from-scope)

### Weekly reports

- A logical report key consists of repository, scope and exact interval/timezone; each generation gets a unique run ID
  and inspected revision. New content means a new run. Default to the previous complete local Monday-to-Monday week,
  allowing explicit endpoints and requiring a timezone if none is configured.
  (ADR-weekly-report-evidence-and-publication)
- Committed evidence is the default. Working-tree observations, optional dirty-state evidence, and events whose
  integration date cannot be proved stay explicitly qualified. A completed-work claim requires verification and
  integration evidence in addition to a status or commit. Missing maintenance evidence is not a clean result.
  (ADR-weekly-report-evidence-and-publication)
- Generate first and verify the local artifact. Publish only to an explicitly selected and authorized destination
  using an existing tool. Record destination, authority, artifact digest and verified receipt separately. Unknown
  publication outcomes require checking the destination before retrying; an unverifiable outcome remains unknown.
  (ADR-weekly-report-evidence-and-publication)
- The selected direction is preliminary until the proposal direction gate. It creates no standing publication
  permission. Artifact location and any external destination are invocation inputs, not fixed organization policy.
  (ADR-weekly-report-evidence-and-publication)

---

## 5. Consequences

- **MCP runtime**: a new release wheel, command path and testing matrix are required. No external consumers require a
  migration shim; previous user-scoped entries get explicit conflict/recovery instructions rather than automatic
  conversion. Machine-local registration ownership must survive normal sync and detect edits. Consumers that track
  native project config cannot receive automatic machine-specific registration in that file; an existing
  host-managed registration or the explicit CLI/PR route remains available. Exclusions created for new files are
  narrowly owned and retained as clone-local setup, with explicit cleanup guidance; creating them must not hide
  existing foreign untracked host files in another registered worktree. Generated absolute paths are local setup.
  Runtime registration cannot prove actual host discovery, trust or form UI; those require separate implementation
  evidence. The configuration proposal is an integration-order dependency, not an assumed accepted contract:
  dependent Development cannot proceed against missing APIs or invent a resolver.
- **Shared artifacts**: consumers must retain exact artifact references and verify source commits; artifact existence
  never approves work. Two reports for one commit may coexist. Filesystem sharing trusts the same OS user and the
  retained MCP process, not forged caller identity. First delivery publishes the remote-adapter protocol and
  registration contract but cannot claim production cross-host support; a concrete backend restarts in a separate
  proposal once its consumer, provider/authentication, namespace owner and integration environment are known.
  `SPEC-cloud-agent-rendering` owns cloud-specific asset rendering; local orchestration still checks MCP connection
  before dependent operations. Scope-registry ownership and revision behavior require no migration.
- **Weekly reports**: reports can be inspected without external setup and retain prior evidence across reruns.
  Several reports may cover one interval, so each names its identity and supersession relationship. Publication
  records can change without changing the report digest. Readers must check scope, revision and limitations before
  comparing runs. The maintenance bundle can be initialized with reporting alone when absent; existing companion
  assets are preserved when present. The Host serializes overlapping catalog writes. The future history backend
  remains independent.

---

## 6. Confirmation

- The `devkit-mcp` testing matrix and dist-only operation without the runtime; the proposals' acceptance fixtures for
  registration, shared artifacts and expiry.
- The reporting playbook remains content-only; manual scenario evidence supplements package and governance tests.

