---
id: CAP-HARN-isolated-execution
title: Isolated Native Command Execution
summary: "Run native commands asynchronously in fixed-commit detached checkouts with persistent evidence, internal waiting and guarded cancellation and cleanup. Callers own external resource isolation and delivery decisions."
area: harness
status: active
usecases:
  - UC-execute-an-isolated-command
entrypoints:
  - packages/devkit/src/devkit_agt/features/isolated_execution/cli.py
  - packages/devkit/src/devkit_agt/features/isolated_execution/usecases/operations.py
---

# [CAP-HARN-isolated-execution] Isolated Native Command Execution

## 1. Summary

The harness `exec` group starts project-native commands independently of the launch caller and retains evidence outside their disposable checkouts. `ADR-isolated-test-runs` assigns ownership; `CAP-WT-task-worktrees` owns checkout creation/removal. `devkit run` remains synchronous in the current directory (`CAP-CMP-bounded-execution`).

## 2. Scope & Boundary

In scope: fixed locally available commit, detached checkout, captured supervisor, project setup, native argv, run discovery, bounded logs, wait, confirmed cancellation and explicit cleanup on POSIX macOS/Linux.

Scope Excluded: profiles, test selection, local/cloud policy selectors, remote dispatch, daemon/reboot durability, Windows, delivery approval, automatic retries or rollback, environment expiry and implicit credential copying. Callers provide disposable data, isolated services and ephemeral ports before dispatch. Intentionally escaped/detached processes require project cooperation; this is worktree isolation, not OS containment. Host-enforced descendant termination and application exit policies have no survival guarantee.

## 3. Business Rules & Policies

1. WHEN a caller starts a command, the executor MUST capture a full commit SHA, native argv and the existing worktree setup or explicit setup override, create a unique detached checkout and return a pending run ID before native completion. Launch exit zero proves no command pass.
2. BEFORE native execution, the executor MUST complete checkout/setup and, for receipt-bearing projects, locked managed sync using the checkout-local environment. Any failure prevents native execution. Inherited VIRTUAL_ENV, UV/project overrides and Python import variables are scrubbed; inherited virtual-environment PATH entries are removed. No `.env` or credentials are copied implicitly. Explicit native argv and setup remain project-owned code and may access external resources.
3. WHILE a run exists, the executor MUST keep its captured standard-library supervisor and checkout implementation, private temporary directory, manifest, process identities, timestamps, result and logs in the common Git directory outside the checkout. The supervisor uses a base interpreter and does not import changing project packages after launch. Atomic replacement publishes complete records.
4. WHEN inspecting a nonterminal run, the executor MUST positively identify its supervisor by PID and OS start identity; missing or changed identity is unknown, never passing evidence. Native process exec may change argv without changing start identity. Linux start identity additionally includes proc start ticks; macOS uses ps start identity.
5. WHEN cancellation is requested, the supervisor MUST terminate only positively identified managed processes, discover nested sessions/process groups and confirm shutdown before persisting cancellation. It escalates after two seconds; an unresolved ten-second cancellation wait reports timeout rather than confirmed cancellation. Cancel retains the checkout.
6. WHEN clean is requested, the executor MUST serialize per-run cleanup, require a durable terminal result and explicit persisted positive managed-group quiescence proof, and verify repository, run marker, detached SHA, registered path and clean tracked/untracked content before removing the checkout. Active, unknown, unrelated and unexpectedly dirty checkouts are retained. Before removal, cleanup durably records in_progress. Interruption retains in_progress or unfinished evidence; explicit retry revalidates eligibility while preserving serialization with any already-started remover. Repeated cleanup is idempotent. Evidence is retained; native artifacts inside a removed checkout are lost.
7. WHEN wait is requested, the executor MUST observe internally until a terminal result, unknown ownership or optional timeout. Interruption/timeout stops observation only. With explicit `--clean`, it requests the same guarded cleanup after preserving the result; execution, observer and cleanup outcomes remain separate in one JSON object. Multiple observers may wait safely.
8. WHEN required verification uses a run, the caller MUST apply its result only to the recorded SHA and tested scope. Tool completion delivery belongs to the caller's execution tool; the CLI provides no push notification into an agent conversation.

9. WHEN the native leader exits, the supervisor MUST establish group quiescence with fresh process enumeration before publishing a terminal result. Unresolved or reused established leader identities are rejected before discovery or signalling; unresolved ownership remains unknown without terminal evidence. Retained older terminal evidence without explicit positive proof remains inspectable but cannot authorize cleanup.

Rules 1–9 are covered by `packages/devkit/tests/e2e/features/isolated_execution/test_lifecycle.py` and feature-owned process-identity, terminal-guard and publication-order unit tests. Linux runtime execution is not established by the macOS Development probes.

## 4. Interfaces & Data Contracts

- `devkit exec start --ref SHA [--setup SHELL] -- ARGV`
- `devkit exec list [--limit 1..100] [--offset N]`; `status ID`; `logs ID [--tail N]`; `wait ID [--clean] [--timeout SECONDS]`; `cancel ID`; `clean ID`.
- Every operation accepts `--format text|json`. JSON emits exactly one object. Text emits named, escaped `EXECUTION_RESULT`, `EXECUTION_LIST`, `EXECUTION_RUN`, `EXECUTION_DETAIL` and `EXECUTION_LOG_LINE` sentinels, including an explicit empty-list result.
- Public status/wait/logs project at most 16 argv elements of 256 characters and 16 managed PID/start/group identities, report full counts and truncation, and retain manifest/state/result/log evidence paths. Internal ownership history remains complete. List defaults to a compact page of 20 and accepts up to 100 entries with offset/next_offset; one unreadable run is unknown without hiding other runs. The manifest records schema, run_id, repository/common directory, retained base, sha, argv, setup, runtime interpreter, checkout/environment paths, log/result paths and creation time. Live/terminal records additionally carry supervisor/managed process identities, phase/outcome, command/complete timestamps, native exit_code, diagnostic detail and bounded resource statistics. The evidence layout is `<common-git-dir>/devkit/executions/<run-id>/`.
- Phases/outcomes: preparing, running, passed, failed, setup_failed, cancelled, interrupted, unknown. On a missing or changed supervisor identity, inspection rechecks newly published terminal evidence before declaring unknown. No trustworthy terminal record plus no identified live supervisor is unknown. `list` includes pending and retained terminal runs.
- Start success exits 0 with pending state; invalid/unavailable launch exits 2. Status exits 0 for pending/pass, 1 for known negative execution, 2 for unknown/unreadable evidence. The native exit code is separate.
- Wait exits 0 for passing execution and successful requested cleanup, 1 for known negative execution, 2 for unknown, timeout or refused requested cleanup. Cleanup never replaces the execution result. Earlier cleanup evidence remains visible without changing later execution-only status exits. Cleanup evidence uses `EXECUTION_CLEAN_IN_PROGRESS`, `EXECUTION_CLEAN_UNFINISHED`, `EXECUTION_CLEAN_REFUSED` or `EXECUTION_CLEANED`; an interrupted remover never reports successful cleanup without confirmation.
- Logs default to 100 lines, accept 0–1000 and read at most 64 KiB; full raw output remains at the log path. Tail metadata reports omitted prefix bytes and omitted lines in the bounded read window, including a clipped single huge line. No automatic pruning is performed.

See the execution command reference for stable codes and examples.
