---
id: PLAN-feedback-guidance-and-scope
spec: SPEC-feedback-guidance-and-scope
---

# Technical Plan: `SPEC-feedback-guidance-and-scope` Scratch cleanup guidance, merge-conflict interaction and declared feedback scope

## 1. Constitution & Invariant Review

None. `ADR-merge-proposal-materials-per-leaf-at-handoff` keeps the code and the class, which this plan keeps; it does
not fix the directive mode. No `MUST` of `docs/architecture/` changes. The scope change narrows `excluded-tree` for
one input kind in `CAP-COLL-work-scope-registry`; `CAP-TRACE-code-entrypoints` derivation is unchanged.

## 2. Architecture Overview & Impact

- **Bundle guidance** (`packages/devkit-spec/src/devkit_spec/bundles/spec/bundle/`): development-worker rule 8, the
  planning-worker probe line and the `spec-delegate` payload reference (AC-01, AC-02); `devkit sync` refreshes the
  projected copies (only ignored `.devkit/managed/` and agent projections; `devkit sync --check` names any tracked
  output). `CAP-DLV-delivery-workflows` mirrors the planning probe wording.
- **Proposal handoff** (`features/proposals/usecases/handoff.py`, `_refuse_merge`): raise
  `ProposalTargetExistsError(..., guardrail=False, actor=Actor.USER)`. `SpecError` keeps `retry=AFTER_FIX`, so the
  advisory derives `INTERACTION` (`devkit.advisory` mode rules: not input error, not guardrail, actor user). The class
  default stays `guardrail = True`, so every other raise stays `BLOCKED` (AC-03, AC-04). The class docstring and
  `CAP-DLV-proposal-incubation` rule 4.5 and the §4.12 row name both modes.
- **Entrypoint tree exclusion** (`features/entrypoints/services/derive.py`): add `feedback_file(code: str) -> bool`
  beside `EXCLUDED_TREES`: `specs/` first segment, at least four segments, the parent segment `feedback`, a `.md`
  file name. Exported from `devkit_spec.features.entrypoints`. `classify_boundary` and `derive` are unchanged
  (AC-06).
- **Scope inputs** (`features/scope/usecases/inputs.py`, `from_spec`): when `classify_boundary` returns
  `EXCLUDED_TREE`, the normalized path is a `feedback_file`, it is not under `spec_dir` and it is not an existing
  directory, append it as `ScopePath(path, kind_of(root, path), Source.DECLARED_CODE, Stage.SPEC)`. Such paths do
  not count as declared code for the candidate replacement (AC-05, AC-07). Comparison already covers declared code,
  so overlap needs no change.
- **Documents** (AC-08): `packages/devkit-spec/README.md`, `guides/install/mcp.md`, `docs/glossary.md`,
  `ARCH-04-1-ecosystem-boundaries`, `CAP-WT-task-worktrees` §7, `CAP-DIST-sync-and-transactions` template; item 4
  writes a new feedback file in this unit.

## 3. Error Handling & Edge Cases

- A merge conflict where the dated path is a symbolic link or file goes through `_refuse_merge` too, so it also asks
  the user; its fix (rename aside, content kept) is unchanged.
- A feedback path with a glob character is `invalid-path` before the exception is considered.
- A feedback path of the declaring unit is under `spec_dir` and stays `excluded-tree`.

## 4. Verification & Test Plan

- `packages/devkit-spec/tests/integration/features/proposals/test_proposal_handoff_merge.py`: assert mode
  `INTERACTION`, `guardrail` false, actor `user` for a different-content conflict and a non-directory dated path;
  `test_proposal_handoff.py`: an existing spec bundle stays `BLOCKED`.
- `packages/devkit-spec/tests/integration/features/scope/`: declared feedback file collected, own feedback, another
  bundle's `spec.md` and `feedback/` directory excluded, candidates kept, two units overlapping on the file.
- `packages/devkit-spec/tests/unit/features/entrypoints/`: `feedback_file` cases; derivation still skips the path.
- `packages/devkit-spec/tests/integration/bundles/spec/test_role_contracts.py` and
  `test_delegation_sandbox_guidance.py`: the guidance sentences.
- `just lint devkit-spec`, `just lint-check devkit-spec`, `just check devkit-spec`, `just test-affected`,
  `uv run devkit rules check --ci --base f35e2b8e`, `uv run devkit sync` then `uv run devkit sync --check`.
