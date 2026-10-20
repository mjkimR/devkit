# Affected-test selection evidence

Repository revision: `c399aee8832397023d1b6a253aed32a0c70083f0` (Planning only changes proposal files).
Evidence was collected with the prepared workspace interpreter, bytecode and pytest cache writes disabled.
No tests were executed and production source was not changed.

## Collection and baseline

`PYTHONDONTWRITEBYTECODE=1 uv run --no-sync python -m pytest --collect-only -q -p no:cacheprovider`
collected **3,826** tests successfully in 3.85 seconds (4.39 seconds subprocess wall time). Of these, **1,117**
belong to devkit-spec. Counts include parametrized cases, not just test functions.

The existing script was imported with importlib.util, then `select(root, [changed_path])` ran for each row.
Counts match the collected node IDs whose file is equal to or below a selected path. Current source mapping is
area-level, so nonexistent historical sample names gate/runner.py, workflow/library.py, rules/engine.py and
compact/runner.py resolve to the same area as the corresponding existing files listed below. The first probe used
those historical names; Development reproduction must use the existing paths. No file-change execution claim is
made by this synthetic path-selection experiment.

| Existing representative source | Current count | File groups only, retaining owner edges |
| --- | ---: | ---: |
| packages/devkit/src/devkit/gate/engine/runner.py | 1,072 | 301 |
| packages/devkit/src/devkit/workflow/workspace.py | 2,035 | 1,660 |
| packages/devkit/src/devkit/worktree/lifecycle.py | 1,852 | 1,487 |
| packages/devkit/src/devkit/rules/engine/evaluator.py | 2,743 | 2,256 |
| packages/devkit-dist/src/devkit/distribution/installation/engines.py | 2,037 | 775 |
| packages/devkit/src/devkit/compact/execute.py | 3,014 | 2,527 |
| packages/devkit-spec/src/devkit_spec/scope/flow.py | 1,117 | 1,117 |

Current group count is 32; expanding each group to its test_*.py files yields 193 file groups. The conservative
simulation retains each file's area/package owner, calculates that file's own imports with existing Workspace.imports,
and always includes SOURCE_TREE_TESTS for devkit namespace changes. It retains the existing coarse production graph.
Measured select calls took 0.622–0.647 seconds in this run; not a cross-machine performance guarantee.

The submitted 187/923/1104 file-split estimates are not reproduced by this conservative model. Removing owner edges,
using different fixtures/revisions or excluding structural tests can change counts; lower counts alone do not
establish safe coverage. The two-stage recommendation is supported by the reductions above and by the unchanged
spec-scope row, not by a universal 100–300-test target. A complete fine-source prototype was not built in Planning.

## Code evidence and safeguards

- Workspace.groups merges an area's tests and embedded rule tests, or a non-devkit workspace package's tests/src,
  into one Group. node_of and _source_node collapse devkit_spec to its package root. dependents computes transitive
  production import propagation; file grouping alone cannot remove that source-level coupling.
- Workspace._helper_imports follows selected module-level testsupport/distsupport imports. A function-local helper
  import is currently excluded there; finer selection must not exploit this omission to report artificial savings.
- packages/devkit/tests/testsupport/gate.py imports devkit.gate while also exposing a generic git function.
  That is a real module import under the current helper structure, even if one caller uses only git.
- packages/devkit-spec/tests/scope/test_flow.py imports scope.support via the pytest test path as well as spec APIs.
  Helper discovery must account for pytest pythonpath and relative imports, not only the two named helper roots.
- packages/devkit-spec/tests/conftest.py currently provides filesystem fixtures without domain imports. Its
  future domain imports must still reach every descendant test group; conftest edits keep full fallback.
- ADR-nightly-ci-verification explicitly accepts static-selection limits and keeps complete nightly/release checks.
  This change does not promise complete dynamic Python dependency inference or change that policy.

## Verification to run in Development

Record a reusable before/after matrix at the actual implementation base and head, using existing source paths,
selected file sets and collected IDs. Keep parser/graph fixtures for relative imports, re-exports, initializers,
helper chains and cycles, conftest scope, dynamic/opaque fallbacks, removed modules and mandatory structural checks.
Add safety expectations independently of the selector implementation. Re-run the matrix after any module-boundary
change from the concurrent MCP work; do not compare differing source trees as if only the algorithm changed.
