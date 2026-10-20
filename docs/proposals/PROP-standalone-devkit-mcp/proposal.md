---
id: PROP-standalone-devkit-mcp
title: Independent devkit-mcp runtime and default approval integration
summary: "Extract the shared MCP runtime into devkit-mcp, manage project registrations through sync, and make native MCP the default interactive approval route while retaining domain services in their owning packages."
status: draft
created_at: 2026-10-20
target_area: host/
priority: high
size: L
planning_effort: medium
dev_effort: medium
boundaries:
  owns:
    - packages/
    - packages/devkit-dist/src/devkit/host/
    - packages/devkit-dist/src/devkit/distribution/
    - packages/devkit/src/devkit/integration/
    - packages/devkit-spec/src/devkit_spec/handoff_mcp.py
    - packages/devkit-spec/src/devkit_spec/bundle/skills/spec/
    - scripts/
    - guides/install/
    - docs/capabilities/host/
    - docs/capabilities/integration/
  excludes:
    - packages/devkit-advisory/
    - packages/devkit-spec/src/devkit_spec/scope/
task_kind: feature
workflow: sdd-proposal
---

# [PROP-standalone-devkit-mcp] Independent devkit-mcp runtime and default approval integration

## 1. Background & Hypothesis

`devkit-dist` currently owns the shared MCP transport, service discovery, confirmation callback and onboarding.
`devkit-agt` supplies integration tools and `devkit-spec` supplies Planning-to-Development handoff tools. Keeping
the server inside the distribution package broadens that package beyond asset delivery. Anticipated worker shared
state also makes an approval-only package name too narrow.

Create an independent `devkit-mcp` package at `packages/devkit-mcp/` for the reusable runtime and registration
foundation. The `packages/` boundary names its existing parent for creation, not unrelated package refactoring.
Keep integration,
handoff and future coordination behavior in their domain packages, registered through a shared service contract.
MCP becomes the default interactive approval route for direct and local-orchestrated work, with the Host collecting
the verified scope and requesting approval. Package presence and tool permission alone do not authorize mutations.

## 2. Technical Spike Questions

- **Q1: Package boundary.** Locate transport, service contracts, discovery, registration adapters and CLI entry
  points without circular dependencies or overlapping wheel paths. Decide whether dependency-free contracts stay
  in a lower shared layer. Keep ordinary host hooks in their existing owner and domain execution in agt/spec.
  Review `ARCH-05-1-containers`, `ARCH-05-2-components` and applicable ADRs before recording the final boundary.
- **Q2: Installation and release.** Define standalone installation, package version/dependency policy and whether
  `devkit-agt[mcp]` remains a convenience extra. Update workspace, lockfile, release instructions, affected-test
  discovery, dist-only checks and wheel smoke coverage. Existing optional extras need an explicit disposition;
  package extraction does not require a new compatibility shim or migration framework.
- **Q3: Project registration.** For Codex CLI and Claude Code, verify supported project-local configuration and
  trust behavior. When devkit-mcp is installed, sync should register it unless explicitly disabled; sync does not
  download packages. Define ownership, collision handling, idempotence, package removal, cloud transitions and
  cleanup of only devkit-owned entries. Preserve unrelated entries and account for existing user-scoped devkit
  registrations without silently replacing them.
- **Q4: Runtime lifetime.** Use a retained executable/runtime rather than one removed with a task worktree.
  Define repository binding, linked-worktree discovery, client reconnects and simultaneous server processes.
  Reuse the extension boundary for future services without implementing shared-state storage in this proposal.
- **Q5: Noninteractive environment.** Consume `PROP-local-config-execution-environment`. Prefer omitting automatic
  interactive-approval registration in cloud and always enforce the restriction at runtime for stale registrations
  and direct launches. Reject interactive approval requests before waiting or executing approved mutations, with
  a stable code and deterministic recovery instruction. Retain actual client elicitation-capability checks in
  local mode. Read-only services need not be blocked with interactive approval; decide registration granularity
  accordingly. Never silently convert unavailable approval into automatic execution.
- **Q6: Default workflow.** Define default bundle guidance and recovery when the package, connection or native
  confirmation is absent. Direct and local-orchestrated flows should route approvals through the Host, avoiding
  duplicate conversational prompts and worker-owned approval requests. Establish the supported explicit fallback
  without manufacturing approval. Host sandbox/tool controls remain independent.

## 3. Proposed Design & Impact

Implement in two stages within this proposal: extract the package while preserving existing service behavior,
then connect effective environment settings, project registration and default approval guidance. Extraction can
start independently; environment-dependent behavior waits for the configuration contract in
`PROP-local-config-execution-environment`.

Expected acceptance evidence:

- A built devkit-mcp wheel starts the stdio server, discovers installed services and handles confirmation,
  decline, cancellation and missing elicitation capability. Integration and handoff retain their exact-scope,
  stale-state and recovery checks; a caller-supplied approval flag grants no authority.
- Distribution-only installation works without the MCP runtime. Installed package combinations have no circular
  dependencies, duplicate installed paths or hidden dependence on the monorepo environment.
- Repeated sync converges project registration for Codex CLI and Claude Code, preserving unrelated settings;
  opt-out, missing package and removal have explicit observable behavior. Tests distinguish registration from
  actual connection and native approval UI evidence.
- A cloud interactive approval request fails before confirmation or approved mutation, including when a stale
  registration remains. Local clients without form support also fail clearly. Environment selection never grants
  automatic integration authority.
- Worktree cleanup does not remove the active server runtime. Verified direct and local-orchestrated tasks use
  one Host-owned native approval of the declared scope, without an extra conversational merge confirmation.

Update `CAP-HOST-lifecycle-observation`, `CAP-INT-mcp-services`, package architecture and installation guidance
when implementation changes their contracts. Planning completes the exact packaging, tests, CLI and asset file
boundaries, including metadata outside the initial ownership hints.

Scope excluded: worker coordination storage and generic shared filesystem APIs; these belong to
`PROP-worker-shared-state-mcp`. Policy-authorized unattended merge and cleanup belong to
`PROP-policy-authorized-integration`. Also excluded: remote multi-host hosting, VS Code/SDK/desktop adapters,
host trust or sandbox bypass, and moving domain execution into the shared runtime.

## 4. Lifecycle & Retirement Criteria

Keep this draft until Planning settles package dependencies, project registration ownership, execution-environment
resolution and default approval recovery. Record structural decisions through the normal Planning ADR process.
The independent-package direction is selected; drafting does not accept its detailed design or start Development.
Future shared-state work should consume this runtime instead of creating a second transport. The automatic
integration proposal separately determines whether explicit policy can authorize noninteractive execution.
