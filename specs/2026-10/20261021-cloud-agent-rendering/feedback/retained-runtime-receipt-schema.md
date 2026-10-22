---
id: FB-retained-runtime-receipt-schema
title: Retained MCP runtime cannot integrate a new receipt field
scope: repo
kind: friction
category: tool-error
target: integration_integrate
origin: agent
severity: blocked
recurring: false
status: resolved
resolved_at: 2026-10-22
created_at: 2026-10-21
---

# [FB-retained-runtime-receipt-schema] Retained MCP runtime cannot integrate a new receipt field

## 1. Friction / Question

- **Context**: Integrating the verified execution-aware rendering feature through the retained MCP service under shared-base auto policy.
- **Expectation**: The integration path can consume the prospective receipt produced by the verified feature, or identifies the required runtime refresh before integration.
- **Actual**: The connected service rejected the new execution_environment receipt key with RECEIPT_INVALID before returning an integration request. The feature checkout's sync check and whole affected-test fallback passed.
- **Workaround**: No automatic fallback attempted. Explicit authority for CLI local integration was requested under the existing completion policy; the request is pending at capture.
- **Suggestion**: Document and test retained-runtime upgrade/bootstrap handling for receipt contract changes. Diagnose reader/runtime mismatch rather than recommending restoration and sync that regenerates the same valid feature receipt. Do not weaken receipt validation or silently change execution authority.

## Diagnostic Details

- **Reproduction**: Official sync on the feature branch adds execution_environment: local. Call integration_integrate for dev-cloud-agent-rendering through the already connected service; it rejects that key.
- **Expected / Actual**: Feature receipt accepted or actionable runtime guidance versus unknown-key failure.
- **Versions**: Feature head c12c57ae78d109d037cb2433222bc96eb5b7a881; retained runtime package revision unknown.
- **Conditions**: Local Codex orchestration; shared-base dev-integration auto; latest main merged cleanly; retained service predates feature receipt support.
- **Workarounds Attempted**: Read-only tool inventory found no runtime refresh operation. No service configuration, receipt rollback, route substitution or permission change performed.
- **Related Assets**: packages/devkit-dist/src/devkit/core/receipt.py; CAP-INT-mcp-services; spec completion procedure.

## Evidence

```text
integration_integrate: RECEIPT_INVALID
.devkit/installation.json: receipt: unknown keys ['execution_environment']
Feature sync --check: workspace matches the selection
Host affected fallback: 4271 passed, 14 skipped
```

- **Disposition**: `SPEC-retained-runtime-receipt`: a source that changes the receipt reader is refused before the readiness provider with `INTEGRATION_RECEIPT_READER_CHANGED` and a CLI-route directive under separately granted authority; a retained MCP service whose loaded devkit code differs from the installed code refuses protected tools with `MCP_RUNTIME_STALE` and a restart or reconnect directive. Receipt validation stays strict and authority is unchanged; verified by `test_receipt_reader.py` and `test_loaded_code.py`
