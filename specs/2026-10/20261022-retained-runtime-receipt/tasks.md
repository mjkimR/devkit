---
id: TASKS-retained-runtime-receipt
spec: SPEC-retained-runtime-receipt
plan: PLAN-retained-runtime-receipt
---

# Task Breakdown: `SPEC-retained-runtime-receipt` Diagnose a retained MCP runtime older than the code it reads

## Phase 1: Reproduction

- [x] **Task 1.1**: Reproduction tests for both cases
  - **_Boundary**: `packages/devkit/tests/integration/features/integration/test_receipt_reader.py`, `packages/devkit-mcp/tests/integration/features/runtime/test_loaded_code.py`
  - _Requirements: AC-01, AC-02, AC-04, AC-05_
  - **Verification**: `just test agt packages/devkit/tests/integration/features/integration/test_receipt_reader.py`; `just test mcp packages/devkit-mcp/tests/integration/features/runtime/test_loaded_code.py`

## Phase 2: Fix

- [ ] **Task 2.1**: Diagnose a source that changes the receipt reader
  - **_Boundary**: `packages/devkit-dist/src/devkit_dist/features/project/repositories/receipt.py`, `packages/devkit/src/devkit_agt/features/integration/models/errors.py`, `packages/devkit/src/devkit_agt/features/integration/repositories/receipts.py`, `packages/devkit/src/devkit_agt/features/integration/services/providers.py`, `packages/devkit/src/devkit_agt/features/integration/__init__.py`, `docs/development/reference/integration.md`
  - _Requirements: AC-01, AC-02, AC-03_
  - **Verification**: `just test agt packages/devkit/tests/integration/features/integration/`; `just test dist packages/devkit-dist/tests/integration/features/project/test_receipt.py`
- [ ] **Task 2.2**: Refuse protected tools of a service with stale loaded code
  - **_Boundary**: `packages/devkit-mcp/src/devkit_mcp/features/runtime/models/`, `packages/devkit-mcp/src/devkit_mcp/features/runtime/services/`, `packages/devkit-mcp/src/devkit_mcp/features/runtime/usecases/loaded_code.py`, `packages/devkit-mcp/src/devkit_mcp/features/runtime/mcp/server.py`, `docs/development/reference/host.md`
  - _Requirements: AC-04, AC-05_
  - **Verification**: `just test mcp`
