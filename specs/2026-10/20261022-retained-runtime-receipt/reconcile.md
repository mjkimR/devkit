---
reconcile_id: REC-retained-runtime-receipt
feature: SPEC-retained-runtime-receipt
status: pending
targets:
  - file: docs/capabilities/mcp/CAP-MCP-runtime-registration.md
    resolution: modified
  - file: docs/capabilities/integration/CAP-INT-mcp-services.md
    resolution: modified
---

# Reconcile: `SPEC-retained-runtime-receipt`

## Living Spec changes

- `CAP-MCP-runtime-registration`, Runtime contract: the server records the installed devkit source at start and
  refuses every non-read-only call with `MCP_RUNTIME_STALE` when a loaded module of those packages no longer matches
  it (AC-04, AC-05); plugins from managed assets and never-imported files do not count; no self-refresh and no
  authority.
- `CAP-INT-mcp-services`, section 3: before every provider run the executor refuses a source that changes the receipt
  reader and carries a receipt only that reader accepts with `INTEGRATION_RECEIPT_READER_CHANGED` and the CLI-route
  directive (AC-01); other refused receipts keep `RECEIPT_INVALID` (AC-02, AC-03). Section 6 points to the stale
  service refusal.
- Quick references: `docs/development/reference/integration.md` and `docs/development/reference/host.md` list the
  two codes.

## No-impact documents

- `CAP-DIST-sync-and-transactions`: the receipt schema, its single-schema rule and strict validation are unchanged;
  `READER_MODULES` only names the reader's modules.
- Use cases: `UC-drive-development-to-integration` steps and postconditions are unchanged; both refusals are
  diagnoses of failures that already stopped integration.

## Source feedback

- `FB-retained-runtime-receipt-schema`: resolved by this spec; both cases are implemented and verified by
  `test_receipt_reader.py` and `test_loaded_code.py` (envelopes `green-01.yaml`, `reverify-01.yaml`).
