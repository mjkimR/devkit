---
id: PLAN-integration-merge-moved-target
spec: SPEC-integration-merge-moved-target
---

# Technical Plan: `SPEC-integration-merge-moved-target` Integrate a conflict-free moved target without requiring the source to contain it

## 1. Constitution & Invariant Review

- `ADR-moved-target-merge` supersedes the local containment clauses of `ADR-local-and-pull-request-integration`;
  `ADR-post-batch-test-run` supersedes the post-merge test clause of `ADR-test-selection-and-ci`. Both are accepted
  and already in `docs/decisions/2026-10/`; Development adds a "Superseded in part by" line to each superseded ADR
  without changing its status or `superseded_by`.
- `ARCH-05-2-components`: the change stays in `devkit_agt.features.worktree`, `devkit_agt.features.integration` and
  `devkit_spec.features.delivery`; no layer direction changes and `packages/devkit-core/` is untouched.
- `ARCH-08-1-agent-output`: new text fields are added to existing sentinels; codes and exit codes stay.
- No other conflict.

## 2. Architecture Overview & Impact

| Component | Change |
| --- | --- |
| `worktree/usecases/planning.py` `plan_finish` | New keyword `advance: bool = False`. With it and `merge_method == "no-ff"`, a source that neither contains nor is contained by the target plans a merge build (still `check_identity`); without it, or under `ff-only`, today's `WORKTREE_MERGE_NOT_FF` and error order stay. |
| `worktree/services/merging.py` | `build_result(..., prospective=False)`: with `prospective=True` (requires `advance`), the merge-tree result is written as a deterministic unsigned commit object (`git hash-object -t commit -w --stdin`). Git 2.38 and conflict refusals are unchanged. |
| `worktree/models/errors.py` | `WORKTREE_MERGE_NOT_FF` and `WORKTREE_MERGE_CONFLICT` fixes name the conditional base merge (and `no-ff`/`devkit integration` for `ff-only`/`finish --merge`). |
| `integration/usecases/service.py` `_prepare` | Local route passes `advance=True`. For a moved target it builds the prospective commit, runs the readiness provider (or the acceptance preview) with the prospective context, the finish guards with `merge-base(target, source)`, `receipts.check_merge` and reads the prospective policy from the merged commit; cleanup scopes come from the approved context. The request's `context` stays the approved context. |
| `integration/models/contracts.py` | `IntegrationContext` docstring: a provider can receive an unlanded prospective result at prepare. |
| `integration/models/errors.py` | `INTEGRATION_RECEIPT_CONFLICT` fix names the conditional base merge and prepare again. |
| `integration/cli.py` | `[INTEGRATION_PREPARED: ... target_sha=<sha>]`; `[INTEGRATION: ... target_sha= build_target= result= disclosure=]`. |
| `delivery/usecases/integration.py` | CI-rule reasons on a result (`result_sha` set) name the conditional base merge and `devkit rules fix`; `_unit_advance` fix names it too; new `result_reasons(context)` runs the result-dependent checks (unit advance, CI rules on the result) for the acceptance preview; docstring states prepare may pass a prospective result. |
| `delivery/usecases/native_plan_accept.py` | Preview runs `result_reasons` when its context has `result_sha` and refuses with `SPEC_PROPOSAL_APPROVAL_NOT_READY`; the composed result adds `target_sha` and `disclosure`. |
| `delivery/cli/proposals.py` | The composed `[ACCEPTED: ...]` line adds `target_sha=`, `landed=` and `disclosure=` when the result carries them. |
| Bundle skills (`spec-integrate`, `spec-orchestrate` and its `git-operator-operations.md`, `spec-review-proposal`, `spec/references/completion.md`) | Conditional base merge; batch test run in `spec-orchestrate` Completion. |
| Repository policy (`AGENTS.md` Verification, `docs/development/{ci-cd,workflow}.md`, `docs/development/reference/{worktree,integration}.md`, `guides/INSTALL_GUIDE.md`) | Coverage outside a batch run and the batch command; the Git 2.38 note covers prepare. |

No new dependency.

## 3. Component & Interface Design

```python
def plan_finish(position, branch, *, pull_request="auto", delete_branch=True, merge_method="no-ff",
                target_sha=None, advance=False) -> FinishPlan: ...

def build_result(base, *, branch, target_branch, target, source, method, advance=False,
                 prospective=False) -> str: ...

# devkit_spec.features.delivery.usecases.integration
def result_reasons(context: IntegrationContext) -> list[str]: ...  # [] without context.result_sha
```

Prospective commit object (bytes passed to `git hash-object -t commit -w --stdin`):

```text
tree <merged tree>
parent <target>
parent <source>
author <committer ident of the later parent, verbatim>
committer <same>

chore(merge): integrate <branch> into <target branch>
```

Prepare flow for a moved target (local route):

```text
plan_finish(advance=True) -> moved = not already and not is_ancestor(target, source)
moved: prospective = build_result(advance=True, prospective=True)   # WORKTREE_MERGE_CONFLICT / _GIT_UNSUPPORTED
       post_digest, config = _prospective(root, prospective, target)
       check context = IntegrationContext(plan, task, result_sha=prospective)
       readiness = preview(check) | providers.check(provider, check)
       run_finish_guards(root, branch, merge-base(target, source), source)
       receipts.check_merge(root, prospective, (target, source))
cleanup_scopes(approved context); request.context = approved context
```

## 4. Error Handling & Edge Cases

- Conflict, Git below 2.38 and missing identity refuse in `_prepare` before a request exists; nothing changes because
  the prospective commit is an unreferenced object.
- `ask`: `integrate` prepares again; a deterministic prospective commit gives the same digest when nothing moved; a
  target moved after the presented prepare changes `TARGET_SHA`/`RESULT_SHA` evidence, so the digest differs and
  `INTEGRATION_REQUEST_STALE` asks for a fresh decision.
- Composed acceptance: `_compose_execute` prepares again after the acceptance commit (normal provider on the new
  prospective result); the request comparison already excludes readiness, so the prospective commits of the preview
  and the fresh preparation may differ.
- Pull-request route: `plan_finish` without `advance`, unchanged.

## 5. Verification & Test Plan

| AC | Tests |
| --- | --- |
| AC-01, AC-03, AC-04, AC-05 (receipt), AC-07, AC-08 (`ff-only`), AC-10 | `packages/devkit/tests/e2e/features/integration/test_base_advance.py` (prepare-time moved target cases) |
| AC-08 (`finish --merge`) | `packages/devkit/tests/integration/features/worktree/test_merging.py` (existing refusal kept) and `test_base_advance.py` |
| AC-08 (pull-request) | `plan_finish` without `advance` in `packages/devkit/tests/integration/features/worktree/` |
| AC-09 | `packages/devkit/tests/e2e/features/integration/` CLI text test; `packages/devkit-spec/tests/e2e/features/delivery/test_plan_accept_cli.py` |
| AC-04 (`[tool.spec]`), AC-05 (CI rules) | `packages/devkit-spec/tests/e2e/features/delivery/test_integration.py` |
| AC-02, AC-06 | `packages/devkit-spec/tests/e2e/features/delivery/test_plan_accept_cli.py` |
| AC-11 | `packages/devkit-spec/tests/integration/bundles/spec/` asset test |

Commands: `just test devkit <paths>`, `just test devkit-spec <paths>` during development; before the final report
`just lint-check`, `just check` per touched package, `just test-affected` (with its `mode=full` fallback),
`just rules-check`, `just smoke` and `uv run devkit sync --check`. The baseline is the accepted head `cf991c47`, where
`test_diverged_branch_is_refused_with_a_sha_preserving_fix` passes.
