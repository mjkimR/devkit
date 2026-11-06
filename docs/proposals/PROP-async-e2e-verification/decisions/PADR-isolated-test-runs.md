---
id: PADR-isolated-test-runs
title: Own isolated asynchronous test runs in the harness
summary: "For asynchronous local verification, we add a harness-owned test-run lifecycle with fixed-commit environments and persistent evidence, to let the Host proceed, accepting setup cost and OS-bounded process survival."
proposal: PROP-async-e2e-verification
status: draft
created_at: 2026-11-06
---

# [PADR-isolated-test-runs] Own isolated asynchronous test runs in the harness

## 1. Context & Problem Statement

The existing worktree API supports revision-aware preparation but models activity branches. `devkit run` waits
for its command, terminates it on interruption and prunes old logs. Neither is a recoverable background test-run
manager. Main's files and dependencies can change while a long E2E command executes.

## 2. Decision Drivers

- Let a single Host launch and later collect verification without mandatory delegation.
- Reuse native project commands across devkit and client repositories.
- Bind execution to an exact commit with isolated dependencies and retained evidence.
- Keep Git-only integration and git-operator responsibility bounded.

## 3. Considered Options

- Repository script plus thin just recipe: smaller initial registration cost, but duplicates launch/state/cleanup
  behavior for clients and mixes reusable lifecycle with devkit's pytest selection.
- Harness `devkit test` plus project-owned commands: selected; adds a public command and run-store contract while
  keeping test selection and setup in the consumer's native tooling.
- Mandatory verifier subagent: adds context/coordination cost and still needs process isolation and evidence.
- Extend git-operator or make compact execution detached by default: expands existing interruption and lifecycle
  responsibilities, risking ordinary command cleanup semantics.

## 4. Decision Outcome

- `devkit_agt.features.test_execution` owns background run launch, persistent state, bounded inspection,
  cancellation and cleanup; typed use cases remain the exposed application boundary.
  → `ARCH-05-2-components` harness feature ownership and layering (MUST).
- Worktree owns creation and removal of run-owned fixed-commit test checkouts. These test-only environments have
  no SDD Unit, merge, push or activity post-finish effects; existing task-worktree policy remains unchanged.
  → `ARCH-05-2-components` worktree and test-execution responsibilities (MUST).
- Local-orch guidance describes direct Host launch, independent work, outstanding coverage, result collection and
  repair priority; git-operator retains Git lifecycle jobs. A one-run starting recommendation stays in guidance,
  rather than becoming an executor-wide admission policy.
  → `CAP-HARN-agent-guidance` local-orch verification procedure (MUST).
- Project-native setup and argv passed directly after `--` determine execution. No test-profile mapping or
  local/cloud policy selection is introduced. Delivery decisions remain with the calling workflow. Test execution
  depends only on the declared worktree and project features; compact and generic integration gain no test-supervision dependency.
  → `ARCH-05-2-components` declared feature graph (MUST).
- Manifests/logs survive eligible checkout cleanup, distinguish setup failure and unknown execution, and never
  turn launch success into passing evidence. Host-enforced termination and reboot have no survival guarantee.
  The harness test-execution capability restates these interface clauses during Development.

The proposal contains command and state details. Restatement traces above name intended Development changes,
not active contracts introduced by Planning.

## 5. Consequences

The CLI requires registration, storage compatibility, process identity checks and tests on macOS/Linux. Each
fresh environment has setup cost and can compete for CPU with workers. No performance improvement is assumed.
A script remains a useful measurement fixture, not a parallel production scheduler. The caller checks shared
external resources and supplies project-specific isolation before dispatch. Missing durable evidence leaves
verification pending; no automatic retries or broad cleanup hide it.

## 6. Confirmation

AC-1 and AC-3 through AC-8 in `PROP-async-e2e-verification` cover tier-safe selection, immutable environment,
nonblocking ordering, local-orch scheduling guidance, restart inspection, process identity and cleanup. AC-9 and
AC-10 check direct native command passing and the boundary between execution evidence and delivery decisions.
Development runs
separate-process probes and a native consumer fixture on supported platforms. Local measurements compare the
same revision/test set with async disabled/enabled. Host scheduling compliance is Review only.
