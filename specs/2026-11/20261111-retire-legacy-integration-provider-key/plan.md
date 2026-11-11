---
id: PLAN-retire-legacy-integration-provider-key
spec: SPEC-retire-legacy-integration-provider-key
---

# Technical Plan: `SPEC-retire-legacy-integration-provider-key` Reject the legacy [integration] provider key

## 1. Constitution & Invariant Review

None. No ADR decides that the legacy key is accepted: `ADR-post-merge-verification` already removed provider binding
from the digest, and the acceptance was a transition reader. `CAP-INT-mcp-services` §5 changes its own normative
text within this spec's contract; devkit-dist `RESERVED_TABLES` and `CAP-DIST-sync-and-transactions` stay as they are
(the table remains a reserved name owned by `devkit_agt.features.integration`). No feature edge changes.

## 2. Architecture Overview & Impact

- `packages/devkit/src/devkit_agt/features/integration/services/providers.py`: `effective()` accepts
  `[integration]` only when absent or an empty table. A non-table raises `INTEGRATION_CONFIG_INVALID`
  ("integration must be a table") with fix "Remove [integration] or leave it empty; it accepts no keys". A table
  containing `provider` raises "integration key provider is retired" with fix "Delete provider from [integration];
  the readiness-provider selection is retired". Any other key raises
  "integration accepts no keys: <sorted keys>" with fix "Remove <keys> from [integration]; it accepts no keys".
  `provider` is reported first when it appears with other keys, because its fix is the specific one (AC-01). The
  `policy()` docstring drops the legacy sentence. The normalized policy and its digest are unchanged.
- Tests under `packages/devkit/tests/`: fixtures and parametrized configs stop writing `provider = "fixture"`;
  `test_service.py` gains the provider refusal case and the unknown-key case keeps an actionable fix;
  `test_project_readiness.py` replaces its legacy case with an empty table; a policy test proves an empty table and
  an absent table give the same digest.
- Living Spec: `CAP-INT-mcp-services` §5 (renamed "Integration table"); `CAP-DLV-project-policy` §3 drops the legacy
  sentence; `CAP-DLV-sdd-baseline-adoption` step 7 and its activation paragraph; `UC-adopt-sdd-from-adaptive-development`
  step 6a and scenario "Provider-free activation". Quick references: `docs/development/reference/integration.md` and
  the integration row of `packages/devkit/README.md`.

## 5. Error Handling & Edge Cases

- `[integration]` absent, or present as an empty table: accepted (AC-03).
- `provider` alone or with other keys: the retirement message and fix (AC-01).
- Other keys only: names them, sorted (AC-02).
- Non-table value: shape message (AC-02).
- All refusals are `IntegrationConfigError` (`INTEGRATION_CONFIG_INVALID`) with `target_files=[".devkit/config.toml"]`,
  raised in `prepare` before any Git effect, as today.

## 6. Verification & Test Plan

- `just test devkit tests/integration/features/integration tests/e2e/features/integration` for AC-01..AC-03.
- `just lint`, `just check`, `just test-affected` (mode=full fallback kept).
- AC-04: the `rg` command in `SPEC-retire-legacy-integration-provider-key` AC-04 prints nothing;
  `uv run devkit rules check --ci --base main`; `uv run devkit sync --check`.
