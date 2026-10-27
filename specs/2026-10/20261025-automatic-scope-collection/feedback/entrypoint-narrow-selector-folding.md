---
id: FB-entrypoint-narrow-selector-folding
title: Explain narrow entrypoint selectors beneath task directory boundaries
scope: repo
kind: friction
category: instruction-conflict
target: packages/devkit-spec/src/devkit_spec/bundles/spec/bundle/skills/spec-entrypoints/SKILL.md
origin: agent
severity: workaround
recurring: false
status: resolved
created_at: 2026-10-25
---

# [FB-entrypoint-narrow-selector-folding] Explain narrow entrypoint selectors beneath task directory boundaries

## 1. Friction / Question

- **Context**: Selecting two exact doorway files for a use case during Living Spec reconciliation.
- **Expectation**: The skill's procedure applies the reviewed document/code pairs through explicit target and code
  selectors, after recommending narrow files instead of broad shared directories.
- **Actual**: Tasks declared the owning scope directory and the two files. Derivation folded the files beneath the
  directory before selection, reported both exact choices as folded, and applied zero pairs.
- **Workaround (or Interpretation Chosen)**: Wrote only the reviewed exact entrypoint paths in the use case and
  verified them through the document query. No broad directory was added merely to satisfy the selector.
- **Suggestion**: Document this directory-boundary case and its direct-edit alternative, or make explicit narrow
  selectors materialize a covered doorway candidate before folding. Keep this separate from runtime collection.

## Diagnostic Details

- **Reproduction**: Declare a task directory and child doorway, then derive with `--apply --target` and child `--code`.
- **Expected / Actual**: Two requested files; both `reason=folded`, `applied=0`.
- **Versions**: SPEC-automatic-scope-collection implementation.
- **Conditions**: Task boundaries use an owning directory; the target use case has no prior entrypoints.
- **Workarounds Attempted**: Added precise task file boundaries; parent folding still prevented CLI application.
- **Related Assets**: CAP-TRACE-code-entrypoints; `features/entrypoints/services/derive.py`; `spec-entrypoints`.

## Evidence

```text
[SKIPPED: .../scope/cli/commands.py kind=apply ... reason=folded]
[SKIPPED: .../scope/usecases/collection.py kind=apply ... reason=folded]
[SUMMARY: pairs=6 new=4 declared=2 skipped=5 applied=0]
```

## Disposition

Resolved by `SPEC-entrypoints-apply-file-codes` (integrated 2026-10-26). A `--code` equal to a folded candidate now
unfolds it and is applied, and a `--code` under a directory candidate becomes its own candidate, so the reported
`reason=folded` / `applied=0` no longer occurs. `test_cli.py::test_selected_folded_candidate_is_applied` reproduces
this item's case (a task `_Boundary` naming the owning directory and the child file, applied with `--target` and the
child `--code`) and passes. An unmatched `--code` is refused with `SPEC_ENTRYPOINTS_CODE_UNMATCHED`.
