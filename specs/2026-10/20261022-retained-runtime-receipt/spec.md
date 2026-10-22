---
id: SPEC-retained-runtime-receipt
title: Diagnose a retained MCP runtime older than the code it reads
summary: Integration refuses a source that changes the receipt reader with INTEGRATION_RECEIPT_READER_CHANGED, and the retained MCP service refuses protected tools with MCP_RUNTIME_STALE when its loaded devkit code differs from the installed code, keeping receipt validation strict.
status: planned
created: 2026-10-22
related_capabilities: [CAP-MCP-runtime-registration, CAP-INT-mcp-services]
related_usecases: []
workflow: sdd-spec-bugfix
---

# [SPEC-retained-runtime-receipt] Diagnose a retained MCP runtime older than the code it reads

## 1. Problem Statement & Motivation

A retained MCP integration service runs the devkit code it loaded when it started, from the retained base checkout's
runtime. Two situations make that code disagree with what it reads, and both reach the Host as a generic refusal
with no deterministic next step:

1. A source branch changes the receipt reader and carries a receipt only the new reader accepts. The target-built
   reader refuses it with `RECEIPT_INVALID` and the directive to restore the receipt and run `devkit sync`, which
   regenerates the same receipt. Restarting the service does not help, because the restarted runtime is still built
   from the target.
2. The retained service keeps running after the installed devkit code changed (a merge into the editable base
   checkout, or a reinstall). Its stale modules then fail against current managed assets with unrelated codes.

### Source feedback

- `FB-retained-runtime-receipt-schema` (scope `repo`, open): diagnose the reader/runtime mismatch with a stable code
  and a deterministic directive, without weakening receipt validation or changing execution authority.

## 2. Defect Characterization

- **Current behavior, case 1 (source changes the receipt reader)**: `integration_integrate` for
  `dev-cloud-agent-rendering` (source head c12c57ae, devkit-dist 0.1.1 on both sides) ran through a service started
  from the base checkout before the feature existed on the target. The feature added the top-level receipt key
  `execution_environment` to the reader's accepted keys (commit 11ed1e42, feature-only before the merge 1b36430e) and
  to its committed receipt. The readiness provider of `devkit-spec` reads the source tree's
  `.devkit/installation.json` with the service's loaded `parse_receipt`, which refuses every key outside its accepted
  sets: `RECEIPT_INVALID`, `.devkit/installation.json: receipt: unknown keys ['execution_environment']`, fix "Restore
  .devkit/installation.json from version control ..., then run `devkit sync`". The same refusal reproduces in the
  current reader for any key it does not know. The refusal reaches the Host unchanged: `providers.check` re-raises an
  `AdvisoryError` from the provider, and the provider's rule and workflow readers report the receipt's own code.
- **Current behavior, case 2 (stale loaded code)**: `integration_integrate` for another unit on 2026-10-22 was refused
  with `INTEGRATION_NOT_READY`, details `RULES_RUN_FAILED`/`RULES_LOAD_FAILED`: "Failed to load rule package
  .../.devkit/managed/spec/rules/id_convention: type object 'Kind' has no attribute 'USECASE'" (also
  `code_entrypoints` and `document_summary`). Every running `devkit_dist mcp serve` process had started at or before
  13:29 (+0900); the merge 277ef3b5 (dev-use-cases, adding `Kind.USECASE` to
  `packages/devkit-spec/src/devkit_spec/features/documents/models/model.py`) landed at 18:02. The base `.venv`
  installs the workspace packages editable from the base checkout, so the installed files gained `Kind.USECASE`
  while the processes kept the module they had imported. The managed rules, read fresh from `.devkit/managed/`,
  reference the new member and fail to load. No refusal names the stale process.
- **Facts available to the service**: the receipt's reader is `devkit_dist.features.project.repositories.receipt`
  (accepted keys and types per object, through `_REQUIRED`, `_OPTIONAL` and the `_object` key sets) together with
  `devkit_dist.features.project.models.receipt` (`SCHEMA` and the record types). The integration executor knows the
  source, the target and their merge base, and reads committed receipts with `git`. The service process knows every
  module it imported (`sys.modules`, each with its source file) and can read the installed source files now. The
  repository does not bump package versions for receipt or code changes and ordinary sync keeps the committed `tool`
  version, so version metadata identifies neither case (both sides reported devkit-dist 0.1.1).
- **Expected behavior and its basis**: per the agreed intent (decision `gate:plan-intent`) and the answer to q1
  (`envelopes/answer-01.yaml`), each case is refused with a stable `UPPER_SNAKE` code and a deterministic `[ACTION]`
  instead of an undiagnosed refusal (`ARCH-08-1-agent-output`, `CAP-ADV-agent-advisory-protocol`):
  - case 1: `INTEGRATION_RECEIPT_READER_CHANGED`, whose `[ACTION]` says a runtime built from the target cannot read
    this source's receipt, restarting does not help, and the integration needs the CLI route run from the source's
    code under separately granted authority;
  - case 2: `MCP_RUNTIME_STALE`, whose `[ACTION]` directs restarting or reconnecting the retained MCP service.
- **Behavior to preserve**: receipt validation stays strict: unknown keys, wrong types, duplicate keys and unsafe
  paths remain refusals (`packages/devkit-dist/tests/integration/features/project/test_receipt.py`); a receipt
  corrupted or hand-edited without a reader change keeps `RECEIPT_INVALID` and its restore directive; runtime
  selection, execution environment guards, read-only diagnostics and integration authority stay unchanged
  (`CAP-MCP-runtime-registration`, `CAP-INT-mcp-services`, tests under `packages/devkit-mcp/tests/` and
  `packages/devkit/tests/`); no automatic runtime refresh or route substitution.
- **Reproduction conditions**: case 1: a Git fixture whose target commits a receipt the running reader accepts and
  whose source commits a receipt with an extra top-level key and changes a file at the reader's module path; prepare
  the integration with the running reader. Case 2: an MCP server built with a baseline of the loaded devkit source
  files, one loaded devkit module's file then differing from that baseline, and a protected tool call.

## 3. Non-Goals

1. **Scope Excluded**: tolerating or ignoring unknown receipt keys, a receipt schema change or version marker,
   migration readers or version dispatch.
2. **Scope Excluded**: an automatic runtime refresh, restart or re-import, a route substitution (MCP to CLI or pull
   request), or any change of execution authority or runtime selection.
3. **Scope Excluded**: detecting stale code in a CLI process; each CLI invocation imports the installed code anew.

## 4. Acceptance Criteria & Behavioral Contracts

The stale-code signal: when `devkit mcp serve` starts, the service records the SHA-256 of every Python source file
under the import locations of the installed devkit packages (top-level `devkit` and `devkit_*`). Before a protected
call, a loaded module of those packages is stale when its source file is now absent, unreadable, outside that record
or different from its recorded digest. A file the process has not imported does not count.

### [AC-01] A source that changes the receipt reader is refused with a dedicated code
- **Given** a target whose committed receipt the running reader accepts, and a source whose committed receipt it
  refuses and whose range from the merge base changes a file at a receipt reader module path
  (`devkit_dist/features/project/repositories/receipt.py` or `devkit_dist/features/project/models/receipt.py`)
- **When** the integration is prepared on the local or the pull-request route, through the MCP service or the CLI
- **Then** it raises `INTEGRATION_RECEIPT_READER_CHANGED` before the readiness provider runs, its `[ACTION]` names the
  CLI route from the source's code under separately granted authority and says restarting does not help, and no
  request is retained

### [AC-02] A corrupted receipt keeps RECEIPT_INVALID
- **Given** a receipt with an unknown top-level key whose source range does not change the receipt reader
- **When** it is read through `load_receipt` or `parse_receipt`, or the integration is prepared
- **Then** the read raises `ReceiptError` with code `RECEIPT_INVALID` and the existing restore directive, and
  integration raises no `INTEGRATION_RECEIPT_READER_CHANGED`

### [AC-03] Validation stays strict
- **Given** any receipt the reader refuses today (unknown, missing or mistyped keys, duplicate keys, unsafe paths)
- **When** it is read, including by the reader-change diagnosis
- **Then** the read refuses; no unknown key is accepted or dropped

### [AC-04] A retained service with stale loaded code refuses protected tools
- **Given** a running MCP server one of whose loaded devkit modules has a source file that differs from the baseline
  recorded at start
- **When** a `bounded_write`, `preflight`, `interactive` or `approved_resume` tool is called
- **Then** the call returns an error with code `MCP_RUNTIME_STALE`, its `[ACTION]` directs restarting or reconnecting
  the retained MCP service, the details name the stale modules, and the tool does not run

### [AC-05] Read-only tools and unchanged code are not refused
- **Given** a running MCP server whose loaded devkit modules all match the baseline, or a `read_only` tool
- **When** the tool is called, including after a devkit file the process never imported changed
- **Then** the tool runs as before and no `MCP_RUNTIME_STALE` is raised
