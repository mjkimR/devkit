---
id: PLAN-cli-naming-consistency
spec: SPEC-cli-naming-consistency
---

# Technical Plan: `SPEC-cli-naming-consistency` Consistent CLI option naming

## 1. Architecture Overview & Impact
- Target Area: `devkit_dist.features.distribution` (bundle refresh), `devkit_agt.features.workflow` (envelope CLI),
  `devkit_spec.features.delivery` (spec new), their capability contracts, references, the installation guide and
  three spec bundle guidance files.
- No new feature edge: `devkit_spec.features.delivery` already depends on `devkit_spec.features.proposals`, which
  owns `require_task_kind`, and every package already uses `devkit_core.base.errors.ArgumentError`.

## 2. Component Breakdown & Interface Contracts

1. **Bundle refresh** (`cli/bundles.py`, `usecases/snapshots.py`): drop the `--check` option and the use case's
   `check` keyword. `RefreshBundleSnapshot.execute(..., expect=None, candidate=None)` previews when both are `None`,
   raises `ArgumentError` (`ARGUMENT_INVALID`, target the missing flag) before taking the lock when exactly one is
   given, and otherwise applies under the existing digest match (`BUNDLE_SNAPSHOT_CONFLICT`).
2. **Envelope help** (`workflow/cli/envelope.py`): `envelope new` loses `hidden=True`; the other workflow authoring
   commands keep it.
3. **Spec new** (`delivery/cli/specs.py`, `delivery/usecases/specs.py`): a `--task-kind` option passed to
   `CreateSpecUseCase.execute(task_kind=...)`. Both `task_kind` and `workflow` given is `ArgumentError`
   (`[TARGET] --task-kind`); otherwise `require_task_kind` validates it and a non-default kind maps to
   `spec_workflow(kind)` (`sdd-spec-<task-kind>`), the default to `None`, as the proposal handoff does. The
   refusals precede `create_spec`, so nothing is written.
4. **Documents**: `CAP-DIST-in-repo-bundles` (rule 6, interface), `CAP-DLV-cli-and-output` §1,
   `CAP-DLV-spec-bundles` (rules 1 and 5, command table and example), `docs/development/reference/distribution.md`,
   `guides/install/existing-repository.md`, the devkit bundle's `in-repo-bundle` instruction and the spec bundle's
   `spec` skill, `worktree` reference and `spec-specify` skill; then `devkit sync`.

## 3. Verification & Test Plan
- Integration: `packages/devkit-dist/tests/integration/features/distribution/test_snapshots.py` (preview without
  digests writes nothing, one digest is `ArgumentError`, mismatches stay conflicts).
- E2E: `packages/devkit-dist/tests/e2e/cli/test_snapshots.py` (CLI preview without digests, `--check` rejected,
  one digest `ARGUMENT_INVALID`).
- Integration: `packages/devkit/tests/integration/features/workflow/test_cli.py` (`envelope new` listed, others
  hidden); `packages/devkit/tests/integration/package/test_agent_output_contract.py` now covers `envelope new` as
  a visible leaf (`--format`, `-w`).
- Integration: `packages/devkit-spec/tests/integration/features/delivery/test_spec_initialization.py`
  (`--task-kind bugfix` binding, `--task-kind feature` default, both options and an invalid kind refused without
  writes).
- Checks: `just lint-check`, `just check`, `just test-affected --base main` (and `--tier e2e`),
  `uv run devkit rules check --ci --base main`, `uv run devkit sync --check`.
