---
id: PLAN-local-config-execution-environment
spec: SPEC-local-config-execution-environment
---

# Technical Plan: `SPEC-local-config-execution-environment`

## 1. Constitution & Invariant Review

None. `ADR-separate-shared-configuration-from-local-execution-and-rendering` authorizes the shared/local split. Core remains independent of distribution and harness; canonical receipt loading and governance remain unchanged.

## 2. Architecture Overview & Impact

- Core gains restricted local parsing, recursive merging, provenance and an explicit-root execution resolver.
- Distribution configuration readers validate the overlay; inventory planning explicitly separates canonical and effective variables. Runtime receipt readers validate local evidence.
- Sync compares inventories, verifies Git ignore/index eligibility and input snapshots, then journals local configuration and the render ledger alongside outputs.
- Worktree start validates and captures the source before creating a checkout, then copies before setup/sync; attach does not copy.
- Distribution/worktree capabilities, architecture, reference and installation guidance explain the boundary.
- No new dependencies. Use existing TOML, transaction, receipt and Git facilities.

## 3. Component & Interface Design

`read_effective_config(root)` returns merged data and leaf source provenance through a stable core result; `resolve_execution_environment(root)` returns environment and selecting source. Shared reads retain their explicit API. Local schema validation lives in core so worktree and future MCP callers need no distribution imports. Shared defaults and current bundle defaults stay in their owners.

Personal rendering compares complete inventories, including selection, modes, guidance, seeds and executable assets. Only differing eligible ignored untracked files enter the local ledger; the canonical receipt is built from shared inventory. Runtime reads use a validated receipt view with local file signatures, while canonical loaders remain untouched.

## 4. Storage & Failure Modes

`.devkit/config.local.toml` is an optional ignored input, updated only for explicit environment persistence. `.devkit/transient/local-render.json` binds personal hashes to canonical receipt and effective variable digests. The existing deployed ledger stores actual bytes. Input digests are checked before the journal applies. Sync rollback preserves prior environment and output. Copy errors retain the created worktree and name deliberate recovery, without setup/sync.

## 5. Verification & Test Plan

AC-01/06: core merge/schema/provenance/root tests. AC-02/03/05/06: distribution transaction, personal rendering, ignore/index, reader, race and CLI matrix tests. AC-04: worktree creation/resume/copy failure tests. Run lint/type checks for dist and harness, `just test-affected --base main` with full fallback, distribution-only and snapshot regressions, governance, independent code review and reconcile review at medium effort.

The existing ignore-file regression is updated to the accepted managed local-entry contract: its unrelated-rule preservation assertion remains and a second sync must be a no-op. Transaction path checks retain case-insensitive alias rejection while allowing the exact shared config path in the journal.
