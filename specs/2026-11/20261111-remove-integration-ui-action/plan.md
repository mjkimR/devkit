---
id: PLAN-remove-integration-ui-action
spec: SPEC-remove-integration-ui-action
---

# Technical Plan: `SPEC-remove-integration-ui-action` Remove the integration ui_action field

## 1. Constitution & Invariant Review

None. `CAP-INT-mcp-services` does not list `ui_action` among the result fields, and no ADR or architecture
invariant names it. The removal narrows output only; `ARCH-08-1-agent-output` is unaffected.

## 2. Architecture Overview & Impact

- `packages/devkit/src/devkit_agt/features/integration/models/contracts.py`: drop the `ui_action` dataclass field
  of `IntegrationResult` and its conditional emission in `compact_dict()` (AC-01). `to_dict()` never emitted it.
  The text renderer in `cli.py` never printed it.
- `packages/devkit/src/devkit_agt/features/integration/usecases/service.py`: rename the third parameter of
  `_compose_execute` from `ui_action` to `authority`, delete `fresh.ui_action = ...` and assign
  `fresh.authority = authority` (AC-02). Callers pass `policy` or `host-conversation` already
  (`native_plan_accept.py`, `test_composition.py`), so the observable `authority` is unchanged.
- `packages/devkit-spec/src/devkit_spec/features/delivery/usecases/native_plan_accept.py`: no code change; its
  embedded `integration` object loses the key through `compact_dict()` (AC-02).
- `docs/capabilities/integration/CAP-INT-mcp-services.md`: add `authority` to the JSON field list (AC-03).

## 3. Component & Interface Design

```python
def _compose_execute(
    self, request: IntegrationRequest, lifecycle: AcceptanceLifecycle, authority: str
) -> IntegrationResult: ...
```

## 6. Verification & Test Plan

- AC-01: `packages/devkit/tests/integration/features/integration/test_policy.py` asserts `ui_action` is absent from
  `compact_dict()` with `authority == "policy"`; `test_cli.py` asserts the ask CLI JSON has no `ui_action`.
- AC-02: `test_composition.py` asserts `authority` and no `ui_action` in `compact_dict()`;
  `packages/devkit-spec/tests/e2e/features/delivery/test_plan_accept_cli.py` asserts the embedded `integration`
  object has no `ui_action`.
- AC-03: `rg -n ui_action docs/capabilities docs/development/reference packages` returns nothing.
- Commands: `just lint devkit`, `just check devkit`, `just test-affected --base main`,
  `just test-affected --base main --tier e2e`, `uv run devkit rules check`.
