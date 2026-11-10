---
id: ADR-verification-execution-ownership
title: Separate worker verification from Host execution management
summary: "For delegated verification, we keep worker checks native and synchronous and reserve integrated-result asynchronous execution for the Host, to prevent inherited lifecycle duplication, accepting separate worker and Host guidance."
status: accepted
created_at: 2026-11-10
---

# [ADR-verification-execution-ownership] Worker and Host verification responsibilities

## 1. Context & Problem Statement

`ADR-isolated-test-runs` assigns direct Host launch of asynchronous commands. Common completion links and
repository-wide instructions describe local-orchestrated work without distinguishing its actors. A worker can
therefore inherit the Host's launch/wait/cleanup procedure and create another execution checkout for ordinary
checks. Client-owned AGENTS prose survives managed asset upgrades and can retain this ambiguity.

## 2. Decision Drivers

- Preserve native required coverage, necessary worker E2E and final integrated verification.
- Prevent workflow responsibility from spreading through inherited instructions and payloads.
- Keep client commands and CI intact, including combined suites and projects without E2E or devkit.
- Keep the executor CLI general purpose without new role/cwd enforcement or configuration.

## 3. Considered Options

- Keep broad local-orchestrated wording: smaller edit, but inherited instructions retain the ambiguity.
- Separate instruction ownership by actor and phase (chosen): native worker checks and Host-owned postlanding
  execution, with an explicit client upgrade procedure.
- Enforce worker/cwd restrictions in the CLI: adds runtime machinery and prevents legitimate separately requested
  uses without fixing inherited project-owned instructions.

## 4. Decision Outcome

Chosen: responsibility follows the actor and task. This clarifies the original executor decision; no clause of
`ADR-isolated-test-runs` is superseded and its runtime behavior is unchanged.

- Workers run required native checks synchronously in their assigned worktree, including necessary selective
  E2E, and return command, source identity and results. → `CAP-HARN-agent-guidance` asynchronous verification (MUST),
  `CAP-DLV-delivery-workflows` asynchronous verification (MUST).
- The local-orchestrated Host owns post-integration asynchronous execution, collection, cleanup, repair and final
  coverage. Worker payloads and common completion routing retain that boundary. → `CAP-HARN-agent-guidance`
  asynchronous verification (MUST), `CAP-DLV-delivery-workflows` asynchronous verification (MUST).
- Direct/session work retains native verification; a Host in a worktree still owns Host responsibilities.
- Client recommendations preserve native commands, coverage and CI. Combined commands need no invented split or
  E2E tier, and adoption requires neither devkit nor a harness. → `CAP-DLV-test-management` rules 8, 9 and 12a (MUST).
- Managed sync refreshes selected assets and its owned guidance block. Manually owned verification instructions
  are reviewed through the consumer's normal workflow; no automatic cross-repository migration is introduced.

## 5. Consequences

Role-specific wording appears in worker, payload, common completion and Host guidance. Client maintainers audit
old generic exec directives separately from managed updates. Instruction regression tests do not prove live agent
compliance. Required checks and general executor behavior remain unchanged.

## 6. Confirmation

`packages/devkit-spec/tests/integration/bundles/spec/test_isolated_execution_guidance.py` checks local/cloud
completion routing and rendered worker instructions. `packages/devkit-catalog/tests/integration/bundles/test_verification_ownership.py`
checks portable maintenance recommendations. `guides/install/verification-ownership.md` and root AGENTS are reviewed
against the role split. Live agent adherence is Review only.
