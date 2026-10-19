---
id: PLAN-direct-planning-procedure
spec: SPEC-direct-planning-procedure
---

# Technical Plan: `SPEC-direct-planning-procedure` Planning procedure reachable from the spec skill for any executor

## 1. Constitution & Invariant Review

- `CAP-DLV-delivery-workflows` §4.6 puts a procedure in a role contract only for a role whose procedure no main
  session runs. A `direct` Host runs Planning, so the steps move to the skill side; the accepted statement that the
  `planning-worker` procedure is in its contract changes with it (`ADR-executor-neutral-planning-steps-in-a-spec-reference`).
- Bundle budgets: 12288 bytes per skill document, 11776 for `spec/SKILL.md`; every `references/` file linked from its
  skill (`packages/devkit-spec/tests/test_bundle_budgets.py`). Role contracts have no budget.
- No CLI, schema or workflow change; `docs/decisions/` stays untouched (the ADRs are already promoted).

## 2. Architecture Overview & Impact

- Target Area: harness/ (the `spec` bundle assets) and delivery/ (`CAP-DLV-delivery-workflows`).
- Measured at base `d981971`: `spec/SKILL.md` 6531 bytes, `planning-worker.md` 7953 bytes. After the move:
  `references/planning.md` 4514 bytes (ADR estimate about 4.5 KB), `spec/SKILL.md` 6613 bytes (about 6.6 KB),
  `planning-worker.md` 4361 bytes (about 4 KB). No other reference changes.

## 3. Component & Interface Design

### Planned Boundaries:
- `harness/`
- `delivery/`

### Excluded Boundaries:
- `docs/decisions/`

- `packages/devkit-spec/src/devkit_spec/bundle/skills/spec/references/planning.md` (new): the contract's steps 2 to 6
  as steps 1 to 5, addressed to "you" as the executor of the turn (the `direct` Host or the `planning-worker`). Only
  the address changes: "with the payload" becomes "with a worker's payload, or from the user in `direct` mode", "the
  `activity-effort` you were given" becomes "the Planning `activity-effort`", "nested subagent" drops from the
  `medium` depth (nesting is the worker's obligation), and the managed paths of `review-loop.md` and `sweep.md` become
  relative links. The step cross-reference "(step 6)" becomes "(step 5)".
- `skills/spec/SKILL.md`: the routing table's `proposal` row links the reference.
- `subagents/planning-worker.md`: `## Procedure` keeps step 1 (worktree, `git -C`, scratch), one step that follows the
  reference by its managed path and names `devkit workflow envelope worker`, and the nested-role rule taken out of
  old step 4 (start as nested subagents, wait, never end while one runs, a failed role is a problem). Purpose, Input,
  Return, Write boundaries and On a problem are unchanged.
- `docs/capabilities/delivery/CAP-DLV-delivery-workflows.md` §4.6: the `planning-worker` row's Skill column and the
  sentence listing the roles whose procedure lives in the contract.

## 4. Error Handling & Edge Cases

- A moved sentence lost or reworded: the `code-reviewer` pass compares the base contract's steps 2 to 6 with the
  reference sentence by sentence; the tests pin the key phrases in the reference and their absence from the contract.
- Rollback: the change is three bundle files, one capability and two tests; reverting the commits restores the base.

## 5. Verification & Test Plan

- `just test devkit-spec` (`test_role_contracts.py`, `test_effort_procedure.py` `CITING`, `test_bundle_budgets.py`,
  `test_workflows.py` projection checks).
- `just lint devkit-spec`, `just check devkit-spec`, `just rules-check`.
- `uv run devkit sync` after the bundle change, and `just smoke` when it rewrites projected files.
