---
id: SPEC-retained-runtime-receipt
title: Diagnose a retained MCP runtime older than the receipt it reads
summary: When a retained MCP service refuses a source receipt that its own older reader cannot parse, integration reports the runtime version mismatch with a stable code and a restart directive instead of a bare RECEIPT_INVALID, without weakening receipt validation.
status: planned
created: 2026-10-22
related_capabilities: [CAP-MCP-runtime-registration, CAP-INT-mcp-services]
related_usecases: []
workflow: sdd-spec-bugfix
---
<!-- devkit:skeleton -->

# [SPEC-retained-runtime-receipt] Diagnose a retained MCP runtime older than the receipt it reads

## 1. Problem Statement & Motivation

A retained MCP integration service runs the devkit code it loaded when it started, from the retained base checkout's
runtime. When a source branch carries a receipt written by a newer receipt writer, that older reader refuses the
receipt with `RECEIPT_INVALID` and the directive to restore the receipt and run `devkit sync`. Following the
directive regenerates the same valid receipt, so the Host has no deterministic next step and integration stalls.

### Source feedback

- `FB-retained-runtime-receipt-schema` (scope `repo`, open): diagnose the reader/runtime mismatch with a stable code
  and a restart or re-registration directive, without weakening receipt validation or changing execution authority.

## 2. Defect Characterization

- **Current behavior**: `integration_integrate` for `dev-cloud-agent-rendering` (source head c12c57ae, devkit-dist
  0.1.1 on both sides) ran through a service started from the base checkout before the feature existed on the target.
  The feature added the top-level receipt key `execution_environment` (commit 11ed1e42, feature-only before the merge
  1b36430e). The readiness provider of `devkit-spec` reads the source tree's `.devkit/installation.json` with the
  service's loaded `devkit_dist.features.project.repositories.receipt.parse_receipt`, which refuses every key outside
  its `_REQUIRED` and `_OPTIONAL` sets: `RECEIPT_INVALID`, `.devkit/installation.json: receipt: unknown keys
  ['execution_environment']`, fix "Restore .devkit/installation.json from version control ..., then run
  `devkit sync`". The same refusal reproduces in the current reader for any key it does not know (a receipt with an
  added `future_key` gives `receipt: unknown keys ['future_key']` and the same fix). The refusal reaches the Host
  unchanged: `providers.check` re-raises an `AdvisoryError` from the provider, and the provider's rule and workflow
  readers report the receipt's own code.
- **Facts available to the service**: the receipt's `tool` record names the writer (`devkit-dist`, its version); the
  service knows its own loaded distribution versions (`importlib.metadata`) and the files it imported.
  `CAP-MCP-runtime-registration` checks matching runtime and service versions only when a launch descriptor is built,
  not while a retained service runs. The repository does not bump package versions for receipt changes, and ordinary
  sync keeps the committed `tool` version, so in the reported case reader and writer report the same version 0.1.1.
  `CAP-DIST-sync-and-transactions` states one current receipt schema, with no version dispatch or migration reader.
- **Expected behavior and its basis**: per the agreed intent (decision `gate:plan-intent`), a retained service whose
  loaded code predates a receipt schema change refuses with a stable UPPER_SNAKE code and a deterministic `[ACTION]`
  directing a service restart or re-registration, instead of an undiagnosed `RECEIPT_INVALID`
  (`ARCH-08-1-agent-output`, `CAP-ADV-agent-advisory-protocol`: everything an agent acts on has a stable code and a
  deterministic directive).
- **Behavior to preserve**: receipt validation stays strict: unknown keys, wrong types, duplicate keys and unsafe
  paths remain refusals (`packages/devkit-dist/tests/integration/features/project/test_receipt.py`); a receipt corrupted or hand-edited
  in the same writer generation keeps `RECEIPT_INVALID` and its restore directive; runtime selection,
  execution environment guards and integration authority stay unchanged (`CAP-MCP-runtime-registration`,
  `CAP-INT-mcp-services` tests under `packages/devkit-mcp/tests/` and `packages/devkit/tests/`); no automatic
  runtime refresh or route substitution.
- **Reproduction conditions**: a retained service (or an in-process reader) whose receipt reader predates a
  top-level receipt key reads a source receipt that carries it; in a test, the reader's known key set lacks a key
  the receipt carries while the receipt's `tool` record names the same writer package.

## 3. Non-Goals

1. **Scope Excluded**: tolerating or ignoring unknown receipt keys, an automatic runtime refresh or restart, a route
   substitution (MCP to CLI or pull request), or any change of execution authority or runtime selection.
2. **Scope Excluded**: migration readers or version dispatch for the receipt schema.

## 4. Acceptance Criteria & Behavioral Contracts

The resolved-behavior criterion depends on the open detection question recorded with this run.

### [AC-02] A corrupted receipt keeps RECEIPT_INVALID
- **Given** a receipt whose writer generation equals the running reader's and which carries an unknown top-level key
- **When** any consumer reads it through `load_receipt` or `parse_receipt`
- **Then** it raises `ReceiptError` with code `RECEIPT_INVALID` and the existing restore directive

### [AC-03] Validation stays strict
- **Given** any receipt the reader refuses today (unknown, missing or mistyped keys, duplicate keys, unsafe paths)
- **When** it is read by a reader of any generation
- **Then** the read refuses; no unknown key is accepted or dropped
