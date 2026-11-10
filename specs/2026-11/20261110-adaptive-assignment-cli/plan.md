---
id: PLAN-adaptive-assignment-cli
spec: SPEC-adaptive-assignment-cli
---

# Technical Plan

## 1. Constitution & Invariant Review

`ARCH-05-2-components` governs feature layering and typed use cases. `ADR-adaptive-assignment-commands`,
`ADR-adaptive-assignment-ledger-storage` and `ADR-adaptive-requires-document-system` settle the contract changes.
No new decision or feature edge beyond the two approved cross-package edges is needed.

## 2. Architecture Overview & Impact

`devkit_adaptive.features.assignment` owns six typed use cases, CLI adapters, pure scope/fold/verification policy,
Git and document repositories and an append-only ledger repository. `devkit_adaptive.cli` mounts the group.
The package requires devkit-core and devkit-docs at 0.1.6 and click>=8.1.7; no devkit_agt or devkit_spec import.
Architecture edges are devkit_dist.features.project and devkit_docs.features.documents only.

## 3. Component & Interface Design

CLI parses options and formats the exact sentinels/JSON of `SPEC-adaptive-assignment-cli`; it invokes one BaseUseCase
per verb. Use cases resolve the root, coordinate repositories and policy, and return typed result values.
Models hold assignment/event/output values and literal scope predicates. Repositories resolve Git identity,
observe status/commits and validate governing IDs with DocumentIndex in the assigned worktree.

## 4. Storage & State Management

The shared Git directory holds devkit/adaptive/ledger.jsonl and lock. Mutations take the 10-second file lock,
read/fold/validate and append one flushed event. Readers ignore and report the trailing fragment; writers truncate
it under lock before appending. No approach, bundle selection or document tree is required to use commands.

## 5. Error Handling & Edge Cases

Package AdvisoryError subclasses carry stable ADAPTIVE codes, deterministic fixes and exact levels. Verification
collects failed checks and exits 1; input/repository/ledger refusals exit 2. Check commands never execute.
Tests cover linked/bare worktrees, rename status records, preexisting dirt, nested authority, missing worktrees,
concurrent append, damaged lines and fragment recovery, governing aliases and duplicates, JSON and strict mode.

## 6. Verification & Test Plan

Unit and integration tests mirror the assignment feature. Installed-consumer tests exercise the independent wheel
without devkit-spec or catalog. Bundle content tests enforce delegation/document guidance. Documented codes are
selected by docs-only changes. Run just init, uv lock --check, just lint-check, just check, just rules-check,
just test-affected --base f0434e6ed0c981340754256022750527f8887e7a, and just smoke. After synchronous checks,
run E2E at a fixed committed SHA via devkit exec start/wait. Record exact SHAs. Later record-only changes reuse
source checks; Host performs final landed checks. No performance claim requires a missing baseline measurement.
