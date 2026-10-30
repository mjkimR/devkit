---
id: PLAN-worker-audit-known-host-advance
spec: SPEC-worker-audit-known-host-advance
---

# Technical Plan: `SPEC-worker-audit-known-host-advance` Stop requiring an unchanged base checkout in worker validation

## 1. Constitution & Invariant Review

`ADR-drop-the-base-checkout-equality-from-worker-validation` (accepted, promoted at handoff) supersedes two clauses of
`ADR-orchestration-workers`: "and the base checkout unchanged" in committed results and their validation, and
"comparing them with what the Host recorded before spawning stays the Host's step" in informational range inspection.
It carries no `supersedes` field (`SPEC-worker-audit-known-host-advance` §5), so `ADR-orchestration-workers` stays
accepted and gets one pointer line. `ADR-reusable-lifecycle-resource-manager` keeps the write audit with the
Host unchanged. No `docs/architecture/` invariant changes; no new ADR is needed.

## 2. Architecture Overview & Impact

Documents and tests only; no code, dependency or CLI change.

- **Bundle source** `packages/devkit-spec/src/devkit_spec/bundles/spec/bundle/skills/spec-delegate/references/`:
  - `worker.md`, Validate: the clean-worktree condition drops "and the base checkout's status and HEAD match what you
    recorded before spawning"; a new condition requires `<returned>` to add this turn's `worker` envelope, absent at
    `<accepted>`; one sentence states that base advances (Host, other session or unknown) never block the range, that
    no base merge is required first and that a partial committed escape is the accepted residual. Bundle text cites
    no ADR ID, because consuming projects lack this repository's decision records; the capability sentence cites it.
  - `payload.md`, Workers: the first bullet drops "record the base checkout's `git status --short` and HEAD before
    spawning".
  - `spec` is a selected bundle, so `devkit sync` reprojects these into `.devkit/managed/` (ignored) and may update
    `.devkit/installation.json` and the managed `AGENTS.md` block; every tracked output is committed and listed as
    `(sync output)`.
- **Living Spec** `CAP-DLV-delivery-workflows`:
  - §4.6.2 One-shot activity workers: "Successful acceptance still requires cumulative ancestry through final HEAD,
    strict allowed paths, clean worktree, unchanged base and checks" names the turn's own `worker` envelope instead of
    "unchanged base"; the Host-validation sentence gains that base advances never block the range and the accepted
    residual, citing the ADR.
  - Worker inspection, Base checkout input: "observations for the Host's comparison with its saved state, not checks"
    becomes information with no Host comparison.
- **ADR pointer** `ADR-orchestration-workers`: one pointer line under "Committed results and their validation" naming
  the promoted ADR and both superseded clauses.
- **Tests** `packages/devkit-spec/tests/`:
  - `integration/bundles/spec/test_role_contracts.py`: the range-validation test replaces the base-checkout token tuple
    with the own-envelope condition and keeps the other conditions; a new test asserts that neither `worker.md` nor
    `payload.md` has a block pairing the base checkout with "before spawning" or "status and HEAD" (AC-01).
  - `integration/features/worker/test_worker_inspect.py`: a characterization test advances `main` in the base
    checkout after the worker's turn and inspects the linked worktree (AC-03).

## 5. Error Handling & Edge Cases

- A full escape: the returned head lacks this turn's envelope, so the new `worker.md` condition fails and the Host
  blocks the range as today.
- A dirty base checkout keeps stopping at handoff (`SPEC_HANDOFF_BASE_DIRTY`) and integration
  (`WORKTREE_BASE_DIRTY`); inspection keeps reporting it as `base_checkout.dirty_paths` without failing.
- A partial committed escape passes every check; the ADR records it as the accepted residual with its follow-up
  trigger, and `worker.md` states it so the Host knows the limit.

## 6. Verification & Test Plan

| Scenario | Evidence |
| --- | --- |
| AC-01 | `just test devkit-spec tests/integration/bundles/spec/test_role_contracts.py` |
| AC-02 | Reconcile review (`reconcile-reviewer`) of the capability and both ADRs, `just rules-check` |
| AC-03 | `just test devkit-spec tests/integration/features/worker/test_worker_inspect.py` |
| Whole unit | `just lint-check devkit-spec`, `just check devkit-spec`, `just test-affected` (mode=full fallback), `just rules-check`, `uv run devkit sync --check` |

Known pre-existing failure on `main`: `test_agent_output_contract.py::test_fixes_carry_no_placeholder`; reported, not
fixed. No before/after measurement applies: the spec names no measured outcome.
