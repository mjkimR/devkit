---
id: PLAN-mcp-tool-execution-classes
spec: SPEC-mcp-tool-execution-classes
---

# Technical Plan: `SPEC-mcp-tool-execution-classes` Two MCP tool execution classes

## 1. Architecture Overview & Impact
- Target Area: the SDK-free MCP contract in `devkit-core`, its runtime adapter in `devkit-mcp` and its one producer
  in `devkit-dist`; `CAP-MCP-runtime-registration`.
- No layering or feature edge changes. `devkit_mcp` discovery derives the accepted classes from the `Literal` type,
  so narrowing the type narrows discovery with no code change there.

## 2. Component Breakdown & Interface Contracts
- `devkit_core.base.mcp.McpTool`: `execution: Literal["read_only", "bounded_write"] = "bounded_write"`; the
  `read_only` field is removed. A module-level `Execution` alias is not introduced (one use).
- `devkit_mcp.features.runtime.mcp.server.build_server`: `read_only_hint=service.execution == "read_only"`.
- `devkit_dist.features.shared.mcp.tools`: drops `read_only=`.
- Tests: `test_runtime.py` replaces the annotation-separation test with checks for the default, the removed keyword
  and discovery refusal of removed classes; adds a listing test for the derived hint; `test_loaded_code.py` drops
  the `preflight` fixture.
- `CAP-MCP-runtime-registration`: runtime contract and cloud paragraph name the two classes.

## 3. Verification & Test Plan
- `just lint-check devkit-core devkit-mcp devkit-dist`, `just check` for the same modules.
- `just test-affected --base main`, `just test-dist`.
- `uv run devkit rules check`, `uv run devkit workflow envelope check --unit specs/2026-11/20261111-mcp-tool-execution-classes`.
